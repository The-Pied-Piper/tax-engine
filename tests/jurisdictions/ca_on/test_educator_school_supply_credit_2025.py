"""The 2025 eligible educator school supply tax credit figures, checked against CRA's T1.

2025 T1, Ontario edition (form 5006-R), Step 6, "Eligible educator school supply tax credit":
"Line 161 and line 46900: Supplies expenses (maximum $1,000) Line 46800 multiplied by 25% =". The
form prints the maximum before the percentage, so it caps the supplies expenses (line 46800), not
the credit. The percentage is a rate (the `rate` kind) and the maximum a plain cap (the `amount`
kind). Line 161 is a dollars-and-cents box, so each is rounded half-up to the cent.

The datasets are tested with the capabilities that read them, on made-up kinds; the lines together,
from the supplies paid to line 48200, are in the `end_to_end` tests.
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
MAXIMUM = "ca/educator_supplies_maximum"
RATE_FAMILY = "ca/educator_supplies_rate"
T1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-r/5006-r-25e.txt"

# Made up for this test and not registered: the supplies paid (line 46800), the part of it that
# counts and the credit (line 46900).
PAID = ArtifactKind("ex/paid", Decimal)
COUNTED = ArtifactKind("ex/counted", Decimal)
CREDIT = ArtifactKind("ex/credit", Decimal)
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_1000() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("1000"))
    # Line 161, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_rate_is_25_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.25"))
    # Line 161, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_t1_text() -> None:
    assert SOURCE.get(MAXIMUM, 2025, AMOUNT).sources == (T1_TEXT,)
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (T1_TEXT,)


@pytest.mark.parametrize(
    ("paid", "counted"),
    [
        # The worked example: 1,200 paid counts as 1,000.
        ("1200", "1000"),
        # At the maximum, and a cent above it.
        ("1000", "1000"),
        ("1000.01", "1000"),
        # Below it, the amount itself.
        ("800", "800"),
        ("0", "0"),
    ],
)
def test_the_supplies_expenses_are_at_most_1000(paid: str, counted: str) -> None:
    capability = CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), PAID, COUNTED)

    result = capability.compute((Artifact(PAID, D(paid)),))

    assert result.outputs == (Artifact(COUNTED, D(counted)),)


@pytest.mark.parametrize(
    ("counted", "credit"),
    [
        # The worked example: 1000 x 25% = 250.00.
        ("1000", "250.00"),
        ("800", "200.00"),
        ("0", "0"),
        # 0.01 x 25% = 0.0025, rounded half-up to 0.00; 0.02 x 25% = 0.005, a tie, up to 0.01.
        ("0.01", "0.00"),
        ("0.02", "0.01"),
    ],
)
def test_25_percent_of_the_supplies_expenses(counted: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), COUNTED, CREDIT)

    result = capability.compute((Artifact(COUNTED, D(counted)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)


def test_supplies_paid_of_1200_give_250_through_the_cap_then_the_rate() -> None:
    cap = CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), PAID, COUNTED)
    rate = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), COUNTED, CREDIT)

    capped = cap.compute((Artifact(PAID, D("1200")),))
    result = rate.compute(capped.outputs)

    assert result.outputs == (Artifact(CREDIT, D("250.00")),)
