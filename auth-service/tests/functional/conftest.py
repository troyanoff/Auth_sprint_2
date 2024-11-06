import asyncio
import json
import pytest
import pytest_asyncio
import os

from aiohttp import ClientSession, RequestInfo

from .settings import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def http_session():
    sess = ClientSession()
    yield sess
    await sess.close()


@pytest_asyncio.fixture
def make_get_request(http_session: ClientSession):
    async def inner(path: str, params: dict = {}, headers: dict = {}) -> RequestInfo:
        url = os.path.join(settings.service_url, path)
        async with http_session.get(url, params=params, headers=headers) as response:
            body = await response.json(content_type=None)
            headers = response.headers
            status = response.status
        return body, headers, status

    return inner


@pytest_asyncio.fixture
def make_post_request(http_session: ClientSession):
    async def inner(
        path: str, params: dict = {}, headers: dict = {}, body: dict = {}
    ) -> RequestInfo:
        url = os.path.join(settings.service_url, path)
        body = json.dumps(body)
        async with http_session.post(
            url, params=params, headers=headers, data=body
        ) as response:
            body = await response.json(content_type=None)
            headers = response.headers
            status = response.status
        return body, headers, status

    return inner
