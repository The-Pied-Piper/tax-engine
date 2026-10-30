"""The 2025 age amount and spouse amounts' datasets, checked against CRA's Federal Worksheet and
Schedule 5.

Federal Worksheet (form 5000-D1), "Line 30100 - Age amount": line 1 "Maximum amount 9,028.00"; line
3 "Income threshold 45,522.00"; line 5 "Applicable rate 15%"; line 6 "Line 4 multiplied by the
percentage from line 5". So the maximum and the threshold are claimed amounts (the `credit` kind),
as the basic reduction is, and the 15% a rate (the `rate` kind) applied to line 4, the net income
over the threshold. The worksheet's "$45,522 or less, enter $9,028" and "$105,709 or more, enter
"0"" follow from the arithmetic and are not datasets.

Schedule 5 (form 5000-S5), "Line 30300 - Spouse or common-law partner amount": line 2 and line
51090 "If you are eligible for the Canada caregiver amount for your spouse or common-law partner,
enter $2,687". "Line 30425": line 1 "Base amount 28,798.00"; line 3 "Line 1 minus line 2 (if
negative, enter "0") (maximum $8,601)". So the $2,687 is a per-unit amount (the `amount` kind) read
once for a spouse eligible for the Canada caregiver amount, the base a claimed amount (the `credit`
kind) and the $8,601 a plain cap (the `amount` kind). Lines 1 to 7 of the Federal Worksheet and the
lines of Schedule 5's line 30300 and line 30425 are dollars-and-cents boxes, so each is rounded
half-up to the cent.

Each dataset is tested with the one capability that reads it, on made-up kinds; the lines together,
from net income and the spouse's net income to lines 30100, 30300 and 30425, are in
the `end_to_end` tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
AGE_MAXIMUM = "ca/age_maximum"
AGE_INCOME_THRESHOLD = "ca/age_income_threshold"
AGE_RATE = "ca/age_rate"
SPOUSE_INFIRMITY = "ca/spouse_infirmity_amount"
CAREGIVER_BASE = "ca/spouse_caregiver_base"
CAREGIVER_MAXIMUM = "ca/spouse_caregiver_maximum"
D1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"
S5_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s5/5000-s5-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the claimed amount a credit dataset gives, the net
# income over the threshold (Federal Worksheet line 4) and the reduction (line 6), the count of
# spouses eligible for the Canada caregiver amount and the supplement (Schedule 5 line 2), and the
# amount before its maximum and at most it (Schedule 5 line 30425, line 3).
CLAIMED = ArtifactKind("ex/claimed_amount", Decimal)
OVER_THRESHOLD = ArtifactKind("ex/over_threshold", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)
ELIGIBLE = ArtifactKind("ex/spouse_eligible", int)
SUPPLEMENT = ArtifactKind("ex/supplement", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/before_maximum", Decimal)
LIMIT = ArtifactKind("ex/limit", Decimal)


def test_2025_age_maximum_is_9028() -> None:
    data = SOURCE.get(AGE_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("9028.00"))
    # Federal Worksheet line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_age_income_threshold_is_45522() -> None:
    data = SOURCE.get(AGE_INCOME_THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("45522.00"))
    # Federal Worksheet line 3, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_age_rate_is_15_percent() -> None:
    data = SOURCE.get(AGE_RATE, 2025, RATE)

    assert data.values == Rate(D("0.15"))
    # Federal Worksheet line 6, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_amount_for_a_spouse_with_an_infirmity_is_2687() -> None:
    data = SOURCE.get(SPOUSE_INFIRMITY, 2025, AMOUNT)

    assert data.values == Amount(D("2687"))
    # Schedule 5 line 30300 line 2, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_caregiver_base_is_28798() -> None:
    data = SOURCE.get(CAREGIVER_BASE, 2025, CREDIT)

    assert data.values == Credit(amount=D("28798.00"))
    # Schedule 5 line 30425 line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_caregiver_maximum_is_8601() -> None:
    data = SOURCE.get(CAREGIVER_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("8601"))
    # Schedule 5 line 30425 line 3, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(AGE_MAXIMUM, 2025, CREDIT).sources == (D1_TEXT,)
    assert SOURCE.get(AGE_INCOME_THRESHOLD, 2025, CREDIT).sources == (D1_TEXT,)
    assert SOURCE.get(AGE_RATE, 2025, RATE).sources == (D1_TEXT,)
    assert SOURCE.get(SPOUSE_INFIRMITY, 2025, AMOUNT).sources == (S5_TEXT,)
    assert SOURCE.get(CAREGIVER_BASE, 2025, CREDIT).sources == (S5_TEXT,)
    assert SOURCE.get(CAREGIVER_MAXIMUM, 2025, AMOUNT).sources == (S5_TEXT,)


@pytest.mark.parametrize(
    ("family", "amount"),
    [
        (AGE_MAXIMUM, "9028.00"),
        (AGE_INCOME_THRESHOLD, "45522.00"),
        (CAREGIVER_BASE, "28798.00"),
    ],
)
def test_a_credit_dataset_is_claimed_whole(family: str, amount: str) -> None:
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), CLAIMED)

    result = capability.compute(())

    assert result.outputs == (Artifact(CLAIMED, D(amount)),)


@pytest.mark.parametrize(
    ("over_threshold", "reduction"),
    [
        # Net income at or below the threshold has nothing over it.
        ("0", "0"),
        # Return C's net income: (49535.00 - 45522) x 15% = 4013.00 x 15%.
        ("4013.00", "601.95"),
        # Net income of 50,000: 4478 x 15%.
        ("4478", "671.70"),
        # Return A: (115000 - 45522) x 15%, more than the 9028 maximum.
        ("69478", "10421.70"),
        # 0.10 x 15% = 0.015, a tie, rounded half-up to 0.02; 0.03 x 15% = 0.0045, down to 0.00.
        ("0.10", "0.02"),
        ("0.03", "0.00"),
    ],
)
def test_15_percent_of_the_net_income_over_the_threshold(
    over_threshold: str, reduction: str
) -> None:
    capability = ApplyRate(SOURCE.get(AGE_RATE, 2025, RATE), OVER_THRESHOLD, REDUCTION)

    result = capability.compute((Artifact(OVER_THRESHOLD, D(over_threshold)),))

    assert result.outputs == (Artifact(REDUCTION, D(reduction)),)


@pytest.mark.parametrize(("eligible", "supplement"), [(0, "0"), (1, "2687.00")])
def test_the_spouse_supplement_is_2687_once_for_a_spouse_eligible_for_the_caregiver_amount(
    eligible: int, supplement: str
) -> None:
    capability = PerUnitAmount(SOURCE.get(SPOUSE_INFIRMITY, 2025, AMOUNT), ELIGIBLE, SUPPLEMENT)

    result = capability.compute((Artifact(ELIGIBLE, eligible),))

    assert result.outputs == (Artifact(SUPPLEMENT, D(supplement)),)


@pytest.mark.parametrize(
    ("before_maximum", "limit"),
    [
        ("0", "0"),
        # Below the maximum: unchanged.
        ("3798.00", "3798.00"),
        ("8600.99", "8600.99"),
        # At and above the maximum: 8601.
        ("8601.00", "8601"),
        ("20175.00", "8601"),
        ("28798.00", "8601"),
    ],
)
def test_the_caregiver_amount_is_at_most_8601_before_the_amount_claimed_comes_off(
    before_maximum: str, limit: str
) -> None:
    capability = CappedAmount(SOURCE.get(CAREGIVER_MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, LIMIT)

    result = capability.compute((Artifact(BEFORE_MAXIMUM, D(before_maximum)),))

    assert result.outputs == (Artifact(LIMIT, D(limit)),)
