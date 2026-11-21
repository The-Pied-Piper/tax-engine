"""Worksheet NL428 (2025) line 58440's inputs, as the Newfoundland and Labrador part declares them.

Form text (Worksheet NL428, CRA 5001-d-25e.txt): "Line 58440 - Disability amount for self.
Complete this calculation if you were under 18 years of age on December 31, 2025." and "Line 3:
Total child care and attendant care expenses for you, claimed by you or another person". The first
is a yes or no answer, the shared count `ca/under_18_on_december_31`; the second is the shared
amount `ca/disability_self_care_expenses`. A salary-only caller leaves both out, so a request that
omits them is read as blank.

The real part is loaded under a test-local header, as the take-home header is another part's.
Newfoundland and Labrador is not yet listed in the registrations, so the source is built over the
Newfoundland and Labrador package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    DISABILITY_SELF_CARE_EXPENSES,
    UNDER_18_ON_DECEMBER_31,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)

PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
# The under-18 answer is the NL428 credits form's input; the care expenses (line 3) are the
# Worksheet NL428 form's own, in a part of their own.
INPUT_PARTS = (
    PARTS / "worksheet_nl428_line_58440_input.yaml",
    PARTS / "worksheet_nl428_line_3_input.yaml",
)
HEADER = """\
jurisdiction: CA-NL
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""
UNDER_18_TITLE = (
    "Disability amount for self (if you were under 18 years of age on December 31, 2025)"
)
UNDER_18_BASIS = "Complete this calculation if you were under 18 years of age on December 31, 2025."
CARE_TITLE = (
    "Total child care and attendant care expenses for you, claimed by you or another person"
)
CARE_BASIS = (
    "Line 3: Total child care and attendant care expenses for you, claimed by you or another person"
)


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    for number, part in enumerate(INPUT_PARTS):
        shutil.copy(part, folder / part.name)
        declared = yaml.safe_load(part.read_text(encoding="utf-8"))
        exports = "".join(f"    - {each['name']}\n" for each in declared["inputs"])
        (folder / f"form_{number}.yaml").write_text(
            f"form:\n  name: {declared['form']['name']}\n  required: true\n  exports:\n{exports}"
            "capabilities: []\n"
        )
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


@pytest.mark.parametrize(
    ("identifier", "title", "basis", "reference"),
    [
        (UNDER_18_ON_DECEMBER_31.identifier, UNDER_18_TITLE, UNDER_18_BASIS, "58440"),
        (DISABILITY_SELF_CARE_EXPENSES.identifier, CARE_TITLE, CARE_BASIS, "3"),
    ],
)
def test_a_request_that_leaves_out_the_input_is_read_as_blank(
    tmp_path: Path, identifier: str, title: str, basis: str, reference: str
) -> None:
    kinds = newfoundland_kinds()
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == basis
    assert declaration.title == title
    assert declaration.reference == reference
    assert default is not None and default.is_blank
