"""The 2025 `ca-bc/exact_rounding` dataset: the rule of a British Columbia product or sum that is
not a dollars-and-cents box, so nothing is rounded (`rounding: none`). The British Columbia
marginal rate on the return summary (a gated bracket rate, and the sum of the federal and British
Columbia parts) uses it: a rate is an exact fraction, so the cent rule of `ca-bc/cent_rounding`
must not touch it."""

from __future__ import annotations

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/exact_rounding"
YEAR = 2025


def test_the_exact_rounding_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == NO_ROUNDING
    assert data.tax_year == YEAR


def test_the_exact_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources
