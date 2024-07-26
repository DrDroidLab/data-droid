import logging
from abc import ABC
from datetime import datetime
from typing import Dict

import boto3
import pytz as pytz
from google.protobuf.wrappers_pb2 import StringValue, UInt64Value, DoubleValue

from pydatadroid.protos.result_pb2 import TableResult, Result, ResultType, TimeseriesResult, LabelValuePair
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict
from pydatadroid.utils.time_utils import current_milli_time, current_epoch

logger = logging.getLogger(__name__)


class AWSCloudwatchProcessor(Processor, ABC):
    def __init__(self, client_type: str, region: str, aws_access_key: str, aws_secret_key: str):
        if client_type not in ['cloudwatch', 'logs']:
            raise ValueError("Invalid pydatadroid type provided for AWS Cloudwatch Processor")

        self.client_type = client_type
        self.__aws_access_key = aws_access_key
        self.__aws_secret_key = aws_secret_key
        self.region = region
        self.__aws_session_token = None

    def get_connection(self):
        try:
            client = boto3.client(self.client_type, aws_access_key_id=self.__aws_access_key,
                                  aws_secret_access_key=self.__aws_secret_key, region_name=self.region,
                                  aws_session_token=self.__aws_session_token)
            return client
        except Exception as e:
            logger.error(f"Exception occurred while creating boto3 pydatadroid with error: {e}")
            raise e

    def test_connection(self):
        try:
            if self.client_type == 'cloudwatch':
                client = self.get_connection()
                response = client.list_metrics()
                if response:
                    return True
                else:
                    raise Exception("No metrics found in the cloudwatch connection")
            elif self.client_type == 'logs':
                client = self.get_connection()
                response = client.describe_log_groups()
                log_groups = response['logGroups']
                if log_groups:
                    return True
                else:
                    raise Exception("No log groups found in the logs connection")
        except Exception as e:
            logger.error(f"Exception occurred while testing cloudwatch connection with error: {e}")
            raise e

    def cloudwatch_get_metric_statistics(self, namespace: str, metric: str, end_time_epoch: int = None,
                                         start_time_epoch: int = None, dimensions: Dict = None, period: int = 300,
                                         statistic: str = 'Average'):
        if not end_time_epoch:
            end_time_epoch = current_epoch()
        if not start_time_epoch:
            start_time_epoch = end_time_epoch - 3600

        dimensions_list = []
        if dimensions:
            for key, value in dimensions.items():
                dimensions_list.append({'Name': key, 'Value': value})

        start_time = datetime.utcfromtimestamp(start_time_epoch)
        end_time = datetime.utcfromtimestamp(end_time_epoch)
        try:
            client = self.get_connection()
            response = client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=[statistic],
                Dimensions=dimensions_list
            )
            if not response or not response['Datapoints']:
                raise Exception(f"No data returned from Cloudwatch for namespace: {namespace} and metric: {metric}")
            response_datapoints = response['Datapoints']
            if len(response_datapoints) > 0:
                metric_unit = response_datapoints[0]['Unit']
            else:
                metric_unit = ''

            metric_datapoints: [TimeseriesResult.LabeledMetricTimeseries.Datapoint] = []
            for item in response_datapoints:
                utc_timestamp = str(item['Timestamp'])
                utc_datetime = datetime.fromisoformat(utc_timestamp)
                utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)
                val = item[statistic]
                datapoint = TimeseriesResult.LabeledMetricTimeseries.Datapoint(
                    timestamp=int(utc_datetime.timestamp() * 1000), value=DoubleValue(value=val))
                metric_datapoints.append(datapoint)

            labeled_metric_timeseries = [TimeseriesResult.LabeledMetricTimeseries(
                metric_label_values=[
                    LabelValuePair(name=StringValue(value='namespace'), value=StringValue(value=namespace)),
                    LabelValuePair(name=StringValue(value='statistic'),
                                   value=StringValue(value=statistic)),
                ],
                unit=StringValue(value=metric_unit),
                datapoints=metric_datapoints
            )]
            metric_metadata = f"{namespace} {metric} {statistic}"
            for i in dimensions_list:
                metric_metadata += f"{i['Name']}:{i['Value']},  "
            timeseries_result = TimeseriesResult(metric_expression=StringValue(value=metric),
                                                 metric_name=StringValue(value=metric_metadata),
                                                 labeled_metric_timeseries=labeled_metric_timeseries)

            task_result = Result(type=ResultType.TIMESERIES, timeseries=timeseries_result)
            return proto_to_dict(task_result)
        except Exception as e:
            logger.error(
                f"Exception occurred while fetching cloudwatch metric statistics for metric: {metric} with error: {e}")
            raise e

    def logs_filter_events(self, log_group: str, query_pattern: str, end_time_epoch: int = None,
                           start_time_epoch: int = None):
        if not end_time_epoch:
            end_time_epoch = current_epoch()
        if not start_time_epoch:
            start_time_epoch = end_time_epoch - 3600

        end_time_millis = end_time_epoch * 1000
        start_time_millis = start_time_epoch * 1000
        try:
            client = self.get_connection()
            start_query_response = client.start_query(
                logGroupName=log_group,
                startTime=start_time_millis,
                endTime=end_time_millis,
                queryString=query_pattern,
            )

            query_id = start_query_response['queryId']

            status = 'Running'
            query_start_time = current_milli_time()
            while status == 'Running' or status == 'Scheduled':
                logger.info("Waiting for query to complete...")
                response = client.get_query_results(queryId=query_id)
                status = response['status']
                if status == 'Complete':
                    results = response['results']
                    if not results:
                        raise Exception(f"No data returned from Cloudwatch Logs for query: {query_pattern}")
                    table_rows: [TableResult.TableRow] = []
                    for item in results:
                        table_columns: [TableResult.TableColumn] = []
                        for i in item:
                            table_column = TableResult.TableColumn(name=StringValue(value=i['field']),
                                                                   value=StringValue(value=i['value']))
                            table_columns.append(table_column)
                        table_row = TableResult.TableRow(columns=table_columns)
                        table_rows.append(table_row)

                    result = TableResult(
                        raw_query=StringValue(value="query_pattern"),
                        rows=table_rows,
                        total_count=UInt64Value(value=len(table_rows)),
                    )
                    task_result = Result(type=ResultType.LOGS, logs=result)
                    return proto_to_dict(task_result)
                elif current_milli_time() - query_start_time > 60000:
                    logger.info("Query took too long to complete. Aborting...")
                    stop_query_response = client.stop_query(queryId=query_id)
                    logger.info(f"Query stopped with response: {stop_query_response}")
                    return None
            return None
        except Exception as e:
            logger.error(f"Exception occurred while fetching logs for log_group: {log_group} with error: {e}")
            raise e
