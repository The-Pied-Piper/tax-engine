"""T1 (2025) line 23300, total deductions from total income, as the Ontario take-home manifest part
wires it: the total of the deductions the filer has, here only Schedule 8's CPP enhanced
contributions.

Form text (5006-R page 4): "Line 53 and line 23300: Add lines 35 to 52." A salary-only filer has one
deduction, line 22215, which Schedule 8 line 28 exports ("Enter this amount ... on line 22215 of
your return"). T1 reads another form's export as the kind `ca/schedule_8.<export>`, a record list
of one amount, so the step is core/record_total over it.

The real parts compose here: the salary, every Schedule 8 part and the T1 form part and line part,
under a test-only header, with only the gross salary typed in. This is not a worked return.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import DEDUCTIONS_FROM_TOTAL_INCOME
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
PARTS = (
    "salary.yaml",
    *sorted(path.name for path in Path(TAKE_HOME).glob("schedule_8*.yaml")),
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_23300.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Salary 70,000: Schedule 8 line 28 is 665.00, the 1% enhanced deduction.
        ("70000", "665.00"),
        # Salary 90,000, above the CPP ceiling: line 28 is at its 1,074.00 maximum.
        ("90000", "1074.00"),
    ],
)
def test_line_23300_is_the_schedule_8_cpp_enhanced_contributions(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    worksheets = take_home_service(HEADER, "capabilities: []\n", *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    assert sheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D(expected)
