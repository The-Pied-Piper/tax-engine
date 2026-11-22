"""TP-1 (2025) lines 451.2, 451.3, 452 to 455, 458 to 460, 462 and 463: the lines that line 465 adds
besides line 456. The take-home gives none of them, so each is an optional input; a blank is read as
0 by line 465. The real part is loaded under a test-local header and form declaration over the
Quebec package list of `support.py`."""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named, inputs_of

PART = "tp1_totals_line_465_inputs.yaml"
PRINTED_BASIS = "Add lines 451.2 through 463."
LINES = (
    "451.2",
    "451.3",
    "452",
    "453",
    "454",
    "455",
    "458",
    "459",
    "460",
    "462",
    "463",
)
NAMES = {line: f"ca-qc/tp1_line_{line.replace('.', '_')}" for line in LINES}
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/tp1_totals\n  required: true\n  exports:\n"
    + "".join(f"    - {name}\n" for name in NAMES.values())
    + "capabilities: []\n"
)


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_the_part_declares_exactly_the_11_lines(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    inputs = inputs_of(_manifest(take_home_service, tmp_path))

    assert {name for name in inputs if name.startswith("ca-qc/tp1_line_")} == set(NAMES.values())


@pytest.mark.parametrize("line", LINES)
def test_a_request_that_leaves_out_the_line_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path, line: str
) -> None:
    declaration = input_named(_manifest(take_home_service, tmp_path), NAMES[line])
    default = declaration.default_artifact(quebec_kinds().kind(NAMES[line]))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.reference == line
    assert default is not None and default.is_blank


@pytest.mark.parametrize("line", LINES)
def test_the_input_kind_is_registered_and_non_negative(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is True
