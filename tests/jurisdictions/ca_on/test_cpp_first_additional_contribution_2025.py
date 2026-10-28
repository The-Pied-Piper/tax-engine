"""The 2025 first additional CPP contribution tier, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 2, 12 months: line B "Your maximum pensionable earnings
for 2025 (maximum $71,300)"; line E "Your maximum basic exemption for 2025 (maximum $3,500)".
Part 3: line 7 "Line 5 minus line 6 (if negative, enter "0") (maximum $67,800)"; line 12
"amount from line 7 multiplied by 1% (maximum $678.00)". So the band is the base contributions'
band, the earnings between the $3,500 exemption and the $71,300 ceiling. Line 18 is "Amount from
line 12" and Part 3a line 26 "Amount from line 18"; line 28 "Line 26 plus line 27 Enter this
amount (in dollars and cents) on line 22215 of your return.", so the tier rounds half-up to the
cent. Part 2's proration for fewer than 12 months is not triggered by the returns modelled.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.contribution_tier import TieredContribution
from tax_calculator.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
FAMILY = "ca/cpp_first_additional_contribution"

# Made up for this test and not registered: the earnings the tier reads, and its contribution.
EARNINGS = ArtifactKind("ex/earnings", Decimal)
CONTRIBUTION = ArtifactKind("ex/contribution", Decimal)


def test_2025_first_additional_tier_is_1_percent_from_3500_to_71300_at_most_678() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.01")), D("3500"), D("71300"), D("678.00"))
    # Schedule 8 Part 3a line 28: "(in dollars and cents)".
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    # Line 7's "(maximum $67,800)" x 1% is line 12's $678.00.
    assert tier.upper - tier.lower == D("67800")
    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


@pytest.mark.parametrize(
    "source",
    [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
        "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/payroll-deductions-contributions/canada-pension-plan-cpp/cpp-contribution-rates-maximums-exemptions.html",
        "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/calculating-deductions/making-deductions/second-additional-cpp-contribution-rates-maximums.html",
    ],
)
def test_2025_first_additional_tier_cites_its_sources(source: str) -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert source in data.sources


@pytest.mark.parametrize(
    ("earnings", "contribution"),
    [
        # Returns A and D: earnings above the $71,300 ceiling, so the maximum.
        ("110000", "678.00"),
        ("75000", "678.00"),
        # Return C: 1% x (50,000 - 3,500) = 465.00.
        ("50000", "465.00"),
        # At the ceiling, and at and below the exemption.
        ("71300", "678.00"),
        ("3500", "0"),
        ("0", "0"),
        # Rounded half-up to the cent: 1% of 0.49 is 0.0049, down to 0.00; of 0.50 is
        # 0.005, a tie, up to 0.01.
        ("3500.49", "0.00"),
        ("3500.50", "0.01"),
    ],
)
def test_contributes_on_employment_income(earnings: str, contribution: str) -> None:
    capability = TieredContribution(
        SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)
