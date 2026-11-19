"""Worksheet NL428 (2025) section "Line 58440 - Disability amount for self", lines 1 to 7, from the
real parts.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt, confirmed 2026-11-19): "Complete this
calculation if you were under 18 years of age on December 31, 2025." "Line 1: Base amount 7,467.00",
"Line 2: Maximum amount 3,514.00", "Line 3: Total child care and attendant care expenses for you,
claimed by you or another person", "Line 4: Threshold for child and attendant care expenses
2,987.00", "Line 5: Line 3 minus line 4 (if negative, enter "0")", "Line 6: Line 2 minus line 5 (if
negative, enter "0")" and "Line 7: Line 1 plus line 6 Enter this amount on line 58440 of your Form
NL428. (maximum $10,981)".

Lines 1, 2 and 4 are printed figures, the datasets `ca-nl/disability_self_base_amount`,
`ca-nl/disability_self_supplement_maximum` and `ca-nl/disability_self_care_threshold`, each claimed
whole through core/credit_amount. Line 3 is the optional shared input
`ca/disability_self_care_expenses`, read as 0 when blank. Lines 5 and 6 are core/subtract_not_below
_zero steps and line 7 is a core/sum step, all rounded half-up to the cent through
`ca-nl/cent_rounding`. Only lines 5, 6 and 7 carry a reference; the printed-figure lines are steps
toward them, as the age amount's lines 1, 2 and 3 are. The "(maximum $10,981)" is line 1 plus line
2 and line 6 is never above line 2, so it cannot bind and is not a step.

The real parts are loaded under a test-local header and form declaration over the package list of
`support.py`.

Figures (hand-computed, not a CRA example): care expenses 4,987 give line 5 = 2,000.00, line 6 =
1,514.00 and line 7 = 8,981.00; none (blank) give 0.00, 3,514.00 and 10,981.00; 2,987 or less give
the same; 6,501 or more give line 6 = 0.00 and line 7 = 7,467.00; 3,000.005 gives line 5 = 13.01
(half-up) and line 6 = 3,500.99.
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
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
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

# care expenses, line 5, line 6, line 7.
CASES = [
    (None, "0.00", "3514.00", "10981.00"),
    ("0", "0.00", "3514.00", "10981.00"),
    ("2986.99", "0.00", "3514.00", "10981.00"),
    ("2987", "0.00", "3514.00", "10981.00"),
    ("2987.01", "0.01", "3513.99", "10980.99"),
    ("4987", "2000.00", "1514.00", "8981.00"),
    ("6500.99", "3513.99", "0.01", "7467.01"),
    ("6501", "3514.00", "0.00", "7467.00"),
    ("9000", "6013.00", "0.00", "7467.00"),
    ("3000.005", "13.01", "3500.99", "10967.99"),
]


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


@pytest.mark.parametrize(("care", "line_5", "line_6", "line_7"), CASES)
def test_lines_5_6_and_7_follow_the_worksheet(
    tmp_path: Path, care: str | None, line_5: str, line_6: str, line_7: str
) -> None:
    sheet = _sheet(tmp_path, care)

    assert _value(sheet, LINE_5) == D(line_5)
    assert _value(sheet, LINE_6) == D(line_6)
    assert _value(sheet, LINE_7) == D(line_7)


def test_the_printed_lines_1_2_and_4_are_the_dataset_figures(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path)

    assert _value(sheet, LINE_1) == D("7467.00")
    assert _value(sheet, LINE_2) == D("3514.00")
    assert _value(sheet, LINE_4) == D("2987.00")


def test_line_7_never_exceeds_the_printed_maximum_of_10981(tmp_path: Path) -> None:
    assert _value(_sheet(tmp_path), LINE_7) == D("10981.00")


def test_a_negative_care_expense_is_refused(tmp_path: Path) -> None:
    with pytest.raises(NegativeArtifactError):
        _sheet(tmp_path, "-0.01")


def test_the_trace_of_line_7_is_the_sum_of_lines_1_and_6(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "4987")

    (line,) = [each for each in sheet.trace if isinstance(each, SumLine)]
    assert line.output is newfoundland_kinds().kind(LINE_7)
    assert [(kind.identifier, value) for kind, value in line.parts] == [
        (LINE_1, D("7467.00")),
        (LINE_6, D("1514.00")),
    ]
    assert line.total == D("8981.00")


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_input_part_declares_the_under_18_answer_and_the_care_expenses() -> None:
    under_18, care = _part(INPUT_PART)["inputs"]

    assert under_18["name"] == "ca/under_18_on_december_31"
    assert under_18["reference"] == "58440"
    assert under_18["required"] is False
    assert under_18["default"] is None
    assert under_18["basis"] == (
        "Complete this calculation if you were under 18 years of age on December 31, 2025."
    )
    assert care["name"] == "ca/disability_self_care_expenses"
    assert care["reference"] == "3"
    assert care["unit"] == "ca/cad"
    assert care["required"] is False
    assert care["default"] is None


def test_line_5_part_is_the_threshold_and_the_subtraction_with_a_blank_read_as_0() -> None:
    part = _part(PART_5)

    assert part["form"] == {"name": FORM_NAME}
    threshold, subtract = part["capabilities"]
    assert threshold["name"] == "core/credit_amount"
    assert threshold["params"] == {"amount": "ca-nl/disability_self_care_threshold"}
    assert threshold["produces"] == {"output": LINE_4}
    assert "reference" not in threshold
    assert subtract["name"] == "core/subtract_not_below_zero"
    assert subtract["reference"] == "5"
    assert subtract["params"] == {"rounding": ROUNDING}
    assert subtract["consumes"] == {"amount": "ca/disability_self_care_expenses", "less": LINE_4}
    assert subtract["blank"] == {"amount": "0"}
    assert subtract["produces"] == {"output": LINE_5}


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


def test_line_7_part_is_the_base_amount_and_the_sum() -> None:
    part = _part(PART_7)

    assert part["form"] == {"name": FORM_NAME}
    base, total = part["capabilities"]
    assert base["name"] == "core/credit_amount"
    assert base["params"] == {"amount": "ca-nl/disability_self_base_amount"}
    assert base["produces"] == {"output": LINE_1}
    assert "reference" not in base
    assert total["name"] == "core/sum"
    assert total["reference"] == "7"
    assert total["params"] == {"rounding": ROUNDING}
    assert total["consumes"] == {"parts": [LINE_1, LINE_6]}
    assert "blank" not in total
    assert total["produces"] == {"output": LINE_7}


@pytest.mark.parametrize("identifier", [LINE_1, LINE_2, LINE_4, LINE_5, LINE_6, LINE_7])
def test_the_line_kinds_are_registered_non_negative_amounts_with_the_line_quoted(
    identifier: str,
) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert identifier.startswith("ca-nl/")
