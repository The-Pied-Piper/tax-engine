"""The PPIP premium (2025) input, as the Quebec take-home manifest part declares it.

5005-R (CRA 5005-r-25e.txt), as printed: "Line 91 and line 31205: Provincial parental insurance plan
(PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)". The take-home caller has no T4
slip, so the figure is an optional input, as T2204 line 4's is: a request that leaves it out is read
as blank, and the line 91 step computes it from the salary.

5005-S10 (CRA 5005-s10-25e.txt) line 13: "Enter the amount from box 56 of all of your T4 slips where
Quebec is the province of employment (if box 56 is blank, enter the amount from box 14 of the T4
slip) (include employment income that you did not get a T4 slip for)". The box 56 total is a second
optional input of the same form, read as blank when a request leaves it out.

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
from tax_engine.jurisdictions.ca_qc.catalog import (
    PPIP_INSURABLE_EARNINGS_GIVEN,
    PPIP_PREMIUMS_GIVEN,
)
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = PPIP_PREMIUMS_GIVEN.identifier
PRINTED_BASIS = "Provincial parental insurance plan (PPIP) premiums paid (box 55 of all T4 slips)"
EARNINGS_IDENTIFIER = PPIP_INSURABLE_EARNINGS_GIVEN.identifier
EARNINGS_BASIS = (
    "Enter the amount from box 56 of all of your T4 slips where Quebec is the province of "
    "employment (if box 56 is blank, enter the amount from box 14 of the T4 slip)"
)
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


def test_the_part_declares_the_box_55_and_box_56_inputs_as_optional() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/ppip_premium"}
    premiums, earnings = part["inputs"]
    assert premiums == {
        "name": "ca-qc/ppip_premiums_given",
        "title": "Provincial parental insurance plan (PPIP) premiums paid",
        "reference": "Box 55",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": PRINTED_BASIS,
    }
    assert earnings == {
        "name": "ca-qc/ppip_insurable_earnings_given",
        "title": "PPIP insurable earnings",
        "reference": "Box 56",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": EARNINGS_BASIS,
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


def test_the_box_56_figure_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(EARNINGS_IDENTIFIER)

    assert EARNINGS_IDENTIFIER == "ca-qc/ppip_insurable_earnings_given"
    assert kind is PPIP_INSURABLE_EARNINGS_GIVEN
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_a_request_that_leaves_out_box_56_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), EARNINGS_IDENTIFIER)
    default = declaration.default_artifact(quebec_kinds().kind(EARNINGS_IDENTIFIER))

    assert not declaration.required
    assert default is not None and default.is_blank
