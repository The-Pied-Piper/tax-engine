"""Worksheet MB428 (2025) line 8, line 6 multiplied by line 7, from the real parts.

Form text (Worksheet MB428, CRA 5007-D, 2025, from the ticket):
"Line 8: Line 6 multiplied by line 7 = ^".
The form names no label for the line, so the step has no title. Line 8 is one core/multiply step
over line 6 (`multiplicand`) and line 7 (`multiplier`), rounded by `ca-mb/cent_rounding` (half-up to
the cent, as the forms state no rounding rule). Line 6 is a ratio, not a rate: it can exceed 1 (a
net income above 400,000.00 gives a line 4 above the 200,000.00 threshold), which
`core/multiply_by_rate` would refuse, so the step is `core/multiply`. Its unit is `ca/cad`. The kind
`ca-mb/worksheet_mb428_line_8` is non-negative.

The test composes the real Manitoba salary part, the real federal parts the T1 taxable income form
needs, the real line 2 to 7 parts and the new `worksheet_mb428_line_8.yaml`, and types in only the
salary. The header and the Worksheet MB428 form declaration are made up here, because the shared
scaffold owns them.

Figures: line 6 is 0 at $10,000 and $200,000 (the line 6 test pins this), and line
7 is 15,780.00 (the basic personal amount dataset), so line 8 is 0.00 there. The cases below are
this test's own additions (not in the ticket), each product recomputed exactly:
- $251,074: net income 251,074 - 678.00 - 396.00 = 250,000.00, line 4 50,000.00, line 6 0.25, line 8
  = 0.25 x 15,780.00 = 3,945.00.
- $300,000: net income 298,926.00, line 4 98,926.00, line 6 0.49463, line 8 = 0.49463 x 15,780.00 =
  7,805.2614, half-up to the cent 7,805.26.
- $450,000: net income 450,000 - 678.00 - 396.00 = 448,926.00 (the recomputed enhanced CPP is
  capped at 71,300 and 81,200), line 4 248,926.00, line 6 = 248,926.00 / 200,000.00 = 1.24463, above
  1; line 8 = 1.24463 x 15,780.00 = 19,640.2614, half-up to 19,640.26. This proves no rate limit.
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
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, ProductLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_part_names, form_parts
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
PART = MB_PARTS / "worksheet_mb428_line_8.yaml"
LINE_6 = "ca-mb/worksheet_mb428_line_6"
KIND = "ca-mb/worksheet_mb428_line_8"
LINE_2 = "ca-mb/worksheet_mb428_line_2"
LINE_3 = "ca-mb/worksheet_mb428_basic_personal_amount_line_3"
LINE_4 = "ca-mb/worksheet_mb428_line_4"
LINE_5 = "ca-mb/worksheet_mb428_basic_personal_amount_line_5"
LINE_7 = "ca-mb/worksheet_mb428_basic_personal_amount_line_7"
ROUNDING = "ca-mb/cent_rounding"
FORM_NAME = "ca-mb/worksheet_mb428"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 2 to 5.
FEDERAL_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

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
        - ca-mb/worksheet_mb428_line_2
        - ca-mb/worksheet_mb428_basic_personal_amount_line_3
        - ca-mb/worksheet_mb428_line_4
        - ca-mb/worksheet_mb428_basic_personal_amount_line_5
        - ca-mb/worksheet_mb428_line_6
        - ca-mb/worksheet_mb428_basic_personal_amount_line_7
        - ca-mb/worksheet_mb428_line_8
    capabilities: []
    """)

