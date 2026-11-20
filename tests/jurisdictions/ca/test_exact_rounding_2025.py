"""The 2025 `ca/exact_rounding` dataset: the rule of a federal form line the engine only carries
through, for an unprinted working step (not a line the form prints), so nothing is rounded

(`rounding: none`); the cent rule of `ca/cent_rounding` must not touch them."""

from __future__ import annotations

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/exact_rounding"
YEAR = 2025


def test_the_exact_rounding_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == NO_ROUNDING
    assert data.tax_year == YEAR


def test_the_exact_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources
