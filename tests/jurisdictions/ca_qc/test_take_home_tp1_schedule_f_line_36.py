"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 36, as the Quebec take-home
manifest wires it. Printed as "Income".

Line 34, the printed sum of the skipped lines 20 to 33, is one optional input, read as 0 when left
out; line 36 is `core/subtract` of line 34 from line 18, rounded half-up to the cent.
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
    TP1_FOREST_PRODUCER_AVERAGING_LINE_276,
    TP1_SCHEDULE_F_INCOME_LINE_36,
    TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import SALARY_PARTS

D = Decimal

PARTS = (
    *SALARY_PARTS,
    "tp1_income.yaml",
    "tp1_income_line_105_input.yaml",
    "tp1_income_line_107_input.yaml",
    "tp1_income_line_box_211_input.yaml",
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
    "tp1_schedule_f_line_10_input.yaml",
    "tp1_schedule_f_line_10.yaml",
    "tp1_schedule_f_line_12.yaml",
    "tp1_schedule_f_line_14_input.yaml",
    "tp1_schedule_f_line_16.yaml",
    "tp1_schedule_f_line_18.yaml",
    "tp1_schedule_f_line_34_input.yaml",
    "tp1_schedule_f_line_36.yaml",
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
        - ca-qc/tp1_schedule_f_income_line_36
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


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_36_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    value = schedule_f(take_home_service, salary).get(TP1_SCHEDULE_F_INCOME_LINE_36).value

    assert str(value) == "0.00"


def test_line_34_is_taken_off_line_18(take_home_service: TakeHomeService) -> None:
    given = (
        (TP1_FOREST_PRODUCER_AVERAGING_LINE_276, "1000"),
        (TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34, "250.50"),
    )
    value = schedule_f(take_home_service, "70000", *given).get(TP1_SCHEDULE_F_INCOME_LINE_36).value

    assert str(value) == "749.50"
