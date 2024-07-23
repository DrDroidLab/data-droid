import pytest
from client.api_processors.executor_interface import ExecutorInterface


class DummyExecutor(ExecutorInterface):

    def execute_http_request(self, request_method, path, headers=None, params=None):
        return "Request Executed"

    def execute_http_get_api(self, url, headers=None, params=None):
        return "GET API Executed"


def test_dummy_executor():
    executor = DummyExecutor()
    assert executor.execute_http_request("GET", "/path") == "Request Executed"
    assert executor.execute_http_get_api("/url") == "GET API Executed"
