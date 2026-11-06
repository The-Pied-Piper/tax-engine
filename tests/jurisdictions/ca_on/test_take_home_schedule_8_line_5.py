"""Schedule 8 (5000-S8, 2025) Part 3 line 5, as the Ontario take-home manifest part wires it.

Form text: Line 5: Line 2 minus line 4 (if negative, enter "0") (CRA 5000-S8 2025).

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them, and lines 2 and 4 are plain inputs because the sibling line
parts are separate tickets. The figures are the ticket's worked cases: a $70,000 salary (line 2 is
70000.00, line 4 is 0) and a $90,000 salary (line 2 is 81200.00, line 4 is 9900.00).
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import tax_engine.jurisdictions.ca_on
import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.deductions import (
    CPP_PART_3_LINE_2,
    CPP_PART_3_LINE_4,
    CPP_PART_3_LINE_5,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "schedule_8_line_5.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_part_3_line_2
        required: true
      - name: ca/cpp_part_3_line_4
        required: true
    outputs:
      - ca/cpp_part_3_line_2
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_part_3_line_5
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "00_header.yaml").write_text(HEADER)
    (parts / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "02_line_5.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def line_5(tmp_path: Path, line_2: str, line_4: str) -> Decimal:
    worksheets = service(tmp_path).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(CPP_PART_3_LINE_2, D(line_2)),
        Artifact(CPP_PART_3_LINE_4, D(line_4)),
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_PART_3_LINE_5).value


def test_line_5_is_line_2_when_line_4_is_zero(tmp_path: Path) -> None:
    assert line_5(tmp_path, "70000.00", "0") == D("70000.00")


def test_line_5_is_line_2_minus_line_4(tmp_path: Path) -> None:
    assert line_5(tmp_path, "81200.00", "9900.00") == D("71300.00")


def test_line_5_is_zero_when_line_4_exceeds_line_2(tmp_path: Path) -> None:
    assert line_5(tmp_path, "100", "250") == D("0")
