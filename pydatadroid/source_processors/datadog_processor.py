import logging
from abc import ABC

from datadog_api_client import Configuration, ApiClient
from datadog_api_client.exceptions import ApiException
from datadog_api_client.v1.api.authentication_api import AuthenticationApi
from datadog_api_client.v1.model.authentication_validation_response import AuthenticationValidationResponse
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.formula_limit import FormulaLimit
from datadog_api_client.v2.model.metrics_data_source import MetricsDataSource
from datadog_api_client.v2.model.metrics_timeseries_query import MetricsTimeseriesQuery
from datadog_api_client.v2.model.query_formula import QueryFormula
from datadog_api_client.v2.model.query_sort_order import QuerySortOrder
from datadog_api_client.v2.model.timeseries_formula_query_request import TimeseriesFormulaQueryRequest
from datadog_api_client.v2.model.timeseries_formula_query_response import TimeseriesFormulaQueryResponse
from datadog_api_client.v2.model.timeseries_formula_request import TimeseriesFormulaRequest
from datadog_api_client.v2.model.timeseries_formula_request_attributes import TimeseriesFormulaRequestAttributes
from datadog_api_client.v2.model.timeseries_formula_request_queries import TimeseriesFormulaRequestQueries
from datadog_api_client.v2.model.timeseries_formula_request_type import TimeseriesFormulaRequestType
from google.protobuf.wrappers_pb2 import StringValue, DoubleValue

from pydatadroid.protos.result_pb2 import Result, ResultType, TimeseriesResult, LabelValuePair
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict
from pydatadroid.utils.time_utils import current_epoch

logger = logging.getLogger(__name__)


class DatadogProcessor(Processor, ABC):
    def __init__(self, dd_app_key: str, dd_api_key: str, dd_api_domain: str = 'datadoghq.com'):
        self.__dd_app_key = dd_app_key
        self.__dd_api_key = dd_api_key
        self.dd_api_domain = dd_api_domain

        self.headers = {
            'Content-Type': 'application/json',
            'DD-API-KEY': dd_api_key,
            'DD-APPLICATION-KEY': dd_app_key,
            'Accept': 'application/json'
        }

        if dd_api_domain:
            self.__dd_host = 'https://api.{}'.format(dd_api_domain)
        else:
            self.__dd_host = 'https://api.datadoghq.com'

    def get_connection(self):
        try:
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = self.__dd_api_key
            configuration.api_key["appKeyAuth"] = self.__dd_app_key
            if self.dd_api_domain:
                configuration.server_variables["site"] = self.dd_api_domain
            configuration.unstable_operations["query_timeseries_data"] = True
            configuration.compress = False
            configuration.enable_retry = True
            configuration.max_retries = 20
            return configuration
        except Exception as e:
            logger.error(f"Error while initializing Datadog API Processor: {e}")
            raise Exception("Error while initializing Datadog API Processor: {}".format(e))

    def test_connection(self):
        try:
            configuration = self.get_connection()
            with ApiClient(configuration) as api_client:
                api_instance = AuthenticationApi(api_client)
                response: AuthenticationValidationResponse = api_instance.validate()
                if not response.get('valid', False):
                    raise Exception("Datadog API connection is not valid. Check API Key")
                return True
        except ApiException as e:
            logger.error("Exception when calling AuthenticationApi->validate: %s\n" % e)
            raise e

    def fetch_metric_timeseries(self, queries: [str], formulas: [str] = None, interval: int = 300000,
                                start_time_epoch: int = None, end_time_epoch: int = None):
        if not end_time_epoch:
            end_time_epoch = current_epoch()
        if not start_time_epoch:
            start_time_epoch = end_time_epoch - 3600
        if not queries:
            raise Exception("No metric queries provided to fetch timeseries data from datadog")
        try:
            queries_list = [
                {
                    "query": query,
                    "name": "a" if i == 0 else "b"
                } for i, query in enumerate(queries)
            ]

            from_tr = start_time_epoch * 1000
            to_tr = end_time_epoch * 1000

            query_formulas: [QueryFormula] = []
            if formulas:
                for f in formulas:
                    query_formulas.append(
                        QueryFormula(formula=f['formula'], limit=FormulaLimit(count=10, order=QuerySortOrder.DESC)))

            timeseries_queries: [MetricsTimeseriesQuery] = []
            for query in queries_list:
                timeseries_queries.append(MetricsTimeseriesQuery(
                    data_source=MetricsDataSource.METRICS,
                    name=query['name'],
                    query=query['query']
                ))

            body = TimeseriesFormulaQueryRequest(
                data=TimeseriesFormulaRequest(
                    attributes=TimeseriesFormulaRequestAttributes(
                        formulas=query_formulas,
                        _from=from_tr,
                        interval=interval,
                        queries=TimeseriesFormulaRequestQueries(timeseries_queries),
                        to=to_tr,
                    ),
                    type=TimeseriesFormulaRequestType.TIMESERIES_REQUEST,
                ),
            )
            configuration = self.get_connection()
            with ApiClient(configuration) as api_client:
                api_instance = MetricsApi(api_client)
                try:
                    response: TimeseriesFormulaQueryResponse = api_instance.query_timeseries_data(body=body)
                    if response:
                        result = response.data.attributes
                except Exception as e:
                    logger.error(f"Exception occurred while fetching metric timeseries with error: {e}")
                    raise e
            labeled_metric_timeseries = []
            for itr, item in enumerate(result.series.value):
                group_tags = item.group_tags.value
                metric_labels: [LabelValuePair] = []
                if item.unit:
                    unit = item.unit[0].name
                else:
                    unit = ''
                for gt in group_tags:
                    metric_labels.append(
                        LabelValuePair(name=StringValue(value='resource_name'), value=StringValue(value=gt)))

                metric_labels.append(
                    LabelValuePair(name=StringValue(value='offset_seconds'), value=StringValue(value='0'))
                )

                times = result.times.value
                values = result.values.value[itr].value
                datapoints: [TimeseriesResult.LabeledMetricTimeseries.Datapoint] = []
                for it, val in enumerate(values):
                    datapoints.append(TimeseriesResult.LabeledMetricTimeseries.Datapoint(timestamp=int(times[it]),
                                                                                         value=DoubleValue(
                                                                                             value=val)))

                labeled_metric_timeseries.append(
                    TimeseriesResult.LabeledMetricTimeseries(metric_label_values=metric_labels,
                                                             unit=StringValue(value=unit), datapoints=datapoints))

            metric = ' '.join(queries)
            timeseries_result = TimeseriesResult(metric_expression=StringValue(value=metric),
                                                 labeled_metric_timeseries=labeled_metric_timeseries)
            task_result = Result(type=ResultType.TIMESERIES, timeseries=timeseries_result)
            return proto_to_dict(task_result)
        except Exception as e:
            logger.error(f"Exception occurred while fetching metric timeseries with error: {e}")
            raise e
