"""T1 line 26000 "Taxable income", from the Ontario take-home manifest's part file.

Line 26000 is "Line 69 and line 26000: Line 57 minus line 68 (if negative, enter "0")
Taxable income" (5006-R page 5). The part file is composed here under a test-local header and
form declaration (the real ones belong to the manifest's other parts), with net income (line 57,
through line 23600) given as a starting amount because its own part file is not part of this
one. Deductions from net income (line 68, through line 25700) are the sum of the optional lines 58
to 67, composed with it: given here through line 25400 (line 65), and left out, they read as 0. The
result is floored at zero: a deduction above net income gives 0, not a negative figure.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import NET_INCOME
from tax_engine.jurisdictions.ca.catalog.taxable_income import (
    T1_LINE_25400,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

ONTARIO = JurisdictionCode("CA-ON")
PARTS = (
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/taxable_income
    - ca/uccb_income_line_11700
    - ca/rdsp_income_line_12500
    - ca/uccb_repayment_line_21300
    - ca/rdsp_income_repayment_line_23200
inputs:
  - name: ca/net_income
    required: true
"""


def line_26000(
    take_home_service: TakeHomeService, net_income: str, deductions: str | None = None
) -> Decimal:
    service = take_home_service(HEADER, FORM, *PARTS)
    artifacts = [Artifact(NET_INCOME, Decimal(net_income))]
    if deductions is not None:
        artifacts.append(Artifact(T1_LINE_25400, Decimal(deductions)))
    (worksheet,) = service.compute(TaxCalculationRequest(ONTARIO, 2025, tuple(artifacts)))[
        "ca/t1_taxable_income"
    ]
    return worksheet.get(TAXABLE_INCOME).value


@pytest.mark.parametrize(
    ("net_income", "deductions", "expected"),
    [
        # The ticket's $70,000 salary: net income 69,335.00, line 25700 left out, so it reads as 0.
        ("69335.00", None, "69335.00"),
        # A deduction below net income is taken off in full.
        ("69335.00", "1000", "68335.00"),
        # Deductions above net income: floored at 0, not negative.
        ("1000", "1500", "0.00"),
    ],
)
def test_line_26000_is_line_57_less_line_68_floored_at_zero(
    take_home_service: TakeHomeService, net_income: str, deductions: str | None, expected: str
) -> None:
    assert line_26000(take_home_service, net_income, deductions) == Decimal(expected)
