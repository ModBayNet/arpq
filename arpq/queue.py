import math
import time

from typing import Any, List, Type, Tuple, Union, Iterable, Awaitable

from aioredis.abc import AbcConnection

from .abc import ABCEncoder
from .message import Message
from .encoders import MarshalEncoder

_RedisResponseType = Any


class MessageQueue:

    """
    Message queue based on sorted set Redis data type.

    Can be used for both receiving and sending items.
    """

    __slots__ = frozenset(("_redis", "_channel", "_encoder"))

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
        """Remove all items from queue and return them."""

        return await self.get(count=await self.get_length())

    async def put(self, priority: int, data: Any) -> None:
        """
        Put a single item into queue. If item exists in queue, priority is increased by
        `priority`.
        """

        await self._redis.execute(
            "ZINCRBY", self._channel, priority, self._encoder.encode(data)
        )

    # TODO: batches?
    async def put_many(self, pairs: Iterable[Tuple[int, Any]]) -> None:
        """
        Put multiple items into queue. Updates priorities of conficting items in queue.
        """

        # TODO: a more efficient way maybe?
        args: List[Union[int, Any]] = []
        for priority, data in pairs:
            args.extend((priority, self._encoder.encode(data)))

        await self._redis.execute(
            "ZADD", self._channel, *args,
        )

    # TODO: batches
    async def get(self, count: int = 1, timeout: int = 0) -> List[Message]:
        """
        Get items from queue. Can get multiple items at once.

        If timeout is reached, returns all items received before timeout.
        Timeout condition can be checked by comparing length of returned list vs
        requested count.
        """

        if timeout != 0:
            start_time = time.time()

        popped: List[Message] = []

        for resp in await self._pop_all(count):
            popped.append(Message._from_zpopmax(resp, self._encoder))

        while len(popped) < count:
            if timeout != 0 and start_time + timeout < time.time():
                break

            resp = await self._wait_one(math.ceil(start_time - time.time() + timeout))
            if resp is not None:
                # None is returned in case of timeout, but users may send None too
                popped.append(Message._from_bzpopmax(resp, self._encoder))

            for resp in await self._pop_all(count - len(popped)):
                popped.append(Message._from_zpopmax(resp, self._encoder))

        return popped

    def _wait_one(self, timeout: int) -> Awaitable[_RedisResponseType]:
        return self._redis.execute("BZPOPMAX", self._channel, timeout)

    async def _pop_all(self, count: int) -> Iterable[_RedisResponseType]:
        if count <= 0:
            return ()

        popped = await self._redis.execute("ZPOPMAX", self._channel, count)

        # group responses into tuples: (data, priority)
        return list(zip(popped[::2], popped[1::2]))

    async def get_length(self) -> int:
        """Return number of items in queue."""

        return await self._redis.execute("ZCARD", self._channel)

    async def is_empty(self) -> bool:
        """Check if queue is empty or not."""

        return await self.get_length() == 0

    @property
    def channel(self) -> str:
        """Redis queue channel ."""

        return self._channel

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} channel={self.channel}>"
