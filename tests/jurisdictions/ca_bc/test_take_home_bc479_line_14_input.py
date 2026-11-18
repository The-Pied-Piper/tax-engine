"""BC479 (2025) line 14's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC479, CRA 5010-TC): "Line 14: Enter your home renovation expenses from line 5 of
your Schedule BC(S12). (maximum $10,000) Line 60480 ^ multiplied by 10% = ^". Single amount, no
columns. The $10,000 maximum is stated in the basis; the check part (`bc479_line_14_check.yaml`)
rejects an amount above it, not this input. A request that leaves the line out is read as blank; the
step that consumes it reads blank as 0.

The real part is loaded under a test-local header over the British Columbia package list of
`support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_bc.catalog import BC479_HOME_RENOVATION_EXPENSES_LINE_14
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative

IDENTIFIER = BC479_HOME_RENOVATION_EXPENSES_LINE_14.identifier
PRINTED_TITLE = "Home renovation expenses from line 5 of your Schedule BC(S12)"
PRINTED_BASIS = (
    "Line 14: Enter your home renovation expenses from line 5 of your Schedule BC(S12). "
    "(maximum $10,000)"
)
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc479_line_14_input.yaml"
)
HEADER = """\
jurisdiction: CA-BC
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
    source = YamlJurisdictionSource(
        british_columbia_packages().roots(), british_columbia_kinds(), british_columbia_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_home_renovation_expenses_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": PRINTED_TITLE,
            "reference": "14",
            "unit": "ca/cad",
            "required": False,
            "default": None,
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


def test_the_home_renovation_expenses_line_14_is_a_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-bc/bc479_home_renovation_expenses_line_14"
    assert kind is BC479_HOME_RENOVATION_EXPENSES_LINE_14
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_14_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
