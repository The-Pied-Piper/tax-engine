"""MB428 (2025) line 54's input, as the Manitoba take-home manifest part declares it.

Form MB428 (CRA 5007-c-25e.txt), line 54, as printed on the form:
"Line 54: Amount from line 13 of your federal Schedule 9".

A salary-only caller has no such claim, so a request that leaves the line out is read as blank,
and the step that reads it takes the blank as 0.

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
from tax_engine.jurisdictions.ca_mb.catalog import MB428_DONATIONS_AMOUNT_LINE_54
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = MB428_DONATIONS_AMOUNT_LINE_54.identifier
PRINTED_BASIS = "Line 54: Amount from line 13 of your federal Schedule 9"
PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / (
    "manifests/2025/mb428_credits_line_54_inputs.yaml"
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


def test_the_part_declares_only_the_line_54_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert list(part["form"]) == ["name"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Amount from line 13 of your federal Schedule 9",
            "reference": "54 box A",
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


def test_the_line_54_input_is_a_non_negative_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-mb/mb428_donations_amount_line_54"
    assert kind is MB428_DONATIONS_AMOUNT_LINE_54
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_54_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(manitoba_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
