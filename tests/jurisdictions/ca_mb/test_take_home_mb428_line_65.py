"""MB428 (2025) line 65, line 60 minus line 64 (not below 0), from the salary alone, real parts.

Form text (Form MB428, CRA 5007-c): "Line 65: Line 60 minus line 64 (if negative, enter "0") = ^  ".
The form prints no title for the line, so the step is untitled. Line 65 is one
core/subtract_not_below_zero step over line 60 (`ca-mb/mb428_tax_before_credits_line_60`) and
line 64 (`ca-mb/mb428_credits_total_line_64`), rounded by `ca-mb/cent_rounding`. Both lines are
always computed (line 60 reads a blank line 59 as 0 and line 64 needs no blank rule for line 62,
which is always computed),
so line 65 has no blank rule and prints no "left blank, taken as 0" row of its own.

The test composes the T1 employment income form, the real Schedule 8, T2204 and T1 taxable income
parts, the real parts of Worksheet MB428 lines 1 to 9, Schedule MB428-A lines 1 to 12, MB428 lines
1, 3 to 9, 18, 19, 21, 28, 29, 33, 36, 41, 42 and 51 of `ca-mb/mb428_credits`, the line 31, line 50
and line 56 input parts, the real `mb428_credits_line_53.yaml`, `mb428_credits_line_57.yaml`,
`mb428_line_58.yaml`, `mb428_line_59_input.yaml`, `mb428_line_60.yaml`, `mb428_line_61.yaml`,
`mb428_line_62.yaml`, `mb428_line_63_input.yaml`, `mb428_line_63.yaml` and
`mb428_line_64.yaml`, and the new `mb428_line_65.yaml`, and types in only the salary (and, in some
tests, line 59, line 62 and the line 63 amount). The header and the form declarations are made up
here: the credits form exports lines 1, 3 to 8 and 57, and `ca-mb/mb428` exports only line 65. The
figures are line 60 (the line 60 test) less line 64 (the line 64 test), not below 0, hand-computed
from the printed forms, not a CRA example: 0.00 / 5,747.59 / 26,863.55 (at 10,000 line 60
is 1,072.98 and line 64 is 1,883.15, so the difference is negative and line 65 is 0).
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

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb428_line_65.yaml"
LINE_64_PART = MB_PARTS / "mb428_line_64.yaml"
LINE_60_PART = MB_PARTS / "mb428_line_60.yaml"
LINE_59_PART = MB_PARTS / "mb428_line_59_input.yaml"
LINE_58_PART = MB_PARTS / "mb428_line_58.yaml"
LINE_61_PART = MB_PARTS / "mb428_line_61.yaml"
LINE_62_PART = MB_PARTS / "mb428_line_62.yaml"
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
LINE_63 = "ca-mb/mb428_minimum_tax_carryover_line_63"
IDENTIFIER = "ca-mb/mb428_tax_after_credits_line_65"
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
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_line_1
        - ca-mb/worksheet_mb428_line_2
        - ca-mb/worksheet_mb428_line_3
        - ca-mb/worksheet_mb428_line_4
        - ca-mb/worksheet_mb428_line_5
        - ca-mb/worksheet_mb428_line_6
        - ca-mb/worksheet_mb428_line_7
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
# The MB428 declaration, test-local: lines 58 to 65 are composed, so it exports only line 65.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 65: line 60 less line 64, not below 0, with every optional input blank.
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
    yield LINE_63_PART
    yield LINE_64_PART
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
            part.read_text(encoding="utf-8"),
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


def _sheet(
    tmp_path: Path,
    salary: str,
    line_59: str | None = None,
    line_62: str | None = None,
    line_63_amount: str | None = None,
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_59 is not None:
        given.append(Artifact(mb_catalog.MB428_TAX_ON_SPLIT_INCOME_LINE_59, D(line_59)))
    if line_62 is not None:
        # `line_62` is the amount of line 12000, with line 12010 at 40% of it.
        given.append(Artifact(manitoba_kinds().kind("ca/taxable_dividends"), D(line_62)))
        given.append(
            Artifact(
                manitoba_kinds().kind("ca/taxable_dividends_other_than_eligible"),
                D(line_62) * D("0.4"),
            )
        )
    if line_63_amount is not None:
        given.append(Artifact(manitoba_kinds().kind("ca/minimum_tax_carryover"), D(line_63_amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


def _blank_rows(sheet: Worksheet) -> list[str]:
    rows = EnglishTraceRenderer().render_all(sheet.trace)
    return [row for row in rows if "left blank, taken as 0" in row.lower()]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_65_is_line_60_less_line_64_not_below_0(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line_60, line_64 = LINES_60_AND_64[salary]

    assert _line(sheet, LINE_60) == D(line_60)
    assert _line(sheet, LINE_64) == D(line_64)
    assert _line(sheet, IDENTIFIER) == D(expected)
    assert str(_line(sheet, IDENTIFIER)) == expected


def test_line_65_is_floored_at_a_positive_cent_zero_when_line_64_exceeds_line_60(
    tmp_path: Path,
) -> None:
    # At 10,000, 1,072.98 less 1,883.15 is negative, so line 65 is 0.00.
    value = _line(_sheet(tmp_path, "10000"), IDENTIFIER)

    assert value == D("0.00")
    assert str(value) == "0.00"
    assert not value.is_signed()


def test_line_65_falls_when_line_62_and_line_63_raise_line_64(tmp_path: Path) -> None:
    # An amount of 1,000.00 gives line 63 of 500.00; line 64 is 2,176.12 + 500.00 = 2,676.12 and
    # line 65 is 7,923.71 less 2,676.12, which is 5,247.59.
    sheet = _sheet(tmp_path, "70000", line_63_amount="1000.00")

    assert _line(sheet, LINE_64) == D("2676.12")
    assert _line(sheet, IDENTIFIER) == D("5247.59")


def test_line_65_falls_when_line_62_is_given(tmp_path: Path) -> None:
    # Line 12000 of 1,000.00 and line 12010 of 400.00 make line 62 51.13 (3.13 plus 48.00), so line
    # 64 is 2,227.25. Line 12000 is also income, so line 60 rises too: line 65 is line 60 less 64.
    sheet = _sheet(tmp_path, "70000", line_62="1000.00")

    assert _line(sheet, LINE_64) == D("2227.25")
    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_60) - D("2227.25")


def test_line_65_rises_when_line_59_raises_line_60(tmp_path: Path) -> None:
    # Line 59 of 100.00 makes line 60 8,023.71; 8,023.71 less 2,176.12 is 5,847.59.
    sheet = _sheet(tmp_path, "70000", line_59="100.00")

    assert _line(sheet, LINE_60) == D("8023.71")
    assert _line(sheet, IDENTIFIER) == D("5847.59")


def test_line_65_has_no_left_blank_row_of_its_own(tmp_path: Path) -> None:
    # With lines 59 and 62 given, the steps that read them print no blank row, and line 65's step
    # (which has no blank rule) prints none either.
    sheet = _sheet(tmp_path, "70000", line_59="100.00", line_62="1000.00", line_63_amount="1000.00")

    assert EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert not _blank_rows(sheet)


def test_the_sheet_prints_no_title_and_the_reference_of_line_65(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "65"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "65",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"amount": LINE_60, "less": LINE_64},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step
    assert "blank" not in step


def test_line_65_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_TAX_AFTER_CREDITS_LINE_65
