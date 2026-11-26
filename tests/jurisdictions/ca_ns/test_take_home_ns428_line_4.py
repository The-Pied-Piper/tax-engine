"""NS428 (2025) line 4, the taxable income over the column's lower bound, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 2026-11-26): "Line 2 minus line 3 (cannot be negative)
=". Line 2 is a copy of line 1 and has no step, so line 4 reads line 1 directly; line 3 is the
printed lower bound of the column line 1 falls in. The step is `core/subtract_not_below_zero` with
`ca-ns/cent_rounding`, no title. Hand figures: 20,000 gives 19,835.00 less 0.00; 70,000 gives
69,335.00 less 61,015.00 = 8,320.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_ns import ns428_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal
LINES = (1, 3, 4)
EXPORTS = (s.LINE_1, s.LINE_3, s.LINE_4)


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return s.sheet(tmp_path, salary, LINES, EXPORTS)


def _part() -> Any:
    part = yaml.safe_load(s.part_path(4).read_text(encoding="utf-8"))
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": s.FORM_NAME}
    return part["capabilities"]


@pytest.mark.parametrize(("salary", "line_1"), [*s.CASES, *s.EDGES])
def test_line_4_is_line_1_less_line_3(tmp_path: Path, salary: str, line_1: str) -> None:
    expected = max(D(line_1) - s.column(D(line_1))[0], D(0))
    value = _sheet(tmp_path, salary).get(s.kind(s.LINE_4)).value

    assert value == expected
    assert str(value) == str(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "19835.00"),
        ("40000", "9128.00"),
        ("70000", "8320.00"),
        ("100000", "3043.00"),
        ("200000", "44276.00"),
        # At a bound line 1 is in the lower column, so line 4 is the whole column width; one
        # cent more starts the next column with 0.01.
        ("30779.80", "30507.00"),
        ("30779.81", "0.01"),
        ("155724.01", "0.01"),
    ],
)
def test_line_4_at_the_hand_figures(tmp_path: Path, salary: str, expected: str) -> None:
    value = _sheet(tmp_path, salary).get(s.kind(s.LINE_4)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize("salary", s.ABOVE_TOP)
def test_line_4_is_not_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(s.kind(s.LINE_4))

    assert not artifact.is_blank
    assert artifact.value == s.taxable_income(D(salary)) - D("154650.00")


def test_the_trace_records_the_subtraction_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=s.kind(s.LINE_4),
        minuend=s.kind(s.LINE_1),
        minuend_amount=D("69335.00"),
        subtrahend=s.kind(s.LINE_3),
        subtrahend_amount=D("61015.00"),
        rounding=s.parameter_source().get(s.ROUNDING, 2025, ROUNDING_ONLY).rounding,
        result=D("8320.00"),
    )


def test_the_part_is_one_untitled_subtract_not_below_zero_step_over_lines_1_and_3() -> None:
    (step,) = _part()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "4",
        "unit": "ca/cad",
        "params": {"rounding": s.ROUNDING},
        "consumes": {"amount": s.LINE_1, "less": s.LINE_3},
        "produces": {"output": s.LINE_4},
    }


def test_line_4_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = nova_scotia_kinds()

    assert s.LINE_4 in kinds.identifiers()
    kind = kinds.kind(s.LINE_4)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
