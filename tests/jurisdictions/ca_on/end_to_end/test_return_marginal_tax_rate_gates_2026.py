"""The gated marginal tax rate runs for tax year 2026 as well, through the real engine.

The Ontario manifest is 2025-only but the engine runs 2026 on it, reading each dataset family's
2026 file, so every dataset of the marginal rate (the gate, the contribution rates, the credit
rates, the basic personal amount band and fraction, the LIFT reduction rate) needs a 2026 dataset
(an absent year is never carried forward).

No new form text is quoted. The 2026 datasets are provisional (the 2026 forms are not published).
Where each tax first turns positive (2026, salary only): basic federal tax (T1 line 42900) at
19,200.18 and ON428 line 86 at 32,577.01 (measured). At 19,200.18 the federal part opens:
14% x 0.99 - 14% x 0.0658 = 0.129388, and with the contributions (CPP 4.95% + 1%, EI 1.63%) the rate
is 0.205188; each other salary pins the structure: the gates are 0 or 1 and open with their taxes,
each marginal part is its gate times its rate, and the total is the exact sum of the four parts.

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
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"

FEDERAL_FORM = "ca/take_home_marginal_rates"
BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
TAX_AFTER_LIFT = "ca-on/ontario_tax_after_lift_return"
FEDERAL_GATE = "ca/marginal_federal_gate"
ONTARIO_GATE = "ca-on/ontario_rate_gate"
REDUCTION_GATE = "ca-on/ontario_reduction_gate"
TAX_REDUCTION = "ca-on/ontario_tax_reduction_return"
FEDERAL_AFTER_CREDITS = "ca/marginal_federal_rate_after_credits"
ONTARIO_AFTER_LIFT = "ca-on/marginal_ontario_rate_after_lift"
FEDERAL_BRACKET = "ca/marginal_federal_bracket_column_rate"
ONTARIO_BRACKET = "ca-on/ontario_bracket_rate_return"
FEDERAL = "ca-on/marginal_federal_rate"
ONTARIO_RATE = "ca-on/ontario_marginal_rate"
PREMIUM = "ca-on/marginal_health_premium_rate"
CONTRIBUTION = "ca-on/marginal_contribution_rate"
MARGINAL = "ca-on/marginal_tax_rate"

SALARIES = ["0", "100", "2000", "19200.18", "20256.98", "25000", "32577.01", "70000", "275000"]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Ontario manifest, as the calculator loads it, salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate and the federal bracket rate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_runs_and_the_total_is_the_exact_sum_of_the_gated_parts(salary: str) -> None:
    summary = _summary(salary)
    federal = _value(summary, FEDERAL)
    ontario = _value(summary, ONTARIO_RATE)
    premium = _value(summary, PREMIUM)
    contribution = _value(summary, CONTRIBUTION)

    assert _value(summary, MARGINAL) == (federal + ontario + premium + contribution).quantize(
        ROUNDING, rounding=ROUND_HALF_UP
    )
    assert _value(_federal(salary), FEDERAL_GATE) in (D("0"), D("1"))
    assert _value(summary, ONTARIO_GATE) in (D("0"), D("1"))
    federal_sheet = _federal(salary)
    assert federal == _value(federal_sheet, FEDERAL_GATE) * _value(
        federal_sheet, FEDERAL_AFTER_CREDITS
    )
    assert ontario == _value(summary, ONTARIO_GATE) * _value(summary, ONTARIO_AFTER_LIFT)
    assert _value(summary, REDUCTION_GATE) in (D("0"), D("1"))


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_each_gate_opens_with_the_tax_it_reads(salary: str) -> None:
    summary = _summary(salary)

    assert _value(_federal(salary), FEDERAL_GATE) == (
        D("1") if _value(_federal(salary), BASIC_FEDERAL_TAX) > 0 else D("0")
    )
    assert _value(summary, ONTARIO_GATE) == (
        D("1") if _value(summary, TAX_AFTER_LIFT) > 0 else D("0")
    )


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_the_reduction_gate_opens_with_the_tax_reduction(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, REDUCTION_GATE) == (
        D("1") if _value(summary, TAX_REDUCTION) > 0 else D("0")
    )


@pytest.mark.parametrize("salary", ["0", "100", "2000"])
def test_2026_the_marginal_tax_rate_is_0_where_nothing_is_paid(salary: str) -> None:
    # No income tax, and no CPP or EI yet (the EI band of T2204 line 16 starts above 2,000).
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, ONTARIO_RATE) == D("0")
    assert _value(summary, PREMIUM) == D("0")
    assert _value(summary, CONTRIBUTION) == D("0")


@pytest.mark.parametrize("salary", ["0", "100", "2000", "19200.18", "20256.98", "25000"])
def test_2026_the_bracket_rates_are_the_first_brackets_of_the_2026_datasets(salary: str) -> None:
    summary = _summary(salary)

    assert _value(_federal(salary), FEDERAL_BRACKET) == D("0.14")
    assert _value(summary, ONTARIO_BRACKET) == D("0.0505")


def test_2026_the_federal_part_opens_at_19200_18_and_the_ontario_part_at_32577_01() -> None:
    assert _value(_summary("19200.17"), FEDERAL) == D("0")
    assert _value(_summary("19200.18"), FEDERAL) == D("0.129388")
    assert _value(_summary("19200.18"), MARGINAL) == D("0.2052")
    assert _value(_summary("32577.00"), ONTARIO_RATE) == D("0")
    assert _value(_summary("32577.01"), ONTARIO_RATE) == D("0.0466721")


def test_2026_the_marginal_tax_rate_at_70000_is_34_36_percent() -> None:
    # Both taxes are positive, over the EI maximum of 68,900 and under the CPP2 band:
    # 0.19602 + 0.08808525 + 0 + 0.0595 (CPP 4.95% + 1%).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.19602")
    assert _value(summary, ONTARIO_RATE) == D("0.08808525")
    assert _value(summary, PREMIUM) == D("0")
    assert _value(summary, CONTRIBUTION) == D("0.0595")
    assert _value(summary, MARGINAL) == D("0.3436")


def test_2026_both_gates_are_open_at_275000() -> None:
    summary = _summary("275000")

    assert _value(_federal("275000"), FEDERAL_GATE) == D("1")
    assert _value(summary, ONTARIO_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.33")
    assert _value(summary, MARGINAL) > D("0.33")
