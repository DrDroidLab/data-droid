import logging
import requests
from datetime import datetime

from pydatadroid.source_processors.processor import Processor
from google.protobuf.wrappers_pb2 import StringValue, DoubleValue
from pydatadroid.protos.result_pb2 import Result, ResultType, TimeseriesResult, LabelValuePair
from pydatadroid.utils.proto_utils import proto_to_dict
from pydatadroid.utils.time_utils import current_epoch

logger = logging.getLogger(__name__)


class GrafanaMimirApiProcessor(Processor):
    client = None

    def __init__(self, mimir_host, mimir_port, mimir_protocol, x_scope_org_id='anonymous', ssl_verify=True):
        self.__host = mimir_host
        self.__port = mimir_port
        self.__protocol = mimir_protocol
        self.__ssl_verify = ssl_verify
        self.headers = {'X-Scope-OrgID': x_scope_org_id}

    def get_connection(self):
        try:
            url = '{}/api/datasources'.format(f"{self.__protocol}://{self.__host}:{self.__port}")
            return url
        except Exception as e:
            logger.error(f"Exception occurred while testing Grafana connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            url = '{}/config'.format(f"{self.__protocol}://{self.__host}:{self.__port}")
            response = requests.get(url, headers=self.headers, verify=self.__ssl_verify)
            if response and response.status_code == 200:
                return True
            else:
                status_code = response.status_code if response else None
                raise Exception(
                    f"Failed to connect with Mimir. Status Code: {status_code}. Response Text: {response.text}")
        except Exception as e:
            logger.error(f"Exception occurred while querying mimir config with error: {e}")
            raise e

    def query(self, query, start_time_epoch: int=None, end_time_epoch: int=None, step: int=300):
        try:
            if not end_time_epoch:
                end_time_epoch = current_epoch()
            if not start_time_epoch:
                start_time_epoch = end_time_epoch - 3600
            url = '{}/prometheus/api/v1/query_range?query={}&start={}&end={}&step={}'.format(
                f"{self.__protocol}://{self.__host}:{self.__port}", query, start_time_epoch, end_time_epoch, step)
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
                mimir_request = Result(
                    type=ResultType.TIMESERIES,
                    timeseries=timeseries_result)
            return proto_to_dict(mimir_request)

        except Exception as e:
            logger.error(f"Exception occurred while getting mimir metric timeseries with error: {e}")
            raise e