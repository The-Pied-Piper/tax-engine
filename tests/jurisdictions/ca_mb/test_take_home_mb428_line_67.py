"""MB428 (2025) line 67, line 65 plus line 66, from the salary alone, real parts.

Form text (Form MB428, CRA 5007-c): "Line 67: Line 65 plus line 66 = ^". The form prints no title
and no maximum for the line, so the step is untitled and a plain sum. Line 67 is one core/sum step
over line 65 (`ca-mb/mb428_tax_after_credits_line_65`) and line 66
(`ca-mb/mb428_additional_tax_minimum_tax_line_66`), rounded by `ca-mb/cent_rounding`. Both lines are
always computed (line 66 reads a blank T691 amount as 0 in its own step), so line 67 has no blank
rule and prints no "left blank, taken as 0" row of its own.

The test composes the real Manitoba salary part, the real Schedule 8, T2204 and T1 taxable income
parts, the real parts of Worksheet MB428 lines 1 to 9, Schedule MB428-A lines 1 to 12, MB428 lines
1, 3 to 9, 18, 19, 21, 28, 29, 33, 36, 41, 42 and 51 of `ca-mb/mb428_credits`, the line 31, line 50
and line 56 input parts, the real `mb428_credits_line_53.yaml`, `mb428_credits_line_57.yaml`,
`mb428_line_58.yaml`, `mb428_line_59_input.yaml`, `mb428_line_60.yaml`, `mb428_line_61.yaml`,
`mb428_line_62_input.yaml`, `mb428_credits_line_63_input.yaml`, `mb428_line_63.yaml`,
`mb428_line_64.yaml`, `mb428_line_65.yaml`, `mb428_line_66_input.yaml` and `mb428_line_66.yaml`, and
the new `mb428_line_67.yaml`, and types in only the salary (and, in some tests, the T691 amount of
line 66). The header and the form declarations are made up here: the credits form exports lines 1,
3 to 8 and 57, and `ca-mb/mb428` exports only line 67. The figures are line 65 (the line 65 test)
plus line 66 (the line 66 test, 0.00 with the T691 amount left out), hand-computed from the printed
forms, not a CRA example: 0.00 / 5,747.59 / 26,863.55.
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
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb428_line_67.yaml"
LINE_66_INPUT_PART = MB_PARTS / "mb428_line_66_input.yaml"
LINE_66_PART = MB_PARTS / "mb428_line_66.yaml"
LINE_65_PART = MB_PARTS / "mb428_line_65.yaml"
LINE_64_PART = MB_PARTS / "mb428_line_64.yaml"
LINE_60_PART = MB_PARTS / "mb428_line_60.yaml"
LINE_59_PART = MB_PARTS / "mb428_line_59_input.yaml"
LINE_58_PART = MB_PARTS / "mb428_line_58.yaml"
LINE_61_PART = MB_PARTS / "mb428_line_61.yaml"
LINE_62_PART = MB_PARTS / "mb428_line_62_input.yaml"
LINE_63_INPUT_PART = MB_PARTS / "mb428_credits_line_63_input.yaml"
LINE_63_PART = MB_PARTS / "mb428_line_63.yaml"
LINE_57_PART = MB_PARTS / "mb428_credits_line_57.yaml"
LINE_53_PART = MB_PARTS / "mb428_credits_line_53.yaml"
LINE_56_PARTS = tuple(
    MB_PARTS / name
    for name in (
        "mb428_credits_line_54_inputs.yaml",
        "mb428_credits_line_54.yaml",
        "mb428_credits_line_55_inputs.yaml",
        "mb428_credits_line_55.yaml",
        "mb428_credits_line_56.yaml",
    )
)
FORM_NAME = "ca-mb/mb428"
CREDITS_FORM_NAME = "ca-mb/mb428_credits"
LINE_57 = "ca-mb/mb428_non_refundable_credits_line_57"
LINE_60 = "ca-mb/mb428_tax_before_credits_line_60"
LINE_64 = "ca-mb/mb428_credits_total_line_64"
LINE_61 = "ca-mb/mb428_non_refundable_credits_line_61"
LINE_62 = "ca-mb/mb428_dividend_tax_credit_line_62"
LINE_63 = "ca-mb/mb428_minimum_tax_carryover_credit_line_63"
LINE_65 = "ca-mb/mb428_tax_after_credits_line_65"
LINE_66 = "ca-mb/mb428_additional_tax_minimum_tax_line_66"
IDENTIFIER = "ca-mb/mb428_tax_line_67"
CREDIT_PARTS = (
    *(f"mb428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8)),
    "mb428_credits_line_9.yaml",
    "mb428_credits_line_19.yaml",
    "mb428_credits_line_21.yaml",
    "mb428_credits_line_28.yaml",
    "mb428_credits_line_18.yaml",
    "mb428_credits_line_29.yaml",
    "mb428_credits_line_31_input.yaml",
    "mb428_credits_line_31.yaml",
    "mb428_credits_line_33.yaml",
    "mb428_credits_line_36.yaml",
    "mb428_credits_line_41.yaml",
    "mb428_credits_line_42.yaml",
    "mb428_credits_line_43_inputs.yaml",
    "mb428_credits_line_44.yaml",
    "mb428_credits_line_46.yaml",
    "mb428_credits_line_47.yaml",
    "mb428_credits_line_48.yaml",
    "worksheet_mb428_other_dependants.yaml",
    "worksheet_mb428_other_dependants_inputs.yaml",
    "worksheet_mb428_other_dependants_line_3.yaml",
    "worksheet_mb428_other_dependants_total.yaml",
    "mb428_credits_line_49.yaml",
    "mb428_credits_line_50.yaml",
    "mb428_credits_line_51.yaml",
)
SCHEDULE_PARTS = (
    "mb428_a_line_1.yaml",
    "mb428_a_line_10.yaml",
    "mb428_a_line_11.yaml",
    "mb428_a_line_11_product.yaml",
    "mb428_a_line_12.yaml",
)
WORKSHEET_PARTS = (
    "worksheet_mb428_line_1.yaml",
    "worksheet_mb428_line_2.yaml",
    "worksheet_mb428_line_3.yaml",
    "worksheet_mb428_line_4.yaml",
    "worksheet_mb428_line_5.yaml",
    "worksheet_mb428_line_6.yaml",
    "worksheet_mb428_line_7.yaml",
    "worksheet_mb428_line_8.yaml",
    "worksheet_mb428_line_9.yaml",
)
# The real federal parts the T1 taxable-income form needs, beside the salary and the worksheet.
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_basic_personal_amount_line_1
        - ca-mb/worksheet_mb428_line_2
        - ca-mb/worksheet_mb428_basic_personal_amount_line_3
        - ca-mb/worksheet_mb428_line_4
        - ca-mb/worksheet_mb428_basic_personal_amount_line_5
        - ca-mb/worksheet_mb428_line_6
        - ca-mb/worksheet_mb428_basic_personal_amount_line_7
        - ca-mb/worksheet_mb428_line_8
        - ca-mb/worksheet_mb428_basic_personal_amount_line_9
    capabilities: []
    """)
