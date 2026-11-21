"""5005-R (2025) line 46800 (supplies expenses): optional inputs
a salary-only caller does not give; a blank is "0" before the maximum and the 25%.

Form text (CRA 5005-R page 8, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt).
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

PART = "t1_tax_and_credits_line_46900_inputs.yaml"
BASIS = {
    "46800": (
        "Line 167 and line 46900: Eligible educator school supply tax credit Supplies "
        "expenses (maximum $1,000) Line 46800"
    ),
}
LINES = tuple(BASIS)
NAMES = {line: f"ca-qc/t1_line_{line}" for line in LINES}
HEADER = f"""\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: [{", ".join(NAMES.values())}]
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/t1_tax_and_credits\n  required: true\n  exports:\n"
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
    inputs = _manifest(take_home_service, tmp_path).inputs

    assert {name for name in inputs if name.startswith("ca-qc/t1_line_")} == set(NAMES.values())


@pytest.mark.parametrize("line", LINES)
def test_a_request_that_leaves_out_the_line_is_read_as_zero(
    take_home_service: TakeHomeService, tmp_path: Path, line: str
) -> None:
    declaration = _manifest(take_home_service, tmp_path).inputs[NAMES[line]]
    default = declaration.default_artifact(quebec_kinds().kind(NAMES[line]))

    assert not declaration.required
    assert declaration.basis == BASIS[line]
    assert declaration.reference == line
    assert default is not None and default.value == 0


@pytest.mark.parametrize("line", LINES)
def test_the_input_kind_is_registered_with_its_sign(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is True
