"""The 2025 federal tuition datasets (Schedule 11), checked against CRA's form 5000-S11.

Form 5000-S11 (T1-2025), "Calculating your federal tuition amount and Canada training credit":
line 2 "Amount from line 1 multiplied by 50% ="; "Enter the amount from line 26000 of your return
on line 11 if it is $57,375 or less. If it is more than $57,375, enter the result of the following
calculation:" and line 11 "Amount from line 76 of your return divided by 14.5% ="; and, on the back,
line 21 "Amount from line 8 of the previous page (maximum $5,000)".

Three datasets, each the figure of one line: the Canada training credit rate (line 2, the `rate`
kind, 50%), the line 11 threshold and rate (the `threshold_rate` kind, $57,375 and 14.5%) and the
transfer maximum (line 21, the `amount` kind, $5,000, a bound the line takes the lesser of).
The form states no rounding rule for these dollars-and-cents boxes, so each rounds half-up to the
cent, the owner's decision.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tax_engine.jurisdictions.ca.capabilities.amount_or_divided_by_rate import (
    AmountOrDividedByRate,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
SCHEDULE_11 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s11/5000-s11-25e.txt"

TRAINING_CREDIT_RATE = "ca/canada_training_credit_rate"
INCOME_LIMIT = "ca/tuition_income_limit"
TRANSFER_MAXIMUM = "ca/tuition_transfer_maximum"

# Made up for these tests and not registered.
FEES = ArtifactKind("ex/fees", Decimal)
INCOME = ArtifactKind("ex/income", Decimal)
TAX = ArtifactKind("ex/tax", Decimal)
OUTPUT = ArtifactKind("ex/out", Decimal)


def test_2025_canada_training_credit_rate_is_50_percent_to_the_cent() -> None:
    data = SOURCE.get(TRAINING_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    assert data.rounding == CENT


def test_2025_line_11_threshold_is_57375_and_rate_14_5_percent_to_the_cent() -> None:
    data = SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE)

    assert data.values == ThresholdRate(Rate(D("0.145")), D("57375"))
    assert data.rounding == CENT


def test_2025_transfer_maximum_is_5000_to_the_cent() -> None:
    data = SOURCE.get(TRANSFER_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("5000"))
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("family", "kind"),
    [
        (TRAINING_CREDIT_RATE, RATE),
        (INCOME_LIMIT, THRESHOLD_RATE),
        (TRANSFER_MAXIMUM, AMOUNT),
    ],
)
def test_2025_tuition_datasets_cite_schedule_11(family: str, kind: ParameterKind[Any]) -> None:
    data = SOURCE.get(family, 2025, kind)

    assert SCHEDULE_11 in data.sources


@pytest.mark.parametrize(
    ("fees", "line_2"),
    [
        # Schedule 11 worked example: $6,000 of Canadian fees, 50% is $3,000.
        ("6000", "3000.00"),
        ("0", "0"),
        # 1000.01 x 50% = 500.005, a tie, rounded half-up to 500.01.
        ("1000.01", "500.01"),
    ],
)
def test_line_2_is_50_percent_of_the_fees_to_the_cent(fees: str, line_2: str) -> None:
    capability = ApplyRate(SOURCE.get(TRAINING_CREDIT_RATE, 2025, RATE), FEES, OUTPUT)

    result = capability.compute((Artifact(FEES, D(fees)),))

    assert result.outputs == (Artifact(OUTPUT, D(line_2)),)


@pytest.mark.parametrize(
    ("income", "tax", "line_11"),
    [
        # At or below $57,375 ("or less") line 11 is the taxable income, line 26000.
        ("30000", "4350", "30000"),
        ("57375", "8319.38", "57375"),
        # Over it: the tax (line 76) divided by 14.5%, rounded half-up to the cent:
        # 8319.38 / 0.145 = 57375.0344..., 57375.03.
        ("57375.01", "8319.38", "57375.03"),
        # 12747.18 / 0.145 = 87911.5862..., 87911.59.
        ("78974", "12747.18", "87911.59"),
    ],
)
def test_line_11_is_the_taxable_income_or_the_tax_divided_by_14_5_percent(
    income: str, tax: str, line_11: str
) -> None:
    capability = AmountOrDividedByRate(
        SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE), INCOME, TAX, OUTPUT
    )

    result = capability.compute((Artifact(INCOME, D(income)), Artifact(TAX, D(tax))))

    assert result.outputs == (Artifact(OUTPUT, D(line_11)),)


@pytest.mark.parametrize(
    ("line_8", "line_21"),
    [
        # Schedule 11 worked example: line 8 is $6,000, so line 21 is the maximum $5,000.
        ("6000", "5000"),
        ("5000", "5000"),
        ("4999.99", "4999.99"),
        ("0", "0"),
    ],
)
def test_line_21_is_line_8_at_most_5000(line_8: str, line_21: str) -> None:
    capability = CappedAmount(SOURCE.get(TRANSFER_MAXIMUM, 2025, AMOUNT), FEES, OUTPUT)

    result = capability.compute((Artifact(FEES, D(line_8)),))

    assert result.outputs == (Artifact(OUTPUT, D(line_21)),)
