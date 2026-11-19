"""NL428 (2025) line 76, the political contribution tax credit, rejected above its printed maximum.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 76: Newfoundland and
Labrador political contribution tax credit (use Worksheet NL428) (maximum $500)". No arithmetic is
printed, so line 76 is an entry line: the entered amount is rejected above the printed maximum, not
capped. The maximum is the `ca-nl/political_contribution_tax_credit_maximum` dataset, supplied by a
first `core/credit_amount` step that carries no title and no line number (it is not a line of the
form); the second step, `core/at_most`, is line 76 and carries "76". A blank input (the default) is
passed on as blank. The output is not exported, as no later line reads it yet.

The real input part and the new `nl428_line_76.yaml` are loaded under a test-local header and form
over the Newfoundland and Labrador package list of `support.py`, the shared scaffold owning those,
and only the salary is typed in (plus, in some tests, the credit).
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_POLITICAL_CONTRIBUTION_TAX_CREDIT_CLAIMED_LINE_76,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
INPUT_PART = PARTS / "nl428_line_76_input.yaml"
LINE_PART = PARTS / "nl428_line_76.yaml"
FORM = "ca-nl/nl428"
CLAIMED = "ca-nl/nl428_political_contribution_tax_credit_claimed_line_76"
MAXIMUM = "ca-nl/nl428_political_contribution_tax_credit_maximum"
LINE_76 = "ca-nl/nl428_political_contribution_tax_credit_line_76"
PRINTED_BASIS = (
    "Line 76: Newfoundland and Labrador political contribution tax credit "
    "(use Worksheet NL428) (maximum $500)"
)

INPUT_HEADER = """\
jurisdiction: CA-NL
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""
HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM_PART = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_76}
    capabilities: []
    """)


def _input_manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(INPUT_HEADER)
    shutil.copy(INPUT_PART, folder / INPUT_PART.name)
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_PART, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_76.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(),
            newfoundland_parameter_parsers(),
            newfoundland_units(),
        ),
        newfoundland_capabilities(),
    )


def _line_76(tmp_path: Path, credit: str | None = None) -> Artifact[Any]:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if credit is not None:
        given.append(Artifact(NL428_POLITICAL_CONTRIBUTION_TAX_CREDIT_CLAIMED_LINE_76, D(credit)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet.get(newfoundland_kinds().kind(LINE_76))


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def _input_part() -> dict[str, Any]:
    part = yaml.safe_load(INPUT_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_input_part_declares_the_optional_input_with_its_printed_basis() -> None:
    part = _input_part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": CLAIMED,
            "title": "Newfoundland and Labrador political contribution tax credit",
            "reference": "76",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]


def test_the_line_part_is_the_maximum_step_then_line_76() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    assert part["capabilities"] == [
        {
            "name": "core/credit_amount",
            "unit": "ca/cad",
            "params": {"amount": "ca-nl/political_contribution_tax_credit_maximum"},
            "produces": {"output": MAXIMUM},
        },
        {
            "name": "core/at_most",
            "title": "Newfoundland and Labrador political contribution tax credit",
            "reference": "76",
            "unit": "ca/cad",
            "consumes": {"amount": CLAIMED, "bound": MAXIMUM},
            "blank": {"amount": "pass_on"},
            "produces": {"output": LINE_76},
        },
    ]


def test_an_amount_at_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_76(tmp_path, "500").value) == D("500.00")


def test_an_amount_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_76(tmp_path, "500.01")


def test_a_request_that_leaves_out_line_76_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _input_manifest(tmp_path).inputs[CLAIMED]
    default = declaration.default_artifact(newfoundland_kinds().kind(CLAIMED))

    assert not declaration.required
    assert default is not None and default.is_blank
    assert _line_76(tmp_path).is_blank
