"""The 2025 EI premiums on self-employment income, checked against CRA's Schedule 13.

T1-2025 Schedule 13 (form 5000-S13), "Employment Insurance Premiums on Self-Employment and Other
Eligible Earnings": line 5 "Maximum insurable earnings 65,700.00"; line 6 and line 54780 "Total EI
insurable earnings (amount from box 24 of all your T4 slips ...)"; line 7 "Line 5 minus line 6 (if
negative, enter "0")"; line 8 "Enter whichever is less: amount from line 4 or line 7."; "Residents
of a province or territory other than Quebec: Line 9: Amount from line 8 multiplied by 1.64%
(maximum $1,077.48)"; "Enter the amount from line 9 or line 10, whichever applies, on line 31217
and line 42120 of your return." CRA, "EI premium rates and maximums", 2025 federal row: maximum
annual insurable earnings $65,700; rate 1.64%; maximum annual employee premium $1,077.48. The
$65,700 is a plain credit amount (the `credit` kind, line 5), not rated on its own; line 8 is
already net of the insurable earnings on T4 slips (line 6), so the premium tier runs from 0 to
$65,700 and its maximum is that band at the rate. Line 9 is not marked "in dollars and cents"
but the premiums are entered on lines 31217 and 42120, both dollars-and-cents boxes, so the tier
rounds half-up to the cent. Not modelled: line 10 (Quebec residents, 1.31% to $860.67), and the
exemption when the T4 EI premiums are $1,077.48 or more (the dollar test before line 5).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.contribution_tier import TieredContribution
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
PREMIUM = "ca/ei_self_employed_premium"
MAXIMUM = "ca/ei_maximum_insurable_earnings"
S13_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s13/5000-s13-25e.txt"
RATES_PAGE = (
    "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/"
    "payroll-deductions-contributions/employment-insurance-ei/ei-premium-rates-maximums.html"
)
HALF_UP_TO_THE_CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the earnings the tier reads, and its premium.
EARNINGS = ArtifactKind("ex/earnings", Decimal)
AMOUNT = ArtifactKind("ex/amount", Decimal)


def test_2025_tier_is_1_64_percent_of_up_to_65700_at_most_1077_48() -> None:
    data = SOURCE.get(PREMIUM, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.0164")), D("0"), D("65700"), D("1077.48"))
    assert data.rounding == HALF_UP_TO_THE_CENT


def test_2025_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(PREMIUM, 2025, CONTRIBUTION_TIER).values

    # 65,700 x 1.64% is line 9's $1,077.48.
    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


def test_the_self_employed_tier_is_the_employment_tier() -> None:
    # The same rate, ceiling and maximum as T1 line 31200's, which reads the employment income.
    mine = SOURCE.get(PREMIUM, 2025, CONTRIBUTION_TIER).values
    employment = SOURCE.get("ca/ei_premium", 2025, CONTRIBUTION_TIER).values

    assert mine == employment


def test_2025_maximum_insurable_earnings_is_65700() -> None:
    data = SOURCE.get(MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(D("65700.00"))
    # Schedule 13 line 5 "Maximum insurable earnings 65,700.00".
    assert data.rounding == HALF_UP_TO_THE_CENT


def test_2025_maximum_insurable_earnings_is_the_top_of_the_tier() -> None:
    assert (
        SOURCE.get(MAXIMUM, 2025, CREDIT).values.amount
        == SOURCE.get(PREMIUM, 2025, CONTRIBUTION_TIER).values.upper
    )


@pytest.mark.parametrize("source", [S13_TEXT, RATES_PAGE])
def test_2025_tier_cites_its_sources(source: str) -> None:
    data = SOURCE.get(PREMIUM, 2025, CONTRIBUTION_TIER)

    assert source in data.sources


@pytest.mark.parametrize("source", [S13_TEXT, RATES_PAGE])
def test_2025_maximum_insurable_earnings_cites_its_sources(source: str) -> None:
    data = SOURCE.get(MAXIMUM, 2025, CREDIT)

    assert source in data.sources


@pytest.mark.parametrize(
    ("earnings", "premium"),
    [
        # Return U: line 8 is the lesser of 50,000 and 65,700, 50,000; 50,000 x 1.64% = 820.00.
        ("50000", "820.00"),
        # At the maximum insurable earnings, and above it: the maximum premium.
        ("65700", "1077.48"),
        ("90000", "1077.48"),
        ("0", "0"),
        # Half-up to the cent: 1.64% of 0.30 is 0.00492, down to 0.00; of 12.5 is 0.205, a tie,
        # up to 0.21.
        ("0.30", "0.00"),
        ("12.5", "0.21"),
    ],
)
def test_charges_premiums_on_the_earnings_of_line_8(earnings: str, premium: str) -> None:
    capability = TieredContribution(SOURCE.get(PREMIUM, 2025, CONTRIBUTION_TIER), EARNINGS, AMOUNT)

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(AMOUNT, D(premium)),)


def test_the_maximum_insurable_earnings_is_read_as_a_credit_amount() -> None:
    capability = CreditAmount(SOURCE.get(MAXIMUM, 2025, CREDIT), AMOUNT)

    result = capability.compute(())

    assert result.outputs == (Artifact(AMOUNT, D("65700.00")),)
