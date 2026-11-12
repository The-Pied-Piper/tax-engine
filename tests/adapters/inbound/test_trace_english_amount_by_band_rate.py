"""English text of the AmountByBandRateLine: where the base falls in the chart and the rate that
band gives, a flat band giving 0%. The position wording and the figures' formatting are those of
the AmountByBandLine sentence (`EnglishFigures.money` for the bound, `.percent` for the rate).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.trace import AmountByBandRateLine

D = Decimal
GROSS = AmountKind("ex/gross_pay")
SLOPE = AmountKind("ex/slope")


def render(line: object) -> str:
    return EnglishTraceRenderer().render(line, None)  # type: ignore[arg-type]


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
