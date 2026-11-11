"""Unit tests for the three bracket column figure capabilities, with made-up brackets.

Each takes a base and a brackets dataset, finds the column the base falls in (a base exactly at a
threshold falls in the lower column, as the form's "more than ... but not more than" reads) and
produces one printed figure of that column, unrounded: BracketColumnLowerBound its lower bound,
BracketColumnRate its rate, BracketColumnTaxAtStart its tax at the start (which the schedule
already rounds by its own rule). The three share the undecorated base class BracketColumnFigure.
Slots: parameter `schedule`, consumed `base`, produced `output`. The trace is one
BracketColumnFigureLine: the output and base kinds, the base amount, the figure's name as text
and the figure.
"""

from __future__ import annotations

from dataclasses import fields
from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import Capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.trace import BracketColumnFigureLine
from tax_engine.jurisdictions.core.capabilities.bracket_column_figure import (
    BracketColumnFigure,
    BracketColumnLowerBound,
    BracketColumnRate,
    BracketColumnTaxAtStart,
)

D = Decimal

TAXABLE_BASE = AmountKind("ex/taxable_base")
FIGURE = AmountKind("ex/column_figure")

SCHEDULE = BracketSchedule(
    (
        Bracket(D(0), D("0.10")),
        Bracket(D(100), D("0.20")),
        Bracket(D(300), D("0.30")),
    )
)
# 10.5% of 105 is 11.025, rounded half-up to the cent at the column's start: 11.03.
ROUNDED = BracketSchedule(
    (
        Bracket(D(0), D("0.105")),
        Bracket(D(105), D("0.205")),
        Bracket(D(210), D("0.30")),
    ),
    RoundTo(D("0.01"), RoundingMode.HALF_UP),
)

CAPABILITIES = (BracketColumnLowerBound, BracketColumnRate, BracketColumnTaxAtStart)


def schedule(values: BracketSchedule = SCHEDULE) -> ParameterDataset[BracketSchedule]:
    return ParameterDataset(
        "ex/brackets", 2025, BRACKETS, values, NO_ROUNDING, ("https://example.org/rates",)
    )


def figure(
    cls: type[BracketColumnFigure], base: str, values: BracketSchedule = SCHEDULE
) -> Decimal:
    result = cls(TAXABLE_BASE, FIGURE, schedule(values)).compute((Artifact(TAXABLE_BASE, D(base)),))
    (output,) = result.outputs
    assert output.kind == FIGURE
    assert isinstance(output.value, Decimal)
    return output.value


def lower(base: str, values: BracketSchedule = SCHEDULE) -> Decimal:
    return figure(BracketColumnLowerBound, base, values)


def rate(base: str, values: BracketSchedule = SCHEDULE) -> Decimal:
    return figure(BracketColumnRate, base, values)


def tax_at_start(base: str, values: BracketSchedule = SCHEDULE) -> Decimal:
    return figure(BracketColumnTaxAtStart, base, values)


# --- the contract ------------------------------------------------------------------------------


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_declares_its_contract(cls: type[BracketColumnFigure]) -> None:
    wired = cls(TAXABLE_BASE, FIGURE, schedule())

    assert wired.consumes == frozenset({TAXABLE_BASE})
    assert wired.produces == frozenset({FIGURE})


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_declares_its_slots(cls: type[BracketColumnFigure]) -> None:
    assert cls.PARAMETERS == {"schedule": BRACKETS}
    assert cls.PARAMETERS["schedule"] is BRACKETS
    assert cls.CONSUMES == {"base": Decimal}
    assert cls.PRODUCES == {"output": Decimal}


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_is_built_from_its_slot_names_as_keywords(cls: type[BracketColumnFigure]) -> None:
    wired = cls(base=TAXABLE_BASE, output=FIGURE, schedule=schedule())

    assert wired.compute((Artifact(TAXABLE_BASE, D(250)),)).outputs[0].kind == FIGURE


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_rejects_one_kind_as_both_base_and_output(cls: type[BracketColumnFigure]) -> None:
    with pytest.raises(InvalidCapabilityError, match=cls.__name__) as raised:
        cls(TAXABLE_BASE, TAXABLE_BASE, schedule())

    assert "'base'" in str(raised.value)
    assert "'output'" in str(raised.value)


def test_the_shared_base_is_not_a_registered_capability() -> None:
    assert issubclass(BracketColumnFigure, Capability)
    assert BracketColumnFigure.identifier() is None
    assert [cls.identifier() for cls in CAPABILITIES] == [
        "core/bracket_column_lower_bound",
        "core/bracket_column_rate",
        "core/bracket_column_tax_at_start",
    ]


