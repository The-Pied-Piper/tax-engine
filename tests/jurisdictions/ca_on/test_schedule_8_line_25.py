"""Schedule 8 Part 3a line 25, from the Ontario take-home manifest's own part file.

Line 25 "Enter the amount from line 15", and line 15 is the amount from line 11. The part file is
composed here under a test-local header and form declaration (the real ones belong to the
manifest's other parts), with line 11 given as a starting amount because its own part is another
ticket's.
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
    CPP_PART_3_LINE_11,
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
)
from tax_engine.registrations import (
    JURISDICTIONS,
    artifact_kinds,
    capabilities,
    parameter_parsers,
)

ONTARIO = JurisdictionCode("CA-ON")
PART = Path(ca_on.__file__).parent / "manifests" / "take_home" / "schedule_8_line_25.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/cpp_part_3_line_11
    required: true
outputs:
  - ca/cpp_part_3_line_11
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/schedule_8_cpp_base_contributions_on_return
"""


def line_25(tmp_path: Path, line_11: str) -> Decimal:
    manifest = tmp_path / "manifests" / "test"
    manifest.mkdir(parents=True)
    (manifest / "00_header.yaml").write_text(HEADER)
    (manifest / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, manifest / "02_line_25.yaml")
    service = TaxComputationService(
        YamlJurisdictionSource({ONTARIO.namespace: tmp_path}, artifact_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        capabilities(),
    )
    (worksheet,) = service.compute(ONTARIO, 2025, Artifact(CPP_PART_3_LINE_11, Decimal(line_11)))[
        "ca/schedule_8"
    ]
    return worksheet.get(SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value


@pytest.mark.parametrize(
    "line_11",
    [
        # The ticket's $70,000 salary: line 11 is 3,291.75.
        "3291.75",
        # $90,000, above the $81,200 ceiling: line 11 is the printed maximum 3,356.10.
        "3356.10",
        "0.00",
        "0.01",
    ],
)
def test_line_25_is_the_amount_from_line_11(tmp_path: Path, line_11: str) -> None:
    assert line_25(tmp_path, line_11) == Decimal(line_11)
