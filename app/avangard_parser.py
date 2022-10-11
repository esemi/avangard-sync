"""Avangard.ru objects parser."""

from __future__ import annotations

import dataclasses
import datetime
import logging
import re
from decimal import Decimal

from lxml import etree

stringify = etree.XPath('string()')


@dataclasses.dataclass
class AvangardPayment:
    """Payment model for avangard."""

    payment_number: int
    payment_date: datetime.date
    agent_inn: int
    invoice_number: str
    income_amount: Decimal
    description: str


def parse_income_payments(html_source: str) -> list[AvangardPayment]:
    """Return income avangard payments from html source."""
    payment_rows = etree.HTML(html_source).xpath('//table[@class="x2f"]//tr')
    logging.debug(f'fetch payment rows {payment_rows=}')
    if not payment_rows:
        return []

    payments_list: list[AvangardPayment] = []
    for row in payment_rows:
        payment = _parse_income_payment_row(row)
        logging.debug(f'parse row {row=}')
        if payment:
            logging.debug(f'parse row result {payment=}')
            payments_list.append(payment)

    return payments_list


def _parse_income_payment_row(row: etree._Element) -> AvangardPayment | None:  # noqa: WPS437
    cells = row.xpath('.//td[@headers]')
    if len(cells) != 9:
        logging.debug(f'Invalid columns count {cells=}')
        return None

    cells = [stringify(cell) for cell in cells]
    income_amount = _parse_payment_amount(cells[3])
    if not income_amount:
        logging.debug('Skip not income payment')
        return None

    description = _parse_payment_description(cells[7])
    invoice_number = _parse_invoice_number(description)
    if not invoice_number:
        logging.warning(f'Invoice number not parsed yet "{description}"')
        return None

    agent_inn = _parse_agent_inn(cells[2])
    if not agent_inn:
        logging.warning(f'Agent INN not parsed yet "{cells[2]=}"')
        return None

    return AvangardPayment(
        payment_number=int(cells[6].strip()),
        payment_date=_parse_payment_date(cells[5]),
        agent_inn=agent_inn,
        invoice_number=invoice_number,
        income_amount=income_amount,
        description=description,
    )


def _parse_agent_inn(source: str) -> int | None:
    source = re.sub(r'\s+', '', source).strip()
    if match := re.search(r'ИНН(\d+)', source):
        return int(match.group(1))
    return None


def _parse_payment_description(source: str) -> str:
    return source.replace('\n', ' ').strip()


def _parse_invoice_number(source: str) -> str | None:
    source = re.sub(r'\s+', '', source).strip()
    if match := re.search(r'[#№]{1}(\d+)', source):
        return match.group(1)
    return None


def _parse_payment_date(source: str) -> datetime.date:
    dt = source.strip().replace('"', '')
    return datetime.datetime.strptime(dt, '%d.%m.%Y').date()


def _parse_payment_amount(source: str) -> Decimal:
    amount_str = source.replace(' ', '')
    if not amount_str:
        return Decimal(0)
    return Decimal(amount_str)
