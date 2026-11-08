"""The 2026 Schedule 8 line 12 tier, checked against CRA's T4127 (Jan 2026).

CRA T4127 (122nd Edition, effective January 1, 2026), as taken into the dataset. The 2026 Schedule
8 (form 5000-S8) is not yet published, so the dataset is provisional. Table 8.5 prints the first
additional rate 1% and the maximum $711; Table 8.3 prints the YMCE $71,100.00, so the band runs
from 0 to 71,100 and the printed maximum is 1% of that band.
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
FAMILY = "ca/cpp_line_12_first_additional_contribution"

# Made up for this test and not registered: the earnings the tier reads, and its contribution.
EARNINGS = AmountKind("ex/earnings")
CONTRIBUTION = AmountKind("ex/contribution")


def test_2026_line_12_tier_is_1_percent_from_0_to_71100_at_most_711() -> None:
    data = SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.01")), D("0"), D("71100"), D("711.00"))
    # Schedule 8 Part 3 line 12 gives no rounding rule of its own; the tier rounds to the cent,
    # as the line 28 "(in dollars and cents)" box it feeds does.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_line_12_cites_t4127_jan_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    )


@pytest.mark.parametrize(
    ("earnings", "contribution"),
    [
        ("66500", "665.00"),
        ("71100", "711.00"),
        ("90000", "711.00"),
        ("0", "0"),
        # Rounded half-up to the cent: 1% of 0.10 is 0.001, of 0.50 is 0.005.
        ("0.10", "0.00"),
        ("0.50", "0.01"),
    ],
)
def test_contributes_on_line_12(earnings: str, contribution: str) -> None:
    # Earnings are line 7's, after the basic exemption: $70,000 - $3,500 = $66,500.
    capability = TieredContribution(
        SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)
