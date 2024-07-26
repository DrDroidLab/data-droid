from abc import ABC, abstractmethod


class Processor(ABC):

    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def test_connection(self):
        pass
