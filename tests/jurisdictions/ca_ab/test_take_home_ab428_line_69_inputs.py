"""AB428 (2025) line 69's input, as the Alberta take-home manifest part declares it.

Form text (AB428, CRA 5009-c-25e.txt in cra-docs/docs/cra-forms-2025): "Line 69: Provincial foreign
tax
credit (complete Form T2036)" is the line's basis in the part. A caller with no provincial foreign
tax credit leaves the line out, so the request is read as blank.

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
from tax_engine.jurisdictions.ca_ab.catalog import AB428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_69
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

IDENTIFIER = "ca-ab/ab428_provincial_foreign_tax_credit_line_69"
PRINTED_BASIS = "Line 69: Provincial foreign tax credit (complete Form T2036)"
PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / (
    "manifests/2025/ab428_line_69_inputs.yaml"
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
    assert AB428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_69.identifier == IDENTIFIER
    assert alberta_kinds().kind(IDENTIFIER) is AB428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_69


def test_the_part_declares_the_one_input_as_printed() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Provincial foreign tax credit",
            "reference": "69",
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


def test_a_request_that_leaves_out_line_69_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(alberta_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
