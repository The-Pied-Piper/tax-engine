"""Worksheet NL428 (2025) line 58440 line 5, line 3 minus line 4, from the real parts.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt, confirmed 2026-11-19), section
"Line 58440 - Disability amount for self": "Complete this calculation if you were under 18 years of
age on December 31, 2025."
"Line 3: Total child care and attendant care expenses for you, claimed by you or another person",
"Line 4: Threshold for child and attendant care expenses 2,987.00" and "Line 5: Line 3 minus line 4
(if negative, enter "0")". Line 4 is the `ca-nl/disability_self_care_threshold` dataset claimed
whole (reference "4"); line 3 is the optional shared input `ca/disability_self_care_expenses`, read
as 0 when blank. Line 5 is core/subtract_not_below_zero rounded half-up to the cent. It carries
the reference "5".

Care expenses 4,987 give line 5 = 2,000.00; 2,987 or less give 0.00; 3,000.005 gives 13.01.

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

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import DISABILITY_SELF_CARE_EXPENSES
from tests.federal_forms import form_parts
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
INPUT_PART = PARTS / "worksheet_nl428_line_3_input.yaml"
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
    outputs: []
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
    for part in form_parts("t1_employment_income"):
        (folder / f"00_t1_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    # The under-18 answer (`worksheet_nl428_line_58440_input.yaml`) is read by NL428 line 40, not by
    # these lines, and a manifest refuses an input nothing reads, so only the care expenses input
    # part, which the Worksheet NL428 form owns, is loaded here.
    (folder / "02_inputs.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
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
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NL"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


CASES = [
    (None, "0.00"),
    ("2987", "0.00"),
    ("4987", "2000.00"),
    ("3000.005", "13.01"),
]


@pytest.mark.parametrize(("care", "line_5"), CASES)
def test_line_5_is_the_care_expenses_less_the_threshold_not_below_0(
    tmp_path: Path, care: str | None, line_5: str
) -> None:
    assert _value(_sheet(tmp_path, care), LINE_5) == D(line_5)


def test_line_4_is_the_printed_threshold(tmp_path: Path) -> None:
    assert _value(_sheet(tmp_path), LINE_4) == D("2987.00")


def test_a_negative_care_expense_is_refused(tmp_path: Path) -> None:
    with pytest.raises(NegativeArtifactError):
        _sheet(tmp_path, "-0.01")


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_line_5_part_is_the_threshold_and_the_subtraction_with_a_blank_read_as_0() -> None:
    part = _part(PART_5)

    assert part["form"] == {"name": FORM_NAME}
    threshold, subtract = part["capabilities"]
    assert threshold["name"] == "core/credit_amount"
    assert threshold["params"] == {"amount": "ca-nl/disability_self_care_threshold"}
    assert threshold["produces"] == {"output": LINE_4}
    assert threshold["reference"] == "4"
    assert subtract["name"] == "core/subtract_not_below_zero"
    assert subtract["reference"] == "5"
    assert subtract["params"] == {"rounding": ROUNDING}
    assert subtract["consumes"] == {"amount": "ca/disability_self_care_expenses", "less": LINE_4}
    assert subtract["blank"] == {"amount": "0"}
    assert subtract["produces"] == {"output": LINE_5}


@pytest.mark.parametrize("identifier", [LINE_4, LINE_5])
def test_the_line_kinds_are_registered_non_negative_amounts_with_the_line_quoted(
    identifier: str,
) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert identifier.startswith("ca-nl/")
