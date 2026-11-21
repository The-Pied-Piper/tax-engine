"""NL428 (2025) line 104, line 98 minus line 103 (not below 0), real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 104: Line 98 minus line 103 (if negative,
enter "0")", and under line 87: "If you are claiming an amount on line 86, enter the amount from
line 87 on line 94, enter "0" on line 104, and continue on line 105." Four steps: a
core/subtract_not_below_zero over line 98 (the low-income tax reduction) and line 103, rounded
half-up to the cent by `ca-nl/cent_rounding`; a core/sum over line 86 alone (a blank read as 0); a
core/amount_by_band over that figure through the `ca-nl/low_income_reduction_line_86_gate` dataset
(1 at 0.00, 0 from one cent); and a core/multiply of the first figure by the gate, which is line 104
and the only step with the reference. The four steps carry plain-words titles, since the form
prints no title the engine takes for the line. Line 94 is line 87 whether or not line 86 is claimed
(a copy line with no step), so only line 104 changes with line 86.

Figures (hand-computed from the printed form, not a CRA example): line 98 is 997.00 at every salary
with lines 96 and 97 blank; line 103 is 0.00 / 7,265.12 at salaries of 20,000 / 70,000, so line
104 is 997.00 / 0.00. At a salary of 28,000 line 103 is 612.32 and line 104
is 384.68. With a line 86 of 500.00 line 104 is 0.00 at every salary, where line 98 less line 103 is
997.00 at a salary of 20,000.
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
from tests.manifest_support import inputs_without_form

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_PART = NL_PARTS / "nl428_line_104.yaml"
LINE_98 = "ca-nl/nl428_low_income_reduction_line_98"
LINE_103 = "ca-nl/nl428_line_103"
LINE_86 = "ca-nl/nl428_unused_low_income_reduction_from_spouse_line_86"
BEFORE_CHECK = "ca-nl/nl428_line_104_before_line_86_check"
CLAIMED_86 = "ca-nl/nl428_unused_low_income_reduction_from_spouse_claimed_line_86"
GATE = "ca-nl/nl428_line_104_line_86_gate"
IDENTIFIER = "ca-nl/nl428_line_104"
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
    "nl428_credits_line_61_input.yaml",
    "nl428_credits_line_62.yaml",
    "nl428_line_86_input.yaml",
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
    "nl428_line_95.yaml",
    "nl428_line_98.yaml",
    "nl428_line_104.yaml",
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
        - ca-nl/nl428_low_income_reduction_line_98
        - ca-nl/nl428_line_103
        - ca-nl/nl428_line_104
    capabilities: []
    """)


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


# salary, line 103, line 104: line 98 minus line 103, lines 96 and 97 blank.
@pytest.mark.parametrize(
    ("salary", "line_103", "expected"),
    [
        ("20000", "0.00", "997.00"),
        ("70000", "7265.12", "0.00"),
    ],
)
def test_line_104_is_line_98_minus_line_103(
    tmp_path: Path, salary: str, line_103: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, FORM_NAME)

    assert _value(sheet, LINE_98) == D("997.00")
    assert _value(sheet, LINE_103) == D(line_103)
    assert _value(sheet, IDENTIFIER) == D(expected)
    assert str(_value(sheet, IDENTIFIER)) == expected


def test_line_104_is_the_difference_when_line_103_is_below_line_98(tmp_path: Path) -> None:
    """At a salary of 28,000 line 101 is 3,827.00, line 103 is 612.32 and line 104 is 384.68."""
    sheet = _sheet(tmp_path, "28000", FORM_NAME)

    assert _value(sheet, LINE_98) == D("997.00")
    assert _value(sheet, LINE_103) == D("612.32")
    assert _value(sheet, IDENTIFIER) == D("384.68")


@pytest.mark.parametrize("salary", ["20000", "28000"])
def test_line_104_is_0_when_line_86_is_claimed(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, salary, FORM_NAME, {LINE_86: "500.00"})

    assert _value(sheet, CLAIMED_86) == D("500.00")
    assert _value(sheet, GATE) == D("0")
    assert _value(sheet, IDENTIFIER) == D("0.00")
    assert str(_value(sheet, IDENTIFIER)) == "0.00"


def test_line_104_before_the_line_86_check_is_still_line_98_minus_line_103(tmp_path: Path) -> None:
    """At a salary of 20,000 with a line 86 of 500.00 the figure before the check is 997.00 and
    line 104 is the printed 0."""
    sheet = _sheet(tmp_path, "20000", FORM_NAME, {LINE_86: "500.00"})

    assert _value(sheet, BEFORE_CHECK) == D("997.00")
    assert _value(sheet, IDENTIFIER) == D("0.00")


def test_line_104_is_0_when_line_86_is_one_cent(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000", FORM_NAME, {LINE_86: "0.01"})

    assert _value(sheet, GATE) == D("0")
    assert _value(sheet, IDENTIFIER) == D("0.00")


@pytest.mark.parametrize("given", [None, "0.00"])
def test_line_104_stands_when_line_86_is_blank_or_0(tmp_path: Path, given: str | None) -> None:
    lines = None if given is None else {LINE_86: given}

    sheet = _sheet(tmp_path, "20000", FORM_NAME, lines)

    assert _value(sheet, CLAIMED_86) == D("0.00")
    assert _value(sheet, GATE) == D("1")
    assert _value(sheet, IDENTIFIER) == D("997.00")


def test_line_104_is_four_titled_steps_and_only_the_last_is_line_104() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/subtract_not_below_zero",
                "title": "Low-income tax reduction before the line 86 rule",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"amount": LINE_98, "less": LINE_103},
                "produces": {"output": BEFORE_CHECK},
            },
            {
                "name": "core/sum",
                "title": (
                    "Unused low-income tax reduction from your spouse or common-law partner, "
                    "with a blank counted as 0"
                ),
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"parts": [LINE_86]},
                "blank": {"parts": "0"},
                "produces": {"output": CLAIMED_86},
            },
            {
                "name": "core/amount_by_band",
                "title": (
                    "Multiplier that is 0 when you claim your spouse's or common-law "
                    "partner's unused reduction"
                ),
                "unit": "ca/cad",
                "params": {"table": "ca-nl/low_income_reduction_line_86_gate"},
                "consumes": {"base": CLAIMED_86},
                "produces": {"output": GATE},
            },
            {
                "name": "core/multiply",
                "title": "Newfoundland and Labrador low-income tax reduction",
                "reference": "104",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"multiplicand": BEFORE_CHECK, "multiplier": GATE},
                "produces": {"output": IDENTIFIER},
            },
        ],
    }
