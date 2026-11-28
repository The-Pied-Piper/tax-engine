"""The gated marginal tax rate runs for tax year 2026 as well, through the real engine.

The British Columbia manifest is 2025-only but the engine runs 2026 on it, reading each dataset
family's 2026 file, so every dataset of the marginal rate (the gate, the credit rate, the reduction
slope, the exact rounding, the contribution rates of the federal form) needs a 2026 dataset (an
absent year is never carried forward).

No new form text is quoted. The 2026 datasets are provisional (the 2026 forms are not published).
Where each tax first turns positive (2026, salary only): basic federal tax (T1 line 42900) at
19,200.18 and BC428 line 80 at 26,752.96 (measured), inside the reduction's range (25,570 to
44,952, the slope ends at a salary of 45,370.60). At 19,200.18 the federal part opens: 14% x 0.99 -
14% x 0.0658 = 0.129388, and with the contributions (CPP 4.95% + 1%, EI 1.63%) the rate is
0.205188; at 26,752.96 the British Columbia part opens: 5.6% x 0.9242 + 3.56% x 0.99 = 0.0869992;
each other salary pins the structure: the gates are 0 or 1 and open with their taxes, each marginal
part is its gate times its rate, and the total is the exact sum of the three parts rounded
half-up to 0.0001: the engine rounds the marginal rate like the average rate
(`ca/take_home_average_rate_rounding`), so 0.205188 is 0.2052 in the tests.

2026, born 1955 (N = 1):
- Salary 44,119.00 = the threshold, line 4 = 0.00; 44,120.00: line 4 = 1.00, line 7 = 5,926.85.
- Salary 47,000: line 4 = 2,881.00, line 6 = 432.15, line 7 = 5,494.85 (over both thresholds).
  Salary 60,000: line 4 = 15,881.00, line 6 = 2,382.15, line 7 = 3,544.85.
- Salary 83,632.29: line 4 = 39,513.29, line 6 = 5,926.9935 -> 5,926.99, line 7 = 0.01. Salary
  83,632.30: line 4 = 39,513.30, line 6 = 5,926.995 -> 5,927.00 (half up), line 7 = 0.

British Columbia's gate on BC428 line 80 stays on the age term, but a filer over the age threshold
always owes British Columbia tax, so the gate is open at every salary here.
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
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
RETURN = "ca-bc/return"


TAX_AFTER_REDUCTION = "ca-bc/british_columbia_tax_after_reduction_return"
TAX_REDUCTION = "ca-bc/british_columbia_tax_reduction_return"
BC_GATE = "ca-bc/british_columbia_rate_gate"
REDUCTION_GATE = "ca-bc/british_columbia_reduction_gate"
PHASE_OUT = "ca-bc/british_columbia_reduction_phase_out_rate"
BRACKET = "ca-bc/british_columbia_bracket_rate_return"
FEDERAL = "ca-bc/marginal_federal_rate"
BC_RATE = "ca-bc/british_columbia_marginal_rate"
CONTRIBUTION = "ca-bc/marginal_contribution_rate"
MARGINAL = "ca-bc/marginal_tax_rate"
AGE_FORM = "ca-bc/bc428"
AGE_CREDIT_RATE = "ca-bc/marginal_british_columbia_age_credit_rate"
AGE_THRESHOLD_GATE = "ca-bc/british_columbia_age_threshold_gate"
AGE_AMOUNT_GATE = "ca-bc/british_columbia_age_amount_gate"
AGE_LINE_4 = "ca-bc/worksheet_bc428_age_amount_line_4"
AGE_LINE_7 = "ca-bc/worksheet_bc428_age_amount_line_7"


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled British Columbia manifest, as the calculator loads it, salary the
    # only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2026, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


SALARIES = ["0", "100", "2000", "19200.18", "26752.96", "30000", "45370.60", "70000", "250000"]


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_runs_and_the_total_is_the_sum_of_the_gated_parts_rounded_to_four_decimals(
    salary: str,
) -> None:
    summary = _summary(salary)
    federal = _value(summary, FEDERAL)
    british_columbia = _value(summary, BC_RATE)
    contribution = _value(summary, CONTRIBUTION)

    assert _value(summary, MARGINAL) == (federal + british_columbia + contribution).quantize(
        ROUNDING, rounding=ROUND_HALF_UP
    )
    assert _value(summary, BC_GATE) in (D("0"), D("1"))
    assert _value(summary, REDUCTION_GATE) in (D("0"), D("1"))


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_each_gate_opens_with_the_tax_it_reads(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, BC_GATE) == (
        D("1") if _value(summary, TAX_AFTER_REDUCTION) > 0 else D("0")
    )


@pytest.mark.parametrize("salary", SALARIES)
def test_2026_the_reduction_gate_opens_with_the_tax_reduction(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, REDUCTION_GATE) == (
        D("1") if _value(summary, TAX_REDUCTION) > 0 else D("0")
    )


@pytest.mark.parametrize("salary", ["0", "100"])
def test_2026_the_marginal_tax_rate_is_0_where_nothing_is_paid(salary: str) -> None:
    # No income tax, and no CPP or EI yet (the EI band of T2204 line 16 starts at 2,000).
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, BC_RATE) == D("0")
    assert _value(summary, CONTRIBUTION) == D("0")


def test_2026_the_marginal_tax_rate_at_2000_is_the_ei_dollar_for_dollar() -> None:
    # No income tax and no CPP, but the EI band of T2204 line 16 starts at 2,000 (included): the
    # dollar at 2,000 is the first that line 7 counts, so the rate is 1 there, as a cent above.
    summary = _summary("2000")

    assert _value(summary, MARGINAL) == D("1")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, BC_RATE) == D("0")
    assert _value(summary, CONTRIBUTION) == D("1")


@pytest.mark.parametrize("salary", ["0", "100", "2000", "19200.18", "25000"])
def test_2026_the_bracket_rate_is_the_first_bracket_of_the_2026_dataset(salary: str) -> None:
    assert _value(_summary(salary), BRACKET) == D("0.056")


def test_2026_the_federal_part_opens_at_19200_18_and_the_british_columbia_part_at_26752_96() -> (
    None
):
    assert _value(_summary("19200.17"), FEDERAL) == D("0")
    assert _value(_summary("19200.18"), FEDERAL) == D("0.129388")
    assert _value(_summary("19200.18"), MARGINAL) == D("0.2052")
    assert _value(_summary("26752.95"), BC_RATE) == D("0")
    assert _value(_summary("26752.96"), BC_RATE) == D("0.0869992")


def test_2026_the_reduction_slope_ends_at_45370_60() -> None:
    assert _value(_summary("45370.59"), PHASE_OUT) == D("0.0356")
    assert _value(_summary("45370.60"), PHASE_OUT) == D("0")
    assert _value(_summary("45370.60"), BC_RATE) == D("0.0517552")


def test_2026_the_marginal_tax_rate_at_70000_is_32_90_percent() -> None:
    # Both taxes are positive, over the EI maximum of 68,900 and under the CPP2 band:
    # 0.19602 + 0.073458 + 0.0595 (CPP 4.95% + 1%).
    summary = _summary("70000")

    assert _value(summary, FEDERAL) == D("0.19602")
    assert _value(summary, BC_RATE) == D("0.073458")
    assert _value(summary, CONTRIBUTION) == D("0.0595")
    assert _value(summary, MARGINAL) == D("0.329")


def test_2026_both_gates_are_open_at_250000() -> None:
    summary = _summary("250000")

    assert _value(summary, BC_GATE) == D("1")
    assert _value(summary, FEDERAL) == D("0.292949296")
    assert _value(summary, MARGINAL) == D("0.4609")


def _age_sheets(salary: str, birth_year: int | None) -> dict[str, Worksheet]:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if birth_year is not None:
        given.append(Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2026, tuple(given))
    )
    return {form: sheet for form, (sheet, *_) in worksheets.items()}


# 2026: (salary, worksheet line 4, line 7, British Columbia age credit rate), hand-worked in the
# module text.
AGE_RANGE = [
    ("0", "0", "5927", "0"),
    ("44119", "0", "5927", "0"),
    ("44120", "1", "5926.85", "0.0084"),
    ("47000", "2881", "5494.85", "0.0084"),
    ("60000", "15881", "3544.85", "0.0084"),
    ("83632.29", "39513.29", "0.01", "0.0084"),
    ("83632.30", "39513.30", "0", "0"),
]


@pytest.mark.parametrize(("salary", "line_4", "line_7", "age_credit"), AGE_RANGE)
def test_2026_a_filer_born_1955_has_the_age_amount_worksheet_and_credit_rate(
    salary: str, line_4: str, line_7: str, age_credit: str
) -> None:
    sheets = _age_sheets(salary, 1955)

    assert _value(sheets[AGE_FORM], AGE_LINE_4) == D(line_4)
    assert _value(sheets[AGE_FORM], AGE_LINE_7) == D(line_7)
    assert _value(sheets[RETURN], AGE_CREDIT_RATE) == D(age_credit)


@pytest.mark.parametrize("birth_year", [1980, None])
@pytest.mark.parametrize(("salary", "_line_4", "_line_7", "_age_credit"), AGE_RANGE)
def test_2026_a_filer_born_1980_or_with_no_birth_year_has_no_age_credit_rate(
    salary: str, _line_4: str, _line_7: str, _age_credit: str, birth_year: int | None
) -> None:
    assert _value(_age_sheets(salary, birth_year)[RETURN], AGE_CREDIT_RATE) == D("0")


@pytest.mark.parametrize(
    ("salary", "threshold_gate", "amount_gate"),
    [
        ("44119", "0", "1"),
        ("44120", "1", "1"),
        ("83632.29", "1", "1"),
        ("83632.30", "1", "0"),
    ],
)
def test_2026_the_two_age_gates_open_at_the_threshold_and_close_when_the_amount_is_gone(
    salary: str, threshold_gate: str, amount_gate: str
) -> None:
    # The threshold gate follows worksheet line 4 (0.00 up to the threshold), the amount gate the
    # amount still claimed (line 7 reaches 0.00 at the salaries below, to the cent).
    sheets = _age_sheets(salary, 1955)

    assert _value(sheets[RETURN], AGE_THRESHOLD_GATE) == D(threshold_gate)
    assert _value(sheets[RETURN], AGE_AMOUNT_GATE) == D(amount_gate)