SCHEDULE_FORM = dedent("""\
    form:
      name: ca-mb/mb428_a
      required: true
      exports:
        - ca-mb/mb428_a_family_tax_benefit_line_12
    capabilities: []
    """)
# The MB428 credits declaration, test-local: lines 1 to 57 are composed, so it exports lines 1, 3 to
# 8 (line 58 reads line 8) and 57.
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS_FORM_NAME}
      required: true
      exports:
        - ca-mb/mb428_taxable_income_line_1
        - ca-mb/mb428_bracket_lower_bound_line_3
        - ca-mb/mb428_taxable_income_over_lower_bound_line_4
        - ca-mb/mb428_bracket_rate_line_5
        - ca-mb/mb428_tax_on_excess_line_6
        - ca-mb/mb428_bracket_tax_at_start_line_7
        - ca-mb/mb428_tax_on_taxable_income_line_8
        - {LINE_57}
    capabilities: []
    """)
# The MB428 declaration, test-local: lines 58 to 67 are composed, so it exports only line 67.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 65 (line 60 less line 64, not below 0), line 67 (line 65 plus line 66) with the T691
# amount left out, so line 66 is 0.00 and line 67 equals line 65.
# Line 60 is 1,072.98 / 2,142.18 / 7,923.71 / 29,046.62; line 64 is 1,883.15 / 1,858.10 / 2,176.12 /
# 2,183.07.
CASES = [
    ("10000", "0.00"),
    ("70000", "5747.59"),
    ("200000", "26863.55"),
]
LINES_60_AND_64 = {
    "10000": ("1072.98", "1883.15"),
    "70000": ("7923.71", "2176.12"),
    "200000": ("29046.62", "2183.07"),
}


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in WORKSHEET_PARTS:
        yield MB_PARTS / name
    for name in SCHEDULE_PARTS:
        yield MB_PARTS / name
    for name in CREDIT_PARTS:
        yield MB_PARTS / name
    yield LINE_53_PART
    yield from LINE_56_PARTS
    yield LINE_57_PART
    yield LINE_58_PART
    yield LINE_59_PART
    yield LINE_60_PART
    yield LINE_61_PART
    yield LINE_62_PART
    yield LINE_63_INPUT_PART
    yield LINE_63_PART
    yield LINE_64_PART
    yield LINE_65_PART
    yield LINE_66_INPUT_PART
    yield LINE_66_PART
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, form declarations and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    (folder / "02_schedule_form.yaml").write_text(SCHEDULE_FORM, encoding="utf-8")
    (folder / "03_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "04_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=5):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, t691_amount: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if t691_amount is not None:
        given.append(Artifact(mb_catalog.MB428_T691_AMOUNT_LINE_66, D(t691_amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


def _blank_rows(sheet: Worksheet) -> list[str]:
    rows = EnglishTraceRenderer().render_all(sheet.trace)
    return [row for row in rows if "left blank, taken as 0" in row.lower()]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_67_is_line_65_when_line_66_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line_60, line_64 = LINES_60_AND_64[salary]
    # Line 65 is line 60 less line 64, not below 0; line 66 is 50% of a blank amount read as 0.
    line_65 = max(D(line_60) - D(line_64), D("0"))

    assert _line(sheet, LINE_65) == line_65
    assert _line(sheet, LINE_66) == D("0.00")
    assert _line(sheet, IDENTIFIER) == line_65 + D("0.00")
    assert _line(sheet, IDENTIFIER) == D(expected)
    assert str(_line(sheet, IDENTIFIER)) == expected


@pytest.mark.parametrize(
    ("amount", "line_66", "expected"),
    [
        # An amount of 1,000.00 gives line 66 of 500.00; 5,747.59 plus 500.00 is 6,247.59.
        ("1000.00", "500.00", "6247.59"),
        # 0.01 x 50% = 0.005, a tie, rounded half-up to 0.01 at line 66; 5,747.59 + 0.01.
        ("0.01", "0.01", "5747.60"),
    ],
)
def test_line_67_adds_line_66_to_line_65_at_70000(
    tmp_path: Path, amount: str, line_66: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, "70000", amount)

    assert _line(sheet, LINE_65) == D("5747.59")
    assert _line(sheet, LINE_66) == D(line_66)
    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_65) + _line(sheet, LINE_66)
    assert _line(sheet, IDENTIFIER) == D(expected)
    assert str(_line(sheet, IDENTIFIER)) == expected


def test_line_67_is_line_66_alone_when_line_65_is_floored_at_10000(tmp_path: Path) -> None:
    # At 10,000 line 65 is 0.00; an amount of 1,000.00 gives line 66 and line 67 of 500.00.
    sheet = _sheet(tmp_path, "10000", "1000.00")

    assert _line(sheet, LINE_65) == D("0.00")
    assert _line(sheet, IDENTIFIER) == D("500.00")


def test_line_67_has_no_left_blank_row_of_its_own(tmp_path: Path) -> None:
    # The composed steps for lines 60, 63 and 64 print one blank row each; line 67's step has no
    # blank rule and adds none. A blank T691 amount adds exactly one more, line 66's own.
    (tmp_path / "given").mkdir()
    (tmp_path / "blank").mkdir()
    given = _blank_rows(_sheet(tmp_path / "given", "70000", "1000.00"))
    blank = _blank_rows(_sheet(tmp_path / "blank", "70000"))

    assert len(given) == 3
    assert len(blank) == len(given) + 1


def test_the_sheet_prints_no_title_and_the_reference_of_line_67(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "67"


def test_the_step_traces_one_sum_line_over_lines_65_and_66(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "1000.00")
    kinds = manitoba_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line.parts == ((kinds.kind(LINE_65), D("5747.59")), (kinds.kind(LINE_66), D("500.00")))
    assert line.total == D("6247.59")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_over_lines_65_and_66() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "67",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_65, LINE_66]},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step
    assert "blank" not in step


def test_line_67_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_TAX_LINE_67
