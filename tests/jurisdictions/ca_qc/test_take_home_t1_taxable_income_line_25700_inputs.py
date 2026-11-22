"""5005-R (2025) lines 59 to 68 (lines 24400 to 25600): optional inputs
a salary-only caller does not give;
each is read as 0 by the sum that adds it, so the default is blank.

Form text (CRA 5005-R page 5, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt).
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
from tests.manifest_support import input_named, inputs_of

PART = "t1_taxable_income_line_25700_inputs.yaml"
BASIS = {
    "24400": (
        "Line 59 and line 24400: Canadian Armed Forces personnel and police deduction "
        "(box 43 of all T4 slips)"
    ),
    "24900": (
        "Line 60 and line 24900: Security options deductions (boxes 39, 41, 91 and 92 of "
        "all T4 slips or see Form T1212)"
    ),
    "25000": (
        "Line 61 and line 25000: Other payments deduction (enter the amount from line "
        "14700 if you did not enter an amount on line 14600; otherwise, use Federal "
        "Worksheet)"
    ),
    "25100": "Line 62 and line 25100: Limited partnership losses of other years",
    "25200": "Line 63 and line 25200: Non-capital losses of other years",
    "25300": "Line 64 and line 25300: Net capital losses of other years",
    "25395": (
        "Line 65 and line 25395: Capital gains deduction for qualifying business "
        "transfers or qualifying cooperative conversions (complete Form T2048)"
    ),
    "25400": "Line 66 and line 25400: Capital gains deduction (complete Form T657)",
    "25500": "Line 67 and line 25500: Northern residents deductions (complete Form T2222)",
    "25600": "Line 68 and line 25600: Additional deductions (specify):",
}
LINES = tuple(BASIS)
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


@pytest.mark.parametrize("line", LINES)
def test_the_input_kind_is_registered_with_its_sign(line: str) -> None:
    assert non_negative(quebec_kinds().kind(NAMES[line])) is True
