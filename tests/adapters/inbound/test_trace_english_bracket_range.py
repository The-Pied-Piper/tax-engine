"""Unit tests for the English text of BracketOutsideRangeLine, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.domain.trace.rate_tables as rate_table_lines
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import BracketOutsideRangeLine

D = Decimal
INCOME = AmountKind("ex/taxable_base")
RATE_FIGURE = AmountKind("ex/column_rate")


def test_the_line_is_exported_from_the_rate_table_trace_module_and_the_package() -> None:
    assert "BracketOutsideRangeLine" in rate_table_lines.__all__
    assert rate_table_lines.BracketOutsideRangeLine is BracketOutsideRangeLine


def test_a_renderer_is_registered_for_the_line() -> None:
    renderer = EnglishRendererRegistry.shared().for_line_class(BracketOutsideRangeLine)

    assert renderer.line_class is BracketOutsideRangeLine


def test_a_base_outside_the_range_of_the_bracket_table_is_left_blank() -> None:
    line = BracketOutsideRangeLine(RATE_FIGURE, INCOME, D("70000"))

    assert EnglishTraceRenderer().render(line) == (
        "Taxable base (70000.00) is outside the range of the bracket table, so it is left blank."
    )


def test_the_base_amount_is_shown_to_the_cent() -> None:
    line = BracketOutsideRangeLine(RATE_FIGURE, INCOME, D("100.5"))

    assert EnglishTraceRenderer().render(line) == (
        "Taxable base (100.50) is outside the range of the bracket table, so it is left blank."
    )
