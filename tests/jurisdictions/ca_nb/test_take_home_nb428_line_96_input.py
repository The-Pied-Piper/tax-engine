"""NB428 (2025) line 96's input, as the New Brunswick take-home manifest part declares.

Form text (Form NB428, CRA 5004-C):
"Line 96: Small business investor tax credit (complete Form T1258) (maximum $125,000)".
Form T1258 is not built; a salary-only filer has no such claim, so the line is
taken as an input, and a request that leaves the line out is read as blank. The amount is
non-negative.

The real part is loaded under a test-local header, as the take-home header is another part's.
New Brunswick is not yet listed in the registrations, so the source is built over the New
Brunswick package list of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nb.catalog import (
    NB428_SMALL_BUSINESS_INVESTOR_CREDIT_LINE_96,
)
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

KIND = NB428_SMALL_BUSINESS_INVESTOR_CREDIT_LINE_96
IDENTIFIER = KIND.identifier
PRINTED_BASIS = (
    "Line 96: Small business investor tax credit (complete Form T1258) (maximum $125,000)"
)
PART = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / (
    "manifests/2025/nb428_line_96_input.yaml"
)
HEADER = """\
jurisdiction: CA-NB
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
        new_brunswick_packages().roots(), new_brunswick_kinds(), new_brunswick_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_a_request_that_leaves_out_line_96_is_read_as_blank(tmp_path: Path) -> None:
    kinds = new_brunswick_kinds()
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(kinds.kind(IDENTIFIER))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_line_96_is_a_non_negative_amount_kind() -> None:
    kind = new_brunswick_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nb/nb428_small_business_investor_credit_line_96"
    assert kind is KIND
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert Artifact(kind, Decimal("1234.56")) is not None


def test_the_part_declares_the_input_with_its_unit_reference_and_title() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-nb/nb428"}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": ("Small business investor tax credit"),
            "reference": "96",
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
