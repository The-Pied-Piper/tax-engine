"""T1 (2025) line 23300, total deductions from total income, from the real part files.

T1 line 23300: "Line 53 and line 23300: Add lines 35 to 52." (5006-R, page 4). The take-home filer
can have three of its lines, added in form line order: line 40 (line 21300, the UCCB repayment),
line 48 (line 22215, the CPP enhanced contributions deduction that Schedule 8 line 28 exports, its
own part `ca/t1_line_22215`) and line 52 (line 23200, the RDSP income repayment). The two
repayments are the form's own steps, each read as 0 when the caller gives none. The output is
`ca/deductions_from_total_income`.

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
from tax_engine.jurisdictions.ca.catalog.income import (
    EMPLOYMENT_INCOME,
    RDSP_INCOME_REPAYMENT,
    UCCB_REPAYMENT,
)
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
PARTS = (
    *form_part_names("schedule_8"),
    *form_part_names("t1_employment_income"),
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_22215.yaml",
    "t1_taxable_income_line_23300.yaml",
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
    - ca/deductions_from_total_income
capabilities: []
"""


def line_23300(
    take_home_service: TakeHomeService,
    salary: str,
    uccb_repayment: str | None = None,
    rdsp_repayment: str | None = None,
) -> Decimal:
    given = [
        Artifact(kind, D(amount))
        for kind, amount in (
            (UCCB_REPAYMENT, uccb_repayment),
            (RDSP_INCOME_REPAYMENT, rdsp_repayment),
        )
        if amount is not None
    ]
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)), *given
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
        # The $3,500 salary, under the basic exemption: no contribution, so 0.00.
        ("3500", "0.00"),
    ],
)
def test_line_23300_is_the_schedule_8_deduction(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_23300(take_home_service, salary) == D(expected)


def test_line_23300_adds_the_uccb_and_rdsp_repayments_to_the_schedule_8_deduction(
    take_home_service: TakeHomeService,
) -> None:
    # 40.10 (line 40, line 21300) + 665.00 (line 48, line 22215) + 9.90 (line 52, line 23200).
    assert line_23300(take_home_service, "70000", "40.10", "9.90") == D("715.00")


def test_line_23300_reads_a_blank_rdsp_repayment_as_zero(
    take_home_service: TakeHomeService,
) -> None:
    assert line_23300(take_home_service, "70000", uccb_repayment="40.10") == D("705.10")


def test_line_23300_reads_a_blank_uccb_repayment_as_zero(
    take_home_service: TakeHomeService,
) -> None:
    assert line_23300(take_home_service, "70000", rdsp_repayment="9.90") == D("674.90")
