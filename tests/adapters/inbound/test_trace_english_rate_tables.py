"""Unit tests for the English text of the rate table trace lines, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind, RateKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rate_table import RateTableRow
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.trace import (
    AmountByBandRateLine,
    BracketColumnLine,
    ChosenRateAppliedLine,
    RateByIncomeBandLine,
    TraceLine,
)

D = Decimal
OUT = AmountKind("ex/tax")
INCOME = AmountKind("ex/income")
RATE_OUT = RateKind("ex/rate_for_income")
CHOSEN_RATE = RateKind("ex/chosen_rate")
GROSS = AmountKind("ex/gross_pay")
SLOPE = AmountKind("ex/slope")
CENT = RoundTo(increment=D("0.01"), mode=RoundingMode.HALF_UP)


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_a_bracket_column() -> None:
    line = BracketColumnLine(
        lower=D("10000"), rate=D("0.2"), excess=D("5000"), tax_at_start=D("1000"), tax=D("2000")
    )

    assert render(line) == "20% of the 5000.00 over 10000.00, plus 1000.00, gives 2000.00."


def test_a_bracket_column_with_a_fractional_rate() -> None:
    line = BracketColumnLine(
        lower=D("0"), rate=D("0.125"), excess=D("800"), tax_at_start=D("0"), tax=D("100")
    )

    assert render(line) == "12.5% of the 800.00 over 0.00, plus 0.00, gives 100.00."


def test_a_rate_by_income_band_with_an_upper_bound() -> None:
    row = RateTableRow(D("1000"), D("5000"), Rate(D("0.1")))

    line = RateByIncomeBandLine(RATE_OUT, INCOME, D("2500"), row, Rate(D("0.1")))

    assert render(line) == (
        "Income (2500.00) is more than 1000.00 but not more than 5000.00, so the rate is 10%."
    )


def test_a_rate_by_income_band_without_an_upper_bound() -> None:
    row = RateTableRow(D("5000"), None, Rate(D("0.25")))

    line = RateByIncomeBandLine(RATE_OUT, INCOME, D("9000"), row, Rate(D("0.25")))

    assert render(line) == "Income (9000.00) is more than 5000.00, so the rate is 25%."


def test_a_chosen_rate_applied() -> None:
    unrounded = ChosenRateAppliedLine(
        OUT, INCOME, D("1000"), CHOSEN_RATE, Rate(D("0.1")), NO_ROUNDING, D("100")
    )
    rounded = ChosenRateAppliedLine(
        OUT, INCOME, D("1000"), CHOSEN_RATE, Rate(D("0.125")), CENT, D("125")
    )

    assert render(unrounded) == "Chosen rate (10%) of income (1000.00) gives 100.00 (not rounded)."
    assert render(rounded) == (
        "Chosen rate (12.5%) of income (1000.00) gives 125.00 (rounded to the nearest cent)."
    )


def test_a_sloped_band_above_its_start_gives_its_rate() -> None:
    line = AmountByBandRateLine(SLOPE, GROSS, D("72300.00"), D("72000"), Rate(D("0.25")), D("0.25"))

    assert render(line) == "Gross pay (72300.00) is over 72000.00, so the rate is 25%."


def test_a_flat_band_gives_a_rate_of_zero() -> None:
    line = AmountByBandRateLine(SLOPE, GROSS, D("69335.00"), D("48600"), None, D("0"))

    assert render(line) == (
        "Gross pay (69335.00) is over 48600.00, so the band is a flat amount and the rate is 0%."
    )


def test_a_base_at_the_start_of_the_band_is_in_the_band_starting_there() -> None:
    line = AmountByBandRateLine(SLOPE, GROSS, D("72000.00"), D("72000"), Rate(D("0.25")), D("0.25"))
    flat = AmountByBandRateLine(SLOPE, GROSS, D("0"), D("0"), None, D("0"))

    assert render(line) == (
        "Gross pay (72000.00) is in the band starting at 72000.00, so the rate is 25%."
    )
    assert render(flat) == (
        "Gross pay (0.00) is in the band starting at 0.00, "
        "so the band is a flat amount and the rate is 0%."
    )


def test_a_rate_prints_as_a_percentage_the_way_other_rates_do() -> None:
    line = AmountByBandRateLine(SLOPE, GROSS, D("21000"), D("20000"), Rate(D("0.06")), D("0.06"))

    assert render(line) == "Gross pay (21000.00) is over 20000.00, so the rate is 6%."
