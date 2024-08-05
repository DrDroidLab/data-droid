import logging
import os
from abc import ABC
from datetime import timedelta

from azure.identity import DefaultAzureCredential
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.monitor.query import LogsQueryClient
from google.protobuf.wrappers_pb2 import StringValue, UInt64Value

from pydatadroid.protos.result_pb2 import TableResult, Result, ResultType
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict
from pydatadroid.utils.time_utils import current_epoch

logger = logging.getLogger(__name__)


def get_credentials(self):
    """
    Function to fetch Azure credentials using client_id, client_secret, and tenant_id.
    """
    os.environ['AZURE_CLIENT_ID'] = self.__client_id
    os.environ['AZURE_CLIENT_SECRET'] = self.__client_secret
    os.environ['AZURE_TENANT_ID'] = self.__tenant_id
    credential = DefaultAzureCredential()
    return credential


def query_response_to_dict(response):
    """
    Function to convert query response tables to dictionaries.
    """
    result = {}
    for table in response.tables:
        result[table.name] = []
        for row in table.rows:
            row_dict = {}
            for i, column in enumerate(table.columns):
                row_dict[column] = str(row[i])
            result[table.name].append(row_dict)
    return result


class AzureProcessor(Processor, ABC):
    def __init__(self, subscription_id: str, tenant_id: str, client_id: str, client_secret: str):
        self.__subscription_id = subscription_id
        self.__tenant_id = tenant_id
        self.__client_id = client_id
        self.__client_secret = client_secret

    def get_credentials(self):
        """
        Function to fetch Azure credentials using client_id, client_secret, and tenant_id.
        """
        os.environ['AZURE_CLIENT_ID'] = self.__client_id
        os.environ['AZURE_CLIENT_SECRET'] = self.__client_secret
        os.environ['AZURE_TENANT_ID'] = self.__tenant_id
        credential = DefaultAzureCredential()
        return credential

    def test_connection(self):
        try:
            credentials = self.get_credentials()
            if not credentials:
                raise ValueError("Azure Connection Error:: Failed to get credentials")
            log_analytics_client = LogAnalyticsManagementClient(credentials, self.__subscription_id)
            workspaces = log_analytics_client.workspaces.list()
            if not workspaces:
                raise ValueError("Azure Connection Error:: No Workspaces Found")
            az_workspaces = []
            for workspace in workspaces:
                az_workspaces.append(workspace.as_dict())
            if len(az_workspaces) > 0:
                return True
            else:
                raise ValueError("Azure Connection Error:: No Workspaces Found")
        except Exception as e:
            raise e

    def query_log_analytics(self, workspace_id: str, query: str, start_time_epoch: int = None,
                            end_time_epoch: int = None):
        if not end_time_epoch:
            end_time_epoch = current_epoch()
        if not start_time_epoch:
            start_time_epoch = end_time_epoch - 3600
        timespan = timedelta(seconds=int(end_time_epoch - start_time_epoch))
        try:
            logger.info(f"Querying Azure Log Analytics workspace: {workspace_id} with query: {query}")
            credentials = self.get_credentials()
            if not credentials:
                raise ValueError("Azure Connection Error:: Failed to get credentials")
            client = LogsQueryClient(credentials)
            response = client.query_workspace(workspace_id, query, timespan=timespan)
            if not response:
                raise ValueError(f"No data returned from Azure Analytics workspace Logs for query: {query}")
            results = query_response_to_dict(response)
            table_rows: [TableResult.TableRow] = []
            for table, rows in results.items():
                for i in rows:
                    table_columns: [TableResult.TableRow.TableColumn] = []
                    for key, value in i.items():
                        table_column_name = f'{table}.{key}'
                        table_column = TableResult.TableColumn(
                            name=StringValue(value=table_column_name), value=StringValue(value=str(value)))
                        table_columns.append(table_column)
                    table_row = TableResult.TableRow(columns=table_columns)
                    table_rows.append(table_row)
            result = TableResult(
                raw_query=StringValue(value=query),
                rows=table_rows,
                total_count=UInt64Value(value=len(table_rows)),
            )
            task_result = Result(type=ResultType.LOGS, logs=result)
            return proto_to_dict(task_result)
        except Exception as e:
            raise Exception(f"Error while executing Azure task: {e}")
