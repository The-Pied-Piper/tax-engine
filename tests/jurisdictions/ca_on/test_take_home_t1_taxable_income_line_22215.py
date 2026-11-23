"""T1 (5006-R, 2025) line 22215 as the Ontario take-home manifest part wires it.

Form text (5006-R page 4): "Line 48 and line 22215: Deduction for CPP or QPP enhanced contributions
on employment income". The figure is Schedule 8 line 28, which the shared form exports as a record
list of one amount; the step is one core/record_total over it, output `ca/t1_line_22215`.

The real Schedule 8 parts are composed beside the salary, so the figure comes from the salary alone
through the real engine. The header and the form's export are made up here. Expected figures are
hand-computed from the printed Schedule 8 lines (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import T1_LINE_22215
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PARTS = (
    *form_part_names("schedule_8"),
    *form_part_names("t1_employment_income"),
    "t1_taxable_income_line_22215.yaml",
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/t1_line_22215
capabilities: []
"""


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 1% of (70,000 - 3,500) is 665.00.
        ("70000", "665.00"),
        # Under the basic exemption: no contribution.
        ("3500", "0.00"),
    ],
)
def test_line_22215_is_the_schedule_8_deduction(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]

    assert sheet.get(T1_LINE_22215).value == D(expected)
