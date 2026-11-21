"""MB479 (2025) line 56's input, as the Manitoba take-home manifest part declares it.

Form MB479 (CRA 5007-TC), line 56, which has no printed label, only the sentence "Line 56 and line
61255: If you (or your spouse or common-law partner) did receive EIA or MSPD payments from Manitoba
in 2025, enter the number from box 14 of your (or your spouse's or common-law partner's) Form T5007,
Statement of Benefits (even if it is 0.00)." Line 57 multiplies line 55 by line 56. A request that
leaves the line out is read as 1, so line 57 is line 55; an entered 0.00 gives 0.

The real part is loaded under a test-local header over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_mb.catalog import MB479_EIA_MSPD_NUMBER_LINE_56
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)
from tests.kinds import non_negative

IDENTIFIER = MB479_EIA_MSPD_NUMBER_LINE_56.identifier
PRINTED_BASIS = (
    "Line 56 and line 61255: If you (or your spouse or common-law partner) did receive EIA or "
    "MSPD payments from Manitoba in 2025, enter the number from box 14 of your (or your spouse's "
    "or common-law partner's) Form T5007, Statement of Benefits (even if it is 0.00). If you and "
    "your spouse or common-law partner both received EIA or MSPD payments from Manitoba in 2025, "
    "enter the number shown in 61255 box 14 of your T5007 slip or theirs, whichever is less."
)
PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / (
    "manifests/2025/mb479_line_56_input.yaml"
)
HEADER = """\
jurisdiction: CA-MB
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
    # The part gives its inputs to the form named in its header, so the manifest declares that form,
    # here exporting the part's own inputs.
    part = _part()
    form = {
        "form": {
            "name": part["form"]["name"],
            "required": True,
            "exports": [declaration["name"] for declaration in part["inputs"]],
        },
        "capabilities": [],
    }
    (folder / "form.yaml").write_text(yaml.safe_dump(form), encoding="utf-8")
    source = YamlJurisdictionSource(manitoba_packages().roots(), manitoba_kinds(), manitoba_units())
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_untitled_line_56_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert list(part["form"]) == ["name"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "reference": "56",
            "unit": "ca/cad",
            "required": False,
            "default": "1",
            "basis": PRINTED_BASIS,
        }
    ]
    assert "title" not in part["inputs"][0]
    assert list(part["inputs"][0]) == [
        "name",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]
    assert part["inputs"][0]["default"] == "1"
    assert isinstance(part["inputs"][0]["default"], str)


def test_the_eia_or_mspd_number_is_a_non_negative_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-mb/mb479_eia_mspd_number_line_56"
    assert kind is MB479_EIA_MSPD_NUMBER_LINE_56
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_56_is_read_as_1(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(manitoba_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == Decimal("1")
