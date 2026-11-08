"""The 2026 `ca-on/surtax_line_67` dataset: the one tier of ON428 line 67, taken from T4127
(Jan 2026) Table 8.2, row ON: 36% over $7,446, rounded half-up to the cent."""

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
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
FAMILY = "ca-on/surtax_line_67"


def test_2026_line_67_is_one_tier_at_36_percent_over_7446() -> None:
    data = SOURCE.get(FAMILY, 2026, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("7446"), Rate(D("0.36"))),))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_line_67_cites_only_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, SURCHARGE_TIERS)

    assert data.sources == (T4127,)
