"""T1 General (5006-R, 2025) lines 10100 to 26000 from the salary alone, one module for the form.

The module pins each line alone and then the whole chain (10100 to 26000) from the salary.
Line 22215 is the first: its step is Schedule 8's own export, so the form builds nothing for it and this test reads that export from the real Schedule 8 parts
composed from the salary. Line 15000 builds its own step in the form's parts
(`t1_taxable_income*.yaml`), so its test composes those with the salary and the real parts, line
10400's optional input among them. The real header is not used because
its output, T1 line 167, is not built yet. This is not a worked return: no return file, no slips,
one form.

Form text: T1 (CRA 5006-R, 2025) "Line 33 and line 15000: Line 28 plus line 32 Total income";
"Line 48 and line 22215: Deduction for CPP or QPP enhanced contributions on employment income
(complete Schedule 8 or Form RC381, whichever applies) (maximum $1,074.00)"; Schedule 8 (CRA
5000-S8, 2025) Part 3a line 28 "Enter this amount (in dollars and cents) on line 22215 of your
return."; "Line 53 and line 23300: Add lines 35 to 52." Line 23300 reads Schedule 8's export as
the kind `ca/schedule_8.<export>`, so its test composes the real Schedule 8 with the T1 parts.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.deductions import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    SOCIAL_BENEFITS_REPAYMENT,
)
from tax_engine.jurisdictions.ca.catalog.income import (
    EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME,
    TOTAL_INCOME,
)
from tax_engine.jurisdictions.ca.catalog.taxable_income import (
    DEDUCTIONS_FROM_NET_INCOME,
    TAXABLE_INCOME,
)
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
HEADER_15000 = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The form's lines compose together: every T1 part beside the salary and the real Schedule 8 whose
# export line 23300 reads.
PARTS_15000 = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t1_taxable_income*.yaml"))),
)
PARTS = ("salary.yaml", *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))))


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


def line_15000(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER_15000, FORM, *PARTS_15000).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet.get(TOTAL_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("70000", "70000.00"), ("90000", "90000.00"), ("1000", "1000.00")],
)
def test_line_15000_is_the_salary_when_line_10400_is_left_out(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_15000(take_home_service, salary) == D(expected)


def line_23300(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER_15000, FORM, *PARTS_15000).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value


@pytest.mark.parametrize(("salary", "expected"), [("70000", "665.00"), ("90000", "1074.00")])
def test_line_23300_is_the_schedule_8_enhanced_contributions_read_as_line_22215(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_23300(take_home_service, salary) == D(expected)


def line_23400(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER_15000, FORM, *PARTS_15000).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value


@pytest.mark.parametrize(("salary", "expected"), [("70000", "69335.00"), ("90000", "88926.00")])
def test_line_23400_is_total_income_less_the_deductions_from_it(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_23400(take_home_service, salary) == D(expected)


def salary_only(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The `ca/t1_taxable_income` worksheet computed from the salary alone, every part composed."""
    worksheets = take_home_service(HEADER_15000, FORM, *PARTS_15000).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "line_22215", "net_income"),
    [
        ("70000", "665.00", "69335.00"),
        ("90000", "1074.00", "88926.00"),
        ("81200", "1074.00", "80126.00"),
        ("3500", "0.00", "3500.00"),
        ("2010", "0.00", "2010.00"),
    ],
)
def test_every_line_from_10100_to_26000_chains_from_the_salary_alone(
    take_home_service: TakeHomeService, salary: str, line_22215: str, net_income: str
) -> None:
    sheet = salary_only(take_home_service, salary)

    assert sheet.get(EMPLOYMENT_INCOME).value == D(salary)  # line 10100
    assert sheet.get(OTHER_EMPLOYMENT_INCOME).value == D("0")  # line 10400, left out
    assert sheet.get(TOTAL_INCOME).value == D(salary)  # line 15000
    assert sheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D(line_22215)  # line 23300
    assert sheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D(net_income)  # line 23400
    assert sheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0")  # line 23500, left out
    assert sheet.get(NET_INCOME).value == D(net_income)  # line 23600
    assert sheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")  # line 25700, left out
    assert sheet.get(TAXABLE_INCOME).value == D(net_income)  # line 26000


def test_the_exports_the_return_reads_at_70000(take_home_service: TakeHomeService) -> None:
    # Net income (23600) and taxable income (26000) are 69,335.00; the others the form exports are
    # total income (15000) and the deductions from it (23300).
    sheet = salary_only(take_home_service, "70000")

    assert sheet.get(TOTAL_INCOME).value == D("70000")
    assert sheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("665.00")
    assert sheet.get(NET_INCOME).value == D("69335.00")
    assert sheet.get(TAXABLE_INCOME).value == D("69335.00")


def test_line_23400_is_signed_and_lines_23600_and_26000_are_floored_at_zero(
    take_home_service: TakeHomeService,
) -> None:
    # A salary alone never makes line 23400 negative (the deduction is 0.00 at a zero salary), so
    # the sign rule is pinned on the kinds' declarations plus the zero-salary edge.
    assert not NET_INCOME_BEFORE_ADJUSTMENTS.non_negative
    assert NET_INCOME.non_negative
    assert TAXABLE_INCOME.non_negative
    sheet = salary_only(take_home_service, "0")
    assert sheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("0")
    assert sheet.get(TAXABLE_INCOME).value == D("0")


def test_a_negative_salary_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        salary_only(take_home_service, "-1")
