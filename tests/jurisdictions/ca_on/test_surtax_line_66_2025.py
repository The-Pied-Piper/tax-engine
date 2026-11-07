"""The 2025 `ca-on/surtax_line_66` dataset: the one tier of ON428 line 66, (line 65 minus $5,710)
multiplied by 20%, rounded half-up to the cent."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/surtax_line_66"


def test_2025_line_66_is_one_tier_at_20_percent_over_5710() -> None:
    data = SOURCE.get(FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("5710"), Rate(D("0.20"))),))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_66_cites_only_the_on428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, SURCHARGE_TIERS)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt",
    )
