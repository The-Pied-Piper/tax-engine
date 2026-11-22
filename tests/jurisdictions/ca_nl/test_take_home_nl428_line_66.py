"""NL428 (2025) line 66, non-refundable tax credits from line 62, real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 66: Newfoundland and Labrador
non-refundable tax credits from line 62 ^". Line 66 is a copy of line 62, which sits on the other
form `ca-nl/nl428_credits` (lines 1 to 62), so its one step is a `core/record_total` over that
form's line 62 export, read as a record list.

The test composes the real parts behind line 62 and the new `nl428_line_66.yaml`. The figures are
line 62 with line 61 blank (hand-computed from the printed form, not a CRA example): 1,062.42 /
1,348.55 at salaries of 20,000 / 200,000.
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
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
LINE_PART = NL_PARTS / "nl428_line_66.yaml"
AMOUNT_59 = "ca-nl/nl428_donations_amount_line_59"
AMOUNT_60 = "ca-nl/nl428_donations_amount_line_60"
LINE_62 = "ca-nl/nl428_non_refundable_credits_line_62"
IDENTIFIER = "ca-nl/nl428_non_refundable_credits_line_66"
FORM_NAME = "ca-nl/nl428"
FEDERAL_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")
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
    "nl428_credits_line_37_input.yaml",
    "nl428_credits_line_37.yaml",
    "nl428_credits_line_38_input.yaml",
    "nl428_credits_line_39.yaml",
    "nl428_credits_line_40_input.yaml",
    "nl428_credits_line_40.yaml",
    "nl428_credits_line_41_input.yaml",
    "nl428_credits_line_42.yaml",
    "nl428_credits_line_43_input.yaml",
    "nl428_credits_line_44_input.yaml",
    "nl428_credits_line_45_input.yaml",
    "nl428_credits_line_46_input.yaml",
    "nl428_credits_line_47.yaml",
    "nl428_credits_line_48_input.yaml",
    "nl428_credits_line_49.yaml",
    "nl428_credits_line_51.yaml",
    "nl428_credits_line_52.yaml",
    "nl428_credits_line_53.yaml",
    "nl428_credits_line_54_input.yaml",
    "nl428_credits_line_55.yaml",
    "nl428_credits_line_56.yaml",
    "nl428_credits_line_58.yaml",
    "nl428_credits_line_59_input.yaml",
    "nl428_credits_line_59.yaml",
    "nl428_credits_line_60_input.yaml",
    "nl428_credits_line_60.yaml",
    "nl428_credits_line_61.yaml",
    "nl428_credits_line_62.yaml",
    "nl428_line_66.yaml",
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
        - ca-nl/nl428_non_refundable_credits_line_62
    capabilities: []
    ---
    form:
      name: ca-nl/nl428
      required: true
      exports:
        - ca-nl/nl428_non_refundable_credits_line_66
    capabilities: []
    """)

# salary, line 66: line 62 with line 61 blank, so line 58.
CASES = [
    ("20000", "1062.42"),
    ("200000", "1348.55"),
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
    form: str,
    given_lines: dict[str, str] | None = None,
) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    kinds = newfoundland_kinds()
    for identifier, amount in (given_lines or {}).items():
        given.append(Artifact(kinds.kind(identifier), D(amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_66_is_line_62_read_across_the_forms(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_62 = _value(_sheet(tmp_path / "credits", salary, "ca-nl/nl428_credits"), LINE_62)
    line_66 = _value(_sheet(tmp_path / "tax", salary, FORM_NAME), IDENTIFIER)

    assert line_62 == line_66 == D(expected)


def test_line_66_follows_line_61_through_line_62(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", FORM_NAME, {AMOUNT_59: "1000", AMOUNT_60: "1000"})

    # 1,342.95 plus 87.00 and 218.00 (8.7% and 21.8% of 1,000 each).
    assert _value(sheet, IDENTIFIER) == D("1647.95")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_titled_record_total_over_the_credits_form_line_62_export() -> None:
    part = _part()

    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": "Newfoundland and Labrador non-refundable tax credits from line 62",
        "reference": "66",
        "unit": "ca/cad",
        "consumes": {"records": "ca-nl/nl428_credits.nl428_non_refundable_credits_line_62"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_66_is_a_registered_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert kind is nl_catalog.NL428_NON_REFUNDABLE_CREDITS_LINE_66
    assert non_negative(kind)
