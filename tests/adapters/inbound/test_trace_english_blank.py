"""Unit tests for the English text of the blank trace lines, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.adapters.inbound.trace_english.blank as english_blank
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.trace import (
    BlankFallbackLine,
    BlankPassedOnLine,
    DefaultedInputLine,
    TraceLine,
)

CHART_GAIN = AmountKind("ex/chart_gain")
LIMIT = AmountKind("ex/limit")
DEDUCTION = AmountKind("ex/deduction")
HOUSEHOLD = CountKind("ex/household_count")


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_the_blank_renderer_module_registers_each_line() -> None:
    assert english_blank.__name__ == "tax_engine.adapters.inbound.trace_english.blank"
    registry = EnglishRendererRegistry.shared()

    for line_class in (BlankFallbackLine, BlankPassedOnLine, DefaultedInputLine):
        assert registry.for_line_class(line_class).line_class is line_class


def test_a_blank_taken_as_a_fallback() -> None:
    assert render(BlankFallbackLine(DEDUCTION, Decimal("0.00"))) == "Left blank, taken as 0.00."
    assert render(BlankFallbackLine(HOUSEHOLD, 0)) == "Left blank, taken as 0."


def test_a_blank_passed_on() -> None:
    assert (
        render(BlankPassedOnLine(DEDUCTION, (CHART_GAIN,))) == "Blank because chart gain was blank."
    )
    assert (
        render(BlankPassedOnLine(DEDUCTION, (CHART_GAIN, LIMIT)))
        == "Blank because chart gain and limit were blank."
    )


def test_a_blank_line_has_no_figure_but_the_fallback_and_the_default() -> None:
    assert BlankPassedOnLine(DEDUCTION, (CHART_GAIN,)).amount == 0
    assert BlankFallbackLine(DEDUCTION, Decimal("3")).amount == 3


def test_an_input_taken_as_its_default() -> None:
    assert (
        render(DefaultedInputLine(HOUSEHOLD, 12))
        == "No value given, so the form's default gives 12."
    )
    assert (
        render(DefaultedInputLine(LIMIT, Decimal("0.00")))
        == "No value given, so the form's default gives 0.00."
    )
