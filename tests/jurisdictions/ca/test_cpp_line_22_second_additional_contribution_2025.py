"""The 2025 rate and maximum of Schedule 8 Part 3 line 22, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 3 line 22: "amount from line 4 multiplied by 4%
(maximum $396.00)". Line 4 is already the earnings between the $71,300 and $81,200 ceilings, so
the band the dataset reads runs from 0 to the printed 9,900 maximum of line 4. Line 22 is printed
in dollars and cents, so it rounds half-up to the cent. The ca_on manifest tests pin what line 22
produces from these figures.
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
FAMILY = "ca/cpp_line_22_second_additional_contribution"


def test_2025_line_22_is_4_percent_of_line_4_to_9900_at_most_396() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.04")), D("0"), D("9900"), D("396.00"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    # 9,900 x 4% is line 22's printed $396.00.
    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


def test_2025_line_22_cites_the_schedule_8_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
    )
