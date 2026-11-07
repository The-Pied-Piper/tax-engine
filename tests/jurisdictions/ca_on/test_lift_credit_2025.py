"""The 2025 Ontario LIFT credit rate and maximum, checked against CRA's ON428-A.

2025 Schedule ON428-A (form 5006-A): line 1 "Amount from line 10100 of your return"; line 2
"Amount from line 10400 of your return"; line 3 "Line 1 plus line 2"; line 4 "Applicable rate
5.05%"; line 5 "Line 3 multiplied by the percentage from line 4 (maximum $875)"; line 13 "Line 9
minus line 12 (if negative, enter "0") Your adjusted net income"; Part A, "If you were single at
the end of the year": line 14 "Amount from line 5 above (maximum $875)"; line 15 "Amount from line
13 above"; line 16 "Individual income threshold 32,500.00"; line 17 "Line 15 minus line 16 (if
negative, enter "0")"; line 18 "Applicable rate 5%"; line 19 "Line 17 multiplied by the percentage
from line 18"; line 20 "Line 14 minus line 19 (if negative, enter "0") Enter this amount on line
62140 of your Form ON428." The 5.05% is a rate (the `rate` kind), the $875 a plain cap (the
`amount` kind). Lines 5 and 14 are dollars-and-cents boxes, so each is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate
from tax_engine.jurisdictions.core.capabilities.capped_amount import CappedAmount
from tax_engine.jurisdictions.core.capabilities.credit_amount import CreditAmount

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
RATE_FAMILY = "ca-on/lift_rate"
MAXIMUM = "ca-on/lift_maximum"
INDIVIDUAL_THRESHOLD = "ca-on/lift_individual_income_threshold"
ON428_A_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-a/5006-a-25e.txt"

# Made up for this test and not registered: the employment income the rate is applied to (line
# 3), and the credit before its maximum and after it (lines 5 and 14).
INCOME = AmountKind("ex/income")
BEFORE_MAXIMUM = AmountKind("ex/before_maximum")
CAPPED = AmountKind("ex/capped")
# Part A: the threshold a credit dataset gives (line 16).
THRESHOLD = AmountKind("ex/threshold")


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


def test_2025_datasets_cite_only_the_on428_a_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (ON428_A_TEXT,)
    assert SOURCE.get(MAXIMUM, 2025, AMOUNT).sources == (ON428_A_TEXT,)


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


def test_2025_individual_income_threshold_is_32500() -> None:
    data = SOURCE.get(INDIVIDUAL_THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("32500.00"))
    # ON428-A line 31, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_part_b_datasets_cite_only_the_on428_a_text() -> None:
    assert SOURCE.get(INDIVIDUAL_THRESHOLD, 2025, CREDIT).sources == (ON428_A_TEXT,)


@pytest.mark.parametrize(
    ("family", "amount"),
    [
        (INDIVIDUAL_THRESHOLD, "32500.00"),
    ],
)
def test_a_threshold_dataset_is_claimed_whole(family: str, amount: str) -> None:
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), THRESHOLD)

    result = capability.compute(())

    assert result.outputs == (Artifact(THRESHOLD, D(amount)),)
