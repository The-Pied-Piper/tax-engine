"""Form SK428 (2025, Saskatchewan tax, single filer) from the salary alone: the real Saskatchewan
manifest composed end to end.

Every SK428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the registered engine (`build_tax_computation`) over the real Saskatchewan 2025 manifest,
with the gross salary (`ca/employment_income`) the only input and every optional input left blank.
It asserts the Saskatchewan tax of SK428 line 82 at salaries of $20,000, $70,000 and $200,000.

Form text (Form SK428, CRA 5008-C): line 82 "Enter this amount on line 42800 of your return.".

The line 82 figures are 0.00 / 5,092.30 / 22,207.93. At $70,000 they are derived apart from the
engine in `test_line_82_at_70000_follows_from_the_printed_figures`: the printed rate and constant of
the second column (line 1 more than $53,463 but not more than $152,750: 12.5%, 5,613.62) give the
tax on the taxable income, and the credits base (the basic personal amount, the CPP and EI amounts)
at the printed 10.5% give the credits. The figures are not a CRA example.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
SASKATCHEWAN = JurisdictionCode("CA-SK")
SK428 = "ca-sk/sk428"
SK428_CREDITS = "ca-sk/sk428_credits"
LINE_1 = "ca-sk/sk428_taxable_income_line_1"
LINE_62 = "ca-sk/sk428_tax_line_62"
LINE_66 = "ca-sk/sk428_credits_subtotal_line_66"
LINE_82 = "ca-sk/sk428_saskatchewan_tax_line_82"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        SASKATCHEWAN, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


@pytest.mark.parametrize(
    ("salary", "saskatchewan_tax"),
    [("20000", "0.00"), ("70000", "5092.30"), ("200000", "22207.93")],
)
def test_line_82_is_the_saskatchewan_tax(salary: str, saskatchewan_tax: str) -> None:
    (sk428,) = _worksheets(salary)[SK428]

    assert _figure(sk428, LINE_82) == D(saskatchewan_tax)


def test_line_82_at_70000_follows_from_the_printed_figures() -> None:
    worksheets = _worksheets("70000")
    (credits_sheet,) = worksheets[SK428_CREDITS]
    (sk428,) = worksheets[SK428]
    taxable_income = _figure(credits_sheet, LINE_1)
    tax_on_taxable_income = _cents((taxable_income - D("53463.00")) * D("0.125") + D("5613.62"))
    # The credits base: the basic personal amount plus the CPP and EI amounts.
    credits_base = D("19491") + D("3291.75") + D("1077.48")
    credits = _cents(credits_base * D("0.105"))

    assert taxable_income == D("69335.00")
    assert credits_base == D("23860.23")
    assert tax_on_taxable_income == D("7597.62")
    assert credits == D("2505.32")
    assert tax_on_taxable_income - credits == D("5092.30")
    assert _figure(sk428, LINE_62) == tax_on_taxable_income
    assert _figure(sk428, LINE_66) == credits
    assert _figure(sk428, LINE_82) == D("5092.30")
