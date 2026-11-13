"""AB428 (2025) line 75, line 73 minus line 74 (not below 0), from the real parts.

Form text (Form AB428, CRA 5009-c): "Line 75: Line 73 minus line 74 (if negative, enter \\"0\\")
Enter this amount on line 42800 of your return. Alberta tax =". The form prints no title for
line 75 beyond its label, so the step is untitled.

Line 75 is one core/subtract_not_below_zero step (`ab428_line_75.yaml`), rounded through
`ca-ab/cent_rounding`, with `amount` line 73 (`ca-ab/ab428_tax_line_73`, non-negative) and `less`
line 74 (`ca-ab/ab428_supplemental_tax_credit_line_74`, non-negative). Line 74 is always computed
(a record_total over the line 9 of Worksheet AB428, never blank), so the step has no blank rule
and prints no "Left blank" row. The form floors line 75 at 0 (printed), so the output
`ca-ab/ab428_alberta_tax_line_75` is a non-negative kind on the form `ca-ab/ab428`.

The test composes the real parts that lead to line 73 (the salary, the federal T1 taxable income
parts, AB428 lines 1 to 73, Schedule 8 and T2204), the real Worksheet AB428 parts for lines 1, 2,
3, 5, 6, 7 and 9, the real line 74 part, plus the new `ab428_line_75.yaml`. Three form declarations
are test-local: `ca-ab/ab428_credits`, `ca-ab/worksheet_ab428` and `ca-ab/ab428` export what the
other parts read (the real `ab428.yaml` exports line 75 and is not composed here).

Figures (hand-computed from the printed forms and the repo figures, not a CRA example): line 73 is
0.00 / 3,598.12 / 17,680.36 at a salary of 20,000 / 70,000 / 200,000, and line 74 is 0.00 at all
three (worksheet line 5 is below line 6's 4,800.00), so line 75 is 0.00 / 3,598.12 / 17,680.36.
With a given line 51 (`ab428_medical_expenses_line_51`) of 200,000, line 74 turns positive; line 75
is then recomputed in the test as line 73 minus line 74, not below 0, half-up to the cent, and at
the lowest salary line 74 exceeds line 73, which exercises the floor through the real chain.
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
import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_ab.catalog as ab_catalog
import tax_engine.jurisdictions.ca_ab.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
)
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-AB")
TAX = "ca-ab/ab428"
LINE_51 = "ca-ab/ab428_medical_expenses_line_51"
LINE_73 = "ca-ab/ab428_tax_line_73"
LINE_74 = "ca-ab/ab428_supplemental_tax_credit_line_74"
LINE_75 = "ca-ab/ab428_alberta_tax_line_75"
ROUNDING = "ca-ab/cent_rounding"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "ab428_line_75.yaml"
T1_PARTS = (
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
# The real Alberta parts after the federal ones, in composition order: lines 1 to 15 and 59 to 61,
# then lines 16 to 58 and 62 to 65, then lines 66 and 67, then lines 68 to 70, then line 72, then
# line 73, then the supplemental credit chain (worksheet lines 1 to 9, then line 74), then line 75.
ALBERTA_LINE_PARTS = (
    "ab428_credits_line_1.yaml",
    "ab428_line_3.yaml",
    "ab428_line_4.yaml",
    "ab428_credits_line_5.yaml",
    "ab428_line_6.yaml",
    "ab428_line_7.yaml",
    "ab428_line_8.yaml",
    "ab428_line_10.yaml",
    "ab428_line_11.yaml",
    "ab428_line_12.yaml",
    "ab428_line_13.yaml",
    "ab428_line_14.yaml",
    "ab428_line_15.yaml",
    "ab428_line_59.yaml",
    "ab428_line_60_inputs.yaml",
    "ab428_line_61.yaml",
    "ab428_line_16.yaml",
    "ab428_line_25.yaml",
    "ab428_credits_line_27.yaml",
    "ab428_line_29.yaml",
    "ab428_credits_line_32.yaml",
    "ab428_credits_line_33.yaml",
    "ab428_line_34_inputs.yaml",
    "ab428_credits_line_36.yaml",
    "ab428_credits_line_39.yaml",
    "ab428_line_41_input.yaml",
    "ab428_credits_line_41.yaml",
    "ab428_credits_line_43.yaml",
    "ab428_line_51_inputs.yaml",
    "ab428_credits_line_52.yaml",
    "ab428_credits_line_54.yaml",
    "ab428_line_57_inputs.yaml",
    "ab428_credits_line_58.yaml",
    "ab428_line_62.yaml",
    "ab428_line_63_inputs.yaml",
    "ab428_line_64_inputs.yaml",
    "ab428_line_64.yaml",
    "ab428_line_65.yaml",
    "ab428_line_66.yaml",
    "ab428_line_67_inputs.yaml",
    "ab428_line_67.yaml",
    "ab428_line_68.yaml",
    "ab428_line_69_inputs.yaml",
    "ab428_line_70.yaml",
    "ab428_line_72_input.yaml",
    "ab428_line_73.yaml",
    "worksheet_ab428_line_1.yaml",
    "worksheet_ab428_line_2.yaml",
    "worksheet_ab428_line_3.yaml",
    "worksheet_ab428_line_5.yaml",
    "worksheet_ab428_line_6.yaml",
    "worksheet_ab428_line_7.yaml",
    "worksheet_ab428_line_9.yaml",
    "ab428_line_74.yaml",
    LINE_PART.name,
)


HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
CREDITS_FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_taxable_income_line_1
        - ca-ab/ab428_bracket_lower_bound_line_3
        - ca-ab/ab428_taxable_income_over_lower_bound_line_4
        - ca-ab/ab428_bracket_rate_line_5
        - ca-ab/ab428_tax_on_excess_line_6
        - ca-ab/ab428_bracket_tax_at_start_line_7
        - ca-ab/ab428_tax_on_taxable_income_line_8
        - ca-ab/ab428_bracket_lower_bound_line_10
        - ca-ab/ab428_taxable_income_over_lower_bound_line_11
        - ca-ab/ab428_bracket_rate_line_12
        - ca-ab/ab428_tax_on_excess_line_13
        - ca-ab/ab428_bracket_tax_at_start_line_14
        - ca-ab/ab428_tax_on_taxable_income_line_15
        - ca-ab/ab428_unused_tuition_rounded_line_41
        - ca-ab/ab428_credits_total_line_52
        - ca-ab/ab428_non_refundable_credits_line_58
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-ab/worksheet_ab428
      required: true
      exports:
        - ca-ab/worksheet_ab428_line_1
        - ca-ab/worksheet_ab428_line_2
        - ca-ab/worksheet_ab428_line_3
        - ca-ab/worksheet_ab428_line_5
        - ca-ab/worksheet_ab428_line_6
        - ca-ab/worksheet_ab428_line_7
        - ca-ab/worksheet_ab428_supplemental_credit_line_9
    capabilities: []
    """)
