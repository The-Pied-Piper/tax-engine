"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 70, as the Quebec take-home
manifest wires it. Printed as "Income subject to the contribution".

Line 68 is a step over the printed lines 41 to 62 (optional inputs, read as 0 when left
out; line 70 is `core/subtract` of line 68 from line 36, rounded half-up to the cent. The $18,130
stop is not a step: Part B prints it.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_FOREST_PRODUCER_AVERAGING_LINE_276,
    TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70,
    TP1_SCHEDULE_F_LINE_41,
    TP1_SCHEDULE_F_LINE_62,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import SALARY_PARTS
from tests.jurisdictions.ca_qc.tp1_schedule_f_support import LINE_68_COPY_PARTS, NET_INCOME_PARTS

D = Decimal

FORM_PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f.yaml"
)

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
    "tp1_schedule_f_line_10_input.yaml",
    "tp1_schedule_f_line_10.yaml",
    "tp1_schedule_f_line_12.yaml",
    "tp1_schedule_f_line_14.yaml",
    "tp1_schedule_f_line_16.yaml",
    "tp1_schedule_f_line_18.yaml",
    "tp1_schedule_f_line_34_inputs.yaml",
    "tp1_schedule_f_line_25_inputs.yaml",
    "tp1_schedule_f_line_25.yaml",
    "tp1_schedule_f_line_22.yaml",
    "tp1_schedule_f_line_23.yaml",
    "tp1_schedule_f_line_26.yaml",
    "tp1_schedule_f_line_28.yaml",
    "tp1_schedule_f_line_29.yaml",
    "tp1_schedule_f_line_34.yaml",
    "tp1_schedule_f_line_36.yaml",
    *NET_INCOME_PARTS,
    *LINE_68_COPY_PARTS,
    "tp1_schedule_f_line_68_inputs.yaml",
    "tp1_schedule_f_line_68.yaml",
    "tp1_schedule_f_line_70.yaml",
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
        - ca-qc/tp1_schedule_f_income_subject_line_70
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


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_70_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    value = schedule_f(take_home_service, salary).get(TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70).value

    assert str(value) == "0.00"


def test_line_68_is_taken_off_line_36(take_home_service: TakeHomeService) -> None:
    given = (
        (TP1_FOREST_PRODUCER_AVERAGING_LINE_276, "1000"),
        (TP1_SCHEDULE_F_LINE_41, "100.25"),
        (TP1_SCHEDULE_F_LINE_62, "200.00"),
    )
    value = (
        schedule_f(take_home_service, "70000", *given)
        .get(TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70)
        .value
    )

    assert str(value) == "699.75"


def test_the_form_part_names_the_form_and_exports_lines_70_and_82() -> None:
    part = yaml.safe_load(FORM_PART.read_text(encoding="utf-8"))

    assert part["form"]["name"] == "ca-qc/tp1_schedule_f"
    assert part["form"]["title"] == "Schedule F: Contribution to the Health Services Fund"
    assert part["form"]["exports"] == [
        "ca-qc/tp1_schedule_f_income_subject_line_70",
        "ca-qc/tp1_schedule_f_contribution_line_82",
    ]
    assert part["capabilities"] == []
