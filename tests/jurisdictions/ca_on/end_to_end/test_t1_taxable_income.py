"""T1 General (5006-R, 2025) lines 10100 to 26000 from the salary alone, one module for the form.

The module pins each line alone and then the whole chain (10100 to 26000) from the salary.
Line 22215 is the first: its step is Schedule 8's own export, so the form builds nothing for it
and this test reads that export from the real Schedule 8 parts
composed from the salary. Line 15000 builds its own step in the form's parts
(`t1_taxable_income*.yaml`), so its test composes those with the salary and the real parts, line
10400's optional input among them. The real header is not used because
its output, T1 line 167, is not built yet. This is not a worked return: no return file, no slips,
one form. The expected figures hold when the contributions deducted (T4 boxes 16 and 16A) are at
least the required amounts, so Schedule 8 line 24 is positive or "0"; the engine computes the
required contributions and reads no box 16.

Form text: T1 (CRA 5006-R, 2025) "Line 33 and line 15000: Line 28 plus line 32 Total income";
"Line 48 and line 22215: Deduction for CPP or QPP enhanced contributions on employment income
(complete Schedule 8 or Form RC381, whichever applies) (maximum $1,074.00)"; Schedule 8 (CRA
5000-S8, 2025) Part 3a line 28 "Enter this amount (in dollars and cents) on line 22215 of your
return."; "Line 53 and line 23300: Add lines 35 to 52."; "Line 54 and line 23400: Line 34 minus
line 53 (if negative, show in brackets)"; "Line 56 and line 23600: Line 54 minus line 55 (if
negative, enter "0")"; "Line 69 and line 26000: Line 57 minus line 68 (if negative, enter "0")".
Line 23300 reads Schedule 8's export as the kind `ca/schedule_8.<export>`, so its test composes the
real Schedule 8 with the T1 parts.
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


def compute(take_home_service: TakeHomeService, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    """Every worksheet of the composed parts, computed from the salary alone."""
    return take_home_service(HEADER, FORM, *PARTS_15000).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


def salary_only(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The `ca/t1_taxable_income` worksheet computed from the salary alone, every part composed."""
    (sheet,) = compute(take_home_service, salary)["ca/t1_taxable_income"]
    return sheet


def line_15000(take_home_service: TakeHomeService, salary: str) -> Decimal:
    return salary_only(take_home_service, salary).get(TOTAL_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("70000", "70000.00"), ("90000", "90000.00"), ("1000", "1000.00")],
)
def test_line_15000_is_the_salary_when_line_10400_is_left_out(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_15000(take_home_service, salary) == D(expected)


def line_23300(take_home_service: TakeHomeService, salary: str) -> Decimal:
    return salary_only(take_home_service, salary).get(DEDUCTIONS_FROM_TOTAL_INCOME).value


@pytest.mark.parametrize(("salary", "expected"), [("70000", "665.00"), ("90000", "1074.00")])
def test_line_23300_is_the_schedule_8_enhanced_contributions_read_as_line_22215(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_23300(take_home_service, salary) == D(expected)


def line_23400(take_home_service: TakeHomeService, salary: str) -> Decimal:
    return salary_only(take_home_service, salary).get(NET_INCOME_BEFORE_ADJUSTMENTS).value


@pytest.mark.parametrize(("salary", "expected"), [("70000", "69335.00"), ("90000", "88926.00")])
def test_line_23400_is_total_income_less_the_deductions_from_it(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_23400(take_home_service, salary) == D(expected)


AMOUNT_LINES = {
    "10100": EMPLOYMENT_INCOME,
    "10400": OTHER_EMPLOYMENT_INCOME,
    "15000": TOTAL_INCOME,
    "23300": DEDUCTIONS_FROM_TOTAL_INCOME,
    "23400": NET_INCOME_BEFORE_ADJUSTMENTS,
    "23500": SOCIAL_BENEFITS_REPAYMENT,
    "23600": NET_INCOME,
    "25700": DEDUCTIONS_FROM_NET_INCOME,
    "26000": TAXABLE_INCOME,
}
CENT_LINES = ("23300", "23400", "23600", "26000")


def amounts(sheet: Worksheet, expected: dict[str, str]) -> dict[str, Decimal]:
    return {line: sheet.get(AMOUNT_LINES[line]).value for line in expected}


def salary_figures(salary: str, line_22215: str, net_income: str) -> dict[str, str]:
    """A salary-only filer's printed figures; line 22215 (Schedule 8) is read as line 23300."""
    return {
        "10100": salary,
        "10400": "0",
        "15000": salary,
        "23300": line_22215,
        "23400": net_income,
        "23500": "0",
        "23600": net_income,
        "25700": "0",
        "26000": net_income,
    }


SALARY_70K_AMOUNTS = salary_figures("70000", "665.00", "69335.00")
SALARY_90K_AMOUNTS = salary_figures("90000", "1074.00", "88926.00")
SALARY_81200_AMOUNTS = salary_figures("81200", "1074.00", "80126.00")
SALARY_3500_AMOUNTS = salary_figures("3500", "0.00", "3500.00")
SALARY_2010_AMOUNTS = salary_figures("2010", "0.00", "2010.00")


@pytest.mark.parametrize(
    ("salary", "expected_amounts"),
    [
        ("70000", SALARY_70K_AMOUNTS),
        ("90000", SALARY_90K_AMOUNTS),
        ("81200", SALARY_81200_AMOUNTS),
        ("3500", SALARY_3500_AMOUNTS),
        ("2010", SALARY_2010_AMOUNTS),
    ],
)
def test_every_line_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected_amounts: dict[str, str]
) -> None:
    worksheets = compute(take_home_service, salary)
    (sheet,) = worksheets["ca/t1_taxable_income"]
    (schedule_8,) = worksheets["ca/schedule_8"]

    assert amounts(sheet, expected_amounts) == {
        line: D(value) for line, value in expected_amounts.items()
    }
    # Line 22215 is Schedule 8's own export (line 28), the figure line 23300 reads.
    assert schedule_8.get(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D(
        expected_amounts["23300"]
    )


def test_the_form_exports_the_return_lines_and_the_worksheet_holds_them_at_70000(
    take_home_service: TakeHomeService,
) -> None:
    # The exports the form declares: total income (15000), the deductions from it (23300), net
    # income (23600) and taxable income (26000).
    service = take_home_service(HEADER, FORM, *PARTS_15000)
    code = JurisdictionCode("CA-ON")
    (form,) = (f for f in service.compose(code, 2025).forms if f.name == "ca/t1_taxable_income")
    assert form.exports == (
        TOTAL_INCOME,
        DEDUCTIONS_FROM_TOTAL_INCOME,
        NET_INCOME,
        TAXABLE_INCOME,
    )

    worksheets = service.compute(code, 2025, Artifact(EMPLOYMENT_INCOME, D("70000")))
    (sheet,) = worksheets["ca/t1_taxable_income"]

    assert [sheet.get(kind).value for kind in form.exports] == [
        D("70000"),
        D("665.00"),
        D("69335.00"),
        D("69335.00"),
    ]


def test_the_kinds_declare_23400_signed_and_23600_and_26000_non_negative(
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


@pytest.mark.parametrize("salary", ["70000", "30000", "12345.67"])
def test_the_cent_lines_have_exactly_two_decimals(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = salary_only(take_home_service, salary)

    for line in CENT_LINES:
        assert sheet.get(AMOUNT_LINES[line]).value.as_tuple().exponent == -2, line
