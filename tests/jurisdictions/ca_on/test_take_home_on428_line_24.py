"""ON428 (2025) line 24, the CPP and EI credit amounts, from the salary alone, real parts.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 24: Add lines 19 to 23." Line 19 (58240) is
Schedule 8 line 25, the CPP base contributions on the return, and line 21 (58300) is T2204 line
16, the EI premiums credit amount; lines 20, 22 and 23 (self-employed CPP and EI, adoption) are
left out. Another form's export arrives only as a record list of one amount, which core/sum cannot
read, so each of lines 19 and 21 is a core/record_total over that export and line 24 sums the two.

The test composes the real salary part, the real Schedule 8 and T2204 parts and the three real
ON428 line parts (`on428_line_19.yaml`, `on428_line_21.yaml`, `on428_line_24.yaml`), and types in
only the salary. The ON428 form declaration is made up here, exporting the three lines read,
because the real header is owned by another change.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import (
    ON428_CPP_BASE_CREDIT_AMOUNT_LINE_19,
    ON428_CPP_EI_CREDIT_AMOUNTS_LINE_24,
    ON428_EI_CREDIT_AMOUNT_LINE_21,
)
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))),
    "on428_line_19.yaml",
    "on428_line_21.yaml",
    "on428_line_24.yaml",
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
      name: ca-on/on428
      required: true
      exports:
        - ca-on/on428_cpp_base_credit_amount_line_19
        - ca-on/on428_ei_credit_amount_line_21
        - ca-on/on428_cpp_ei_credit_amounts_line_24
    capabilities: []
    """)

# salary, line 19, line 21, line 24. At $150,000 both lines are at their maximums.
CASES = [
    ("20000", "816.75", "328.00", "1144.75"),
    ("70000", "3291.75", "1077.48", "4369.23"),
    ("150000", "3356.10", "1077.48", "4433.58"),
]


def _line(take_home_service: TakeHomeService, salary: str, kind: AmountKind) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-on/on428"]
    return sheet.get(kind).value


@pytest.mark.parametrize(("salary", "expected"), [(c[0], c[1]) for c in CASES])
def test_line_19_is_the_schedule_8_cpp_base_contributions(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert _line(take_home_service, salary, ON428_CPP_BASE_CREDIT_AMOUNT_LINE_19) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), [(c[0], c[2]) for c in CASES])
def test_line_21_is_the_t2204_line_16_ei_premiums(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert _line(take_home_service, salary, ON428_EI_CREDIT_AMOUNT_LINE_21) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), [(c[0], c[3]) for c in CASES])
def test_line_24_adds_lines_19_and_21(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert _line(take_home_service, salary, ON428_CPP_EI_CREDIT_AMOUNTS_LINE_24) == D(expected)
