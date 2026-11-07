"""The 2025 `ca-on/tax_reduction_multiplier` dataset: the one fraction of ON428 line 78, line 77
multiplied by 2 (numerator 2, denominator 1), with no rounding."""

from __future__ import annotations

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rounding import NO_ROUNDING

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/tax_reduction_multiplier"


def test_2025_tax_reduction_multiplier_is_2_over_1() -> None:
    data = SOURCE.get(FAMILY, 2025, FRACTION)

    assert data.values == Fraction(numerator=2, denominator=1)
    assert data.rounding == NO_ROUNDING


def test_2025_tax_reduction_multiplier_cites_only_the_on428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, FRACTION)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt",
    )
