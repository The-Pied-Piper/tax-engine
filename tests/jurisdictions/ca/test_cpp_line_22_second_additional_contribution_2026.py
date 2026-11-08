"""The 2026 rate and maximum of Schedule 8 Part 3 line 22, checked against CRA's T4127 (Jan 2026).

CRA T4127 (122nd Edition, effective January 1, 2026), as taken into the dataset. The 2026 Schedule
8 (form 5000-S8) is not yet published, so the dataset is provisional. Table 8.6 prints the second
additional rate 4%, the earnings subject to it $10,400.00 and the maximum $416; the band runs from
0 to 10,400, rounded half-up to the cent as in 2025.
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
FAMILY = "ca/cpp_line_22_second_additional_contribution"

# Made up for this test and not registered: the earnings the tier reads, and its contribution.
EARNINGS = AmountKind("ex/earnings")
CONTRIBUTION = AmountKind("ex/contribution")


def test_2026_line_22_is_4_percent_of_line_4_to_10400_at_most_416() -> None:
    data = SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.04")), D("0"), D("10400"), D("416.00"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER).values

    # 10,400 x 4% is the printed $416.
    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


def test_2026_line_22_cites_t4127_jan_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    )


@pytest.mark.parametrize(
    ("earnings", "contribution"),
    [
        ("10400", "416.00"),
        ("20000", "416.00"),
        ("5000", "200.00"),
        ("0", "0"),
        # Rounded half-up to the cent: 4% of 0.10 is 0.004, of 0.125 is 0.005.
        ("0.10", "0.00"),
        ("0.125", "0.01"),
    ],
)
def test_contributes_on_line_22(earnings: str, contribution: str) -> None:
    # Earnings are line 4's, the earnings between the two ceilings.
    capability = TieredContribution(
        SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)
