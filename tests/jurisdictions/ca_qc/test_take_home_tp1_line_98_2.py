"""Revenu Quebec TP-1 (2025) line 98.2, "Additional contribution to the QPP. RL-1, box B.B", as the
Quebec take-home manifest part
wires it: the amount given when the filer has it, else computed from line 101, the salary.

The form prints no rate or ceiling for the slip box. The caller has no RL-1 slip, so the input
`ca-qc/tp1_additional_qpp_contribution_given_line_98_2` is optional: a request that gives it has
that figure as line 98.2,
unchanged; a request that leaves it out has line 98.2 computed by
`ca/given_or_contribution_tier` from the salary with the `ca-
qc/tp1_line_98_2_additional_qpp_contribution` dataset
(4% from $71,300 to $81,200, at most $396.00; the figures are a listed check from a Revenu Quebec
web page).
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
    TP1_ADDITIONAL_QPP_CONTRIBUTION_GIVEN_LINE_98_2,
    TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "salary.yaml",
    "tp1_income_line_98_2_input.yaml",
    "tp1_income_line_98_2.yaml",
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
        - ca-qc/tp1_additional_qpp_contribution_line_98_2
    """)


def tp1(take_home_service: TakeHomeService, salary: str, given: str | None = None) -> Worksheet:
    """The TP-1 income worksheet for a salary; line 98.2 is left out unless `given` is passed."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if given is not None:
        starting.append(Artifact(TP1_ADDITIONAL_QPP_CONTRIBUTION_GIVEN_LINE_98_2, D(given)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_income"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "0.00"),
        ("70000", "0.00"),
        ("200000", "396.00"),
        ("75000", "148.00"),
    ],
)
def test_a_blank_line_98_2_is_computed_from_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert tp1(take_home_service, salary).get(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2).value == D(
        expected
    )


def test_a_blank_line_98_2_is_computed_to_the_cent(take_home_service: TakeHomeService) -> None:
    value = tp1(take_home_service, "70000").get(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2).value

    assert str(value) == "0.00"


@pytest.mark.parametrize("given", ["100.00", "0"])
def test_a_given_line_98_2_is_the_output_unchanged(
    take_home_service: TakeHomeService, given: str
) -> None:
    value = (
        tp1(take_home_service, "70000", given).get(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2).value
    )

    assert str(value) == given


def test_a_given_line_98_2_is_not_computed_from_the_salary(
    take_home_service: TakeHomeService,
) -> None:
    value = (
        tp1(take_home_service, "200000", "100.00")
        .get(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2)
        .value
    )

    assert str(value) == "100.00"
