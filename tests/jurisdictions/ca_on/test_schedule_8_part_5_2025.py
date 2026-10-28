"""The 2025 Schedule 8 Part 5 conditions, multiplier and rate, checked against CRA's 5000-S8.

2025 Schedule 8 (form 5000-S8), Part 5 "Contributions on self-employment income and other earnings
when you also have employment income": "If the amount from line 20 of Part 3 is negative and line
23 of Part 3 is positive, complete lines 8 and 9. If not, enter "0" on line 9 and continue at line
10."; "Line 8: Enter the amount from line 20 of Part 3 as a positive amount."; "Line 9: Enter
whichever is less: amount from line 23 of Part 3 or line 8."; "If the amount from line 20 of Part
3 is positive and line 23 of Part 3 is negative, complete lines 14 and 15. If not, enter "0" on
line 15 and continue at line 16."; "Line 14: Enter the amount from line 23 of Part 3 as a positive
amount."; "Line 15: Enter whichever is less: amount from line 20 of Part 3 or line 14."; "Line 20:
Amount from line 10 multiplied by 16.80672 ="; "If the amount from line 33 is more than line 17,
complete lines 34 to 42. If not, enter "0" on line 42 and continue at line 43."; "Line 35: Amount
from line 16 divided by 4% =".

One conditions dataset per count, each copying the form's condition in its words, with the count 1
when it holds and 0 otherwise. "Line 20 of Part 3 is negative" is read as line 8 (line 20 as a
positive amount) being more than 0, and "line 20 of Part 3 is positive and line 23 of Part 3 is
negative" as line 20 and line 14 (line 23 as a positive amount) each being more than 0, which are
the same conditions and need no count of their own; "more than line 17" is a test of an amount
against another amount. The counts are not the amount of a line, so nothing is rounded.

16.80672 is above one, which the `rate` kind refuses, so line 20's multiplier is a `fraction`
dataset, 1,680,672 over 100,000, kept as given (it is 1 / 0.0595 to five decimals, so line 20 for a
line 10 of 3,361.75 is 56,499.99 and not 56,500.00). Line 35's 4% is a `rate` dataset. Lines 20 and
35 are dollars-and-cents boxes, so each rounds half-up to the cent, as the form states no rounding
rule.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.divided_by_rate import DividedByRate

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
S8_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

LINE_9 = "ca/cpp_part_5_line_20_negative_line_23_positive_conditions"
LINE_15 = "ca/cpp_part_5_line_20_positive_line_23_negative_conditions"
LINE_42 = "ca/cpp_part_5_line_33_more_than_line_17_conditions"
MULTIPLIER = "ca/cpp_part_5_line_20_multiplier"
DIVISOR_RATE = "ca/cpp_part_5_line_35_rate"

# Made up for this test and not registered.
AMOUNT_1 = ArtifactKind("ex/amount_1", Decimal)
AMOUNT_2 = ArtifactKind("ex/amount_2", Decimal)
APPLIES = ArtifactKind("ex/applies", int)
LINE_10 = ArtifactKind("ex/line_10", Decimal)
LINE_20 = ArtifactKind("ex/line_20", Decimal)
LINE_16 = ArtifactKind("ex/line_16", Decimal)
LINE_35 = ArtifactKind("ex/line_35", Decimal)


def conditions_dataset(family: str) -> Any:
    return SOURCE.get(family, 2025, CONDITIONS)


def amount_test(position: int, relation: str, than: str) -> ConditionTest:
    return ConditionTest("amount", position, relation, D(than), None)


# --- the datasets, in the form's wording ---------------------------------------------------------


@pytest.mark.parametrize(
    ("family", "text"),
    [
        (LINE_9, "line 20 of Part 3 is negative and line 23 of Part 3 is positive"),
        (LINE_15, "line 20 of Part 3 is positive and line 23 of Part 3 is negative"),
    ],
)
def test_2025_lines_9_and_15_need_two_amounts_that_are_both_more_than_zero(
    family: str, text: str
) -> None:
    data = conditions_dataset(family)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                text,
                (
                    ConditionPart((amount_test(1, "more_than", "0"),)),
                    ConditionPart((amount_test(2, "more_than", "0"),)),
                ),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1, 2})
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_line_34_to_42_apply_when_line_33_is_more_than_line_17() -> None:
    data = conditions_dataset(LINE_42)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "the amount from line 33 is more than line 17",
                (ConditionPart((ConditionTest("amount", 1, "more_than", None, 2),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.values.amount_positions_read == frozenset({1, 2})
    assert data.rounding == NO_ROUNDING


def test_2025_line_20_multiplies_line_10_by_16_80672() -> None:
    data = SOURCE.get(MULTIPLIER, 2025, FRACTION)

    # 16.80672 as 1,680,672 / 100,000, kept as given: more than 1, so a fraction, not a rate.
    assert data.values == Fraction(1680672, 100000)
    # Line 20, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (S8_TEXT,)


def test_2025_line_35_divides_line_16_by_4_percent() -> None:
    data = SOURCE.get(DIVISOR_RATE, 2025, RATE)

    assert data.values == Rate(D("0.04"))
    # Line 35, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (S8_TEXT,)


def test_2025_the_conditions_cite_only_the_schedule_8_text() -> None:
    for family in (LINE_9, LINE_15, LINE_42):
        assert conditions_dataset(family).sources == (S8_TEXT,), family


# --- the datasets run through their capabilities -------------------------------------------------


def applies(family: str, first: str, second: str) -> int:
    capability = CountByConditions(conditions_dataset(family), (), (AMOUNT_1, AMOUNT_2), APPLIES)

    (output,) = capability.compute(
        (Artifact(AMOUNT_1, D(first)), Artifact(AMOUNT_2, D(second)))
    ).outputs

    assert isinstance(output.value, int)
    return output.value


@pytest.mark.parametrize("family", [LINE_9, LINE_15])
@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        # Line 8 (line 20 as a positive amount) and line 23 of Part 3 of Return BN's third case:
        # box 16 of 4,000.00 and box 16A of 400.00 on employment income of 80,000.
        ("34.10", "52.00", 1),
        ("0.01", "0.01", 1),
        # Either "0" or negative switches it off, whichever of the two it is.
        ("0", "52.00", 0),
        ("34.10", "0", 0),
        ("0.00", "0.00", 0),
        ("-1.00", "52.00", 0),
        ("34.10", "-1.00", 0),
        ("-1.00", "-1.00", 0),
    ],
)
def test_lines_9_and_15_need_both_amounts_more_than_zero(
    family: str, first: str, second: str, expected: int
) -> None:
    assert applies(family, first, second) == expected


@pytest.mark.parametrize(
    ("line_33", "line_17", "expected"),
    [
        # Return BN: employment income of 60,000 and self-employment income of 20,000.
        ("80000.00", "71300.00", 1),
        ("71300.01", "71300.00", 1),
        # "More than": equal is not enough.
        ("71300.00", "71300.00", 0),
        ("60000.00", "71300.00", 0),
        ("0", "71300.00", 0),
        ("-5000.00", "71300.00", 0),
    ],
)
def test_lines_34_to_42_apply_only_when_line_33_is_more_than_line_17(
    line_33: str, line_17: str, expected: int
) -> None:
    assert applies(LINE_42, line_33, line_17) == expected


@pytest.mark.parametrize(
    ("line_10", "line_20"),
    [
        # Return BN: employment income of 60,000 with box 16 equal to the required 3,361.75:
        # 3,361.75 x 16.80672 = 56,499.99096 (not 56,500.00), to the cent 56,499.99.
        ("3361.75", "56499.99"),
        # A line 10 of 4,034.10, the most box 16 requires: 4,034.10 x 16.80672 = 67,799.989152, to
        # the cent 67,799.99.
        ("4034.10", "67799.99"),
        ("0", "0"),
        # Rounded half-up to the cent: 0.01 x 16.80672 = 0.1680672 is 0.17.
        ("0.01", "0.17"),
    ],
)
def test_line_20_is_line_10_times_16_80672_to_the_cent(line_10: str, line_20: str) -> None:
    capability = ApplyFraction(SOURCE.get(MULTIPLIER, 2025, FRACTION), LINE_10, LINE_20)

    result = capability.compute((Artifact(LINE_10, D(line_10)),))

    assert result.outputs == (Artifact(LINE_20, D(line_20)),)


@pytest.mark.parametrize(
    ("line_16", "line_35"),
    [
        # 348.00 / 0.04 = 8,700: the second additional contribution required on employment
        # income of 80,000 (4% of 8,700) as line 16.
        ("348.00", "8700.00"),
        ("0", "0"),
        # A cent divided by 4% is 25 cents: the quotient of a whole number of cents is exact.
        ("0.01", "0.25"),
        ("1.01", "25.25"),
    ],
)
def test_line_35_is_line_16_divided_by_4_percent_to_the_cent(line_16: str, line_35: str) -> None:
    capability = DividedByRate(SOURCE.get(DIVISOR_RATE, 2025, RATE), LINE_16, LINE_35)

    result = capability.compute((Artifact(LINE_16, D(line_16)),))

    assert result.outputs == (Artifact(LINE_35, D(line_35)),)
