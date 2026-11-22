"""NL428 (2025) line 88's column 2 input, as the Newfoundland and Labrador take-home part declares.

Form text (Form NL428, CRA 5001-C): "Line 88: Net income from line 23600 of the return (or the
amount you would have entered if the instructions on line 23600 said "if negative, show in
brackets")", column 2: your spouse or common-law partner. Column 1 is a copy of line 23600 and has
no step. A salary-only caller has no spouse or common-law partner, so a request that leaves the
line out is read as blank. The amount is signed: the line takes the amount as if a negative were
shown in brackets.

The real part is loaded under a test-local header, as the take-home header is another part's.
Newfoundland and Labrador is not yet listed in the registrations, so the source is built over the
Newfoundland and Labrador package list of `support.py`.
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
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nl.catalog import NL428_SPOUSE_NET_INCOME_LINE_88
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

KIND = NL428_SPOUSE_NET_INCOME_LINE_88
IDENTIFIER = KIND.identifier
PRINTED_LABEL = (
    "Net income from line 23600 of the return (or the amount you would have entered if the "
    'instructions on line 23600 said "if negative, show in brackets")'
)
PRINTED_BASIS = f"Line 88: {PRINTED_LABEL}"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_line_88_column_2_input.yaml"
)
HEADER = """\
jurisdiction: CA-NL
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    declared = yaml.safe_load(PART.read_text(encoding="utf-8"))
    exports = "".join(f"    - {each['name']}\n" for each in declared["inputs"])
    (folder / "form.yaml").write_text(
        f"form:\n  name: {declared['form']['name']}\n  required: true\n  exports:\n{exports}"
        "capabilities: []\n"
    )
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_the_input_with_its_unit_reference_and_title() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-nl/nl428"}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": PRINTED_LABEL,
            "reference": "88 (column 2)",
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


def test_a_request_that_leaves_out_line_88_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(newfoundland_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_spouse_net_income_line_88_is_a_signed_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_spouse_net_income_line_88"
    assert kind is KIND
    assert isinstance(kind, AmountKind)
    assert not non_negative(kind)


def test_a_negative_amount_for_line_88_is_taken_as_given() -> None:
    assert Artifact(KIND, Decimal("-1234.56")).value == Decimal("-1234.56")
