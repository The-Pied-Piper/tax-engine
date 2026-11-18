"""SK428 (2025) line 73's input, as the Saskatchewan take-home manifest part declares it.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 73: Saskatchewan political contribution tax
credit (use Worksheet SK428) (maximum $650)". A salary-only caller has no political
contributions, so a request that leaves the line out is read as blank, not 0.

The real part is loaded under a test-local header over the Saskatchewan package list in
`support.py`, not over the engine's registrations.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_sk.catalog import SK428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_73
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_units,
)
from tests.kinds import non_negative

IDENTIFIER = "ca-sk/sk428_political_contributions_credit_line_73"
PRINTED_BASIS = (
    "Line 73: Saskatchewan political contribution tax credit (use Worksheet SK428) (maximum $650)"
)
PART = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / (
    "manifests/2025/sk428_line_73_input.yaml"
)
HEADER = """\
jurisdiction: CA-SK
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
        saskatchewan_packages().roots(), saskatchewan_kinds(), saskatchewan_units()
    )
    return source.load(folder)


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert SK428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_73.identifier == IDENTIFIER
    assert kind is SK428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_73
    assert non_negative(kind)


def test_the_part_declares_the_one_input_as_printed() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Saskatchewan political contribution tax credit",
            "reference": "73",
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


def test_a_request_that_leaves_out_line_73_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(saskatchewan_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
