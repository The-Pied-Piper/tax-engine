"""The 2026 `ca/marginal_federal_bpa_rows` dataset: as 2025 with the 2026 figures of T4127,
from $181,440 to $258,482."""

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
FAMILY = "ca/marginal_federal_bpa_rows"
YEAR = 2026


def _rate(base: str) -> Decimal:
    band = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.band_for(D(base))
    return band.rate.value if band.rate is not None else D("0")


def test_2026_marginal_federal_bpa_rows_is_the_amount_by_band_kind_and_rounds_nothing() -> None:
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
        ("181440", "0"),
        ("181440.01", "1"),
        ("258482", "1"),
        ("258482.01", "0"),
    ],
)
def test_2026_marginal_federal_bpa_rows_gives_the_band_rate(base: str, rate: str) -> None:
    assert _rate(base) == D(rate)
