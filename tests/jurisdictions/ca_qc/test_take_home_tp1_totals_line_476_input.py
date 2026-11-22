"""TP-1 (2025) line 476, "Refund transferred to your spouse": an optional input a single filer does
not give. A blank is read as 0 by line 478.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`."""

from __future__ import annotations

from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named

PART = "tp1_totals_line_476_input.yaml"
NAME = "ca-qc/tp1_refund_transferred_to_spouse_line_476"
PRINTED_BASIS = "Refund transferred to your spouse"
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = """\
form:
  name: ca-qc/tp1_totals
  required: true
  exports:
    - ca-qc/tp1_refund_transferred_to_spouse_line_476
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_a_request_that_leaves_out_line_476_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    declaration = input_named(_manifest(take_home_service, tmp_path), NAME)
    default = declaration.default_artifact(quebec_kinds().kind(NAME))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.reference == "476"
    assert declaration.title == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_line_476_input_kind_is_registered_and_non_negative() -> None:
    assert non_negative(quebec_kinds().kind(NAME)) is True
