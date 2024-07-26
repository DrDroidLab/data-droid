"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.struct_pb2
import google.protobuf.wrappers_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _ResultType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _ResultTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_ResultType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    UNKNOWN: _ResultType.ValueType  # 0
    TIMESERIES: _ResultType.ValueType  # 1
    TABLE: _ResultType.ValueType  # 2
    API_RESPONSE: _ResultType.ValueType  # 3
    BASH_COMMAND_OUTPUT: _ResultType.ValueType  # 4
    TEXT: _ResultType.ValueType  # 5
    LOGS: _ResultType.ValueType  # 6

class ResultType(_ResultType, metaclass=_ResultTypeEnumTypeWrapper): ...

UNKNOWN: ResultType.ValueType  # 0
TIMESERIES: ResultType.ValueType  # 1
TABLE: ResultType.ValueType  # 2
API_RESPONSE: ResultType.ValueType  # 3
BASH_COMMAND_OUTPUT: ResultType.ValueType  # 4
TEXT: ResultType.ValueType  # 5
LOGS: ResultType.ValueType  # 6
global___ResultType = ResultType

@typing.final
class LabelValuePair(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    @property
    def name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def value(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        value: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["name", b"name", "value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["name", b"name", "value", b"value"]) -> None: ...

global___LabelValuePair = LabelValuePair

@typing.final
class TimeseriesResult(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class LabeledMetricTimeseries(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        @typing.final
        class Datapoint(google.protobuf.message.Message):
            DESCRIPTOR: google.protobuf.descriptor.Descriptor

            TIMESTAMP_FIELD_NUMBER: builtins.int
            VALUE_FIELD_NUMBER: builtins.int
            timestamp: builtins.int
            @property
            def value(self) -> google.protobuf.wrappers_pb2.DoubleValue: ...
            def __init__(
                self,
                *,
                timestamp: builtins.int = ...,
                value: google.protobuf.wrappers_pb2.DoubleValue | None = ...,
            ) -> None: ...
            def HasField(self, field_name: typing.Literal["value", b"value"]) -> builtins.bool: ...
            def ClearField(self, field_name: typing.Literal["timestamp", b"timestamp", "value", b"value"]) -> None: ...

        METRIC_LABEL_VALUES_FIELD_NUMBER: builtins.int
        UNIT_FIELD_NUMBER: builtins.int
        DATAPOINTS_FIELD_NUMBER: builtins.int
        @property
        def metric_label_values(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___LabelValuePair]: ...
        @property
        def unit(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        @property
        def datapoints(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___TimeseriesResult.LabeledMetricTimeseries.Datapoint]: ...
        def __init__(
            self,
            *,
            metric_label_values: collections.abc.Iterable[global___LabelValuePair] | None = ...,
            unit: google.protobuf.wrappers_pb2.StringValue | None = ...,
            datapoints: collections.abc.Iterable[global___TimeseriesResult.LabeledMetricTimeseries.Datapoint] | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing.Literal["unit", b"unit"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing.Literal["datapoints", b"datapoints", "metric_label_values", b"metric_label_values", "unit", b"unit"]) -> None: ...

    METRIC_NAME_FIELD_NUMBER: builtins.int
    METRIC_EXPRESSION_FIELD_NUMBER: builtins.int
    LABELED_METRIC_TIMESERIES_FIELD_NUMBER: builtins.int
    @property
    def metric_name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def metric_expression(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def labeled_metric_timeseries(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___TimeseriesResult.LabeledMetricTimeseries]: ...
    def __init__(
        self,
        *,
        metric_name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        metric_expression: google.protobuf.wrappers_pb2.StringValue | None = ...,
        labeled_metric_timeseries: collections.abc.Iterable[global___TimeseriesResult.LabeledMetricTimeseries] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["metric_expression", b"metric_expression", "metric_name", b"metric_name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["labeled_metric_timeseries", b"labeled_metric_timeseries", "metric_expression", b"metric_expression", "metric_name", b"metric_name"]) -> None: ...

global___TimeseriesResult = TimeseriesResult

@typing.final
class TableResult(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class TableColumn(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        NAME_FIELD_NUMBER: builtins.int
        TYPE_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        @property
        def name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        @property
        def type(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        @property
        def value(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        def __init__(
            self,
            *,
            name: google.protobuf.wrappers_pb2.StringValue | None = ...,
            type: google.protobuf.wrappers_pb2.StringValue | None = ...,
            value: google.protobuf.wrappers_pb2.StringValue | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing.Literal["name", b"name", "type", b"type", "value", b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing.Literal["name", b"name", "type", b"type", "value", b"value"]) -> None: ...

    @typing.final
    class TableRow(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        COLUMNS_FIELD_NUMBER: builtins.int
        @property
        def columns(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___TableResult.TableColumn]: ...
        def __init__(
            self,
            *,
            columns: collections.abc.Iterable[global___TableResult.TableColumn] | None = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing.Literal["columns", b"columns"]) -> None: ...

    RAW_QUERY_FIELD_NUMBER: builtins.int
    TOTAL_COUNT_FIELD_NUMBER: builtins.int
    ROWS_FIELD_NUMBER: builtins.int
    @property
    def raw_query(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def total_count(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def rows(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___TableResult.TableRow]: ...
    def __init__(
        self,
        *,
        raw_query: google.protobuf.wrappers_pb2.StringValue | None = ...,
        total_count: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        rows: collections.abc.Iterable[global___TableResult.TableRow] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["raw_query", b"raw_query", "total_count", b"total_count"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["raw_query", b"raw_query", "rows", b"rows", "total_count", b"total_count"]) -> None: ...

global___TableResult = TableResult

@typing.final
class ApiResponseResult(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REQUEST_METHOD_FIELD_NUMBER: builtins.int
    REQUEST_URL_FIELD_NUMBER: builtins.int
    RESPONSE_STATUS_FIELD_NUMBER: builtins.int
    RESPONSE_HEADERS_FIELD_NUMBER: builtins.int
    RESPONSE_BODY_FIELD_NUMBER: builtins.int
    ERROR_FIELD_NUMBER: builtins.int
    METADATA_FIELD_NUMBER: builtins.int
    @property
    def request_method(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def request_url(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def response_status(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def response_headers(self) -> google.protobuf.struct_pb2.Struct: ...
    @property
    def response_body(self) -> google.protobuf.struct_pb2.Struct: ...
    @property
    def error(self) -> google.protobuf.struct_pb2.Struct: ...
    @property
    def metadata(self) -> google.protobuf.struct_pb2.Struct: ...
    def __init__(
        self,
        *,
        request_method: google.protobuf.wrappers_pb2.StringValue | None = ...,
        request_url: google.protobuf.wrappers_pb2.StringValue | None = ...,
        response_status: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        response_headers: google.protobuf.struct_pb2.Struct | None = ...,
        response_body: google.protobuf.struct_pb2.Struct | None = ...,
        error: google.protobuf.struct_pb2.Struct | None = ...,
        metadata: google.protobuf.struct_pb2.Struct | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["error", b"error", "metadata", b"metadata", "request_method", b"request_method", "request_url", b"request_url", "response_body", b"response_body", "response_headers", b"response_headers", "response_status", b"response_status"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["error", b"error", "metadata", b"metadata", "request_method", b"request_method", "request_url", b"request_url", "response_body", b"response_body", "response_headers", b"response_headers", "response_status", b"response_status"]) -> None: ...

global___ApiResponseResult = ApiResponseResult

@typing.final
class BashCommandOutputResult(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class CommandOutput(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        COMMAND_FIELD_NUMBER: builtins.int
        OUTPUT_FIELD_NUMBER: builtins.int
        @property
        def command(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        @property
        def output(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        def __init__(
            self,
            *,
            command: google.protobuf.wrappers_pb2.StringValue | None = ...,
            output: google.protobuf.wrappers_pb2.StringValue | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing.Literal["command", b"command", "output", b"output"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing.Literal["command", b"command", "output", b"output"]) -> None: ...

    COMMAND_OUTPUTS_FIELD_NUMBER: builtins.int
    @property
    def command_outputs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___BashCommandOutputResult.CommandOutput]: ...
    def __init__(
        self,
        *,
        command_outputs: collections.abc.Iterable[global___BashCommandOutputResult.CommandOutput] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["command_outputs", b"command_outputs"]) -> None: ...

global___BashCommandOutputResult = BashCommandOutputResult

@typing.final
class TextResult(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    OUTPUT_FIELD_NUMBER: builtins.int
    @property
    def output(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        output: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["output", b"output"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["output", b"output"]) -> None: ...

global___TextResult = TextResult

@typing.final
class Result(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ERROR_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    TIMESERIES_FIELD_NUMBER: builtins.int
    TABLE_FIELD_NUMBER: builtins.int
    API_RESPONSE_FIELD_NUMBER: builtins.int
    BASH_COMMAND_OUTPUT_FIELD_NUMBER: builtins.int
    TEXT_FIELD_NUMBER: builtins.int
    LOGS_FIELD_NUMBER: builtins.int
    type: global___ResultType.ValueType
    @property
    def error(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def timeseries(self) -> global___TimeseriesResult: ...
    @property
    def table(self) -> global___TableResult: ...
    @property
    def api_response(self) -> global___ApiResponseResult: ...
    @property
    def bash_command_output(self) -> global___BashCommandOutputResult: ...
    @property
    def text(self) -> global___TextResult: ...
    @property
    def logs(self) -> global___TableResult: ...
    def __init__(
        self,
        *,
        error: google.protobuf.wrappers_pb2.StringValue | None = ...,
        type: global___ResultType.ValueType = ...,
        timeseries: global___TimeseriesResult | None = ...,
        table: global___TableResult | None = ...,
        api_response: global___ApiResponseResult | None = ...,
        bash_command_output: global___BashCommandOutputResult | None = ...,
        text: global___TextResult | None = ...,
        logs: global___TableResult | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["api_response", b"api_response", "bash_command_output", b"bash_command_output", "error", b"error", "logs", b"logs", "result", b"result", "table", b"table", "text", b"text", "timeseries", b"timeseries"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["api_response", b"api_response", "bash_command_output", b"bash_command_output", "error", b"error", "logs", b"logs", "result", b"result", "table", b"table", "text", b"text", "timeseries", b"timeseries", "type", b"type"]) -> None: ...
    def WhichOneof(self, oneof_group: typing.Literal["result", b"result"]) -> typing.Literal["timeseries", "table", "api_response", "bash_command_output", "text", "logs"] | None: ...

global___Result = Result
