"""The 2025 labour-sponsored funds tax credit figures, checked against CRA's guide.

2025 General Income Tax and Benefit Guide (form 5000-G), "Line 41400 - Labour-sponsored funds tax
credit": "Claim the amount of your allowable credit on line 41400 of your return that is equal to
15% of the net cost reported on line 41300 of your return, to a maximum of $750." The percentage is
a rate (the `rate` kind) and the maximum a plain cap (the `amount` kind); the credit is the product
first and then at most the maximum, so the cap sits after the percentage. Line 41400 is a
dollars-and-cents box, so each is rounded half-up to the cent.

The datasets are tested with the capabilities that read them, on made-up kinds; the lines together,
from the net cost of line 41300 to line 42000, are in the `end_to_end` tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
RATE_FAMILY = "ca/labour_sponsored_funds_rate"
MAXIMUM = "ca/labour_sponsored_funds_maximum"
GUIDE_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the net cost of the shares (line 41300), the credit
# before its maximum and the credit (line 41400).
NET_COST = ArtifactKind("ex/net_cost", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/before_maximum", Decimal)
CREDIT = ArtifactKind("ex/credit", Decimal)


def test_2025_rate_is_15_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.15"))
    # Line 41400, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_maximum_is_750() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("750"))
    # Line 41400, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_guide_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (GUIDE_TEXT,)
    assert SOURCE.get(MAXIMUM, 2025, AMOUNT).sources == (GUIDE_TEXT,)


@pytest.mark.parametrize(
    ("net_cost", "before_maximum"),
    [
        # The worked example: 4,000 x 15% = 600.00.
        ("4000", "600.00"),
        ("0", "0.00"),
        # 0.03 x 15% = 0.0045, rounded half-up to 0.00; 0.10 x 15% = 0.015, a tie, up to 0.02.
        ("0.03", "0.00"),
        ("0.10", "0.02"),
    ],
)
def test_15_percent_of_the_net_cost(net_cost: str, before_maximum: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), NET_COST, BEFORE_MAXIMUM)

    result = capability.compute((Artifact(NET_COST, D(net_cost)),))

    assert result.outputs == (Artifact(BEFORE_MAXIMUM, D(before_maximum)),)


@pytest.mark.parametrize(
    ("before_maximum", "credit"),
    [
        # Below the maximum, the amount itself.
        ("600.00", "600.00"),
        ("0", "0.00"),
        # At the maximum, and a cent above it.
        ("750.00", "750.00"),
        ("750.01", "750.00"),
        # The worked example's second case: 6,000 x 15% = 900.00, at most 750.00.
        ("900.00", "750.00"),
    ],
)
def test_the_credit_is_at_most_750(before_maximum: str, credit: str) -> None:
    capability = CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, CREDIT)

    result = capability.compute((Artifact(BEFORE_MAXIMUM, D(before_maximum)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)


@pytest.mark.parametrize(
    ("net_cost", "credit"),
    [
        # The acceptance criteria: a net cost of 4,000 gives 600.00; 6,000 gives 900.00, capped at
        # 750.00.
        ("4000", "600.00"),
        ("6000", "750.00"),
        # The net cost at which the cap starts: 5,000 x 15% = 750.00 exactly.
        ("5000", "750.00"),
        ("5000.01", "750.00"),
        # 4999.90 x 15% = 749.985, a tie, rounded half-up to 749.99, below the maximum.
        ("4999.90", "749.99"),
        ("0", "0.00"),
    ],
)
def test_a_net_cost_gives_15_percent_through_the_rate_then_the_cap(
    net_cost: str, credit: str
) -> None:
    rate = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), NET_COST, BEFORE_MAXIMUM)
    cap = CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, CREDIT)

    rated = rate.compute((Artifact(NET_COST, D(net_cost)),))
    result = cap.compute(rated.outputs)

    assert result.outputs == (Artifact(CREDIT, D(credit)),)
