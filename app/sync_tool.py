"""This module periodically fetch actual payments from avangard and update orders on moysklad."""

import asyncio
import datetime
import logging
import signal
from collections import Counter
from typing import Optional

from app.avangard_client import AvangardApi
from app.avangard_parser import AvangardPayment
from app.settings import app_settings

FORCE_SHUTDOWN = False


def sigint_handler(current_signal, frame) -> None:  # type: ignore
    """Handle correct signal for restart service."""
    global FORCE_SHUTDOWN  # noqa: WPS420
    FORCE_SHUTDOWN = True  # noqa: WPS442


async def main(  # noqa: WPS231
    throttling_max_time: float,
    max_iterations: Optional[int] = None,
) -> Counter:
    """
    Background task for sync payments between avangard and moy sklad.

    - fetch incoming payments from avangard bank
    - get wait-orders from moysklad
    - close orders by payments from bank

    """
    cnt: Counter = Counter(
        iteration=0,
        fails=0,
        success=0,
    )
    throttling_timer: float = 0
    throttling_timer_chunk: float = min(app_settings.throttling_min_time, throttling_max_time)
    while not max_iterations or cnt['iteration'] < max_iterations:
        if FORCE_SHUTDOWN:
            break

        if cnt['iteration']:
            if throttling_timer < throttling_max_time:
                logging.debug(f'sleep chunk time {throttling_timer=} {throttling_max_time}')
                throttling_timer += throttling_timer_chunk
                await asyncio.sleep(throttling_timer_chunk)
                continue
            else:
                logging.debug('sleep time end')
                throttling_timer = 0

        cnt['iteration'] += 1
        logging.info(f'Current iteration {cnt=}')

        ok = await _process_payments_sync()
        cnt['success' if ok else 'fails'] += 1

    logging.info(f'shutdown {cnt=}')
    return cnt


async def _process_payments_sync() -> bool:
    # todo test
    # todo impl
    await _get_income_payments()

    return True


async def _get_income_payments() -> list[AvangardPayment]:
    # todo test

    avangard_client = AvangardApi(
        user_dir=app_settings.avangard_user_dir,
        timeout_seconds=app_settings.avangard_http_timeout,
        slow_mo=app_settings.avangard_human_slow_factor,
        headless=not app_settings.debug,
        user_agent=app_settings.http_user_agent,
    )
    await avangard_client.setup_browser()

    await avangard_client.login(app_settings.avangard_login, app_settings.avangard_password)
    end_dt = datetime.datetime.utcnow().date()
    start_dt = end_dt - datetime.timedelta(days=7)

    payments = await avangard_client.get_income_payments(start_dt, end_dt)
    logging.debug(f'fetch {len(payments)=}')

    await avangard_client.terminate()
    return payments


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',  # noqa: WPS323
    )

    signal.signal(signal.SIGINT, sigint_handler)

    asyncio.run(main(
        throttling_max_time=app_settings.throttling_time,
        max_iterations=None,
    ))
