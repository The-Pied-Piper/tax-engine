"""BC428 line 84, the political contribution tax credit against its printed maximum, end to end.

Form text (Form BC428, CRA 5010-c-25e.txt line 285-286, confirmed): "Line 84: British Columbia
political contribution tax credit (use Worksheet BC428) (maximum $500)". An amount typed above the
printed maximum is rejected with `InputAboveBoundError`, not capped. The bundled engine
(`build_tax_computation`) runs over the real British Columbia manifest with the salary
(`ca/employment_income`) and, where stated, the credit typed in. The maximum is the dataset figure
`ca-bc/political_contribution_tax_credit_maximum`: 500 in 2025 and, provisionally, 500 in 2026
(carried forward). Line 85 is line 82 less line 84, not below 0; at a 70,000 salary line 82 is
3,162.39 in 2025 and 3,293.84 in 2026 (the line 91 figures of `test_bc428.py` and
`test_bc428_2026.py`, no other credit being claimed), so a line 84 of 400.00 gives 2,762.39 and
2,893.84.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import AtMostLine, CreditAmountLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
INPUT = "ca-bc/bc428_political_contribution_tax_credit_line_84"
MAXIMUM = "ca-bc/bc428_political_contribution_tax_credit_maximum"
LINE_84 = "ca-bc/bc428_british_columbia_political_contribution_tax_credit_line_84"
LINE_85 = "ca-bc/bc428_tax_after_political_credit_line_85"
BC428 = "ca-bc/bc428"
SALARY = "70000"
LINE_85_AT_SALARY = {2025: D("3162.39"), 2026: D("3293.84")}
TAKE_HOME = {2025: D("54217.74"), 2026: D("54348.15")}


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _given(credit: str | None) -> list[Artifact[Decimal]]:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if credit is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(credit)))
    return given


def _bc428(year: int, credit: str | None = None) -> Worksheet:
    worksheets = build_tax_computation().compute(BRITISH_COLUMBIA, year, *_given(credit))
    (sheet,) = worksheets[BC428]
    return sheet


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_maximum_is_500(year: int) -> None:
    assert _figure(_bc428(year), MAXIMUM) == D("500.00")


@pytest.mark.parametrize("year", [2025, 2026])
def test_an_amount_exactly_at_the_maximum_passes(year: int) -> None:
    sheet = _bc428(year, "500.00")

    assert _figure(sheet, LINE_84) == D("500.00")
    assert _figure(sheet, LINE_85) == LINE_85_AT_SALARY[year] - D("500.00")


@pytest.mark.parametrize("year", [2025, 2026])
def test_an_amount_one_cent_above_the_maximum_is_rejected(year: int) -> None:
    with pytest.raises(InputAboveBoundError):
        _bc428(year, "500.01")


def test_the_rejection_names_both_kinds() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        _bc428(2025, "500.01")

    assert INPUT in str(raised.value)
    assert MAXIMUM in str(raised.value)


@pytest.mark.parametrize("year", [2025, 2026])
def test_a_blank_credit_leaves_line_84_blank_and_line_85_unchanged(year: int) -> None:
    sheet = _bc428(year)

    assert sheet.get(artifact_kinds().kind(LINE_84)).is_blank
    assert _figure(sheet, LINE_85) == LINE_85_AT_SALARY[year]


@pytest.mark.parametrize("year", [2025, 2026])
def test_a_claim_of_400_reduces_line_85_by_400(year: int) -> None:
    sheet = _bc428(year, "400.00")

    assert _figure(sheet, LINE_84) == D("400.00")
    assert _figure(sheet, LINE_85) == LINE_85_AT_SALARY[year] - D("400.00")


def test_the_trace_has_one_at_most_line_and_one_credit_amount_line_for_the_maximum() -> None:
    sheet = _bc428(2025, "400.00")

    at_most = [
        line
        for line in sheet.trace
        if isinstance(line, AtMostLine) and line.output.identifier == LINE_84
    ]
    maximum = [
        line
        for line in sheet.trace
        if isinstance(line, CreditAmountLine) and line.output.identifier == MAXIMUM
    ]
    (line_84,) = at_most
    (maximum_line,) = maximum
    assert line_84.output.identifier == LINE_84
    assert line_84.amount_kind.identifier == INPUT
    assert line_84.amount_value == D("400.00")
    assert line_84.bound.identifier == MAXIMUM
    assert line_84.bound_value == D("500.00")
    assert maximum_line.value == D("500.00")


def _take_home(year: int, credit: str | None = None) -> Decimal:
    worksheets = build_tax_computation().compute(BRITISH_COLUMBIA, year, *_given(credit))
    (summary,) = worksheets["ca-bc/return"]
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    cpp = sum(
        (
            _figure(schedule_8, name)
            for name in (
                "ca/schedule_8_cpp_base_contributions_on_return",
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
            )
        ),
        D("0"),
    )
    return (
        D(SALARY)
        - cpp
        - _figure(t2204, "ca/t2204_premiums_deducted")
        - _figure(summary, "ca/refund_or_balance_owing")
    )


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_70000_take_home_is_unchanged_with_no_political_contribution(year: int) -> None:
    assert _take_home(year) == TAKE_HOME[year]


@pytest.mark.parametrize("year", [2025, 2026])
def test_a_claim_of_400_raises_the_take_home_by_400(year: int) -> None:
    assert _take_home(year, "400.00") == TAKE_HOME[year] + D("400.00")
