"""Unit tests for the English text of `MultipliedByRateLine`, with made-up kinds and values.

The sentence reads "<output>: <rate kind> <rate as a percentage>% of <base kind> <base> = <result>
(<rounding>)", the rate shown as a percentage though it is held as a fraction (0.0915 reads
"9.15%"). The renderer is registered in `tax_engine.adapters.inbound.trace_english.arithmetic`.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.adapters.inbound.trace_english.arithmetic as english_arithmetic
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.trace import MultipliedByRateLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

EXCESS_TAX = AmountKind("ex/excess_tax")
EXCESS_INCOME = AmountKind("ex/excess_income")
COLUMN_RATE = AmountKind("ex/column_rate")


def render(line: MultipliedByRateLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_the_multiplied_by_rate_renderer_module_registers_the_line() -> None:
    assert english_arithmetic.__name__ == "tax_engine.adapters.inbound.trace_english.arithmetic"
    registry = EnglishRendererRegistry.shared()

    assert registry.for_line_class(MultipliedByRateLine).line_class is MultipliedByRateLine


def test_reads_the_rate_as_a_percentage_of_the_base_and_the_result_with_the_rule() -> None:
    line = MultipliedByRateLine(
        EXCESS_TAX,
        EXCESS_INCOME,
        D("16449.00"),
        COLUMN_RATE,
        D("0.0915"),
        CENT,
        D("1505.08"),
    )

    assert render(line) == (
        "excess_tax: column_rate 9.15% of excess_income 16449 = 1505.08 (half-up to 0.01)"
    )


def test_reads_a_rate_of_five_hundredths_as_5_05_percent() -> None:
    line = MultipliedByRateLine(
        EXCESS_TAX,
        EXCESS_INCOME,
        D("19835.00"),
        COLUMN_RATE,
        D("0.0505"),
        CENT,
        D("1001.67"),
    )

    assert render(line) == (
        "excess_tax: column_rate 5.05% of excess_income 19835 = 1001.67 (half-up to 0.01)"
    )


def test_reads_an_unrounded_result_with_no_rounding() -> None:
    line = MultipliedByRateLine(
        EXCESS_TAX,
        EXCESS_INCOME,
        D("19835.00"),
        COLUMN_RATE,
        D("0.0505"),
        NO_ROUNDING,
        D("1001.6675"),
    )

    assert render(line) == (
        "excess_tax: column_rate 5.05% of excess_income 19835 = 1001.6675 (no rounding)"
    )


def test_reads_a_whole_base_without_trailing_zeros() -> None:
    line = MultipliedByRateLine(
        EXCESS_TAX,
        EXCESS_INCOME,
        D("43151.00"),
        COLUMN_RATE,
        D("0.1116"),
        CENT,
        D("4815.65"),
    )

    assert render(line) == (
        "excess_tax: column_rate 11.16% of excess_income 43151 = 4815.65 (half-up to 0.01)"
    )
