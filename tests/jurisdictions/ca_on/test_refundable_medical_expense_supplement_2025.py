"""The 2025 refundable medical expense supplement figures (T1 line 45200), checked against CRA.

2025 Federal Worksheet (form 5000-D1), "Line 45200 - Refundable medical expense supplement": "You
may be able to claim this supplement if all of the following apply:" "You entered an amount on line
21500 or line 33200 of your return" "You were resident in Canada throughout 2025" "You were 18
years of age or older at the end of 2025" "Your adjusted family net income is less than $63,374";
"In addition, the total of the following two amounts must be $4,390 or more:" "your employment
income from lines 10100 and 10400 of your return (other than amounts received from a wage-loss
replacement plan) minus the amounts from lines 20700, 21200, 22900, and 23100 of your return (if the
result is negative, consider it as "0")" "your net self-employment income (not including losses)
from lines 13500, 13700, 13900, 14100, and 14300 of your return". The calculation: "Line 6: Add the
amounts from line 5 of columns 1 and 2. Adjusted family net income"; "Line 7: Income threshold
33,294.00"; "Line 8: Line 6 minus line 7 (if negative, enter "0") ="; "Line 9: Amount from line
21500 of your return"; "Line 10: Amount from line 33200 of your return"; "Line 11: Line 9 plus line
10"; "Line 12: Applicable rate 25%"; "Line 13: Line 11 multiplied by the percentage from line 12
="; "Line 14: Enter whichever is less: amount from line 13 or $1,504"; "Line 15: Amount from line
8" "multiplied by 5% ="; "Line 16: Line 14 minus line 15 (if negative, enter "0") Enter this
amount on line 45200 of your return. =".

Every printed figure is a dataset as printed, none derived: the $33,294.00 of line 7 a constant (the
`credit` kind, claimed whole), the 25% of line 12 and the 5% of line 15 rates, the $1,504 of line 14
a plain cap (the `amount` kind) and the $4,390 of the working income condition an amount for
`ca/threshold_gate` (the `amount` kind). The form states no rounding rule; lines 7, 13, 14, 15 and
16 are dollars-and-cents boxes, so each is rounded half-up to the cent, the owner's decision. The
condition "less than $63,374" has no step of its own: at 63,374 line 15 is 5% x 30,080 = 1,504, so
line 16 is already 0 there.

The datasets are tested with the capabilities that read them, on made-up kinds for the worksheet's
lines; the lines together, from line 6 and the amounts of lines 9 and 10 to line 16 and through the
working income condition, are tested against the cases the worksheet's text settles.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.capped_amount import CappedAmount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capability import CapabilityResult
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.jurisdictions.ca.capabilities.threshold_gate import ThresholdGate

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"
INCOME_THRESHOLD = "ca/medical_supplement_income_threshold"
RATE_25 = "ca/medical_supplement_rate"
MAXIMUM = "ca/medical_supplement_maximum"
REDUCTION_RATE = "ca/medical_supplement_reduction_rate"
WORKING_INCOME_THRESHOLD = "ca/medical_supplement_working_income_threshold"

# Made up for this test and not registered: the adjusted family net income (line 6), the printed
# income threshold (line 7), line 8, line 9 plus line 10 (line 11), lines 13, 14, 15 and 16, the
# working income and the gated line 16.
LINE_6 = ArtifactKind("ex/line_6", Decimal)
LINE_7 = ArtifactKind("ex/line_7", Decimal)
LINE_8 = ArtifactKind("ex/line_8", Decimal)
LINE_9 = ArtifactKind("ex/line_9", Decimal)
LINE_10 = ArtifactKind("ex/line_10", Decimal)
LINE_11 = ArtifactKind("ex/line_11", Decimal)
LINE_13 = ArtifactKind("ex/line_13", Decimal)
LINE_14 = ArtifactKind("ex/line_14", Decimal)
LINE_15 = ArtifactKind("ex/line_15", Decimal)
LINE_16 = ArtifactKind("ex/line_16", Decimal)
WORKING_INCOME = ArtifactKind("ex/working_income", Decimal)
GATED = ArtifactKind("ex/gated_line_16", Decimal)


def only(result: CapabilityResult) -> Artifact[Decimal]:
    (output,) = result.outputs
    return cast(Artifact[Decimal], output)


def line_16(family_net_income: str, line_9: str, line_10: str) -> Decimal:
    """Line 16 from the real datasets: lines 7, 8, 11, 13, 14 and 15 as the form prints them."""
    line_7 = only(CreditAmount(SOURCE.get(INCOME_THRESHOLD, 2025, CREDIT), LINE_7).compute(()))
    line_8 = only(
        SubtractNotBelowZero(LINE_6, LINE_7, LINE_8).compute(
            (Artifact(LINE_6, D(family_net_income)), line_7)
        )
    )
    line_11 = only(
        Sum((LINE_9, LINE_10), LINE_11).compute(
            (Artifact(LINE_9, D(line_9)), Artifact(LINE_10, D(line_10)))
        )
    )
    line_13 = only(ApplyRate(SOURCE.get(RATE_25, 2025, RATE), LINE_11, LINE_13).compute((line_11,)))
    line_14 = only(
        CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), LINE_13, LINE_14).compute((line_13,))
    )
    line_15 = only(
        ApplyRate(SOURCE.get(REDUCTION_RATE, 2025, RATE), LINE_8, LINE_15).compute((line_8,))
    )
    return only(SubtractNotBelowZero(LINE_14, LINE_15, LINE_16).compute((line_14, line_15))).value


def gated(working_income: str, amount: str) -> Decimal:
    """Line 16 passed through the "$4,390 or more" condition, on the real threshold dataset."""
    gate = ThresholdGate(
        SOURCE.get(WORKING_INCOME_THRESHOLD, 2025, AMOUNT), LINE_16, WORKING_INCOME, GATED
    )
    return only(
        gate.compute((Artifact(LINE_16, D(amount)), Artifact(WORKING_INCOME, D(working_income))))
    ).value


def test_2025_line_7_is_the_printed_constant() -> None:
    data = SOURCE.get(INCOME_THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("33294.00"))
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_line_12_is_the_printed_rate() -> None:
    data = SOURCE.get(RATE_25, 2025, RATE)

    assert data.values == Rate(D("0.25"))
    # Line 13, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_line_14_maximum_is_1504() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("1504"))
    # Line 14, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_line_15_rate_is_the_printed_5_percent() -> None:
    data = SOURCE.get(REDUCTION_RATE, 2025, RATE)

    assert data.values == Rate(D("0.05"))
    # Line 15, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_working_income_threshold_is_4390() -> None:
    data = SOURCE.get(WORKING_INCOME_THRESHOLD, 2025, AMOUNT)

    assert data.values == Amount(D("4390"))
    # Line 16 is a dollars-and-cents box, so the gated amount is rounded half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


@pytest.mark.parametrize(
    ("family_net_income", "line_9", "line_10", "expected"),
    [
        # Lines 9 and 10 total 6,000, 25% = 1,500, under the 1,504
        # maximum; adjusted family net income 20,000 is under the 33,294 threshold, so no reduction.
        ("20000", "0", "6000", "1500.00"),
        # Line 9 and line 10 are added: 1,000 + 5,000.
        ("20000", "1000", "5000", "1500.00"),
        # 25% of 6,016 is 1,504 exactly, the maximum.
        ("20000", "0", "6016", "1504.00"),
        # Over the maximum: 25% of 8,000 is 2,000, line 14 is 1,504.
        ("20000", "0", "8000", "1504.00"),
        # No amount on line 21500 or line 33200: line 11 is 0, so line 16 is 0.
        ("20000", "0", "0", "0.00"),
        # At the income threshold line 8 is 0; a dollar over it line 8 is 1, line 15 is 0.05.
        ("33294", "0", "8000", "1504.00"),
        ("33295", "0", "8000", "1503.95"),
        # Line 8 = 63,373 - 33,294 = 30,079, line 15 = 1,503.95, line 16 = 0.05.
        ("63373", "0", "8000", "0.05"),
        # "Your adjusted family net income is less than $63,374": at 63,374 line 15 is 5% x 30,080
        # = 1,504.00, so line 16 is 0 without a step of its own, and above it, too.
        ("63374", "0", "8000", "0.00"),
        ("63375", "0", "8000", "0.00"),
        ("100000", "0", "8000", "0.00"),
        # Line 13 is half-up to the cent: 25% of 6,000.02 = 1,500.005, up to 1,500.01.
        ("20000", "0", "6000.02", "1500.01"),
        # Line 15 is half-up to the cent: 5% x 0.10 = 0.005, up to 0.01, so 1,500.00 - 0.01.
        ("33294.10", "0", "6000", "1499.99"),
        # Below the income threshold there is no reduction: 25% of 3,000 = 750.
        ("10000.40", "0", "3000", "750.00"),
        # A reduction over line 14: line 8 = 40,000 - 33,294 = 6,706, line 15 = 335.30, line 14 =
        # 25% x 1,000 = 250.00, so line 16 is 0 (not negative).
        ("40000", "0", "1000", "0.00"),
    ],
)
def test_line_16_is_line_14_less_line_15_not_below_zero(
    family_net_income: str, line_9: str, line_10: str, expected: str
) -> None:
    assert line_16(family_net_income, line_9, line_10) == D(expected)


@pytest.mark.parametrize(
    ("working_income", "passed"),
    [
        # "$4,390 or more": 4,389.99 gives 0; 4,390 and 4,390.01 give the amount.
        ("4389.99", "0.00"),
        ("4390", "1500.00"),
        ("4390.01", "1500.00"),
        # The worked example: working income 4,300 gives 0, 4,390 gives 1,500.
        ("4300", "0.00"),
        ("0", "0.00"),
        ("100000", "1500.00"),
    ],
)
def test_working_income_of_4390_or_more_passes_line_16_through(
    working_income: str, passed: str
) -> None:
    assert gated(working_income, "1500.00") == D(passed)
