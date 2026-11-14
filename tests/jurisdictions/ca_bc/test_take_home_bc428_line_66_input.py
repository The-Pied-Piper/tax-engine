"""BC428 (2025) line 66's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC428, CRA 5010-C, docs/cra-forms-2025): "Line 66 and line 61540: Amount from
line 40427 of your return". A salary-only caller has no minimum tax carryover amount, so a request
that leaves the line out is read as blank, and the step that multiplies it reads that blank as 0.

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
from tax_engine.jurisdictions.ca_bc.catalog import BC428_MINIMUM_TAX_CARRYOVER_AMOUNT
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative

IDENTIFIER = BC428_MINIMUM_TAX_CARRYOVER_AMOUNT.identifier
PRINTED_BASIS = "Line 66 and line 61540: Amount from line 40427 of your return"
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc428_line_66_input.yaml"
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


def test_the_part_declares_only_the_minimum_tax_carryover_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Amount from line 40427 of your return",
            "reference": "66",
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


def test_the_minimum_tax_carryover_amount_is_a_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-bc/bc428_minimum_tax_carryover_amount"
    assert kind is BC428_MINIMUM_TAX_CARRYOVER_AMOUNT
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_66_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
