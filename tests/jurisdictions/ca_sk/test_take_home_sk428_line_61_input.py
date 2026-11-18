"""SK428 (2025) line 61's input, as the Saskatchewan take-home manifest part declares it.

Form SK428 (CRA 5008-C), line 61, as printed on the form. A salary-only caller has no tax on split
income, so a request that leaves the line out is read as blank.

The real part is loaded under a test-local header over the Saskatchewan package list of
`support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_sk.catalog import SK428_TAX_ON_SPLIT_INCOME_LINE_61
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_units,
)

IDENTIFIER = SK428_TAX_ON_SPLIT_INCOME_LINE_61.identifier
PRINTED_BASIS = "Line 61 and line 61510: Saskatchewan tax on split income (complete Form T1206)"
PART = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / (
    "manifests/2025/sk428_line_61_input.yaml"
)
HEADER = """\
jurisdiction: CA-SK
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
        saskatchewan_packages().roots(), saskatchewan_kinds(), saskatchewan_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_tax_on_split_income_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Saskatchewan tax on split income",
            "reference": "61",
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


def test_the_tax_on_split_income_line_61_is_an_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-sk/sk428_tax_on_split_income_line_61"
    assert kind is SK428_TAX_ON_SPLIT_INCOME_LINE_61


def test_a_request_that_leaves_out_line_61_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(saskatchewan_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
