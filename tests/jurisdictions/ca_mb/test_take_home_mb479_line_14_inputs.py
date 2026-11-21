"""MB479 (2025) line 14's input, as the Manitoba take-home manifest part declares it.

Form MB479 (CRA 5007-tc-25e.txt), line 14, as printed on the form:
"Line 14: Number of disability claims".

A salary-only caller has no such claim, so a request that leaves the line out is read as 0,
and the step that reads it multiplies it.

The real part is loaded under a test-local header over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_mb.catalog import MB479_DISABILITY_CLAIMS_NUMBER_LINE_14
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)
from tests.kinds import non_negative

IDENTIFIER = MB479_DISABILITY_CLAIMS_NUMBER_LINE_14.identifier
PRINTED_BASIS = (
    "Disability credit for self or for a dependant other than your spouse or common-law partner. "
    "Line 14: Number of disability claims"
)
PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / (
    "manifests/2025/mb479_line_14_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-MB
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""

FORM = """\
form:
  name: ca-mb/mb479
  required: true
  exports:
    - ca/total_income
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(FORM)
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(manitoba_packages().roots(), manitoba_kinds(), manitoba_units())
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_line_14_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-mb/mb479"}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Number of disability claims",
            "reference": "14 box A",
            "unit": "ca/cad",
            "required": False,
            "default": "0",
            "basis": PRINTED_BASIS,
        }
    ]
    assert list(part["inputs"][0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]


def test_the_line_14_input_is_a_non_negative_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-mb/mb479_disability_claims_number_line_14"
    assert kind is MB479_DISABILITY_CLAIMS_NUMBER_LINE_14
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_14_is_read_as_0(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(manitoba_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.value == Decimal("0")
