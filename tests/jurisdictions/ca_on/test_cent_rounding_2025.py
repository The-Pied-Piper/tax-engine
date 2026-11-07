"""The 2025 `ca-on/cent_rounding` dataset: the one rule shared by the Ontario floor steps
(`core/subtract_not_below_zero`), ON428 lines 4, 53, 61, 65, 71, 80, 81, 83, 86 and 88 and ON428-A
lines 17 and 20. It carries nothing but its rule, half-up to the cent, the rule of the
dollars-and-cents boxes. It cites the ON428 and ON428-A text."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/cent_rounding"


def test_2025_cent_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_cent_rounding_cites_the_on428_and_on428_a_text() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-a/5006-a-25e.txt",
    )
