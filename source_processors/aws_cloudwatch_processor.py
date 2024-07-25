import logging
from abc import ABC

import boto3

from source_processors.processor import Processor
from utils.time_utils import current_milli_time

logger = logging.getLogger(__name__)


class AWSCloudwatchProcessor(Processor, ABC):
    def __init__(self, client_type: str, region: str, aws_access_key: str, aws_secret_key: str):
        if client_type not in ['cloudwatch', 'logs']:
            raise ValueError("Invalid client type provided for AWS Cloudwatch Processor")

        self.client_type = client_type
        self.__aws_access_key = aws_access_key
        self.__aws_secret_key = aws_secret_key
        self.region = region,
        self.__aws_session_token = None

    def get_connection(self):
        try:
            client = boto3.client(self.client_type, aws_access_key_id=self.__aws_access_key,
                                  aws_secret_access_key=self.__aws_secret_key, region_name=self.region,
                                  aws_session_token=self.__aws_session_token)
            return client
        except Exception as e:
            logger.error(f"Exception occurred while creating boto3 client with error: {e}")
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
                log_groups = self._logs_describe_log_groups()
                if log_groups:
                    return True
                else:
                    raise Exception("No log groups found in the logs connection")
        except Exception as e:
            logger.error(f"Exception occurred while testing cloudwatch connection with error: {e}")
            raise e

    def cloudwatch_get_metric_statistics(self, namespace, metric, start_time, end_time, period, statistics, dimensions):
        try:
            client = self.get_connection()
            response = client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=statistics,
                Dimensions=dimensions
            )
            return response
        except Exception as e:
            logger.error(
                f"Exception occurred while fetching cloudwatch metric statistics for metric: {metric} with error: {e}")
            raise e

    def _logs_describe_log_groups(self):
        try:
            client = self.get_connection()
            paginator = client.get_paginator('describe_log_groups')
            log_groups = []
            for page in paginator.paginate():
                for log_group in page['logGroups']:
                    log_groups.append(log_group['logGroupName'])
            return log_groups
        except Exception as e:
            logger.error(f"Exception occurred while fetching log groups with error: {e}")
            raise e

    def logs_filter_events(self, log_group, query_pattern, start_time, end_time):
        try:
            client = self.get_connection()
            start_query_response = client.start_query(
                logGroupName=log_group,
                startTime=start_time,
                endTime=end_time,
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
                    return response['results']
                elif current_milli_time() - query_start_time > 60000:
                    logger.info("Query took too long to complete. Aborting...")
                    stop_query_response = client.stop_query(queryId=query_id)
                    logger.info(f"Query stopped with response: {stop_query_response}")
                    return None
            return None
        except Exception as e:
            logger.error(f"Exception occurred while fetching logs for log_group: {log_group} with error: {e}")
            raise e
