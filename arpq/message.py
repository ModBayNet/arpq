from __future__ import annotations

from typing import Any

from .abc import ABCEncoder


class Message:
    """Message returned from queue. Should not be created manually."""

    __slots__ = frozenset(("_priority", "_data"))

    def __init__(self, priority: int, data: Any):
        self._priority = priority
        self._data = data

    @classmethod
    def _from_zpopmax(cls, resp: Any, encoder: ABCEncoder) -> Message:
        return cls(priority=int(resp[1]), data=encoder.decode(resp[0]))

    @classmethod
    def _from_bzpopmax(cls, resp: Any, encoder: ABCEncoder) -> Message:
        return cls(priority=int(resp[2]), data=encoder.decode(resp[1]))

    @property
    def priority(self) -> int:
        """Message priority."""

        return self._priority

    @property
    def data(self) -> Any:
        """Message data."""

        return self._data

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} priority={self.priority} data={self.data}>"
