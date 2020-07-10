import abc

from typing import Any


class ABCEncoder(abc.ABC):
    @abc.abstractmethod
    def encode(self, data: Any) -> bytes:
        ...

    @abc.abstractmethod
    def decode(self, stream: bytes) -> Any:
        ...
