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
The figures are hand-computed from the printed lines (the return summary tests carry the working),
not a CRA or Revenu Quebec example.
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
    REFUND_OR_BALANCE_OWING_LINE_172,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    SOLIDARITY_CREDIT,
    SOLIDARITY_LIVED_ALONE_LINE_12,
    SOLIDARITY_TENANT_OR_OWNER_LINES_32_36,
    TOTAL_PAYABLE,
    TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450,
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
