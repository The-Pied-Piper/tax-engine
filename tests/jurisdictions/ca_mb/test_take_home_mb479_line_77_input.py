"""MB479 (2025) line 77's input, as the Manitoba take-home manifest part declares it.

Form MB479 (CRA 5007-TC), line 77, printed "Line 77 and line 61490: Enter your Manitoba employee
share purchase tax credit from line 6 of Form T1256-2. (maximum $27,000)". The form prints no label
for the line, so the input stays untitled. A salary-only filer has no such credit, so a request that
leaves the line out is read as blank.

The real part is loaded under a test-local header over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_mb.catalog import MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_LINE_77
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_LINE_77.identifier
PRINTED_BASIS = (
    "Line 77 and line 61490: Enter your Manitoba employee share purchase tax credit from line 6 of "
    "Form T1256-2. (maximum $27,000)"
)
PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / (
    "manifests/2025/mb479_line_77_input.yaml"
)
HEADER = """\
jurisdiction: CA-MB
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


def test_the_part_declares_only_the_line_77_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert list(part["form"]) == ["name"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "reference": "77",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]
    assert list(part["inputs"][0]) == [
        "name",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]


def test_the_employee_share_purchase_credit_line_77_is_a_non_negative_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-mb/mb479_employee_share_purchase_credit_line_77"
    assert kind is MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_LINE_77
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_77_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(manitoba_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
