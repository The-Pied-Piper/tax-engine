"""MB479 (2025) line 80's input, as the Manitoba take-home manifest part declares it.

Form MB479 (CRA 5007-TC) prints "Rental housing construction incentive tax credit:" and then
"Line 80: Certificate number: Line 61496 ^" and "Tax credit amount from your certificate ^". The
line prints no maximum. It is an optional credit input that a salary-only filer does not give, so a
request that leaves the line out is read as blank. The consuming step is a later one and is not
tested here.

The real part is loaded under a test-local header over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_mb.catalog import (
    MB479_RENTAL_HOUSING_CONSTRUCTION_INCENTIVE_TAX_CREDIT_LINE_80,
)
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)
from tests.kinds import non_negative

IDENTIFIER = MB479_RENTAL_HOUSING_CONSTRUCTION_INCENTIVE_TAX_CREDIT_LINE_80.identifier
PRINTED_TITLE = "Rental housing construction incentive tax credit"
PRINTED_BASIS = "Line 80: Certificate number: Line 61496 Tax credit amount from your certificate"
PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / (
    "manifests/2025/mb479_line_80_input.yaml"
)
HEADER = """\
jurisdiction: CA-MB
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
    source = YamlJurisdictionSource(manitoba_packages().roots(), manitoba_kinds(), manitoba_units())
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_line_80_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": PRINTED_TITLE,
            "reference": "80",
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


def test_the_rental_housing_construction_incentive_tax_credit_is_a_non_negative_amount_kind() -> (
    None
):
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-mb/mb479_rental_housing_construction_incentive_tax_credit_line_80"
    assert kind is MB479_RENTAL_HOUSING_CONSTRUCTION_INCENTIVE_TAX_CREDIT_LINE_80
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_80_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(manitoba_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
