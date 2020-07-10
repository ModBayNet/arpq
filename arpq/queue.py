import time

from typing import Any, List, Type, Union, Iterable, Awaitable

from aioredis.abc import AbcConnection

from .abc import ABCEncoder
from .encoder import MarshalEncoder
from .message import Message

_RedisResponseType = Any


class MessageQueue:

    __slots__ = ("_redis", "_channel", "_encoder")

    def __init__(
        self,
        redis: AbcConnection,
        channel: str,
        encoder_cls: Type[ABCEncoder] = MarshalEncoder,
    ):
        self._redis = redis
        self._channel = channel
        self._encoder = encoder_cls()

    # TODO: batches
    async def drain(self) -> List[Message]:
        return await self.get(count=await self.get_length())

    async def put(self, msg: Union[Message, Iterable[Message]]) -> None:
        if not isinstance(msg, Iterable):
            msg = [msg]

        for i in msg:
            await self._redis.execute(
                "ZINCRBY", self._channel, i.priority, self._encoder.encode(i.data)
            )

    # TODO: batches
    async def get(self, count: int = 1, timeout: int = 0) -> List[Message]:
        if timeout != 0:
            start_time = time.time()

        popped: List[Message] = []

        for resp in await self._pop_all(count):
            popped.append(Message._from_zpopmax(resp, self._encoder))

        while len(popped) < count:
            if timeout != 0 and start_time + timeout > time.time():
                break

            popped.append(
                Message._from_bzpopmax(await self._wait_one(timeout), self._encoder)
            )

            for resp in await self._pop_all(count - len(popped)):
                popped.append(Message._from_zpopmax(resp, self._encoder))

        return popped

    def _wait_one(self, timeout: int) -> Awaitable[_RedisResponseType]:
        return self._redis.execute("BZPOPMAX", self._channel, timeout)

    async def _pop_all(self, count: int) -> Iterable[_RedisResponseType]:
        popped = await self._redis.execute("ZPOPMAX", self._channel, count)

        # group responses into tuples: (data, priority)
        return list(zip(popped[::2], popped[1::2]))

    async def get_length(self) -> int:
        return await self._redis.execute("ZCARD", self._channel)

    async def is_empty(self) -> bool:
        return await self.get_length() == 0

    @property
    def channel(self) -> str:
        return self._channel
