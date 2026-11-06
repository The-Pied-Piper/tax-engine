"""Schedule 8 Part 2 line D, from the Ontario take-home manifest's own part file.

Line D "Your additional maximum pensionable earnings for 2025 (maximum $81,200)" is the row of the
monthly proration table for the months on line A. The part file is composed here under a
test-local header and form declaration (the real ones belong to the manifest's other parts), with
the line A input as the manifest declares it: optional, "12" when left out.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions import ca_on
from tax_engine.jurisdictions.ca.catalog import (
    CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_MONTHS,
)
from tax_engine.registrations import (
    JURISDICTIONS,
    artifact_kinds,
    capabilities,
    parameter_parsers,
)

ONTARIO = JurisdictionCode("CA-ON")
PART = Path(ca_on.__file__).parent / "manifests" / "take_home" / "schedule_8_line_d.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/cpp_months
    required: false
    default: "12"
    basis: Enter "12" on line A below unless any of the following conditions apply
outputs:
  - ca/cpp_months
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/cpp_additional_maximum_pensionable_earnings
"""


def line_d(tmp_path: Path, *starting: Artifact[int]) -> Decimal:
    manifest = tmp_path / "manifests" / "test"
    manifest.mkdir(parents=True)
    (manifest / "00_header.yaml").write_text(HEADER)
    (manifest / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, manifest / "02_line_d.yaml")
    service = TaxComputationService(
        YamlJurisdictionSource({ONTARIO.namespace: tmp_path}, artifact_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        capabilities(),
    )
    (worksheet,) = service.compute(ONTARIO, 2025, *starting)["ca/schedule_8"]
    return worksheet.get(CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS).value


def test_line_d_is_the_twelve_month_figure_when_line_a_is_left_out(tmp_path: Path) -> None:
    assert line_d(tmp_path) == Decimal("81200.00")


def test_line_d_is_the_row_for_the_months_on_line_a(tmp_path: Path) -> None:
    assert line_d(tmp_path, Artifact(CPP_MONTHS, 5)) == Decimal("33833.33")
