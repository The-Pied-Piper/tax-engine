"""The 2025 `ca-on/surtax_line_67` dataset: the one tier of ON428 line 67, (line 65 minus $7,307)
multiplied by 36%, rounded half-up to the cent."""

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
FAMILY = "ca-on/surtax_line_67"


def test_2025_line_67_is_one_tier_at_36_percent_over_7307() -> None:
    data = SOURCE.get(FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("7307"), Rate(D("0.36"))),))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
