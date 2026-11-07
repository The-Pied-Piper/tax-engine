"""T1 (2025) line 23300, total deductions from total income, as the Ontario take-home manifest part
wires it: the sum of the parts the filer has, here only Schedule 8's CPP enhanced contributions.

Form text (5006-R page 4): "Line 53 and line 23300: Add lines 35 to 52." The line is a sum, a
calculation, so step 1 takes it through core/sum over the one part present. The part is
`ca/schedule_8_cpp_enhanced_contributions_on_return`, the export Schedule 8 line 28 produces (the
name the form prints: "Enter this amount ... on line 22215 of your return"). The output is
`ca/deductions_from_total_income`.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. The Schedule 8 export is a required starting input, as the
T2204 line 14 test declares its lines 8 and 13.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_23300.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/schedule_8_cpp_enhanced_contributions_on_return
        required: true
    outputs:
      - ca/schedule_8_cpp_enhanced_contributions_on_return
    """)
FORM = dedent("""\
    form:
      name: ca/t1_taxable_income
      required: true
      exports:
        - ca/deductions_from_total_income
    """)


def line_23300(take_home_service: TakeHomeService, schedule_8_line_28: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN, D(schedule_8_line_28)),
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value


@pytest.mark.parametrize(
    ("schedule_8_line_28", "expected"),
    [
        # Salary 70,000: Schedule 8 line 28 is 665.00, the 1% enhanced deduction.
        ("665.00", "665.00"),
        # Salary 90,000, above the CPP ceiling: Schedule 8 line 28 is at its 1,074.00 maximum.
        ("1074.00", "1074.00"),
        # No enhanced contributions: nothing is deducted.
        ("0", "0"),
    ],
)
def test_line_23300_is_the_schedule_8_cpp_enhanced_contributions(
    take_home_service: TakeHomeService, schedule_8_line_28: str, expected: str
) -> None:
    assert line_23300(take_home_service, schedule_8_line_28) == D(expected)
