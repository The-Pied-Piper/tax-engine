"""The gated Prince Edward Island marginal tax rate, 2026, through the real engine.

The 2026 manifest is the 2025 one and the engine runs it on each dataset family's 2026 file, so
the gate, the credit rate and the low-income reduction datasets need a 2026 file (an absent year
is never carried forward). The 2026 datasets are provisional (the 2026 forms are not published).

The provincial part is counted only while PE428 line 97 "Line 93 minus line 96 (if negative,
enter "0")" is above zero, and the low-income tax reduction slope (5%, PE428 line 85) only while
PE428 line 84 and line 87 are both above zero. Each boundary below is found cent by cent from the
engine, and each rate is the hand-worked figure of `test_return_marginal_tax_rate_values.py`; each
other salary pins the structure: the gates are 0 or 1 and open with the amounts they read, the
provincial part is its gate times its rate, and the total is the exact sum of the three parts.

- line 97 is 0.00 at a salary of 19,991.38 and 0.01 at 19,991.39; line 84 is 0.00 at 22,843.43 and
  0.01 at 22,843.44; line 87 is 0.01 at 29,914.03 and 0.00 at 29,914.04; between line 97 opening
  and line 84 opening, and after line 87 is used up, the provincial part is 9.5% x 0.99 - 9.5% x
  0.0658 = 0.087799; in between it is that plus 5% x 0.99 = 0.137299.

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
PRINCE_EDWARD_ISLAND = JurisdictionCode("CA-PE")
RETURN = "ca-pe/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
FEDERAL_AFTER_CREDITS = "ca/marginal_federal_rate_after_credits"
FEDERAL_BRACKET = "ca/marginal_federal_bracket_column_rate"
LINE_97 = "ca-pe/prince_edward_island_tax_return"
TAX_GATE = "ca-pe/prince_edward_island_rate_gate"
PE_BRACKET = "ca-pe/prince_edward_island_bracket_rate_return"
REDUCTION_RATE = "ca-pe/marginal_prince_edward_island_rate_with_reduction"
INCOME_GATE = "ca-pe/income_over_base_amount_gate"
REDUCTION_GATE = "ca-pe/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-pe/low_income_reduction_phase_out_gate"
FEDERAL = "ca-pe/marginal_federal_rate"
PROVINCIAL = "ca-pe/prince_edward_island_marginal_rate"
CONTRIBUTION = "ca-pe/marginal_contribution_rate"
MARGINAL = "ca-pe/marginal_tax_rate"

SALARIES = [
    "0",
    "100",
    "2000",
    "11750",
    "19200.18",
    "19991.39",
    "22843.44",
    "28000",
    "29914.04",
    "70000",
    "275000",
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Prince Edward Island manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate and the federal bracket rate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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
        (TAX_GATE, LINE_97),
        (INCOME_GATE, "ca-pe/income_over_base_amount_return"),
        (REDUCTION_GATE, "ca-pe/low_income_tax_reduction_return"),
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
    assert _value(summary, PE_BRACKET) == D("0.095")


def test_2026_the_federal_part_opens_at_19200_18() -> None:
    assert _value(_summary("19200.17"), FEDERAL) == D("0")
    assert _value(_summary("19200.18"), FEDERAL) == D("0.129388")
    assert _value(_summary("19200.18"), MARGINAL) == D("0.2052")


def test_2026_the_marginal_tax_rate_at_70000_is_41_52_percent() -> None:
    # Both taxes are positive, over the EI maximum of 68,900 and under the CPP2 band:
    # 0.19602 + 0.1596375 + 0.0595 (CPP 4.95% + 1%).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.19602")
    assert _value(summary, PROVINCIAL) == D("0.1596375")
    assert _value(summary, CONTRIBUTION) == D("0.0595")
    assert _value(summary, MARGINAL) == D("0.4152")


def test_2026_both_gates_are_open_at_275000() -> None:
    summary = _summary("275000")

    assert _value(_federal("275000"), FEDERAL_GATE) == D("1")
    assert _value(summary, TAX_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.33")
    assert _value(summary, MARGINAL) > D("0.33")


@pytest.mark.parametrize(
    ("salary", "gate", "provincial"),
    [
        ("19991.38", "0", "0"),
        ("19991.39", "1", "0.087799"),
        ("22843.43", "1", "0.087799"),
        ("22843.44", "1", "0.137299"),
        ("29914.03", "1", "0.137299"),
        ("29914.04", "1", "0.087799"),
    ],
)
def test_2026_the_provincial_part_follows_line_97_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)
