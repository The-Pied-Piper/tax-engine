"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 16, as the Quebec take-home
manifest wires it. Printed as "Add lines 12 and 14, or subtract line 14 from line 12".

Line 14 (the correction of employment income) is a signed copy of TP-1 line 105, 0 when that is left
out; line 16 is `core/sum` of lines 12 and 14, rounded half-up to the cent.
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
    TP1_LINE_105,
    TP1_SCHEDULE_F_EMPLOYMENT_INCOME_TOTAL_LINE_16,
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
    "tp1_schedule_f_line_12.yaml",
    "tp1_schedule_f_line_14.yaml",
    "tp1_schedule_f_line_16.yaml",
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
        - ca-qc/tp1_schedule_f_employment_income_total_line_16
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
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "200000.00")],
)
def test_a_blank_line_14_is_read_as_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = (
        schedule_f(take_home_service, salary)
        .get(TP1_SCHEDULE_F_EMPLOYMENT_INCOME_TOTAL_LINE_16)
        .value
    )

    assert str(value) == expected


def test_a_positive_line_105_reaches_line_16(take_home_service: TakeHomeService) -> None:
    given = (TP1_LINE_105, "500")
    value = (
        schedule_f(take_home_service, "70000", given)
        .get(TP1_SCHEDULE_F_EMPLOYMENT_INCOME_TOTAL_LINE_16)
        .value
    )

    assert str(value) == "70500.00"
