"""The 2025 `ca/marginal_ei_rate_rows` dataset: the rate per extra dollar of the EI band a base
falls in, through `core/amount_by_band_rate`. Form T2204 line 16 "Enter whichever amount is
the least: line 7, line 9 or line 12": 0 up to the $2,000 of line 7, then 1 for 1 (line 7)
up to the $2,033 of note (3), then line 10's 1.64%, up to the maximum $65,700 of line 3."""

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
FAMILY = "ca/marginal_ei_rate_rows"
YEAR = 2025


def _rate(base: str) -> Decimal:
    band = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.band_for(D(base))
    return band.rate.value if band.rate is not None else D("0")


def test_2025_marginal_ei_rate_rows_is_the_amount_by_band_kind_and_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == YEAR
    assert data.rounding == NO_ROUNDING
    assert data.sources
    assert len(data.values.bands) == 4


@pytest.mark.parametrize(
    ("base", "rate"),
    [
        ("2000", "0"),
        ("2000.01", "1"),
        ("2033", "1"),
        ("2033.01", "1"),
        ("2033.35", "0.0164"),
        ("65700", "0.0164"),
        ("65700.01", "0"),
    ],
)
def test_2025_marginal_ei_rate_rows_gives_the_band_rate(base: str, rate: str) -> None:
    assert _rate(base) == D(rate)
