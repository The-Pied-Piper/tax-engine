"""Worksheet MB428 (2025) line 4, line 2 minus line 3 (not below 0), from the real parts.

Form text (Worksheet MB428, CRA 5007-D, 2025, from the ticket):
"Line 4: Line 2 minus line 3 (if negative, enter \\"0\\") = ^".
The form names no label for the line, so the step has no title. Line 4 is one
core/subtract_not_below_zero step over line 2 (`amount`) and line 3 (`less`), rounded half-up to the
cent by `ca-mb/cent_rounding`. The kind `ca-mb/worksheet_mb428_line_4` is non-negative.

The test composes the T1 employment income form, the real federal parts the T1 taxable income form
needs (as the line 2 test does), the real `worksheet_mb428_line_2.yaml` and
`worksheet_mb428_line_3.yaml` parts and the new
`worksheet_mb428_line_4.yaml`, and types in only the salary. The header and the Worksheet MB428
form declaration (exporting lines 2, 3 and 4) are made up here, because the shared scaffold owns
them.

Figures: the ticket's table (hand-computed, not a CRA example) gives line 4 as 0.00 at $10,000
and $200,000: line 2 (net income) is 9,935.00 and 198,926.00, both below line 3 (200,000.00), so
the floor bites. The $300,000 case is this test's own addition, not in the ticket's table: net
income is 300,000 less the enhanced CPP deduction, 1% of (71,300 - 3,500) = 678.00 plus 4% of
(81,200 - 71,300) = 396.00, so 300,000 - 678.00 - 396.00 =
298,926.00, and line 4 = 298,926.00 - 200,000.00 = 98,926.00. It is reached by the salary alone.
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
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "worksheet_mb428_line_4.yaml"
KIND = "ca-mb/worksheet_mb428_line_4"
LINE_2 = "ca-mb/worksheet_mb428_line_2"
LINE_3 = "ca-mb/worksheet_mb428_basic_personal_amount_line_3"
ROUNDING = "ca-mb/cent_rounding"
FORM_NAME = "ca-mb/worksheet_mb428"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 2 and 3.
FEDERAL_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
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
    capabilities: []
    """)

# salary, line 2 (the line 2 test pins these), line 3, line 4. The first four are the ticket's
# table: line 2 is below line 3, so line 4 is the floor, 0.00.
FLOORED = [
    ("10000", "9935.00", "200000.00", "0.00"),
    ("200000", "198926.00", "200000.00", "0.00"),
]
# This test's own addition (not in the ticket's table): line 2 above line 3.
POSITIVE = ("300000", "298926.00", "200000.00", "98926.00")


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "worksheet_mb428_line_2.yaml"
    yield MB_PARTS / "worksheet_mb428_line_3.yaml"
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
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


def _line_4(sheet: Worksheet) -> Decimal:
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


@pytest.mark.parametrize(("salary", "line_2", "line_3", "expected"), FLOORED)
def test_line_4_is_zero_while_line_2_is_below_line_3_at_each_ticket_salary(
    tmp_path: Path, salary: str, line_2: str, line_3: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    # Lines 2 and 3 are recomputed from the real parts, not only taken from the ticket.
    assert _net_income(D(salary)) == D(line_2)
    assert sheet.get(kinds.kind(LINE_2)).value == D(line_2)
    assert sheet.get(kinds.kind(LINE_3)).value == D(line_3)
    line_4 = _line_4(sheet)
    assert line_4 == D(expected)
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert str(line_4) == "0.00"
    assert line_4.as_tuple().exponent == -2
    assert not line_4.is_signed()


def test_line_4_is_line_2_minus_line_3_when_line_2_is_above_line_3_own_addition(
    tmp_path: Path,
) -> None:
    salary, line_2, line_3, expected = POSITIVE
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    # 300,000 - 678.00 - 396.00 = 298,926.00; 298,926.00 - 200,000.00 = 98,926.00.
    assert _net_income(D(salary)) == D(line_2)
    assert sheet.get(kinds.kind(LINE_2)).value == D(line_2)
    assert sheet.get(kinds.kind(LINE_3)).value == D(line_3)
    assert D(line_2) - D(line_3) == D(expected)
    assert _line_4(sheet) == D(expected)
    assert str(_line_4(sheet)) == "98926.00"


def test_line_4_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(manitoba_kinds().kind(KIND)).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = manitoba_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(KIND),
        minuend=kinds.kind(LINE_2),
        minuend_amount=D("69335.00"),
        subtrahend=kinds.kind(LINE_3),
        subtrahend_amount=D("200000.00"),
        rounding=_rounding().rounding,
        result=D("0.00"),
    )


def test_the_positive_row_traces_the_subtraction_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")
    kinds = manitoba_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(KIND),
        minuend=kinds.kind(LINE_2),
        minuend_amount=D("298926.00"),
        subtrahend=kinds.kind(LINE_3),
        subtrahend_amount=D("200000.00"),
        rounding=_rounding().rounding,
        result=D("98926.00"),
    )


def test_the_part_is_one_untitled_subtract_not_below_zero_step_with_no_blank_rule() -> None:
    step = _step()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "4",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_2, "less": LINE_3},
        "produces": {"output": KIND},
    }


def test_line_4_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(KIND)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
