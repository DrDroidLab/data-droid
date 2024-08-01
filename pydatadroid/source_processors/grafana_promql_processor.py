import logging
from datetime import datetime
import requests

from pydatadroid.source_processors.processor import Processor
from google.protobuf.wrappers_pb2 import StringValue, DoubleValue
from pydatadroid.protos.result_pb2 import Result, ResultType, TimeseriesResult, LabelValuePair
from pydatadroid.utils.proto_utils import proto_to_dict
from pydatadroid.utils.time_utils import current_epoch

logger = logging.getLogger(__name__)


class GrafanaPromqlProcessor(Processor):
    client = None

    def __init__(self, grafana_host, port, protocol, grafana_api_key, ssl_verify=True):
        self.__host = grafana_host
        self.__port = port
        self.__protocol = protocol
        self.__api_key = grafana_api_key
        self.__ssl_verify = ssl_verify
        self.headers = {
            'Authorization': f'Bearer {self.__api_key}'
        }

    def get_connection(self):
        try:
            url = '{}/api/datasources'.format(f"{self.__protocol}://{self.__host}:{self.__port}")
            return url
        except Exception as e:
            logger.error(f"Exception occurred while testing Grafana connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            url = '{}/api/datasources'.format(f"{self.__protocol}://{self.__host}:{self.__port}")
            response = requests.get(url, headers=self.headers, verify=self.__ssl_verify)
            if response and response.status_code == 200:
                return True
            else:
                status_code = response.status_code if response else None
                raise Exception(
                    f"Failed to connect with Grafana. Status Code: {status_code}. Response Text: {response.text}")
        except Exception as e:
            logger.error(f"Exception occurred while fetching grafana data sources with error: {e}")
            raise e

    def query(self, promql_datasource_uid: str, query: str, start_time_epoch: int=None, end_time_epoch: int=None, step=300):
        try:
            if not end_time_epoch:
                end_time_epoch = current_epoch()
            if not start_time_epoch:
                start_time_epoch = end_time_epoch - 3600

            url = '{}/api/datasources/proxy/uid/{}/api/v1/query_range?query={}&start={}&end={}&step={}'.format(
                f"{self.__protocol}://{self.__host}:{self.__port}", promql_datasource_uid, query, start_time_epoch, end_time_epoch, step)
            response = requests.get(url, headers=self.headers, verify=self.__ssl_verify)
            if not response:
                raise Exception("No data returned from Grafana PromQL")
            if response.status_code!=200:
                raise Exception(f"Failed to fetch data from Grafana PromQL with error message: {response.text}")
            result = response.json()
            if 'data' in result and 'result' in result['data']:
                labeled_metric_timeseries_list = []
                for item in result['data']['result']:
                    metric_datapoints: [TimeseriesResult.LabeledMetricTimeseries.Datapoint] = []
                    for value in item['values']:
                        utc_timestamp = value[0]
                        utc_datetime = datetime.utcfromtimestamp(utc_timestamp)
                        val = value[1]
                        datapoint = TimeseriesResult.LabeledMetricTimeseries.Datapoint(
                            timestamp=int(utc_datetime.timestamp() * 1000), value=DoubleValue(value=float(val)))
                        metric_datapoints.append(datapoint)
                    item_metrics = item['metric']
                    metric_label_values = []
                    for key, value in item_metrics.items():
                        metric_label_values.append(
                            LabelValuePair(name=StringValue(value=key), value=StringValue(value=value)))
                    labeled_metric_timeseries = TimeseriesResult.LabeledMetricTimeseries(
                        metric_label_values=metric_label_values, unit=StringValue(value=""),
                        datapoints=metric_datapoints)
                    labeled_metric_timeseries_list.append(labeled_metric_timeseries)

                timeseries_result = TimeseriesResult(
                    metric_expression=StringValue(value=query),
                    labeled_metric_timeseries=labeled_metric_timeseries_list
                )
                promql_request = Result(
                    type=ResultType.TIMESERIES,
                    timeseries=timeseries_result)
            return proto_to_dict(promql_request)
        except Exception as e:
            logger.error(f"Exception occurred while getting promql metric timeseries with error: {e}")
            raise e
