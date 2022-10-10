"""This module periodically update actual cash and forex rates to the database."""

import asyncio
import logging
import signal
from collections import Counter
from typing import Optional

from app.settings import app_settings

FORCE_SHUTDOWN = False


def sigint_handler(current_signal, frame) -> None:  # type: ignore
    """Handle correct signal for restart service."""
    global FORCE_SHUTDOWN  # noqa: WPS420
    FORCE_SHUTDOWN = True  # noqa: WPS442


async def main(throttling_max_time: float, max_iterations: Optional[int] = None) -> Counter:  # noqa: WPS231
    """
    Background task for sync payments between avangard and moy sklad.

    - get incomming payments from avangard bank
    - get wait-orders from moy sklad
    - close orders by payments from bank

    """
    # todo test

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
    # todo impl
    # todo test
    return True


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
