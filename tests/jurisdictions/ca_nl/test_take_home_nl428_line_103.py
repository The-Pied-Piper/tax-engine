"""NL428 (2025) line 103, line 101 multiplied by the 16% rate, real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 102: Applicable rate 16%" and "Line
103: Line 101 multiplied by the percentage from line 102 =". Line 102 is the printed 16%, the
`ca-nl/low_income_reduction_rate` dataset, and has no step. One core/apply_rate step applies it to
line 101, rounded half-up to the cent by the dataset's rule. The form prints no title for the
line, so the step is untitled.

Figures (hand-computed from the printed form, not a CRA example): line 101 is 0.00 / 45,407.00
at salaries of 20,000 / 70,000, so line 103 is 0.00 / 7,265.12.
With an amount claimed on line 96, line 101 at a salary of 70,000 is 28,875.00 and line 103 is
4,620.00.
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
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_PART = NL_PARTS / "nl428_line_103.yaml"
LINE_22 = "ca-nl/nl428_eligible_dependant_net_income_line_22"
LINE_93 = "ca-nl/nl428_adjusted_family_income_line_93"
LINE_100 = "ca-nl/nl428_low_income_threshold_line_100"
LINE_101 = "ca-nl/nl428_line_101"
IDENTIFIER = "ca-nl/nl428_line_103"
LINE_96 = "ca-nl/nl428_reduction_for_spouse_or_common_law_partner_claimed_line_96"
FORM_NAME = "ca-nl/nl428"
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
    "nl428_credits_line_19_input.yaml",
    "nl428_credits_line_20.yaml",
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
    "nl428_credits_line_59.yaml",
    "nl428_credits_line_60.yaml",
    "nl428_credits_line_61.yaml",
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
    "nl428_line_103.yaml",
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
        - ca-nl/nl428_line_103
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("schedule_9")
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
        kind = kinds.kind(identifier)
        given.append(Artifact(kind, int(amount) if isinstance(kind, CountKind) else D(amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


# salary, line 103: line 101 times 16%, line 96 and line 97 blank.
@pytest.mark.parametrize(
    ("salary", "line_101", "expected"),
    [
        ("20000", "0.00", "0.00"),
        ("70000", "45407.00", "7265.12"),
    ],
)
def test_line_103_is_line_101_times_16_percent(
    tmp_path: Path, salary: str, line_101: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, FORM_NAME)

    assert _value(sheet, LINE_101) == D(line_101)
    assert (D(line_101) * D("0.16")).quantize(D("0.01")) == D(expected)
    assert _value(sheet, IDENTIFIER) == D(expected)
    assert str(_value(sheet, IDENTIFIER)) == expected


def test_line_103_follows_line_101_when_line_96_is_claimed(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", FORM_NAME, {LINE_96: "1"})

    assert _value(sheet, LINE_101) == D("28875.00")
    assert _value(sheet, IDENTIFIER) == D("4620.00")


def test_line_103_is_one_untitled_apply_rate_step_over_line_101() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/apply_rate",
                "reference": "103",
                "unit": "ca/cad",
                "params": {"rate": "ca-nl/low_income_reduction_rate"},
                "consumes": {"base": LINE_101},
                "produces": {"output": IDENTIFIER},
            }
        ],
    }
