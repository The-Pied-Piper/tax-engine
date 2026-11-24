"""The 2025 `ca-on/marginal_lift_reduction_rows` dataset: ON428-A line 19 (line 17 times line
18 "Applicable rate 5%") over the credit's $875 maximum (lines 5 and 14): the reduction rate
while the reduction is above 0.00 and not over the $875 credit."""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.parameters.rounding import NO_ROUNDING

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/marginal_lift_reduction_rows"
YEAR = 2025


def _rate(base: str) -> Decimal:
    band = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.band_for(D(base))
    return band.rate.value if band.rate is not None else D("0")


def test_2025_marginal_lift_reduction_rows_is_the_amount_by_band_kind_and_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == YEAR
    assert data.rounding == NO_ROUNDING
    assert data.sources
    assert len(data.values.bands) == 3


@pytest.mark.parametrize(
    ("base", "rate"),
    [
        ("0.00", "0"),
        ("0.01", "0.05"),
        ("875", "0.05"),
        ("875.01", "0"),
    ],
)
def test_2025_marginal_lift_reduction_rows_gives_the_band_rate(base: str, rate: str) -> None:
    assert _rate(base) == D(rate)
