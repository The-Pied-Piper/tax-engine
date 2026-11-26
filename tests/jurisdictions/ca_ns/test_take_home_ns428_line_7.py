"""NS428 (2025) line 7, the printed figure of the column line 1 falls in, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 2026-11-26): the five columns print "Line 7:" 0.00,
2,681.57, 7,242.51, 13,055.01 and 23,339.23. The step takes the printed figure of the column line 1
falls in (`core/bracket_column_tax_at_start`), never computed from the rates; the form prints no
title for line 7. Checked: 30,507 x 8.79% = 2,681.57; + 30,508 x 14.95% = 7,242.51; + 34,868 x
16.67% = 13,055.01; + 58,767 x 17.5% = 23,339.23 (each to the cent).
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
from tax_engine.domain.trace import BracketColumnFigureLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_ns import ns428_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal
LINES = (1, 7)
EXPORTS = (s.LINE_1, s.LINE_7)


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return s.sheet(tmp_path, salary, LINES, EXPORTS)


def _part() -> Any:
    part = yaml.safe_load(s.part_path(7).read_text(encoding="utf-8"))
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": s.FORM_NAME}
    return part["capabilities"]


@pytest.mark.parametrize(("salary", "line_1"), [*s.CASES, *s.EDGES])
def test_line_7_is_the_printed_figure_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    value = _sheet(tmp_path, salary).get(s.kind(s.LINE_7)).value

    assert value == s.column(D(line_1))[2]
    assert str(value) == str(s.column(D(line_1))[2])


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "0.00"),
        ("40000", "2681.57"),
        ("70000", "7242.51"),
        ("100000", "13055.01"),
        ("200000", "23339.23"),
    ],
)
def test_line_7_at_the_hand_figures(tmp_path: Path, salary: str, expected: str) -> None:
    value = _sheet(tmp_path, salary).get(s.kind(s.LINE_7)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize("salary", s.ABOVE_TOP)
def test_line_7_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(s.kind(s.LINE_7))

    assert not artifact.is_blank
    assert artifact.value == D("23339.23")


@pytest.mark.parametrize(("salary", "line_1"), s.CASES)
def test_the_trace_names_the_tax_at_start_of_the_bracket_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    expected = s.column(D(line_1))[2]
    line = BracketColumnFigureLine(
        output=s.kind(s.LINE_7),
        base=s.kind(s.LINE_1),
        base_amount=D(line_1),
        name="tax at start",
        figure=expected,
    )

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith(f"falls in a bracket with {expected:.2f} of tax on the income below it.")
    )


def test_the_part_is_one_untitled_bracket_column_tax_at_start_step_over_line_1() -> None:
    (step,) = _part()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_tax_at_start",
        "reference": "7",
        "unit": "ca/cad",
        "params": {"schedule": s.BRACKETS},
        "consumes": {"base": s.LINE_1},
        "produces": {"output": s.LINE_7},
    }


def test_line_7_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = nova_scotia_kinds()

    assert s.LINE_7 in kinds.identifiers()
    kind = kinds.kind(s.LINE_7)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_BRACKET_TAX_AT_START_LINE_7
