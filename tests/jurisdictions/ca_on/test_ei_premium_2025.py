"""The 2025 EI premium tier, checked against CRA's EI premium rates and maximums.

CRA, "EI premium rates and maximums", 2025 federal row: maximum annual insurable earnings
$65,700; rate 1.64%; maximum annual employee premium $1,077.48. T1-2025 line 88 (line 31200)
"through employment (boxes 18 and 55 of all T4 slips) (maximum $1,077.48)". So the band is the
earnings from 0 to the $65,700 maximum insurable earnings, with no exemption. Premiums are in
dollars and cents, and 1.64% of 65,700 is exactly the printed $1,077.48, so the tier rounds
half-up to the cent. Employment income is taken as the insurable earnings. Not triggered by the
returns modelled, so not modelled: insurable earnings (T4 boxes 18 and 55) that differ from
employment income, and the EI overpayment (T1 line 45000).
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
FAMILY = "ca/ei_premium"

# Made up for this test and not registered: the earnings the tier reads, and its premium.
EARNINGS = ArtifactKind("ex/earnings", Decimal)
PREMIUM = ArtifactKind("ex/premium", Decimal)


def test_2025_ei_tier_is_1_64_percent_from_0_to_65700_at_most_1077_48() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.0164")), D("0"), D("65700"), D("1077.48"))
    # Premiums are in dollars and cents.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_the_maximum_insurable_earnings_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    # No exemption: 65,700 x 1.64% is exactly line 31200's "(maximum $1,077.48)".
    assert tier.lower == D("0")
    assert tier.upper * tier.rate.value == tier.maximum


@pytest.mark.parametrize(
    "source",
    [
        "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/payroll-deductions-contributions/employment-insurance-ei/ei-premium-rates-maximums.html",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-r/5000-r-25e.txt",
    ],
)
def test_2025_ei_tier_cites_its_sources(source: str) -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert source in data.sources


@pytest.mark.parametrize(
    ("earnings", "premium"),
    [
        # Returns A and D: earnings above the $65,700 maximum insurable earnings, so the maximum.
        ("110000", "1077.48"),
        ("75000", "1077.48"),
        # Return C: 1.64% x 50,000 = 820.00.
        ("50000", "820.00"),
        # The low-income return: 1.64% x 10,000 = 164.00.
        ("10000", "164.00"),
        # At the maximum insurable earnings, and at zero.
        ("65700", "1077.48"),
        ("0", "0"),
        # Rounded half-up to the cent: 1.64% of 0.30 is 0.00492, down to 0.00; of 12.5 is 0.205,
        # a tie, up to 0.21.
        ("0.30", "0.00"),
        ("12.5", "0.21"),
    ],
)
def test_charges_premiums_on_employment_income(earnings: str, premium: str) -> None:
    capability = TieredContribution(SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, PREMIUM)

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(PREMIUM, D(premium)),)
