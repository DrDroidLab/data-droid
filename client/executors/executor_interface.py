from abc import ABC, abstractmethod


class ExecutorInterface(ABC):

    @abstractmethod
    def execute_http_request(self, request_method, path, headers=None, params=None):
        pass

    @abstractmethod
    def execute_http_get_api(self, url, headers=None, params=None):
        pass
