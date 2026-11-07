"""T1 General (5006-R, 2025) lines 10100 to 26000 from the salary alone, one module for the form.

This module grows one line at a time. Line 22215 is the first: its step is Schedule 8's own export,
so the form builds nothing for it and this test reads that export from the real Schedule 8 parts
composed from the salary. The real header is not used because its output, T1 line 167, is not built
yet. This is not a worked return: no return file, no slips, one form.

Form text: T1 (CRA 5006-R, 2025) "Line 48 and line 22215: Deduction for CPP or QPP enhanced
contributions on employment income (complete Schedule 8 or Form RC381, whichever applies)
(maximum $1,074.00)"; Schedule 8 (CRA 5000-S8, 2025) Part 3a line 28 "Enter this amount (in dollars
and cents) on line 22215 of your return."
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import (
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
)
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
# The real Schedule 8 declaration (`schedule_8.yaml`) carries the form and its two exports to the
# return, so the fixture's own form text is an empty mapping.
FORM = "{}\n"
PARTS = ("salary.yaml", *(part.name for part in sorted(TAKE_HOME.glob("schedule_8*.yaml"))))


def line_22215(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("70000", "665.00"),
        ("90000", "1074.00"),
        ("81200", "1074.00"),
        ("3500", "0.00"),
    ],
)
def test_line_22215_is_the_schedule_8_enhanced_contributions(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_22215(take_home_service, salary) == D(expected)
