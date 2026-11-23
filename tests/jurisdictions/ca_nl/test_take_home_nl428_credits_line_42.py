"""NL428 (2025) line 42, add lines 39 to 41, from the salary alone, real parts.

Form text (Form NL428, CRA 5001-c-25e.txt, line 138): "Line 42: Add lines 39 to 41. = ^". Line 40
is the disability amount for self (7,467.00 when the claim is 1, 0.00 otherwise) and line 41 the
disability amount transferred from a dependant (an optional input); line 41 is blank for a
salary-only filer and read as 0. So line 42 is one core/sum over lines 39, 40 and 41 in line order.

The test composes the real parts behind lines 39 to 41 (the federal parts Worksheet NL428 needs,
the worksheet parts, lines 16 to 39, Schedule 8, T2204, lines 40 and 41) and the new
`nl428_credits_line_42.yaml`, and types in only the salary (and, in some tests, optional inputs).
The header and the two form declarations are made up here, because the shared scaffold owns them.
The figures are hand-computed from the printed form (not a CRA example): line 39 is line 36,
which is line 26 (the basic personal amount 11,067.00, the amount from line 25) plus line 35, and
line 35 is line 27 plus line 29 (1,144.75 / 4,433.58 at salaries of 20,000 /
200,000).
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_PART = NL_PARTS / "nl428_credits_line_42.yaml"
IDENTIFIER = "ca-nl/nl428_credits_subtotal_line_42"
LINE_39 = "ca-nl/nl428_credits_subtotal_line_39"
LINE_40 = "ca-nl/nl428_disability_amount_self_line_40"
LINE_41 = "ca-nl/nl428_disability_amount_transferred_from_a_dependant_line_41"
FORM_NAME = "ca-nl/nl428_credits"
FEDERAL_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
NL_PART_NAMES = (
    "worksheet_nl428_line_4.yaml",
    "worksheet_nl428_line_6.yaml",
    "worksheet_nl428_line_7.yaml",
    "worksheet_nl428_line_58080_input.yaml",
    "worksheet_nl428_line_58440_input.yaml",
    "worksheet_nl428_line_3_input.yaml",
    "worksheet_nl428_58440_line_5.yaml",
    "worksheet_nl428_58440_line_6.yaml",
    "worksheet_nl428_58440_line_7.yaml",
    "nl428_credits_line_16.yaml",
    "nl428_credits_line_17.yaml",
    "nl428_credits_line_22_input.yaml",
    "nl428_credits_line_23.yaml",
    "nl428_credits_line_24_input.yaml",
    "nl428_credits_line_25.yaml",
    "nl428_credits_line_27.yaml",
    "nl428_credits_line_28.yaml",
    "nl428_credits_line_29.yaml",
    "nl428_credits_line_30.yaml",
    "nl428_credits_line_31_input.yaml",
    "nl428_credits_line_32_input.yaml",
    "nl428_credits_line_33_input.yaml",
    "nl428_credits_line_34_input.yaml",
    "nl428_credits_line_35.yaml",
    "nl428_credits_line_36.yaml",
    "nl428_credits_line_37_input.yaml",
    "nl428_credits_line_37.yaml",
    "nl428_credits_line_38_input.yaml",
    "nl428_credits_line_39.yaml",
    "nl428_credits_line_40_input.yaml",
    "nl428_credits_line_40.yaml",
    "nl428_credits_line_41_input.yaml",
    "nl428_credits_line_42.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORMS = dedent("""\
    form:
      name: ca-nl/nl428_worksheet
      required: true
      exports:
        - ca-nl/worksheet_nl428_age_amount_line_7
        - ca-nl/worksheet_nl428_disability_self_line_7
    capabilities: []
    ---
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_credits_subtotal_line_42
    capabilities: []
    """)

# salary, line 42: line 39 (line 26 of 11,067.00 plus line 35), lines 40 and 41 being blank.
CASES = [
    ("20000", "12211.75"),
    ("200000", "15500.58"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in NL_PART_NAMES:
        yield NL_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Newfoundland and Labrador manifest of a test header, the form
    declarations and the real part files, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    forms = FORMS.split("---\n")
    for number, text in enumerate(forms, start=1):
        (folder / f"01_form_{number}.yaml").write_text(text, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
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


def _sheet(
    tmp_path: Path,
    salary: str,
    given_lines: dict[str, str] | None = None,
    claim: int | None = None,
) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if claim is not None:
        given.append(Artifact(NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40, claim))
    kinds = newfoundland_kinds()
    for identifier, amount in (given_lines or {}).items():
        given.append(Artifact(kinds.kind(identifier), D(amount)))
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NL"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_42_is_line_39_when_lines_40_and_41_are_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _value(sheet, LINE_39) == D(expected)
    assert _value(sheet, LINE_40) == D("0.00")
    assert _value(sheet, IDENTIFIER) == D(expected)


def test_line_42_adds_the_disability_amount_for_self(tmp_path: Path) -> None:
    # 12,211.75 plus 7,467.00 on line 40.
    sheet = _sheet(tmp_path, "20000", claim=1)

    assert _value(sheet, LINE_40) == D("7467.00")
    assert _value(sheet, IDENTIFIER) == D("19678.75")


def test_line_42_adds_the_disability_amount_transferred_from_a_dependant(tmp_path: Path) -> None:
    # 12,211.75 plus 1,500.25 on line 41.
    sheet = _sheet(tmp_path, "20000", {LINE_41: "1500.25"})

    assert _value(sheet, IDENTIFIER) == D("13712.00")


def test_line_42_adds_lines_39_40_and_41(tmp_path: Path) -> None:
    # 12,211.75 plus 7,467.00 on line 40 plus 1,500.25 on line 41.
    sheet = _sheet(tmp_path, "20000", {LINE_41: "1500.25"}, claim=1)

    assert _value(sheet, IDENTIFIER) == D("21179.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_lines_39_to_41() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "42",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nl/cent_rounding"},
        "consumes": {"parts": [LINE_39, LINE_40, LINE_41]},
        "blank": {LINE_41: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_42_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert kind is nl_catalog.NL428_CREDITS_SUBTOTAL_LINE_42
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
