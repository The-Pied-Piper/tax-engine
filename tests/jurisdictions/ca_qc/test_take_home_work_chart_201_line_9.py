"""Revenu Quebec Work Chart 201 (TP-1.D.GR-V 2025-12) line 9, "Deduction for workers", as the Quebec
take-home manifest parts wire it.

Form text: "x 6% Multiply line 8 by 6%. 9. Carry the result to line 201 of your return (maximum
$1,420). Deduction for workers". The 6% and the maximum are printed figures, held in the
`ca-qc/work_chart_201_rate` and `ca-qc/work_chart_201_maximum` datasets. A salary-only filer's line
9 is 6% of the salary, at most $1,420: $1,200.00 at $20,000, $1,420.00 at $70,000 and at $200,000
(hand-computed from the printed chart). `core/apply_rate` multiplies without rounding, then
`core/capped_amount` rounds half-up to the cent once.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest
import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    WORK_CHART_201_DEDUCTION_FOR_WORKERS_LINE_9,
    WORK_CHART_201_LINE_293_AMOUNT_LINE_7,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import TP1_PARTS

D = Decimal

PARTS = (
    *TP1_PARTS,
    "work_chart_201_line_1.yaml",
    "work_chart_201_line_2_input.yaml",
    "work_chart_201_line_3_input.yaml",
    "work_chart_201_line_4_input.yaml",
    "work_chart_201_line_5.yaml",
    "work_chart_201_line_6.yaml",
    "work_chart_201_line_7_input.yaml",
    "work_chart_201_line_8.yaml",
    "work_chart_201_line_9.yaml",
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
        - ca-qc/work_chart_201_deduction_for_workers_line_9
    """)


def chart(take_home_service: TakeHomeService, salary: str, line_7: str | None = None) -> Worksheet:
    """The Work Chart 201 worksheet for a salary; line 7 is left out unless `line_7`."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_7 is not None:
        starting.append(Artifact(WORK_CHART_201_LINE_293_AMOUNT_LINE_7, D(line_7)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )["ca-qc/work_chart_201"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1200.00"), ("70000", "1420.00"), ("200000", "1420.00")],
)
def test_a_salary_only_line_9_is_6_percent_of_the_salary_at_most_1420(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart(take_home_service, salary).get(WORK_CHART_201_DEDUCTION_FOR_WORKERS_LINE_9).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("23666.67", "1420.00"), ("23666.50", "1419.99"), ("0.09", "0.01"), ("0.08", "0.00")],
)
def test_the_maximum_and_the_cent_are_reached_at_the_printed_figures(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart(take_home_service, salary).get(WORK_CHART_201_DEDUCTION_FOR_WORKERS_LINE_9).value

    assert str(value) == expected


def test_line_7_is_taken_off_before_the_rate(take_home_service: TakeHomeService) -> None:
    value = (
        chart(take_home_service, "20000", "10000")
        .get(WORK_CHART_201_DEDUCTION_FOR_WORKERS_LINE_9)
        .value
    )

    assert str(value) == "600.00"


def test_the_real_form_declaration_exports_line_9_and_the_inputs_other_forms_read() -> None:
    declaration = yaml.safe_load((QUEBEC_PARTS / "work_chart_201.yaml").read_text(encoding="utf-8"))

    assert declaration["form"]["name"] == "ca-qc/work_chart_201"
    assert declaration["form"]["required"] is True
    assert set(declaration["form"]["exports"]) >= {
        "ca-qc/work_chart_201_deduction_for_workers_line_9",
        "ca-qc/work_chart_201_research_grants_line_3",
        "ca-qc/work_chart_201_wepp_payments_line_4",
    }
