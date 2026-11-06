"""Schedule 8 Part 3 line 7, from the Ontario take-home manifest's own part file.

Line 7 "Line 5 minus line 6 (if negative, enter "0") (maximum $67,800)": line 6 is "Amount from line
E of Part 2" (a copy, so line 7 reads line E's figure). The part file is composed here under a
test-local header and form declaration (the real ones belong to the manifest's other parts), with
line 5 and line E given as starting amounts because their own parts are other tickets'.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions import ca_on
from tax_engine.jurisdictions.ca.catalog import (
    CPP_BASIC_EXEMPTION,
    CPP_PART_3_LINE_5,
    CPP_PART_3_LINE_7,
)
from tax_engine.registrations import (
    JURISDICTIONS,
    artifact_kinds,
    capabilities,
    parameter_parsers,
)

ONTARIO = JurisdictionCode("CA-ON")
PART = Path(ca_on.__file__).parent / "manifests" / "take_home" / "schedule_8_line_7.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/cpp_part_3_line_5
    required: true
  - name: ca/cpp_basic_exemption
    required: true
outputs:
  - ca/cpp_part_3_line_5
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/cpp_part_3_line_7
"""


def line_7(tmp_path: Path, line_5: str, line_e: str) -> Decimal:
    manifest = tmp_path / "manifests" / "test"
    manifest.mkdir(parents=True)
    (manifest / "00_header.yaml").write_text(HEADER)
    (manifest / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, manifest / "02_line_7.yaml")
    service = TaxComputationService(
        YamlJurisdictionSource({ONTARIO.namespace: tmp_path}, artifact_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        capabilities(),
    )
    (worksheet,) = service.compute(
        ONTARIO,
        2025,
        Artifact(CPP_PART_3_LINE_5, Decimal(line_5)),
        Artifact(CPP_BASIC_EXEMPTION, Decimal(line_e)),
    )["ca/schedule_8"]
    return worksheet.get(CPP_PART_3_LINE_7).value


@pytest.mark.parametrize(
    ("line_5", "line_e", "expected"),
    [
        # The ticket's $70,000 salary: line 5 is 70,000 and line E is 3,500 at 12 months.
        ("70000.00", "3500.00", "66500.00"),
        # $90,000: line 5 is 71,300, so 71,300 - 3,500 is exactly the printed maximum.
        ("71300.00", "3500.00", "67800.00"),
        # The difference above the maximum is the maximum: line E of a 7-month year.
        ("71300.00", "2041.67", "67800.00"),
        # A line 5 equal to line E and one below it are both "0".
        ("3500.00", "3500.00", "0.00"),
        ("3499.99", "3500.00", "0.00"),
        # A cent over line E is a cent.
        ("3500.01", "3500.00", "0.01"),
    ],
)
def test_line_7_is_line_5_less_line_e_between_zero_and_the_maximum(
    tmp_path: Path, line_5: str, line_e: str, expected: str
) -> None:
    assert line_7(tmp_path, line_5, line_e) == Decimal(expected)
