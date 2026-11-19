"""NL428 (2025) line 22's input, as the NL take-home manifest part declares it.

Form NL428 (CRA 5001-C, 5001-c-25e.txt, confirmed 2026-11-18), as printed on the form: "Line 22:
Your eligible dependant's net income from line 23600 of their return". The input is the dependant's
net income, a signed amount: it can be a loss, and line 22 prints no floor, so the kind does not
refuse a negative value. A salary-only caller leaves it out, so it is read as blank, and nothing is
claimed on line 23, which reads this input.

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
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nl.catalog import NL428_ELIGIBLE_DEPENDANT_NET_INCOME_LINE_22
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative

IDENTIFIER = NL428_ELIGIBLE_DEPENDANT_NET_INCOME_LINE_22.identifier
PRINTED_BASIS = "Line 22: Your eligible dependant's net income from line 23600 of their return"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_credits_line_22_input.yaml"
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


def test_the_part_declares_only_the_line_22_input_as_optional() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    (declaration,) = part["inputs"]
    assert list(declaration) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]
    assert declaration["name"] == "ca-nl/nl428_eligible_dependant_net_income_line_22"
    assert (
        declaration["title"]
        == "Your eligible dependant's net income from line 23600 of their return"
    )
    assert declaration["reference"] == "22"
    assert declaration["unit"] == "ca/cad"
    assert declaration["required"] is False
    assert declaration["default"] is None
    assert declaration["basis"] == PRINTED_BASIS


def test_the_net_income_is_a_signed_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_eligible_dependant_net_income_line_22"
    assert kind is NL428_ELIGIBLE_DEPENDANT_NET_INCOME_LINE_22
    assert isinstance(kind, AmountKind)
    assert not non_negative(kind)
    assert Artifact(kind, Decimal("-1234.56")).value == Decimal("-1234.56")


def test_a_request_that_leaves_out_the_net_income_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(newfoundland_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
