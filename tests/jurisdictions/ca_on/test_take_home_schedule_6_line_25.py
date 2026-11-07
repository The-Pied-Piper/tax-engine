"""Schedule 6 (5000-S6, 2025) line 25, the net income over the base amount, as the Ontario take-home
manifest parts wire it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, line 304): "Line 25: Line 23 minus
line 24 (if negative, enter "0")". Line 23 is a copy of line 15 ("Adjusted family net income from
line 15", no step), so line 25 reads line 15 directly. Line 24 is the base amount, 26,855.00 for a
filer with no eligible spouse or dependant. Line 25 is one core/subtract_not_below_zero of line 24
from line 15.

The test loads the same parts as test_take_home_schedule_6_line_15.py, which compose line 15 from
the real salary, Schedule 8 and T1 taxable-income parts, then the line 24 and line 25 parts. The
manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import (
    CWB_NET_INCOME_OVER_BASE_AMOUNT,
)
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so the T1 net income is read from the salary; then the line 7
# part, the line 10 part, the optional line 11 input, the line 12 part, the line 13 part that line
# 15 subtracts from, the optional line 14 input and the line 15 part; then the line 24 part and the
# line 25 part under test.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "schedule_6_line_7.yaml",
    "schedule_6_line_10.yaml",
    "schedule_6_line_11_inputs.yaml",
    "schedule_6_line_12.yaml",
    "schedule_6_line_13.yaml",
    "schedule_6_line_14_inputs.yaml",
    "schedule_6_line_15.yaml",
    "schedule_6_line_24.yaml",
    "schedule_6_line_25.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_6
      required: true
      exports:
        - ca/cwb_net_income_over_base_amount
    """)


def line_25(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_NET_INCOME_OVER_BASE_AMOUNT).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 25 is line 15 (the salary less the T1 deductions, with line 14 blank) less line 24
        # ($26,855.00), floored at zero. At $20,000 line 15 is 19,835.00, below the base amount, so
        # line 25 prints "0.00".
        ("2000", "0.00"),
        ("6000", "0.00"),
        ("20000", "0.00"),
        ("30000", "2880.00"),
        ("35000", "7830.00"),
        ("40000", "12780.00"),
        ("70000", "42480.00"),
    ],
)
def test_schedule_6_line_25_is_line_15_less_the_base_amount_not_below_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_25(take_home_service, salary) == D(expected)
