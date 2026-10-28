"""The 2025 Ontario LIFT credit rate, maximum and reduction, checked against CRA's ON428-A.

2025 Schedule ON428-A (form 5006-A): line 1 "Amount from line 10100 of your return"; line 2
"Amount from line 10400 of your return"; line 3 "Line 1 plus line 2"; line 4 "Applicable rate
5.05%"; line 5 "Line 3 multiplied by the percentage from line 4 (maximum $875)"; line 13 "Line 9
minus line 12 (if negative, enter "0") Your adjusted net income"; Part A, "If you were single at
the end of the year": line 14 "Amount from line 5 above (maximum $875)"; line 15 "Amount from line
13 above"; line 16 "Individual income threshold 32,500.00"; line 17 "Line 15 minus line 16 (if
negative, enter "0")"; line 18 "Applicable rate 5%"; line 19 "Line 17 multiplied by the percentage
from line 18"; line 20 "Line 14 minus line 19 (if negative, enter "0") Enter this amount on line
62140 of your Form ON428." The 5.05% is a rate (the `rate` kind), the $875 a plain cap (the
`amount` kind), and lines 16 to 19 one tier over the threshold (the `surcharge_tiers` kind). Lines
5, 14 and 19 are dollars-and-cents boxes, so each is rounded half-up to the cent.

Part B, "If you had a spouse or common-law partner at the end of the year": line 31 "Individual
income threshold 32,500.00"; line 36 "Family income threshold 65,0000.00", a typo for 65,000.00;
line 39 "Applicable rate 5%"; line 40 "Line 38 multiplied by the percentage from line 39". Each
threshold is a printed amount taken whole (the `credit` kind) and the rate a rate (the `rate`
kind). Lines 31, 36 and 40 are dollars-and-cents boxes, so each is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.capped_amount import CappedAmount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
RATE_FAMILY = "ca-on/lift_rate"
MAXIMUM = "ca-on/lift_maximum"
REDUCTION_FAMILY = "ca-on/lift_reduction"
INDIVIDUAL_THRESHOLD = "ca-on/lift_individual_income_threshold"
FAMILY_THRESHOLD = "ca-on/lift_family_income_threshold"
FAMILY_RATE = "ca-on/lift_family_rate"
ON428_A_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-a/5006-a-25e.txt"

# Made up for this test and not registered: the employment income the rate is applied to (line
# 3), the credit before its maximum and after it (lines 5 and 14), the net income the reduction
# is on (line 15) and the reduction (line 19).
INCOME = ArtifactKind("ex/income", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/before_maximum", Decimal)
CAPPED = ArtifactKind("ex/capped", Decimal)
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)
# Part B: the threshold a credit dataset gives (lines 31 and 36), the larger excess over a
# threshold (line 38) and the reduction from it (line 40).
THRESHOLD = ArtifactKind("ex/threshold", Decimal)
GREATER_EXCESS = ArtifactKind("ex/greater_excess", Decimal)
FAMILY_REDUCTION = ArtifactKind("ex/family_reduction", Decimal)


def test_2025_rate_is_5_05_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.0505"))
    # ON428-A line 5, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_875() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("875"))
    # ON428-A lines 5 and 14, dollars-and-cents boxes: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_reduction_is_5_percent_over_32500() -> None:
    data = SOURCE.get(REDUCTION_FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("32500"), Rate(D("0.05"))),))
    # ON428-A line 19, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_datasets_cite_only_the_on428_a_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (ON428_A_TEXT,)
    assert SOURCE.get(MAXIMUM, 2025, AMOUNT).sources == (ON428_A_TEXT,)
    assert SOURCE.get(REDUCTION_FAMILY, 2025, SURCHARGE_TIERS).sources == (ON428_A_TEXT,)


@pytest.mark.parametrize(
    ("income", "credit"),
    [
        # Return B: 30000 x 5.05%, already in cents.
        ("30000", "1515.00"),
        # Return C, and the low-income return of the worked-return tests.
        ("50000", "2525.00"),
        ("10000", "505.00"),
        # Return A.
        ("110000", "5555.00"),
        # 1234.57 x 5.05% = 62.345785, rounded half-up to 62.35.
        ("1234.57", "62.35"),
        ("0", "0"),
    ],
)
def test_5_05_percent_of_employment_income(income: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), INCOME, BEFORE_MAXIMUM)

    result = capability.compute((Artifact(INCOME, D(income)),))

    assert result.outputs == (Artifact(BEFORE_MAXIMUM, D(credit)),)


@pytest.mark.parametrize(
    ("credit", "capped"),
    [
        # Return B: 1515.00 is above the maximum.
        ("1515.00", "875"),
        # At the maximum, and a cent above it.
        ("875", "875"),
        ("875.01", "875"),
        # Below it, the credit itself, as for the low-income return's 505.00.
        ("505.00", "505.00"),
        ("0", "0"),
    ],
)
def test_at_most_875(credit: str, capped: str) -> None:
    capability = CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, CAPPED)

    result = capability.compute((Artifact(BEFORE_MAXIMUM, D(credit)),))

    assert result.outputs == (Artifact(CAPPED, D(capped)),)


@pytest.mark.parametrize(
    ("net_income", "reduction"),
    [
        # Return B: net income of 29735.00 is below the threshold, so line 17 is 0.
        ("29735.00", "0"),
        # Return C: (49535.00 - 32500) x 5% = 17035.00 x 5%.
        ("49535.00", "851.75"),
        # Return A: (115000 - 32500) x 5%, above the 875 maximum, so its credit is 0.
        ("115000", "4125.00"),
        # At the threshold nothing is over it; a cent above, 5% of the cent is 0.0005, rounded
        # half-up to 0.00; 5% of 0.10 is 0.005, a tie, up to 0.01.
        ("32500", "0"),
        ("32500.01", "0.00"),
        ("32500.10", "0.01"),
        ("0", "0"),
    ],
)
def test_5_percent_of_net_income_over_32500(net_income: str, reduction: str) -> None:
    capability = TieredSurcharge(
        SOURCE.get(REDUCTION_FAMILY, 2025, SURCHARGE_TIERS), NET_INCOME, REDUCTION
    )

    result = capability.compute((Artifact(NET_INCOME, D(net_income)),))

    assert result.outputs == (Artifact(REDUCTION, D(reduction)),)


def test_2025_individual_income_threshold_is_32500() -> None:
    data = SOURCE.get(INDIVIDUAL_THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("32500.00"))
    # ON428-A line 31, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_family_income_threshold_is_65000() -> None:
    data = SOURCE.get(FAMILY_THRESHOLD, 2025, CREDIT)

    # The form's text prints "65,0000.00", a typo; the threshold is 65,000.00.
    assert data.values == Credit(amount=D("65000.00"))
    # ON428-A line 36, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_family_rate_is_5_percent() -> None:
    data = SOURCE.get(FAMILY_RATE, 2025, RATE)

    assert data.values == Rate(D("0.05"))
    # ON428-A line 40, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_part_b_datasets_cite_only_the_on428_a_text() -> None:
    assert SOURCE.get(INDIVIDUAL_THRESHOLD, 2025, CREDIT).sources == (ON428_A_TEXT,)
    assert SOURCE.get(FAMILY_THRESHOLD, 2025, CREDIT).sources == (ON428_A_TEXT,)
    assert SOURCE.get(FAMILY_RATE, 2025, RATE).sources == (ON428_A_TEXT,)


@pytest.mark.parametrize(
    ("family", "amount"),
    [
        (INDIVIDUAL_THRESHOLD, "32500.00"),
        (FAMILY_THRESHOLD, "65000.00"),
    ],
)
def test_a_threshold_dataset_is_claimed_whole(family: str, amount: str) -> None:
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), THRESHOLD)

    result = capability.compute(())

    assert result.outputs == (Artifact(THRESHOLD, D(amount)),)


@pytest.mark.parametrize(
    ("excess", "reduction"),
    [
        # The ticket example: family income 75000 less 65000, 10000 x 5%.
        ("10000", "500.00"),
        ("0", "0"),
        # 0.10 x 5% = 0.005, a tie, rounded half-up to 0.01; 0.09 x 5% = 0.0045, down to 0.00.
        ("0.10", "0.01"),
        ("0.09", "0.00"),
    ],
)
def test_5_percent_of_the_greater_excess(excess: str, reduction: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY_RATE, 2025, RATE), GREATER_EXCESS, FAMILY_REDUCTION)

    result = capability.compute((Artifact(GREATER_EXCESS, D(excess)),))

    assert result.outputs == (Artifact(FAMILY_REDUCTION, D(reduction)),)
