import asyncio

import pytest

from app.settings import app_settings
from app.avangard_client import AvangardApi


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def avangard_client() -> AvangardApi:
    yield AvangardApi()


@pytest.fixture
async def avangard_client_authorized(avangard_client: AvangardApi):
    await avangard_client.conn(app_settings.avangard_login, app_settings.avangard_password)
    yield avangard_client
    await avangard_client.close()
