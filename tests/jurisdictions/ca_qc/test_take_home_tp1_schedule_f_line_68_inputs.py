"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, lines 41, 42, 43, 43.1, 44, 45, 60 and
62: the lines that line 68 adds ("Add lines 41 through 62") and that no other form owns (lines 46,
54, 56 and 58 copy TP-1 lines 245, 225, 231 and 234; line 41 stays an input because the printed line
excludes certain repayments that TP-1 line 246 includes). Each is an optional input a salary-only
caller does not give; line 68 reads a blank as 0.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`."""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.jurisdictions.ca_qc.tp1_schedule_f_support import LINE_68_INPUTS
from tests.kinds import non_negative
from tests.manifest_support import input_named, inputs_of

PART = "tp1_schedule_f_line_68_inputs.yaml"
NAMES = {line: f"ca-qc/tp1_schedule_f_line_{line}" for line in LINE_68_INPUTS}
BASES = {
    "41": ("Amounts you repaid in 2025 because you received an overpayment (line 246)"),
    "42": ("Deduction for a repayment of wage loss replacement benefits (line 207, point 12)"),
    "43": ("Amount from line 26 of Schedule R"),
    "43_1": (
        "Total of lines 101, 103 and 115 of Schedule U or, if you completed form LE-35-V, "
        "total of lines 112, 113 and 116 of that form"
    ),
    "44": (
        "Employment Insurance benefits to be repaid in your federal income tax return "
        "(line 250, point 3)"
    ),
    "45": ("Deductions claimed on line 250 (points 4, 5, 6, 11, 13, 14 and 15)"),
    "60": (
        "Deduction claimed on line 293, unless it was for the amount on line 16, 20, 25 or 28 above"
    ),
    "62": (
        "Deductions claimed on line 297, except those claimed for the amount on line 12 or 26 above"
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


@pytest.mark.parametrize("line", LINE_68_INPUTS)
def test_a_request_that_leaves_out_the_line_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path, line: str
) -> None:
    declaration = input_named(_manifest(take_home_service, tmp_path), NAMES[line])
    default = declaration.default_artifact(quebec_kinds().kind(NAMES[line]))

    assert not declaration.required
    assert declaration.title == BASES[line]
    assert declaration.basis == BASES[line]
    assert declaration.reference == line.replace("_", ".")
    assert default is not None and default.is_blank


@pytest.mark.parametrize("line", LINE_68_INPUTS)
def test_the_input_kind_is_registered_and_non_negative(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is True
