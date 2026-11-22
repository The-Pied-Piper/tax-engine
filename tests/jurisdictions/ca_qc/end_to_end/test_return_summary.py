"""The Quebec take-home return (2025), end to end: the registered engine computes CA-QC from the
salary alone, at $20,000, $70,000 and $200,000.

The engine runs over the real Quebec 2025 manifest (`build_tax_computation`, Quebec listed in
`registrations.JURISDICTIONS`) with the gross salary (`ca/employment_income`) the only input and
every optional input left blank, except the three optional answers, which take their defaults (not
alone, neither tenant nor owner, not covered by a group drug plan). Two other scenarios give those
answers: "alone and a tenant" (Schedule B line 20, Schedule D lines 12 and 32 to 36) and "covered by
a group drug plan" (Schedule K line 50).

Each printed figure of the chain is one test, over the three salaries and the scenarios:
- the refund or balance owing (positive is owing, negative a refund): 5005-R line 172 plus
  TP-1 line 450 less line 456;
- the total payable: 5005-R line 43500 less line 44000 plus TP-1 line 450;
- 5005-R line 172, "Line 152 minus line 171 ... Refund or balance owing" (CRA 5005-R);
- TP-1 line 450, "Add lines 432 through 447. Income tax and contributions" (Revenu Quebec TP-1.D-V
  (2025-12));
- TP-1 line 456, "Tax credits respecting the work premium";
- the solidarity tax credit of July 2026 to June 2027, its own yearly amount;
- 5005-R line 45300, the Canada workers benefit.
The figures are hand-computed from the printed lines of the two returns, not a CRA or Revenu
Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from functools import cache

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import REFUND_OR_BALANCE_OWING
from tax_engine.jurisdictions.ca_qc.catalog import (
    CWB_LINE_161,
    FEDERAL_TOTAL_PAYABLE_RETURN,
    PPIP_PREMIUMS_LINE_91,
    REFUND_OR_BALANCE_OWING_LINE_172,
    REFUNDABLE_QUEBEC_ABATEMENT_RETURN,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    SOLIDARITY_CREDIT,
    SOLIDARITY_LIVED_ALONE_LINE_12,
    SOLIDARITY_TENANT_OR_OWNER_LINES_32_36,
    TOTAL_PAYABLE,
    TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450,
    TP1_LINE_457,
    TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456,
)

D = Decimal
QUEBEC = JurisdictionCode("CA-QC")
SALARIES = ("20000", "70000", "200000")
DEFAULT = "default"
GROUP_PLAN = "group plan"
ALONE_AND_TENANT = "alone and tenant"
SCENARIOS = (DEFAULT, GROUP_PLAN, ALONE_AND_TENANT)


@cache
def _sheets(salary: str, scenario: str) -> dict[str, Worksheet]:
    """The one sheet of each form the engine computes for a salary and a scenario."""
    answers = {
        DEFAULT: [],
        GROUP_PLAN: [Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, 1)],
        ALONE_AND_TENANT: [
            # Schedule B line 20 and Schedule D line 12 are the same fact entered on two forms.
            Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1),
            Artifact(SOLIDARITY_LIVED_ALONE_LINE_12, 1),
            Artifact(SOLIDARITY_TENANT_OR_OWNER_LINES_32_36, 1),
        ],
    }[scenario]
    worksheets = build_tax_computation().compute(
        QUEBEC, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)), *answers
    )
    return {form: sheets[0] for form, sheets in worksheets.items()}


def _cases(figures: dict[tuple[str, str], str]) -> list[tuple[str, str, str]]:
    return [(salary, scenario, value) for (salary, scenario), value in figures.items()]


REFUND_OR_BALANCE_OWING_FIGURES = {
    ("20000", DEFAULT): "-3135.08",
    ("70000", DEFAULT): "14678.32",
    ("200000", DEFAULT): "71643.79",
    ("20000", GROUP_PLAN): "-3135.08",
    ("70000", GROUP_PLAN): "13923.32",
    ("200000", GROUP_PLAN): "70888.79",
    ("20000", ALONE_AND_TENANT): "-3144.04",
    ("70000", ALONE_AND_TENANT): "14678.32",
    ("200000", ALONE_AND_TENANT): "71643.79",
}


@pytest.mark.parametrize(
    ("salary", "scenario", "expected"), _cases(REFUND_OR_BALANCE_OWING_FIGURES)
)
def test_the_refund_or_balance_owing(salary: str, scenario: str, expected: str) -> None:
    sheet = _sheets(salary, scenario)["ca-qc/return"]

    assert sheet.get(REFUND_OR_BALANCE_OWING).value == D(expected)


TOTAL_PAYABLE_FIGURES = {
    ("20000", DEFAULT): "128.01",
    ("70000", DEFAULT): "14678.32",
    ("200000", DEFAULT): "71643.79",
    ("20000", GROUP_PLAN): "128.01",
    ("70000", GROUP_PLAN): "13923.32",
    ("200000", GROUP_PLAN): "70888.79",
    ("20000", ALONE_AND_TENANT): "119.05",
    ("70000", ALONE_AND_TENANT): "14678.32",
    ("200000", ALONE_AND_TENANT): "71643.79",
}


@pytest.mark.parametrize(("salary", "scenario", "expected"), _cases(TOTAL_PAYABLE_FIGURES))
def test_the_total_payable(salary: str, scenario: str, expected: str) -> None:
    sheet = _sheets(salary, scenario)["ca-qc/return"]

    assert sheet.get(TOTAL_PAYABLE).value == D(expected)


LINE_172_FIGURES = {
    ("20000", DEFAULT): "-2560.02",
    ("70000", DEFAULT): "6282.16",
    ("200000", DEFAULT): "32886.26",
    ("20000", GROUP_PLAN): "-2560.02",
    ("70000", GROUP_PLAN): "6282.16",
    ("200000", GROUP_PLAN): "32886.26",
    ("20000", ALONE_AND_TENANT): "-2560.02",
    ("70000", ALONE_AND_TENANT): "6282.16",
    ("200000", ALONE_AND_TENANT): "32886.26",
}


@pytest.mark.parametrize(("salary", "scenario", "expected"), _cases(LINE_172_FIGURES))
def test_5005_r_line_172(salary: str, scenario: str, expected: str) -> None:
    sheet = _sheets(salary, scenario)["ca-qc/t1_tax_and_credits"]

    assert sheet.get(REFUND_OR_BALANCE_OWING_LINE_172).value == D(expected)


LINE_450_FIGURES = {
    ("20000", DEFAULT): "8.96",
    ("70000", DEFAULT): "8396.16",
    ("200000", DEFAULT): "38757.53",
    ("20000", GROUP_PLAN): "8.96",
    ("70000", GROUP_PLAN): "7641.16",
    ("200000", GROUP_PLAN): "38002.53",
    ("20000", ALONE_AND_TENANT): "0.00",
    ("70000", ALONE_AND_TENANT): "8396.16",
    ("200000", ALONE_AND_TENANT): "38757.53",
}


@pytest.mark.parametrize(("salary", "scenario", "expected"), _cases(LINE_450_FIGURES))
def test_tp1_line_450(salary: str, scenario: str, expected: str) -> None:
    sheet = _sheets(salary, scenario)["ca-qc/tp1_totals"]

    assert sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value == D(expected)


LINE_456_FIGURES = {
    ("20000", DEFAULT): "584.02",
    ("70000", DEFAULT): "0.00",
    ("200000", DEFAULT): "0.00",
    ("20000", GROUP_PLAN): "584.02",
    ("70000", GROUP_PLAN): "0.00",
    ("200000", GROUP_PLAN): "0.00",
    ("20000", ALONE_AND_TENANT): "584.02",
    ("70000", ALONE_AND_TENANT): "0.00",
    ("200000", ALONE_AND_TENANT): "0.00",
}


@pytest.mark.parametrize(("salary", "scenario", "expected"), _cases(LINE_456_FIGURES))
def test_tp1_line_456(salary: str, scenario: str, expected: str) -> None:
    sheet = _sheets(salary, scenario)["ca-qc/tp1_totals"]

    assert sheet.get(TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456).value == D(expected)


SOLIDARITY_FIGURES = {
    ("20000", DEFAULT): "363.00",
    ("70000", DEFAULT): "0.00",
    ("200000", DEFAULT): "0.00",
    ("20000", GROUP_PLAN): "363.00",
    ("70000", GROUP_PLAN): "0.00",
    ("200000", GROUP_PLAN): "0.00",
    ("20000", ALONE_AND_TENANT): "1281.00",
    ("70000", ALONE_AND_TENANT): "0.00",
    ("200000", ALONE_AND_TENANT): "0.00",
}


@pytest.mark.parametrize(("salary", "scenario", "expected"), _cases(SOLIDARITY_FIGURES))
def test_the_solidarity_credit(salary: str, scenario: str, expected: str) -> None:
    sheet = _sheets(salary, scenario)["ca-qc/return"]

    assert sheet.get(SOLIDARITY_CREDIT).value == D(expected)


LINE_45300_FIGURES = {
    ("20000", DEFAULT): "2679.07",
    ("70000", DEFAULT): "0.00",
    ("200000", DEFAULT): "0.00",
    ("20000", GROUP_PLAN): "2679.07",
    ("70000", GROUP_PLAN): "0.00",
    ("200000", GROUP_PLAN): "0.00",
    ("20000", ALONE_AND_TENANT): "2679.07",
    ("70000", ALONE_AND_TENANT): "0.00",
    ("200000", ALONE_AND_TENANT): "0.00",
}


@pytest.mark.parametrize(("salary", "scenario", "expected"), _cases(LINE_45300_FIGURES))
def test_5005_r_line_45300(salary: str, scenario: str, expected: str) -> None:
    sheet = _sheets(salary, scenario)["ca-qc/t1_tax_and_credits"]

    assert sheet.get(CWB_LINE_161).value == D(expected)


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("salary", SALARIES)
def test_the_refund_and_the_total_payable_follow_from_the_printed_lines(
    salary: str, scenario: str
) -> None:
    sheets = _sheets(salary, scenario)
    line_172 = sheets["ca-qc/t1_tax_and_credits"].get(REFUND_OR_BALANCE_OWING_LINE_172).value
    line_450 = sheets["ca-qc/tp1_totals"].get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value
    line_456 = sheets["ca-qc/tp1_totals"].get(TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456).value
    summary = sheets["ca-qc/return"]

    assert summary.get(REFUND_OR_BALANCE_OWING).value == line_172 + line_450 - line_456
    line_43500 = summary.get(FEDERAL_TOTAL_PAYABLE_RETURN).value
    line_44000 = summary.get(REFUNDABLE_QUEBEC_ABATEMENT_RETURN).value
    assert summary.get(TOTAL_PAYABLE).value == line_43500 - line_44000 + line_450


# 5000-G, line 31205: under $2,000 of PPIP insurable earnings, "do not claim any PPIP premiums on
# line 31205. Instead, claim this amount as an overpayment on your Revenu Quebec Income Tax Return":
# 0.494% of 1,500 is 7.41, claimed on TP-1 line 457 and nowhere else. Columns: 5005-R line 91 and
# 31205, TP-1 line 457, the refund or balance owing.
UNDER_2000_FIGURES = {
    "1500": ("0.00", "7.41", "-7.41"),
}


@pytest.mark.parametrize(("salary", "figures"), list(UNDER_2000_FIGURES.items()))
def test_under_2000_of_salary_the_premium_is_claimed_once_as_the_qpip_overpayment(
    salary: str, figures: tuple[str, str, str]
) -> None:
    sheets = _sheets(salary, DEFAULT)

    assert (
        sheets["ca-qc/t1_tax_and_credits"].get(PPIP_PREMIUMS_LINE_91).value,
        sheets["ca-qc/tp1_totals"].get(TP1_LINE_457).value,
        sheets["ca-qc/return"].get(REFUND_OR_BALANCE_OWING).value,
    ) == tuple(D(figure) for figure in figures)
