"""PE428 (2025) line 5, the rate of the column line 1 falls in, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): the five columns print "Line 5:" 9.5%,
13.47%, 16.6%, 17.62% and 19%. The step is `core/bracket_column_rate` over `ca-pe/brackets`,
titled "Rate" as Saskatchewan's is; a line 1 exactly at a column's upper bound is in that column.
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
LINES = (1, 5)
EXPORTS = (s.LINE_1, s.LINE_5)


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return s.sheet(tmp_path, salary, LINES, EXPORTS)


def _part() -> Any:
    part = yaml.safe_load(s.part_path(5).read_text(encoding="utf-8"))
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": s.FORM_NAME}
    return part["capabilities"]


PERCENT = {"0.095": "9.5", "0.1347": "13.47", "0.166": "16.6", "0.1762": "17.62", "0.19": "19"}


@pytest.mark.parametrize(("salary", "line_1"), [*s.CASES, *s.EDGES])
def test_line_5_is_the_rate_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    value = _sheet(tmp_path, salary).get(s.kind(s.LINE_5)).value

    assert value == s.column(D(line_1))[1]
    assert isinstance(value, Decimal)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "0.095"),
        ("33629.29", "0.095"),
        ("33629.30", "0.1347"),
        ("65273.74", "0.1347"),
        ("65273.75", "0.166"),
        ("106074", "0.166"),
        ("106074.01", "0.1762"),
        ("141074", "0.1762"),
        ("141074.01", "0.19"),
    ],
)
def test_line_5_at_the_bound_values(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(s.kind(s.LINE_5)).value == D(expected)


@pytest.mark.parametrize("salary", s.ABOVE_TOP)
def test_line_5_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(s.kind(s.LINE_5))

    assert not artifact.is_blank
    assert artifact.value == D("0.19")


@pytest.mark.parametrize(("salary", "line_1"), s.CASES)
def test_the_trace_names_the_rate_of_the_bracket_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    expected = s.column(D(line_1))[1]
    line = BracketColumnFigureLine(
        output=s.kind(s.LINE_5),
        base=s.kind(s.LINE_1),
        base_amount=D(line_1),
        name="rate",
        figure=expected,
    )

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith(f"falls in a bracket with the rate {PERCENT[str(expected)]}%.")
    )


def test_the_part_is_one_titled_bracket_column_rate_step_over_line_1() -> None:
    (step,) = _part()

    assert list(step) == ["name", "title", "reference", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_rate",
        "title": "Rate",
        "reference": "5",
        "params": {"schedule": s.BRACKETS},
        "consumes": {"base": s.LINE_1},
        "produces": {"output": s.LINE_5},
    }


def test_line_5_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = prince_edward_island_kinds()

    assert s.LINE_5 in kinds.identifiers()
    kind = kinds.kind(s.LINE_5)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is pe_catalog.PE428_BRACKET_RATE_LINE_5
