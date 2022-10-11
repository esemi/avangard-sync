import pytest

from app.avangard_client import AvangardApi
from app.settings import app_settings
from tests.utils import avangard_client_configured


@pytest.mark.skipif(
    not avangard_client_configured(), reason="requires configured settings.avangard_[login|password]"
)
async def test_login_happy_path(avangard_client: AvangardApi):
    assert not avangard_client.authorized

    res = await avangard_client.login(app_settings.avangard_login, app_settings.avangard_password)

    assert res is True
    assert avangard_client.authorized


async def test_login_failed(avangard_client: AvangardApi):
    res = await avangard_client.login('invalid-login', 'invalid-password')

    assert res is False
    assert not avangard_client.authorized
