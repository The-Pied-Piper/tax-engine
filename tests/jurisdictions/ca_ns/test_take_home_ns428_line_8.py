"""NS428 (2025) line 8, the Nova Scotia tax on taxable income, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 2026-11-26 from the PDF 5003-c-25e): "Line 6 plus
line 7 Nova Scotia tax on taxable income =" and "Enter the amount from line 8 on line 53". Line 8
is a `core/sum` over lines 6 and 7 with `ca-ns/cent_rounding`, titled "Nova Scotia tax on taxable
income".
Line 53 is a copy of line 8 and has no step: the tax after credits reads line 8 directly (as
Saskatchewan's line 58 does).

Hand figures (the ticket's): 20,000 gives 1,743.50; 30,000 gives 2,613.71; 70,000 gives 8,320.00 x
16.67% = 1,386.94 plus 7,242.51 = 8,629.45. One more value in each other column, hand-computed:
40,000 gives 9,128.00 x 14.95% = 1,364.64 plus 2,681.57 = 4,046.21; 100,000 gives 3,043.00 x 17.5%
= 532.53 plus 13,055.01 = 13,587.54; 200,000 gives 44,276.00 x 21% = 9,297.96 plus 23,339.23 =
32,637.19. At a bound value line 1 is in the lower column, so line 8 is its full-column tax (line 6,
printed to the cent) plus its line 7; the form's constants are the unrounded sums, so at 61,015 and
154,650 the lower column gives 7,242.52 and 23,339.24 against 7,242.51 and 23,339.23 one cent
higher: the form's own figures, taken as printed.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_ns import ns428_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal
LINES = (1, 3, 4, 5, 6, 7, 8)
EXPORTS = (s.LINE_6, s.LINE_7, s.LINE_8)


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return s.sheet(tmp_path, salary, LINES, EXPORTS)


def _part() -> Any:
    part = yaml.safe_load(s.part_path(8).read_text(encoding="utf-8"))
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": s.FORM_NAME}
    return part["capabilities"]


HAND = [
    ("20000", "1743.50"),
    ("30000", "2613.71"),
    ("40000", "4046.21"),
    ("70000", "8629.45"),
    ("100000", "13587.54"),
    ("200000", "32637.19"),
]
# The bound values: line 1 exactly at 30,507 / 61,015 / 95,883 / 154,650 (the lower column), and
# one cent more (the next column).
BOUNDS = [
    ("30779.80", "2681.57"),
    ("30779.81", "2681.57"),
    ("61595.96", "7242.52"),
    ("61595.97", "7242.51"),
    ("96957.00", "13055.01"),
    ("96957.01", "13055.01"),
    ("155724.00", "23339.24"),
    ("155724.01", "23339.23"),
]


@pytest.mark.parametrize(("salary", "expected"), [*HAND, *BOUNDS])
def test_line_8_is_the_tax_on_taxable_income(tmp_path: Path, salary: str, expected: str) -> None:
    # The form's arithmetic in Decimal is checked before the engine is asked.
    assert s.derived(D(salary))[s.LINE_8] == D(expected)
    value = _sheet(tmp_path, salary).get(s.kind(s.LINE_8)).value

    assert value == D(expected)
    assert isinstance(value, Decimal)
    assert str(value) == expected


@pytest.mark.parametrize(("salary", "expected"), HAND)
def test_line_8_equals_line_6_plus_line_7_exactly(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    six, seven = sheet.get(s.kind(s.LINE_6)).value, sheet.get(s.kind(s.LINE_7)).value
    assert isinstance(six, Decimal)
    assert isinstance(seven, Decimal)

    assert sheet.get(s.kind(s.LINE_8)).value == six + seven


@pytest.mark.parametrize("salary", s.ABOVE_TOP)
def test_line_8_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(s.kind(s.LINE_8))

    assert not artifact.is_blank
    assert artifact.value == s.derived(D(salary))[s.LINE_8]


def test_the_sheet_prints_the_title_and_the_reference_of_line_8(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = s.kind(s.LINE_8).label

    assert sheet.title(label) == "Nova Scotia tax on taxable income"
    assert sheet.reference(label) == "8"


def test_the_trace_adds_line_6_and_line_7_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line = SumLine(
        output=s.kind(s.LINE_8),
        parts=((s.kind(s.LINE_6), D("1386.94")), (s.kind(s.LINE_7), D("7242.51"))),
        rounding=s.parameter_source().get(s.ROUNDING, 2025, ROUNDING_ONLY).rounding,
        total=D("8629.45"),
    )
    assert line in sheet.trace


def test_the_sum_reads_in_english_as_line_6_plus_line_7_with_its_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [
        each
        for each in sheet.trace
        if isinstance(each, SumLine) and each.output is s.kind(s.LINE_8)
    ]
    text = EnglishTraceRenderer().render(line)

    assert " plus " in text
    assert "1386.94" in text
    assert "7242.51" in text
    assert text.endswith("8629.45 (rounded to the nearest cent).")


def test_the_part_is_one_titled_sum_step_over_lines_6_and_7() -> None:
    (step,) = _part()

    assert list(step) == ["name", "title", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "title": "Nova Scotia tax on taxable income",
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": s.ROUNDING},
        "consumes": {"parts": [s.LINE_6, s.LINE_7]},
        "produces": {"output": s.LINE_8},
    }


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = nova_scotia_kinds()

    assert s.LINE_8 in kinds.identifiers()
    kind = kinds.kind(s.LINE_8)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_ON_TAXABLE_INCOME_LINE_8
