"""PE428 (2025) line 8, the Prince Edward Island tax on taxable income, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the PDF 5002-c-25e): "Line 6 plus
line 7 Prince Edward Island tax on taxable income" and "Enter the amount from line 8 on line 55".
Line 8 is a `core/sum` over lines 6 and 7 with `ca-pe/cent_rounding`, titled "Prince Edward Island
tax on taxable income". Line 55 is a copy of line 8 and has no step: the later lines read line 8
directly (as Saskatchewan's line 58 does).

Hand figures (the ticket's): 20,000 gives 1,884.33; 30,000 gives 2,824.83; 70,000 gives 4,679.00 x
16.6% = 776.71 plus 7,386.04 = 8,162.75. Taxable incomes of 50,000, 120,000 and 200,000 (columns 2,
4 and 5, from the ticket's comment) give 5,411.88, 16,726.15 and 31,650.15. Also hand-computed:
40,000 gives 6,307.00 x 13.47% = 849.55 plus 3,166.16 = 4,015.71; 100,000 gives 34,270.00 x 16.6% =
5,688.82 plus 7,386.04 = 13,074.86. At a bound value line 1 is in the lower column, so line 8 is
its full-column tax (line 6, printed to the cent) plus its line 7; the form's constants are the
unrounded sums, so at 105,000 the lower column gives 14,083.14 against 14,083.15 one cent higher:
the form's own figures, taken as printed.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe.catalog as pe_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_pe import pe428_support as s
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
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
    ("20000", "1884.33"),
    ("30000", "2824.83"),
    ("40000", "4015.71"),
    ("50469.70", "5411.88"),
    ("70000", "8162.75"),
    ("100000", "13074.86"),
    ("121074", "16726.15"),
    ("200000", "31446.09"),
    ("201074", "31650.15"),
]
# The bound values: line 1 exactly at 33,328 / 64,656 / 105,000 / 140,000 (the lower column), and
# one cent more (the next column).
BOUNDS = [
    ("33629.29", "3166.16"),
    ("33629.30", "3166.16"),
    ("65273.74", "7386.04"),
    ("65273.75", "7386.04"),
    ("106074", "14083.14"),
    ("106074.01", "14083.15"),
    ("141074", "20250.15"),
    ("141074.01", "20250.15"),
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

    assert sheet.title(label) == "Prince Edward Island tax on taxable income"
    assert sheet.reference(label) == "8"


def test_the_trace_adds_line_6_and_line_7_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line = SumLine(
        output=s.kind(s.LINE_8),
        parts=((s.kind(s.LINE_6), D("776.71")), (s.kind(s.LINE_7), D("7386.04"))),
        rounding=s.parameter_source().get(s.ROUNDING, 2025, ROUNDING_ONLY).rounding,
        total=D("8162.75"),
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
    assert "776.71" in text
    assert "7386.04" in text
    assert text.endswith("8162.75 (rounded to the nearest cent).")


def test_the_part_is_one_titled_sum_step_over_lines_6_and_7() -> None:
    (step,) = _part()

    assert list(step) == ["name", "title", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "title": "Prince Edward Island tax on taxable income",
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": s.ROUNDING},
        "consumes": {"parts": [s.LINE_6, s.LINE_7]},
        "produces": {"output": s.LINE_8},
    }


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = prince_edward_island_kinds()

    assert s.LINE_8 in kinds.identifiers()
    kind = kinds.kind(s.LINE_8)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is pe_catalog.PE428_TAX_ON_TAXABLE_INCOME_LINE_8
