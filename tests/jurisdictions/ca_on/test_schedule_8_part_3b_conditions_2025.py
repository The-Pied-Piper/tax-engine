"""The 2025 Schedule 8 Part 3a and Part 3b conditions and the form's "0", checked against CRA's
Schedule 8 (form 5000-S8).

2025 Schedule 8 (form 5000-S8), Part 3 (continued): "If your earnings subject to contributions are
from employment income only and line 24 is: - positive, complete Part 3a below - "0", complete
Part 3b below - negative, ... complete Part 3b below." Part 3b: "Line 30: If line 16 is positive
or "0", enter the amount from line 15 at line 30 and line 36, and continue at line 37. If not,
enter the amount from line 14 and continue at line 31.", "If line 16 is negative and line 19 is
positive, enter whichever is less: Line 32: amount from line 19 or line 31. If not, enter "0".",
"Line 35: If line 23 and line 33 are both positive, enter whichever is less. If not, enter "0".",
the instruction printed under the misprinted heading "Line 36" (it is line 37) "If line 19 is
positive or "0", enter the amount from line 18 at line 37 and line 43, and continue at line 44.
If not, enter the amount from line 17 and continue at line 38.", "If line 16 is positive, enter
whichever is less: Line 39: amount from line 16 or line 38. If not, enter "0".", "Line 42: If
line 23 and line 40 are both positive, enter whichever is less: amount from line 40 or the result
of line 23 minus line 35. If not, enter "0".", "Line 44: If line 23 is positive or "0", enter the
amount from line 22 on line 44 and line 47, and continue at line 48. If not, enter the amount from
line 21 and continue at line 45." and "If line 20 is positive, enter whichever is less: Line 46:
amount from line 20 or line 45. If not, enter "0".".

One conditions dataset per count, each copying the form's condition in its words, with the count 1
when it holds and 0 otherwise. "Positive or "0"" is one part of two tests, either of which holds
(more than 0, equal to 0); "both positive" is two parts, each of one test (the parts must both
hold); "line 16 is negative" is the line 30 count (positive or "0") being 0, read as a count.
The counts are not the amount of a line, so nothing is rounded. The form's "0" of "If not, enter
"0"" is the `credit` kind `ca/schedule_8_zero` (claimed whole, as the OAS benefits base amount
is), a dollars-and-cents box, so it rounds half-up to the cent as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
S8_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"
ZERO_FAMILY = "ca/schedule_8_zero"

LINE_24 = "ca/cpp_line_24_positive_conditions"
LINE_16_NOT_NEGATIVE = "ca/cpp_line_16_not_negative_conditions"
LINE_19_NOT_NEGATIVE = "ca/cpp_line_19_not_negative_conditions"
LINE_23_NOT_NEGATIVE = "ca/cpp_line_23_not_negative_conditions"
LINE_32 = "ca/cpp_line_16_negative_line_19_positive_conditions"
LINE_35 = "ca/cpp_line_23_and_line_33_positive_conditions"
LINE_39 = "ca/cpp_line_16_positive_conditions"
LINE_42 = "ca/cpp_line_23_and_line_40_positive_conditions"
LINE_46 = "ca/cpp_line_20_positive_conditions"

# Made up for this test and not registered.
AMOUNT_1 = ArtifactKind("ex/amount_1", Decimal)
AMOUNT_2 = ArtifactKind("ex/amount_2", Decimal)
COUNT_1 = ArtifactKind("ex/count_1", int)
APPLIES = ArtifactKind("ex/applies", int)
ZERO = ArtifactKind("ex/zero", Decimal)


def conditions_dataset(family: str) -> Any:
    return SOURCE.get(family, 2025, CONDITIONS)


def amount_test(position: int, relation: str, than: str) -> ConditionTest:
    return ConditionTest("amount", position, relation, D(than), None)


def positive_or_zero(text: str) -> ConditionList:
    return ConditionList(
        1,
        (
            Condition(
                text,
                (
                    ConditionPart(
                        (amount_test(1, "more_than", "0"), amount_test(1, "equal_to", "0"))
                    ),
                ),
            ),
        ),
    )


def positive(text: str) -> ConditionList:
    part = ConditionPart((amount_test(1, "more_than", "0"),))
    return ConditionList(1, (Condition(text, (part,)),))


def both_positive(text: str) -> ConditionList:
    return ConditionList(
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


# --- the datasets, in the form's wording ---------------------------------------------------------


def test_2025_line_24_positive_completes_part_3a() -> None:
    data = conditions_dataset(LINE_24)

    assert data.values == positive("positive, complete Part 3a below")
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("family", "text"),
    [
        (LINE_16_NOT_NEGATIVE, 'line 16 is positive or "0"'),
        (LINE_19_NOT_NEGATIVE, 'line 19 is positive or "0"'),
        (LINE_23_NOT_NEGATIVE, 'line 23 is positive or "0"'),
    ],
)
def test_2025_lines_30_37_and_44_read_a_line_that_is_positive_or_zero(
    family: str, text: str
) -> None:
    data = conditions_dataset(family)

    assert data.values == positive_or_zero(text)
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    assert data.rounding == NO_ROUNDING


def test_2025_line_32_reads_line_16_negative_as_the_line_30_count_being_zero() -> None:
    data = conditions_dataset(LINE_32)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "line 16 is negative and line 19 is positive",
                (
                    ConditionPart((ConditionTest("count", 1, "equal_to", D(0), None),)),
                    ConditionPart((amount_test(1, "more_than", "0"),)),
                ),
            ),
        ),
    )
    # The count is the line 30 count (line 16 positive or "0"), 0 when line 16 is negative; the
    # amount is line 19.
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset({1})
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("family", "text"),
    [
        (LINE_35, "line 23 and line 33 are both positive"),
        (LINE_42, "line 23 and line 40 are both positive"),
    ],
)
def test_2025_lines_35_and_42_read_two_amounts_that_must_both_be_positive(
    family: str, text: str
) -> None:
    data = conditions_dataset(family)

    assert data.values == both_positive(text)
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1, 2})
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("family", "text"),
    [
        (LINE_39, "line 16 is positive"),
        (LINE_46, "line 20 is positive"),
    ],
)
def test_2025_lines_39_and_46_read_one_line_that_is_positive(family: str, text: str) -> None:
    data = conditions_dataset(family)

    assert data.values == positive(text)
    assert data.values.amount_positions_read == frozenset({1})
    assert data.rounding == NO_ROUNDING


def test_2025_the_zero_is_the_forms_enter_0_claimed_whole() -> None:
    data = SOURCE.get(ZERO_FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("0"))
    # A dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_datasets_cite_only_the_schedule_8_text() -> None:
    for family in (
        LINE_24,
        LINE_16_NOT_NEGATIVE,
        LINE_19_NOT_NEGATIVE,
        LINE_23_NOT_NEGATIVE,
        LINE_32,
        LINE_35,
        LINE_39,
        LINE_42,
        LINE_46,
    ):
        assert conditions_dataset(family).sources == (S8_TEXT,), family
    assert SOURCE.get(ZERO_FAMILY, 2025, CREDIT).sources == (S8_TEXT,)


# --- the datasets run through their capabilities -------------------------------------------------


def applies(family: str, amounts: tuple[str, ...], counts: tuple[int, ...] = ()) -> int:
    amount_kinds = (AMOUNT_1, AMOUNT_2)[: len(amounts)]
    count_kinds = (COUNT_1,)[: len(counts)]
    capability = CountByConditions(conditions_dataset(family), count_kinds, amount_kinds, APPLIES)
    inputs = tuple(
        Artifact(kind, D(value)) for kind, value in zip(amount_kinds, amounts, strict=True)
    ) + tuple(Artifact(kind, value) for kind, value in zip(count_kinds, counts, strict=True))

    (output,) = capability.compute(inputs).outputs

    assert isinstance(output.value, int)
    return output.value


@pytest.mark.parametrize(
    ("line_24", "expected"),
    [
        # Return BN as filed: 138.25 over the required contributions.
        ("138.25", 1),
        ("0.01", 1),
        # "0" and negative complete Part 3b.
        ("0", 0),
        ("0.00", 0),
        ("-0.01", 0),
        ("-61.75", 0),
    ],
)
def test_part_3a_applies_only_when_line_24_is_positive(line_24: str, expected: int) -> None:
    assert applies(LINE_24, (line_24,)) == expected


@pytest.mark.parametrize(
    "family", [LINE_16_NOT_NEGATIVE, LINE_19_NOT_NEGATIVE, LINE_23_NOT_NEGATIVE]
)
@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("115.02", 1),
        ("0.01", 1),
        ("0", 1),
        ("0.00", 1),
        ("-0.01", 0),
        ("-51.37", 0),
    ],
)
def test_a_line_that_is_positive_or_zero_counts_1_and_a_negative_one_counts_0(
    family: str, line: str, expected: int
) -> None:
    assert applies(family, (line,)) == expected


@pytest.mark.parametrize(
    ("line_16_not_negative", "line_19", "expected"),
    [
        # Line 16 negative (the line 30 count is 0) and line 19 positive.
        (0, "0.01", 1),
        (0, "10.38", 1),
        # Line 19 is "0" or negative.
        (0, "0", 0),
        (0, "-10.38", 0),
        # Line 16 positive or "0".
        (1, "10.38", 0),
        (1, "-10.38", 0),
        (1, "0", 0),
    ],
)
def test_line_32_takes_the_lesser_only_when_line_16_is_negative_and_line_19_positive(
    line_16_not_negative: int, line_19: str, expected: int
) -> None:
    assert applies(LINE_32, (line_19,), (line_16_not_negative,)) == expected


@pytest.mark.parametrize("family", [LINE_35, LINE_42])
@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        ("5.00", "499.16", 1),
        ("0.01", "0.01", 1),
        # Either "0" or negative switches it off, whichever of the two it is.
        ("0", "499.16", 0),
        ("5.00", "0", 0),
        ("-1.00", "499.16", 0),
        ("5.00", "-1.00", 0),
        ("0", "0", 0),
        ("-1.00", "-1.00", 0),
    ],
)
def test_lines_35_and_42_need_both_lines_positive(
    family: str, first: str, second: str, expected: int
) -> None:
    assert applies(family, (first, second)) == expected


@pytest.mark.parametrize("family", [LINE_39, LINE_46])
@pytest.mark.parametrize(
    ("line", "expected"),
    [("54.83", 1), ("0.01", 1), ("0", 0), ("0.00", 0), ("-0.01", 0), ("-61.75", 0)],
)
def test_lines_39_and_46_need_their_line_positive(family: str, line: str, expected: int) -> None:
    assert applies(family, (line,)) == expected


def test_the_zero_is_claimed_whole() -> None:
    capability = CreditAmount(SOURCE.get(ZERO_FAMILY, 2025, CREDIT), ZERO)

    result = capability.compute(())

    assert result.outputs == (Artifact(ZERO, D("0")),)
