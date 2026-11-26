"""PE428 (2025) line 3, the lower bound of the column line 1 falls in, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): the five columns print "Line 3: 0.00",
"33,328.00", "64,656.00", "105,000.00" and "140,000.00" under "Column 1: Line 1 is $33,328.00 or
less", "Column 2: ... more than $33,328 but not more than $64,656", "Column 3: ... more than
$64,656 but not more than $105,000", "Column 4: ... more than $105,000 but not more than $140,000"
and "Column 5: more than $140,000". A line 1 exactly at a column's upper bound is in that column.

The step is `core/bracket_column_lower_bound` over `ca-pe/brackets`, one step with no title.
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
from tax_engine.domain.trace import BracketColumnFigureLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_pe import pe428_support as s
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
LINES = (1, 3)
EXPORTS = (s.LINE_1, s.LINE_3)


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return s.sheet(tmp_path, salary, LINES, EXPORTS)


def _part() -> Any:
    part = yaml.safe_load(s.part_path(3).read_text(encoding="utf-8"))
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": s.FORM_NAME}
    return part["capabilities"]


@pytest.mark.parametrize(("salary", "line_1"), [*s.CASES, *s.EDGES])
def test_line_3_is_the_lower_bound_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    assert s.taxable_income(D(salary)) == D(line_1)
    sheet = _sheet(tmp_path, salary)
    value = sheet.get(s.kind(s.LINE_3)).value

    assert value == s.column(D(line_1))[0]
    assert str(value) == str(s.column(D(line_1))[0])


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "0.00"),
        ("40000", "33328.00"),
        ("50469.70", "33328.00"),
        ("70000", "64656.00"),
        ("121074", "105000.00"),
        ("201074", "140000.00"),
        ("33629.30", "33328.00"),
        ("106074.01", "105000.00"),
    ],
)
def test_line_3_at_the_hand_figures(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(s.kind(s.LINE_3)).value == D(expected)


@pytest.mark.parametrize("salary", s.ABOVE_TOP)
def test_line_3_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(s.kind(s.LINE_3))

    assert not artifact.is_blank
    assert artifact.value == D("140000.00")


@pytest.mark.parametrize(("salary", "line_1"), s.CASES)
def test_the_trace_names_the_bracket_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    expected = s.column(D(line_1))[0]
    line = BracketColumnFigureLine(
        output=s.kind(s.LINE_3),
        base=s.kind(s.LINE_1),
        base_amount=D(line_1),
        name="lower bound",
        figure=expected,
    )

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith(f"falls in the bracket that starts at {expected:.2f}.")
    )


def test_the_part_is_one_untitled_bracket_column_lower_bound_step_over_line_1() -> None:
    (step,) = _part()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_lower_bound",
        "reference": "3",
        "unit": "ca/cad",
        "params": {"schedule": s.BRACKETS},
        "consumes": {"base": s.LINE_1},
        "produces": {"output": s.LINE_3},
    }


def test_line_3_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = prince_edward_island_kinds()

    assert s.LINE_3 in kinds.identifiers()
    kind = kinds.kind(s.LINE_3)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is pe_catalog.PE428_BRACKET_LOWER_BOUND_LINE_3
