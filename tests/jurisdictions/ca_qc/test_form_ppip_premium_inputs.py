"""The PPIP premium (2025) input, as the Quebec take-home manifest part declares it.

5005-R (CRA 5005-r-25e.txt), as printed: "Line 91 and line 31205: Provincial parental insurance plan
(PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)". The take-home caller has no T4
slip, so the figure is an optional input, as T2204 line 4's is: a request that leaves it out is read
as blank, and the line 91 step computes it from the salary.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_qc.catalog import PPIP_PREMIUMS_GIVEN
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = PPIP_PREMIUMS_GIVEN.identifier
PRINTED_BASIS = "Provincial parental insurance plan (PPIP) premiums paid (box 55 of all T4 slips)"
PART = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / (
    "manifests/2025/ppip_premium_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = """\
form:
  name: ca-qc/ppip_premium
  required: true
  exports:
    - ca-qc/ppip_premiums_given
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "00_header.yaml").write_text(HEADER)
    (folder / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units())
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_box_55_input_as_optional() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/ppip_premium"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": "ca-qc/ppip_premiums_given",
        "title": "Provincial parental insurance plan (PPIP) premiums paid",
        "reference": "Box 55",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": PRINTED_BASIS,
    }


def test_the_figure_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-qc/ppip_premiums_given"
    assert kind is PPIP_PREMIUMS_GIVEN
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_figure_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(quebec_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert default is not None and default.is_blank
