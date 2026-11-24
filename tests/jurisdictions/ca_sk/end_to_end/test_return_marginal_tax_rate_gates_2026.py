"""The gated marginal tax rate runs for tax year 2026 as well, through the real engine.

The Saskatchewan manifest is 2025-only but the engine runs 2026 on it, reading each dataset
family's 2026 file, so every dataset of the marginal rate (the gate, the contribution rates, the
credit rates, the basic personal amount band and fraction) needs a 2026 dataset (an absent year is
never carried forward).

No new form text is quoted. The 2026 datasets are provisional (the 2026 forms are not published).
Where each tax first turns positive (2026, salary only): basic federal tax (T1 line 42900) at
19,200.18 and SK428 line 67 at 21,827.32 (measured). At 19,200.18 the federal part opens:
14% x 0.99 - 14% x 0.0658 = 0.129388, and with the contributions (CPP 4.95% + 1%, EI 1.63%) the rate
is 0.205188; each other salary pins the structure: the gates are 0 or 1 and open with their taxes,
each marginal part is its gate times its rate, and the total is the exact sum of the three parts.

The engine rounds the marginal tax rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`): the total is the sum of the parts rounded half-up to four
places, and the marginal values pinned below are the exact figures in the comments rounded the same
way; the parts stay exact.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
ROUNDING = D("0.0001")
SASKATCHEWAN = JurisdictionCode("CA-SK")
RETURN = "ca-sk/return"

FEDERAL_FORM = "ca/take_home_marginal_rates"
BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
LINE_67 = "ca-sk/saskatchewan_tax_after_credits_return"
FEDERAL_GATE = "ca/marginal_federal_gate"
SASKATCHEWAN_GATE = "ca-sk/saskatchewan_rate_gate"
FEDERAL_AFTER_CREDITS = "ca/marginal_federal_rate_after_credits"
SASKATCHEWAN_AFTER_CREDITS = "ca-sk/marginal_saskatchewan_rate_after_credits"
FEDERAL_BRACKET = "ca/marginal_federal_bracket_column_rate"
SASKATCHEWAN_BRACKET = "ca-sk/saskatchewan_bracket_rate_return"
FEDERAL = "ca-sk/marginal_federal_rate"
SASKATCHEWAN_RATE = "ca-sk/saskatchewan_marginal_rate"
CONTRIBUTION = "ca-sk/marginal_contribution_rate"
MARGINAL = "ca-sk/marginal_tax_rate"

SALARIES = ["0", "100", "2000", "19200.18", "21827.32", "25000", "70000", "275000"]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Saskatchewan manifest, as the calculator loads it, salary the only
    # input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate and the federal bracket rate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_runs_and_the_total_is_the_exact_sum_of_the_gated_parts(salary: str) -> None:
    summary = _summary(salary)
    federal_sheet = _federal(salary)
    federal = _value(summary, FEDERAL)
    saskatchewan = _value(summary, SASKATCHEWAN_RATE)
    contribution = _value(summary, CONTRIBUTION)

    assert _value(summary, MARGINAL) == (federal + saskatchewan + contribution).quantize(
        ROUNDING, rounding=ROUND_HALF_UP
    )
    assert _value(federal_sheet, FEDERAL_GATE) in (D("0"), D("1"))
    assert _value(summary, SASKATCHEWAN_GATE) in (D("0"), D("1"))
    assert federal == _value(federal_sheet, FEDERAL_GATE) * _value(
        federal_sheet, FEDERAL_AFTER_CREDITS
    )
    assert saskatchewan == _value(summary, SASKATCHEWAN_GATE) * _value(
        summary, SASKATCHEWAN_AFTER_CREDITS
    )


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_each_gate_opens_with_the_tax_it_reads(salary: str) -> None:
    summary = _summary(salary)
    federal = _federal(salary)

    assert _value(federal, FEDERAL_GATE) == (
        D("1") if _value(federal, BASIC_FEDERAL_TAX) > 0 else D("0")
    )
    assert _value(summary, SASKATCHEWAN_GATE) == (
        D("1") if _value(summary, LINE_67) > 0 else D("0")
    )


@pytest.mark.parametrize("salary", ["0", "100", "2000"])
def test_2026_the_marginal_tax_rate_is_0_where_nothing_is_paid(salary: str) -> None:
    # No income tax, and no CPP or EI yet (the EI band of T2204 line 16 starts above 2,000).
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, SASKATCHEWAN_RATE) == D("0")
    assert _value(summary, CONTRIBUTION) == D("0")


@pytest.mark.parametrize("salary", ["0", "100", "2000", "19200.18", "21827.32", "25000"])
def test_2026_the_bracket_rates_are_the_first_brackets_of_the_2026_datasets(salary: str) -> None:
    summary = _summary(salary)

    assert _value(_federal(salary), FEDERAL_BRACKET) == D("0.14")
    assert _value(summary, SASKATCHEWAN_BRACKET) == D("0.105")


def test_2026_the_federal_part_opens_at_19200_18_and_the_saskatchewan_part_at_21827_32() -> None:
    assert _value(_summary("19200.17"), FEDERAL) == D("0")
    assert _value(_summary("19200.18"), FEDERAL) == D("0.129388")
    assert _value(_summary("19200.18"), MARGINAL) == D("0.2052")
    assert _value(_summary("21827.31"), SASKATCHEWAN_RATE) == D("0")
    assert _value(_summary("21827.32"), SASKATCHEWAN_RATE) == D("0.097041")


def test_2026_the_marginal_tax_rate_at_70000_is_37_41_percent() -> None:
    # Both taxes are positive, over the EI maximum of 68,900 and under the CPP2 band:
    # 0.19602 + 0.1185525 + 0.0595 (CPP 4.95% + 1%).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.19602")
    assert _value(summary, SASKATCHEWAN_RATE) == D("0.1185525")
    assert _value(summary, CONTRIBUTION) == D("0.0595")
    assert _value(summary, MARGINAL) == D("0.3741")


def test_2026_both_gates_are_open_at_275000() -> None:
    summary = _summary("275000")

    assert _value(_federal("275000"), FEDERAL_GATE) == D("1")
    assert _value(summary, SASKATCHEWAN_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.33")
    assert _value(summary, MARGINAL) > D("0.33")
