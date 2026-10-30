"""The 2025 second additional CPP contribution tier, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 2, 12 months: line B "Your maximum pensionable earnings
for 2025 (maximum $71,300)"; line D "Your additional maximum pensionable earnings for 2025
(maximum $81,200)". Part 3: line 2 "Enter whichever is less: amount from line D of Part 2 or
line 1."; line 3 "Amount from line B of Part 2"; line 4 "Line 2 minus line 3 (if negative, enter
"0")"; line 22 "amount from line 4 multiplied by 4% (maximum $396.00)". So the band is the
earnings between the $71,300 and $81,200 ceilings. Part 3a line 27 is "Amount from line 22 (if
any)" and line 28 "Line 26 plus line 27 Enter this amount (in dollars and cents) on line 22215
of your return.", so the tier rounds half-up to the cent. Part 2's proration for fewer than 12
months is not triggered by the returns modelled.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.contribution_tier import TieredContribution
from tax_engine.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FAMILY = "ca/cpp_second_additional_contribution"

# Made up for this test and not registered: the earnings the tier reads, and its contribution.
EARNINGS = ArtifactKind("ex/earnings", Decimal)
CONTRIBUTION = ArtifactKind("ex/contribution", Decimal)


def test_2025_second_additional_tier_is_4_percent_from_71300_to_81200_at_most_396() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.04")), D("71300"), D("81200"), D("396.00"))
    # Schedule 8 Part 3a line 28: "(in dollars and cents)".
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    # 81,200 - 71,300 = 9,900, and 9,900 x 4% is line 22's $396.00.
    assert tier.upper - tier.lower == D("9900")
    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


@pytest.mark.parametrize(
    "source",
    [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
        "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/payroll-deductions-contributions/canada-pension-plan-cpp/cpp-contribution-rates-maximums-exemptions.html",
        "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/calculating-deductions/making-deductions/second-additional-cpp-contribution-rates-maximums.html",
    ],
)
def test_2025_second_additional_tier_cites_its_sources(source: str) -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert source in data.sources


@pytest.mark.parametrize(
    ("earnings", "contribution"),
    [
        # Return A: earnings above the $81,200 ceiling, so the maximum.
        ("110000", "396.00"),
        # Return D: 4% x (75,000 - 71,300) = 148.00.
        ("75000", "148.00"),
        # Return C: earnings below the $71,300 ceiling, so nothing.
        ("50000", "0"),
        # At each ceiling.
        ("71300", "0"),
        ("81200", "396.00"),
        ("0", "0"),
        # Rounded half-up to the cent: 4% of 0.12 is 0.0048, down to 0.00; of 0.125 is
        # 0.005, a tie, up to 0.01.
        ("71300.12", "0.00"),
        ("71300.125", "0.01"),
    ],
)
def test_contributes_on_employment_income(earnings: str, contribution: str) -> None:
    capability = TieredContribution(
        SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)
