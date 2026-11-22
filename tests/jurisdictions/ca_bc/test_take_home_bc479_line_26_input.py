"""BC479 (2025) line 26's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC479, CRA 5010-TC, the printed section heading "British Columbia mining
exploration tax credit"): "Line 26 and line 60510: Enter the amount from line 23 of your Form T88."
Single amount, no columns. The form takes the figure from Form T88, which the engine does not
compute, so a request that leaves the line out is read as blank.

The real part is loaded under a test-local header over the British Columbia package list of
`support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_bc.catalog import BC479_MINING_EXPLORATION_CREDIT_LINE_26
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = BC479_MINING_EXPLORATION_CREDIT_LINE_26.identifier
PRINTED_TITLE = "British Columbia mining exploration tax credit"
PRINTED_BASIS = "Line 26 and line 60510: Enter the amount from line 23 of your Form T88"
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc479_line_26_input.yaml"
)
HEADER = """\
jurisdiction: CA-BC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""


FORM_NAME = "ca-bc/bc479"


def _owner_form() -> str:
    """A declaration of the form the part names as owner of its inputs, exporting one input."""
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    name = part["form"]["name"]
    export = part["inputs"][0]["name"]
    return f"form:\n  name: {name}\n  required: true\n  exports: [{export}]\ncapabilities: []\n"


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(_owner_form())
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(
        british_columbia_packages().roots(), british_columbia_kinds(), british_columbia_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_mining_exploration_credit_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": PRINTED_TITLE,
            "reference": "26",
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


def test_the_mining_exploration_credit_line_26_is_a_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-bc/bc479_mining_exploration_credit_line_26"
    assert kind is BC479_MINING_EXPLORATION_CREDIT_LINE_26
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_26_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
