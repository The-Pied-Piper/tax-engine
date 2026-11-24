"""The 2026 `ca/federal_bpa_phase_down_fraction` dataset: Federal Worksheet (5000-D1) lines 2
and 8 over line 6, the supplement of the basic personal amount (1623) over its range
(77042), kept as an exact fraction and rounded once, half-up to seven places."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.fraction import FRACTION
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/federal_bpa_phase_down_fraction"
YEAR = 2026


def test_2026_federal_bpa_phase_down_fraction_is_the_supplement_over_the_range() -> None:
    data = SOURCE.get(FAMILY, YEAR, FRACTION)

    assert data.kind is FRACTION
    assert data.family == FAMILY
    assert data.tax_year == YEAR
    assert (data.values.numerator, data.values.denominator) == (1623, 77042)
    assert data.rounding == RoundTo(D("0.0000001"), RoundingMode.HALF_UP)
    assert data.rounding.apply(D("0.02106394")) == D("0.0210639")
    assert data.sources
