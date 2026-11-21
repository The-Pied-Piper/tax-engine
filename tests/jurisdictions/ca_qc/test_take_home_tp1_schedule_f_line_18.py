"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 18, as the Quebec take-home
manifest wires it. Printed as "Subtract line 16 from line 10".

Line 18 is `core/subtract` of line 16 from line 10, rounded half-up to the cent. The form prints no
floor, and the $18,130 stop is not a step.
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
    TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14,
    TP1_SCHEDULE_F_INCOME_LINE_18,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "salary.yaml",
    "tp1_income.yaml",
    "tp1_income_line_105_input.yaml",
    "tp1_income_line_107_input.yaml",
    "tp1_income_line_box_211_input.yaml",
    "tp1_income_line_110_input.yaml",
    "tp1_income_line_111_input.yaml",
    "tp1_income_line_114_input.yaml",
    "tp1_income_line_119_input.yaml",
    "tp1_income_line_122_input.yaml",
    "tp1_income_line_123_input.yaml",
    "tp1_income_line_128_input.yaml",
    "tp1_income_line_130_input.yaml",
    "tp1_income_line_136_input.yaml",
    "tp1_income_line_139_input.yaml",
    "tp1_income_line_142_input.yaml",
    "tp1_income_line_147_input.yaml",
    "tp1_income_line_148_input.yaml",
    "tp1_income_line_154_input.yaml",
    "tp1_income_line_164_input.yaml",
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
        - ca-qc/tp1_schedule_f_income_line_18
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
def test_a_salary_only_line_18_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    value = schedule_f(take_home_service, salary).get(TP1_SCHEDULE_F_INCOME_LINE_18).value

    assert str(value) == "0.00"


def test_the_forest_averaging_amount_reaches_line_18(take_home_service: TakeHomeService) -> None:
    given = (TP1_FOREST_PRODUCER_AVERAGING_LINE_276, "1000")
    value = schedule_f(take_home_service, "70000", given).get(TP1_SCHEDULE_F_INCOME_LINE_18).value

    assert str(value) == "1000.00"


def test_line_18_is_not_floored(take_home_service: TakeHomeService) -> None:
    given = (TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14, "500")
    value = schedule_f(take_home_service, "70000", given).get(TP1_SCHEDULE_F_INCOME_LINE_18).value

    assert str(value) == "-500.00"
