"""Worksheet NL428 (2025) line 58440 line 6, line 2 minus line 5, from the real parts.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt, confirmed 2026-11-19), section
"Line 58440 - Disability amount for self": "Complete this calculation if you were under 18 years of
age on December 31, 2025."
"Line 2: Maximum amount 3,514.00" and "Line 6: Line 2 minus line 5 (if negative, enter "0")". Line 2
is the `ca-nl/disability_self_supplement_maximum` dataset claimed whole (no reference). Line 6 is
core/subtract_not_below_zero rounded half-up to the cent. It carries the reference "6".

Care expenses 4,987 give line 6 = 1,514.00; 2,987 or less give 3,514.00; 6,501 or more give 0.00.

The real parts are loaded under a test-local header and form declaration over the package list of
`support.py`. Figures are hand-computed, not a CRA example.
"""

from __future__ import annotations

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
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import DISABILITY_SELF_CARE_EXPENSES
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
INPUT_PART = PARTS / "worksheet_nl428_line_58440_input.yaml"
PART_5 = PARTS / "worksheet_nl428_58440_line_5.yaml"
PART_6 = PARTS / "worksheet_nl428_58440_line_6.yaml"
PART_7 = PARTS / "worksheet_nl428_58440_line_7.yaml"
FORM_NAME = "ca-nl/nl428_worksheet"
LINE_1 = "ca-nl/worksheet_nl428_disability_self_base_amount_line_1"
LINE_2 = "ca-nl/worksheet_nl428_disability_self_supplement_maximum_line_2"
LINE_4 = "ca-nl/worksheet_nl428_disability_self_care_threshold_line_4"
LINE_5 = "ca-nl/worksheet_nl428_disability_self_care_over_threshold_line_5"
LINE_6 = "ca-nl/worksheet_nl428_disability_self_supplement_line_6"
LINE_7 = "ca-nl/worksheet_nl428_disability_self_line_7"
ROUNDING = "ca-nl/cent_rounding"

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_2}
        - {LINE_4}
        - {LINE_5}
        - {LINE_6}
        - {LINE_7}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    # The under-18 answer is read by NL428 line 40, not by these lines, and a manifest refuses an
    # input nothing reads, so only the care expenses input is loaded here.
    inputs = _part(INPUT_PART)["inputs"]
    care_only = {
        "inputs": [each for each in inputs if each["name"] != "ca/under_18_on_december_31"]
    }
    (folder / "02_inputs.yaml").write_text(yaml.safe_dump(care_only), encoding="utf-8")
    for number, found in enumerate((PART_5, PART_6, PART_7), start=3):
        (folder / f"{number:02d}_{found.name}").write_text(
            found.read_text(encoding="utf-8"), encoding="utf-8"
        )
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


def _sheet(tmp_path: Path, care: str | None = None) -> Worksheet:
    given: list[Artifact[Decimal]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if care is not None:
        given.append(Artifact(DISABILITY_SELF_CARE_EXPENSES, D(care)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


CASES = [
    (None, "3514.00"),
    ("2987", "3514.00"),
    ("2987.01", "3513.99"),
    ("4987", "1514.00"),
    ("6500.99", "0.01"),
    ("6501", "0.00"),
    ("9000", "0.00"),
    ("3000.005", "3500.99"),
]


@pytest.mark.parametrize(("care", "line_6"), CASES)
def test_line_6_is_the_maximum_less_line_5_not_below_0(
    tmp_path: Path, care: str | None, line_6: str
) -> None:
    assert _value(_sheet(tmp_path, care), LINE_6) == D(line_6)


def test_line_2_is_the_printed_maximum(tmp_path: Path) -> None:
    assert _value(_sheet(tmp_path), LINE_2) == D("3514.00")


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_line_6_part_is_the_maximum_and_the_subtraction() -> None:
    part = _part(PART_6)

    assert part["form"] == {"name": FORM_NAME}
    maximum, subtract = part["capabilities"]
    assert maximum["name"] == "core/credit_amount"
    assert maximum["params"] == {"amount": "ca-nl/disability_self_supplement_maximum"}
    assert maximum["produces"] == {"output": LINE_2}
    assert "reference" not in maximum
    assert subtract["name"] == "core/subtract_not_below_zero"
    assert subtract["reference"] == "6"
    assert subtract["params"] == {"rounding": ROUNDING}
    assert subtract["consumes"] == {"amount": LINE_2, "less": LINE_5}
    assert "blank" not in subtract
    assert subtract["produces"] == {"output": LINE_6}


@pytest.mark.parametrize("identifier", [LINE_2, LINE_6])
def test_the_line_kinds_are_registered_non_negative_amounts_with_the_line_quoted(
    identifier: str,
) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert identifier.startswith("ca-nl/")