@pytest.mark.parametrize("cls", CAPABILITIES)
def test_the_three_share_one_base_class(cls: type[BracketColumnFigure]) -> None:
    assert issubclass(cls, BracketColumnFigure)


# --- the figures -------------------------------------------------------------------------------


def test_the_lower_bound_is_the_start_of_the_column_the_base_falls_in() -> None:
    assert lower("50") == D(0)
    assert lower("250") == D(100)
    assert lower("400") == D(300)


def test_the_rate_is_the_rate_of_the_column_the_base_falls_in() -> None:
    assert rate("50") == D("0.10")
    assert rate("250") == D("0.20")
    assert rate("400") == D("0.30")


def test_the_tax_at_start_is_the_schedules_tax_at_the_columns_start() -> None:
    assert tax_at_start("50") == D(0)
    assert tax_at_start("250") == D("10.00")
    assert tax_at_start("400") == D("50.00")


def test_the_tax_at_start_is_the_schedules_rounded_figure_not_the_exact_one() -> None:
    assert tax_at_start("150", ROUNDED) == D("11.03")


def test_a_base_at_a_threshold_falls_in_the_lower_column() -> None:
    assert lower("100") == D(0)
    assert rate("100") == D("0.10")
    assert tax_at_start("100") == D(0)
    assert lower("300") == D(100)
    assert rate("300") == D("0.20")
    assert tax_at_start("300") == D("10.00")


def test_a_base_just_over_a_threshold_falls_in_the_upper_column() -> None:
    assert lower("100.01") == D(100)
    assert rate("100.01") == D("0.20")
    assert tax_at_start("105.01", ROUNDED) == D("11.03")


def test_a_zero_base_falls_in_the_first_column() -> None:
    assert lower("0") == D(0)
    assert rate("0") == D("0.10")
    assert tax_at_start("0") == D(0)


def test_a_base_in_the_open_top_column() -> None:
    assert lower("1000000") == D(300)
    assert rate("1000000") == D("0.30")
    assert tax_at_start("1000000") == D("50.00")


def test_the_figure_is_not_rounded_by_the_capability() -> None:
    cent = BracketSchedule((Bracket(D(0), D("0.0505")),))

    assert rate("10", cent) == D("0.0505")
    assert lower("10.005") == D(0)


def test_rejects_negative_base() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        lower("-1")


# --- trace -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("cls", "name", "expected"),
    [
        (BracketColumnLowerBound, "lower bound", D(100)),
        (BracketColumnRate, "rate", D("0.20")),
        (BracketColumnTaxAtStart, "tax at start", D("10.00")),
    ],
)
def test_traces_one_line_with_the_base_the_figures_name_and_the_figure(
    cls: type[BracketColumnFigure], name: str, expected: Decimal
) -> None:
    result = cls(TAXABLE_BASE, FIGURE, schedule()).compute((Artifact(TAXABLE_BASE, D(250)),))

    assert result.trace == (
        BracketColumnFigureLine(
            output=FIGURE,
            base=TAXABLE_BASE,
            base_amount=D(250),
            name=name,
            figure=expected,
        ),
    )


def test_the_trace_line_amount_is_the_figure() -> None:
    line = BracketColumnFigureLine(
        output=FIGURE, base=TAXABLE_BASE, base_amount=D(250), name="lower bound", figure=D(100)
    )

    assert line.amount == D(100)


def test_the_trace_line_has_these_fields_in_order() -> None:
    assert [f.name for f in fields(BracketColumnFigureLine)] == [
        "output",
        "base",
        "base_amount",
        "name",
        "figure",
    ]


def test_the_trace_line_is_frozen() -> None:
    line = BracketColumnFigureLine(
        output=FIGURE, base=TAXABLE_BASE, base_amount=D(250), name="rate", figure=D("0.2")
    )

    with pytest.raises(AttributeError):
        line.figure = D(1)  # type: ignore[misc]


# --- English text ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("cls", "text"),
    [
        (BracketColumnLowerBound, "Bracket lower bound for taxable_base (250): 100."),
        (BracketColumnRate, "Bracket rate for taxable_base (250): 20%."),
        (
            BracketColumnTaxAtStart,
            "Bracket tax at start for taxable_base (250): 10.00.",
        ),
    ],
)
def test_the_trace_reads_in_english(cls: type[BracketColumnFigure], text: str) -> None:
    result = cls(TAXABLE_BASE, FIGURE, schedule()).compute((Artifact(TAXABLE_BASE, D(250)),))

    assert EnglishTraceRenderer().render_all(result.trace) == (text,)
