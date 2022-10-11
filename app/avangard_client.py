"""Avangard.ru internal api client."""
from __future__ import annotations

import logging
from datetime import date

from playwright.async_api import BrowserContext, Page, Playwright
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright

from app.avangard_parser import AvangardPayment, parse_income_payments

LOGIN_START_PAGE = 'https://login.avangard.ru/'
MAIN_PAGE = 'https://corp.avangard.ru/clbAvn/faces/facelet-pages/iday_balance.jspx'


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

    async def get_income_payments(  # noqa: WPS217
        self,
        start_date: date,
        end_date: date,
    ) -> list[AvangardPayment]:
        """Return list of income payments."""
        page = await self._get_page()
        await page.goto(MAIN_PAGE)
        logging.debug(f'open main page {page.url}')

        self.authorized = await self._check_authorized(page)
        if not self.authorized:
            raise RuntimeError('Unauthorized')

        await page.locator('//input[@value="Выписки и отчеты"]').click()
        logging.debug(f'open reports page {page.url}')

        await self._fill_search_form(
            page,
            start_date.strftime('%d.%m.%Y'),
            end_date.strftime('%d.%m.%Y'),
        )

        await page.locator('//img[@title="Показать"]').click()
        logging.debug('click search')

        try:
            await page.locator('//div[@class="pageTitle"]').wait_for(
                timeout=self._locator_timeout_ms,
            )
        except PlaywrightTimeout:
            raise RuntimeError('Search payments failed')

        return parse_income_payments(await page.content())

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

    async def _fill_search_form(self, page: Page, start_date: str, end_date: str) -> None:
        await page.locator('//input[@name="docslist:main:startdate"]').fill(
            value=start_date,
            timeout=self._locator_timeout_ms,
        )
        await page.locator('//input[@name="docslist:main:finishdate"]').fill(
            value=end_date,
            timeout=self._locator_timeout_ms,
        )
        logging.debug('fill search payments form')

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
