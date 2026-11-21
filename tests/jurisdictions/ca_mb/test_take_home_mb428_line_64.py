"""MB428 (2025) line 64, line 61 plus line 62 plus line 63, from the salary alone, real parts.

Form text (Form MB428, CRA 5007-c): "Line 64: Add lines 61 to 63. = ^". The form prints no title
for the line and no maximum, so the step is untitled and has no cap. Line 62, "Line 62 and line
61520: Manitoba dividend tax credit (use Worksheet MB428)", is an optional input, blank for a
salary-only filer. Line 63 is its own calculation (50% of the optional amount from line 40427),
always computed because that step reads a blank amount as 0. Line 64 is one core/sum over lines 61,
62 and 63; the blank line 62 is read as 0 and the step prints its own "left blank, taken as 0" row.

The test composes the T1 employment income form, the real Schedule 8, T2204 and T1 taxable income
parts, the real parts of Worksheet MB428 lines 1 to 9, Schedule MB428-A lines 1 to 12, MB428 lines
9, 18, 19, 21, 28, 29, 33, 36, 41, 42 and 51 of `ca-mb/mb428_credits`, the line 31, line 50 and line
56 input parts, the real `mb428_credits_line_53.yaml`, `mb428_credits_line_57.yaml`,
`mb428_line_61.yaml`, `mb428_line_62_input.yaml`, `mb428_credits_line_63_input.yaml` and
`mb428_line_63.yaml`, and the new `mb428_line_64.yaml`, and types in only the salary (and, in some
tests, line 62 and the line 63 amount). The header and the form declarations are made up here: the
credits form exports only line 57, and `ca-mb/mb428` exports only line 64. The figures are line 61
(the line 61 test, hand-computed from the printed forms, not a CRA example) plus line 62 and line 63
of 0 when blank: 1,883.15 / 1,858.10 / 2,176.12 / 2,183.07.
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
LINE_PART = MB_PARTS / "mb428_line_64.yaml"
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
LINE_61 = "ca-mb/mb428_non_refundable_credits_line_61"
LINE_62 = "ca-mb/mb428_dividend_tax_credit_line_62"
LINE_63 = "ca-mb/mb428_minimum_tax_carryover_credit_line_63"
IDENTIFIER = "ca-mb/mb428_credits_total_line_64"
CREDIT_PARTS = (
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
    "mb428_credits_line_49_inputs.yaml",
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
# The MB428 credits declaration, test-local: lines 1 to 56 are composed, so it exports only line 57.
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS_FORM_NAME}
      required: true
      exports:
        - {LINE_57}
    capabilities: []
    """)
# The MB428 declaration, test-local: lines 61 to 64 are composed, so it exports only line 64.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 64: line 61 (the same as line 57), plus lines 62 and 63, blank and read as 0.
CASES = [
    ("10000", "1883.15"),
    ("200000", "2183.07"),
]


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
    yield LINE_61_PART
    yield LINE_62_PART
    yield LINE_63_INPUT_PART
    yield LINE_63_PART
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
    tmp_path: Path, salary: str, line_62: str | None = None, line_63_amount: str | None = None
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_62 is not None:
        given.append(Artifact(mb_catalog.MB428_DIVIDEND_TAX_CREDIT_LINE_62, D(line_62)))
    if line_63_amount is not None:
        given.append(Artifact(mb_catalog.MB428_MINIMUM_TAX_CARRYOVER_LINE_63, D(line_63_amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


def _blank_rows(sheet: Worksheet) -> list[str]:
    rows = EnglishTraceRenderer().render_all(sheet.trace)
    return [row for row in rows if "left blank, taken as 0" in row.lower()]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_64_is_line_61_when_lines_62_and_63_are_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_61) == D(expected)
    assert _line(sheet, LINE_63) == D("0")
    assert str(_line(sheet, IDENTIFIER)) == expected


def test_line_64_adds_line_62_when_it_is_given(tmp_path: Path) -> None:
    # Line 61 at a 70,000 salary is 2,176.12; line 62 of 100.00 makes 2,276.12.
    sheet = _sheet(tmp_path, "70000", line_62="100.00")

    assert _line(sheet, IDENTIFIER) == D("2276.12")


def test_line_64_adds_line_63_when_its_amount_is_given(tmp_path: Path) -> None:
    # An amount of 1,000.00 gives line 63 of 500.00 (50%); 2,176.12 plus 500.00 is 2,676.12.
    sheet = _sheet(tmp_path, "70000", line_63_amount="1000.00")

    assert _line(sheet, LINE_63) == D("500.00")
    assert _line(sheet, IDENTIFIER) == D("2676.12")


def test_line_64_adds_lines_61_62_and_63_when_both_optionals_are_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", line_62="100.00", line_63_amount="1000.00")

    assert _line(sheet, IDENTIFIER) == D("2776.12")


def test_a_given_line_62_prints_no_left_blank_row_from_line_64(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", line_62="100.00", line_63_amount="1000.00")

    assert EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert not _blank_rows(sheet)


def test_the_sheet_prints_no_title_and_the_reference_of_line_64(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "64"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_over_lines_61_to_63() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "64",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_61, LINE_62, LINE_63]},
        "blank": {LINE_62: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_64_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_CREDITS_TOTAL_LINE_64
