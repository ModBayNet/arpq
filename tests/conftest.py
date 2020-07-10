import asyncio

import pytest
import aioredis


@pytest.yield_fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def redis_connection():
    conn = await aioredis.create_connection("redis://localhost/0")
    yield conn
    conn.close()
