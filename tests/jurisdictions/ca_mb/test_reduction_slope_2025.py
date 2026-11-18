"""The 2025 `ca-mb/reduction_slope` dataset: a two-band chart that is 0 where Worksheet MB428 line 8
is 0.00 and the printed 10.8% from one cent, read with no rounding.

Form text (Form MB428, CRA 5007-c-25e.txt): "Line 52: Manitoba non-refundable tax credits rate
10.8%". Worksheet MB428 (CRA 5007-d-25e.txt): "Line 8: Line 6 multiplied by line 7 = ^". The
return summary reads line 8 through this chart (`core/amount_by_band_rate`), so that the slope of
the basic personal amount's fall counts in the marginal tax rate only above a net income of
200,000.06 (where line 8, a dollars-and-cents box, is first above zero). The rate is the same
printed 10.8% as `ca-mb/credit_rate`, which rounds half-up to the cent (a rate of 0.108 would read
0.11), so the chart carries it with `rounding: none`. A base of 0.00 gives 0 and a base of 0.01 or
more gives 0.108; a base exactly at the second row's `over` (0.005) is in the lower band.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.core.capabilities.amount_by_band_rate import AmountByBandRate
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/reduction_slope"
YEAR = 2025

# Made up for this test and not registered: the amount read, and the slope.
AMOUNT = AmountKind("ex/amount")
SLOPE = AmountKind("ex/slope")


def _slope(base: str) -> Decimal:
    capability = AmountByBandRate(SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND), AMOUNT, SLOPE)

    (output,) = capability.compute((Artifact(AMOUNT, D(base)),)).outputs

    assert output.kind is SLOPE
    assert isinstance(output.value, Decimal)
    return output.value


def test_the_chart_is_the_amount_by_band_kind() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == YEAR


def test_the_chart_has_two_bands_the_first_from_0_and_the_second_above_half_a_cent() -> None:
    bands = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.bands

    assert len(bands) == 2
    assert bands[0].over == 0
    assert bands[0].amount == 0
    assert bands[1].over == D("0.005")
    assert bands[1].minus == 0
    assert bands[1].plus == 0
    assert bands[1].rate is not None
    assert bands[1].rate.value == D("0.108")


def test_the_chart_band_for_0_is_not_the_band_for_one_cent() -> None:
    values = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values

    assert values.band_for(D("0.00")) is values.bands[0]
    assert values.band_for(D("0.01")) is values.bands[1]


@pytest.mark.parametrize(
    ("base", "rate"),
    [
        ("0.00", "0"),
        ("0", "0"),
        ("0.005", "0"),
        ("0.01", "0.108"),
        ("0.02", "0.108"),
        ("1", "0.108"),
        ("3860.26", "0.108"),
        ("15779.99", "0.108"),
        ("15780.00", "0.108"),
        ("16484.26", "0.108"),
        ("1000000", "0.108"),
    ],
)
def test_the_slope_is_0_at_0_00_and_0_108_from_one_cent(base: str, rate: str) -> None:
    assert _slope(base) == D(rate)


def test_the_slope_times_the_printed_ratio_is_the_exact_0_0085212() -> None:
    assert D("15780") / D("200000") * _slope("0.01") == D("0.0085212")


def test_the_chart_rounds_nothing() -> None:
    assert SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).rounding == NO_ROUNDING


def test_the_chart_names_a_source() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.sources
