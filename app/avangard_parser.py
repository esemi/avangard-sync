"""Avangard.ru objects parser."""

from __future__ import annotations

import dataclasses
import datetime
import logging
from decimal import Decimal

from lxml import etree

stringify = etree.XPath("string()")


@dataclasses.dataclass
class AvangardPayment:
    """Payment model for avangard."""

    payment_number: int
    payment_date: datetime.date
    agent_inn: int
    agent_company_name: str
    invoice_number: str
    income_amount: Decimal
    description: str


def parse_income_payments(html_source: str) -> list[AvangardPayment]:
    """Return income avangard payments from html source."""
    # todo test
    payment_rows = etree.HTML(html_source).xpath('//table[@class="x2f"]//tr')
    logging.debug(f'fetch payment rows {payment_rows=}')
    if not payment_rows:
        return []

    result: list[AvangardPayment] = []
    for row in payment_rows:
        payment = _parse_income_payment_row(row)
        logging.debug(f'parse row result {row}')
        if payment:
            result.append(payment)

    return result


def _parse_income_payment_row(row: etree._Element) -> AvangardPayment | None:
    cells = row.xpath('.//td[@headers]')
    if len(cells) != 9:
        logging.debug(f'Invalid columns count {cells=}')
        return None

    payment_number = int(stringify(cells[6]).strip())
    payment_date = _parse_payment_date(stringify(cells[5]))

    print(payment_number, payment_date)
    # todo impl
    # todo test
    return None


def _parse_payment_date(source: str) -> datetime.date:
    dt = source.strip().replace('"', '')
    return datetime.datetime.strptime(dt, '%d.%m.%Y').date()
