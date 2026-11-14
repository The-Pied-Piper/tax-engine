"""BC428 (2025) line 62's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC428, CRA 5010-C): "Line 62 and line 61510: British Columbia tax on split income
(complete Form T1206)". A caller with no split income leaves the line out, so the request is read
as blank (as Alberta's line 60), and the step that consumes line 62 reads that blank as 0. The form
prints no floor on this line, so the kind is not a non-negative amount.

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
from tax_engine.jurisdictions.ca_bc.catalog import BC428_TAX_ON_SPLIT_INCOME_LINE_62
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)

IDENTIFIER = "ca-bc/bc428_tax_on_split_income_line_62"
PRINTED_BASIS = "Line 62 and line 61510: British Columbia tax on split income (complete Form T1206)"
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc428_line_62_input.yaml"
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


def test_the_kind_is_in_the_british_columbia_catalog() -> None:
    assert BC428_TAX_ON_SPLIT_INCOME_LINE_62.identifier == IDENTIFIER
    assert british_columbia_kinds().kind(IDENTIFIER) is BC428_TAX_ON_SPLIT_INCOME_LINE_62


def test_the_part_declares_the_one_input_as_printed() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "British Columbia tax on split income",
            "reference": "62",
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


def test_a_request_that_leaves_out_line_62_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
