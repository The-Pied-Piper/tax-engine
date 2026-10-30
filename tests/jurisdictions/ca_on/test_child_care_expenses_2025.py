"""The 2025 child care expenses deduction's figures, checked against CRA's Form T778.

2025 T1 (form 5000-R) line 41 (line 21400) "Child care expenses (complete Form T778)". Form T778:
Part A line 67950 "Total (add all entries for Child care expenses paid)"; Part B line 1 "Number of
eligible children born in 2019 or later whom the disability amount cannot be claimed for"
"multiplied by $8,000"; line 2 (67960) "Number of eligible children born in 2025 or earlier whom
the disability amount can be claimed for" "multiplied by $11,000"; line 3 "Number of eligible
children born in 2009 to 2018 (and born in 2008 or earlier with a mental or physical infirmity
whom the disability amount cannot be claimed for)" "multiplied by $5,000"; line 4 "Add lines 1 to
3."; line 5 "Enter the amount from line 67950."; line 6 "Enter your earned income." "multiplied by
two-thirds"; line 7 "Enter whichever amount is the least: line 4, line 5 or line 6."; line 9 "Line
7 minus line 8. ... enter this amount on line 21400 of your return. Allowable deduction". The
$8,000, $11,000 and $5,000 are per-unit amounts (the `amount` kind); two-thirds is not a finite
decimal, so it is a `fraction`. Each line is a dollars-and-cents box, so lines 1 to 3 and 6
are rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
UNDER_SEVEN = "ca/child_care_limit_under_seven"
DISABILITY = "ca/child_care_limit_disability"
SEVEN_TO_SIXTEEN = "ca/child_care_limit_seven_to_sixteen"
EARNED_INCOME_FRACTION = "ca/child_care_earned_income_fraction"
T778_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t778/t778-25e.txt"

# Made up for this test and not registered: a number of eligible children and their limit (T778
# Part B lines 1 to 3), and the earned income and two-thirds of it (line 6).
CHILDREN = ArtifactKind("ex/children", int)
LIMIT = ArtifactKind("ex/limit", Decimal)
EARNED = ArtifactKind("ex/earned_income", Decimal)
EARNED_LIMIT = ArtifactKind("ex/earned_income_limit", Decimal)


@pytest.mark.parametrize(
    ("family", "amount"),
    [(UNDER_SEVEN, "8000"), (DISABILITY, "11000"), (SEVEN_TO_SIXTEEN, "5000")],
)
def test_2025_amount_per_eligible_child(family: str, amount: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT)

    assert data.values == Amount(D(amount))
    # T778 Part B lines 1 to 3, dollars-and-cents boxes: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_earned_income_fraction_is_two_thirds() -> None:
    data = SOURCE.get(EARNED_INCOME_FRACTION, 2025, FRACTION)

    assert data.values == Fraction(2, 3)
    # T778 line 6, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_datasets_cite_only_their_form_text() -> None:
    for family in (UNDER_SEVEN, DISABILITY, SEVEN_TO_SIXTEEN):
        assert SOURCE.get(family, 2025, AMOUNT).sources == (T778_TEXT,), family
    assert SOURCE.get(EARNED_INCOME_FRACTION, 2025, FRACTION).sources == (T778_TEXT,)


@pytest.mark.parametrize(
    ("family", "count", "limit"),
    [
        # Returns A to F: no child born in 2019 or later and none with the disability amount.
        (UNDER_SEVEN, 0, "0"),
        (UNDER_SEVEN, 1, "8000"),
        (UNDER_SEVEN, 2, "16000"),
        (DISABILITY, 0, "0"),
        (DISABILITY, 1, "11000"),
        (DISABILITY, 3, "33000"),
        # Return F: one child born in 2015; Returns A to E: none.
        (SEVEN_TO_SIXTEEN, 0, "0"),
        (SEVEN_TO_SIXTEEN, 1, "5000"),
        (SEVEN_TO_SIXTEEN, 2, "10000"),
    ],
)
def test_the_limit_for_each_eligible_child(family: str, count: int, limit: str) -> None:
    capability = PerUnitAmount(SOURCE.get(family, 2025, AMOUNT), CHILDREN, LIMIT)

    result = capability.compute((Artifact(CHILDREN, count),))

    assert result.outputs == (Artifact(LIMIT, D(limit)),)


@pytest.mark.parametrize(
    ("earned", "limit"),
    [
        # Return F: two-thirds of 60000.
        ("60000", "40000"),
        ("30000", "20000"),
        ("75000", "50000"),
        # Return A: 220000 / 3 = 73333.333..., rounded half-up to the cent.
        ("110000", "73333.33"),
        # 200 / 3 = 66.666..., rounded half-up to 66.67.
        ("100", "66.67"),
        ("0", "0"),
    ],
)
def test_the_earned_income_limit_is_two_thirds_of_it(earned: str, limit: str) -> None:
    capability = ApplyFraction(
        SOURCE.get(EARNED_INCOME_FRACTION, 2025, FRACTION), EARNED, EARNED_LIMIT
    )

    result = capability.compute((Artifact(EARNED, D(earned)),))

    assert result.outputs == (Artifact(EARNED_LIMIT, D(limit)),)
