"""NL428 (2025) line 58, line 56 multiplied by the 8.7% rate, from the salary, real parts.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 58 and line 58840: Line 56
multiplied by the percentage from line 57 =". Line 57 is the printed 8.7% (`ca-nl/credit_rate`, no
step). Line 58 is one core/apply_rate step over line 56 (`nl428_credits_line_56.yaml`), rounded
half-up to the cent by the dataset. The form prints no label for the line, so the step has no title.

The test composes the real parts behind line 56 and the new `nl428_credits_line_58.yaml`. The
figures are hand-computed from the printed form (not a CRA example): line 56 is 12,211.75 /
15,500.58 at salaries of 20,000 / 200,000.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
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
LINE_PART = NL_PARTS / "nl428_credits_line_58.yaml"
LINE_56 = "ca-nl/nl428_credits_total_line_56"
IDENTIFIER = "ca-nl/nl428_credits_at_rate_line_58"
LINE_47 = "ca-nl/nl428_credits_subtotal_line_47"
LINE_55 = "ca-nl/nl428_medical_expenses_allowable_line_55"
LINE_48 = "ca/medical_expenses"
FORM_NAME = "ca-nl/nl428_credits"
FEDERAL_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
NL_PART_NAMES = (
    "worksheet_nl428_line_4.yaml",
    "worksheet_nl428_line_6.yaml",
    "worksheet_nl428_line_7.yaml",
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
    "nl428_credits_line_43.yaml",
    "nl428_credits_line_44_input.yaml",
    "nl428_credits_line_45_input.yaml",
    "nl428_credits_line_46_input.yaml",
    "nl428_credits_line_47.yaml",
    "nl428_credits_line_48.yaml",
    "nl428_credits_line_49.yaml",
    "nl428_credits_line_51.yaml",
    "nl428_credits_line_52.yaml",
    "nl428_credits_line_53.yaml",
    "nl428_credits_line_54_input.yaml",
    "nl428_credits_line_55.yaml",
    "nl428_credits_line_56.yaml",
    "nl428_credits_line_58.yaml",
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
        - ca-nl/worksheet_nl428_age_amount_maximum_line_1
        - ca-nl/worksheet_nl428_age_amount_line_7
        - ca-nl/worksheet_nl428_disability_self_line_7
    capabilities: []
    ---
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_credits_at_rate_line_58
    capabilities: []
    """)

# salary, line 56, line 58: no medical expenses, so line 56 is line 47.
CASES = [
    ("20000", "12211.75", "1062.42"),
    ("200000", "15500.58", "1348.55"),
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
    for number, found in enumerate(dict.fromkeys(_part_files()), start=2):
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
) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
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


@pytest.mark.parametrize(("salary", "line_56", "expected"), CASES)
def test_line_58_is_line_56_times_8_point_7_percent(
    tmp_path: Path, salary: str, line_56: str, expected: str
) -> None:
    assert (D(line_56) * D("0.087")).quantize(D("0.01"), rounding=ROUND_HALF_UP) == D(expected)

    sheet = _sheet(tmp_path, salary)

    assert _value(sheet, LINE_56) == D(line_56)
    assert _value(sheet, IDENTIFIER) == D(expected)


def test_line_58_rounds_half_up_to_the_cent(tmp_path: Path) -> None:
    # Line 56 is 12,211.75 plus 2,404.95 = 14,616.70; 14,616.70 times 0.087 = 1,271.6529.
    sheet = _sheet(tmp_path, "20000", {LINE_48: "3000"})

    assert _value(sheet, LINE_56) == D("14616.70")
    assert _value(sheet, IDENTIFIER) == D("1271.65")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_untitled_apply_rate_step_over_line_56() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "58",
        "unit": "ca/cad",
        "params": {"rate": "ca-nl/credit_rate"},
        "consumes": {"base": LINE_56},
        "produces": {"output": IDENTIFIER},
    }


def test_line_58_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert kind is nl_catalog.NL428_CREDITS_AT_RATE_LINE_58
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
