import pytest
from client.executors.api.api_processor import ApiSource, ApiProcessor
from client.executors.api.bash_api_processor import BashApiProcessor
from client.executors.api.api_processor_facade import ApiProcessorFacade



def test_api_processor_facade():
    facade = ApiProcessorFacade()
    bash_processor = BashApiProcessor()

    facade.register(ApiSource.BASH, bash_processor)

    assert facade.get_source_api_processor(ApiSource.BASH) == bash_processor

    with pytest.raises(ValueError):
        facade.get_source_api_processor(ApiSource.UNKNOWN)