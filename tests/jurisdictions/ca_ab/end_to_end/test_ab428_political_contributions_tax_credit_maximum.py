"""AB428 line 72, the political contributions credit checked against its maximum, end to end.

Form text (Form AB428, CRA 5009-c-25e.txt line 238, confirmed): "Line 72: Alberta political
contributions tax credit (use Worksheet AB428) (maximum $1,000)". Worksheet AB428 is not built, so
line 72 is an entry line: an amount typed above the printed maximum is rejected with
`InputAboveBoundError` (a `ValidationError`), not capped. The bundled engine
(`build_tax_computation`) runs over the real Alberta manifest with the salary (70,000, where line
70 is 3,598.12 in 2025 and 3,534.79 in 2026) and, where stated, the credit typed in. The maximum is
the dataset figure `ca-ab/political_contributions_tax_credit_maximum`: 1,000 in 2025 and,
provisionally, 1,000 in 2026.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError, ValidationError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import AtMostLine, CreditAmountLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds
from tests.jurisdictions.ca_ab.support import alberta_kinds

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")
INPUT = "ca-ab/ab428_political_contributions_credit_line_72"
MAXIMUM = "ca-ab/political_contributions_tax_credit_maximum"
LINE_72 = "ca-ab/ab428_alberta_political_contributions_tax_credit_line_72"
LINE_70 = "ca-ab/ab428_tax_line_70"
LINE_73 = "ca-ab/ab428_tax_line_73"
RETURN = "ca-ab/return"
LINE_167 = "ca/refund_or_balance_owing"
FORM = "ca-ab/ab428"
SALARY = "70000"
LINE_70_AT_SALARY = {2025: D("3598.12"), 2026: D("3534.79")}
# Salary-only T1 line 167 (the take-home is the salary less CPP, EI and this), unchanged.
LINE_167_AT_SALARY = {2025: D("11183.76"), 2026: D("10812.98")}


def _figure(sheet: Worksheet, name: str) -> Any:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _sheet(year: int, credit: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if credit is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(credit)))
    worksheets = build_tax_computation().compute(TaxCalculationRequest(ALBERTA, year, tuple(given)))
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize("year", [2025, 2026])
def test_a_salary_only_request_leaves_line_72_blank_and_line_73_equals_line_70(year: int) -> None:
    sheet = _sheet(year)

    assert sheet.get(alberta_kinds().kind(LINE_72)).is_blank
    assert _figure(sheet, LINE_73) == LINE_70_AT_SALARY[year]
    assert _figure(sheet, LINE_70) == LINE_70_AT_SALARY[year]


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_salary_only_return_figure_is_unchanged(year: int) -> None:
    (summary,) = build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, year, (Artifact(EMPLOYMENT_INCOME, D(SALARY)),))
    )[RETURN]

    assert _figure(summary, LINE_167) == LINE_167_AT_SALARY[year]


def test_the_maximum_is_1000_in_2025() -> None:
    assert _figure(_sheet(2025), MAXIMUM) == D("1000.00")


def test_the_maximum_is_1000_in_2026() -> None:
    assert _figure(_sheet(2026), MAXIMUM) == D("1000.00")


def test_an_amount_exactly_at_the_maximum_passes_and_reduces_line_73() -> None:
    sheet = _sheet(2025, "1000.00")

    assert _figure(sheet, LINE_72) == D("1000.00")
    assert _figure(sheet, LINE_73) == LINE_70_AT_SALARY[2025] - D("1000.00")
    assert _figure(sheet, LINE_73) == D("2598.12")


def test_an_amount_below_the_maximum_passes_unchanged() -> None:
    assert _figure(_sheet(2025, "250.50"), LINE_72) == D("250.50")


def test_an_amount_of_zero_passes() -> None:
    assert _figure(_sheet(2025, "0"), LINE_72) == D("0")


def test_an_amount_one_cent_above_the_maximum_is_rejected_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(2025, "1000.01")


def test_the_rejection_is_a_validation_error() -> None:
    with pytest.raises(ValidationError):
        _sheet(2025, "1000.01")


def test_the_rejection_names_both_kinds() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        _sheet(2025, "1000.01")

    assert INPUT in str(raised.value)
    assert MAXIMUM in str(raised.value)


def test_a_2026_amount_at_its_maximum_passes() -> None:
    assert _figure(_sheet(2026, "1000.00"), LINE_72) == D("1000.00")


def test_a_2026_amount_one_cent_above_the_maximum_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(2026, "1000.01")


def test_the_trace_has_one_at_most_line_and_one_credit_amount_line_for_the_maximum() -> None:
    sheet = _sheet(2025, "500.00")

    at_most = [line for line in sheet.trace if isinstance(line, AtMostLine)]
    maximum = [
        line
        for line in sheet.trace
        if isinstance(line, CreditAmountLine) and line.output.identifier == MAXIMUM
    ]
    (line_72,) = [line for line in at_most if line.output.identifier == LINE_72]
    (maximum_line,) = maximum
    assert line_72.amount_kind.identifier == INPUT
    assert line_72.amount_value == D("500.00")
    assert line_72.bound.identifier == MAXIMUM
    assert line_72.bound_value == D("1000.00")
    assert maximum_line.value == D("1000.00")
