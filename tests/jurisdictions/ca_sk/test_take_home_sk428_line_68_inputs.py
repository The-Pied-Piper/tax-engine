"""SK428 (2025) line 68's input, as the Saskatchewan take-home manifest part declares it.

Form text (Form SK428, CRA 5008-c-25e.txt): "Saskatchewan additional tax for minimum tax
purposes: Line 68: Form T691: Line 1 minus Line 2 of Part 7 multiplied by 50% =" is the line's
printed text; the part takes the text before "multiplied by 50%" as its basis. The form prints no
floor, so the kind is not declared non-negative. A caller with no minimum tax to report leaves the
line out, so the request is read as 0, not blank.

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
from tax_engine.jurisdictions.ca_sk.catalog import SK428_MINIMUM_TAX_T691_AMOUNT_LINE_68
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_units,
)
from tests.manifest_support import input_named

D = Decimal
IDENTIFIER = "ca-sk/sk428_minimum_tax_t691_amount_line_68"
PRINTED_BASIS = "Line 68: Form T691: Line 1 minus Line 2 of Part 7"
PART = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / (
    "manifests/2025/sk428_line_68_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-SK
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
# The form that owns the input, declared here as the real parts of the form declare it.
FORM_NAME = "ca-sk/sk428"
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
        saskatchewan_packages().roots(), saskatchewan_kinds(), saskatchewan_units()
    )
    return source.load(folder)


def test_the_kind_is_in_the_saskatchewan_catalog() -> None:
    assert SK428_MINIMUM_TAX_T691_AMOUNT_LINE_68.identifier == IDENTIFIER
    assert saskatchewan_kinds().kind(IDENTIFIER) is SK428_MINIMUM_TAX_T691_AMOUNT_LINE_68


def test_the_part_declares_the_one_input_as_printed() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Saskatchewan additional tax for minimum tax purposes",
            "reference": "68 box A",
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


def test_a_request_that_leaves_out_line_68_is_read_as_zero(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(saskatchewan_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
