"""The 2025 tier behind Schedule 8 Part 3 line 11, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 3 line 7: "Line 5 minus line 6 (if negative, enter "0")
(maximum $67,800)"; line 11: "amount from line 7 multiplied by 4.95% (maximum $3,356.10)". Line 7
already holds the earnings above the basic exemption, so this tier starts at 0 and ends at the
printed $67,800. Part 3a line 25 says "Enter this amount (in dollars and cents) on line 30800 of
your return", so the tier rounds half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.contribution_tier import TieredContribution
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/cpp_line_11_base_contribution"

# Made up for this test and not registered: the earnings the tier reads, and its contribution.
EARNINGS = AmountKind("ex/earnings")
CONTRIBUTION = AmountKind("ex/contribution")


def test_2025_line_11_tier_is_4_95_percent_from_0_to_67800_at_most_3356_10() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.0495")), D("0"), D("67800"), D("3356.10"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_11_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


def test_2025_line_11_tier_cites_the_schedule_8_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
    )


@pytest.mark.parametrize(
    ("earnings", "contribution"),
    [
        ("66500", "3291.75"),
        ("67800", "3356.10"),
        ("90000", "3356.10"),
        ("0", "0"),
        # Rounded half-up to the cent: 4.95% of 0.10 is 0.00495, of 0.30 is 0.01485.
        ("0.10", "0.00"),
        ("0.30", "0.01"),
    ],
)
def test_contributes_on_line_7(earnings: str, contribution: str) -> None:
    capability = TieredContribution(
        SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)
