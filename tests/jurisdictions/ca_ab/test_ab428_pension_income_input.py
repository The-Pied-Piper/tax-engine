"""AB428 (2025) line 34's input, as the Alberta take-home manifest part declares it.

Form text (AB428, CRA 5009-c-25e.txt in docs/cra-forms-2025): "Line 34 and line 58360: Pension
income amount (maximum $1,719)". A salary-only caller has no pension income amount, so a request
that leaves the line out is read as 0, not blank.

Alberta is not yet listed, so the real part is loaded under a test-local header over the Alberta
package list in `support.py`, not over the engine's registrations.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_ab.catalog import AB428_PENSION_INCOME_AMOUNT
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = AB428_PENSION_INCOME_AMOUNT.identifier
PRINTED_BASIS = "Line 34 and line 58360: Pension income amount (maximum $1,719)"
PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / (
    "manifests/2025/ab428_pension_income_inputs.yaml"
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
            "reference": "34",
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
    kind = alberta_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-ab/ab428_pension_income_amount"
    assert kind is AB428_PENSION_INCOME_AMOUNT
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_pension_income_amount_is_read_as_zero(
    tmp_path: Path,
) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(alberta_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
