"""T1 line 23400 "Net income before adjustments", from the Ontario take-home manifest's part file.

Line 23400 is "Line 54 and line 23400: Line 34 minus line 53 (if negative, show in brackets) Net
income before adjustments" (5006-R page 4). The part file is composed here under a test-local header
and form declaration (the real ones belong to the manifest's other parts), with total income (line
34, through line 15000) and total deductions (line 53, through line 23300) given as starting
amounts because their own part files are not part of this one. The result is not floored: a
deduction above income gives a negative figure, shown in brackets on the form.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.trace import SubtractedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.deductions import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
)
from tax_engine.jurisdictions.ca.catalog.income import TOTAL_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
ONTARIO = JurisdictionCode("CA-ON")
PART = "t1_taxable_income_line_23400.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/total_income
    required: true
  - name: ca/deductions_from_total_income
    required: true
outputs:
  - ca/total_income
  - ca/deductions_from_total_income
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/net_income_before_adjustments
"""


def sheet_23400(
    take_home_service: TakeHomeService, total_income: str, deductions: str
) -> Worksheet:
    service = take_home_service(HEADER, FORM, PART)
    (worksheet,) = service.compute(
        ONTARIO,
        2025,
        Artifact(TOTAL_INCOME, D(total_income)),
        Artifact(DEDUCTIONS_FROM_TOTAL_INCOME, D(deductions)),
    )["ca/t1_taxable_income"]
    return worksheet


def line_23400(take_home_service: TakeHomeService, total_income: str, deductions: str) -> Decimal:
    return (
        sheet_23400(take_home_service, total_income, deductions)
        .get(NET_INCOME_BEFORE_ADJUSTMENTS)
        .value
    )


@pytest.mark.parametrize(
    ("total_income", "deductions", "expected"),
    [
        # The ticket's $70,000 salary: enhanced CPP deduction 665.00, so 70,000 less 665 is 69,335.
        ("70000", "665.00", "69335.00"),
        # $90,000, above the CPP ceiling: enhanced CPP deduction at its 1,074.00 maximum.
        ("90000", "1074.00", "88926.00"),
        # No deductions at all: the net income is the total income.
        ("15000", "0", "15000.00"),
        # Deductions equal to income: exactly 0.
        ("1000", "1000", "0.00"),
        # Deductions above income: the result is negative and is not floored (shown in brackets).
        ("1000", "1500", "-500.00"),
        # A cent case: 1,000.01 less 0.02 is 999.99.
        ("1000.01", "0.02", "999.99"),
    ],
)
def test_line_23400_is_line_34_less_line_53_not_floored(
    take_home_service: TakeHomeService, total_income: str, deductions: str, expected: str
) -> None:
    assert line_23400(take_home_service, total_income, deductions) == D(expected)


@pytest.mark.parametrize(
    ("total_income", "deductions", "printed"),
    [
        # The ticket's $70,000 salary: whole dollars print their cents.
        ("70000", "665.00", "69335.00"),
        ("1000", "1000", "0.00"),
        ("1000", "1500", "-500.00"),
        # Rounded once, half-up, on the exact difference: 1,000.005 less 0 is 1,000.01.
        ("1000.005", "0", "1000.01"),
        # 1,000.014 less 0.005 is 1,000.009, so 1,000.01 (rounding each first gives 1,000.00).
        ("1000.014", "0.005", "1000.01"),
        ("1000.004", "0.001", "1000.00"),
    ],
)
def test_line_23400_prints_cents_through_the_shared_rounding_dataset(
    take_home_service: TakeHomeService, total_income: str, deductions: str, printed: str
) -> None:
    value = line_23400(take_home_service, total_income, deductions)

    assert str(value) == printed
    assert value.as_tuple().exponent == -2


def test_the_line_23400_step_traces_the_cent_rounding(
    take_home_service: TakeHomeService,
) -> None:
    sheet = sheet_23400(take_home_service, "70000", "665.00")

    (line,) = [line for line in sheet.trace if isinstance(line, SubtractedLine)]

    assert line.output == NET_INCOME_BEFORE_ADJUSTMENTS
    assert line.rounding == CENT
    assert str(line.result) == "69335.00"
