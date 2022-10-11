import datetime

import pytest

from app.avangard_client import AvangardApi
from tests.utils import avangard_client_configured


@pytest.mark.skipif(
    not avangard_client_configured(), reason="requires configured settings.avangard_[login|password]"
)
async def test_get_payments_happy_path(avangard_client_authorized: AvangardApi):
    start_date = datetime.date(year=2020, month=1, day=1)
    end_date = datetime.date(year=2020, month=12, day=31)

    res = await avangard_client_authorized.get_income_payments(start_date, end_date)

    assert isinstance(res, list)
    assert len(res) >= 1
    assert res[0].payment_number


async def test_get_payments_unauthorized(avangard_client: AvangardApi):
    with pytest.raises(RuntimeError):
        await avangard_client.get_income_payments(
            datetime.date(year=2020, month=1, day=1),
            datetime.date(year=2020, month=12, day=31),
        )
