"""The 2025 `ca-on/exact_rounding` dataset: the rule of an Ontario product that is not a
dollars-and-cents box, so nothing is rounded. It carries nothing but its rule, `rounding: none`.
The Ontario marginal rate on the return summary (the ON428 line 5 rate times the surtax factor of
lines 66 and 67) uses it: a rate is an exact fraction, so the cent rule of `ca-on/cent_rounding`
must not touch it."""

from __future__ import annotations

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/exact_rounding"


def test_2025_exact_rounding_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == NO_ROUNDING


def test_2025_exact_rounding_is_not_the_cent_rule() -> None:
    exact = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)
    cent = SOURCE.get("ca-on/cent_rounding", 2025, ROUNDING_ONLY)

    assert exact.rounding != cent.rounding


def test_2025_exact_rounding_names_a_source() -> None:
    # The source is to be confirmed: a rule of no rounding has no printed rounding text to quote.
    assert SOURCE.get(FAMILY, 2025, ROUNDING_ONLY).sources
