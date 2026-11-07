"""The 2025 `ca-on/bracket_column_tax_rounding` dataset: the rounding rule of ON428 line 6, a
dollars-and-cents box, with no values beyond its rule.

The rule is half-up to the cent, the owner's decision as the form states no rounding rule.
`ca-on/brackets` has no rounding rule (every line 7 figure is in whole cents). The dataset cites
only the ON428 text."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/bracket_column_tax_rounding"


def test_2025_bracket_column_tax_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_bracket_column_tax_rounding_cites_only_the_on428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt",
    )
