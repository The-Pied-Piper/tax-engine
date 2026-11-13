"""AB428 (2025) line 73, line 70 minus line 72 (not below 0), from the real parts.

Form text (Form AB428, CRA 5009-c): "Line 73: Line 70 minus line 72 (if negative, enter \\"0\\") =
^" and "Line 72: Alberta political contributions tax credit (use Worksheet AB428) (maximum
$1,000)". The form prints no title for line 73 beyond its label, so the step is untitled.

Line 73 is one core/subtract_not_below_zero step (`ab428_line_73.yaml`), rounded through
`ca-ab/cent_rounding`, with `amount` line 70 (`ca-ab/ab428_tax_line_70`, non-negative) and `less`
line 72 (`ca-ab/ab428_political_contributions_credit_line_72`, an optional input, from
`ab428_line_72_input.yaml`). A salary-only caller has no political contributions, so line 72 is
left blank, and the step has a blank rule reading it as 0 and prints its own "Left blank, taken as
0" row. The form floors line 73 at 0 (printed), so the output `ca-ab/ab428_tax_line_73` is a
non-negative kind on the form `ca-ab/ab428`.

The test composes the real parts that lead to line 70 (the salary, the federal T1 taxable income
parts, AB428 lines 1 to 70, Schedule 8 and T2204), the line 72 input part plus the new
`ab428_line_73.yaml`. Two form declarations are test-local: `ca-ab/ab428_credits` and `ca-ab/ab428`
export what the other parts read (the real `ab428.yaml` exports line 75, which is not built).

Figures (hand-computed from the printed forms and the repo figures, not a CRA example): line 70 is
0.00 / 3,598.12 / 17,680.36 at a salary of 20,000 / 70,000 / 200,000, and line 72 is blank (0), so
line 73 is 0.00 / 3,598.12 / 17,680.36. With a line 72 of 1,000.00 line 73 is 0.00 (line 70 is 0.00,
so the difference is -1,000.00, floored) / 2,598.12 / 16,680.36.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
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
LINE_70 = "ca-ab/ab428_tax_line_70"
LINE_72 = "ca-ab/ab428_political_contributions_credit_line_72"
LINE_73 = "ca-ab/ab428_tax_line_73"
ROUNDING = "ca-ab/cent_rounding"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "ab428_line_73.yaml"
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
# (the line 61 test's), then lines 16 to 58 and 62 to 65 (the line 65 test's), then lines 66 and
# 67, then lines 68 to 70, then line 72, then line 73.
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
    "ab428_line_66.yaml",
    "ab428_line_67_inputs.yaml",
    "ab428_line_67.yaml",
    "ab428_line_68.yaml",
    "ab428_line_69_inputs.yaml",
    "ab428_line_70.yaml",
    "ab428_line_72_input.yaml",
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
        - ca-ab/ab428_additional_minimum_tax_line_67
        - ca-ab/ab428_tax_line_70
        - ca-ab/ab428_tax_line_73
    capabilities: []
    """)


