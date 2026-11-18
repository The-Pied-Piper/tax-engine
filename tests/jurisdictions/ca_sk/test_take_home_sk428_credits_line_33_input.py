"""SK428 (2025) line 33's input, as the Saskatchewan take-home manifest part declares it.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 33 and line 58360: Pension income amount
(maximum $1,000)". A salary-only caller has no pension income amount, so a request that leaves
the line out is read as 0, not blank.

Saskatchewan is not yet listed, so the real part is loaded under a test-local header over the
Saskatchewan package list in `support.py`, not over the engine's registrations.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_sk.catalog import SK428_PENSION_INCOME_AMOUNT
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = SK428_PENSION_INCOME_AMOUNT.identifier
PRINTED_BASIS = "Line 33 and line 58360: Pension income amount (maximum $1,000)"
PART = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / (
    "manifests/2025/sk428_credits_line_33_input.yaml"
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


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_pension_income_input_in_the_printed_order() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Pension income amount",
            "reference": "33",
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


def test_the_pension_income_amount_is_a_non_negative_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-sk/sk428_pension_income_amount"
    assert kind is SK428_PENSION_INCOME_AMOUNT
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_pension_income_amount_is_read_as_zero(
    tmp_path: Path,
) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(saskatchewan_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
