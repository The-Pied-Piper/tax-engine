"""The 2025 Schedule 8 Part 5 lines 43 to 69 conditions, multiplier and rate, checked against CRA's
5000-S8.

2025 Schedule 8 (form 5000-S8), Part 5 "Contributions on self-employment income and other earnings
when you also have employment income": "Line 43: amount from line 30 multiplied by 9.9% (maximum
$6,712.20) ="; "Line 44: amount from line 30 multiplied by 2% (maximum $1,356.00) ="; "Line 45:
amount from line 42 multiplied by 8% (maximum $792.00) ="; "Line 48: Amount from line 24 of Part 3
(if positive) multiplied by 2 ="; "Line 49: Line 47 minus line 48. If positive, enter the amount (in
dollars and cents) on line 42100 of your return and continue at line 51. If negative, show in
brackets and continue at line 50. ="; "Line 50: Enter the result of the following calculation (in
dollars and cents) on line 44800 of your return: amount from line 49 entered as a positive amount
multiplied by 50% ="; "Line 56: If line 23 of Part 3 and line 54 are both positive, enter
whichever is less. If not, enter "0"." and "If line 23 of Part 3 and line 61 are both positive,
enter whichever is less: Line 63: amount from line 61 or the result of line 23 of Part 3 minus
line 56. If not, enter "0"."

Lines 43 to 45 are the tiers of Part 4 lines 10 to 12 (`ca/cpp_self_employed_base_contribution`,
`..._first_additional_contribution` and `..._second_additional_contribution`, tested in
`test_cpp_self_employment_2025.py`) on lines 30 and 42, so only their use on a negative line 42 is
checked here. Line 48's 2 is above one, which the `rate` kind refuses, so it is a `fraction`
dataset, 2 over 1, as the 138% of the eligible dividend gross-up is 138 over 100. Line 50's 50% is
a `rate` dataset of its own (Part 4 line 15 has the same 50% as its own dataset). Lines 48 and 50
are dollars-and-cents boxes, so each rounds half-up to the cent, as the form states no rounding
rule.

One conditions dataset per count, each copying the form's condition in its words, with the count 1
when it holds and 0 otherwise: "both positive" is two parts, each of one test (the parts must both
hold). The counts are not the amount of a line, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.contribution_tier import TieredContribution
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.contribution_tier import CONTRIBUTION_TIER
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
S8_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

LINE_56 = "ca/cpp_part_5_line_23_and_line_54_positive_conditions"
LINE_63 = "ca/cpp_part_5_line_23_and_line_61_positive_conditions"
MULTIPLIER = "ca/cpp_part_5_line_48_multiplier"
HALF = "ca/cpp_part_5_line_50_rate"
BASE_TIER = "ca/cpp_self_employed_base_contribution"
FIRST_ADDITIONAL_TIER = "ca/cpp_self_employed_first_additional_contribution"
SECOND_ADDITIONAL_TIER = "ca/cpp_self_employed_second_additional_contribution"

# Made up for this test and not registered.
AMOUNT_1 = ArtifactKind("ex/amount_1", Decimal)
AMOUNT_2 = ArtifactKind("ex/amount_2", Decimal)
APPLIES = ArtifactKind("ex/applies", int)
LINE_IN = ArtifactKind("ex/line_in", Decimal)
LINE_OUT = ArtifactKind("ex/line_out", Decimal)


def conditions_dataset(family: str) -> Any:
    return SOURCE.get(family, 2025, CONDITIONS)


def amount_test(position: int, relation: str, than: str) -> ConditionTest:
    return ConditionTest("amount", position, relation, D(than), None)


# --- the datasets, in the form's wording ---------------------------------------------------------


@pytest.mark.parametrize(
    ("family", "text"),
    [
        (LINE_56, "line 23 of Part 3 and line 54 are both positive"),
        (LINE_63, "line 23 of Part 3 and line 61 are both positive"),
    ],
)
def test_2025_lines_56_and_63_need_two_amounts_that_are_both_more_than_zero(
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
    assert data.sources == (S8_TEXT,)


def test_2025_line_48_multiplies_line_24_of_part_3_by_2() -> None:
    data = SOURCE.get(MULTIPLIER, 2025, FRACTION)

    # 2 is more than 1, so a fraction (2 / 1), not a rate.
    assert data.values == Fraction(2, 1)
    # Line 48, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (S8_TEXT,)


def test_2025_line_50_multiplies_line_49_as_a_positive_amount_by_50_percent() -> None:
    data = SOURCE.get(HALF, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    # Line 50, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (S8_TEXT,)


# --- the datasets run through their capabilities -------------------------------------------------


def applies(family: str, first: str, second: str) -> int:
    capability = CountByConditions(conditions_dataset(family), (), (AMOUNT_1, AMOUNT_2), APPLIES)

    (output,) = capability.compute(
        (Artifact(AMOUNT_1, D(first)), Artifact(AMOUNT_2, D(second)))
    ).outputs

    assert isinstance(output.value, int)
    return output.value


@pytest.mark.parametrize("family", [LINE_56, LINE_63])
@pytest.mark.parametrize(
    ("line_23", "other_line", "expected"),
    [
        # Line 23 of Part 3 (52.00) and line 54 (or 61) both more than 0.
        ("52.00", "34.10", 1),
        ("0.01", "0.01", 1),
        # Either "0" or negative switches it off, whichever of the two it is.
        ("0", "34.10", 0),
        ("52.00", "0", 0),
        ("0.00", "0.00", 0),
        ("-48.00", "34.10", 0),
        ("52.00", "-1.00", 0),
        ("-1.00", "-1.00", 0),
    ],
)
def test_lines_56_and_63_need_both_amounts_more_than_zero(
    family: str, line_23: str, other_line: str, expected: int
) -> None:
    assert applies(family, line_23, other_line) == expected


@pytest.mark.parametrize(
    ("line_24", "line_48"),
    [
        # Return BN as filed: line 24 of Part 3 is 138.25, so line 48 is 276.50.
        ("138.25", "276.50"),
        ("0", "0"),
        ("0.01", "0.02"),
    ],
)
def test_line_48_is_line_24_of_part_3_if_positive_times_2_to_the_cent(
    line_24: str, line_48: str
) -> None:
    capability = ApplyFraction(SOURCE.get(MULTIPLIER, 2025, FRACTION), LINE_IN, LINE_OUT)

    result = capability.compute((Artifact(LINE_IN, D(line_24)),))

    assert result.outputs == (Artifact(LINE_OUT, D(line_48)),)


@pytest.mark.parametrize(
    ("line_49_positive", "line_50"),
    [
        # Return BN as filed: line 49 is -276.50, entered as a positive 276.50, times 50%.
        ("276.50", "138.25"),
        ("0", "0.00"),
        # Half-up to the cent: 0.01 x 50% is 0.005, a tie, up to 0.01; 0.03 x 50% is 0.015, up to
        # 0.02.
        ("0.01", "0.01"),
        ("0.03", "0.02"),
    ],
)
def test_line_50_is_line_49_as_a_positive_amount_times_50_percent_to_the_cent(
    line_49_positive: str, line_50: str
) -> None:
    capability = ApplyRate(SOURCE.get(HALF, 2025, RATE), LINE_IN, LINE_OUT)

    result = capability.compute((Artifact(LINE_IN, D(line_49_positive)),))

    assert result.outputs == (Artifact(LINE_OUT, D(line_50)),)


@pytest.mark.parametrize(
    ("family", "earnings", "contribution"),
    [
        # Return BN's ticket example: line 30 is 11,300.01 and line 42 is 8,699.99.
        (BASE_TIER, "11300.01", "1118.70"),
        (FIRST_ADDITIONAL_TIER, "11300.01", "226.00"),
        (SECOND_ADDITIONAL_TIER, "8699.99", "696.00"),
        # Line 42 prints no floor, so it is negative for a loss with employment income above
        # $71,300: a negative amount is below the band, so line 45 is 0, not a negative amount.
        (SECOND_ADDITIONAL_TIER, "-5000", "0"),
        (SECOND_ADDITIONAL_TIER, "-0.01", "0"),
        (SECOND_ADDITIONAL_TIER, "0", "0"),
        # Line 30 is never negative (line 30 floors at 0), and 0 contributes nothing.
        (BASE_TIER, "0", "0"),
        (FIRST_ADDITIONAL_TIER, "0", "0"),
    ],
)
def test_lines_43_to_45_contribute_on_the_earnings_of_lines_30_and_42(
    family: str, earnings: str, contribution: str
) -> None:
    capability = TieredContribution(SOURCE.get(family, 2025, CONTRIBUTION_TIER), LINE_IN, LINE_OUT)

    result = capability.compute((Artifact(LINE_IN, D(earnings)),))

    assert result.outputs == (Artifact(LINE_OUT, D(contribution)),)
