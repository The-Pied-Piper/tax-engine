"""The gated Newfoundland and Labrador marginal tax rate, 2026, through the real engine.

The 2026 manifest is the 2025 one and the engine runs it on each dataset family's 2026 file, so
the gate, the credit rate and the low-income reduction datasets need a 2026 file (an absent year
is never carried forward). The 2026 datasets are provisional (the 2026 forms are not published).

The provincial part is counted only while NL428 line 105 "Line 94 minus line 104 (if negative,
enter "0")" is above zero, and the low-income tax reduction slope (16%, NL428 line 102) only while
NL428 line 101 and line 104 are both above zero. Each boundary below is found cent by cent from the
engine, and each rate is the hand-worked figure of `test_return_marginal_tax_rate_values.py`; each
other salary pins the structure: the gates are 0 or 1 and open with the amounts they read, the
provincial part is its gate times its rate, and the total is the exact sum of the three parts.

- line 105 is 0.00 at a salary of 24,404.89 and 0.01 at 24,404.90; line 104 is 0.01 at 29,715.62
  and 0.00 at 29,715.63; in between the provincial part is 8.7% x 0.99 - 8.7% x 0.0658 + 16% x 0.99
  = 0.2388054, and after it 0.0804054.

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
NEWFOUNDLAND = JurisdictionCode("CA-NL")
RETURN = "ca-nl/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
FEDERAL_AFTER_CREDITS = "ca/marginal_federal_rate_after_credits"
FEDERAL_BRACKET = "ca/marginal_federal_bracket_column_rate"
LINE_105 = "ca-nl/newfoundland_and_labrador_tax_return"
TAX_GATE = "ca-nl/newfoundland_and_labrador_rate_gate"
NL_BRACKET = "ca-nl/newfoundland_and_labrador_bracket_rate_return"
REDUCTION_RATE = "ca-nl/marginal_newfoundland_and_labrador_rate_with_reduction"
INCOME_GATE = "ca-nl/income_over_low_income_threshold_gate"
REDUCTION_GATE = "ca-nl/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-nl/low_income_reduction_phase_out_gate"
FEDERAL = "ca-nl/marginal_federal_rate"
PROVINCIAL = "ca-nl/newfoundland_and_labrador_marginal_rate"
CONTRIBUTION = "ca-nl/marginal_contribution_rate"
MARGINAL = "ca-nl/marginal_tax_rate"

SALARIES = [
    "0",
    "100",
    "2000",
    "11750",
    "19200.18",
    "24404.90",
    "28000",
    "29715.63",
    "70000",
    "275000",
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Newfoundland and Labrador manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate and the federal bracket rate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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

    assert _value(summary, MARGINAL) == (
        federal + _value(summary, PROVINCIAL) + _value(summary, CONTRIBUTION)
    ).quantize(ROUNDING, rounding=ROUND_HALF_UP)
    assert _value(federal_sheet, FEDERAL_GATE) in (D("0"), D("1"))
    assert federal == _value(federal_sheet, FEDERAL_GATE) * _value(
        federal_sheet, FEDERAL_AFTER_CREDITS
    )
    assert _value(summary, PROVINCIAL) == _value(summary, TAX_GATE) * _value(
        summary, REDUCTION_RATE
    )


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_each_gate_opens_with_the_amount_it_reads(salary: str) -> None:
    summary = _summary(salary)
    federal = _federal(salary)

    assert _value(federal, FEDERAL_GATE) == (
        D("1") if _value(federal, BASIC_FEDERAL_TAX) > 0 else D("0")
    )
    for gate, amount in (
        (TAX_GATE, LINE_105),
        (INCOME_GATE, "ca-nl/income_over_low_income_threshold_return"),
        (REDUCTION_GATE, "ca-nl/low_income_tax_reduction_return"),
    ):
        assert _value(summary, gate) == (D("1") if _value(summary, amount) > 0 else D("0"))
    assert _value(summary, PHASE_OUT_GATE) == (
        _value(summary, INCOME_GATE) * _value(summary, REDUCTION_GATE)
    )


@pytest.mark.parametrize("salary", ["0", "100"])
def test_2026_the_marginal_tax_rate_is_0_where_nothing_is_paid(salary: str) -> None:
    # No income tax, and no CPP or EI yet (the EI band of T2204 line 16 starts at 2,000).
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, PROVINCIAL) == D("0")
    assert _value(summary, CONTRIBUTION) == D("0")


def test_2026_the_marginal_tax_rate_at_2000_is_the_ei_dollar_for_dollar() -> None:
    # No income tax and no CPP, but the EI band of T2204 line 16 starts at 2,000 (included): the
    # dollar at 2,000 is the first that line 7 counts, so the rate is 1 there, as a cent above.
    summary = _summary("2000")

    assert _value(summary, MARGINAL) == D("1")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, PROVINCIAL) == D("0")
    assert _value(summary, CONTRIBUTION) == D("1")


@pytest.mark.parametrize("salary", ["0", "100", "2000", "11750", "19200.18"])
def test_2026_the_bracket_rates_are_the_first_brackets_of_the_2026_datasets(salary: str) -> None:
    summary = _summary(salary)

    assert _value(_federal(salary), FEDERAL_BRACKET) == D("0.14")
    assert _value(summary, NL_BRACKET) == D("0.087")


def test_2026_the_federal_part_opens_at_19200_18() -> None:
    assert _value(_summary("19200.17"), FEDERAL) == D("0")
    assert _value(_summary("19200.18"), FEDERAL) == D("0.129388")
    assert _value(_summary("19200.18"), MARGINAL) == D("0.2052")


def test_2026_the_marginal_tax_rate_at_70000_is_39_48_percent() -> None:
    # Both taxes are positive, over the EI maximum of 68,900 and under the CPP2 band:
    # 0.19602 + 0.1392435 + 0.0595 (CPP 4.95% + 1%).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.19602")
    assert _value(summary, PROVINCIAL) == D("0.1392435")
    assert _value(summary, CONTRIBUTION) == D("0.0595")
    assert _value(summary, MARGINAL) == D("0.3948")


def test_2026_both_gates_are_open_at_275000() -> None:
    summary = _summary("275000")

    assert _value(_federal("275000"), FEDERAL_GATE) == D("1")
    assert _value(summary, TAX_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.33")
    assert _value(summary, MARGINAL) > D("0.33")


@pytest.mark.parametrize(
    ("salary", "gate", "provincial"),
    [
        ("24404.89", "0", "0"),
        ("24404.90", "1", "0.2388054"),
        ("29715.62", "1", "0.2388054"),
        ("29715.63", "1", "0.0804054"),
    ],
)
def test_2026_the_provincial_part_follows_line_105_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)
