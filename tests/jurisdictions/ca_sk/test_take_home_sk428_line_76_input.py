"""SK428 (2025) line 76's input, as the Saskatchewan take-home manifest part declares it.

Form SK428 Saskatchewan Tax 2025 (CRA 5008-C), line 76, printed as the line text in
`PRINTED_BASIS`. A request that leaves the line out is read as blank, and
the line 77 sum reads that blank as 0.

The real part is loaded under a test-local header over the Saskatchewan package list of
`support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_sk.catalog import SK428_VENTURE_CAPITAL_CREDIT_FEDERAL_LINE_76
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = SK428_VENTURE_CAPITAL_CREDIT_FEDERAL_LINE_76.identifier
PRINTED_BASIS = (
    "Line 76: For investments in venture capital corporations registered federally: Enter "
    "your tax credit from T2C Slip (Sask.). (maximum $875)"
)
PART = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / (
    "manifests/2025/sk428_line_76_input.yaml"
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


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_line_76_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": (
                "For investments in venture capital corporations registered federally: Enter "
                "your tax credit from T2C Slip (Sask.)"
            ),
            "reference": "76",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]


def test_line_76_is_a_non_negative_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is SK428_VENTURE_CAPITAL_CREDIT_FEDERAL_LINE_76
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_76_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(saskatchewan_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
