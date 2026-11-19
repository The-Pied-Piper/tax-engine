"""Worksheet NL428 (2025) line 58440 line 7, line 1 plus line 6, from the real parts.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt, confirmed 2026-11-19), section
"Line 58440 - Disability amount for self": "Complete this calculation if you were under 18 years of
age on December 31, 2025."
"Line 1: Base amount 7,467.00" and "Line 7: Line 1 plus line 6 Enter this amount on line 58440 of
your Form NL428. (maximum $10,981)". Line 1 is the `ca-nl/disability_self_base_amount` dataset
claimed whole (reference "1"). Line 7 is core/sum rounded half-up to the cent and carries the
reference "7". The "(maximum $10,981)" is line 1 plus line 2 and line 6 is never above line 2, so it
cannot bind and is not a step.

Care expenses 4,987 give line 7 = 8,981.00; none give 10,981.00; 6,501 or more give 7,467.00.

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
    (None, "10981.00"),
    ("4987", "8981.00"),
    ("6501", "7467.00"),
    ("3000.005", "10967.99"),
]


@pytest.mark.parametrize(("care", "line_7"), CASES)
def test_line_7_is_the_base_amount_plus_line_6(
    tmp_path: Path, care: str | None, line_7: str
) -> None:
    assert _value(_sheet(tmp_path, care), LINE_7) == D(line_7)


def test_line_1_is_the_printed_base_amount(tmp_path: Path) -> None:
    assert _value(_sheet(tmp_path), LINE_1) == D("7467.00")


def test_line_7_never_exceeds_the_printed_maximum_of_10981(tmp_path: Path) -> None:
    assert _value(_sheet(tmp_path), LINE_7) == D("10981.00")


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


def test_line_7_part_is_the_base_amount_and_the_sum() -> None:
    part = _part(PART_7)

    assert part["form"] == {"name": FORM_NAME}
    base, total = part["capabilities"]
    assert base["name"] == "core/credit_amount"
    assert base["params"] == {"amount": "ca-nl/disability_self_base_amount"}
    assert base["produces"] == {"output": LINE_1}
    assert base["reference"] == "1"
    assert total["name"] == "core/sum"
    assert total["reference"] == "7"
    assert total["params"] == {"rounding": ROUNDING}
    assert total["consumes"] == {"parts": [LINE_1, LINE_6]}
    assert "blank" not in total
    assert total["produces"] == {"output": LINE_7}


@pytest.mark.parametrize("identifier", [LINE_1, LINE_7])
def test_the_line_kinds_are_registered_non_negative_amounts_with_the_line_quoted(
    identifier: str,
) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert identifier.startswith("ca-nl/")
