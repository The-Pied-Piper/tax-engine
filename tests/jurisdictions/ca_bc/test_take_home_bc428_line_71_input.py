"""BC428 (2025) line 71's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC428, CRA 5010-C): "Line 71: Provincial foreign tax credit (complete Form T2036)".
Form T2036 is not built. A salary-only caller has no provincial foreign tax credit, so a request
that leaves the line out is read as blank, and the step that consumes it reads that blank as 0.

British Columbia is not yet listed in the registrations, so the real part is loaded under a
test-local header over the British Columbia package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_bc.catalog import BC428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_71
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative

IDENTIFIER = BC428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_71.identifier
PRINTED_BASIS = "Line 71: Provincial foreign tax credit (complete Form T2036)"
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc428_line_71_input.yaml"
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


def test_the_part_declares_only_the_provincial_foreign_tax_credit_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Provincial foreign tax credit",
            "reference": "71",
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


def test_the_provincial_foreign_tax_credit_line_71_is_a_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-bc/bc428_provincial_foreign_tax_credit_line_71"
    assert kind is BC428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_71
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_71_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
