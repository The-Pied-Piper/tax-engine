"""Unit tests for the English text of BracketColumnFigureLine, made-up values.

It reads "bracket <name> for <base>: <figure>", figures as plain numbers without trailing zeros;
the rate figure is a percentage with a "%" sign.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.adapters.inbound.trace_english.rate_tables as english_rate_tables
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.trace import BracketColumnFigureLine

D = Decimal


def render(line: BracketColumnFigureLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_the_rate_tables_renderer_module_registers_the_line() -> None:
    assert english_rate_tables.__name__ == "tax_engine.adapters.inbound.trace_english.rate_tables"
    registry = EnglishRendererRegistry.shared()

    assert registry.for_line_class(BracketColumnFigureLine).line_class is BracketColumnFigureLine


def test_a_lower_bound_reads_as_a_plain_figure() -> None:
    line = BracketColumnFigureLine(
        base_amount=D("69335.00"), name="lower bound", figure=D("52886.00")
    )

    assert render(line) == "bracket lower bound for 69335: 52886"


def test_a_zero_lower_bound_reads_as_0() -> None:
    line = BracketColumnFigureLine(base_amount=D("19835.00"), name="lower bound", figure=D("0.00"))

    assert render(line) == "bracket lower bound for 19835: 0"


def test_a_rate_reads_as_a_percentage() -> None:
    line = BracketColumnFigureLine(base_amount=D("69335.00"), name="rate", figure=D("0.0915"))

    assert render(line) == "bracket rate for 69335: 9.15%"


def test_a_tax_at_start_reads_as_a_plain_figure() -> None:
    line = BracketColumnFigureLine(base_amount=D("250"), name="tax at start", figure=D("10.50"))

    assert render(line) == "bracket tax at start for 250: 10.5"
