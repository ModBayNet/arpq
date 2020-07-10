import pytest

from arpq import Message, JSONEncoder, MessageQueue

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
    msg = Message(0, data)
    await queue.put(msg)

    assert msg.data == (await queue.get())[0].data


async def test_many_messages(redis_connection):
    queue = MessageQueue(
        redis_connection, "queue:test_many_messages", encoder_cls=JSONEncoder
    )
    await queue.drain()

    num_elements = 10

    assert 0 == await queue.get_length()
    assert await queue.is_empty()

    await queue.put([Message(i, str(i)) for i in range(num_elements)])

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

    msg_low = Message(-10, low_priority_data)
    msg_high = Message(10, high_priority_data)

    await queue.put([msg_low, msg_high])

    assert high_priority_data == (await queue.get())[0].data
