"""Schedule 8 (5000-S8, 2025) Part 2 line E, the maximum basic exemption, as the Ontario
manifest part wires it: the row of the monthly proration table for the months on line A.

The manifest part is loaded from the package. The header, the form's export and the months
input (line A, "Enter "12" on line A below unless any of the following conditions apply") are
made up here, because the shared scaffold owns them. The figure is the printed 12-month row,
$3,500.00, whatever the salary: no salary reaches this line.
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
from tax_engine.jurisdictions.ca.catalog.deductions import CPP_BASIC_EXEMPTION, CPP_MONTHS

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "schedule_8_line_e.yaml"
)

SCAFFOLD = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_months
        required: false
        default: "12"
        basis: 'Enter "12" on line A below unless any of the following conditions apply'
    outputs:
      - ca/cpp_months
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_basic_exemption
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "00_header.yaml").write_text(SCAFFOLD)
    (parts / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "02_line_e.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parser_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parser_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def line_e(tmp_path: Path, *artifacts: Artifact[int]) -> Decimal:
    worksheets = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *artifacts)
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_BASIC_EXEMPTION).value


def test_line_e_is_3500_for_the_default_twelve_months(tmp_path: Path) -> None:
    assert line_e(tmp_path) == D("3500.00")


def test_line_e_is_3500_for_twelve_months_given(tmp_path: Path) -> None:
    assert line_e(tmp_path, Artifact(CPP_MONTHS, 12)) == D("3500.00")


def test_line_e_is_the_printed_row_for_fewer_months(tmp_path: Path) -> None:
    assert line_e(tmp_path, Artifact(CPP_MONTHS, 7)) == D("2041.67")
