import logging

import psycopg2
from psycopg2 import extras

from google.protobuf.wrappers_pb2 import StringValue, UInt64Value

from pydatadroid.protos.result_pb2 import TableResult, Result, ResultType
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


class PostgresDBProcessor(Processor):
    client = None

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 5432,
                 connect_timeout: int = None):
        if not host or not user or not password or not database:
            raise Exception("Host, User, Password and Database are required to connect to postgres")

        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'connect_timeout': connect_timeout,
        }

    def get_connection(self):
        try:
            client = psycopg2.connect(**self.config)
            return client
        except Exception as e:
            logger.error(f"Exception occurred while testing postgres connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            client = self.get_connection()
            cursor = client.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            client.close()
            return True
        except Exception as e:
            logger.error(f"Exception occurred while testing postgres connection with error: {e}")
            raise e

    def get_query_result(self, query):
        try:
            client = self.get_connection()
            cursor = client.cursor(cursor_factory=extras.DictCursor)
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            client.close()
            table_rows = []
            for row in result:
                table_columns = []
                for column, value in row.items():
                    table_column = TableResult.TableColumn(name=StringValue(value=column),
                                                           value=StringValue(value=str(value)))
                    table_columns.append(table_column)
                table_rows.append(TableResult.TableRow(columns=table_columns))
            table = TableResult(raw_query=StringValue(value=query),
                                total_count=UInt64Value(value=int(len(result))),
                                rows=table_rows)
            proto_result = Result(type=ResultType.TABLE, table=table)
            return proto_to_dict(proto_result)
        except Exception as e:
            logger.error(f"Exception occurred while executing postgres query with error: {e}")
            raise e
