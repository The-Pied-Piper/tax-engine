"""The 2025 tier behind Quebec Schedule 8 Part 2 line 11, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (Quebec edition 5005-S8), Part 2 line 7: "Line 5 minus line 6 (if negative,
enter "0") (maximum $67,800)"; line 11: "amount from line 7 multiplied by 5.4% (maximum $3,661.20)".
Line 7 already holds the earnings above the basic exemption, so this tier starts at 0 and ends
at the printed $67,800. Part 2a line 25 says "Enter this amount (in dollars and cents) on line
30800 of your return", so the tier rounds half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

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
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/qpp_line_11_base_contribution"

# Made up for this test and not registered: the earnings the tier reads, and its contribution.
EARNINGS = AmountKind("ex/earnings")
CONTRIBUTION = AmountKind("ex/contribution")


def test_2025_line_11_tier_is_5_4_percent_from_0_to_67800_at_most_3661_20() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.054")), D("0"), D("67800"), D("3661.20"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_11_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


def test_2025_line_11_tier_cites_the_quebec_schedule_8_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s8/5005-s8-25e.txt",
    )


@pytest.mark.parametrize(
    ("earnings", "contribution"),
    [
        ("16500", "891.00"),
        ("66500", "3591.00"),
        ("67800", "3661.20"),
        ("90000", "3661.20"),
        ("0", "0"),
        # Rounded half-up to the cent: 5.4% of 0.09 is 0.00486, of 0.10 is 0.0054, of 0.30 is
        # 0.0162.
        ("0.09", "0.00"),
        ("0.10", "0.01"),
        ("0.30", "0.02"),
    ],
)
def test_contributes_on_line_7(earnings: str, contribution: str) -> None:
    capability = TieredContribution(
        SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)
