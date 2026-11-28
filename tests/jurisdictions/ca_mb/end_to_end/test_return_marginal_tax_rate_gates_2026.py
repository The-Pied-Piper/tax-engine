"""The gated marginal tax rate runs for tax year 2026 as well, through the real engine.

The Manitoba manifest is 2025-only but the engine runs 2026 on it, reading each dataset family's
2026 file, so every dataset of the marginal rate (the gate, the contribution rates, the credit
rates, the family tax benefit rate, the basic personal amount band and fraction) needs a 2026
dataset (an absent year is never carried forward).

No new form text is quoted. The 2026 datasets are provisional (the 2026 forms are not published).
Where each tax first turns positive (2026, salary only): MB428 line 65 at 17,402.22 and basic
federal tax (T1 line 42900) at 19,200.18 (measured). At 17,402.22 the Manitoba part opens: 10.8% x
0.99 + 9% x 10.8% x 0.99 - 10.8% x 0.0658 = 0.1094364, and with the contributions (CPP 4.95% + 1%,
EI 1.63%) the rate is 0.1852364; each other salary pins the structure: the gates are 0 or 1 and
open with their taxes, each marginal part is its gate times its rate, and the total is the exact
sum of the three parts rounded half-up to 0.0001: the engine rounds the marginal rate like the
average rate (`ca/take_home_average_rate_rounding`), so 0.1852364 is 0.1852 in the tests.

The fall of the age amount (Worksheet MB428 "Line 58080 - Age amount", MB428 line 10) is a term of
the Manitoba rate for a filer born in 1960 or earlier: 15% x 10.8% x N = 0.0162 x N from a net
income of 27,749.01 to 52,601.99; a filer born in 1955 pays no CPP in 2026 (N = 1, credit-earning
rate 0.0163 EI), born in 1980 N = 0.99 and the rate 0.0658. Exact Manitoba terms with the credit
on the contributions taken off: born 1955, 10.8% bracket 0.108 - 0.0017604 = 0.1062396, 12.75%
bracket 0.1275 - 0.0017604 = 0.1257396, family tax benefit 0.00972, age 0.0162; born 1980, 10.8%
bracket 0.10692 - 0.0071064 = 0.0998136, 12.75% bracket 0.126225 - 0.0071064 = 0.1191186. The
salaries 27,749 and 27,749.01 are a net income of exactly that for a filer born in 1955 (no CPP),
and 52,601.99 and 52,602 the end of the amount (the printed "$52,602 or more, enter 0"). The
marginal totals are in `test_return_marginal_tax_rate_values.py`.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
ROUNDING = D("0.0001")
MANITOBA = JurisdictionCode("CA-MB")
RETURN = "ca-mb/return"
YEAR = 2026

FEDERAL_FORM = "ca/take_home_marginal_rates"
BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
LINE_65 = "ca-mb/manitoba_tax_after_credits_return"
FEDERAL_GATE = "ca/marginal_federal_gate"
MANITOBA_GATE = "ca-mb/manitoba_rate_gate"
FEDERAL_AFTER_CREDITS = "ca/marginal_federal_rate_after_credits"
MANITOBA_AFTER_CREDITS = "ca-mb/marginal_manitoba_rate_after_credits"
FEDERAL_BRACKET = "ca/marginal_federal_bracket_column_rate"
MANITOBA_BRACKET = "ca-mb/manitoba_bracket_rate_return"
FEDERAL = "ca-mb/marginal_federal_rate"
MANITOBA_RATE = "ca-mb/manitoba_marginal_rate"
AGE_RATE = "ca-mb/marginal_manitoba_age_credit_rate"
CONTRIBUTION = "ca-mb/marginal_contribution_rate"
MARGINAL = "ca-mb/marginal_tax_rate"

SALARIES = ["0", "100", "2000", "17402.22", "19200.18", "25000", "70000", "275000"]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Manitoba manifest, as the calculator loads it, salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate and the federal bracket rate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_runs_and_the_total_is_the_sum_of_the_gated_parts_rounded_to_four_decimals(
    salary: str,
) -> None:
    summary = _summary(salary)
    federal_sheet = _federal(salary)
    federal = _value(summary, FEDERAL)
    manitoba = _value(summary, MANITOBA_RATE)
    contribution = _value(summary, CONTRIBUTION)

    assert _value(summary, MARGINAL) == (federal + manitoba + contribution).quantize(
        ROUNDING, rounding=ROUND_HALF_UP
    )
    assert _value(federal_sheet, FEDERAL_GATE) in (D("0"), D("1"))
    assert _value(summary, MANITOBA_GATE) in (D("0"), D("1"))
    assert federal == _value(federal_sheet, FEDERAL_GATE) * _value(
        federal_sheet, FEDERAL_AFTER_CREDITS
    )
    assert manitoba == _value(summary, MANITOBA_GATE) * _value(summary, MANITOBA_AFTER_CREDITS)


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_each_gate_opens_with_the_tax_it_reads(salary: str) -> None:
    summary = _summary(salary)
    federal = _federal(salary)

    assert _value(federal, FEDERAL_GATE) == (
        D("1") if _value(federal, BASIC_FEDERAL_TAX) > 0 else D("0")
    )
    assert _value(summary, MANITOBA_GATE) == (D("1") if _value(summary, LINE_65) > 0 else D("0"))


@pytest.mark.parametrize("salary", ["0", "100"])
def test_2026_the_marginal_tax_rate_is_0_where_nothing_is_paid(salary: str) -> None:
    # No income tax, and no CPP or EI yet (the EI band of T2204 line 16 starts at 2,000).
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, MANITOBA_RATE) == D("0")
    assert _value(summary, CONTRIBUTION) == D("0")


def test_2026_the_marginal_tax_rate_at_2000_is_the_ei_dollar_for_dollar() -> None:
    # No income tax and no CPP, but the EI band of T2204 line 16 starts at 2,000 (included): the
    # dollar at 2,000 is the first that line 7 counts, so the rate is 1 there, as a cent above.
    summary = _summary("2000")

    assert _value(summary, MARGINAL) == D("1")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, MANITOBA_RATE) == D("0")
    assert _value(summary, CONTRIBUTION) == D("1")


@pytest.mark.parametrize("salary", ["0", "100", "2000", "17402.22", "19200.18", "25000"])
def test_2026_the_bracket_rates_are_the_first_brackets_of_the_2026_datasets(salary: str) -> None:
    summary = _summary(salary)

    assert _value(_federal(salary), FEDERAL_BRACKET) == D("0.14")
    assert _value(summary, MANITOBA_BRACKET) == D("0.108")


def test_2026_the_manitoba_part_opens_at_17402_22_and_the_federal_part_at_19200_18() -> None:
    assert _value(_summary("17402.21"), MANITOBA_RATE) == D("0")
    assert _value(_summary("17402.22"), MANITOBA_RATE) == D("0.1094364")
    assert _value(_summary("17402.22"), MARGINAL) == D("0.1852")
    assert _value(_summary("19200.17"), FEDERAL) == D("0")
    assert _value(_summary("19200.18"), FEDERAL) == D("0.129388")


def test_2026_the_marginal_tax_rate_at_70000_is_37_64_percent() -> None:
    # Both taxes are positive, over the EI maximum of 68,900 and under the CPP2 band:
    # 0.19602 + 0.120879 + 0.0595 (CPP 4.95% + 1%).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.19602")
    assert _value(summary, MANITOBA_RATE) == D("0.120879")
    assert _value(summary, CONTRIBUTION) == D("0.0595")
    assert _value(summary, MARGINAL) == D("0.3764")


def test_2026_both_gates_are_open_at_275000() -> None:
    summary = _summary("275000")

    assert _value(_federal("275000"), FEDERAL_GATE) == D("1")
    assert _value(summary, MANITOBA_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.33")
    assert _value(summary, MARGINAL) > D("0.33")


# Born 1955: salary, age term, Manitoba marginal rate (no CPP, so a net income equal to the salary).
BORN_1955 = [
    ("0", "0", "0"),
    ("27749", "0", "0.1159596"),
    ("27749.01", "0.0162", "0.1321596"),
    ("40000", "0.0162", "0.1321596"),
    ("46000", "0.0162", "0.1224396"),
    ("50000", "0.0162", "0.1419396"),
    ("52601.99", "0.0162", "0.1419396"),
    ("52602", "0", "0.1257396"),
    ("60000", "0", "0.1257396"),
]
# Born 1980 or no year of birth: no age amount, so no age term at any salary.
UNDER_65 = [
    ("0", "0", "0"),
    ("27993.94", "0", "0.0998136"),
    ("27993.95", "0", "0.0998136"),
    ("40000", "0", "0.0998136"),
    ("50000", "0", "0.1191186"),
    ("53097.97", "0", "0.1191186"),
    ("53097.98", "0", "0.1191186"),
    ("60000", "0", "0.1191186"),
]
AGE_CASES = [(born, *row) for born in (1955,) for row in BORN_1955] + [
    (born, *row) for born in (1980, None) for row in UNDER_65
]


def _aged_summary(salary: str, born: int | None) -> Worksheet:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if born is not None:
        given.append(Artifact(BIRTH_YEAR, born))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, YEAR, tuple(given))
    )
    (summary,) = worksheets[RETURN]
    return summary


@pytest.mark.parametrize(("born", "salary", "age", "manitoba"), AGE_CASES)
def test_the_age_term_and_the_manitoba_marginal_rate(
    born: int | None, salary: str, age: str, manitoba: str
) -> None:
    summary = _aged_summary(salary, born)

    assert _value(summary, AGE_RATE) == D(age)
    assert _value(summary, MANITOBA_RATE) == D(manitoba)
