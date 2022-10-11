from app.sync_tool import _get_income_payments


async def test_get_income_payments_happy_path(mocker):
    login_mock = mocker.patch('app.sync_tool.AvangardApi.login')
    get_payments_mock = mocker.patch('app.sync_tool.AvangardApi.get_income_payments', return_value=[])

    res = await _get_income_payments()

    assert len(res) == 0
    assert login_mock.call_count == 1
    assert get_payments_mock.call_count == 1
