"""Form NS428 (2025, Nova Scotia tax, single filer) from the salary alone: the real Nova Scotia
manifest composed end to end.

Every NS428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the registered engine (`build_tax_computation`) over the real Nova Scotia 2025 manifest,
with the gross salary (`ca/employment_income`) the only input and every optional input left blank.
It asserts the Nova Scotia tax of NS428 line 99 at salaries of $20,000, $30,000 and $70,000 (and
$200,000).

Form text (Form NS428, CRA 5003-C): line 99 "Line 97 minus line 98 (if negative, enter "0") Enter
this amount on line 42800 of your return.".

The line 99 figures are 552.33 / 1,422.86 / 7,213.10 / 31,215.18. Each is derived apart from the
engine in `test_line_99_follows_from_the_printed_figures`, from the printed form alone: the column
of lines 3 to 7 that the taxable income falls in (printed rate and constant), the credits base
(line 19, the basic personal amount $11,744, plus the CPP and EI amounts of lines 21 and 23) at the
printed 8.79% (line 47), and the low-income tax reduction of lines 65 to 85 ($300 less 5% of the
family income above $15,000). The taxable income is the salary less the CPP enhanced contribution
(1% of the salary up to $71,300 less $3,500, and 4% from $71,300 to $81,200). The figures are not a
CRA example.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
NOVA_SCOTIA = JurisdictionCode("CA-NS")
NS428 = "ca-ns/ns428"
LINE_1 = "ca-ns/ns428_taxable_income_line_1"
LINE_8 = "ca-ns/ns428_tax_on_taxable_income_line_8"
LINE_48 = "ca-ns/ns428_credits_at_rate_line_48"
LINE_64 = "ca-ns/ns428_tax_after_credits_line_64"
LINE_83 = "ca-ns/ns428_line_83"
LINE_84 = "ca-ns/ns428_low_income_reduction_line_84"
LINE_99 = "ca-ns/ns428_nova_scotia_tax_line_99"
SALARIES = [
    ("20000", "552.33"),
    ("30000", "1422.86"),
    ("70000", "7213.10"),
    ("200000", "31215.18"),
]


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


def _sheet(salary: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[NS428]
    return sheet


@pytest.mark.parametrize(("salary", "nova_scotia_tax"), SALARIES)
def test_line_99_is_the_nova_scotia_tax(salary: str, nova_scotia_tax: str) -> None:
    assert _figure(_sheet(salary), LINE_99) == D(nova_scotia_tax)


def test_line_99_at_20000_follows_from_the_printed_figures() -> None:
    sheet = _sheet("20000")
    taxable_income = D("20000") - _cents((D("20000") - D("3500")) * D("0.01"))
    # Column 1 (line 1 of $30,507 or less): rate 8.79%, constant 0.00.
    tax_on_taxable_income = _cents(taxable_income * D("0.0879"))
    cpp = (D("20000") - D("3500")) * D("0.0495")
    ei = _cents(D("20000") * D("0.0164"))
    credits = _cents((D("11744") + cpp + ei) * D("0.0879"))
    line_64 = tax_on_taxable_income - credits
    # Lines 81 to 84: the $300 reduction less 5% of the income above the $15,000 base amount.
    line_83 = _cents((taxable_income - D("15000")) * D("0.05"))
    line_84 = D("300") - line_83

    assert taxable_income == D("19835.00")
    assert (cpp, ei) == (D("816.75"), D("328.00"))
    assert tax_on_taxable_income == D("1743.50")
    assert credits == D("1132.92")
    assert line_64 == D("610.58")
    assert line_83 == D("241.75")
    assert _figure(sheet, LINE_1) == taxable_income
    assert _figure(sheet, LINE_8) == tax_on_taxable_income
    assert _figure(sheet, LINE_48) == credits
    assert _figure(sheet, LINE_64) == line_64
    assert _figure(sheet, LINE_83) == line_83
    assert _figure(sheet, LINE_84) == line_84 == D("58.25")
    assert _figure(sheet, LINE_99) == line_64 - line_84 == D("552.33")


def test_line_99_at_30000_follows_from_the_printed_figures() -> None:
    sheet = _sheet("30000")
    taxable_income = D("30000") - _cents((D("30000") - D("3500")) * D("0.01"))
    # Column 1 (line 1 of $30,507 or less): rate 8.79%, constant 0.00.
    tax_on_taxable_income = _cents(taxable_income * D("0.0879"))
    cpp = (D("30000") - D("3500")) * D("0.0495")
    ei = _cents(D("30000") * D("0.0164"))
    credits = _cents((D("11744") + cpp + ei) * D("0.0879"))
    line_64 = tax_on_taxable_income - credits
    # 5% of the income above $15,000 is more than the $300 reduction.
    line_83 = _cents((taxable_income - D("15000")) * D("0.05"))

    assert taxable_income == D("29735.00")
    assert (cpp, ei) == (D("1311.75"), D("492.00"))
    assert tax_on_taxable_income == D("2613.71")
    assert credits == D("1190.85")
    assert line_83 == D("736.75")
    assert D("300") - line_83 < 0
    assert _figure(sheet, LINE_1) == taxable_income
    assert _figure(sheet, LINE_8) == tax_on_taxable_income
    assert _figure(sheet, LINE_48) == credits
    assert _figure(sheet, LINE_84) == D("0.00")
    assert _figure(sheet, LINE_99) == line_64 == D("1422.86")


def test_line_99_at_70000_follows_from_the_printed_figures() -> None:
    sheet = _sheet("70000")
    taxable_income = D("70000") - _cents((D("70000") - D("3500")) * D("0.01"))
    # Column 3 (line 1 more than $61,015 but not more than $95,883): 16.67%, constant 7,242.51.
    tax_on_taxable_income = _cents((taxable_income - D("61015")) * D("0.1667") + D("7242.51"))
    cpp = (D("70000") - D("3500")) * D("0.0495")
    # The EI premium stops at the maximum insurable earnings of $65,700.
    ei = _cents(D("65700") * D("0.0164"))
    credits = _cents((D("11744") + cpp + ei) * D("0.0879"))
    line_64 = tax_on_taxable_income - credits

    assert taxable_income == D("69335.00")
    assert (cpp, ei) == (D("3291.75"), D("1077.48"))
    assert tax_on_taxable_income == D("8629.45")
    assert credits == D("1416.35")
    assert line_64 == D("7213.10")
    assert _figure(sheet, LINE_1) == taxable_income
    assert _figure(sheet, LINE_8) == tax_on_taxable_income
    assert _figure(sheet, LINE_48) == credits
    assert _figure(sheet, LINE_84) == D("0.00")
    assert _figure(sheet, LINE_99) == D("7213.10")


def test_line_99_at_200000_follows_from_the_printed_figures() -> None:
    sheet = _sheet("200000")
    # The CPP enhanced contribution is 1% of 71,300 less 3,500 and 4% of 81,200 less 71,300.
    enhanced = _cents(D("67800") * D("0.01")) + _cents(D("9900") * D("0.04"))
    taxable_income = D("200000") - enhanced
    # Column 5 (line 1 more than $154,650): 21%, constant 23,339.23.
    tax_on_taxable_income = _cents((taxable_income - D("154650")) * D("0.21") + D("23339.23"))
    cpp = D("67800") * D("0.0495")
    ei = _cents(D("65700") * D("0.0164"))
    credits = _cents((D("11744") + cpp + ei) * D("0.0879"))
    line_64 = tax_on_taxable_income - credits

    assert enhanced == D("1074.00")
    assert taxable_income == D("198926.00")
    assert cpp == D("3356.10")
    assert tax_on_taxable_income == D("32637.19")
    assert credits == D("1422.01")
    assert line_64 == D("31215.18")
    assert _figure(sheet, LINE_1) == taxable_income
    assert _figure(sheet, LINE_8) == tax_on_taxable_income
    assert _figure(sheet, LINE_48) == credits
    assert _figure(sheet, LINE_99) == D("31215.18")
