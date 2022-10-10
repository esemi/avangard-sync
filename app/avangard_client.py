"""Avangard.ru internal api client."""
from __future__ import annotations

import asyncio
import dataclasses
import logging
import random
from decimal import Decimal

import httpx

from app.settings import app_settings

LOGIN_URL = 'https://login.avangard.ru/client4/afterlogin'


@dataclasses.dataclass
class AvangardPayment:
    """Payment model for avangard."""

    id: int
    from_inn: int
    from_company: str
    invoice_number: str
    description: str
    income_amount: Decimal


class AvangardApi:
    """API client."""

    def __init__(self) -> None:
        """Create new client."""
        self.authorized: bool = False
        self._client: httpx.AsyncClient | None = None

    async def close(self) -> None:
        """Close client and logout from bank."""
        self.authorized = False
        if self._client:
            # todo logout
            await self._client.aclose()
            self._client = None

    async def wait_like_a_human(self) -> None:
        """Block calls for a random time like a real user."""
        waiting_time = app_settings.avangard_human_waiting_time * random.random()
        logging.debug(f'sleep {waiting_time=} seconds')
        await asyncio.sleep(waiting_time)

    async def conn(self, login: str, password: str) -> bool:
        """Auth on avangard.ru."""
        await self.close()
        self._client = httpx.AsyncClient(
            max_redirects=5,
            follow_redirects=True,
            timeout=app_settings.avangard_http_timeout,
            headers={
                b'User-Agent': app_settings.http_user_agent,
            },
        )

        try:  # noqa: WPS229
            response = await self._client.post(
                LOGIN_URL,
                params={
                    'login_v': '',
                    'login': login,
                    'passwd_v': '',
                    'passwd': password,
                    'nw': 1,
                },
            )
            response.raise_for_status()
            logging.debug('Avangard auth response {0} {1}', response.url, response.status_code)
            self.authorized = b'ticket' in response.url.query
        except httpx.HTTPError as fetch_exc:
            logging.warning('authentication failed', fetch_exc)

        await self.wait_like_a_human()
        return self.authorized
