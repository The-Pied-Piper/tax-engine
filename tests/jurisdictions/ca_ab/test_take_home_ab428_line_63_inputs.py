"""AB428 (2025) line 63's input, as the Alberta take-home manifest part declares it.

Form text (AB428, CRA 5009-c-25e.txt in docs/cra-forms-2025): "Line 63 and line 61520: Alberta
dividend tax credit (use Worksheet AB428)" is the line's basis in the take-home part. A salary-only
caller has no dividend income, so a request that leaves the line out is read as blank.

The part is loaded from the test data folder under a test-local header, as the take-home header is
another part's. Alberta is not in `registrations.JURISDICTIONS`, so the source is built over the
Alberta package list of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_ab.catalog import AB428_DIVIDEND_TAX_CREDIT_LINE_63
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units
from tests.kinds import non_negative

IDENTIFIER = "ca-ab/ab428_dividend_tax_credit_line_63"
PRINTED_BASIS = "Line 63 and line 61520: Alberta dividend tax credit (use Worksheet AB428)"
PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / (
    "manifests/2025/ab428_line_63_inputs.yaml"
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
    return YamlJurisdictionSource(
        alberta_packages().roots(), alberta_kinds(), alberta_units()
    ).load(folder)


def _declaration() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    (declaration,) = part["inputs"]
    assert isinstance(declaration, dict)
    return declaration


def test_a_request_that_leaves_out_line_63_is_read_as_blank(tmp_path: Path) -> None:
    kinds = alberta_kinds()
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(kinds.kind(IDENTIFIER))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_part_declares_line_63_as_one_optional_input() -> None:
    assert _declaration() == {
        "name": IDENTIFIER,
        "title": "Alberta dividend tax credit",
        "reference": "63",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": PRINTED_BASIS,
    }


def test_the_declaration_keys_mirror_the_ontario_on428_line_57_part() -> None:
    assert list(_declaration()) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = alberta_kinds().kind(IDENTIFIER)

    assert kind is AB428_DIVIDEND_TAX_CREDIT_LINE_63
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
