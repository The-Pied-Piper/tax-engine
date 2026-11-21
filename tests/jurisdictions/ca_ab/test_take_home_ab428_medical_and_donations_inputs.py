"""AB428 (2025) inputs of the medical expenses (lines 44 and 50) and donations (lines 55 and 56)
blocks, as the Alberta take-home manifest parts declare them.

Form text (Form AB428, CRA 5009-c-25e.txt): line 44 "Line 44 and line 58689: Amount from line
33099 of your return", line 50 "Line 50 and line 58729: Allowable amount of medical expenses for
other dependants (use Worksheet AB428)", line 55 "Line 55: Amount from line 13 of your federal
Schedule 9 multiplied by 60% =" and line 56 "Line 56: Amount from line 14 of your federal Schedule 9
multiplied by 21% =". Each part declares the one amount the form takes from the filer; a salary-only
caller has none, so a request that leaves it out is read as blank.

The real part is loaded under a test-local header, as the take-home header is another part's. The
Alberta registries of `support.py` are used.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
HEADER = """\
jurisdiction: CA-AB
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""
# part file, input, title, reference, printed basis
CASES = [
    (
        "ab428_credits_line_44_input.yaml",
        "ca-ab/ab428_medical_expenses_line_44",
        "Amount from line 33099 of your return",
        "44",
        "Line 44 and line 58689: Amount from line 33099 of your return",
    ),
    (
        "ab428_credits_line_50_input.yaml",
        "ca-ab/ab428_allowable_medical_expenses_for_other_dependants_line_50",
        "Allowable amount of medical expenses for other dependants (use Worksheet AB428)",
        "50",
        "Line 50 and line 58729: Allowable amount of medical expenses for other dependants "
        "(use Worksheet AB428)",
    ),
    (
        "ab428_credits_line_55_input.yaml",
        "ca-ab/ab428_donations_amount_line_55",
        "Amount from line 13 of your federal Schedule 9",
        "55 box A",
        "Line 55: Amount from line 13 of your federal Schedule 9",
    ),
    (
        "ab428_credits_line_56_input.yaml",
        "ca-ab/ab428_donations_amount_line_56",
        "Amount from line 14 of your federal Schedule 9",
        "56 box A",
        "Line 56: Amount from line 14 of your federal Schedule 9",
    ),
]


def _manifest(tmp_path: Path, part: str) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PARTS / part, folder / part)
    source = YamlJurisdictionSource(alberta_packages().roots(), alberta_kinds(), alberta_units())
    return source.load(folder)


@pytest.mark.parametrize(("part", "identifier", "title", "reference", "basis"), CASES)
def test_the_part_declares_the_one_optional_input_as_printed(
    tmp_path: Path, part: str, identifier: str, title: str, reference: str, basis: str
) -> None:
    manifest = _manifest(tmp_path, part)

    assert list(manifest.inputs) == [identifier]
    declaration = manifest.inputs[identifier]
    assert not declaration.required
    assert declaration.basis == basis
    assert declaration.title == title
    assert declaration.reference == reference
    assert declaration.unit == "ca/cad"


@pytest.mark.parametrize(("part", "identifier", "title", "reference", "basis"), CASES)
def test_a_request_that_leaves_the_line_out_is_read_as_blank(
    tmp_path: Path, part: str, identifier: str, title: str, reference: str, basis: str
) -> None:
    declaration = _manifest(tmp_path, part).inputs[identifier]
    default = declaration.default_artifact(alberta_kinds().kind(identifier))

    assert default is not None and default.is_blank
