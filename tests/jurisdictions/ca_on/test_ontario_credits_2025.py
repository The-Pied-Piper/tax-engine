"""The 2025 Ontario fertility and seniors' transit credit figures, checked against CRA's ON479.

2025 Form ON479 (form 5006-TC), "Ontario fertility treatment tax credit": "Line 1 and line 61268:
Eligible medical expenses for fertility treatment multiplied by 25% (maximum $5,000) ="; "Ontario
seniors' public transit tax credit": "Line 14: Amount paid in the year for eligible seniors' use
of Ontario public transit services (maximum $3,000) Line 63100 multiplied by 15% =". The form
prints the fertility maximum after the rate, so it caps the credit; it prints the transit maximum
before the rate, so it bounds the amount paid: an amount paid above it is refused, not capped. Each
percentage is a rate (the `rate` kind), the fertility maximum a plain cap (the `amount` kind) and
the transit maximum a claimed amount (the `credit` kind). Lines 1 and 14 are dollars-and-cents
boxes, so each is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT as CREDIT_PARAMETER
from tax_engine.domain.parameters.credit import Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FERTILITY_RATE = "ca-on/fertility_credit_rate"
FERTILITY_MAXIMUM = "ca-on/fertility_credit_maximum"
TRANSIT_MAXIMUM = "ca-on/seniors_transit_maximum"
TRANSIT_RATE = "ca-on/seniors_transit_rate"
ON479_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-tc/5006-tc-25e.txt"

# Made up for this test and not registered: the amounts the rates and maximums are applied to
# and the results.
EXPENSES = ArtifactKind("ex/expenses", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/before_maximum", Decimal)
RESULT = ArtifactKind("ex/result", Decimal)
PAID = ArtifactKind("ex/paid", Decimal)
CREDIT = ArtifactKind("ex/credit", Decimal)
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_fertility_rate_is_25_percent() -> None:
    data = SOURCE.get(FERTILITY_RATE, 2025, RATE)

    assert data.values == Rate(D("0.25"))
    # ON479 line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_fertility_maximum_is_5000() -> None:
    data = SOURCE.get(FERTILITY_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("5000"))
    # ON479 line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_transit_maximum_is_3000() -> None:
    data = SOURCE.get(TRANSIT_MAXIMUM, 2025, CREDIT_PARAMETER)

    assert data.values == Credit(D("3000"))
    # ON479 line 14, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_transit_rate_is_15_percent() -> None:
    data = SOURCE.get(TRANSIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.15"))
    # ON479 line 14, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_on479_text() -> None:
    assert SOURCE.get(FERTILITY_RATE, 2025, RATE).sources == (ON479_TEXT,)
    assert SOURCE.get(FERTILITY_MAXIMUM, 2025, AMOUNT).sources == (ON479_TEXT,)
    assert SOURCE.get(TRANSIT_MAXIMUM, 2025, CREDIT_PARAMETER).sources == (ON479_TEXT,)
    assert SOURCE.get(TRANSIT_RATE, 2025, RATE).sources == (ON479_TEXT,)


@pytest.mark.parametrize(
    ("expenses", "credit"),
    [
        # Return G: 24000 x 25% = 6000, before the maximum.
        ("24000", "6000.00"),
        # Below the maximum: 12000 x 25% = 3000.
        ("12000", "3000.00"),
        # Returns A to G's other cases and the edges.
        ("0", "0"),
        ("20000", "5000.00"),
        # 1000.01 x 25% = 250.0025, rounded half-up to 250.00; 1000.02 x 25% = 250.005, a tie,
        # up to 250.01.
        ("1000.01", "250.00"),
        ("1000.02", "250.01"),
    ],
)
def test_25_percent_of_the_fertility_expenses(expenses: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(FERTILITY_RATE, 2025, RATE), EXPENSES, BEFORE_MAXIMUM)

    result = capability.compute((Artifact(EXPENSES, D(expenses)),))

    assert result.outputs == (Artifact(BEFORE_MAXIMUM, D(credit)),)


@pytest.mark.parametrize(
    ("credit", "capped"),
    [
        # Return G: 6000.00 is above the maximum.
        ("6000.00", "5000"),
        # At the maximum, and a cent above it.
        ("5000", "5000"),
        ("5000.01", "5000"),
        # Below it, the credit itself.
        ("3000.00", "3000.00"),
        ("0", "0"),
    ],
)
def test_the_fertility_credit_is_at_most_5000(credit: str, capped: str) -> None:
    capability = CappedAmount(SOURCE.get(FERTILITY_MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, RESULT)

    result = capability.compute((Artifact(BEFORE_MAXIMUM, D(credit)),))

    assert result.outputs == (Artifact(RESULT, D(capped)),)


MAXIMUM = ArtifactKind("ex/transit_maximum", Decimal)


def transit_bound(paid: str) -> Artifact[Decimal]:
    """The amount paid, checked against ON479 line 14's $3,000 maximum: the lines' two steps."""
    maximum = CreditAmount(SOURCE.get(TRANSIT_MAXIMUM, 2025, CREDIT_PARAMETER), MAXIMUM).compute(())
    result = AtMost(PAID, MAXIMUM, RESULT).compute((Artifact(PAID, D(paid)), *maximum.outputs))
    (checked,) = result.outputs
    return checked


@pytest.mark.parametrize(
    "paid",
    [
        # Return G: 1200 is below the maximum.
        "1200",
        # At the maximum.
        "3000",
        "0",
    ],
)
def test_the_transit_amount_paid_up_to_3000_is_taken_as_entered(paid: str) -> None:
    assert transit_bound(paid) == Artifact(RESULT, D(paid))


@pytest.mark.parametrize("paid", ["3000.01", "3500"])
def test_the_transit_amount_paid_above_3000_is_refused_not_capped(paid: str) -> None:
    with pytest.raises(InputAboveBoundError, match="ex/transit_maximum 3000"):
        transit_bound(paid)


@pytest.mark.parametrize(
    ("amount", "credit"),
    [
        # Return G: 1200 x 15% = 180.
        ("1200", "180.00"),
        # 3000 paid, the most the line takes: 3000 x 15% = 450.
        ("3000", "450.00"),
        ("0", "0"),
        # 0.03 x 15% = 0.0045, rounded half-up to 0.00; 0.10 x 15% = 0.015, a tie, up to 0.02.
        ("0.03", "0.00"),
        ("0.10", "0.02"),
    ],
)
def test_15_percent_of_the_transit_amount(amount: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(TRANSIT_RATE, 2025, RATE), RESULT, CREDIT)

    result = capability.compute((Artifact(RESULT, D(amount)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)


def test_transit_paid_3000_gives_450_through_the_check_then_the_rate() -> None:
    rate = ApplyRate(SOURCE.get(TRANSIT_RATE, 2025, RATE), RESULT, CREDIT)

    result = rate.compute((transit_bound("3000"),))

    assert result.outputs == (Artifact(CREDIT, D("450.00")),)
