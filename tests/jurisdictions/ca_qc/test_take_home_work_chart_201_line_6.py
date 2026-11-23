"""Revenu Quebec Work Chart 201 (TP-1.D.GR-V 2025-12) line 6, "Add lines 1 through 5", as the Quebec
take-home manifest parts wire it.

Form text: "6. Add lines 1 through 5. =". Line 1 is the eligible work income (the salary when
nothing else is given); lines 2 to 5 are optional inputs, read as 0 when left out. A salary-only
filer's line 6 is the salary ($20,000, $70,000, $200,000). The sum is `core/sum`, rounded half-up to
the cent by `ca-qc/cent_rounding`.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    WORK_CHART_201_NET_BUSINESS_INCOME_LINE_5,
    WORK_CHART_201_RESEARCH_GRANTS_LINE_3,
    WORK_CHART_201_TOTAL_LINE_6,
    WORK_CHART_201_WEPP_PAYMENTS_LINE_4,
    WORK_CHART_201_WORK_INCENTIVE_AMOUNTS_LINE_2,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import TP1_PARTS

D = Decimal

PARTS = (
    *TP1_PARTS,
    "work_chart_201_line_1.yaml",
    "work_chart_201_line_2_input.yaml",
    "work_chart_201_line_3_input.yaml",
    "work_chart_201_line_4_input.yaml",
    "work_chart_201_line_5_input.yaml",
    "work_chart_201_line_6.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/work_chart_201
      required: true
      exports:
        - ca-qc/work_chart_201_total_line_6
    """)

LINES = {
    "line_2": WORK_CHART_201_WORK_INCENTIVE_AMOUNTS_LINE_2,
    "line_3": WORK_CHART_201_RESEARCH_GRANTS_LINE_3,
    "line_4": WORK_CHART_201_WEPP_PAYMENTS_LINE_4,
    "line_5": WORK_CHART_201_NET_BUSINESS_INCOME_LINE_5,
}


def chart(take_home_service: TakeHomeService, salary: str, **given: str) -> Worksheet:
    """The Work Chart 201 worksheet for a salary; lines 2 to 5 are left out unless passed."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    starting += [Artifact(LINES[name], D(value)) for name, value in given.items()]
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )["ca-qc/work_chart_201"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "200000.00")],
)
def test_a_salary_only_line_6_is_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart(take_home_service, salary).get(WORK_CHART_201_TOTAL_LINE_6).value

    assert str(value) == expected


def test_lines_2_to_5_are_added_to_line_1(take_home_service: TakeHomeService) -> None:
    sheet = chart(
        take_home_service,
        "70000",
        line_2="100.10",
        line_3="200.20",
        line_4="300.30",
        line_5="400.40",
    )

    assert str(sheet.get(WORK_CHART_201_TOTAL_LINE_6).value) == "71001.00"


def test_each_of_lines_2_to_5_is_read_as_zero_when_left_out(
    take_home_service: TakeHomeService,
) -> None:
    sheet = chart(take_home_service, "70000", line_4="50")

    assert str(sheet.get(WORK_CHART_201_TOTAL_LINE_6).value) == "70050.00"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    sheet = chart(take_home_service, "70000", line_3="0.005")

    assert str(sheet.get(WORK_CHART_201_TOTAL_LINE_6).value) == "70000.01"
