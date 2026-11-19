"""NL428 (2025) line 80's input, as the Newfoundland and Labrador take-home manifest declares it.

Form NL428 (CRA 5001-C), line 80, as printed on the form: "Line 80: Resort property investment tax
credit (complete Form T1297)". Form T1297 is not built; a salary-only caller has no resort property
investment tax credit, so a request that leaves the line out is read as blank; the step that reads
line 80 reads that blank as 0.

The real part is loaded under a test-local header over the Newfoundland and Labrador package list
of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_RESORT_PROPERTY_INVESTMENT_TAX_CREDIT_LINE_80,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative

KIND = NL428_RESORT_PROPERTY_INVESTMENT_TAX_CREDIT_LINE_80
IDENTIFIER = KIND.identifier
PRINTED_BASIS = "Line 80: Resort property investment tax credit (complete Form T1297)"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_line_80_input.yaml"
)
HEADER = """\
jurisdiction: CA-NL
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
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_resort_property_investment_tax_credit_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Resort property investment tax credit",
            "reference": "80",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]


def test_the_resort_property_investment_tax_credit_line_80_is_a_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_resort_property_investment_tax_credit_line_80"
    assert kind is KIND
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_80_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(newfoundland_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
