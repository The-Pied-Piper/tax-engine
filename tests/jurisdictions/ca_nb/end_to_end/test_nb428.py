"""Form NB428 (2025, New Brunswick tax, single filer) from the salary alone: the real New Brunswick
manifest composed end to end.

Every NB428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the registered engine (`build_tax_computation`) over the real New Brunswick 2025 manifest,
with the gross salary (`ca/employment_income`) the only input and every optional input left blank.
It asserts the New Brunswick tax of NB428 line 97 at salaries of $20,000, $30,000, $70,000 and
$200,000.

Form text (Form NB428, CRA 5004-C): line 97 "Line 95 minus line 96 (if negative, enter "0") ...
Enter this amount on line 42800 of your return.".

The line 97 figures are 0.00 / 798.76 / 5,676.89 / 26,050.13. Each is derived apart from the engine
in the `test_line_97_at_..._follows_from_the_printed_figures` tests, from the printed form alone:
the column of lines 2 to 8 that the taxable income falls in (printed rate and constant), the
credits base (the basic personal amount $13,396 plus the CPP and EI amounts of lines 19 and 21) at
the printed 9.4%, and the low-income tax reduction of lines 77 to 86 ($802 less 3% of the adjusted
family income above $21,920, nothing from a net income of $48,653). The taxable income is the salary
less the CPP enhanced contribution (1% of the salary up to $71,300 less $3,500, and 4% from
$71,300 to $81,200). The figures are not a CRA example.
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
NEW_BRUNSWICK = JurisdictionCode("CA-NB")
NB428 = "ca-nb/nb428"
LINE_1 = "ca-nb/nb428_taxable_income_line_1"
LINE_6 = "ca-nb/nb428_tax_on_excess_line_6"
LINE_67 = "ca-nb/nb428_tax_line_67"
LINE_83 = "ca-nb/nb428_line_83"
LINE_85 = "ca-nb/nb428_line_85"
LINE_86 = "ca-nb/nb428_line_86"
LINE_87 = "ca-nb/nb428_tax_line_87"
LINE_97 = "ca-nb/nb428_new_brunswick_tax_line_97"
SALARIES = [
    ("20000", "0.00"),
    ("30000", "798.76"),
    ("70000", "5676.89"),
    ("200000", "26050.13"),
]


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


@pytest.mark.parametrize(("salary", "new_brunswick_tax"), SALARIES)
def test_line_97_is_the_new_brunswick_tax(salary: str, new_brunswick_tax: str) -> None:
    (nb428,) = _worksheets(salary)[NB428]

    assert _figure(nb428, LINE_97) == D(new_brunswick_tax)


def test_line_97_at_20000_follows_from_the_printed_figures() -> None:
    (nb428,) = _worksheets("20000")[NB428]
    taxable_income = D("20000") - _cents((D("20000") - D("3500")) * D("0.01"))
    # Column 1 (line 1 of $51,306 or less): rate 9.4%, constant 0.00.
    tax_on_excess = _cents(taxable_income * D("0.094"))
    cpp = (D("20000") - D("3500")) * D("0.0495")
    ei = _cents(D("20000") * D("0.0164"))
    credits = _cents((D("13396") + cpp + ei) * D("0.094"))
    line_67 = tax_on_excess - credits
    # Lines 77 to 86: adjusted family income 19,835.00 is below the printed base amount 21,920.
    line_85 = _cents(max(taxable_income - D("21920"), D("0")) * D("0.03"))
    line_86 = D("802") - line_85

    assert taxable_income == D("19835.00")
    assert (cpp, ei) == (D("816.75"), D("328.00"))
    assert tax_on_excess == D("1864.49")
    assert credits == D("1366.83")
    assert line_67 == D("497.66")
    assert line_86 == D("802.00")
    assert _figure(nb428, LINE_1) == taxable_income
    assert _figure(nb428, LINE_6) == tax_on_excess
    assert _figure(nb428, LINE_67) == line_67
    assert _figure(nb428, LINE_83) == D("0.00")
    assert _figure(nb428, LINE_86) == line_86
    assert max(line_67 - line_86, D("0")) == D("0.00")
    assert _figure(nb428, LINE_97) == D("0.00")


def test_line_97_at_30000_follows_from_the_printed_figures() -> None:
    (nb428,) = _worksheets("30000")[NB428]
    taxable_income = D("30000") - _cents((D("30000") - D("3500")) * D("0.01"))
    tax_on_excess = _cents(taxable_income * D("0.094"))
    cpp = (D("30000") - D("3500")) * D("0.0495")
    ei = _cents(D("30000") * D("0.0164"))
    credits = _cents((D("13396") + cpp + ei) * D("0.094"))
    line_67 = tax_on_excess - credits
    # Lines 82 to 86: 3% of the 7,815.00 over the base amount takes 234.45 off the $802 reduction.
    line_83 = taxable_income - D("21920")
    line_85 = _cents(line_83 * D("0.03"))
    line_86 = D("802") - line_85

    assert taxable_income == D("29735.00")
    assert (cpp, ei) == (D("1311.75"), D("492.00"))
    assert tax_on_excess == D("2795.09")
    assert credits == D("1428.78")
    assert line_67 == D("1366.31")
    assert line_83 == D("7815.00")
    assert line_85 == D("234.45")
    assert line_86 == D("567.55")
    assert _figure(nb428, LINE_1) == taxable_income
    assert _figure(nb428, LINE_6) == tax_on_excess
    assert _figure(nb428, LINE_67) == line_67
    assert _figure(nb428, LINE_83) == line_83
    assert _figure(nb428, LINE_85) == line_85
    assert _figure(nb428, LINE_86) == line_86
    assert _figure(nb428, LINE_87) == line_67 - line_86
    assert _figure(nb428, LINE_97) == D("798.76")


def test_line_97_at_70000_follows_from_the_printed_figures() -> None:
    (nb428,) = _worksheets("70000")[NB428]
    taxable_income = D("70000") - _cents((D("70000") - D("3500")) * D("0.01"))
    # Column 2 (line 1 more than $51,306 but not more than $102,614): 14%, constant 4,822.76.
    tax_on_excess = _cents((taxable_income - D("51306")) * D("0.14"))
    tax = tax_on_excess + D("4822.76")
    cpp = (D("70000") - D("3500")) * D("0.0495")
    # The EI premium stops at the maximum insurable earnings of $65,700.
    ei = _cents(D("65700") * D("0.0164"))
    credits = _cents((D("13396") + cpp + ei) * D("0.094"))
    line_67 = tax - credits
    # Net income 69,335.00 is not less than the single income limit of $48,653: no reduction.
    line_83 = taxable_income - D("21920")

    assert taxable_income == D("69335.00")
    assert (cpp, ei) == (D("3291.75"), D("1077.48"))
    assert tax_on_excess == D("2524.06")
    assert credits == D("1669.93")
    assert line_67 == D("5676.89")
    assert taxable_income >= D("48653")
    assert _figure(nb428, LINE_1) == taxable_income
    assert _figure(nb428, LINE_6) == tax_on_excess
    assert _figure(nb428, LINE_67) == line_67
    assert _figure(nb428, LINE_83) == line_83
    assert _figure(nb428, LINE_86) == D("0.00")
    assert _figure(nb428, LINE_97) == D("5676.89")


def test_line_97_at_200000_follows_from_the_printed_figures() -> None:
    (nb428,) = _worksheets("200000")[NB428]
    # The CPP enhanced contribution is 1% of 71,300 less 3,500 and 4% of 81,200 less 71,300.
    enhanced = _cents(D("67800") * D("0.01")) + _cents(D("9900") * D("0.04"))
    taxable_income = D("200000") - enhanced
    # Column 4 (line 1 more than $190,060): 19.5%, constant 25,997.24.
    tax_on_excess = _cents((taxable_income - D("190060")) * D("0.195"))
    tax = tax_on_excess + D("25997.24")
    cpp = D("67800") * D("0.0495")
    ei = _cents(D("65700") * D("0.0164"))
    credits = _cents((D("13396") + cpp + ei) * D("0.094"))
    line_67 = tax - credits

    assert enhanced == D("1074.00")
    assert taxable_income == D("198926.00")
    assert cpp == D("3356.10")
    assert tax_on_excess == D("1728.87")
    assert credits == D("1675.98")
    assert line_67 == D("26050.13")
    assert _figure(nb428, LINE_1) == taxable_income
    assert _figure(nb428, LINE_6) == tax_on_excess
    assert _figure(nb428, LINE_67) == line_67
    assert _figure(nb428, LINE_86) == D("0.00")
    assert _figure(nb428, LINE_97) == D("26050.13")
