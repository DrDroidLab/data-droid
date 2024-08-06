import logging
import threading
from abc import ABC

import clickhouse_connect
from google.protobuf.wrappers_pb2 import StringValue, UInt64Value

from pydatadroid.exceptions.execption import TimeoutException
from pydatadroid.protos.result_pb2 import TableResult, Result, ResultType
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


class ClickhouseDBProcessor(Processor, ABC):
    def __init__(self, protocol: str, host: str, port: str, user: str, password: str, database: str):
        self.config = {
            'interface': protocol,
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }

    def get_connection(self):
        try:
            client = clickhouse_connect.get_client(**self.config)
            return client
        except Exception as e:
            logger.error(f"Exception occurred while creating clickhouse connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            client = self.get_connection()
            query = 'SELECT 1'
            result = client.query(query)
            client.close()
            if result:
                return True
            else:
                raise Exception("Clickhouse Connection Error:: Failed to fetch result from clickhouse")
        except Exception as e:
            logger.error(f"Exception occurred while testing clickhouse connection with error: {e}")
            raise e

    def get_query_result(self, query, timeout=120):
        try:
            if not self.config.get('database'):
                raise Exception("Database is required to fetch clickhouse query result")
            count_query = f"SELECT COUNT(*) FROM ({query}) AS subquery"

            def query_db():
                nonlocal count_result, result, exception
                try:
                    client = self.get_connection()
                    count_result = client.query(count_query, settings={'session_timeout': timeout})
                    result = client.query(query, settings={'session_timeout': timeout})
                    client.close()
                except Exception as e:
                    exception = e

            count_result = None
            result = None
            exception = None

            query_thread = threading.Thread(target=query_db)
            query_thread.start()
            query_thread.join(timeout)

            if query_thread.is_alive():
                raise TimeoutException(f"Function 'execute_sql_query' exceeded the timeout of {timeout} seconds")
            if exception:
                raise exception

            table_rows: [TableResult.TableRow] = []
            for row in result.result_set:
                table_columns = []
                for i, column in enumerate(result.column_names):
                    table_column = TableResult.TableColumn(name=StringValue(value=column),
                                                           value=StringValue(value=str(row[i])))
                    table_columns.append(table_column)
                table_rows.append(TableResult.TableRow(columns=table_columns))
            table = TableResult(raw_query=StringValue(value=query),
                                total_count=UInt64Value(value=int(count_result.result_set[0][0])),
                                rows=table_rows)
            task_result = Result(type=ResultType.TABLE, table=table)
            return proto_to_dict(task_result)
        except Exception as e:
            logger.error(f"Exception occurred while fetching clickhouse query result with error: {e}")
            raise e
