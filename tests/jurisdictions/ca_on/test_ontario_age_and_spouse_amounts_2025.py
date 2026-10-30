"""The 2025 Ontario age amount and spouse amount's datasets, checked against CRA's ON428 forms.

Worksheet ON428 (form 5006-D), "Line 58080 - Age amount": line 1 "Maximum amount 6,223.00"; line 3
"Income threshold 46,330.00"; line 5 "Applicable rate 15%"; line 6 "Line 4 multiplied by the
percentage from line 5". So the maximum and the threshold are claimed amounts (the `credit` kind),
as the basic reduction is, and the 15% a rate (the `rate` kind) applied to line 4, the net income
over the threshold. The worksheet's "$46,330 or less, enter $6,223" and "$87,817 or more, enter
"0"" follow from the arithmetic and are not datasets.

Form ON428 (form 5006-C): line 11 "Base amount 11,905.00"; line 13 (line 58120) "Line 11 minus line
12 (if negative, enter "0") (maximum $10,823)". So the base is a claimed amount (the `credit`
kind) and the maximum a plain cap (the `amount` kind). Lines 1 to 7 of the worksheet and lines 11
and 13 of the form are dollars-and-cents boxes, so each is rounded half-up to the cent.

Each dataset is tested with the one capability that reads it, on made-up kinds; the lines together,
from net income and the spouse's net income to lines 58080 and 58120, are in
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
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
AGE_MAXIMUM = "ca-on/age_maximum"
AGE_INCOME_THRESHOLD = "ca-on/age_income_threshold"
AGE_RATE = "ca-on/age_rate"
SPOUSE_BASE = "ca-on/spouse_base"
SPOUSE_MAXIMUM = "ca-on/spouse_maximum"
D_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the claimed amount a credit dataset gives, the net
# income over the threshold (Worksheet ON428 line 4) and the reduction (line 6), and the spouse
# amount before its maximum and at most it (ON428 line 13).
CLAIMED = ArtifactKind("ex/claimed_amount", Decimal)
OVER_THRESHOLD = ArtifactKind("ex/over_threshold", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/before_maximum", Decimal)
LIMIT = ArtifactKind("ex/limit", Decimal)


def test_2025_ontario_age_maximum_is_6223() -> None:
    data = SOURCE.get(AGE_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("6223.00"))
    # Worksheet ON428 line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ontario_age_income_threshold_is_46330() -> None:
    data = SOURCE.get(AGE_INCOME_THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("46330.00"))
    # Worksheet ON428 line 3, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ontario_age_rate_is_15_percent() -> None:
    data = SOURCE.get(AGE_RATE, 2025, RATE)

    assert data.values == Rate(D("0.15"))
    # Worksheet ON428 line 6, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ontario_spouse_base_is_11905() -> None:
    data = SOURCE.get(SPOUSE_BASE, 2025, CREDIT)

    assert data.values == Credit(amount=D("11905.00"))
    # ON428 line 11, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ontario_spouse_maximum_is_10823() -> None:
    data = SOURCE.get(SPOUSE_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("10823"))
    # ON428 line 13, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(AGE_MAXIMUM, 2025, CREDIT).sources == (D_TEXT,)
    assert SOURCE.get(AGE_INCOME_THRESHOLD, 2025, CREDIT).sources == (D_TEXT,)
    assert SOURCE.get(AGE_RATE, 2025, RATE).sources == (D_TEXT,)
    assert SOURCE.get(SPOUSE_BASE, 2025, CREDIT).sources == (ON428_TEXT,)
    assert SOURCE.get(SPOUSE_MAXIMUM, 2025, AMOUNT).sources == (ON428_TEXT,)


@pytest.mark.parametrize(
    ("family", "amount"),
    [
        (AGE_MAXIMUM, "6223.00"),
        (AGE_INCOME_THRESHOLD, "46330.00"),
        (SPOUSE_BASE, "11905.00"),
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
        # Return J's net income: (50000.00 - 46330.00) x 15% = 3670.00 x 15%.
        ("3670.00", "550.50"),
        # Return C's net income: (49535.00 - 46330) x 15%.
        ("3205.00", "480.75"),
        # Return A: (115000 - 46330) x 15%, more than the 6223 maximum.
        ("68670", "10300.50"),
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


@pytest.mark.parametrize(
    ("before_maximum", "limit"),
    [
        ("0", "0"),
        # Below the maximum: unchanged, as for a spouse with 4000 of net income.
        ("7905.00", "7905.00"),
        ("10822.99", "10822.99"),
        # At and above the maximum: 10823.
        ("10823.00", "10823"),
        ("11905.00", "10823"),
    ],
)
def test_the_ontario_spouse_amount_is_at_most_10823(before_maximum: str, limit: str) -> None:
    capability = CappedAmount(SOURCE.get(SPOUSE_MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, LIMIT)

    result = capability.compute((Artifact(BEFORE_MAXIMUM, D(before_maximum)),))

    assert result.outputs == (Artifact(LIMIT, D(limit)),)
