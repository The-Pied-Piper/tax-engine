"""Schedule 6 (5000-S6, 2025) line 1, employment income and other employment income (column 1
"You"), as the Ontario take-home manifest part wires it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, lines 130-133): "Line 1: Employment
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
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
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
    worksheets = take_home_service(HEADER, FORM, LINE_10400_PART, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *artifacts
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_EMPLOYMENT_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Employment income (line 10100) at salaries of $2,000, $6,000, $20,000, $30,000, $35,000,
        # $40,000 and $70,000. No other employment income is given, so line 10400 reads as 0 and
        # each line 1 is the salary alone.
        ("2000", "2000.00"),
        ("6000", "6000.00"),
        ("20000", "20000.00"),
        ("30000", "30000.00"),
        ("35000", "35000.00"),
        ("40000", "40000.00"),
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
        ("2000", "1500.25", "3500.25"),
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
