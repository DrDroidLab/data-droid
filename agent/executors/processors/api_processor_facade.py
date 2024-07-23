from .api_processor import ApiSource, ApiProcessor
from .bash_api_processor import BashApiProcessor


class ApiProcessorFacade:

    def __init__(self):
        self._map = {}

    def register(self, source: ApiSource, api_processor: ApiProcessor):
        self._map[source] = api_processor

    def get_source_api_processor(self, source: ApiSource):
        if source not in self._map:
            raise ValueError(f'No api processor found for source: {source}')
        source = self._map[source]
        if not source.configured:
            raise ValueError(f'Api processor not configured for source: {source.source}')
        return source


api_processor_facade = ApiProcessorFacade()
api_processor_facade.register(ApiSource.BASH, BashApiProcessor())
