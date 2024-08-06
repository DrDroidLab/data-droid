import logging
import re
from abc import ABC
from datetime import datetime

import pytz
from google.protobuf.wrappers_pb2 import StringValue, DoubleValue
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from pydatadroid.protos.result_pb2 import Result, ResultType, TimeseriesResult, LabelValuePair
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict
from pydatadroid.utils.time_utils import current_epoch

logger = logging.getLogger(__name__)


def get_nrql_expression_result_alias(nrql_expression):
    pattern = r'AS\s+\'(.*?)\'|AS\s+(\w+)'
    match = re.search(pattern, nrql_expression, re.IGNORECASE)
    if match:
        return match.group(1) or match.group(2)
    return 'result'


class NewRelicProcessor(Processor, ABC):
    def __init__(self, nr_api_key: str, nr_account_id: str, nr_api_domain: str = 'api.newrelic.com'):
        self.__nr_api_key = nr_api_key
        self.nr_account_id = nr_account_id
        self.nr_api_domain = nr_api_domain

    def get_connection(self):
        try:
            headers = {
                "Api-Key": self.__nr_api_key,
                "Content-Type": "application/json",
            }

            graphql_endpoint = "https://{}/graphql".format(self.nr_api_domain)
            transport = RequestsHTTPTransport(url=graphql_endpoint, use_json=True, headers=headers, verify=True,
                                              retries=3)

            # Create a GraphQL client
            client = Client(transport=transport, fetch_schema_from_transport=False)
            return client
        except Exception as e:
            logger.error(f"Exception occurred while creating NewRelic client with error: {e}")
            raise e

    def test_connection(self):
        query = gql(f"""{{
                                actor {{
                                    account(id: {self.nr_account_id}) {{
                                        name
                                    }}
                                }}
                            }}""")

        try:
            client = self.get_connection()
            result = client.execute(query)
            if result:
                output = result.get('actor', {}).get('account', {})
                if output:
                    return True
                else:
                    raise Exception("Failed to connect with NewRelic GQL API Server")
            else:
                raise Exception("Failed to connect with NewRelic GQL API Server")
        except Exception as e:
            raise e

    def execute_nrql_query(self, nrql_expression: str, start_time_epoch: int = None, end_time_epoch: int = None):
        if not end_time_epoch:
            end_time_epoch = current_epoch()
        if not start_time_epoch:
            start_time_epoch = end_time_epoch - 3600

        if not nrql_expression:
            raise Exception("Invalid NRQL expression. NRQL expression is missing")

        if 'timeseries' not in nrql_expression.lower():
            raise Exception("Invalid NRQL expression. TIMESERIES is missing in the NRQL expression")

        if 'limit max timeseries' in nrql_expression.lower():
            nrql_expression = re.sub('limit max timeseries', 'TIMESERIES 5 MINUTE', nrql_expression,
                                     flags=re.IGNORECASE)
        if 'since' not in nrql_expression.lower():
            time_since = start_time_epoch
            time_until = end_time_epoch
            total_seconds = (time_until - time_since)
            nrql_expression = nrql_expression + f' SINCE {total_seconds} SECONDS AGO'

        try:
            result_alias = get_nrql_expression_result_alias(nrql_expression)

            query = gql(f"""{{
                                            actor {{
                                                account(id: {self.nr_account_id}) {{
                                                    nrql(query: "{nrql_expression}") {{
                                                        metadata {{
                                                            eventTypes
                                                            facets
                                                            messages
                                                            timeWindow {{
                                                                begin
                                                                compareWith
                                                                end
                                                                since
                                                                until
                                                            }}
                                                        }}
                                                        nrql
                                                        otherResult
                                                        previousResults
                                                        rawResponse
                                                        results
                                                        totalResult
                                                    }}
                                                }}
                                            }}
                                        }}
                                    """)

            response = None
            try:
                client = self.get_connection()
                result = client.execute(query)
                if result:
                    response = result.get('actor', {}).get('account', {}).get('nrql', {})

            except Exception as e:
                logger.error(f"NewRelic execute_nrql_query error: {e}")
                raise e

            if not response:
                raise Exception("No data returned from New Relic")

            results = response.get('results', [])
            metric_datapoints = []
            for item in results:
                utc_timestamp = item['beginTimeSeconds']
                utc_datetime = datetime.utcfromtimestamp(utc_timestamp)
                utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)
                val = item.get(result_alias)
                datapoint = TimeseriesResult.LabeledMetricTimeseries.Datapoint(
                    timestamp=int(utc_datetime.timestamp() * 1000), value=DoubleValue(value=val))
                metric_datapoints.append(datapoint)

            labeled_metric_timeseries_list = [TimeseriesResult.LabeledMetricTimeseries(datapoints=metric_datapoints)]
            timeseries_result = TimeseriesResult(metric_expression=StringValue(value=nrql_expression),
                                                 labeled_metric_timeseries=labeled_metric_timeseries_list)
            task_result = Result(type=ResultType.TIMESERIES, timeseries=timeseries_result)
            return proto_to_dict(task_result)
        except Exception as e:
            logger.error(f"Exception occurred while fetching metric timeseries with error: {e}")
            raise e
