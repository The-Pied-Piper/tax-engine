"""NL428 (2025) line 105, line 94 minus line 104 (not below 0), real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 94: Amount from line 87 of the previous
page", "Line 104: Line 98 minus line 103 (if negative, enter \"0\")" and "Line 105: Line 94 minus
line 104 (if negative, enter \"0\") Enter this amount on line 42800 of your return. Newfoundland
and Labrador tax =". One core/subtract_not_below_zero step over line 94 and line 104, rounded
half-up to the cent by `ca-nl/cent_rounding`. Line 94 is a copy of line 87 and has no step (owner
ruling, 18 Nov 2026), so the step reads line 87. The form prints no title for the line, so the step
is untitled. The form's branch for a claim on line 86 (enter 0 on line 104) is built in line 104,
so with line 86 claimed line 105 is line 87.

Figures (hand-computed from the printed form, not a CRA example): line 87 is 663.23 / 6,147.49
and line 104 is 997.00 / 0.00 at salaries of 20,000 / 70,000, so line 105 is 0.00 / 6,147.49. At a
salary of 28,000 line 104 is 384.68 and line 87 is 1,306.40, so line 105 is 921.72. With a line 86
of 500.00 at a salary of 20,000 line 87 is 163.23 and line 104 is 0.00, so line 105 is 163.23; at a
salary of 70,000 line 87 is 5,647.49 and line 105 is 5,647.49.
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
LINE_PART = NL_PARTS / "nl428_line_105.yaml"
LINE_87 = "ca-nl/nl428_tax_line_87"
LINE_86 = "ca-nl/nl428_unused_low_income_reduction_from_spouse_line_86"
LINE_104 = "ca-nl/nl428_line_104"
IDENTIFIER = "ca-nl/nl428_newfoundland_and_labrador_tax_line_105"
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
    "nl428_line_78_input.yaml",
    "nl428_line_79.yaml",
    "nl428_line_80_input.yaml",
    "nl428_line_81.yaml",
    "nl428_line_84_input.yaml",
    "nl428_line_85.yaml",
    "nl428_line_86_input.yaml",
    "nl428_line_87.yaml",
    "nl428_line_96_input.yaml",
    "nl428_line_96.yaml",
    "nl428_line_97.yaml",
    "nl428_line_100.yaml",
    "nl428_line_88.yaml",
    "nl428_line_89_input.yaml",
    "nl428_line_90.yaml",
    "nl428_line_91_input.yaml",
    "nl428_line_92.yaml",
    "nl428_line_88_column_2_input.yaml",
    "nl428_line_89_column_2_input.yaml",
    "nl428_line_90_column_2.yaml",
    "nl428_line_91_column_2_input.yaml",
    "nl428_line_92_column_2.yaml",
    "nl428_line_93.yaml",
    "nl428_line_101.yaml",
    "nl428_line_103.yaml",
    "nl428_line_95.yaml",
    "nl428_line_98.yaml",
    "nl428_line_104.yaml",
    "nl428_line_105.yaml",
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
        - ca-nl/nl428_tax_on_taxable_income_line_8
        - ca-nl/nl428_tax_on_taxable_income_line_15
    capabilities: []
    ---
    form:
      name: ca-nl/nl428
      required: true
      exports:
        - ca-nl/nl428_adjusted_family_income_line_93
        - ca-nl/nl428_low_income_threshold_line_100
        - ca-nl/nl428_line_101
        - ca-nl/nl428_low_income_reduction_line_98
        - ca-nl/nl428_line_103
        - ca-nl/nl428_newfoundland_and_labrador_tax_line_105
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


# salary, line 87, line 104, line 105: line 94 (a copy of line 87) minus line 104, lines 86, 96 and
# 97 blank.
@pytest.mark.parametrize(
    ("salary", "line_87", "line_104", "expected"),
    [
        ("20000", "663.23", "997.00", "0.00"),
        ("70000", "6147.49", "0.00", "6147.49"),
    ],
)
def test_line_105_is_line_87_minus_line_104(
    tmp_path: Path, salary: str, line_87: str, line_104: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, FORM_NAME)

    assert _value(sheet, LINE_87) == D(line_87)
    assert _value(sheet, LINE_104) == D(line_104)
    assert _value(sheet, IDENTIFIER) == D(expected)
    assert str(_value(sheet, IDENTIFIER)) == expected


def test_line_105_is_the_difference_when_line_104_is_below_line_87(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "28000", FORM_NAME)

    assert _value(sheet, LINE_104) == D("384.68")
    assert _value(sheet, LINE_87) == D("1306.40")
    assert _value(sheet, IDENTIFIER) == D("921.72")


@pytest.mark.parametrize(
    ("salary", "line_87"),
    [("20000", "163.23"), ("70000", "5647.49")],
)
def test_line_105_is_line_87_when_line_86_is_claimed(
    tmp_path: Path, salary: str, line_87: str
) -> None:
    sheet = _sheet(tmp_path, salary, FORM_NAME, {LINE_86: "500.00"})

    assert _value(sheet, LINE_87) == D(line_87)
    assert _value(sheet, LINE_104) == D("0.00")
    assert _value(sheet, IDENTIFIER) == D(line_87)


def test_line_105_is_one_untitled_subtract_not_below_zero_step() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/subtract_not_below_zero",
                "reference": "105",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"amount": LINE_87, "less": LINE_104},
                "produces": {"output": IDENTIFIER},
            }
        ],
    }
