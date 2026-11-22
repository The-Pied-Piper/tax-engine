"""5005-R (2025) lines 29 to 31 (14400 to 14600): optional inputs
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
from tests.manifest_support import input_named, inputs_of

PART = "t1_taxable_income_line_32_inputs.yaml"
BASIS = {
    "14400": "Line 29 and line 14400: Workers' compensation benefits (box 10 of the T5007 slip)",
    "14500": "Line 30 and line 14500: Social assistance payments",
    "14600": "Line 31 and line 14600: Net federal supplements paid (box 21 of the T4A(OAS) slip)",
}
LINES = ("14400", "14500", "14600")
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
