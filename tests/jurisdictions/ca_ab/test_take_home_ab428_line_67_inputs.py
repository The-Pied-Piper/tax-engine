"""AB428 (2025) line 67's input, as the Alberta take-home manifest part declares it.

Form text (AB428, CRA 5009-c-25e.txt in docs/cra-forms-2025): "Alberta additional tax for minimum
tax purposes: Line 67: Form T691: line 1 minus line 2 of Part 7 ^ multiplied by 35% = ^" is the
line's printed text; the part takes the text before the ^ marker as its basis. The form prints no
floor, so the kind is not non_negative. A caller with no minimum tax to report leaves the line out,
so the request is read as blank (the $20,000, $70,000 and $200,000 figures of the ticket are 0.00,
a blank line).

The real part is loaded under a test-local header, as the Alberta manifest cannot be built yet.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_ab.catalog import AB428_MINIMUM_TAX_T691_AMOUNT_LINE_67
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

IDENTIFIER = "ca-ab/ab428_minimum_tax_t691_amount_line_67"
PRINTED_BASIS = "Line 67: Form T691: line 1 minus line 2 of Part 7"
PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / (
    "manifests/2025/ab428_line_67_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-AB
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
    source = YamlJurisdictionSource(alberta_packages().roots(), alberta_kinds(), alberta_units())
    return source.load(folder)


def test_the_kind_is_in_the_alberta_catalog() -> None:
    assert AB428_MINIMUM_TAX_T691_AMOUNT_LINE_67.identifier == IDENTIFIER
    assert alberta_kinds().kind(IDENTIFIER) is AB428_MINIMUM_TAX_T691_AMOUNT_LINE_67


def test_the_part_declares_the_one_input_as_printed() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Alberta additional tax for minimum tax purposes",
            "reference": "67 box A",
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


def test_a_request_that_leaves_out_line_67_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(alberta_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
