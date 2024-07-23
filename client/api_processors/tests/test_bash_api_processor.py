import pytest
from client.api_processors.api.bash_api_processor import BashApiProcessor


def test_bash_api_processor():
    processor = BashApiProcessor()
    result = processor.execute_http_get_api('echo "Hello World"')
    assert result["stdout"] == "Hello World"
    assert result["stderr"] == ""
    assert result["returncode"] == 0

    result = processor.execute_http_get_api('exit 1')
    assert result["returncode"] == 1
    assert "Command execution failed" in result["error"]

