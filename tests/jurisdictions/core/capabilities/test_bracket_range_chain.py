"""End to end on a tiny made-up worksheet: two bracket tables that each cover a range, the three
figure steps for each, then a subtract whose blanks are passed on.

The tables are "0 to 100" (`ex/low_*`) and "more than 100" (`ex/high_*`, with printed tax at
start). The base picks the table: the one that covers it gives its figures, and the other gives
blanks all the way down, so a later step can read whichever has a figure. A base exactly at 100 is
in the lower table only.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import BracketOutsideRangeLine
from tax_engine.domain.trace.blank import BlankPassedOnLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.core.capabilities.bracket_column_figure import (
    BracketColumnLowerBound,
    BracketColumnRate,
    BracketColumnTaxAtStart,
)
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import SubtractNotBelowZero

D = Decimal

LINE_1 = AmountKind("ex/line_1")

LOW_LOWER = AmountKind("ex/low_lower_bound")
LOW_RATE = AmountKind("ex/low_rate")
LOW_START = AmountKind("ex/low_tax_at_start")
LOW_EXCESS = AmountKind("ex/low_excess")
HIGH_LOWER = AmountKind("ex/high_lower_bound")
HIGH_RATE = AmountKind("ex/high_rate")
HIGH_START = AmountKind("ex/high_tax_at_start")
HIGH_EXCESS = AmountKind("ex/high_excess")

LOW = BracketSchedule((Bracket(D(0), D("0.10")), Bracket(D(50), D("0.20"))), up_to=D(100))
HIGH = BracketSchedule(
    (Bracket(D(100), D("0.30"), D("25.00")), Bracket(D(200), D("0.40"), D("55.00")))
)


def table(name: str, values: BracketSchedule) -> ParameterDataset[BracketSchedule]:
    return ParameterDataset(
        f"ex/{name}", 2025, BRACKETS, values, NO_ROUNDING, ("https://example.org/rates",)
    )


def subtract() -> ParameterDataset[RoundingOnly]:
    return ParameterDataset(
        "ex/excess_rounding", 2025, ROUNDING_ONLY, RoundingOnly(), NO_ROUNDING, ("https://x.org",)
    )


def chain(base: str) -> Worksheet:
    sheet = Worksheet(Artifact(LINE_1, D(base)))
    for name, values, lower, rate, start, excess in (
        ("low_brackets", LOW, LOW_LOWER, LOW_RATE, LOW_START, LOW_EXCESS),
        ("high_brackets", HIGH, HIGH_LOWER, HIGH_RATE, HIGH_START, HIGH_EXCESS),
    ):
        data = table(name, values)
        sheet.apply(BracketColumnLowerBound(LINE_1, lower, data))
        sheet.apply(BracketColumnRate(LINE_1, rate, data))
        sheet.apply(BracketColumnTaxAtStart(LINE_1, start, data))
        sheet.apply(
            SubtractNotBelowZero(subtract(), LINE_1, lower, excess).with_blank_rules(
                {"amount": PASS_ON, "less": PASS_ON}
            )
        )
    return sheet


def values(sheet: Worksheet, *kinds: AmountKind) -> tuple[object, ...]:
    return tuple(BLANK if sheet.get(kind).is_blank else sheet.get(kind).value for kind in kinds)


LOW_KINDS = (LOW_LOWER, LOW_RATE, LOW_START, LOW_EXCESS)
HIGH_KINDS = (HIGH_LOWER, HIGH_RATE, HIGH_START, HIGH_EXCESS)
ALL_BLANK = (BLANK, BLANK, BLANK, BLANK)


@pytest.mark.parametrize(
    ("base", "low", "high"),
    [
        ("0", (D(0), D("0.10"), D(0), D(0)), ALL_BLANK),
        ("30", (D(0), D("0.10"), D(0), D(30)), ALL_BLANK),
        ("100", (D(50), D("0.20"), D("5.0"), D(50)), ALL_BLANK),  # the boundary: lower table only
        ("100.01", ALL_BLANK, (D(100), D("0.30"), D("25.00"), D("0.01"))),
        ("150", ALL_BLANK, (D(100), D("0.30"), D("25.00"), D(50))),
        ("200", ALL_BLANK, (D(100), D("0.30"), D("25.00"), D(100))),
        ("250", ALL_BLANK, (D(200), D("0.40"), D("55.00"), D(50))),
    ],
)
def test_the_table_that_covers_the_base_gives_figures_and_the_other_gives_blanks(
    base: str, low: tuple[object, ...], high: tuple[object, ...]
) -> None:
    sheet = chain(base)

    assert values(sheet, *LOW_KINDS) == low
    assert values(sheet, *HIGH_KINDS) == high


def test_exactly_one_table_has_a_figure_for_any_base() -> None:
    for base in ("0", "99.99", "100", "100.01", "5000"):
        sheet = chain(base)

        assert (values(sheet, *LOW_KINDS) == ALL_BLANK) != (values(sheet, *HIGH_KINDS) == ALL_BLANK)


def test_the_blank_table_says_why_in_the_trace_and_the_subtract_passes_it_on() -> None:
    sheet = chain("100")

    assert [line for line in sheet.trace if isinstance(line, BracketOutsideRangeLine)] == [
        BracketOutsideRangeLine(HIGH_LOWER, LINE_1, D(100)),
        BracketOutsideRangeLine(HIGH_RATE, LINE_1, D(100)),
        BracketOutsideRangeLine(HIGH_START, LINE_1, D(100)),
    ]
    assert BlankPassedOnLine(HIGH_EXCESS, (HIGH_LOWER,)) in sheet.trace
    assert not [
        line
        for line in sheet.trace
        if isinstance(line, BlankPassedOnLine) and line.output == LOW_EXCESS
    ]
