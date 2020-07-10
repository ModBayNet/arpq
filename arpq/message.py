from __future__ import annotations

from typing import Any

from .abc import ABCEncoder


class Message:
    __slots__ = ("_priority", "_data")

    def __init__(self, priority: int, data: Any):
        self._priority = priority
        self._data = data

    @classmethod
    def _from_zpopmax(cls, resp: Any, encoder: ABCEncoder) -> Message:
        return cls(priority=resp[1], data=encoder.decode(resp[0]))

    @classmethod
    def _from_bzpopmax(cls, resp: Any, encoder: ABCEncoder) -> Message:
        return cls(priority=resp[2], data=encoder.decode(resp[1]))

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def data(self) -> Any:
        return self._data

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} priority={self.priority} data={self.data}>"
