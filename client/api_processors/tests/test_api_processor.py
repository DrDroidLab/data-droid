import pytest
from client.api_processors.api.api_processor import ApiProcessor, ApiSource


class TestApiProcessor(ApiProcessor):
    def execute_http_get_api(self, url, headers=None, params=None):
        return "GET API Executed"


def test_api_processor():
    processor = TestApiProcessor()
    assert processor.execute_http_request("GET", "/path") == "GET API Executed"
    with pytest.raises(NotImplementedError):
        processor.execute_http_request("POST", "/path")
    with pytest.raises(ValueError):
        processor.execute_http_request("DELETE", "/path")