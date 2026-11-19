"""NL428 (2025) line 36, line 26 plus line 35, from the salary alone, real parts.

Form text (Form NL428, CRA 5001-c-25e.txt, lines 118 and 130): "Line 26: Amount from line 25 of the
previous page ^" and "Line 36: Line 26 plus line 35 = ^". Line 26 is a copy of line 25 and has no
step, so line 36 is one core/sum over line 25 and line 35 in line order.

The test composes the real parts behind lines 25 and 35 (the federal parts Worksheet NL428 needs,
the worksheet parts, lines 16 to 25, Schedule 8, T2204 and lines 27 to 35) and the new
`nl428_credits_line_36.yaml`, and types in only the salary (and, in some tests, optional inputs).
The header and the two form declarations are made up here, because the shared scaffold owns them.
The figures are hand-computed from the printed form (not a CRA example): line 25 is the basic
personal amount 11,067.00 and line 35 is line 27 plus line 29 (1,144.75 / 4,369.23 / 4,433.58 at
salaries of 20,000 / 70,000 / 200,000).
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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = NL_PARTS / "nl428_credits_line_36.yaml"
IDENTIFIER = "ca-nl/nl428_credits_subtotal_line_36"
FORM_NAME = "ca-nl/nl428_credits"
LINE_25 = "ca-nl/nl428_credits_subtotal_line_25"
LINE_35 = "ca-nl/nl428_cpp_ei_and_other_line_35"
LINE_34 = "ca-nl/nl428_adoption_expenses_line_34"
LINE_24 = "ca-nl/nl428_infirm_dependants_amount_line_24"
FEDERAL_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
)
NL_PART_NAMES = (
    "worksheet_nl428_line_4.yaml",
    "worksheet_nl428_line_6.yaml",
    "worksheet_nl428_line_7.yaml",
    "worksheet_nl428_line_58080_input.yaml",
    "nl428_credits_line_16.yaml",
    "nl428_credits_line_17.yaml",
    "nl428_credits_line_19_input.yaml",
    "nl428_credits_line_20.yaml",
    "nl428_credits_line_22_input.yaml",
    "nl428_credits_line_23.yaml",
    "nl428_credits_line_24_input.yaml",
    "nl428_credits_line_25.yaml",
    "nl428_credits_line_27.yaml",
    "nl428_credits_line_28_input.yaml",
    "nl428_credits_line_29.yaml",
    "nl428_credits_line_30_input.yaml",
    "nl428_credits_line_31_input.yaml",
    "nl428_credits_line_32_input.yaml",
    "nl428_credits_line_33_input.yaml",
    "nl428_credits_line_34_input.yaml",
    "nl428_credits_line_35.yaml",
    "nl428_credits_line_36.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        title: "Employment income"
        reference: "10100"
        unit: ca/cad
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORMS = dedent("""\
    form:
      name: ca-nl/nl428_worksheet
      required: true
      exports:
        - ca-nl/worksheet_nl428_age_amount_line_7
    capabilities: []
    ---
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_credits_subtotal_line_36
    capabilities: []
    """)

# salary, line 36: line 25 (11,067.00) plus line 35.
CASES = [
    ("20000", "12211.75"),
    ("70000", "15436.23"),
    ("200000", "15500.58"),
]


def _part_files() -> Iterator[Path]:
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
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
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
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


def _sheet(tmp_path: Path, salary: str, given_lines: dict[str, str] | None = None) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    kinds = newfoundland_kinds()
    for identifier, amount in (given_lines or {}).items():
        given.append(Artifact(kinds.kind(identifier), D(amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_36_adds_line_25_and_line_35(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _value(sheet, LINE_25) == D("11067.00")
    assert _value(sheet, IDENTIFIER) == D(expected)


def test_line_36_adds_an_optional_line_feeding_line_25(tmp_path: Path) -> None:
    # 11,067.00 plus 100.25 on line 24 plus 1,144.75 on line 35.
    sheet = _sheet(tmp_path, "20000", {LINE_24: "100.25"})

    assert _value(sheet, IDENTIFIER) == D("12312.00")


def test_line_36_adds_an_optional_line_feeding_line_35(tmp_path: Path) -> None:
    # 11,067.00 plus 1,144.75 plus 100.25 on line 34.
    sheet = _sheet(tmp_path, "20000", {LINE_34: "100.25"})

    assert _value(sheet, LINE_35) == D("1245.00")
    assert _value(sheet, IDENTIFIER) == D("12312.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_lines_25_and_35() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "36",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nl/cent_rounding"},
        "consumes": {"parts": [LINE_25, LINE_35]},
        "produces": {"output": IDENTIFIER},
    }


def test_line_36_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert kind is nl_catalog.NL428_CREDITS_SUBTOTAL_LINE_36
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
