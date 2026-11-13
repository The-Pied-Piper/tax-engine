"""AB428 (2025) line 68, line 66 plus line 67, from the real parts.

Form text (form AB428 2025, CRA 5009-C): "Line 68: Line 66 plus line 67 = ^". The form prints no
title for the line beyond its label, so the step is untitled.

Line 68 is one core/sum step (`ab428_line_68.yaml`), rounded through `ca-ab/cent_rounding`, adding
line 66 (`ca-ab/ab428_tax_after_credits_line_66`) and line 67
(`ca-ab/ab428_additional_minimum_tax_line_67`), in that order. Both parts are always computed (line
67 reads its optional T691 amount as 0 when left out), so the step has no blank rule and prints no
blank row. The output is `ca-ab/ab428_tax_line_68`, a signed kind (the form prints no floor) on the
form `ca-ab/ab428`.

The test composes the real parts that lead to line 66 (the salary, the federal T1 taxable income
parts, AB428 lines 1 to 66, Schedule 8 and T2204), the line 67 inputs part and line 67, plus the
new `ab428_line_68.yaml`. Two form declarations are test-local: `ca-ab/ab428_credits` and
`ca-ab/ab428` export what the other parts read (the real `ab428.yaml` exports line 75, which is
not built).

Figures (hand-computed from the printed forms and the repo figures, not a CRA example): line 66 is
0.00 / 3,598.12 / 17,680.36 at a salary of 20,000 / 70,000 / 200,000, and line 67 is 0.00 when the
T691 amount is left out, so line 68 is 0.00 / 3,598.12 / 17,680.36. With a T691 amount of 1,000.00
line 67 is 350.00 (35%), so line 68 is 350.00 / 3,948.12 / 18,030.36.
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
from tax_engine.domain.trace import BlankPassedOnLine, SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
LINE_66 = "ca-ab/ab428_tax_after_credits_line_66"
LINE_67 = "ca-ab/ab428_additional_minimum_tax_line_67"
LINE_68 = "ca-ab/ab428_tax_line_68"
AMOUNT = "ca-ab/ab428_minimum_tax_t691_amount_line_67"
ROUNDING = "ca-ab/cent_rounding"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "ab428_line_68.yaml"
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
# 67, then line 68.
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
        - ca-ab/ab428_tax_line_68
    capabilities: []
    """)


# salary, line 66, line 67 with the T691 amount left out, line 68 (line 66 plus line 67).
CASES = [
    ("20000", "0.00", "0.00", "0.00"),
    ("70000", "3598.12", "0.00", "3598.12"),
    ("200000", "17680.36", "0.00", "17680.36"),
]
# salary, T691 amount, line 66, line 67 (35% of the amount), line 68.
CASES_WITH_AMOUNT = [
    ("20000", "1000.00", "0.00", "350.00", "350.00"),
    ("70000", "1000.00", "3598.12", "350.00", "3948.12"),
    ("200000", "1000.00", "17680.36", "350.00", "18030.36"),
    # 0.10 x 35% = 0.035, a tie, rounded half-up to 0.04 on line 67; line 68 adds it exactly.
    ("70000", "0.10", "3598.12", "0.04", "3598.16"),
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


def _sheet(tmp_path: Path, salary: str, amount: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if amount is not None:
        given.append(Artifact(_amount_kind(AMOUNT), D(amount)))
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


@pytest.mark.parametrize(("salary", "line_66", "line_67", "expected"), CASES)
def test_line_68_is_line_66_plus_line_67_at_each_salary(
    tmp_path: Path, salary: str, line_66: str, line_67: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Lines 66 and 67 are recomputed from the real parts, and line 68 is their sum.
    got_66 = sheet.get(_amount_kind(LINE_66)).value
    got_67 = sheet.get(_amount_kind(LINE_67)).value
    assert got_66 == D(line_66)
    assert got_67 == D(line_67)
    line_68 = sheet.get(_amount_kind(LINE_68)).value
    assert line_68 == got_66 + got_67
    assert line_68 == D(expected)
    assert str(line_68) == expected
    assert line_68.as_tuple().exponent == -2


@pytest.mark.parametrize(("salary", "amount", "line_66", "line_67", "expected"), CASES_WITH_AMOUNT)
def test_line_68_adds_line_67_when_the_t691_amount_is_given(
    tmp_path: Path, salary: str, amount: str, line_66: str, line_67: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, amount)

    got_66 = sheet.get(_amount_kind(LINE_66)).value
    got_67 = sheet.get(_amount_kind(LINE_67)).value
    assert got_66 == D(line_66)
    assert got_67 == D(line_67)
    line_68 = sheet.get(_amount_kind(LINE_68)).value
    assert line_68 == got_66 + got_67
    assert line_68 == D(expected)
    assert line_68.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "line_66", "line_67", "expected"),
    [
        ("20000", "0.00", "-350.00", "-350.00"),
        ("70000", "3598.12", "-350.00", "3248.12"),
    ],
)
def test_a_negative_t691_amount_gives_a_negative_line_67_and_line_68_without_raising(
    tmp_path: Path, salary: str, line_66: str, line_67: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, "-1000")

    assert sheet.get(_amount_kind(LINE_66)).value == D(line_66)
    assert sheet.get(_amount_kind(LINE_67)).value == D(line_67)
    line_68 = sheet.get(_amount_kind(LINE_68)).value
    assert line_68 == D(expected)
    assert str(line_68) == expected


def test_line_68_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(_amount_kind(LINE_68)).is_blank
    # The step has no blank rule: both parts are always computed, so no row names line 68.
    assert not [
        t
        for t in sheet.trace
        if isinstance(t, BlankPassedOnLine) and t.output is alberta_kinds().kind(LINE_68)
    ]


def test_the_step_traces_one_sum_line_over_lines_66_and_67_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "1000.00")
    kinds = alberta_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(LINE_68)]
    assert line == SumLine(
        output=kinds.kind(LINE_68),
        parts=((kinds.kind(LINE_66), D("3598.12")), (kinds.kind(LINE_67), D("350.00"))),
        rounding=_rounding().rounding,
        total=D("3948.12"),
    )


def test_the_trace_row_for_line_68_reads_in_english_with_the_rounding_named(
    tmp_path: Path,
) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000", "1000.00").trace)

    (row,) = [r for r in rows if " plus " in r and "(3598.12)" in r and "(350.00)" in r]
    assert row.index("(3598.12)") < row.index("(350.00)")
    assert " gives 3948.12 " in row
    assert row.endswith("(rounded to the nearest cent).")


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
        "name": "core/sum",
        "reference": "68",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_66, LINE_67]},
        "produces": {"output": LINE_68},
    }
    assert "title" not in step


def test_line_68_is_a_registered_signed_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert LINE_68 in kinds.identifiers()
    kind = kinds.kind(LINE_68)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    # The form prints no floor on line 68, and line 67 is signed, so the kind is not non_negative.
    assert not non_negative(kind)
    assert kind is vars(ab_catalog)["AB428_TAX_LINE_68"]
