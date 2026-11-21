"""Revenu Quebec TP-1 (2025) line 97, "QPIP premium. RL-1 slip, box H", as the Quebec take-home
manifest part
wires it: the amount given when the filer has it, else computed from line 101, the salary.

The form prints no rate or ceiling for the slip box. The caller has no RL-1 slip, so the input
`ca-qc/tp1_qpip_premium_given_line_97` is optional: a request that gives it has that figure as line
97,
unchanged; a request that leaves it out has line 97 computed by
`ca/given_or_contribution_tier` from the salary with the `ca-qc/tp1_line_97_qpip_premium` dataset
(0.494% up to $98,000, at most $484.12; the figures are a listed check from a Revenu Quebec web
page).
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
    TP1_QPIP_PREMIUM_GIVEN_LINE_97,
    TP1_QPIP_PREMIUM_LINE_97,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import SALARY_PARTS

D = Decimal

PARTS = (
    *SALARY_PARTS,
    "tp1_income_line_97_input.yaml",
    "tp1_income_line_97.yaml",
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
        - ca-qc/tp1_qpip_premium_line_97
    """)


def tp1(take_home_service: TakeHomeService, salary: str, given: str | None = None) -> Worksheet:
    """The TP-1 income worksheet for a salary; line 97 is left out unless `given` is passed."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if given is not None:
        starting.append(Artifact(TP1_QPIP_PREMIUM_GIVEN_LINE_97, D(given)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_income"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "98.80"),
        ("70000", "345.80"),
        ("200000", "484.12"),
        ("0", "0.00"),
    ],
)
def test_a_blank_line_97_is_computed_from_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert tp1(take_home_service, salary).get(TP1_QPIP_PREMIUM_LINE_97).value == D(expected)


def test_a_blank_line_97_is_computed_to_the_cent(take_home_service: TakeHomeService) -> None:
    value = tp1(take_home_service, "70000").get(TP1_QPIP_PREMIUM_LINE_97).value

    assert str(value) == "345.80"


@pytest.mark.parametrize("given", ["300.00", "0"])
def test_a_given_line_97_is_the_output_unchanged(
    take_home_service: TakeHomeService, given: str
) -> None:
    value = tp1(take_home_service, "70000", given).get(TP1_QPIP_PREMIUM_LINE_97).value

    assert str(value) == given


def test_a_given_line_97_is_not_computed_from_the_salary(
    take_home_service: TakeHomeService,
) -> None:
    value = tp1(take_home_service, "200000", "300.00").get(TP1_QPIP_PREMIUM_LINE_97).value

    assert str(value) == "300.00"
