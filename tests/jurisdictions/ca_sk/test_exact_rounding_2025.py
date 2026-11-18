"""The 2025 `ca-sk/exact_rounding` dataset: the rule of a Saskatchewan product or sum that is
not a dollars-and-cents box, so nothing is rounded (`rounding: none`). The Saskatchewan
marginal rate on the return summary (a gated bracket rate, and the sum of the federal and
Saskatchewan parts) uses it: a rate is an exact fraction, so the cent rule of `ca-sk/cent_rounding`
must not touch it."""

from __future__ import annotations

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
)

SOURCE = YamlParameterSource(saskatchewan_packages().roots(), saskatchewan_parameter_parsers())
FAMILY = "ca-sk/exact_rounding"
YEAR = 2025


def test_the_exact_rounding_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == NO_ROUNDING
    assert data.tax_year == YEAR


def test_the_exact_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources
