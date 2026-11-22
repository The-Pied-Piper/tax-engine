"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 14,
"Correction of employment income (line 105)", as the Quebec take-home manifest wires it.

Line 14 is a copy of TP-1 line 105, an input of the TP-1 income form only. It reads that form's
export as a record list of one, so the one step is `core/record_total`; a blank line 105 is read
as 0.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_105,
    TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.test_take_home_tp1_schedule_f_line_16 import (
    HEADER,
    PARTS,
)

D = Decimal

MANIFESTS = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025"
PART = MANIFESTS / "tp1_schedule_f_line_14.yaml"
# The end of the chain: a form cannot hold a produced line that nothing reads or exports.
LINE_14_PARTS = tuple(
    part
    for part in PARTS
    if part not in ("tp1_schedule_f_line_12.yaml", "tp1_schedule_f_line_16.yaml")
)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_f
      required: true
      exports:
        - ca-qc/tp1_schedule_f_employment_income_correction_line_14
    """)


def test_the_input_part_is_gone_and_line_14_declares_no_input() -> None:
    assert not (MANIFESTS / "tp1_schedule_f_line_14_input.yaml").exists()
    assert "inputs" not in yaml.safe_load(PART.read_text(encoding="utf-8"))


def test_line_14_is_one_record_total_of_the_tp1_line_105_export() -> None:
    (step,) = yaml.safe_load(PART.read_text(encoding="utf-8"))["capabilities"]

    assert step["name"] == "core/record_total"
    assert step["reference"] == "14"
    assert step["consumes"] == {"records": "ca-qc/tp1_income.tp1_line_105"}
    assert step["blank"] == {"records": {"ca-qc/tp1_line_105": "0"}}
    assert step["produces"] == {
        "output": "ca-qc/tp1_schedule_f_employment_income_correction_line_14"
    }


def _line_14(take_home_service: TakeHomeService, *given: str) -> Decimal:
    starting = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    starting.extend(Artifact(TP1_LINE_105, D(value)) for value in given)
    (sheet,) = take_home_service(HEADER, FORM, *LINE_14_PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_schedule_f"]
    return sheet.get(TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14).value


def test_line_14_is_zero_when_line_105_is_left_blank(take_home_service: TakeHomeService) -> None:
    assert _line_14(take_home_service) == D("0")


def test_line_14_is_the_line_105_the_caller_gave(take_home_service: TakeHomeService) -> None:
    assert _line_14(take_home_service, "500") == D("500")
