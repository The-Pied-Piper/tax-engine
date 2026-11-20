"""Schedule 6 (5000-S6, 2025) line 1, employment income and other employment income (column 1
"You"), as the Ontario take-home manifest part wires it.

Form text (5000-S6 2025): "Line 1: Employment
income and other employment income from line 10100 and line 10400 of the return", then "Column 1
You". Line 1 is a calculation: the sum of T1 line 10100 (`ca/employment_income`) and T1 line 10400
(`ca/other_employment_income`). Line 10400 is optional and reads as 0 when the caller gives none
(the default is in `t1_taxable_income_line_10400_inputs.yaml`). Line 1 is therefore one core/sum
over both parts, employment income first.

The manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, OTHER_EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
# The real T1 taxable-income parts (with the Schedule 8 parts its line 23300 reads), composed beside
# the form under test, which imports T1 lines 10100 and 10400 from the T1.
T1_PARTS = (
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_10100.yaml",
    "t1_taxable_income_line_10400.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
)
PART = "schedule_6_line_1.yaml"
# The T1 line 10400 inputs part, which declares `ca/other_employment_income` as optional with a
# default of 0. Line 1 reads it, so the part is composed beside line 1.
LINE_10400_PART = "t1_taxable_income_line_10400_inputs.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_6
      required: true
      exports:
        - ca/cwb_employment_income
    """)


def line_1(take_home_service: TakeHomeService, salary: str, other: str | None = None) -> Decimal:
    """Line 1 from the salary, and from the other employment income when one is given."""
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if other is not None:
        artifacts.append(Artifact(OTHER_EMPLOYMENT_INCOME, D(other)))
    worksheets = take_home_service(HEADER, FORM, *T1_PARTS, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *artifacts
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_EMPLOYMENT_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Employment income (line 10100) at salaries of $2,000 and $70,000. No other employment
        # income is given, so line 10400 reads as 0 and each line 1 is the salary alone.
        ("2000", "2000.00"),
        ("70000", "70000.00"),
    ],
)
def test_schedule_6_line_1_is_employment_income_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_1(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


def test_an_omitted_other_employment_income_is_read_as_zero(
    take_home_service: TakeHomeService,
) -> None:
    # The caller gives the salary only. Line 10400 is left out, so the optional input reads as its
    # default of 0 and line 1 is the salary.
    assert line_1(take_home_service, "70000") == D("70000.00")


@pytest.mark.parametrize(
    ("salary", "other", "expected"),
    [
        # Line 1 adds line 10400 to line 10100 to the cent.
        ("70000", "5000.50", "75000.50"),
        # Other employment income alone: no salary, so line 1 is the other income.
        ("0", "5000", "5000.00"),
    ],
)
def test_schedule_6_line_1_adds_other_employment_income_to_employment_income(
    take_home_service: TakeHomeService, salary: str, other: str, expected: str
) -> None:
    value = line_1(take_home_service, salary, other)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2
