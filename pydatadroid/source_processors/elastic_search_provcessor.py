import logging
from abc import ABC

from elasticsearch import Elasticsearch
from google.protobuf.wrappers_pb2 import StringValue, UInt64Value

from pydatadroid.protos.result_pb2 import TableResult, Result, ResultType
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict
from pydatadroid.utils.time_utils import current_epoch

logger = logging.getLogger(__name__)


class ElasticSearchProcessor(Processor, ABC):
    def __init__(self, protocol: str, host: str, port: str, api_key_id: str, api_key: str, verify_certs: bool = False):
        self.protocol = protocol
        self.host = host
        self.port = int(port) if port else 9200
        self.verify_certs = verify_certs
        self.__api_key_id = api_key_id
        self.__api_key = api_key

    def get_connection(self):
        try:
            client = Elasticsearch(
                [f"{self.protocol}://{self.host}:{self.port}"],
                api_key=(self.__api_key_id, self.__api_key),
                verify_certs=self.verify_certs
            )
            return client
        except Exception as e:
            logger.error(f"Exception occurred while creating elasticsearch connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            connection = self.get_connection()
            indices = connection.indices.get_alias()
            connection.close()
            if len(list(indices.keys())) > 0:
                return True
            else:
                raise Exception("Elasticsearch Connection Error:: No indices found in elasticsearch")
        except Exception as e:
            logger.error(f"Exception occurred while fetching elasticsearch indices with error: {e}")
            raise e

    def query(self, index: str, lucene_query: str, limit: int = 2000, offset: int = 0, timestamp_field: str = "",
              start_time_epoch: int = None, end_time_epoch: int = None):
        if not end_time_epoch:
            end_time_epoch = current_epoch()
        if not start_time_epoch:
            start_time_epoch = end_time_epoch - 3600
        if not index:
            raise Exception("Task execution Failed:: No index found")
        try:
            lucene_query = lucene_query.strip()
            sort = []
            if timestamp_field:
                sort.append({timestamp_field: "desc"})
            sort.append({"_score": "desc"})

            if timestamp_field:
                query = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "query_string": {
                                        "query": lucene_query
                                    }
                                },
                                {
                                    "range": {
                                        timestamp_field: {
                                            "gte": start_time_epoch * 1000,
                                            "lt": end_time_epoch * 1000
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "size": limit,
                    "from": offset,
                    "sort": sort
                }
            else:
                query = {
                    "query": {
                        "query_string": {
                            "query": lucene_query
                        }
                    },
                    "size": limit,
                    "from": offset,
                    "sort": sort
                }

            connection = self.get_connection()
            result = connection.search(index=index, body=query, pretty=True)
            connection.close()
            if 'hits' not in result or not result['hits']['hits']:
                raise Exception(f"No data found for the query: {lucene_query}")

            hits = result['hits']['hits']
            count_result = len(hits)
            if count_result == 0:
                raise Exception(f"No data found for the query: {query}")

            table_rows: [TableResult.TableRow] = []
            for hit in hits:
                table_columns = []
                for column, value in hit.items():
                    if column == '_source':
                        try:
                            for key, val in value.items():
                                table_column = TableResult.TableColumn(name=StringValue(value=key),
                                                                       value=StringValue(value=str(val)))
                                table_columns.append(table_column)
                        except Exception as e:
                            table_column = TableResult.TableColumn(name=StringValue(value=column),
                                                                   value=StringValue(value=str(value)))
                            table_columns.append(table_column)
                    else:
                        table_column = TableResult.TableColumn(name=StringValue(value=column),
                                                               value=StringValue(value=str(value)))
                        table_columns.append(table_column)
                table_rows.append(TableResult.TableRow(columns=table_columns))
            table = TableResult(raw_query=StringValue(value=lucene_query),
                                total_count=UInt64Value(value=count_result),
                                rows=table_rows)
            task_result = Result(type=ResultType.LOGS, logs=table)
            return proto_to_dict(task_result)
        except Exception as e:
            logger.error(f"Exception occurred while fetching clickhouse query result with error: {e}")
            raise e
