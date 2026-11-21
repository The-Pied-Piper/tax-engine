"""Revenu Quebec TP-1 (2025) line 98, "QPP contribution. RL-1 slip, box B.A", as the Quebec take-
home manifest part
wires it: the amount given when the filer has it, else computed from line 101, the salary.

The form prints no rate or ceiling for the slip box. The caller has no RL-1 slip, so the input
`ca-qc/tp1_qpp_contribution_given_line_98` is optional: a request that gives it has that figure as
line 98,
unchanged; a request that leaves it out has line 98 computed by
`ca/given_or_contribution_tier` from the salary with the `ca-qc/tp1_line_98_qpp_contribution`
dataset
(6.40% from $3,500 to $71,300, at most $4,339.20; the figures are a listed check from a Revenu
Quebec web page).
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
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_income
      required: true
      exports:
        - ca-qc/tp1_qpp_contribution_line_98
    """)


def tp1(take_home_service: TakeHomeService, salary: str, given: str | None = None) -> Worksheet:
    """The TP-1 income worksheet for a salary; line 98 is left out unless `given` is passed."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if given is not None:
        starting.append(Artifact(TP1_QPP_CONTRIBUTION_GIVEN_LINE_98, D(given)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
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
