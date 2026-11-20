"""Revenu Quebec Work Chart 201 (TP-1.D.GR-V 2025-12) line 8, "Subtract line 7 from line 6", as the
Quebec take-home manifest parts wire it.

Form text: "7. Amount included in the income above and entitling you to a deduction on line 293 -
8. Subtract line 7 from line 6. =". Line 7 is an optional input, read as 0 when left out, so a
salary-only filer's line 8 is the salary ($20,000, $70,000, $200,000). The form prints no floor, so
line 7 above line 6 gives a negative line 8. The difference is `core/subtract`, rounded half-up to
the cent by `ca-qc/cent_rounding`.
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
    WORK_CHART_201_LINE_8,
    WORK_CHART_201_LINE_293_AMOUNT_LINE_7,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import TP1_INCOME_WORK_INCOME_FORM

D = Decimal

PARTS = (
    "salary.yaml",
    "tp1_income_line_105_input.yaml",
    "tp1_income_line_107_input.yaml",
    "tp1_income_line_box_211_input.yaml",
    "work_chart_201_line_1.yaml",
    "work_chart_201_line_2_input.yaml",
    "work_chart_201_line_3_input.yaml",
    "work_chart_201_line_4_input.yaml",
    "work_chart_201_line_5_input.yaml",
    "work_chart_201_line_6.yaml",
    "work_chart_201_line_7_input.yaml",
    "work_chart_201_line_8.yaml",
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
        - ca-qc/work_chart_201_line_8
    """)


def chart(take_home_service: TakeHomeService, salary: str, line_7: str | None = None) -> Worksheet:
    """The Work Chart 201 worksheet for a salary; line 7 is left out unless `line_7`."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_7 is not None:
        starting.append(Artifact(WORK_CHART_201_LINE_293_AMOUNT_LINE_7, D(line_7)))
    (sheet,) = take_home_service(
        HEADER, FORM, *PARTS, extra_forms=(TP1_INCOME_WORK_INCOME_FORM,)
    ).compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca-qc/work_chart_201"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "200000.00")],
)
def test_a_salary_only_line_8_is_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart(take_home_service, salary).get(WORK_CHART_201_LINE_8).value

    assert str(value) == expected


def test_line_7_is_taken_off_line_6(take_home_service: TakeHomeService) -> None:
    value = chart(take_home_service, "70000", "1234.56").get(WORK_CHART_201_LINE_8).value

    assert str(value) == "68765.44"


def test_the_form_prints_no_floor_on_line_8(take_home_service: TakeHomeService) -> None:
    value = chart(take_home_service, "1000", "1500").get(WORK_CHART_201_LINE_8).value

    assert str(value) == "-500.00"
