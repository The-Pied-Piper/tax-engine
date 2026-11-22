"""The spouse's line 275 input (2025), as the Quebec take-home manifest part declares it.

Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part A, line 37, and TP-1.D.P-V, Schedule P,
Part C, line 53: "Amount from line 275 of your spouse's return (spouse on December 31, 2025)". The
spouse's return is not computed here, so the amount is an optional input, left blank by a single
filer. The TP-1 net income form takes it once and exports it; Schedule K line 37 and Schedule P
line 53 read the export and read the blank as 0.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_qc.catalog import TP1_SPOUSE_NET_INCOME_LINE_275
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = TP1_SPOUSE_NET_INCOME_LINE_275.identifier
PRINTED_BASIS = "Amount from line 275 of your spouse's return (spouse on December 31, 2025)"
PART = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / (
    "manifests/2025/tp1_net_income_line_275_spouse_input.yaml"
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
  name: ca-qc/tp1_net_income
  required: true
  exports:
    - ca-qc/tp1_spouse_net_income_line_275
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


def test_the_part_declares_only_the_spouse_line_275_input_as_optional() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/tp1_net_income"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": IDENTIFIER,
        "title": "Amount from line 275 of your spouse's return",
        "reference": "275",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": PRINTED_BASIS,
    }


def test_the_amount_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-qc/tp1_spouse_net_income_line_275"
    assert kind is TP1_SPOUSE_NET_INCOME_LINE_275
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_amount_is_left_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(quebec_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert default is not None and default.is_blank
