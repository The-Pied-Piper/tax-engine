"""Unit tests for the English text of the blank trace lines, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.adapters.inbound.trace_english.blank as english_blank
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.trace import BlankFallbackLine, BlankPassedOnLine, LeftBlankLine, TraceLine

CHART_GAIN = ArtifactKind("ex/chart_gain", Decimal)
LIMIT = ArtifactKind("ex/limit", Decimal)
DEDUCTION = ArtifactKind("ex/deduction", Decimal)
HOUSEHOLD = ArtifactKind("ex/household_count", int)


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_the_blank_renderer_module_registers_each_line() -> None:
    assert english_blank.__name__ == "tax_engine.adapters.inbound.trace_english.blank"
    registry = EnglishRendererRegistry.shared()

    for line_class in (LeftBlankLine, BlankFallbackLine, BlankPassedOnLine):
        assert registry.for_line_class(line_class).line_class is line_class


def test_a_line_left_blank() -> None:
    assert render(LeftBlankLine(CHART_GAIN)) == "chart_gain: left blank"


def test_a_blank_taken_as_a_fallback() -> None:
    assert (
        render(BlankFallbackLine(DEDUCTION, Decimal("0.00"))) == "deduction: left blank, taken as 0"
    )
    assert render(BlankFallbackLine(HOUSEHOLD, 0)) == "household_count: left blank, taken as 0"


def test_a_blank_passed_on() -> None:
    assert (
        render(BlankPassedOnLine(DEDUCTION, (CHART_GAIN,)))
        == "deduction: blank because chart_gain was blank"
    )
    assert (
        render(BlankPassedOnLine(DEDUCTION, (CHART_GAIN, LIMIT)))
        == "deduction: blank because chart_gain, limit were blank"
    )


def test_a_blank_line_has_no_figure_but_the_fallback() -> None:
    assert LeftBlankLine(CHART_GAIN).amount == 0
    assert BlankPassedOnLine(DEDUCTION, (CHART_GAIN,)).amount == 0
    assert BlankFallbackLine(DEDUCTION, Decimal("3")).amount == 3
