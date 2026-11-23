"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 24: the line that line 25 takes off
line 23 ("Subtract line 24 from line 23"). It is an optional input a salary-only caller does not
give; line 25 reads a blank as 0. Line 23 is a copy of TP-1 line 128, so it is not an input here.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`."""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.jurisdictions.ca_qc.tp1_schedule_f_support import LINE_25_INPUTS
from tests.kinds import non_negative
from tests.manifest_support import input_named, inputs_of

PART = "tp1_schedule_f_line_25_inputs.yaml"
NAMES = {line: f"ca-qc/tp1_schedule_f_line_{line}" for line in LINE_25_INPUTS}
BASES = {
    "24": (
        "Dividends from taxable Canadian corporations, actual amount (total of lines 166 and 167)"
    ),
}
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/tp1_schedule_f\n  required: true\n  exports:\n"
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
    inputs = inputs_of(_manifest(take_home_service, tmp_path))

    assert set(inputs) == set(NAMES.values())


@pytest.mark.parametrize("line", LINE_25_INPUTS)
def test_a_request_that_leaves_out_the_line_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path, line: str
) -> None:
    declaration = input_named(_manifest(take_home_service, tmp_path), NAMES[line])
    default = declaration.default_artifact(quebec_kinds().kind(NAMES[line]))

    assert not declaration.required
    assert declaration.title == BASES[line]
    assert declaration.basis == BASES[line]
    assert declaration.reference == line
    assert default is not None and default.is_blank


@pytest.mark.parametrize("line", LINE_25_INPUTS)
def test_the_input_kind_is_registered_and_non_negative(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is True
