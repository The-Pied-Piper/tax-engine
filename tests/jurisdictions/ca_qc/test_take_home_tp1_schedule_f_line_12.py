"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 12, as the Quebec take-home
manifest wires it. Printed as "Employment income".

Line 12 is a copy of TP-1 line 101, the salary. It arrives from the TP-1 income form as a record
list of one, so the one step is `core/record_total`.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_SCHEDULE_F_EMPLOYMENT_INCOME_LINE_12,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "salary.yaml",
    "tp1_income.yaml",
    "tp1_income_line_199_input.yaml",
    "tp1_income_line_199.yaml",
    "tp1_income_line_97_input.yaml",
    "tp1_income_line_97.yaml",
    "tp1_income_line_98_input.yaml",
    "tp1_income_line_98.yaml",
    "tp1_income_line_98_1_input.yaml",
    "tp1_income_line_98_1.yaml",
    "tp1_income_line_98_2_input.yaml",
    "tp1_income_line_98_2.yaml",
    "tp1_schedule_f_line_12.yaml",
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
      name: ca-qc/tp1_schedule_f
      required: true
      exports:
        - ca-qc/tp1_schedule_f_employment_income_line_12
    """)


def schedule_f(
    take_home_service: TakeHomeService, salary: str, *given: tuple[AmountKind, str]
) -> Worksheet:
    """The Schedule F worksheet for a salary; every optional input is left out unless in `given`."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    starting.extend(Artifact(kind, D(value)) for kind, value in given)
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_schedule_f"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000"), ("70000", "70000"), ("200000", "200000")],
)
def test_line_12_is_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = (
        schedule_f(take_home_service, salary).get(TP1_SCHEDULE_F_EMPLOYMENT_INCOME_LINE_12).value
    )

    assert value == D(expected)
