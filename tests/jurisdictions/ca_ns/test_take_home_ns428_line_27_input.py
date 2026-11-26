"""NS428 (2025) line 27's input, as the Nova Scotia take-home manifest part declares it.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 27 and line
58360: Pension income amount (maximum $1,173)". A salary-only caller has no pension income amount,
so a request that leaves the line out is read as 0, not blank.

Nova Scotia is not yet listed, so the real part is loaded under a test-local header over the Nova
Scotia package list in `support.py`, not over the engine's registrations.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ns
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_ns.catalog import NS428_PENSION_INCOME_AMOUNT
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_kinds,
    nova_scotia_packages,
    nova_scotia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

D = Decimal
IDENTIFIER = NS428_PENSION_INCOME_AMOUNT.identifier
PRINTED_BASIS = "Line 27 and line 58360: Pension income amount (maximum $1,173)"
PART = (
    Path(tax_engine.jurisdictions.ca_ns.__file__).parent / "manifests/2025/ns428_line_27_input.yaml"
)
HEADER = """\
jurisdiction: CA-NS
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM_NAME = "ca-ns/ns428"
FORM = f"""\
form:
  name: {FORM_NAME}
  required: true
  exports:
    - {IDENTIFIER}
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(FORM)
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(
        nova_scotia_packages().roots(), nova_scotia_kinds(), nova_scotia_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_pension_income_input_in_the_printed_order() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Pension income amount",
            "reference": "27",
            "unit": "ca/cad",
            "required": False,
            "default": "0",
            "basis": PRINTED_BASIS,
        }
    ]


def test_the_pension_income_amount_is_a_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-ns/ns428_pension_income_amount"
    assert kind is NS428_PENSION_INCOME_AMOUNT
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_pension_income_amount_is_read_as_zero(
    tmp_path: Path,
) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(nova_scotia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
