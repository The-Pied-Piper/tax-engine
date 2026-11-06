"""Schedule 8 (5000-S8, 2025) Part 2 line B, the maximum pensionable earnings, as the Ontario
take-home manifest part wires it: the row of the monthly proration table for the months on line A.

The manifest part is loaded from the package. The header, the form's export and the months input
(line A, "Enter "12" on line A below unless any of the following conditions apply") are made up
here, because the shared scaffold owns them. The figure is the printed 12-month row, $71,300.00,
for a full-year filer whatever the salary: line B reads no salary.
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
    CPP_MONTHS,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "schedule_8_line_b.yaml"
)

HEADER = dedent("""\
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
        - ca/cpp_maximum_pensionable_earnings
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "a_header.yaml").write_text(HEADER)
    (parts / "b_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "c_line_b.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def line_b(tmp_path: Path, *artifacts: Artifact[int]) -> Decimal:
    worksheets = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *artifacts)
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_MAXIMUM_PENSIONABLE_EARNINGS).value


def test_line_b_is_71300_for_the_default_twelve_months(tmp_path: Path) -> None:
    assert line_b(tmp_path) == D("71300.00")


def test_line_b_is_71300_for_twelve_months_given(tmp_path: Path) -> None:
    assert line_b(tmp_path, Artifact(CPP_MONTHS, 12)) == D("71300.00")


def test_line_b_is_the_printed_row_for_fewer_months(tmp_path: Path) -> None:
    assert line_b(tmp_path, Artifact(CPP_MONTHS, 7)) == D("41591.67")
