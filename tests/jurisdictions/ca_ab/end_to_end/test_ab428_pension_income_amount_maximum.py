"""AB428 line 34, the pension income amount checked against its printed maximum, end to end.

Form text (Form AB428, CRA 5009-c-25e.txt line 142, confirmed): "Line 34 and line 58360: Pension
income amount (maximum $1,719) ^". An amount typed above the printed maximum is rejected with
`InputAboveBoundError`, not capped. The bundled engine (`build_tax_computation`) runs over the real
Alberta manifest with the salary (`ca/employment_income`) and, where stated, the pension income
amount typed in. The maximum is the dataset figure `ca-ab/pension_income_amount_maximum`: 1,719 in
2025 and, provisionally, 1,753 in 2026 (1,719 x 1.02 rounded down). Line 36 is line 33 (26,692.23 at
a 70,000 salary, from its own test) plus line 34.
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
ALBERTA = JurisdictionCode("CA-AB")
INPUT = "ca-ab/ab428_pension_income_amount"
MAXIMUM = "ca-ab/pension_income_amount_maximum"
LINE_34 = "ca-ab/ab428_pension_income_amount_line_34"
LINE_36 = "ca-ab/ab428_credits_subtotal_line_36"
CREDITS = "ca-ab/ab428_credits"
SALARY = "70000"
LINE_33_AT_SALARY = D("26692.23")


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _credits(year: int, pension: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if pension is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(pension)))
    worksheets = build_tax_computation().compute(TaxCalculationRequest(ALBERTA, year, tuple(given)))
    (sheet,) = worksheets[CREDITS]
    return sheet


def test_a_salary_only_request_has_line_34_of_0_and_line_36_unchanged() -> None:
    sheet = _credits(2025)

    assert _figure(sheet, LINE_34) == D("0")
    assert _figure(sheet, LINE_36) == LINE_33_AT_SALARY


def test_the_maximum_is_1719_in_2025() -> None:
    assert _figure(_credits(2025), MAXIMUM) == D("1719.00")


def test_the_maximum_is_1753_in_2026() -> None:
    assert _figure(_credits(2026), MAXIMUM) == D("1753.00")


def test_an_amount_exactly_at_the_maximum_passes_and_flows_into_line_36() -> None:
    sheet = _credits(2025, "1719.00")

    assert _figure(sheet, LINE_34) == D("1719.00")
    assert _figure(sheet, LINE_36) == LINE_33_AT_SALARY + D("1719.00")


def test_an_amount_below_the_maximum_passes_unchanged() -> None:
    assert _figure(_credits(2025, "1000.00"), LINE_34) == D("1000.00")


def test_an_amount_one_cent_above_the_maximum_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError):
        _credits(2025, "1719.01")


def test_the_rejection_names_both_kinds() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        _credits(2025, "1719.01")

    assert INPUT in str(raised.value)
    assert MAXIMUM in str(raised.value)


def test_a_2026_amount_at_its_maximum_of_1753_passes() -> None:
    sheet = _credits(2026, "1753.00")

    assert _figure(sheet, LINE_34) == D("1753.00")


def test_a_2026_amount_one_cent_above_1753_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError):
        _credits(2026, "1753.01")


def test_the_2025_maximum_does_not_bound_a_2026_request() -> None:
    # 1,719.01 is above the 2025 maximum but below the 2026 one of 1,753.
    assert _figure(_credits(2026, "1719.01"), LINE_34) == D("1719.01")


def test_the_trace_has_one_at_most_line_and_one_credit_amount_line_for_the_maximum() -> None:
    sheet = _credits(2025, "1000.00")

    at_most = [
        line
        for line in sheet.trace
        if isinstance(line, AtMostLine) and line.output.identifier == LINE_34
    ]
    maximum = [
        line
        for line in sheet.trace
        if isinstance(line, CreditAmountLine) and line.output.identifier == MAXIMUM
    ]
    (line_34,) = at_most
    (maximum_line,) = maximum
    assert line_34.output.identifier == LINE_34
    assert line_34.amount_kind.identifier == INPUT
    assert line_34.amount_value == D("1000.00")
    assert line_34.bound.identifier == MAXIMUM
    assert line_34.bound_value == D("1719.00")
    assert maximum_line.value == D("1719.00")


def _take_home(year: int, pension: str | None = None) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if pension is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(pension)))
    worksheets = build_tax_computation().compute(TaxCalculationRequest(ALBERTA, year, tuple(given)))
    (summary,) = worksheets["ca-ab/return"]
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


def _line_75(year: int, pension: str | None = None) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if pension is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(pension)))
    (ab428,) = build_tax_computation().compute(TaxCalculationRequest(ALBERTA, year, tuple(given)))[
        "ca-ab/ab428"
    ]
    return _figure(ab428, "ca-ab/ab428_alberta_tax_line_75")


def test_the_70000_take_home_is_unchanged_with_no_pension_income_amount() -> None:
    assert _take_home(2025) == D("53782.01")
    assert _take_home(2026) == D("54107.20")


def test_a_pension_income_amount_of_1719_lowers_alberta_tax_by_the_credit_at_8_percent() -> None:
    # Line 34 of 1,719.00 adds to line 36 and so to the credits at the 8% credit rate (0.08 x
    # 1,719.00 = 137.52), hand-checked from the form. Alberta tax at 70,000 falls from 3,598.12 to
    # 3,460.60 and the take-home rises by the same 137.52.
    assert _line_75(2025, "1719.00") == D("3598.12") - D("137.52")
    assert _take_home(2025, "1719.00") == D("53782.01") + D("137.52")
