"""Avangard.ru internal api client."""
from __future__ import annotations

import dataclasses
import logging
from decimal import Decimal

from playwright.async_api import BrowserContext, Page, Playwright
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright

LOGIN_START_PAGE = 'https://login.avangard.ru/'
MAIN_PAGE = 'https://corp.avangard.ru/clbAvn/faces/facelet-pages/iday_balance.jspx'


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

    def __init__(  # noqa: WPS211
        self,
        user_dir: str,
        timeout_seconds: float,
        slow_mo: int | None = None,
        headless: bool = True,
        user_agent: str = None,
    ) -> None:
        """Create new client."""
        self.authorized: bool = False
        self._slow_mo = slow_mo
        self._user_agent = user_agent
        self._user_dir = user_dir
        self._headless = headless
        self._base_timeout_ms = timeout_seconds * 1000
        self._locator_timeout_ms = self._base_timeout_ms / 2
        self._playwright_wrapper: Playwright | None = None
        self._browser: BrowserContext | None = None
        self._active_page: Page | None = None
        self._initialized = False

    async def setup_browser(self) -> None:
        """Init browser env."""
        if self._initialized:
            return

        self._playwright_wrapper = await async_playwright().start()
        self._browser = await self._playwright_wrapper.chromium.launch_persistent_context(
            user_data_dir=self._user_dir,
            user_agent=self._user_agent,
            timeout=self._base_timeout_ms,
            headless=self._headless,
            slow_mo=self._slow_mo,
        )
        self._initialized = True

    async def terminate(self) -> None:
        """Close client and logout from bank."""
        logging.debug('close call')
        self.authorized = False
        self._initialized = False

        if self._active_page:
            await self._active_page.close()
            self._active_page = None

        if self._browser:
            logging.debug('close browser')
            await self._browser.close()
            self._browser = None

        if self._playwright_wrapper:
            logging.debug('close wrapper')
            self._playwright_wrapper.stop()
            self._playwright_wrapper = None

    async def login(self, login: str, password: str) -> bool:
        """Login to internet bank."""
        page = await self._get_page()
        await page.goto(LOGIN_START_PAGE)
        logging.debug(f'open start page {page.url}')

        await self._fill_login_form(page, login, password)

        await page.locator('//div[@class="buttonLoginBank"]').click()
        logging.debug('click login')

        self.authorized = await self._check_authorized(page)
        logging.debug(f'check login result {self.authorized}')

        return self.authorized

    async def _check_authorized(self, page: Page) -> bool:
        authorized = True
        try:
            await page.locator('//input[@value="Выписки и отчеты"]').wait_for(
                timeout=self._locator_timeout_ms,
            )
        except PlaywrightTimeout:
            authorized = False
        logging.debug(f'check authorized {authorized}')
        return authorized

    async def _fill_login_form(self, page: Page, login: str, password: str) -> None:
        await page.locator('//input[@name="login_v"]').type(
            text=login,
            timeout=self._locator_timeout_ms,
        )
        await page.locator('//input[@name="passwd_v"]').type(
            text=password,
            timeout=self._locator_timeout_ms,
        )
        logging.debug('fill auth form')

    async def _get_page(self) -> Page:
        if not self._initialized:
            raise RuntimeError('Browser not initialized.')

        if not self._active_page:
            self._active_page = await self._browser.new_page()  # type: ignore

        if not self._active_page:
            raise RuntimeError('Browser.Page not initialized.')

        return self._active_page
