import logging

import requests

from pydatadroid.source_processors.processor import Processor
from google.protobuf.wrappers_pb2 import StringValue, UInt64Value

from pydatadroid.protos.result_pb2 import TableResult, Result, ResultType
from pydatadroid.utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


class GrafanaLokiApiProcessor(Processor):
    client = None

    def __init__(self, host, port, protocol, x_scope_org_id='anonymous', ssl_verify=True):
        self.__protocol = protocol
        self.__host = host
        self.__port = port
        self.__ssl_verify = ssl_verify
        self.__headers = {'X-Scope-OrgID': x_scope_org_id}


    def get_connection(self):
        try:
            url = '{}/ready'.format(f"{self.__protocol}://{self.__host}:{self.__port}")
            return url
        except Exception as e:
            logger.error(f"Exception occurred while testing Loki connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            url = '{}/ready'.format(f"{self.__protocol}://{self.__host}:{self.__port}")
            response = requests.get(url, headers=self.__headers, verify=self.__ssl_verify)
            if response and response.status_code == 200:
                return True
            else:
                status_code = response.status_code if response else None
                raise Exception(
                    f"Failed to connect with Grafana. Status Code: {status_code}. Response Text: {response.text}")
        except Exception as e:
            logger.error(f"Exception occurred while fetching grafana data sources with error: {e}")
            raise e

    def query(self, query, start: int=None, end: int=None, limit=1000):
        try:
            url = '{}/loki/api/v1/query_range'.format(f"{self.__protocol}://{self.__host}:{self.__port}")
            params = {
                'query': query,
                'start': start,
                'end': end,
                'limit': limit
            }
            response = requests.get(url, headers=self.__headers, verify=self.__ssl_verify, params=params)
            if not response:
                raise Exception("No data returned from Grafana Loki")
            if response.status_code!=200:
                raise Exception(f"Failed to fetch data from Grafana Loki with error message: {response.text}")
            result = response.json().get('data', {}).get('result', [])
            table_rows: [TableResult.TableRow] = []
            for r in result:
                table_meta_columns = []
                data_rows = []
                for key, value in r.items():
                    if key == 'stream' or key == 'metric':
                        for k, v in value.items():
                            table_meta_columns.append(TableResult.TableColumn(name=StringValue(value=str(k)),
                                                                              value=StringValue(value=str(v))))
                    elif key == 'values':
                        for v in value:
                            table_columns = []
                            for i, val in enumerate(v):
                                if i == 0:
                                    key = 'timestamp'
                                else:
                                    key = 'log'
                                table_columns.append(TableResult.TableColumn(name=StringValue(value=key),
                                                                             value=StringValue(value=str(val))))
                            data_rows.append(table_columns)
                for dc in data_rows:
                    update_columns = table_meta_columns + dc
                    table_row = TableResult.TableRow(columns=update_columns)
                    table_rows.append(table_row)
            table = TableResult(raw_query=StringValue(value=f"Execute ```{query}```"),
                                total_count=UInt64Value(value=len(result)),
                                rows=table_rows)
            result_proto = Result(
                type=ResultType.LOGS,
                logs=table
            )
            return proto_to_dict(result_proto)
        except Exception as e:
            logger.error(f"Exception occurred while fetching grafana data sources with error: {e}")
            raise e