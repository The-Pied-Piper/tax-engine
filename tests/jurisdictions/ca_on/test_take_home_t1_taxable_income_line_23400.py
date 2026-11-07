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
from tax_engine.jurisdictions.ca.catalog.deductions import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
)
from tax_engine.jurisdictions.ca.catalog.income import TOTAL_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
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


def line_23400(take_home_service: TakeHomeService, total_income: str, deductions: str) -> Decimal:
    service = take_home_service(HEADER, FORM, PART)
    (worksheet,) = service.compute(
        ONTARIO,
        2025,
        Artifact(TOTAL_INCOME, D(total_income)),
        Artifact(DEDUCTIONS_FROM_TOTAL_INCOME, D(deductions)),
    )["ca/t1_taxable_income"]
    return worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value


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
