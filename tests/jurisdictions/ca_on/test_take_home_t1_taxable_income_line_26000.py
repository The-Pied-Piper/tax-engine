"""T1 line 26000 "Taxable income", from the Ontario take-home manifest's part file.

Line 26000 is "Line 69 and line 26000: Line 57 minus line 68 (if negative, enter "0")
Taxable income" (5006-R page 5). The part file is composed here under a test-local header and
form declaration (the real ones belong to the manifest's other parts), with net income (line 57,
through line 23600) given as a starting amount because its own part file is not part of this
one. Deductions from net income (line 68, through line 25700) are an optional input, declared in
the form's inputs part that is composed with it: left out, they read as 0. The result is floored at
zero: a deduction above net income gives 0, not a negative figure.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import NET_INCOME
from tax_engine.jurisdictions.ca.catalog.taxable_income import (
    DEDUCTIONS_FROM_NET_INCOME,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

ONTARIO = JurisdictionCode("CA-ON")
PARTS = ("t1_taxable_income_line_25700_inputs.yaml", "t1_taxable_income_line_26000.yaml")
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/net_income
    required: true
outputs:
  - ca/net_income
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/taxable_income
"""


def line_26000(
    take_home_service: TakeHomeService, net_income: str, deductions: str | None = None
) -> Decimal:
    service = take_home_service(HEADER, FORM, *PARTS)
    artifacts = [Artifact(NET_INCOME, Decimal(net_income))]
    if deductions is not None:
        artifacts.append(Artifact(DEDUCTIONS_FROM_NET_INCOME, Decimal(deductions)))
    (worksheet,) = service.compute(ONTARIO, 2025, *artifacts)["ca/t1_taxable_income"]
    return worksheet.get(TAXABLE_INCOME).value


@pytest.mark.parametrize(
    ("net_income", "deductions", "expected"),
    [
        # The ticket's $70,000 salary: net income 69,335.00, line 25700 left out, so it reads as 0.
        ("69335.00", None, "69335.00"),
        # $90,000: net income 88,926.00, line 25700 left out.
        ("88926.00", None, "88926.00"),
        # A deduction below net income is taken off in full.
        ("69335.00", "1000", "68335.00"),
        # Deductions equal to net income: exactly 0.
        ("1000", "1000", "0.00"),
        # Deductions above net income: floored at 0, not negative.
        ("1000", "1500", "0.00"),
        # A cent case: 1,000.01 less 0.02 is 999.99.
        ("1000.01", "0.02", "999.99"),
    ],
)
def test_line_26000_is_line_57_less_line_68_floored_at_zero(
    take_home_service: TakeHomeService, net_income: str, deductions: str | None, expected: str
) -> None:
    assert line_26000(take_home_service, net_income, deductions) == Decimal(expected)
