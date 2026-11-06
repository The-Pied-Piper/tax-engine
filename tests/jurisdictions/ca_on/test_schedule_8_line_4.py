"""Schedule 8 (5000-S8, 2025) Part 3 line 4, the earnings subject to the second additional
contribution, as the Ontario manifest part wires it.

The manifest part is loaded from the package. The header, the form's export and the two
upstream figures are made up here, because other parts own them: line 2 and line B (the
amount copied on line 3). Line 4 reads: Line 2 minus line 3 (if negative, enter "0").
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
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_PART_3_LINE_2,
    CPP_PART_3_LINE_4,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "schedule_8_line_4.yaml"
)

SCAFFOLD = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_part_3_line_2
        required: true
      - name: ca/cpp_maximum_pensionable_earnings
        required: true
    outputs:
      - ca/cpp_part_3_line_2
      - ca/cpp_maximum_pensionable_earnings
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_part_3_line_4
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "00_header.yaml").write_text(SCAFFOLD)
    (parts / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "02_line_4.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parser_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parser_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def line_4(tmp_path: Path, line_2: str, line_b: str) -> Decimal:
    worksheets = service(tmp_path).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(CPP_PART_3_LINE_2, D(line_2)),
        Artifact(CPP_MAXIMUM_PENSIONABLE_EARNINGS, D(line_b)),
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_PART_3_LINE_4).value


def test_line_4_is_zero_when_line_2_is_below_line_b(tmp_path: Path) -> None:
    assert line_4(tmp_path, "70000.00", "71300.00") == D("0")


def test_line_4_is_line_2_minus_line_b_above_line_b(tmp_path: Path) -> None:
    assert line_4(tmp_path, "81200.00", "71300.00") == D("9900.00")


def test_line_4_is_zero_when_line_2_equals_line_b(tmp_path: Path) -> None:
    assert line_4(tmp_path, "71300.00", "71300.00") == D("0")


def test_line_4_is_one_cent_just_above_line_b(tmp_path: Path) -> None:
    assert line_4(tmp_path, "71300.01", "71300.00") == D("0.01")
