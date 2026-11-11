"""Unit tests for the English text of the choice trace lines, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.trace import (
    ChosenByCountLine,
    ChosenByRangeLine,
    ChosenBySignLine,
    TraceLine,
)

D = Decimal
OUT = AmountKind("ex/result")
CREDIT = AmountKind("ex/credit")
INCOME = AmountKind("ex/income")
BALANCE = AmountKind("ex/balance")
CHILDREN = CountKind("ex/children")


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_a_candidate_chosen_by_a_count() -> None:
    assert render(ChosenByCountLine(OUT, CHILDREN, 0, CREDIT, D("500"))) == (
        "credit (500.00), chosen because children (0)."
    )
    assert render(ChosenByCountLine(OUT, CHILDREN, 2, CREDIT, D("750.5"))) == (
        "credit (750.50), chosen because children (2)."
    )


def test_a_candidate_chosen_by_the_sign_of_an_amount() -> None:
    assert render(ChosenBySignLine(OUT, BALANCE, D("4"), CREDIT, D("10"))) == (
        "credit (10.00), chosen because balance (4.00) is positive."
    )
    assert render(ChosenBySignLine(OUT, BALANCE, D("-4"), CREDIT, D("10"))) == (
        "credit (10.00), chosen because balance (-4.00) is negative."
    )
    assert render(ChosenBySignLine(OUT, BALANCE, D("0"), CREDIT, D("10"))) == (
        "credit (10.00), chosen because balance (0.00) is zero."
    )


def test_a_sign_with_no_candidate_gives_no_amount() -> None:
    assert render(ChosenBySignLine(OUT, BALANCE, D("-4"), None, D("0"))) == (
        "0, no amount when balance (-4.00) is negative."
    )
    assert render(ChosenBySignLine(OUT, BALANCE, D("0"), None, D("0"))) == (
        "0, no amount when balance (0.00) is zero."
    )


def test_a_candidate_chosen_by_the_range_of_an_amount() -> None:
    assert render(ChosenByRangeLine(OUT, INCOME, D("52000"), CREDIT, D("300"))) == (
        "credit (300.00), chosen because income (52000.00) fits its range."
    )
