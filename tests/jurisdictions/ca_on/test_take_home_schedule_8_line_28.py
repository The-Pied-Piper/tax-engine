"""Schedule 8 (5000-S8, 2025) Part 3 line 28, as the Ontario take-home manifest part wires it.

Form text: Line 28: Line 26 plus line 27 (CRA 5000-S8 2025).

Lines 26 and 27 are pure copies of lines 12 and 22, so the part sums lines 12 and 22 directly.
The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them, and lines 12 and 22 are plain inputs because the sibling
line parts are separate tickets. The figures are the ticket's worked cases: a $70,000 salary
(line 12 is 665.00, line 22 is 0) and a $90,000 salary (line 12 is 678.00, line 22 is 396.00).
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
    CPP_PART_3_LINE_12,
    CPP_PART_3_LINE_22,
    CPP_PART_3_LINE_28,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "schedule_8_line_28.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_part_3_line_12
        required: true
      - name: ca/cpp_part_3_line_22
        required: true
    outputs:
      - ca/cpp_part_3_line_12
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_part_3_line_28
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "00_header.yaml").write_text(HEADER)
    (parts / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "02_line_28.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def line_28(tmp_path: Path, line_12: str, line_22: str) -> Decimal:
    worksheets = service(tmp_path).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(CPP_PART_3_LINE_12, D(line_12)),
        Artifact(CPP_PART_3_LINE_22, D(line_22)),
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_PART_3_LINE_28).value


def test_line_28_is_line_12_when_line_22_is_zero(tmp_path: Path) -> None:
    assert line_28(tmp_path, "665.00", "0") == D("665.00")


def test_line_28_is_line_12_plus_line_22(tmp_path: Path) -> None:
    assert line_28(tmp_path, "678.00", "396.00") == D("1074.00")


def test_line_28_is_zero_when_both_lines_are_zero(tmp_path: Path) -> None:
    assert line_28(tmp_path, "0", "0") == D("0")


def test_line_28_applies_no_rounding(tmp_path: Path) -> None:
    assert line_28(tmp_path, "0.01", "0.02") == D("0.03")
