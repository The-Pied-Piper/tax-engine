"""Worksheet MB428 (2025) line 9, line 1 minus line 8 (not below 0), from the real parts.

Form text (Worksheet MB428, CRA 5007-D, 2025, from the ticket):
"Line 9: Line 1 minus line 8 (if negative, enter \\"0\\") Enter this amount on line 58040 of your
Form MB428. = ^".
The form names no label for the line, so the step has no title. Line 9 is one
core/subtract_not_below_zero step over line 1 (`amount`) and line 8 (`less`), rounded half-up to the
cent by `ca-mb/cent_rounding`. The kind `ca-mb/worksheet_mb428_basic_personal_amount_line_9` is
non-negative; it is the figure the form says to enter on line 58040 of Form MB428.

The test composes the real Manitoba salary part, the real federal parts the T1 taxable income form
needs, the real parts of lines 1 to 8 and the new
`worksheet_mb428_line_9.yaml`, and types in only the salary. The header and
the Worksheet MB428 form declaration (exporting lines 1 to 9) are made up here, because the shared
scaffold owns them.

Figures: line 1 is 15,780.00 (the basic personal amount dataset). Line 8 is 0.00 at $10,000
and $200,000 (the line 8 test pins this), so line 9 is 15,780.00 there. The two
larger cases come from the line 8 test and are recomputed here:
- $300,000: net income 300,000 - 678.00 - 396.00 = 298,926.00, line 6 0.49463, line 8 = 0.49463 x
  15,780.00 = 7,805.2614, half-up to the cent 7,805.26; line 9 = 15,780.00 - 7,805.26 = 7,974.74.
- $450,000: net income 448,926.00, line 6 1.24463, line 8 = 1.24463 x 15,780.00 = 19,640.2614,
  half-up to 19,640.26, above line 1, so the floor bites and line 9 = 0.00.
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
import tax_engine.jurisdictions.ca_mb
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
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = MB_PARTS / "worksheet_mb428_line_9.yaml"
KIND = "ca-mb/worksheet_mb428_basic_personal_amount_line_9"
LINE_1 = "ca-mb/worksheet_mb428_basic_personal_amount_line_1"
LINE_2 = "ca-mb/worksheet_mb428_line_2"
LINE_6 = "ca-mb/worksheet_mb428_line_6"
LINE_8 = "ca-mb/worksheet_mb428_line_8"
ROUNDING = "ca-mb/cent_rounding"
FORM_NAME = "ca-mb/worksheet_mb428"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 1 to 8.
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
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
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

# salary, line 1, line 8, line 9. The first four are the ticket's salaries: line 8 is 0.00, so
# line 9 is line 1.
UNREDUCED = [
    ("10000", "15780.00", "0.00", "15780.00"),
    ("200000", "15780.00", "0.00", "15780.00"),
]
# salary, line 1, line 8, line 9: line 8 reduces line 1 but stays below it.
REDUCED = ("300000", "15780.00", "7805.26", "7974.74")
# salary, line 1, line 8, line 9: line 8 is above line 1, so the floor bites.
FLOORED = ("450000", "15780.00", "19640.26", "0.00")


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "worksheet_mb428_line_1.yaml"
    yield MB_PARTS / "worksheet_mb428_line_2.yaml"
    yield MB_PARTS / "worksheet_mb428_line_3.yaml"
    yield MB_PARTS / "worksheet_mb428_line_4.yaml"
    yield MB_PARTS / "worksheet_mb428_line_5.yaml"
    yield MB_PARTS / "worksheet_mb428_line_6.yaml"
    yield MB_PARTS / "worksheet_mb428_line_7.yaml"
    yield MB_PARTS / "worksheet_mb428_line_8.yaml"
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _rounding() -> Any:
    return YamlParameterSource(
        manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _line_9(sheet: Worksheet) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(KIND)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize(("salary", "line_1", "line_8", "expected"), UNREDUCED)
def test_line_9_is_line_1_while_line_8_is_zero_at_each_ticket_salary(
    tmp_path: Path, salary: str, line_1: str, line_8: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    assert sheet.get(kinds.kind(LINE_1)).value == D(line_1)
    assert sheet.get(kinds.kind(LINE_8)).value == D(line_8)
    assert _line_9(sheet) == D(expected)
    assert str(_line_9(sheet)) == expected
    assert not _line_9(sheet).is_signed()


def test_line_9_is_line_1_minus_line_8_when_line_8_is_below_line_1(tmp_path: Path) -> None:
    salary, line_1, line_8, expected = REDUCED
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    # Net income is recomputed from the salary; line 8 = 0.49463 x 15,780.00 = 7,805.2614, rounded
    # half-up to 7,805.26; 15,780.00 - 7,805.26 = 7,974.74.
    assert _net_income(D(salary)) == D("298926.00")
    assert sheet.get(kinds.kind(LINE_2)).value == D("298926.00")
    assert sheet.get(kinds.kind(LINE_6)).value == D("0.49463")
    assert D("0.49463") * D("15780.00") == D("7805.2614")
    assert sheet.get(kinds.kind(LINE_1)).value == D(line_1)
    assert sheet.get(kinds.kind(LINE_8)).value == D(line_8)
    assert D(line_1) - D(line_8) == D(expected)
    assert _line_9(sheet) == D(expected)
    assert str(_line_9(sheet)) == "7974.74"


def test_line_9_is_zero_when_line_8_is_above_line_1_so_the_floor_bites(tmp_path: Path) -> None:
    salary, line_1, line_8, expected = FLOORED
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    # 1.24463 x 15,780.00 = 19,640.2614, rounded half-up to 19,640.26, above line 1.
    assert _net_income(D(salary)) == D("448926.00")
    assert D("1.24463") * D("15780.00") == D("19640.2614")
    assert sheet.get(kinds.kind(LINE_1)).value == D(line_1)
    assert sheet.get(kinds.kind(LINE_8)).value == D(line_8)
    assert D(line_8) > D(line_1)
    line_9 = _line_9(sheet)
    assert line_9 == D(expected)
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert str(line_9) == "0.00"
    assert line_9.as_tuple().exponent == -2
    assert not line_9.is_signed()


def test_line_9_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(manitoba_kinds().kind(KIND)).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def test_the_step_traces_a_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "300000")
    kinds = manitoba_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output == kinds.kind(KIND)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(KIND),
        minuend=kinds.kind(LINE_1),
        minuend_amount=D("15780.00"),
        subtrahend=kinds.kind(LINE_8),
        subtrahend_amount=D("7805.26"),
        rounding=_rounding().rounding,
        result=D("7974.74"),
    )


def test_the_floored_row_traces_the_subtraction_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "450000")
    kinds = manitoba_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output == kinds.kind(KIND)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(KIND),
        minuend=kinds.kind(LINE_1),
        minuend_amount=D("15780.00"),
        subtrahend=kinds.kind(LINE_8),
        subtrahend_amount=D("19640.26"),
        rounding=_rounding().rounding,
        result=D("0.00"),
    )


def test_the_part_is_one_untitled_subtract_not_below_zero_step_with_no_blank_rule() -> None:
    step = _step()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "9",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_1, "less": LINE_8},
        "produces": {"output": KIND},
    }


def test_line_9_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(KIND)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
