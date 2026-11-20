"""Revenu Quebec Work Chart 201 (TP-1.D.GR-V 2025-12) line 1, "Eligible work income", as the Quebec
take-home manifest parts wire it.

Form text: "1. Eligible work income (lines 101, 107 and, if positive, 105, minus the amount from box
211 of your RL-1 slip)." Line 101 is the salary; lines 107 and 105 and box 211 are optional inputs,
read as 0 when left out. A salary-only filer's line 1 is the salary ($20,000, $70,000, $200,000).
The sum is `core/sum`, the subtraction `core/subtract_not_below_zero`, both rounded half-up to the
cent by `ca-qc/cent_rounding`.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1,
    WORK_CHART_201_LINE_105,
    WORK_CHART_201_LINE_107,
    WORK_CHART_201_RL1_BOX_211,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "salary.yaml",
    "work_chart_201_line_1_input_105.yaml",
    "work_chart_201_line_1_input_107.yaml",
    "work_chart_201_line_1_input_box_211.yaml",
    "work_chart_201_line_1.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-qc/work_chart_201
      required: true
      exports:
        - ca-qc/work_chart_201_eligible_work_income_line_1
    """)


def chart(take_home_service: TakeHomeService, salary: str, **given: str) -> Worksheet:
    """The Work Chart 201 worksheet for a salary; `line_105`, `line_107` and `box_211` are left
    out unless passed."""
    kinds = {
        "line_105": WORK_CHART_201_LINE_105,
        "line_107": WORK_CHART_201_LINE_107,
        "box_211": WORK_CHART_201_RL1_BOX_211,
    }
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    starting += [Artifact(kinds[name], D(value)) for name, value in given.items()]
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/work_chart_201"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "200000.00"), ("0", "0.00")],
)
def test_a_salary_only_line_1_is_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart(take_home_service, salary).get(WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1).value

    assert str(value) == expected


def test_lines_107_and_105_are_added_to_the_salary(take_home_service: TakeHomeService) -> None:
    sheet = chart(take_home_service, "70000", line_107="1000.50", line_105="200.25")

    assert str(sheet.get(WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1).value) == "71200.75"


def test_box_211_is_taken_off(take_home_service: TakeHomeService) -> None:
    sheet = chart(take_home_service, "70000", box_211="2500.10")

    assert str(sheet.get(WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1).value) == "67499.90"


def test_box_211_above_the_income_leaves_zero(take_home_service: TakeHomeService) -> None:
    sheet = chart(take_home_service, "1000", box_211="1500")

    assert str(sheet.get(WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1).value) == "0.00"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    sheet = chart(take_home_service, "70000", line_107="0.005")

    assert str(sheet.get(WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1).value) == "70000.01"
