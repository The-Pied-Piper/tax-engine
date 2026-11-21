"""MB479 (2025) lines 9, 10 and 11's inputs, as the Manitoba take-home manifest part declares them.

Form MB479 (CRA 5007-TC, 5007-tc-25e.txt): "Line 9: Basic credit for spouse or common-law partner
Claim $195", "Line 10: Age credit for spouse or common-law partner (if they were born in 1960 or
earlier) Claim $113", "Line 11: Disability credit for spouse or common-law partner Claim $113".
Each is the credit claimed. A salary-only caller claims none of them, so a request that leaves one
out is read as blank, and the step of line 12 reads each blank as 0.

The real part is loaded under a test-local header over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_mb.catalog import (
    MB479_AGE_CREDIT_SPOUSE_LINE_10,
    MB479_BASIC_CREDIT_SPOUSE_LINE_9,
    MB479_DISABILITY_CREDIT_SPOUSE_LINE_11,
)
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / (
    "manifests/2025/mb479_line_12_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-MB
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
# (kind, identifier, reference, printed title), in the order of the form.
LINES = [
    (
        MB479_BASIC_CREDIT_SPOUSE_LINE_9,
        "ca-mb/mb479_basic_credit_spouse_line_9",
        "9",
        "Basic credit for spouse or common-law partner",
    ),
    (
        MB479_AGE_CREDIT_SPOUSE_LINE_10,
        "ca-mb/mb479_age_credit_spouse_line_10",
        "10",
        "Age credit for spouse or common-law partner (if they were born in 1960 or earlier)",
    ),
    (
        MB479_DISABILITY_CREDIT_SPOUSE_LINE_11,
        "ca-mb/mb479_disability_credit_spouse_line_11",
        "11",
        "Disability credit for spouse or common-law partner",
    ),
]

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


def test_the_part_declares_only_the_three_spouse_credit_inputs() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-mb/mb479"}
    assert part["inputs"] == [
        {
            "name": identifier,
            "title": title,
            "reference": reference,
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": f"Line {reference}: {title}",
        }
        for _, identifier, reference, title in LINES
    ]
    for declared in part["inputs"]:
        assert list(declared) == [
            "name",
            "title",
            "reference",
            "unit",
            "required",
            "default",
            "basis",
        ]


@pytest.mark.parametrize(("constant", "identifier", "reference", "title"), LINES)
def test_each_credit_is_a_non_negative_amount_kind(
    constant: Any, identifier: str, reference: str, title: str
) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert constant.identifier == identifier
    assert kind is constant
    assert non_negative(kind)


@pytest.mark.parametrize(("constant", "identifier", "reference", "title"), LINES)
def test_a_request_that_leaves_out_a_credit_is_read_as_blank(
    tmp_path: Path, constant: Any, identifier: str, reference: str, title: str
) -> None:
    declaration = input_named(_manifest(tmp_path), identifier)
    default = declaration.default_artifact(manitoba_kinds().kind(identifier))

    assert not declaration.required
    assert declaration.basis == f"Line {reference}: {title}"
    assert default is not None and default.is_blank
