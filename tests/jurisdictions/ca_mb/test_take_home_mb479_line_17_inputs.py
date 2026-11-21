"""MB479 (2025) line 17's inputs, as the Manitoba take-home manifest part declares them.

Form MB479 (CRA 5007-TC, 5007-tc-25e.txt), the personal tax credit lines that line 17 adds: line 8,
line 12 (the printed sum of lines 9 to 11, whose own lines are not built) and line 13. Lines 14 to
16 are computed from their counts and have their own parts. A salary-only caller claims none of
them, so a request that leaves one out is read as blank.

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
    MB479_AGE_CREDIT_LINE_8,
    MB479_ELIGIBLE_DEPENDANT_CREDIT_LINE_13,
    MB479_SPOUSE_CREDITS_LINE_12,
)
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)
from tests.kinds import non_negative

PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / (
    "manifests/2025/mb479_line_17_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-MB
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""
# (kind, identifier, reference, printed title), in the order of the form.
LINES = [
    (
        MB479_AGE_CREDIT_LINE_8,
        "ca-mb/mb479_age_credit_line_8",
        "8",
        "Age credit for self (if you were born in 1960 or earlier)",
    ),
    (
        MB479_SPOUSE_CREDITS_LINE_12,
        "ca-mb/mb479_spouse_credits_line_12",
        "12",
        "Add lines 9 to 11.",
    ),
    (
        MB479_ELIGIBLE_DEPENDANT_CREDIT_LINE_13,
        "ca-mb/mb479_eligible_dependant_credit_line_13",
        "13",
        "Credit for an eligible dependant claimed on line 58160 of your Form MB428",
    ),
]


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(manitoba_packages().roots(), manitoba_kinds(), manitoba_units())
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_three_credit_inputs() -> None:
    part = _part()

    assert list(part) == ["inputs"]
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
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(manitoba_kinds().kind(identifier))

    assert not declaration.required
    assert declaration.basis == f"Line {reference}: {title}"
    assert default is not None and default.is_blank
