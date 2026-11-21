"""NL428 (2025) line 77, line 74 minus line 76 (not below 0), real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 77: Line 74 minus line 76 (if negative,
enter "0") =". One core/subtract_not_below_zero step over line 74 and line 76 (the political
contribution tax credit, an optional input read as 0 when blank), rounded half-up to the cent by
`ca-nl/cent_rounding`. The form prints no title for the line, so the step is untitled.

Figures (hand-computed from the printed form, not a CRA example), with line 76 blank: line 74 is
663.23 / 27,192.33 at salaries of 20,000 / 200,000, so line 77 is the same. With
a line 76 of 500.00, line 77 at a salary of 70,000 is 5,647.49; with a line 76 of 500.00 at a
salary of 15,000 (line 74 is 261.24) it is 0.00.
A line 76 above the printed maximum of 500.00 is refused.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
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
LINE_74 = "ca-nl/nl428_tax_line_74"
LINE_76 = "ca-nl/nl428_political_contribution_tax_credit_claimed_line_76"
IDENTIFIER = "ca-nl/nl428_tax_line_77"
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
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)
NL_PART_NAMES = (
    *(
        f"nl428_credits_line_{number}.yaml"
        for number in (1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15)
    ),
    "nl428_line_63.yaml",
    "nl428_line_64_input.yaml",
    "nl428_line_65.yaml",
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
    "nl428_line_66.yaml",
    "nl428_line_67_input.yaml",
    "nl428_line_68_inputs.yaml",
    "nl428_line_68.yaml",
    "nl428_line_69.yaml",
    "nl428_line_70.yaml",
    "nl428_line_71_input.yaml",
    "nl428_line_71.yaml",
    "nl428_line_72.yaml",
    "nl428_line_73_input.yaml",
    "nl428_line_74.yaml",
    "nl428_line_76_input.yaml",
    "nl428_line_76.yaml",
    "nl428_line_77.yaml",
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
        - ca-nl/nl428_non_refundable_credits_line_62
        - ca-nl/nl428_tax_on_taxable_income_line_8
        - ca-nl/nl428_tax_on_taxable_income_line_15
    capabilities: []
    ---
    form:
      name: ca-nl/nl428
      required: true
      exports:
        - ca-nl/nl428_tax_line_77
    capabilities: []
    """)

# salary, line 77: line 74 minus line 76, line 76 blank.
CASES = [
    ("20000", "663.23"),
    ("200000", "27192.33"),
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
def test_line_77_is_line_74_when_line_76_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    value = _value(_sheet(tmp_path, salary, FORM_NAME), IDENTIFIER)

    assert value == D(expected)
    assert str(value) == expected


def test_line_77_is_line_74_minus_line_76(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", FORM_NAME, {LINE_76: "500.00"})

    assert _value(sheet, LINE_74) == D("6147.49")
    assert _value(sheet, IDENTIFIER) == D("5647.49")


def test_line_77_is_not_below_zero(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "15000", FORM_NAME, {LINE_76: "500.00"})

    assert _value(sheet, LINE_74) == D("261.24")
    assert _value(sheet, IDENTIFIER) == D("0.00")


def test_a_line_76_above_the_maximum_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(tmp_path, "70000", FORM_NAME, {LINE_76: "500.01"})
