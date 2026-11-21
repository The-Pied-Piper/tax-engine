"""BC428 (2025) line 69's input, as the British Columbia take-home manifest part declares it.

Form BC428 (CRA 5010-C), line 69, as printed on the form; the part takes the printed text before its
^ marker as its basis. The form prints no floor, so the kind is not non_negative. A caller with no
minimum tax to report leaves the line out, so the request is read as 0, not blank, because the step
that multiplies it by the rate needs a base.

The real part is loaded under a test-local header over the British Columbia package list of
`support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_bc.catalog import BC428_ADDITIONAL_MINIMUM_TAX_AMOUNT_LINE_69
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = "ca-bc/bc428_additional_minimum_tax_amount_line_69"
PRINTED_BASIS = "Line 69: Amount from line 14 of Part 7 of Form T691"
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc428_line_69_input.yaml"
)
HEADER = """\
jurisdiction: CA-BC
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""


FORM_NAME = "ca-bc/bc428"


def _owner_form() -> str:
    """A declaration of the form the part names as owner of its inputs, exporting one input."""
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    name = part["form"]["name"]
    export = part["inputs"][0]["name"]
    return f"form:\n  name: {name}\n  required: true\n  exports: [{export}]\ncapabilities: []\n"


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(_owner_form())
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(
        british_columbia_packages().roots(), british_columbia_kinds(), british_columbia_units()
    )
    return source.load(folder)


def test_the_kind_is_in_the_british_columbia_catalog_and_not_non_negative() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert BC428_ADDITIONAL_MINIMUM_TAX_AMOUNT_LINE_69.identifier == IDENTIFIER
    assert kind is BC428_ADDITIONAL_MINIMUM_TAX_AMOUNT_LINE_69
    assert not non_negative(kind)


def test_the_part_declares_the_one_input_as_printed() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Amount from line 14 of Part 7 of Form T691",
            "reference": "69",
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


def test_a_request_that_leaves_out_line_69_is_read_as_zero(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
