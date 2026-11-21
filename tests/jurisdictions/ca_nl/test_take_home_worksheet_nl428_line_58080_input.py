"""Worksheet NL428 (2025) line 58080's input, as the Newfoundland and Labrador part declares it.

Form text (Worksheet NL428, CRA 5001-d-25e.txt): "Line 58080 - Age amount(if you were born in 1960
or earlier)". A salary-only caller need not say whether they were born in 1960 or earlier, so a
request that leaves the question out is read as blank.

The real part is loaded under a test-local header, as the take-home header is another part's.
Newfoundland and Labrador is not yet listed in the registrations, so the source is built over the
Newfoundland and Labrador package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BORN_IN_1960_OR_EARLIER
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)

PRINTED_BASIS = "Line 58080 - Age amount (if you were born in 1960 or earlier)"
PRINTED_TITLE = "Age amount (if you were born in 1960 or earlier)"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/worksheet_nl428_line_58080_input.yaml"
)
HEADER = """\
jurisdiction: CA-NL
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    declared = yaml.safe_load(PART.read_text(encoding="utf-8"))
    exports = "".join(f"    - {each['name']}\n" for each in declared["inputs"])
    (folder / "form.yaml").write_text(
        f"form:\n  name: {declared['form']['name']}\n  required: true\n  exports:\n{exports}"
        "capabilities: []\n"
    )
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def test_a_request_that_leaves_out_line_58080_is_read_as_blank(tmp_path: Path) -> None:
    kinds = newfoundland_kinds()
    identifier = BORN_IN_1960_OR_EARLIER.identifier
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.title == PRINTED_TITLE
    assert declaration.reference == "58080"
    assert default is not None and default.is_blank
