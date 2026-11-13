"""AB428 (2025) line 66, line 61 minus line 65 (not below 0), from the real parts.

Form text (Form AB428, CRA 5009-c): "Line 66: Line 61 minus line 65 (if negative, enter
\\"0\\") = ^". The form prints no title for the line beyond its label, so the step is untitled.

Line 66 is one core/subtract_not_below_zero step (`ab428_line_66.yaml`), rounded through
`ca-ab/cent_rounding`, with `amount` line 61 (`ca-ab/ab428_tax_line_61`, signed) and `less` line 65
(`ca-ab/ab428_credits_subtotal_line_65`). Both inputs are always computed, so the step has no blank
rule and prints no blank row. The form floors line 66 at 0 (printed), unlike signed line 61, so
the output `ca-ab/ab428_tax_after_credits_line_66` is a non-negative kind on the form `ca-ab/ab428`.

The test composes the real parts that lead to line 61 (the salary, the federal T1 taxable income
parts, AB428 lines 1 to 15, lines 59 and 60) and to line 65 (Schedule 8, T2204, AB428 lines 16 to
58, lines 62 to 64) plus the new `ab428_line_66.yaml`, and types in only the salary. Two form
declarations are test-local: `ca-ab/ab428_credits` and `ca-ab/ab428` export what the other parts
read (the real `ab428.yaml` exports line 75, which is not built).

Figures (hand-computed from the printed forms and the repo figures, not a CRA example; a salary of
20,000 / 70,000 / 200,000 is a taxable income of 19,835.00 / 69,335.00 / 198,926.00): line 61 is
1,586.80 / 5,733.50 / 19,820.89 and line 65 is 1,877.42 / 2,135.38 / 2,140.53, so line 66 is 0.00
(line 61 minus line 65 is -290.62, floored) / 3,598.12 / 17,680.36.
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
from tax_engine.domain.trace import BlankPassedOnLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_CREDITS_SUBTOTAL_LINE_65,
    AB428_TAX_LINE_61,
)
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
LINE_61 = "ca-ab/ab428_tax_line_61"
LINE_65 = "ca-ab/ab428_credits_subtotal_line_65"
LINE_66 = "ca-ab/ab428_tax_after_credits_line_66"
ROUNDING = "ca-ab/cent_rounding"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "ab428_line_66.yaml"
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
# The real Alberta parts after the federal ones, in composition order: lines 1 to 15 and 59 to 61
# (the line 61 test's), then lines 16 to 58 and 62 to 65 (the line 65 test's), then line 66.
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
        - ca-ab/ab428_non_refundable_credits_line_58
    capabilities: []
    """)
TAX_FORM = dedent("""\
    form:
      name: ca-ab/ab428
      required: true
      exports:
        - ca-ab/ab428_alberta_tax_on_taxable_income_line_59
        - ca-ab/ab428_tax_line_61
        - ca-ab/ab428_credits_subtotal_line_65
        - ca-ab/ab428_tax_after_credits_line_66
    capabilities: []
    """)

