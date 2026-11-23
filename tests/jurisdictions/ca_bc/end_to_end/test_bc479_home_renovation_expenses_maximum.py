"""BC479 line 14, the home renovation expenses checked against their printed maximum, end to end.

Form text (Form BC479, CRA 5010-TC, 2025): "Line 14: Enter your home renovation expenses from line 5
of your Schedule BC(S12). (maximum $10,000) Line 60480 ^ multiplied by 10% = ^". An amount typed
above the printed maximum is rejected with `InputAboveBoundError`, not capped. The bundled engine
(`build_tax_computation`) runs over the real British Columbia manifest with the salary
(`ca/employment_income`) and, where stated, the home renovation expenses typed in. The maximum is
the dataset figure `ca-bc/home_renovation_expenses_maximum`: 10,000 in 2025 and, provisionally,
10,000 in 2026 (carried forward unchanged). Line 14 is the checked amount times the printed 10%.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
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
FORM = "ca-bc/bc479"
INPUT = "ca-bc/bc479_home_renovation_expenses_line_14"
MAXIMUM = "ca-bc/bc479_home_renovation_expenses_maximum"
CHECKED = "ca-bc/bc479_home_renovation_expenses_checked"
LINE_14 = "ca-bc/bc479_home_renovation_credit_line_14"
RETURN = "ca-bc/return"
SALARY = "70000"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _bc479(year: int, expenses: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if expenses is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(expenses)))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, tuple(given))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize("year", [2025, 2026])
def test_an_amount_exactly_at_the_maximum_passes_and_is_multiplied_by_10_percent(year: int) -> None:
    sheet = _bc479(year, "10000.00")

    assert _figure(sheet, CHECKED) == D("10000.00")
    assert _figure(sheet, LINE_14) == D("1000.00")


@pytest.mark.parametrize("year", [2025, 2026])
def test_an_amount_below_the_maximum_passes_unchanged(year: int) -> None:
    sheet = _bc479(year, "5000.00")

    assert _figure(sheet, CHECKED) == D("5000.00")
    assert _figure(sheet, LINE_14) == D("500.00")


@pytest.mark.parametrize("year", [2025, 2026])
def test_an_amount_one_cent_above_the_maximum_is_rejected(year: int) -> None:
    with pytest.raises(InputAboveBoundError):
        _bc479(year, "10000.01")


def test_the_rejection_names_both_kinds() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        _bc479(2025, "10000.01")

    assert INPUT in str(raised.value)
    assert MAXIMUM in str(raised.value)


def test_a_salary_only_request_leaves_the_checked_amount_blank_and_line_14_at_0() -> None:
    sheet = _bc479(2025)

    assert sheet.get(artifact_kinds().kind(CHECKED)).is_blank
    assert _figure(sheet, LINE_14) == D("0.00")


def test_the_maximum_is_10000_in_2025() -> None:
    assert _figure(_bc479(2025), MAXIMUM) == D("10000.00")


def test_the_maximum_is_10000_in_2026() -> None:
    assert _figure(_bc479(2026), MAXIMUM) == D("10000.00")


def test_the_trace_has_one_at_most_line_and_one_credit_amount_line_for_the_maximum() -> None:
    sheet = _bc479(2025, "1000.00")

    at_most = [
        line
        for line in sheet.trace
        if isinstance(line, AtMostLine) and line.output.identifier == CHECKED
    ]
    maximum = [
        line
        for line in sheet.trace
        if isinstance(line, CreditAmountLine) and line.output.identifier == MAXIMUM
    ]
    (line_check,) = at_most
    (maximum_line,) = maximum
    assert line_check.output.identifier == CHECKED
    assert line_check.amount_kind.identifier == INPUT
    assert line_check.amount_value == D("1000.00")
    assert line_check.bound.identifier == MAXIMUM
    assert line_check.bound_value == D("10000.00")
    assert maximum_line.value == D("10000.00")


def _take_home(year: int) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, tuple(given))
    )
    (summary,) = worksheets[RETURN]
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


def test_the_70000_take_home_is_unchanged_in_2025() -> None:
    assert _take_home(2025) == D("54217.74")


def test_the_70000_take_home_is_unchanged_in_2026() -> None:
    assert _take_home(2026) == D("54348.15")
