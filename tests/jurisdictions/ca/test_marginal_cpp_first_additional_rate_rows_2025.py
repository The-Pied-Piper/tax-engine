"""The 2025 `ca/marginal_cpp_first_additional_rate_rows` dataset: the rate per extra dollar of
the CPP band a base falls in, through `core/amount_by_band_rate`. Schedule 8 (form 5000-S8)
Part 3 line 12 "multiplied by 1%", from the basic exemption (Part 2 line E, $3,500) up to
the maximum pensionable earnings (line B, $71,300): no rate up to $3,500, 1% to $71,300,
none above. Source: 5000-S8 (2025 forms)."""

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
FAMILY = "ca/marginal_cpp_first_additional_rate_rows"
YEAR = 2025


def _rate(base: str) -> Decimal:
    band = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.band_for(D(base))
    return band.rate.value if band.rate is not None else D("0")


def test_2025_marginal_cpp_first_additional_rate_rows_is_the_amount_by_band_kind() -> None:
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
        ("3500", "0"),
        ("50000", "0.01"),
        ("3500.01", "0.01"),
        ("71300", "0.01"),
        ("71300.01", "0"),
    ],
)
def test_2025_first_additional_rate_rows_gives_the_band_rate(base: str, rate: str) -> None:
    assert _rate(base) == D(rate)
