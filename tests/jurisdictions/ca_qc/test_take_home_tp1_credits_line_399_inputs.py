"""TP-1 (2025) lines 390, 391, 392, 395, 396, 398 and 398.1: the lines that line 399 adds besides
lines 377.1, 389 and 397. The take-home gives none of them, so each is an optional input; a blank
is read as 0 by line 399.

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
from tests.manifest_support import input_named, inputs_of

PART = "tp1_credits_line_399_inputs.yaml"
PRINTED = {
    "390": (
        "Tax credit for volunteer firefighters and search and rescue volunteers",
        "Tax credit for volunteer firefighters and search and rescue volunteers. "
        "Specify: 390.1 + 390",
    ),
    "391": (
        "Tax credit for career extension",
        "Tax credit for career extension. Complete form TP-752.PC-V.",
    ),
    "392": (
        "Tax credit for recent graduates working in remote resource regions",
        "Tax credit for recent graduates working in remote resource regions. "
        "Complete form TP-776.1.ND-V.",
    ),
    "395": (
        "Tax credits for donations and gifts",
        "Tax credits for donations and gifts. Amount from line 1 of Work Chart 395",
    ),
    "396": ("Home buyers' tax credit", "Home buyers' tax credit. Complete form TP-752.HA-V."),
    "398": (
        "Tax credit for tuition or examination fees",
        "Tax credit for tuition or examination fees. Complete Schedule T.",
    ),
    "398.1": (
        "Tax credit for tuition or examination fees transferred by a child",
        "Tax credit for tuition or examination fees transferred by a child",
    ),
}
LINES = ("390", "391", "392", "395", "396", "398", "398.1")
NAMES = {line: f"ca-qc/tp1_line_{line.replace('.', '_')}" for line in LINES}
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/tp1_credits\n  required: true\n  exports:\n"
    + "".join(f"    - {name}\n" for name in NAMES.values())
    + "capabilities: []\n"
)


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_the_part_declares_exactly_the_seven_lines(
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
    assert (declaration.title, declaration.basis) == PRINTED[line]
    assert declaration.reference == line
    assert default is not None and default.is_blank


@pytest.mark.parametrize("line", LINES)
def test_the_input_kind_is_registered_and_non_negative(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is True
