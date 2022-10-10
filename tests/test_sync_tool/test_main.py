from app.sync_tool import main


async def test_main_happy_path():
    res = await main(throttling_max_time=1.0, max_iterations=2)

    assert res['success'] == 2
    assert res['iteration'] == 2
    assert res['fails'] == 0