"""Unit tests for the three bracket column figure capabilities on a schedule with a range.

A base the schedule does not cover (`schedule.covers(base)` is false) gives a blank `output`
instead of a figure, with one BracketOutsideRangeLine as its trace: the output and base kinds and
the base amount. The slot is declared `MAY_BE_BLANK`, so `run` accepts the blank. A covered base,
and every base of a schedule from 0 with no `up_to`, gives its figure. Made-up values.
"""

from __future__ import annotations

from dataclasses import fields
from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import BracketColumnFigureLine, BracketOutsideRangeLine
from tax_engine.jurisdictions.core.capabilities.bracket_column_figure import (
    BracketColumnFigure,
    BracketColumnLowerBound,
    BracketColumnRate,
    BracketColumnTaxAtStart,
)

D = Decimal

LINE_1 = AmountKind("ex/taxable_base")
FIGURE = AmountKind("ex/column_figure")

# 0 to 100 inclusive: 10% to 50, 20% above.
LOWER = BracketSchedule((Bracket(D(0), D("0.10")), Bracket(D(50), D("0.20"))), up_to=D(100))
# More than 100, no upper end: 30% over 100 on top of 25.00, 40% over 200 on top of 55.00.
UPPER = BracketSchedule(
    (Bracket(D(100), D("0.30"), D("25.00")), Bracket(D(200), D("0.40"), D("55.00")))
)
OPEN = BracketSchedule((Bracket(D(0), D("0.10")), Bracket(D(100), D("0.20"))))

CAPABILITIES = (BracketColumnLowerBound, BracketColumnRate, BracketColumnTaxAtStart)


def dataset(values: BracketSchedule) -> ParameterDataset[BracketSchedule]:
    return ParameterDataset(
        "ex/brackets", 2025, BRACKETS, values, NO_ROUNDING, ("https://example.org/rates",)
    )


def run(cls: type[BracketColumnFigure], base: str, values: BracketSchedule) -> Artifact[Decimal]:
    result = cls(LINE_1, FIGURE, dataset(values)).run((Artifact(LINE_1, D(base)),))
    (output,) = result.outputs
    return output


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_the_output_slot_may_be_blank(cls: type[BracketColumnFigure]) -> None:
    assert cls.MAY_BE_BLANK == frozenset({"output"})


def test_the_shared_base_declares_it_so_the_three_inherit_it() -> None:
    assert BracketColumnFigure.MAY_BE_BLANK == frozenset({"output"})


@pytest.mark.parametrize("cls", CAPABILITIES)
@pytest.mark.parametrize(
    ("base", "values"),
    [("100.01", LOWER), ("70000", LOWER), ("100", UPPER), ("0", UPPER), ("50", UPPER)],
)
def test_a_base_outside_the_range_gives_a_blank_output(
    cls: type[BracketColumnFigure], base: str, values: BracketSchedule
) -> None:
    assert run(cls, base, values) == Artifact(FIGURE, BLANK)


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_a_base_outside_the_range_traces_one_outside_range_line(
    cls: type[BracketColumnFigure],
) -> None:
    result = cls(LINE_1, FIGURE, dataset(UPPER)).run((Artifact(LINE_1, D(100)),))

    assert result.trace == (
        BracketOutsideRangeLine(output=FIGURE, base=LINE_1, base_amount=D(100)),
    )


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_compute_itself_returns_the_blank_and_the_line(cls: type[BracketColumnFigure]) -> None:
    result = cls(LINE_1, FIGURE, dataset(LOWER)).compute((Artifact(LINE_1, D(500)),))

    assert result.outputs == (Artifact(FIGURE, BLANK),)
    assert result.trace == (BracketOutsideRangeLine(FIGURE, LINE_1, D(500)),)


def test_a_base_in_the_lower_range_gives_the_figures_of_its_column() -> None:
    assert run(BracketColumnLowerBound, "30", LOWER).value == D(0)
    assert run(BracketColumnRate, "30", LOWER).value == D("0.10")
    assert run(BracketColumnTaxAtStart, "30", LOWER).value == D(0)


def test_a_base_exactly_at_up_to_is_still_in_the_lower_range() -> None:
    assert run(BracketColumnLowerBound, "100", LOWER).value == D(50)
    assert run(BracketColumnRate, "100", LOWER).value == D("0.20")
    assert run(BracketColumnTaxAtStart, "100", LOWER).value == D("5.0")


def test_a_base_exactly_at_the_boundary_is_in_the_lower_table_only() -> None:
    for cls in CAPABILITIES:
        assert not run(cls, "100", LOWER).is_blank
        assert run(cls, "100", UPPER).is_blank


def test_a_base_just_over_the_boundary_is_in_the_upper_table_only() -> None:
    for cls in CAPABILITIES:
        assert run(cls, "100.01", LOWER).is_blank
        assert not run(cls, "100.01", UPPER).is_blank


def test_a_base_in_a_range_above_zero_gives_the_figures_of_its_column() -> None:
    assert run(BracketColumnLowerBound, "100.01", UPPER).value == D(100)
    assert run(BracketColumnRate, "100.01", UPPER).value == D("0.30")
    assert run(BracketColumnTaxAtStart, "100.01", UPPER).value == D("25.00")
    assert run(BracketColumnLowerBound, "250", UPPER).value == D(200)
    assert run(BracketColumnRate, "250", UPPER).value == D("0.40")
    assert run(BracketColumnTaxAtStart, "250", UPPER).value == D("55.00")


def test_a_covered_base_traces_the_figure_line_as_before() -> None:
    result = BracketColumnRate(LINE_1, FIGURE, dataset(UPPER)).run((Artifact(LINE_1, D(250)),))

    assert result.trace == (
        BracketColumnFigureLine(
            output=FIGURE, base=LINE_1, base_amount=D(250), name="rate", figure=D("0.40")
        ),
    )


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_a_schedule_from_zero_with_no_up_to_never_gives_a_blank(
    cls: type[BracketColumnFigure],
) -> None:
    assert not run(cls, "0", OPEN).is_blank
    assert not run(cls, "1000000", OPEN).is_blank


# --- trace line --------------------------------------------------------------------------------


def test_the_outside_range_line_has_these_fields_in_order() -> None:
    assert [f.name for f in fields(BracketOutsideRangeLine)] == ["output", "base", "base_amount"]


def test_the_outside_range_line_is_frozen() -> None:
    line = BracketOutsideRangeLine(FIGURE, LINE_1, D(100))

    with pytest.raises(AttributeError):
        line.base_amount = D(1)  # type: ignore[misc]


def test_the_outside_range_line_is_about_the_output_figure() -> None:
    assert BracketOutsideRangeLine(FIGURE, LINE_1, D(100)).label == FIGURE.label


def test_the_outside_range_line_amount_is_zero_as_for_other_blank_lines() -> None:
    assert BracketOutsideRangeLine(FIGURE, LINE_1, D(100)).amount == D(0)


def test_the_blank_reads_in_english() -> None:
    result = BracketColumnRate(LINE_1, FIGURE, dataset(UPPER)).run((Artifact(LINE_1, D(70)),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "Taxable base (70.00) is outside the range of the bracket table, so it is left blank.",
    )
