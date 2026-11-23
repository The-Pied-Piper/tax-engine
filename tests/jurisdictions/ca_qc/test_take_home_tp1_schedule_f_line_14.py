"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 14, as the Quebec take-home
manifest wires it. Printed as "Correction of employment income (line 105)".

Line 14 is a copy of TP-1 line 105, an input of the TP-1 income form only. It arrives from that form
as a record list of one, so the one step is `core/record_total`; a blank line 105 is read as 0.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_105,
    TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14,
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
    "tp1_schedule_f_line_14.yaml",
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
      name: ca-qc/tp1_schedule_f
      required: true
      exports:
        - ca-qc/tp1_schedule_f_employment_income_correction_line_14
    """)


def schedule_f(
    take_home_service: TakeHomeService, salary: str, *given: tuple[AmountKind, str]
) -> Worksheet:
    """The Schedule F worksheet for a salary; every optional input is left out unless in `given`."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    starting.extend(Artifact(kind, D(value)) for kind, value in given)
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )["ca-qc/tp1_schedule_f"]
    return sheet


def test_a_blank_line_105_makes_line_14_zero(take_home_service: TakeHomeService) -> None:
    value = (
        schedule_f(take_home_service, "70000")
        .get(TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14)
        .value
    )

    assert value == D("0")


@pytest.mark.parametrize("given", ["500", "1234.56", "-500"])
def test_line_14_is_the_line_105_the_caller_gave(
    take_home_service: TakeHomeService, given: str
) -> None:
    value = (
        schedule_f(take_home_service, "70000", (TP1_LINE_105, given))
        .get(TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14)
        .value
    )

    assert value == D(given)
