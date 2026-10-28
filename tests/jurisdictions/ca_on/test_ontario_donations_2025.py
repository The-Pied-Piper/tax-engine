"""The 2025 Ontario donations and gifts credit rates and arithmetic, checked against CRA's ON428.

2025 ON428 (form 5006-C), "Donations and gifts:": line 47 "Amount from line 13 of your federal
Schedule 9" "multiplied by 5.05% ="; line 48 "Amount from line 14 of your federal Schedule 9 ="
"multiplied by 11.16% ="; line 49 and line 58969 "Line 47 plus line 48 ="; line 50 and line 61500
"Line 46 plus line 49 Enter this amount on line 52. Ontario non-refundable tax credits =". Each
percentage is a rate (the `rate` kind), and every box is dollars and cents, so each product is
rounded half-up to the cent; the sums take amounts already in cents. Lines 47 and 48 read the
federal Schedule 9 (the amounts of its lines 13 and 14, from the federal artifacts); nothing here
recomputes them. Line 46 is the Ontario credit rate applied once to the total of the credit
amounts, and line 50 adds line 49 to it.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FIRST_TIER_RATE = "ca-on/donation_first_tier_rate"
OVER_FIRST_TIER_RATE = "ca-on/donation_over_first_tier_rate"
CREDIT_RATE = "ca-on/credit_rate"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: Schedule 9 lines 12, 13 and 14 (the federal
# artifacts the Ontario lines read), the $200, and one kind for each ON428 line.
SCHEDULE_9_LINE_12 = ArtifactKind("ex/schedule_9_line_12", Decimal)
FIRST_TIER_MAXIMUM = ArtifactKind("ex/first_tier_maximum", Decimal)
SCHEDULE_9_LINE_13 = ArtifactKind("ex/schedule_9_line_13", Decimal)
SCHEDULE_9_LINE_14 = ArtifactKind("ex/schedule_9_line_14", Decimal)
LINE_46 = ArtifactKind("ex/line_46", Decimal)
LINE_47 = ArtifactKind("ex/line_47", Decimal)
LINE_48 = ArtifactKind("ex/line_48", Decimal)
LINE_49 = ArtifactKind("ex/line_49", Decimal)
LINE_50 = ArtifactKind("ex/line_50", Decimal)


def line_47(schedule_9_line_13: str) -> Decimal:
    capability = ApplyRate(SOURCE.get(FIRST_TIER_RATE, 2025, RATE), SCHEDULE_9_LINE_13, LINE_47)
    result = capability.compute((Artifact(SCHEDULE_9_LINE_13, D(schedule_9_line_13)),))
    (artifact,) = result.outputs
    value: Decimal = artifact.value
    return value


def line_48(schedule_9_line_14: str) -> Decimal:
    capability = ApplyRate(
        SOURCE.get(OVER_FIRST_TIER_RATE, 2025, RATE), SCHEDULE_9_LINE_14, LINE_48
    )
    result = capability.compute((Artifact(SCHEDULE_9_LINE_14, D(schedule_9_line_14)),))
    (artifact,) = result.outputs
    value: Decimal = artifact.value
    return value


def line_49(schedule_9_line_13: str, schedule_9_line_14: str) -> Decimal:
    result = Sum((LINE_47, LINE_48), LINE_49).compute(
        (
            Artifact(LINE_47, line_47(schedule_9_line_13)),
            Artifact(LINE_48, line_48(schedule_9_line_14)),
        )
    )
    (artifact,) = result.outputs
    value: Decimal = artifact.value
    return value


def test_2025_first_tier_rate_is_5_05_percent() -> None:
    data = SOURCE.get(FIRST_TIER_RATE, 2025, RATE)

    assert data.values == Rate(D("0.0505"))
    # ON428 line 47, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_rate_over_the_first_tier_is_11_16_percent() -> None:
    data = SOURCE.get(OVER_FIRST_TIER_RATE, 2025, RATE)

    assert data.values == Rate(D("0.1116"))
    # ON428 line 48, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_donation_rates_cite_only_the_on428_text() -> None:
    assert SOURCE.get(FIRST_TIER_RATE, 2025, RATE).sources == (ON428_TEXT,)
    assert SOURCE.get(OVER_FIRST_TIER_RATE, 2025, RATE).sources == (ON428_TEXT,)


@pytest.mark.parametrize(
    ("schedule_9_line_13", "credit"),
    [
        # The worked example and Return N: 5.05% x 200.
        ("200", "10.10"),
        ("200.00", "10.10"),
        ("0", "0"),
        ("100", "5.05"),
        # A line 13 under $200: 5.05% x 150.25 = 7.587625, rounded half-up to 7.59.
        ("150.25", "7.59"),
        # 5.05% x 10 = 0.505, a tie, up to 0.51 (half-even would give 0.50); 5.05% x 50 = 2.525,
        # a tie, up to 2.53 (half-even would give 2.52).
        ("10", "0.51"),
        ("50", "2.53"),
        # 0.10 x 5.05% = 0.00505, over a half cent, up to 0.01; 0.01 x 5.05% = 0.000505, down.
        ("0.10", "0.01"),
        ("0.01", "0.00"),
    ],
)
def test_line_47_is_5_05_percent_of_schedule_9_line_13(
    schedule_9_line_13: str, credit: str
) -> None:
    assert line_47(schedule_9_line_13) == D(credit)


@pytest.mark.parametrize(
    ("schedule_9_line_14", "credit"),
    [
        # The worked example and Return N: 11.16% x 1,300.
        ("1300", "145.08"),
        ("1300.00", "145.08"),
        ("0", "0"),
        ("50000", "5580.00"),
        # 11.16% x 1,234.57 = 137.778012, rounded half-up to 137.78.
        ("1234.57", "137.78"),
        # 11.16% x 12.50 = 1.395, a tie, up to 1.40; 11.16% x 37.50 = 4.185, a tie, up to 4.19
        # (half-even would give 4.18); 11.16% x 87.50 = 9.765, up to 9.77 (half-even 9.76).
        ("12.50", "1.40"),
        ("37.50", "4.19"),
        ("87.50", "9.77"),
        ("0.01", "0.00"),
        ("0.05", "0.01"),
    ],
)
def test_line_48_is_11_16_percent_of_schedule_9_line_14(
    schedule_9_line_14: str, credit: str
) -> None:
    assert line_48(schedule_9_line_14) == D(credit)


@pytest.mark.parametrize(
    ("schedule_9_line_13", "schedule_9_line_14", "line_47_amount", "line_48_amount", "total"),
    [
        # The worked example: 5.05% x 200 = 10.10 and 11.16% x 1,300 = 145.08; line 58969 =
        # 155.18.
        ("200", "1300", "10.10", "145.08", "155.18"),
        # Only the first tier: a line 12 of 120 gives a line 13 of 120 and a line 14 of 0.
        ("120", "0", "6.06", "0.00", "6.06"),
        ("0", "0", "0.00", "0.00", "0.00"),
        # Two ties on one return: 5.05% x 50 = 2.525, up to 2.53, and 11.16% x 37.50 = 4.185, up
        # to 4.19. The sum takes the rounded lines: 2.53 + 4.19 = 6.72, not the unrounded
        # 2.525 + 4.185 = 6.71.
        ("50", "37.50", "2.53", "4.19", "6.72"),
    ],
)
def test_line_49_adds_lines_47_and_48(
    schedule_9_line_13: str,
    schedule_9_line_14: str,
    line_47_amount: str,
    line_48_amount: str,
    total: str,
) -> None:
    assert line_47(schedule_9_line_13) == D(line_47_amount)
    assert line_48(schedule_9_line_14) == D(line_48_amount)
    assert line_49(schedule_9_line_13, schedule_9_line_14) == D(total)


@pytest.mark.parametrize(
    ("line_46_amount", "line_49_amount", "line_50"),
    [
        # Return N: 794.72 + 155.18.
        ("794.72", "155.18", "949.90"),
        # No donations: line 50 is line 46, as for Returns A to M.
        ("867.62", "0.00", "867.62"),
        ("0", "155.18", "155.18"),
        ("0", "0", "0"),
        ("0.01", "0.01", "0.02"),
    ],
)
def test_line_50_is_line_46_plus_line_49(
    line_46_amount: str, line_49_amount: str, line_50: str
) -> None:
    result = Sum((LINE_46, LINE_49), LINE_50).compute(
        (Artifact(LINE_46, D(line_46_amount)), Artifact(LINE_49, D(line_49_amount)))
    )

    assert result.outputs == (Artifact(LINE_50, D(line_50)),)


@pytest.mark.parametrize(
    ("line_12", "line_13", "line_14", "line_47_amount", "line_48_amount", "line_58969"),
    [
        # The worked example: a Schedule 9 line 12 of 1,500 gives a line 13 of 200 and a line 14
        # of 1,300.
        ("1500", "200", "1300", "10.10", "145.08", "155.18"),
        # A line 12 of exactly 200: all at the first tier.
        ("200", "200", "0", "10.10", "0.00", "10.10"),
        # A line 12 under 200.
        ("120", "120", "0", "6.06", "0.00", "6.06"),
        ("0", "0", "0", "0.00", "0.00", "0.00"),
        # A line 12 of 50,200: line 14 is 50,000 and 11.16% of it is 5,580.00.
        ("50200", "200", "50000", "10.10", "5580.00", "5590.10"),
    ],
)
def test_the_three_lines_from_schedule_9_line_12(
    line_12: str,
    line_13: str,
    line_14: str,
    line_47_amount: str,
    line_48_amount: str,
    line_58969: str,
) -> None:
    # Schedule 9 line 13 is the lesser of line 12 and $200 and line 14 is line 12 less line 13;
    # ON428 reads both, so a larger line 12 moves only the 11.16% tier.
    known = {
        SCHEDULE_9_LINE_12: D(line_12),
        FIRST_TIER_MAXIMUM: D("200"),
    }
    first_tier = LesserOf((SCHEDULE_9_LINE_12, FIRST_TIER_MAXIMUM), SCHEDULE_9_LINE_13).compute(
        tuple(Artifact(k, v) for k, v in known.items())
    )
    (line_13_artifact,) = first_tier.outputs
    over = Subtract(SCHEDULE_9_LINE_12, SCHEDULE_9_LINE_13, SCHEDULE_9_LINE_14).compute(
        (Artifact(SCHEDULE_9_LINE_12, D(line_12)), line_13_artifact)
    )
    (line_14_artifact,) = over.outputs

    assert line_13_artifact.value == D(line_13)
    assert line_14_artifact.value == D(line_14)
    assert line_47(str(line_13_artifact.value)) == D(line_47_amount)
    assert line_48(str(line_14_artifact.value)) == D(line_48_amount)
    assert line_49(str(line_13_artifact.value), str(line_14_artifact.value)) == D(line_58969)
