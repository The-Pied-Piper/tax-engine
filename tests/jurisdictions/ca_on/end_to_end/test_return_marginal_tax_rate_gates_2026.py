"""The gated marginal tax rate runs for tax year 2026 as well, through the real engine.

The Ontario manifest is 2025-only but the engine runs 2026 on it, reading each dataset family's
2026 file, so `ca-on/marginal_rate_gate` needs a 2026 dataset (an absent year is never carried
forward). Without it every 2026 salary is refused ("no ca-on/marginal_rate_gate dataset for tax
year 2026").

No new form text is quoted. The 2026 datasets are provisional (the 2026 forms are not published).
Figures that depend on the 2026 credit amounts (where each tax first turns positive) are not
derived by hand: each salary pins the structure instead, that the gates are 0 or 1 and open with
their taxes, each marginal part is its gate times its bracket rate (the Ontario one doubled while
the Ontario tax reduction is above 0), the total is the exact sum of the three parts, and the
bracket rates are those of the 2026 bracket datasets (federal 14% to 58,523, then 20.5%; Ontario
5.05% to 53,891, then 9.15%).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"

BASIC_FEDERAL_TAX = "ca/federal_tax_after_credits_return"
TAX_AFTER_REDUCTION = "ca-on/ontario_tax_after_reduction_return"
FEDERAL_GATE = "ca/federal_rate_gate"
ONTARIO_GATE = "ca-on/ontario_rate_gate"
REDUCTION_GATE = "ca-on/ontario_reduction_gate"
TAX_REDUCTION = "ca-on/ontario_tax_reduction_return"
FEDERAL_BRACKET = "ca/federal_bracket_rate_return"
ONTARIO_BRACKET = "ca-on/ontario_bracket_marginal_rate"
FEDERAL = "ca/federal_marginal_rate"
ONTARIO_RATE = "ca-on/ontario_marginal_rate"
SLOPE = "ca-on/return_health_premium_slope"
MARGINAL = "ca-on/marginal_tax_rate"

SALARIES = ["0", "100", "2000", "18820.27", "19868.74", "25000", "70000", "275000"]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Ontario manifest, as the calculator loads it, salary the only input.
    worksheets = build_tax_computation().compute(
        ONTARIO, 2026, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_runs_and_the_total_is_the_exact_sum_of_the_gated_parts(salary: str) -> None:
    summary = _summary(salary)
    federal = _value(summary, FEDERAL)
    ontario = _value(summary, ONTARIO_RATE)
    slope = _value(summary, SLOPE)

    assert _value(summary, MARGINAL) == federal + ontario + slope
    assert _value(summary, FEDERAL_GATE) in (D("0"), D("1"))
    assert _value(summary, ONTARIO_GATE) in (D("0"), D("1"))
    assert federal == _value(summary, FEDERAL_GATE) * _value(summary, FEDERAL_BRACKET)
    # The Ontario tax reduction phase-out doubles the bracket rate while line 80 is above 0.
    assert _value(summary, REDUCTION_GATE) in (D("0"), D("1"))
    assert ontario == _value(summary, ONTARIO_GATE) * _value(summary, ONTARIO_BRACKET) * (
        1 + _value(summary, REDUCTION_GATE)
    )
    assert slope in (D("0"), D("0.06"), D("0.25"))


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_each_gate_opens_with_the_tax_it_reads(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL_GATE) == (
        D("1") if _value(summary, BASIC_FEDERAL_TAX) > 0 else D("0")
    )
    assert _value(summary, ONTARIO_GATE) == (
        D("1") if _value(summary, TAX_AFTER_REDUCTION) > 0 else D("0")
    )


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_the_reduction_gate_opens_with_the_tax_reduction(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, REDUCTION_GATE) == (
        D("1") if _value(summary, TAX_REDUCTION) > 0 else D("0")
    )


@pytest.mark.parametrize("salary", ["0", "100", "2000"])
def test_2026_the_marginal_tax_rate_is_0_where_no_tax_is_paid(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, ONTARIO_RATE) == D("0")
    assert _value(summary, SLOPE) == D("0")


@pytest.mark.parametrize("salary", ["0", "100", "2000", "18820.27", "19868.74", "25000"])
def test_2026_the_bracket_rates_are_the_first_brackets_of_the_2026_datasets(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL_BRACKET) == D("0.14")
    assert _value(summary, ONTARIO_BRACKET) == D("0.0505")


def test_2026_the_marginal_tax_rate_at_70000_is_29_65_percent() -> None:
    # Both taxes are positive: 0.205 + 0.0915 x 1 + 0 (the same rates as 2025 above the first
    # brackets).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.205")
    assert _value(summary, ONTARIO_RATE) == D("0.0915")
    assert _value(summary, SLOPE) == D("0")
    assert _value(summary, MARGINAL) == D("0.2965")


def test_2026_both_gates_are_open_at_275000() -> None:
    summary = _summary("275000")

    assert _value(summary, FEDERAL_GATE) == D("1")
    assert _value(summary, ONTARIO_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.33")
    assert _value(summary, MARGINAL) > D("0.33")
