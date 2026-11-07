"""Unit tests for the English text of the trace line of an amount by band, with made-up values.

An `AmountByBandLine` is rendered by the renderer in `trace_english.rate_tables`, registered for
its line class. The wording is not settled by the ticket, so these tests pin only what the line
must say: its output, the income it was given, the band's figures and the rounding rule, each as
`EnglishFigures` writes them.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.adapters.inbound.trace_english.rate_tables as english_rate_tables
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.trace import AmountByBandLine

D = Decimal
INCOME = AmountKind("ex/income")
PREMIUM = AmountKind("ex/premium")
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def render(line: AmountByBandLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_the_rate_tables_renderer_module_registers_the_line() -> None:
    assert english_rate_tables.__name__ == "tax_engine.adapters.inbound.trace_english.rate_tables"
    registry = EnglishRendererRegistry.shared()

    assert registry.for_line_class(AmountByBandLine).line_class is AmountByBandLine


def test_the_renderer_lives_in_the_rate_tables_module() -> None:
    found = EnglishRendererRegistry.shared().for_line_class(AmountByBandLine)

    assert type(found).__module__ == "tax_engine.adapters.inbound.trace_english.rate_tables"


def test_a_flat_band_line_reads_with_its_income_its_amount_and_its_result() -> None:
    line = AmountByBandLine(
        PREMIUM, INCOME, D("250"), D("200"), D("12"), None, None, None, NO_ROUNDING, D("12")
    )

    text = render(line)

    assert text
    assert EnglishFigures.money(D("250")) in text
    assert EnglishFigures.money(D("200")) in text
    assert EnglishFigures.money(D("12")) in text


def test_a_sloped_band_line_reads_with_its_rate_and_its_result() -> None:
    line = AmountByBandLine(
        PREMIUM,
        INCOME,
        D("150"),
        D("100"),
        None,
        D("100"),
        Rate(D("0.10")),
        D("0"),
        NO_ROUNDING,
        D("5"),
    )

    text = render(line)

    assert EnglishFigures.percent(D("0.10")) in text
    assert EnglishFigures.money(D("150")) in text
    assert EnglishFigures.money(D("100")) in text


def test_a_line_names_the_datasets_rounding_rule() -> None:
    line = AmountByBandLine(
        PREMIUM,
        INCOME,
        D("150.05"),
        D("100"),
        None,
        D("100"),
        Rate(D("0.10")),
        D("0"),
        CENT,
        D("5.01"),
    )

    assert EnglishFigures.rounding(CENT) in render(line)


def test_the_text_is_the_renderers_own_sentence_for_the_line() -> None:
    line = AmountByBandLine(
        PREMIUM, INCOME, D("250"), D("200"), D("12"), None, None, None, NO_ROUNDING, D("12")
    )

    assert EnglishTraceRenderer().render_all((line,)) == (render(line),)