TAX_FORM = dedent("""\
    form:
      name: ca-ab/ab428
      required: true
      exports:
        - ca-ab/ab428_alberta_tax_line_75
    capabilities: []
    """)


# salary, line 73, line 74, line 75 with every optional input blank.
CASES = [
    ("20000", "0.00", "0.00", "0.00"),
    ("70000", "3598.12", "0.00", "3598.12"),
    ("200000", "17680.36", "0.00", "17680.36"),
]
# salary, given line 51, line 73, line 74, line 75: a given line 51 lifts line 74 (and lowers
# line 73 through the credits). The first row has line 73 above line 74; the rest have line 74 at
# or above line 73, so the floor is exercised.
CASES_WITH_LINE_51 = [
    ("200000", "100000", "9680.36", "1335.13", "8345.23"),
    ("200000", "200000", "1680.36", "3335.13", "0.00"),
    ("70000", "100000", "0.00", "1333.85", "0.00"),
    ("20000", "200000", "0.00", "3269.36", "0.00"),
]


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield ALBERTA_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    for name in T1_PARTS:
        yield _federal(name)
    for name in ALBERTA_LINE_PARTS:
        yield ALBERTA_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, three form declarations and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_worksheet_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    (folder / "03_tax_form.yaml").write_text(TAX_FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=4):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, line_51: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_51 is not None:
        given.append(Artifact(_amount_kind(LINE_51), D(line_51)))
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
    (sheet,) = worksheets[TAX]
    return sheet


def _rounding() -> Any:
    return YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _amount_kind(identifier: str) -> AmountKind:
    kind = alberta_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _cent(value: Decimal) -> Decimal:
    return value.quantize(D("0.01"), rounding=ROUND_HALF_UP)


