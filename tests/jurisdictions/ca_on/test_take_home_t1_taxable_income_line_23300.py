"""T1 (2025) line 23300, total deductions from total income, from the real part files.

T1 line 23300: "Line 53 and line 23300: Add lines 35 to 52." (5006-R, page 4). A salary-only filer
has one deduction, line 22215, the CPP enhanced contributions deduction that Schedule 8 line 28
exports. Another form's export reaches this form only as the record list of one amount
`ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return`, so the one step is a
`core/record_total` over it and the output is `ca/deductions_from_total_income`.

The real Schedule 8 parts are composed beside the salary and the line 23300 part, so the figure
comes from the salary alone through the real engine. The T1 form declaration is test-local: it
exports line 23300, the only T1 line composed here, because the real one exports lines whose parts
are not.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import DEDUCTIONS_FROM_TOTAL_INCOME
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_line_23300.yaml",
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs:
  - ca/employment_income
capabilities: []
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/deductions_from_total_income
capabilities: []
"""


def line_23300(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    value = sheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # The $70,000 salary: the Schedule 8 deduction is 665.00, the only line to add.
        ("70000", "665.00"),
        # The $90,000 salary, above the CPP ceiling: the printed maximum, 1,074.00.
        ("90000", "1074.00"),
        # The $3,500 salary, under the basic exemption: no contribution, so 0.00.
        ("3500", "0.00"),
    ],
)
def test_line_23300_is_the_schedule_8_deduction(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_23300(take_home_service, salary) == D(expected)
