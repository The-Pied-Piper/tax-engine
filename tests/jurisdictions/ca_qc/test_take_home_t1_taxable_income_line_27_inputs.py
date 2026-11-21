"""5005-R (2025) lines 22 to 26 (net boxes 13500 to 14300): optional inputs
a salary-only caller does not give; each is read as 0 by the sum that adds it, so the
default is blank.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt).
The real part is loaded under a test-local header, as the Quebec header is another part's.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named, inputs_of

PART = "t1_taxable_income_line_27_inputs.yaml"
BASIS = {
    "13500": "Line 22: Business income: Line 13500: Net",
    "13700": "Line 23: Professional income Line 13700: Net",
    "13900": "Line 24: Commission income: Line 13900: Net",
    "14100": "Line 25: Farming income Line 14100: Net",
    "14300": "Line 26: Fishing income Line 14300: Net",
}
LINES = ("13500", "13700", "13900", "14100", "14300")
NAMES = {line: f"ca-qc/t1_line_{line}" for line in LINES}
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/t1_taxable_income\n  required: true\n  exports:\n"
    + "".join(f"    - {name}\n" for name in NAMES.values())
    + "capabilities: []\n"
)


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_the_part_declares_exactly_these_lines(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    inputs = inputs_of(_manifest(take_home_service, tmp_path))

    assert {name for name in inputs if name.startswith("ca-qc/t1_line_")} == set(NAMES.values())


@pytest.mark.parametrize("line", LINES)
def test_a_request_that_leaves_out_the_line_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path, line: str
) -> None:
    declaration = input_named(_manifest(take_home_service, tmp_path), NAMES[line])
    default = declaration.default_artifact(quebec_kinds().kind(NAMES[line]))

    assert not declaration.required
    assert declaration.basis == BASIS[line]
    assert declaration.reference == line
    assert default is not None and default.is_blank


@pytest.mark.parametrize("line", LINES)
def test_the_input_kind_is_registered_with_its_sign(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is False
