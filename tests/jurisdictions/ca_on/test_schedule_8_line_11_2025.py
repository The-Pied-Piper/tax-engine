"""Schedule 8 Part 3 line 11, from the Ontario take-home manifest's own part file.

Line 11 "amount from line 7 multiplied by 4.95% (maximum $3,356.10)". The part file is composed
here under a test-local header and form declaration (the real ones belong to the manifest's other
parts), with line 7 given as a starting amount because its own part is another ticket's.
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
from tax_engine.jurisdictions.ca.catalog import CPP_PART_3_LINE_7, CPP_PART_3_LINE_11
from tax_engine.registrations import (
    JURISDICTIONS,
    artifact_kinds,
    capabilities,
    parameter_parsers,
)

ONTARIO = JurisdictionCode("CA-ON")
PART = Path(ca_on.__file__).parent / "manifests" / "take_home" / "schedule_8_line_11.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/cpp_part_3_line_7
    required: true
outputs:
  - ca/cpp_part_3_line_7
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/cpp_part_3_line_11
"""


def line_11(tmp_path: Path, line_7: str) -> Decimal:
    manifest = tmp_path / "manifests" / "test"
    manifest.mkdir(parents=True)
    (manifest / "00_header.yaml").write_text(HEADER)
    (manifest / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, manifest / "02_line_11.yaml")
    service = TaxComputationService(
        YamlJurisdictionSource({ONTARIO.namespace: tmp_path}, artifact_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        capabilities(),
    )
    (worksheet,) = service.compute(ONTARIO, 2025, Artifact(CPP_PART_3_LINE_7, Decimal(line_7)))[
        "ca/schedule_8"
    ]
    return worksheet.get(CPP_PART_3_LINE_11).value


@pytest.mark.parametrize(
    ("line_7", "expected"),
    [
        # The ticket's $70,000 salary: line 7 is 66,500, and 66,500 x 4.95% is 3,291.75.
        ("66500.00", "3291.75"),
        # $90,000: line 7 is the printed maximum 67,800, and 67,800 x 4.95% is 3,356.10.
        ("67800.00", "3356.10"),
        # Above the printed maximum is capped at line 11's "(maximum $3,356.10)".
        ("70000.00", "3356.10"),
        ("0.00", "0.00"),
        # Rounded half-up to the cent: 4.95% of 0.10 is 0.00495, of 0.30 is 0.01485.
        ("0.10", "0.00"),
        ("0.30", "0.01"),
    ],
)
def test_line_11_is_line_7_at_4_95_percent_up_to_the_maximum(
    tmp_path: Path, line_7: str, expected: str
) -> None:
    assert line_11(tmp_path, line_7) == Decimal(expected)
