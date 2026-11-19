"""NL428 (2025) line 68's input, as the Newfoundland and Labrador take-home manifest declares it.

Form NL428 (CRA 5001-C), line 68, as printed on the form: "Newfoundland and Labrador minimum tax
carryover: Line 68 and line 61540: Amount from line 40427 of your return ... multiplied by 60% =".
The first box takes the amount from line 40427 of the return; the 60% is a later ticket. The input
carries no title: the heading printed above the line names the line's result, not box A. A
salary-only caller has no minimum tax carryover, so a request that leaves the line out is read as
blank; the step that reads line 68 reads that blank as 0.

The real part is loaded under a test-local header over the Newfoundland and Labrador package list
of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_68,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative

KIND = NL428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_68
IDENTIFIER = KIND.identifier
PRINTED_BASIS = "Line 68 and line 61540: Amount from line 40427 of your return"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_line_68_inputs.yaml"
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


def test_the_part_declares_only_the_minimum_tax_carryover_line_68_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "reference": "68 box A",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]


def test_the_minimum_tax_carryover_line_68_is_a_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_minimum_tax_carryover_amount_line_68"
    assert kind is KIND
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_68_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(newfoundland_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_an_amount_for_line_68_is_taken_as_given() -> None:
    assert Artifact(KIND, Decimal("1234.56")).value == Decimal("1234.56")
