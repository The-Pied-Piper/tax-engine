"""The 2026 `ca/marginal_ei_rate_rows` dataset: as 2025 with the 2026 figures of T4127: 0 up to
$2,000, then 1 for 1 up to $2,033, then the 1.63% premium rate, up to the maximum $68,900."""

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
YEAR = 2026


def _rate(base: str) -> Decimal:
    band = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.band_for(D(base))
    return band.rate.value if band.rate is not None else D("0")


def test_2026_marginal_ei_rate_rows_is_the_amount_by_band_kind_and_rounds_nothing() -> None:
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
        ("2033.01", "1"),
        ("2033.15", "0.0163"),
        ("68900", "0.0163"),
        ("68900.01", "0"),
    ],
)
def test_2026_marginal_ei_rate_rows_gives_the_band_rate(base: str, rate: str) -> None:
    assert _rate(base) == D(rate)