# salary, line 61, line 65 (the line 61 and line 65 tests pin these), line 66: line 61 minus line
# 65 is -290.62 at 20,000, so line 66 is the floor, 0.00.
CASES = [
    ("20000", "1586.80", "1877.42", "0.00"),
    ("70000", "5733.50", "2135.38", "3598.12"),
    ("200000", "19820.89", "2140.53", "17680.36"),
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
    """The engine over a temporary Alberta manifest of a test header, two form declarations and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_tax_form.yaml").write_text(TAX_FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=3):
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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
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


@pytest.mark.parametrize(("salary", "line_61", "line_65", "expected"), CASES)
def test_line_66_is_line_61_minus_line_65_not_below_zero_at_each_salary(
    tmp_path: Path, salary: str, line_61: str, line_65: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Lines 61 and 65 are recomputed from the real parts, not only taken from the ticket.
    assert sheet.get(AB428_TAX_LINE_61).value == D(line_61)
    assert sheet.get(AB428_CREDITS_SUBTOTAL_LINE_65).value == D(line_65)
    line_66 = sheet.get(_amount_kind(LINE_66)).value
    assert line_66 == D(expected)
    assert line_66.as_tuple().exponent == -2


def test_line_66_at_20000_is_the_floor_of_a_negative_difference(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")

    assert sheet.get(AB428_TAX_LINE_61).value - sheet.get(AB428_CREDITS_SUBTOTAL_LINE_65).value == (
        D("-290.62")
    )
    line_66 = sheet.get(_amount_kind(LINE_66)).value
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert str(line_66) == "0.00"
    assert not line_66.is_signed()


def test_line_66_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(_amount_kind(LINE_66)).is_blank
    # The step has no blank rule: nothing on this step's path is blank, so no row names line 66.
    assert not [
        t
        for t in sheet.trace
        if isinstance(t, BlankPassedOnLine) and t.output is alberta_kinds().kind(LINE_66)
    ]


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = alberta_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_66)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_66),
        minuend=kinds.kind(LINE_61),
        minuend_amount=D("5733.50"),
        subtrahend=kinds.kind(LINE_65),
        subtrahend_amount=D("2135.38"),
        rounding=_rounding().rounding,
        result=D("3598.12"),
    )


def test_the_trace_row_for_line_66_reads_in_english_with_the_rounding_named(
    tmp_path: Path,
) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    (row,) = [r for r in rows if "not below 0" in r and "(5733.50)" in r]
    # The same wording as the other subtract-not-below-zero steps: "<line> (<amount>) less <line>
    # (<amount>), not below 0, gives <result> (rounded to the nearest cent)."
    assert "(2135.38)" in row
    assert " less " in row
    assert row.endswith(", not below 0, gives 3598.12 (rounded to the nearest cent).")


def test_the_floored_row_for_line_66_reads_gives_zero(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "20000").trace)

    (row,) = [r for r in rows if "not below 0" in r and "(1586.80)" in r]
    assert "(1877.42)" in row
    assert row.endswith(", not below 0, gives 0.00 (rounded to the nearest cent).")


def _line_66_at(line_61_amount: str, line_65_amount: str) -> Artifact[Decimal]:
    """Line 66 over given lines 61 and 65: the capability the part builds, with the real dataset."""
    line_61, line_65, line_66 = _amount_kind(LINE_61), _amount_kind(LINE_65), _amount_kind(LINE_66)
    capability = SubtractNotBelowZero(_rounding(), line_61, line_65, line_66)
    result = capability.compute(
        (Artifact(line_61, D(line_61_amount)), Artifact(line_65, D(line_65_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_61", "line_65", "expected"),
    [
        # Line 61 above line 65: the difference.
        ("5733.50", "2135.38", "3598.12"),
        ("100.01", "100.00", "0.01"),
        # Exactly equal: the cent zero, not negative.
        ("2140.53", "2140.53", "0.00"),
        # Line 61 below line 65: the floor.
        ("1586.80", "1877.42", "0.00"),
        ("99.99", "100.00", "0.00"),
        # Line 61 is signed (a negative line 60), so the floor also catches a negative minuend.
        ("-266.50", "2135.38", "0.00"),
        ("0.00", "0.00", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01, 0.004 to 0.00.
        ("100.005", "100.00", "0.01"),
        ("100.004", "100.00", "0.00"),
    ],
)
def test_line_66_is_line_61_minus_line_65_not_below_zero_to_the_cent(
    line_61: str, line_65: str, expected: str
) -> None:
    line_66 = _line_66_at(line_61, line_65).value

    assert line_66 == D(expected)
    assert str(line_66) == expected
    assert line_66.as_tuple().exponent == -2
    assert not line_66.is_signed()


def test_a_floored_zero_and_an_exact_equal_are_the_same_positive_cent_zero() -> None:
    below = _line_66_at("100.00", "4800.00").value
    equal = _line_66_at("4800.00", "4800.00").value

    assert str(below) == str(equal) == "0.00"
    assert not below.is_signed()
    assert not equal.is_signed()


def test_the_positive_row_traces_the_subtraction_with_the_rounding_named() -> None:
    kinds = alberta_kinds()
    line_61, line_65, line_66 = _amount_kind(LINE_61), _amount_kind(LINE_65), _amount_kind(LINE_66)
    result = SubtractNotBelowZero(_rounding(), line_61, line_65, line_66).compute(
        (Artifact(line_61, D("19820.89")), Artifact(line_65, D("2140.53")))
    )

    (line,) = result.trace
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_66),
        minuend=kinds.kind(LINE_61),
        minuend_amount=D("19820.89"),
        subtrahend=kinds.kind(LINE_65),
        subtrahend_amount=D("2140.53"),
        rounding=_rounding().rounding,
        result=D("17680.36"),
    )


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
        "reference": "66",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_61, "less": LINE_65},
        "produces": {"output": LINE_66},
    }
    assert "title" not in step


def test_line_66_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert LINE_66 in kinds.identifiers()
    kind = kinds.kind(LINE_66)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is ab_catalog.AB428_TAX_AFTER_CREDITS_LINE_66


def test_line_61_stays_signed_while_line_66_is_floored() -> None:
    assert not non_negative(AB428_TAX_LINE_61)
    assert non_negative(_amount_kind(LINE_66))
