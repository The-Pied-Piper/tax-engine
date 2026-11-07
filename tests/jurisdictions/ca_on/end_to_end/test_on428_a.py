"""Schedule ON428-A (2025, Ontario LIFT credit, Part A, single filer) from the salary alone: the
form's real parts composed end to end.

Every ON428-A line part has its own test with its neighbours typed in. This module composes the
whole form: it copies `salary.yaml`, every Schedule 8 part (line 22215 comes from there), every
`t1_taxable_income*.yaml` part (the form reads T1 lines 10100 and 23600) and every `on428_a*.yaml`
part into a temporary manifest folder beside a test-only header, and types in only the gross salary
(`ca/employment_income`). The real header is not used because its output, T1 line 167, is not built
yet. This is not a worked return: no return file, no slips, one form.

Line 1 is the salary itself, the input, so the form builds no step for it. Line 2 (T1 line 10400,
other employment income) is read as 0 when not given, is never typed in here and has no pin of its
own: line 3 equal to the salary is its only evidence. Lines 14 and 15 are copies of lines 5 and 13
and have no step. Lines 7 to 12 and Part B are not built.

Form text: Schedule ON428-A (CRA 5006-A, 2025), "Line 3: Line 1 plus line 2"; "Line 4: Applicable
rate 5.05%"; "Line 6: Net income from line 23600 of your return"; "Line 5: Line 3 multiplied by
the percentage from line 4 (maximum $875)"; "Line 13: Line 9 minus line 12 (if negative, enter
"0") Your adjusted net income"; "Line 16: Individual income threshold 32,500.00"; "Line 17: Line
15 minus line 16 (if negative, enter "0")"; "Line 19: Line 17 multiplied by the percentage from
line 18"; "Line 20: Line 14 minus line 19 (if negative, enter "0") Enter this amount on line
62140 of your Form ON428." Net income at line 23600 is the salary less the Schedule 8 (CRA
5000-S8, 2025) "Line 28: Line 26 plus line 27", which the form sends to line 22215 of the
return. Eligibility for the credit is not printed on the form and is assumed true.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import (
    LIFT_ADJUSTED_NET_INCOME,
    LIFT_CREDIT_BEFORE_MAXIMUM,
    LIFT_CREDIT_SINGLE,
    LIFT_EMPLOYMENT_INCOME,
    LIFT_INDIVIDUAL_INCOME_THRESHOLD,
    LIFT_MAXIMUM_CREDIT,
    LIFT_NET_INCOME,
    LIFT_REDUCTION,
    LIFT_SINGLE_EXCESS_OVER_THRESHOLD,
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
# The real ON428-A declaration (`on428_a.yaml`) carries the form and its exports, so the fixture's
# own form text is an empty mapping.
FORM = "{}\n"
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t1_taxable_income*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("on428_a*.yaml"))),
)

# Amount lines by form line. Line 4's printed rate (5.05%) is a dataset figure with no figure of its
# own, so the "4" entry is not a printed line: it is line 5's first operation, line 3 times that
# rate before the $875 maximum, the one direct pin of the rate. Line 18's 5% is pinned only through
# line 19.
AMOUNT_LINES: dict[str, AmountKind] = {
    "3": LIFT_EMPLOYMENT_INCOME,
    "4": LIFT_CREDIT_BEFORE_MAXIMUM,
    "5": LIFT_MAXIMUM_CREDIT,
    "6": LIFT_NET_INCOME,
    "13": LIFT_ADJUSTED_NET_INCOME,
    "16": LIFT_INDIVIDUAL_INCOME_THRESHOLD,
    "17": LIFT_SINGLE_EXCESS_OVER_THRESHOLD,
    "19": LIFT_REDUCTION,
    "20": LIFT_CREDIT_SINGLE,
}
CENT_LINES = ("5", "17", "19", "20")

# Each salary's figures by form line, hand-computed from the printed lines. Line 6 is the salary
# less the Schedule 8 enhanced contributions (T1 line 22215, Schedule 8 line 28); line 19 is line
# 18's 5% of line 17.
CASES: list[tuple[str, dict[str, str]]] = [
    ("70000", {"3": "70000", "4": "3535.00", "5": "875.00", "6": "69335.00", "13": "69335.00",
               "16": "32500", "17": "36835.00", "19": "1841.75", "20": "0.00"}),
    ("40000", {"3": "40000", "4": "2020.00", "5": "875.00", "6": "39635.00", "13": "39635.00",
               "16": "32500", "17": "7135.00", "19": "356.75", "20": "518.25"}),
    ("30000", {"3": "30000", "4": "1515.00", "5": "875.00", "6": "29735.00", "13": "29735.00",
               "16": "32500", "17": "0.00", "19": "0.00", "20": "875.00"}),
    ("10000", {"3": "10000", "4": "505.00", "5": "505.00", "6": "9935.00", "13": "9935.00",
               "16": "32500", "17": "0.00", "19": "0.00", "20": "505.00"}),
    ("90000", {"3": "90000", "4": "4545.00", "5": "875.00", "6": "88926.00", "13": "88926.00",
               "16": "32500", "17": "56426.00", "19": "2821.30", "20": "0.00"}),
]  # fmt: skip


def on428_a(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-on/on428_a"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_every_line_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: dict[str, str]
) -> None:
    sheet = on428_a(take_home_service, salary)

    assert {line: sheet.get(AMOUNT_LINES[line]).value for line in expected} == {
        line: D(figure) for line, figure in expected.items()
    }


def test_the_form_exports_line_20_the_figure_on428_line_85_reads(
    take_home_service: TakeHomeService,
) -> None:
    sheet = on428_a(take_home_service, "40000")

    assert sheet.get(LIFT_CREDIT_SINGLE).value == D("518.25")


def test_the_form_exports_exactly_line_20(take_home_service: TakeHomeService) -> None:
    # Lines 3, 17 and 19 are read only inside the form, so the form exports line 20 alone.
    service = take_home_service(HEADER, FORM, *PARTS)
    code = JurisdictionCode("CA-ON")
    (form,) = (f for f in service.compose(code, 2025).forms if f.name == "ca-on/on428_a")
    assert form.exports == (LIFT_CREDIT_SINGLE,)

    worksheets = service.compute(code, 2025, Artifact(EMPLOYMENT_INCOME, D("40000")))
    (sheet,) = worksheets["ca-on/on428_a"]

    assert [sheet.get(kind).value for kind in form.exports] == [D("518.25")]


@pytest.mark.parametrize("salary", [case[0] for case in CASES])
def test_the_cent_lines_have_exactly_two_decimals(
    take_home_service: TakeHomeService, salary: str
) -> None:
    # A floored line (lines 17, 19 and 20 under the threshold or past the credit) rounds through its
    # own dataset, so it prints 0.00 and every cent line is pinned to two decimals, zero included.
    sheet = on428_a(take_home_service, salary)

    for line in CENT_LINES:
        value = sheet.get(AMOUNT_LINES[line]).value
        assert value.as_tuple().exponent == -2, line


def test_a_negative_salary_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        on428_a(take_home_service, "-1")
