import time

import pytest

from arpq import JSONEncoder, MessageQueue

pytestmark = pytest.mark.asyncio


async def test_properties(redis_connection):
    channel_name = "queue:test_properties"
    queue = MessageQueue(redis_connection, channel_name, encoder_cls=JSONEncoder)

    assert queue.channel == channel_name


async def test_single_message(redis_connection):
    queue = MessageQueue(
        redis_connection, "queue:test_single_message", encoder_cls=JSONEncoder
    )
    await queue.drain()

    data = "Hello World"
    await queue.put(0, data)

    assert data == (await queue.get())[0].data


async def test_many_messages(redis_connection):
    queue = MessageQueue(
        redis_connection, "queue:test_many_messages", encoder_cls=JSONEncoder
    )
    await queue.drain()

    num_elements = 10

    assert 0 == await queue.get_length()
    assert await queue.is_empty()

    await queue.put_many([(i, str(i)) for i in range(num_elements)])

    assert num_elements == await queue.get_length()
    assert not await queue.is_empty()

    assert num_elements - 1 == len(await queue.get(num_elements - 1))

    await queue.drain()

    assert await queue.is_empty()


async def test_priority(redis_connection):
    queue = MessageQueue(
        redis_connection, "queue:test_priority", encoder_cls=JSONEncoder
    )
    await queue.drain()

    low_priority_data = "low"
    high_priority_data = "high"

    msg_low = (-10, low_priority_data)
    msg_high = (10, high_priority_data)

    await queue.put_many([msg_low, msg_high])

    assert high_priority_data == (await queue.get())[0].data

    await queue.drain()

    await queue.put(1, "test")
    await queue.put(1, "test")

    assert 1 == await queue.get_length()
    assert 2 == (await queue.get())[0].priority


async def test_timeout(redis_connection):
    queue = MessageQueue(
        redis_connection, "queue:test_timeout", encoder_cls=JSONEncoder
    )
    await queue.drain()

    timeout = 3

    await queue.put(0, 42)
    assert 1 == len(await queue.get(timeout=timeout))

    start_time = time.time()

    assert 0 == len(await queue.get(timeout=timeout))
    assert time.time() - start_time > timeout
