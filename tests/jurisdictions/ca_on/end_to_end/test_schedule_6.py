"""Schedule 6 (2025, Canada workers benefit, basic CWB, single filer) from the salary alone: the
form's real parts composed end to end.

Every Schedule 6 line part has its own test with its neighbours typed in. This module composes the
whole form: it copies `salary.yaml`, every Schedule 8 part (line 22215 comes from there), every
`t1_taxable_income*.yaml` part (the form reads T1 lines 10100 and 23600) and every
`schedule_6*.yaml` part into a temporary manifest folder beside a test-only header, and types in
only the gross salary (`ca/employment_income`). The real header is not used because its output, T1
line 167, is not built yet. This is not a worked return: no return file, no slips, one form.

Lines 11 and 14 are optional inputs that default to 0 and are never typed in here. Lines 16 and 23
are copies of the working income and adjusted family net income and have no step, so they get no
check; lines 18 and 25 read the figures those lines copy. Lines 2 to 4, 8, 9 and the disability and
election parts are not built.

Form text: Schedule 6 (CRA 5000-S6, 2025, docs/cra-forms-2025/5000-s6-25e.txt), "Line 5: Add lines
1 to 4"; "Line 7: Net income from line 23600 of the return"; "Line 17: Base amount 3,000.00"; "Line
18: Line 16 minus line 17 (if negative, enter "0")"; "Line 19: Rate 27%"; "Line 20: Line 18
multiplied by the percentage from line 19"; "Line 21: ... If not, enter $1,633"; "Line 22: Enter
whichever is less: amount from line 20 or line 21"; "Line 24: ... If not, enter $26,855"; "Line 25:
Line 23 minus line 24 (if negative, enter "0")"; "Line 26: Rate 15%"; "Line 27: Line 25 multiplied
by the percentage from line 26"; "Line 28: Line 22 minus line 27 (if negative, enter "0") ... enter
this amount on line 45300 of your return". Net income at line 23600 is the salary less the Schedule
8 (CRA 5000-S8, 2025) "Line 28: Line 26 plus line 27", which the form sends to line 22215 of the
return. Eligibility (resident all year, 19 or over, not a full-time student, not in prison, not a
diplomat) is not printed as lines and is assumed true.
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
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import (
    ADJUSTED_FAMILY_NET_INCOME,
    CWB_BASE_AMOUNT,
    CWB_BASIC_BENEFIT_LINE_22,
    CWB_BENEFIT_LINE_28,
    CWB_EMPLOYMENT_INCOME,
    CWB_FAMILY_NET_INCOME_LINE_10,
    CWB_FAMILY_NET_INCOME_LINE_12,
    CWB_FAMILY_NET_INCOME_LINE_13,
    CWB_FAMILY_WORKING_INCOME,
    CWB_MAXIMUM,
    CWB_NET_INCOME_LINE_7,
    CWB_NET_INCOME_OVER_BASE_AMOUNT,
    CWB_REDUCTION_LINE_27,
    CWB_REDUCTION_THRESHOLD,
    CWB_WORKING_INCOME_OVER_BASE_AMOUNT,
    CWB_WORKING_INCOME_RATE_LINE_20,
    WORKING_INCOME,
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
# The real Schedule 6 declaration (`schedule_6.yaml`) carries the form and its export, so the
# fixture's own form text is an empty mapping.
FORM = "{}\n"
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t1_taxable_income*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_6*.yaml"))),
)

# Amount lines by form line. The printed rates (27% on line 19, 15% on line 26) are dataset figures
# with no figure of their own: they are pinned through lines 20 and 27.
AMOUNT_LINES: dict[str, AmountKind] = {
    "1": CWB_EMPLOYMENT_INCOME,
    "5": WORKING_INCOME,
    "6": CWB_FAMILY_WORKING_INCOME,
    "7": CWB_NET_INCOME_LINE_7,
    "10": CWB_FAMILY_NET_INCOME_LINE_10,
    "12": CWB_FAMILY_NET_INCOME_LINE_12,
    "13": CWB_FAMILY_NET_INCOME_LINE_13,
    "15": ADJUSTED_FAMILY_NET_INCOME,
    "17": CWB_BASE_AMOUNT,
    "18": CWB_WORKING_INCOME_OVER_BASE_AMOUNT,
    "20": CWB_WORKING_INCOME_RATE_LINE_20,
    "21": CWB_MAXIMUM,
    "22": CWB_BASIC_BENEFIT_LINE_22,
    "24": CWB_REDUCTION_THRESHOLD,
    "25": CWB_NET_INCOME_OVER_BASE_AMOUNT,
    "27": CWB_REDUCTION_LINE_27,
    "28": CWB_BENEFIT_LINE_28,
}
CENT_LINES = ("20", "22", "27", "28")


def figures(salary: str, net_income: str, over_base: str, line_20: str, line_22: str,
            over_threshold: str, line_27: str, line_28: str) -> dict[str, str]:  # fmt: skip
    """The whole worksheet for one salary: lines 1, 5, 6 are the salary; 7, 10, 12, 13, 15 the net
    income; 17, 21, 24 the printed single amounts."""
    return {
        "1": salary, "5": salary, "6": salary,
        "7": net_income, "10": net_income, "12": net_income, "13": net_income, "15": net_income,
        "17": "3000.00", "18": over_base, "20": line_20, "21": "1633.00", "22": line_22,
        "24": "26855.00", "25": over_threshold, "27": line_27, "28": line_28,
    }  # fmt: skip


# Each salary's figures, hand-computed from the printed lines. Net income is the salary less the
# Schedule 8 enhanced contributions (T1 line 22215); the benefit is line 22 less line 27.
CASES: list[tuple[str, dict[str, str]]] = [
    ("70000", figures("70000", "69335.00", "67000", "18090.00", "1633.00",
                      "42480.00", "6372.00", "0.00")),
    ("30000", figures("30000", "29735.00", "27000", "7290.00", "1633.00",
                      "2880.00", "432.00", "1201.00")),
    ("20000", figures("20000", "19835.00", "17000", "4590.00", "1633.00",
                      "0.00", "0.00", "1633.00")),
    ("2010", figures("2010", "2010.00", "0", "0.00", "0.00",
                     "0.00", "0.00", "0.00")),
]  # fmt: skip


def schedule_6(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_every_line_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: dict[str, str]
) -> None:
    sheet = schedule_6(take_home_service, salary)

    assert {line: sheet.get(kind).value for line, kind in AMOUNT_LINES.items()} == {
        line: D(figure) for line, figure in expected.items()
    }


def test_the_form_exports_line_28_the_figure_t1_line_45300_reads(
    take_home_service: TakeHomeService,
) -> None:
    sheet = schedule_6(take_home_service, "30000")

    assert sheet.get(CWB_BENEFIT_LINE_28).value == D("1201.00")


def test_the_form_exports_exactly_line_28(take_home_service: TakeHomeService) -> None:
    # Every earlier line is read only inside the form, so the form exports line 28 alone.
    service = take_home_service(HEADER, FORM, *PARTS)
    code = JurisdictionCode("CA-ON")
    (form,) = (f for f in service.compose(code, 2025).forms if f.name == "ca/schedule_6")
    assert form.exports == (CWB_BENEFIT_LINE_28,)

    worksheets = service.compute(code, 2025, Artifact(EMPLOYMENT_INCOME, D("30000")))
    (sheet,) = worksheets["ca/schedule_6"]

    assert [sheet.get(kind).value for kind in form.exports] == [D("1201.00")]


def test_the_benefit_at_seventy_thousand_is_zero(take_home_service: TakeHomeService) -> None:
    # The phase-out of the form's own printed amounts ends near net income 37,742, so a $70,000
    # salary gets no benefit: line 27 (6,372.00) exceeds line 22 (1,633.00) and line 28 floors to 0.
    sheet = schedule_6(take_home_service, "70000")

    assert sheet.get(CWB_BASIC_BENEFIT_LINE_22).value == D("1633.00")
    assert sheet.get(CWB_REDUCTION_LINE_27).value == D("6372.00")
    assert sheet.get(CWB_BENEFIT_LINE_28).value == D("0.00")


@pytest.mark.parametrize("salary", [case[0] for case in CASES] + ["12345.67"])
def test_the_cent_lines_have_exactly_two_decimals(
    take_home_service: TakeHomeService, salary: str
) -> None:
    # A floored or capped line (22 at a low salary, 27 under the threshold, 28 past the phase-out)
    # rounds through its own dataset, so it prints 0.00 and every cent line is pinned to two
    # decimals, zero included.
    sheet = schedule_6(take_home_service, salary)

    for line in CENT_LINES:
        value = sheet.get(AMOUNT_LINES[line]).value
        assert value.as_tuple().exponent == -2, line


def test_a_negative_salary_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        schedule_6(take_home_service, "-1")