# salary, line 6, line 7, line 8. The first four are the ticket's salaries: line 6 is 0, so line 8
# is 0.00.
ZERO = [
    ("10000", "0", "15780.00", "0.00"),
    ("200000", "0", "15780.00", "0.00"),
]
# salary, net income (line 2), line 6, line 8: this test's own additions (not in the ticket). The
# last has a line 6 above 1.
POSITIVE = [
    ("251074", "250000.00", "0.25", "3945.00"),
    ("300000", "298926.00", "0.49463", "7805.26"),
    ("450000", "448926.00", "1.24463", "19640.26"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "worksheet_mb428_line_2.yaml"
    yield MB_PARTS / "worksheet_mb428_line_3.yaml"
    yield MB_PARTS / "worksheet_mb428_line_4.yaml"
    yield MB_PARTS / "worksheet_mb428_line_5.yaml"
    yield MB_PARTS / "worksheet_mb428_line_6.yaml"
    yield MB_PARTS / "worksheet_mb428_line_7.yaml"
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


def _line_8(sheet: Worksheet) -> Decimal:
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


def _expected(line_6: Decimal, line_7: Decimal) -> Decimal:
    """The exact product, rounded once half-up to the cent."""
    return _cent(line_6 * line_7)


@pytest.mark.parametrize(("salary", "line_6", "line_7", "expected"), ZERO)
def test_line_8_is_zero_while_line_6_is_zero_at_each_ticket_salary(
    tmp_path: Path, salary: str, line_6: str, line_7: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    assert sheet.get(kinds.kind(LINE_6)).value == D(line_6)
    assert sheet.get(kinds.kind(LINE_7)).value == D(line_7)
    assert _line_8(sheet) == D(expected)
    assert str(_line_8(sheet)) == expected
    assert not _line_8(sheet).is_signed()


@pytest.mark.parametrize(("salary", "line_2", "line_6", "expected"), POSITIVE)
def test_line_8_is_line_6_times_line_7_rounded_half_up_to_the_cent(
    tmp_path: Path, salary: str, line_2: str, line_6: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    # Net income is recomputed from the salary; line 6 is (net income - 200,000.00) / 200,000.00.
    assert _net_income(D(salary)) == D(line_2)
    assert sheet.get(kinds.kind(LINE_2)).value == D(line_2)
    assert sheet.get(kinds.kind(LINE_6)).value == D(line_6)
    assert sheet.get(kinds.kind(LINE_7)).value == D("15780.00")
    assert _line_8(sheet) == D(expected)
    assert str(_line_8(sheet)) == expected
    assert _line_8(sheet) == _expected(D(line_6), D("15780.00"))


def test_line_8_computes_when_line_6_is_above_one(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "450000")
    line_6 = D(sheet.get(manitoba_kinds().kind(LINE_6)).value)

    # (448,926.00 - 200,000.00) / 200,000.00 = 1.24463: a rate above 1 would be refused by
    # core/multiply_by_rate, the product is not.
    assert line_6 > 1
    assert _net_income(D("450000")) - D("200000.00") == D("248926.00")
    assert _line_8(sheet) == D("19640.26")


def test_line_8_is_rounded_once_from_the_exact_product(tmp_path: Path) -> None:
    # 0.49463 x 15,780.00 = 7,805.2614 exactly; the rounded figure is 7,805.26.
    assert D("0.49463") * D("15780.00") == D("7805.2614")
    assert _line_8(_sheet(tmp_path, "300000")) == D("7805.26")


def test_line_8_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(manitoba_kinds().kind(KIND)).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def test_the_step_traces_one_product_line_rounded_to_the_cent(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")
    kinds = manitoba_kinds()

    assert _rounding().rounding == RoundTo(CENT, RoundingMode.HALF_UP)
    (line,) = [t for t in sheet.trace if isinstance(t, ProductLine)]
    assert line == ProductLine(
        output=kinds.kind(KIND),
        multiplicand=kinds.kind(LINE_6),
        multiplicand_amount=D("0.49463"),
        multiplier=kinds.kind(LINE_7),
        multiplier_amount=D("15780.00"),
        rounding=RoundTo(CENT, RoundingMode.HALF_UP),
        result=D("7805.26"),
    )


def test_the_zero_row_traces_the_product_of_zero(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = manitoba_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, ProductLine)]
    assert line.multiplicand == kinds.kind(LINE_6)
    assert line.multiplicand_amount == D("0")
    assert line.multiplier == kinds.kind(LINE_7)
    assert line.multiplier_amount == D("15780.00")
    assert line.result == D("0.00")
    assert line.rounding == RoundTo(CENT, RoundingMode.HALF_UP)


def test_the_product_row_reads_in_english_as_rounded_to_the_cent(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    (row,) = [row for row in rows if " multiplied by " in row]
    assert "0.49463" in row
    assert "15780.00" in row
    assert "gives" in row
    assert "7805.26" in row
    assert row.endswith("(rounded to the nearest cent).")


def test_the_part_is_one_untitled_multiply_step_in_canadian_dollars() -> None:
    step = _step()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/multiply",
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"multiplicand": LINE_6, "multiplier": LINE_7},
        "produces": {"output": KIND},
    }


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(KIND)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
