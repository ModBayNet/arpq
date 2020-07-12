import abc

from typing import Any


class ABCEncoder(abc.ABC):
    """Encoder interface."""

    @abc.abstractmethod
    def encode(self, data: Any) -> bytes:
        """Encode data."""

    @abc.abstractmethod
    def decode(self, stream: bytes) -> Any:
        """Dencode data."""
