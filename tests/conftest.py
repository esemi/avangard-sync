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
    client = AvangardApi(
        '/tmp',
        10,
        headless=not app_settings.debug,
    )
    await client.setup_browser()
    yield client
    await client.terminate()


@pytest.fixture
async def avangard_client_authorized(avangard_client: AvangardApi):
    res = await avangard_client.login(app_settings.avangard_login, app_settings.avangard_password)
    assert res

    yield avangard_client