# salary, line 70 (the line 70 test pins these), line 73 with line 72 left blank (read as 0).
CASES = [
    ("20000", "0.00", "0.00"),
    ("70000", "3598.12", "3598.12"),
    ("200000", "17680.36", "17680.36"),
]
# salary, line 72, line 70, line 73: line 70 minus line 72, not below 0.
CASES_WITH_LINE_72 = [
    # Line 70 minus line 72 is -1,000.00 at 20,000: the floor.
    ("20000", "1000.00", "0.00", "0.00"),
    ("70000", "1000.00", "3598.12", "2598.12"),
    ("200000", "1000.00", "17680.36", "16680.36"),
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


def _sheet(tmp_path: Path, salary: str, line_72: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_72 is not None:
        given.append(Artifact(_amount_kind(LINE_72), D(line_72)))
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


@pytest.mark.parametrize(("salary", "line_70", "expected"), CASES)
def test_line_73_is_line_70_when_line_72_is_left_blank(
    tmp_path: Path, salary: str, line_70: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 70 is recomputed from the real parts, and line 72 is blank, read as 0.
    assert sheet.get(_amount_kind(LINE_70)).value == D(line_70)
    assert sheet.get(_amount_kind(LINE_72)).is_blank
    line_73 = sheet.get(_amount_kind(LINE_73)).value
    assert line_73 == D(expected)
    assert str(line_73) == expected
    assert line_73.as_tuple().exponent == -2
    assert not line_73.is_signed()


@pytest.mark.parametrize(("salary", "line_72", "line_70", "expected"), CASES_WITH_LINE_72)
def test_line_73_is_line_70_minus_line_72_not_below_zero_when_line_72_is_given(
    tmp_path: Path, salary: str, line_72: str, line_70: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_72)

    assert sheet.get(_amount_kind(LINE_70)).value == D(line_70)
    line_73 = sheet.get(_amount_kind(LINE_73)).value
    assert line_73 == D(expected)
    assert str(line_73) == expected
    assert line_73.as_tuple().exponent == -2
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert not line_73.is_signed()


def _left_blank_rows(rows: Sequence[str]) -> int:
    return sum("Left blank, taken as 0" in row for row in rows)


def test_a_blank_line_72_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    given_dir = tmp_path / "given"
    given_dir.mkdir()
    blank = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)
    given = EnglishTraceRenderer().render_all(_sheet(given_dir, "70000", "1000.00").trace)

    # Other steps on the sheet print their own blank rows either way; line 73's is the difference.
    assert _left_blank_rows(blank) == _left_blank_rows(given) + 1


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "1000.00")
    kinds = alberta_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_73)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_73),
        minuend=kinds.kind(LINE_70),
        minuend_amount=D("3598.12"),
        subtrahend=kinds.kind(LINE_72),
        subtrahend_amount=D("1000.00"),
        rounding=_rounding().rounding,
        result=D("2598.12"),
    )


def test_the_trace_row_for_line_73_reads_in_english_with_the_rounding_named(
    tmp_path: Path,
) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000", "1000.00").trace)

    (row,) = [r for r in rows if "not below 0" in r and "(1000.00)" in r]
    assert "(3598.12)" in row
    assert " less " in row
    assert row.endswith(", not below 0, gives 2598.12 (rounded to the nearest cent).")


def test_the_floored_row_for_line_73_reads_gives_zero(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "20000", "1000.00").trace)

    (row,) = [r for r in rows if "not below 0" in r and "(1000.00)" in r]
    assert "(0.00)" in row
    assert row.endswith(", not below 0, gives 0.00 (rounded to the nearest cent).")


def _line_73_at(line_70_amount: str, line_72_amount: str) -> Artifact[Decimal]:
    """Line 73 over given lines 70 and 72: the capability the part builds, with the real dataset."""
    line_70, line_72, line_73 = _amount_kind(LINE_70), _amount_kind(LINE_72), _amount_kind(LINE_73)
    capability = SubtractNotBelowZero(_rounding(), line_70, line_72, line_73)
    result = capability.compute(
        (Artifact(line_70, D(line_70_amount)), Artifact(line_72, D(line_72_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_70", "line_72", "expected"),
    [
        ("3598.12", "1000.00", "2598.12"),
        ("100.01", "100.00", "0.01"),
        ("2140.53", "2140.53", "0.00"),
        ("1000.00", "3598.12", "0.00"),
        ("0.00", "0.00", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01, 0.004 to 0.00.
        ("100.005", "100.00", "0.01"),
        ("100.004", "100.00", "0.00"),
    ],
)
def test_line_73_is_line_70_minus_line_72_not_below_zero_to_the_cent(
    line_70: str, line_72: str, expected: str
) -> None:
    line_73 = _line_73_at(line_70, line_72).value

    assert line_73 == D(expected)
    assert str(line_73) == expected
    assert line_73.as_tuple().exponent == -2
    assert not line_73.is_signed()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_a_blank_rule_on_line_72() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": TAX}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "73",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_70, "less": LINE_72},
        "blank": {"less": "0"},
        "produces": {"output": LINE_73},
    }
    assert "title" not in step


def test_line_73_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert LINE_73 in kinds.identifiers()
    kind = kinds.kind(LINE_73)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(ab_catalog)["AB428_TAX_LINE_73"]


def test_line_70_and_line_73_are_both_non_negative() -> None:
    assert non_negative(_amount_kind(LINE_70))
    assert non_negative(_amount_kind(LINE_73))
