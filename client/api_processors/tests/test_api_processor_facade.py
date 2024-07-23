import pytest
from client.api_processors.api.api_processor import ApiSource, ApiProcessor
from client.api_processors.api.bash_api_processor import BashApiProcessor
from client.api_processors.api.api_processor_facade import ApiProcessorFacade


def test_api_processor_facade():
    facade = ApiProcessorFacade()
    bash_processor = BashApiProcessor()

    facade.register(ApiSource.BASH, bash_processor)

    assert facade.get_source_api_processor(ApiSource.BASH) == bash_processor

    with pytest.raises(ValueError):
        facade.get_source_api_processor(ApiSource.UNKNOWN)