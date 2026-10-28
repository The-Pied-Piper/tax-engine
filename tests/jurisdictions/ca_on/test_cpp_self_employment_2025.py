"""The 2025 CPP contributions on self-employment income, checked against CRA's Schedule 8 Part 4.

T1-2025 Schedule 8 (form 5000-S8), Part 4 - "Contributions on self-employment income and other
earnings only (no employment income)": line 9 "Line 7 minus line 8 (if negative, enter "0")
(maximum $67,800)", the earnings subject to base and first additional contributions; line 10
"amount from line 9 multiplied by 9.9% (maximum $6,712.20)"; line 11 "amount from line 9
multiplied by 2% (maximum $1,356.00)"; line 6 "Line 4 minus line 5 (if negative, enter "0")", the
earnings subject to second additional contributions; line 12 "amount from line 6 multiplied by
8% (maximum $792.00)"; line 15 "amount from line 10 multiplied by 50%". The earnings of lines 9 and
6 are already net of the basic exemption and the ceilings (Part 4 lines 3 to 9), so each tier
starts at 0: its upper bound is the printed maximum of its earnings line ($67,800 and $9,900,
the 12-month row of Part 2 less the exemption, and line C), and its maximum is that band at the
rate. A self-employed person pays both halves, so the rates are twice the employee's 4.95%, 1%
and 4% (CRA, "CPP contribution rates, maximums and exemptions" and "Second additional CPP
contribution rates and maximums", 2025 rows). Lines 14, 15 and 17 are "in dollars and cents"
(lines 14 and 17 "Enter this amount (in dollars and cents)", line 15 the amount "(in dollars and
cents)" for line 31000), and lines 10 to 12 feed them, so each rounds half-up to the cent. Part 5
(employment income and self-employment income together) is not modelled.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.contribution_tier import TieredContribution
from tax_calculator.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASE = "ca/cpp_self_employed_base_contribution"
FIRST_ADDITIONAL = "ca/cpp_self_employed_first_additional_contribution"
SECOND_ADDITIONAL = "ca/cpp_self_employed_second_additional_contribution"
BASE_CREDIT_RATE = "ca/cpp_self_employed_base_credit_rate"
S8_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"
RATES_PAGE = (
    "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/"
    "payroll-deductions-contributions/canada-pension-plan-cpp/"
    "cpp-contribution-rates-maximums-exemptions.html"
)
SECOND_ADDITIONAL_PAGE = (
    "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/"
    "calculating-deductions/making-deductions/"
    "second-additional-cpp-contribution-rates-maximums.html"
)
HALF_UP_TO_THE_CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the earnings a tier reads, and its contribution.
EARNINGS = ArtifactKind("ex/earnings", Decimal)
CONTRIBUTION = ArtifactKind("ex/contribution", Decimal)


def test_2025_base_tier_is_9_9_percent_of_up_to_67800_at_most_6712_20() -> None:
    data = SOURCE.get(BASE, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.099")), D("0"), D("67800"), D("6712.20"))
    # Schedule 8 Part 4 line 10, and line 14 "(in dollars and cents)".
    assert data.rounding == HALF_UP_TO_THE_CENT


def test_2025_first_additional_tier_is_2_percent_of_up_to_67800_at_most_1356() -> None:
    data = SOURCE.get(FIRST_ADDITIONAL, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.02")), D("0"), D("67800"), D("1356.00"))
    assert data.rounding == HALF_UP_TO_THE_CENT


def test_2025_second_additional_tier_is_8_percent_of_up_to_9900_at_most_792() -> None:
    data = SOURCE.get(SECOND_ADDITIONAL, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.08")), D("0"), D("9900"), D("792.00"))
    assert data.rounding == HALF_UP_TO_THE_CENT


@pytest.mark.parametrize("family", [BASE, FIRST_ADDITIONAL, SECOND_ADDITIONAL])
def test_2025_maximum_is_the_full_band_at_the_rate(family: str) -> None:
    tier = SOURCE.get(family, 2025, CONTRIBUTION_TIER).values

    # Line 10: 67,800 x 9.9% = 6,712.20; line 11: 67,800 x 2% = 1,356.00; line 12: 9,900 x 8% =
    # 792.00.
    assert tier.lower == D("0")
    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


@pytest.mark.parametrize(
    ("self_employed", "employee"),
    [
        (BASE, "ca/cpp_base_contribution"),
        (FIRST_ADDITIONAL, "ca/cpp_first_additional_contribution"),
        (SECOND_ADDITIONAL, "ca/cpp_second_additional_contribution"),
    ],
)
def test_the_rate_is_twice_the_employees_for_the_same_band(
    self_employed: str, employee: str
) -> None:
    # Employee: 4.95%, 1% and 4%, on bands 3,500 to 71,300 and 71,300 to 81,200; self-employed
    # on the same bands net of the exemption and the ceiling (67,800 and 9,900 wide).
    mine = SOURCE.get(self_employed, 2025, CONTRIBUTION_TIER).values
    theirs = SOURCE.get(employee, 2025, CONTRIBUTION_TIER).values

    assert mine.rate.value == theirs.rate.value * 2
    assert mine.upper - mine.lower == theirs.upper - theirs.lower
    assert mine.maximum == theirs.maximum * 2


def test_2025_base_credit_rate_is_50_percent() -> None:
    data = SOURCE.get(BASE_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    # Schedule 8 Part 4 line 15 "(in dollars and cents)": it is entered on line 31000.
    assert data.rounding == HALF_UP_TO_THE_CENT


@pytest.mark.parametrize(
    ("family", "source"),
    [
        (BASE, S8_TEXT),
        (BASE, RATES_PAGE),
        (FIRST_ADDITIONAL, S8_TEXT),
        (FIRST_ADDITIONAL, RATES_PAGE),
        (SECOND_ADDITIONAL, S8_TEXT),
        (SECOND_ADDITIONAL, SECOND_ADDITIONAL_PAGE),
    ],
)
def test_2025_tiers_cite_their_sources(family: str, source: str) -> None:
    data = SOURCE.get(family, 2025, CONTRIBUTION_TIER)

    assert source in data.sources


def test_2025_base_credit_rate_cites_schedule_8() -> None:
    assert S8_TEXT in SOURCE.get(BASE_CREDIT_RATE, 2025, RATE).sources


@pytest.mark.parametrize(
    ("family", "earnings", "contribution"),
    [
        # Return U: line 9 is 50,000 - 3,500 = 46,500; line 6 is 0.
        (BASE, "46500", "4603.50"),
        (FIRST_ADDITIONAL, "46500", "930.00"),
        (SECOND_ADDITIONAL, "0", "0"),
        # At each upper bound, the printed maximums.
        (BASE, "67800", "6712.20"),
        (FIRST_ADDITIONAL, "67800", "1356.00"),
        (SECOND_ADDITIONAL, "9900", "792.00"),
        # Above them: capped at the maximum, never more.
        (BASE, "90000", "6712.20"),
        (FIRST_ADDITIONAL, "90000", "1356.00"),
        (SECOND_ADDITIONAL, "12000", "792.00"),
        # Half-up to the cent: 9.9% of 0.05 is 0.00495, down to 0.00; of 0.06 is 0.00594, up
        # to 0.01; 2% of 0.25 is 0.005, a tie, up to 0.01; 8% of 0.0625 is 0.005, a tie, up
        # to 0.01.
        (BASE, "0.05", "0.00"),
        (BASE, "0.06", "0.01"),
        (FIRST_ADDITIONAL, "0.25", "0.01"),
        (SECOND_ADDITIONAL, "0.0625", "0.01"),
    ],
)
def test_contributes_on_the_earnings_of_its_line(
    family: str, earnings: str, contribution: str
) -> None:
    capability = TieredContribution(
        SOURCE.get(family, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)


@pytest.mark.parametrize(
    ("base_contributions", "credit"),
    [
        # Return U: line 15 is 4,603.50 x 50% = 2,301.75.
        ("4603.50", "2301.75"),
        # The maximum: 6,712.20 x 50% = 3,356.10, the employee's maximum on line 31000 too.
        ("6712.20", "3356.10"),
        ("0", "0.00"),
        # Half-up to the cent: 0.01 x 50% is 0.005, a tie, up to 0.01; 0.03 x 50% is 0.015, up
        # to 0.02.
        ("0.01", "0.01"),
        ("0.03", "0.02"),
    ],
)
def test_the_base_credit_is_half_of_the_base_contributions(
    base_contributions: str, credit: str
) -> None:
    capability = ApplyRate(SOURCE.get(BASE_CREDIT_RATE, 2025, RATE), EARNINGS, CONTRIBUTION)

    result = capability.compute((Artifact(EARNINGS, D(base_contributions)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(credit)),)
