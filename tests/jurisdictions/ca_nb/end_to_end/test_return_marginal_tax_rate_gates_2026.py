"""The gated New Brunswick marginal tax rate, 2026, through the real engine.

The 2026 manifest is the 2025 one and the engine runs it on each dataset family's 2026 file, so
the gate, the credit rate, the exact rounding and the low-income reduction datasets need a 2026
file (an absent year is never carried forward). The 2026 datasets are provisional (the 2026 forms
are not published).

The provincial part is counted only while NB428 line 97 "Line 95 minus line 96 (if negative, enter
"0")" is above zero, and the low-income tax reduction slope (3%, NB428 line 84) only while NB428
line 83 and line 86 are both above zero. Each boundary below is found cent by cent from the engine,
and each rate is the hand-worked figure of `test_return_marginal_tax_rate_values.py`; each other
salary pins the structure: the gates are 0 or 1 and open with the amounts they read, the provincial
part is its gate times its rate, and the total is the exact sum of the three parts.

- line 97 is 0.00 at a salary of 23,611.70 and 0.01 at 23,611.71; line 86 is 0.01 at 50,090.39 and
  0.00 at 50,090.40; in between the provincial part is 9.4% x 0.99 - 9.4% x 0.0658 + 3% x 0.99 =
  0.1165748, and after it 0.0868748;
- the age amount falls, for a filer born in 1961 or earlier, from net income 45,844 (worksheet
  line 4 is 0.00 at a salary of 45,844 and 0.01 at 45,844.01) until it is 0 (the amount left is
  0.01 at a salary of 86,897.29 and 0.00 at 86,897.30; the filer born in 1955 is 71 and pays no
  CPP, so the net income is the salary), at 15% x 9.4% = 0.0141 of tax per dollar in the range.

The engine rounds the marginal tax rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`): the total is the sum of the parts rounded half-up to four
places, and the marginal values pinned below are the exact figures in the comments rounded the same
way; the parts stay exact.
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
NEW_BRUNSWICK = JurisdictionCode("CA-NB")
RETURN = "ca-nb/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
FEDERAL_AFTER_CREDITS = "ca/marginal_federal_rate_after_credits"
FEDERAL_BRACKET = "ca/marginal_federal_bracket_column_rate"
LINE_97 = "ca-nb/new_brunswick_tax_return"
TAX_GATE = "ca-nb/new_brunswick_rate_gate"
NB_BRACKET = "ca-nb/new_brunswick_bracket_rate_return"
REDUCTION_RATE = "ca-nb/marginal_new_brunswick_rate_with_reduction"
INCOME_GATE = "ca-nb/income_over_base_amount_gate"
REDUCTION_GATE = "ca-nb/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-nb/low_income_reduction_phase_out_gate"
FEDERAL = "ca-nb/marginal_federal_rate"
PROVINCIAL = "ca-nb/new_brunswick_marginal_rate"
CONTRIBUTION = "ca-nb/marginal_contribution_rate"
MARGINAL = "ca-nb/marginal_tax_rate"
AGE_LINE_4 = "ca-nb/marginal_age_income_over_threshold"
AGE_CLAIMED = "ca-nb/marginal_age_amount_claimed"
AGE_LINE_4_GATE = "ca-nb/marginal_age_threshold_gate"
AGE_CLAIMED_GATE = "ca-nb/marginal_age_amount_gate"
AGE_REDUCTION_RATE = "ca-nb/marginal_age_reduction_rate"
AGE_CREDIT_RATE = "ca-nb/marginal_new_brunswick_age_credit_rate"

SALARIES = [
    "0",
    "100",
    "2000",
    "11750",
    "19200.18",
    "23611.71",
    "28000",
    "50090.40",
    "70000",
    "275000",
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled New Brunswick manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate and the federal bracket rate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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
        (INCOME_GATE, "ca-nb/income_over_base_amount_return"),
        (REDUCTION_GATE, "ca-nb/low_income_tax_reduction_return"),
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
    assert _value(summary, NB_BRACKET) == D("0.094")


def test_2026_the_federal_part_opens_at_19200_18() -> None:
    assert _value(_summary("19200.17"), FEDERAL) == D("0")
    assert _value(_summary("19200.18"), FEDERAL) == D("0.129388")
    assert _value(_summary("19200.18"), MARGINAL) == D("0.2052")


def test_2026_the_marginal_tax_rate_at_70000_is_38_95_percent() -> None:
    # Both taxes are positive, over the EI maximum of 68,900 and under the CPP2 band:
    # 0.19602 + 0.133947 + 0.0595 (CPP 4.95% + 1%).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.19602")
    assert _value(summary, PROVINCIAL) == D("0.133947")
    assert _value(summary, CONTRIBUTION) == D("0.0595")
    assert _value(summary, MARGINAL) == D("0.3895")


def test_2026_both_gates_are_open_at_275000() -> None:
    summary = _summary("275000")

    assert _value(_federal("275000"), FEDERAL_GATE) == D("1")
    assert _value(summary, TAX_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.33")
    assert _value(summary, MARGINAL) > D("0.33")


@pytest.mark.parametrize(
    ("salary", "gate", "provincial"),
    [
        ("23611.70", "0", "0"),
        ("23611.71", "1", "0.1165748"),
        ("50090.39", "1", "0.1165748"),
        ("50090.40", "1", "0.0868748"),
    ],
)
def test_2026_the_provincial_part_follows_line_97_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)


def _age_summary(salary: str, birth_year: int | None) -> Worksheet:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if birth_year is not None:
        given.append(Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, 2026, tuple(given))
    )
    (summary,) = worksheets[RETURN]
    return summary


@pytest.mark.parametrize(
    (
        "salary",
        "line_4",
        "line_4_gate",
        "claimed",
        "claimed_gate",
        "reduction_rate",
        "credit_rate",
    ),
    [
        # The filer born in 1955 is 71 in 2026, pays no CPP, so the net income is the salary.
        ("45844", "0.00", "0", "6158.00", "1", "0", "0"),
        # 15% of 0.01 is 0.0015, which rounds to 0.00: the amount claimed is still the maximum.
        ("45844.01", "0.01", "1", "6158.00", "1", "0.15", "0.0141"),
        ("50000", "4156.00", "1", "5534.60", "1", "0.15", "0.0141"),
        # 15% of 41,053.29 is 6,157.9935 (6,157.99, 0.01 left); of 41,053.30 it is 6,157.995, which
        # rounds half up to 6,158.00 and leaves nothing.
        ("86897.29", "41053.29", "1", "0.01", "1", "0.15", "0.0141"),
        ("86897.30", "41053.30", "1", "0.00", "0", "0", "0"),
    ],
)
def test_the_age_gates_open_with_line_4_and_the_amount_claimed_for_a_filer_born_in_1955(
    salary: str,
    line_4: str,
    line_4_gate: str,
    claimed: str,
    claimed_gate: str,
    reduction_rate: str,
    credit_rate: str,
) -> None:
    summary = _age_summary(salary, 1955)

    assert _value(summary, AGE_LINE_4) == D(line_4)
    assert _value(summary, AGE_LINE_4_GATE) == D(line_4_gate)
    assert _value(summary, AGE_CLAIMED) == D(claimed)
    assert _value(summary, AGE_CLAIMED_GATE) == D(claimed_gate)
    assert _value(summary, AGE_REDUCTION_RATE) == D(reduction_rate)
    assert _value(summary, AGE_CREDIT_RATE) == D(credit_rate)


@pytest.mark.parametrize("birth_year", [1980, None])
@pytest.mark.parametrize("salary", ["0", "45844.01", "50000", "86897.29"])
def test_the_age_amount_is_not_claimed_and_adds_no_rate_for_a_filer_born_in_1980_or_with_no_year(
    salary: str, birth_year: int | None
) -> None:
    # Worksheet line 4 is worked out for every filer, but with no age amount claimed the gate on
    # the amount is 0, so the term is 0.
    summary = _age_summary(salary, birth_year)

    assert _value(summary, AGE_CLAIMED) == D("0")
    assert _value(summary, AGE_CLAIMED_GATE) == D("0")
    assert _value(summary, AGE_REDUCTION_RATE) == D("0")
    assert _value(summary, AGE_CREDIT_RATE) == D("0")


def test_the_age_term_is_held_by_the_new_brunswick_tax_gate_at_a_salary_of_0() -> None:
    # Born in 1955 and a salary of 0: the amount is claimed in full, line 4 is 0.00 and no tax is
    # due, so no part of the rate is counted.
    summary = _age_summary("0", 1955)

    assert _value(summary, AGE_CLAIMED_GATE) == D("1")
    assert _value(summary, AGE_LINE_4_GATE) == D("0")
    assert _value(summary, TAX_GATE) == D("0")
    assert _value(summary, PROVINCIAL) == D("0")
