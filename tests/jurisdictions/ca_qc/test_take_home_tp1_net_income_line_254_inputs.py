"""TP-1 (2025) lines 205, 207, 214, 215, 225, 228, 231, 234, 236, 241, 245, 246, 250 and 252: the
lines that line 254 adds besides lines 201 and 248. The take-home gives none of them, so each is an
optional input; a blank is read as 0 by line 254. Lines 225, 231, 234, 245 and 246 are printed as
deductions the filer enters as positive amounts, so a negative is refused at entry; the other nine
lines print no sign rule and stay signed.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named, inputs_of

PART = "tp1_net_income_line_254_inputs.yaml"
LINES = (
    "205",
    "207",
    "214",
    "215",
    "225",
    "228",
    "231",
    "234",
    "236",
    "241",
    "245",
    "246",
    "250",
    "252",
)
# The deductions the printed form has the filer enter as positive amounts: line 225 "Support
# payments made (deductible amount)", 231 "Carrying charges and interest expenses", 234 "Business
# investment loss ... Allowable loss", 245 "Complete Schedule Q" and 246 "Deduction for a repayment
# of amounts overpaid to you" (TP-1.D-V, 2025-12, page 3); none prints a negative.
NON_NEGATIVE_LINES = ("225", "231", "234", "245", "246")
SIGNED_LINES = tuple(line for line in LINES if line not in NON_NEGATIVE_LINES)
NAMES = {line: f"ca-qc/tp1_line_{line.replace('.', '_')}" for line in LINES}
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/tp1_net_income\n  required: true\n  exports:\n"
    + "".join(f"    - {name}\n" for name in NAMES.values())
    + "capabilities: []\n"
)


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_the_part_declares_exactly_the_fourteen_lines(
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
    assert declaration.basis
    assert declaration.reference == line
    assert default is not None and default.is_blank


@pytest.mark.parametrize("line", SIGNED_LINES)
def test_the_input_kind_is_registered_and_signed(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is False


@pytest.mark.parametrize("line", NON_NEGATIVE_LINES)
def test_a_negative_amount_is_refused_at_entry(line: str) -> None:
    kind = quebec_kinds().kind(NAMES[line])

    assert non_negative(kind) is True
    with pytest.raises(NegativeArtifactError, match=rf"{NAMES[line]}.*-1"):
        Artifact(kind, Decimal("-1"))
