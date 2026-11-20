"""TP-1 (2025) line 425, "Add lines 414 through 424": the printed sum of lines 414 to 424, an
optional input a salary-only caller does not give. A blank is read as 0 by line 430.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`."""

from __future__ import annotations

from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative

PART = "tp1_tax_line_425_input.yaml"
NAME = "ca-qc/tp1_line_425"
PRINTED_BASIS = "Add lines 414 through 424."
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: [ca-qc/tp1_line_425]
capabilities: []
"""
FORM = """\
form:
  name: ca-qc/tp1_tax
  required: true
  exports:
    - ca-qc/tp1_line_425
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_a_request_that_leaves_out_line_425_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    declaration = _manifest(take_home_service, tmp_path).inputs[NAME]
    default = declaration.default_artifact(quebec_kinds().kind(NAME))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.reference == "425"
    assert default is not None and default.is_blank


def test_the_line_425_input_kind_is_registered_and_non_negative() -> None:
    assert non_negative(quebec_kinds().kind(NAME)) is True
