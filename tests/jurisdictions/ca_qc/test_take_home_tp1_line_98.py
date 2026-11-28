"""Revenu Quebec TP-1 (2025) line 98, "QPP contribution. RL-1 slip, box B.A", as the Quebec take-
home manifest part wires it: the amount given when the filer has it, else Schedule 8 line 11 plus
line 12, each to the cent, as the form's own lines are (the same lines the take-home deductions
read, so a filer with no QPP months has 0).

The form prints no rate or ceiling for the slip box. The caller has no RL-1 slip, so the input
`ca-qc/tp1_qpp_contribution_given_line_98` is optional: a request that leaves it out has line 98
as Schedule 8 line 11 (5.4% of line 7, at most $3,661.20) plus line 12 (1% of line 7, at most
$678.00).
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
    TP1_QPP_CONTRIBUTION_GIVEN_LINE_98,
    TP1_QPP_CONTRIBUTION_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import SALARY_PARTS

D = Decimal

PARTS = (
    *SALARY_PARTS,
    "tp1_income_line_98_input.yaml",
    "tp1_income_line_98.yaml",
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
      name: ca-qc/tp1_income
      required: true
      exports:
        - ca-qc/tp1_employment_income_line_101
        - ca-qc/tp1_qpp_contribution_line_98
    """)


def tp1(take_home_service: TakeHomeService, salary: str, given: str | None = None) -> Worksheet:
    """The TP-1 income worksheet for a salary; line 98 is left out unless `given` is passed."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if given is not None:
        starting.append(Artifact(TP1_QPP_CONTRIBUTION_GIVEN_LINE_98, D(given)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )["ca-qc/tp1_income"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "1056.00"),
        ("70000", "4256.00"),
        ("200000", "4339.20"),
        ("3000", "0.00"),
    ],
)
def test_a_blank_line_98_is_computed_from_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert tp1(take_home_service, salary).get(TP1_QPP_CONTRIBUTION_LINE_98).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    # Line 7 is the salary less 3,500: 50,000.08 gives 2,700.00 (5.4%) + 500.00 (1%) = 3,200.00,
    # where one 6.4% rounding would give 3,200.01; 50,000.24 gives 2,700.01 + 500.00 = 3,200.01.
    [("53500.08", "3200.00"), ("53500.24", "3200.01")],
)
def test_a_blank_line_98_adds_the_two_schedule_8_lines_each_rounded_to_the_cent(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert tp1(take_home_service, salary).get(TP1_QPP_CONTRIBUTION_LINE_98).value == D(expected)


def test_a_blank_line_98_is_computed_to_the_cent(take_home_service: TakeHomeService) -> None:
    value = tp1(take_home_service, "70000").get(TP1_QPP_CONTRIBUTION_LINE_98).value

    assert str(value) == "4256.00"


@pytest.mark.parametrize("given", ["4000.00", "0"])
def test_a_given_line_98_is_the_output_unchanged(
    take_home_service: TakeHomeService, given: str
) -> None:
    value = tp1(take_home_service, "70000", given).get(TP1_QPP_CONTRIBUTION_LINE_98).value

    assert str(value) == given


def test_a_given_line_98_is_not_computed_from_the_salary(
    take_home_service: TakeHomeService,
) -> None:
    value = tp1(take_home_service, "200000", "4000.00").get(TP1_QPP_CONTRIBUTION_LINE_98).value

    assert str(value) == "4000.00"
