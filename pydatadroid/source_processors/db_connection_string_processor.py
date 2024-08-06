import logging
import threading
from abc import ABC

from google.protobuf.wrappers_pb2 import StringValue, UInt64Value
from sqlalchemy import create_engine, text

from pydatadroid.exceptions.execption import TimeoutException
from pydatadroid.protos.result_pb2 import TableResult, Result, ResultType
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


class DBConnectionStringProcessor(Processor, ABC):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def get_connection(self):
        try:
            engine = create_engine(self.connection_string)
            connection = engine.connect()
            return connection
        except Exception as e:
            logger.error(f"Exception occurred while creating db connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            connection = self.get_connection()
            result = connection.execute(text("SELECT 1"))
            connection.close()
            return True
        except Exception as e:
            logger.error(f"Exception occurred while testing db connection connection with error: {e}")
            raise e

    def get_query_result(self, query, timeout=120):
        try:
            if query.endswith(";"):
                query = query[:-1]
            c_query = f"SELECT COUNT(*) FROM ({query}) AS subquery"

            def query_db():
                nonlocal count_result, result, exception
                try:
                    connection = self.get_connection()
                    count_result = connection.execution_options(timeout=timeout).execute(text(c_query)).fetchone()[0]
                    result = connection.execution_options(timeout=timeout).execute(text(query))
                    connection.close()
                    return result
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
            col_names = list(result.keys())
            query_result = result.fetchall()
            for row in query_result:
                table_columns = []
                for i, value in enumerate(row):
                    table_column = TableResult.TableColumn(name=StringValue(value=col_names[i]),
                                                           value=StringValue(value=str(value)))
                    table_columns.append(table_column)
                table_rows.append(TableResult.TableRow(columns=table_columns))
            table = TableResult(raw_query=StringValue(value=query),
                                total_count=UInt64Value(value=int(count_result)),
                                rows=table_rows)
            task_result = Result(type=ResultType.TABLE, table=table)
            return proto_to_dict(task_result)
        except Exception as e:
            logger.error(f"Exception occurred while fetching clickhouse query result with error: {e}")
            raise e
