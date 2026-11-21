"""TP-1 (2025) lines 415, 422 and 424: the inputs of the lines that line 425 adds ("Add lines 414
through 424."; line 414 is computed from Work Chart 414, not an input). Each is an optional input a
salary-only caller does not give; line 425 reads a blank as 0.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`."""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative

PART = "tp1_tax_line_425_inputs.yaml"
LINES = ("415", "422", "424")
NAMES = {line: f"ca-qc/tp1_line_{line}" for line in LINES}
BASES = {
    "415": "Dividend tax credit",
    "422": "Tax credit for the acquisition of Capital régional et coopératif Desjardins shares",
    "424": "Tax credit for a labour-sponsored fund",
}
HEADER = f"""\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: [{", ".join(NAMES.values())}]
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/tp1_tax\n  required: true\n  exports:\n"
    + "".join(f"    - {name}\n" for name in NAMES.values())
    + "capabilities: []\n"
)


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_the_part_declares_exactly_the_printed_lines(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    inputs = _manifest(take_home_service, tmp_path).inputs

    assert {name for name in inputs if name.startswith("ca-qc/tp1_line_")} == set(NAMES.values())


@pytest.mark.parametrize("line", LINES)
def test_a_request_that_leaves_out_the_line_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path, line: str
) -> None:
    declaration = _manifest(take_home_service, tmp_path).inputs[NAMES[line]]
    default = declaration.default_artifact(quebec_kinds().kind(NAMES[line]))

    assert not declaration.required
    assert declaration.title == BASES[line]
    assert declaration.basis == BASES[line]
    assert declaration.reference == line
    assert default is not None and default.is_blank


@pytest.mark.parametrize("line", LINES)
def test_the_input_kind_is_registered_and_non_negative(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is True
