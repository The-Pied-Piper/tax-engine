"""NL428 (2025) line 101, line 99 minus line 100 (not below 0), real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 99: Amount from line 93" and "Line
101: Line 99 minus line 100 (if negative, enter "0") =". One core/subtract_not_below_zero step over
line 93 (line 99 is its copy) and line 100, rounded half-up to the cent by `ca-nl/cent_rounding`.
The form prints no title for the line, so the step is untitled.

Figures (hand-computed from the printed form, not a CRA example): line 93 is 19,835.00 / 69,335.00
and line 100 is 23,928 at salaries of 20,000 / 70,000, so line 101 is 0.00 / 45,407.00. With an
amount claimed on line 96, line 100 is 40,460 and line 101 at a salary of 70,000 is 28,875.00.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import CountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.manifest_support import inputs_without_form

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = NL_PARTS / "nl428_line_101.yaml"
LINE_22 = "ca-nl/nl428_eligible_dependant_net_income_line_22"
LINE_93 = "ca-nl/nl428_adjusted_family_income_line_93"
LINE_100 = "ca-nl/nl428_low_income_threshold_line_100"
IDENTIFIER = "ca-nl/nl428_line_101"
LINE_96 = "ca-nl/nl428_reduction_for_spouse_or_common_law_partner_claimed_line_96"
FORM_NAME = "ca-nl/nl428"
FEDERAL_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200.yaml",
)
NL_PART_NAMES = (
    "worksheet_nl428_line_4.yaml",
    "worksheet_nl428_line_6.yaml",
    "worksheet_nl428_line_7.yaml",
    "worksheet_nl428_line_58080_input.yaml",
    "worksheet_nl428_line_58440_input.yaml",
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
    "nl428_credits_line_61_input.yaml",
    "nl428_credits_line_62.yaml",
    "nl428_line_96_input.yaml",
    "nl428_line_96.yaml",
    "nl428_line_97.yaml",
    "nl428_line_100.yaml",
    "nl428_line_88.yaml",
    "nl428_line_89.yaml",
    "nl428_line_90.yaml",
    "nl428_line_91.yaml",
    "nl428_line_92.yaml",
    "nl428_line_88_column_2_input.yaml",
    "nl428_line_89_column_2_input.yaml",
    "nl428_line_90_column_2.yaml",
    "nl428_line_91_column_2_input.yaml",
    "nl428_line_92_column_2.yaml",
    "nl428_line_93.yaml",
    "nl428_line_101.yaml",
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
        - ca-nl/worksheet_nl428_disability_self_line_7
    capabilities: []
    ---
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_eligible_dependant_amount_line_23
        - ca-nl/nl428_non_refundable_credits_line_62
    capabilities: []
    ---
    form:
      name: ca-nl/nl428
      required: true
      exports:
        - ca-nl/nl428_adjusted_family_income_line_93
        - ca-nl/nl428_low_income_threshold_line_100
        - ca-nl/nl428_line_101
    capabilities: []
    """)


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


def _sheet(
    tmp_path: Path,
    salary: str,
    form: str,
    given_lines: dict[str, str] | None = None,
) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    kinds = newfoundland_kinds()
    for identifier, amount in (given_lines or {}).items():
        kind = kinds.kind(identifier)
        given.append(Artifact(kind, int(amount) if isinstance(kind, CountKind) else D(amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


# salary, line 101: line 99 (line 93) minus line 100, line 96 and line 97 blank.
@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "45407.00")],
)
def test_line_101_is_line_93_minus_line_100_not_below_zero(
    tmp_path: Path, salary: str, expected: str
) -> None:
    value = _value(_sheet(tmp_path, salary, FORM_NAME), IDENTIFIER)

    assert value == D(expected)
    assert str(value) == expected


def test_line_101_takes_the_larger_line_100_when_line_96_is_claimed(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", FORM_NAME, {LINE_96: "1"})

    assert _value(sheet, LINE_93) == D("69335.00")
    assert _value(sheet, LINE_100) == D("40460")
    assert _value(sheet, IDENTIFIER) == D("28875.00")


def test_line_101_is_one_untitled_subtract_step_over_line_93_and_line_100() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/subtract_not_below_zero",
                "reference": "101",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"amount": LINE_93, "less": LINE_100},
                "produces": {"output": IDENTIFIER},
            }
        ],
    }
