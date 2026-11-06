"""The 2025 Schedule 8 line 12 tier, checked against CRA's Schedule 8 (form 5000-S8).

T1-2025 Schedule 8 (form 5000-S8), Part 3, line 12: "amount from line 7 multiplied by 1%
(maximum $678.00)". Line 7 is "Line 5 minus line 6 (if negative, enter "0") (maximum $67,800)",
so the band runs from 0 to $67,800 of line 7 earnings, and the printed maximum is 1% of that band.
The dataset holds the printed figures as they are printed. The ca_on manifest tests pin what
line 12 produces from them.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/cpp_line_12_first_additional_contribution"


def test_2025_line_12_tier_is_1_percent_from_0_to_67800_at_most_678() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.01")), D("0"), D("67800"), D("678.00"))
    # Schedule 8 Part 3 line 12 gives no rounding rule of its own; the tier rounds to the cent,
    # as the line 28 "(in dollars and cents)" box it feeds does.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_12_cites_the_schedule_8_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
    )