@pytest.mark.parametrize(("salary", "line_73", "line_74", "expected"), CASES)
def test_line_75_is_line_73_when_line_74_is_zero(
    tmp_path: Path, salary: str, line_73: str, line_74: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Lines 73 and 74 are recomputed from the real parts; line 74 is computed, never blank.
    assert sheet.get(_amount_kind(LINE_73)).value == D(line_73)
    assert not sheet.get(_amount_kind(LINE_74)).is_blank
    assert sheet.get(_amount_kind(LINE_74)).value == D(line_74)
    line_75 = sheet.get(_amount_kind(LINE_75)).value
    assert line_75 == D(expected)
    assert str(line_75) == expected
    assert line_75.as_tuple().exponent == -2
    assert not line_75.is_signed()


@pytest.mark.parametrize(
    ("salary", "line_51", "line_73", "line_74", "expected"), CASES_WITH_LINE_51
)
def test_line_75_is_line_73_minus_line_74_not_below_zero_when_a_given_line_51_lifts_line_74(
    tmp_path: Path, salary: str, line_51: str, line_73: str, line_74: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_51)

    # Lines 73 and 74 come from the real chain; line 75 is recomputed here, half-up to the cent.
    real_73 = sheet.get(_amount_kind(LINE_73)).value
    real_74 = sheet.get(_amount_kind(LINE_74)).value
    assert real_73 == D(line_73)
    assert real_74 == D(line_74)
    assert real_74 > D("0")
    independent = max(_cent(real_73 - real_74), D("0.00"))
    line_75 = sheet.get(_amount_kind(LINE_75)).value
    assert line_75 == independent
    assert line_75 == D(expected)
    assert str(line_75) == expected
    assert line_75.as_tuple().exponent == -2
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert not line_75.is_signed()


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "200000", "100000")
    kinds = alberta_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_75)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_75),
        minuend=kinds.kind(LINE_73),
        minuend_amount=D("9680.36"),
        subtrahend=kinds.kind(LINE_74),
        subtrahend_amount=D("1335.13"),
        rounding=_rounding().rounding,
        result=D("8345.23"),
    )


def test_the_trace_row_for_line_75_reads_in_english_with_the_rounding_named(
    tmp_path: Path,
) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "200000", "100000").trace)

    (row,) = [r for r in rows if "not below 0" in r and "(1335.13)" in r]
    assert "(9680.36)" in row
    assert " less " in row
    assert row.endswith(", not below 0, gives 8345.23 (rounded to the nearest cent).")
    assert not any("Left blank" in r and "(1335.13)" in r for r in rows)


def test_the_floored_row_for_line_75_reads_gives_zero(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "200000", "200000").trace)

    (row,) = [r for r in rows if "not below 0" in r and "(3335.13)" in r]
    assert "(1680.36)" in row
    assert row.endswith(", not below 0, gives 0.00 (rounded to the nearest cent).")


def _line_75_at(line_73_amount: str, line_74_amount: str) -> Artifact[Decimal]:
    """Line 75 over given lines 73 and 74: the capability the part builds, with the real dataset."""
    line_73, line_74, line_75 = _amount_kind(LINE_73), _amount_kind(LINE_74), _amount_kind(LINE_75)
    capability = SubtractNotBelowZero(_rounding(), line_73, line_74, line_75)
    result = capability.compute(
        (Artifact(line_73, D(line_73_amount)), Artifact(line_74, D(line_74_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_73", "line_74", "expected"),
    [
        ("3598.12", "0.00", "3598.12"),
        ("100.01", "100.00", "0.01"),
        ("2140.53", "2140.53", "0.00"),
        ("1000.00", "3598.12", "0.00"),
        ("0.00", "0.00", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01, 0.004 to 0.00.
        ("100.005", "100.00", "0.01"),
        ("100.004", "100.00", "0.00"),
    ],
)
def test_line_75_is_line_73_minus_line_74_not_below_zero_to_the_cent(
    line_73: str, line_74: str, expected: str
) -> None:
    line_75 = _line_75_at(line_73, line_74).value

    assert line_75 == D(expected)
    assert str(line_75) == expected
    assert line_75.as_tuple().exponent == -2
    assert not line_75.is_signed()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": TAX}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "75",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_73, "less": LINE_74},
        "produces": {"output": LINE_75},
    }
    assert "title" not in step
    # Line 74 is always computed (never blank), so the step has no blank rule.
    assert "blank" not in step


def test_line_75_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert LINE_75 in kinds.identifiers()
    kind = kinds.kind(LINE_75)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(ab_catalog)["AB428_ALBERTA_TAX_LINE_75"]


def test_lines_73_74_and_75_are_all_non_negative() -> None:
    assert non_negative(_amount_kind(LINE_73))
    assert non_negative(_amount_kind(LINE_74))
    assert non_negative(_amount_kind(LINE_75))
