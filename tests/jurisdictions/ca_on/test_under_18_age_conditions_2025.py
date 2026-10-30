"""The 2025 conditions datasets of a filer entered as under 18 together with another age, against
Form ON428 and Worksheet ON428.

Worksheet ON428 line 58440: "Complete the following calculation if you were under 18 years of age
on December 31, 2025." and Form ON428 line 10: "Age amount (if you were born in 1960 or earlier)".
The federal worksheet for line 45200 asks "You were 18 years of age or older at the end of 2025".
Under 18 excludes both of the others: born in 1960 or earlier means 65 or older, and under 18 and 18
or older exclude each other by definition.

Two pairs, one for born in 1960 or earlier
(`ca/under_18_and_born_in_1960_or_earlier_conditions`) and one for 18 or older
(`ca/under_18_and_aged_18_or_older_conditions`). Each count is 1 when
`ca/under_18_on_december_31` and the other count are each more than 0, two parts of one test each
(the parts must both hold), and 0 otherwise. The refused conditions (`..._refused`) refuse a count
of 1. The forms print no refusal; it is the guard of this check. The counts together are tested with
made-up kinds.
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import InputOutOfRangeError
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
BASE_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg"
WORKSHEET_TXT = f"{BASE_URL}/5006-d/5006-d-25e.txt"
FORM_TXT = f"{BASE_URL}/5006-c/5006-c-25e.txt"
GUIDE_TXT = f"{BASE_URL}/5000-g/5000-g-25e.txt"

BORN_FAMILY = "ca/under_18_and_born_in_1960_or_earlier_conditions"
BORN_REFUSED_FAMILY = "ca/under_18_and_born_in_1960_or_earlier_refused"
AGED_FAMILY = "ca/under_18_and_aged_18_or_older_conditions"
AGED_REFUSED_FAMILY = "ca/under_18_and_aged_18_or_older_refused"

BORN_TEXT = (
    "under 18 years of age on December 31, 2025 and born in 1960 or earlier are both entered"
)
BORN_REFUSED_TEXT = (
    "under 18 years of age on December 31, 2025 and born in 1960 or earlier are both entered, but "
    "a filer born in 1960 or earlier is 65 or older"
)
AGED_TEXT = (
    "under 18 years of age on December 31, 2025 and 18 years of age or older at the end of 2025 "
    "are both entered"
)
AGED_REFUSED_TEXT = (
    "under 18 years of age on December 31, 2025 and 18 years of age or older at the end of 2025 "
    "are both entered, but a filer cannot be both"
)

# Made up for this test and not registered: the under 18 count, the two other ages, and the count of
# each pair and its checked count.
UNDER_18 = ArtifactKind("ex/under_18_on_december_31", int)
BORN = ArtifactKind("ex/born_in_1960_or_earlier", int)
AGED = ArtifactKind("ex/aged_18_or_older_at_end_of_2025", int)
UNDER_18_AND_BORN = ArtifactKind("ex/under_18_and_born_in_1960_or_earlier", int)
UNDER_18_AND_BORN_CHECKED = ArtifactKind("ex/under_18_and_born_in_1960_or_earlier_checked", int)
UNDER_18_AND_AGED = ArtifactKind("ex/under_18_and_aged_18_or_older", int)
UNDER_18_AND_AGED_CHECKED = ArtifactKind("ex/under_18_and_aged_18_or_older_checked", int)


def _more_than_0(position: int) -> ConditionPart:
    """The part that the count at `position` is more than 0."""
    return ConditionPart((ConditionTest("count", position, "more_than", D("0"), None),))


def _equal_to_1(position: int) -> ConditionPart:
    """The part that the count at `position` is 1."""
    return ConditionPart((ConditionTest("count", position, "equal_to", D("1"), None),))


def pair_count(
    family: str, other: ArtifactKind[int], count: ArtifactKind[int], under_18: int, other_count: int
) -> int:
    """The count of under 18 entered together with `other`."""
    capability = CountByConditions(
        SOURCE.get(family, 2025, CONDITIONS), (UNDER_18, other), (), count
    )
    (result,) = capability.compute(
        (Artifact(UNDER_18, under_18), Artifact(other, other_count))
    ).outputs
    return int(result.value)


def pair_checked(
    family: str,
    refused_family: str,
    other: ArtifactKind[int],
    count: ArtifactKind[int],
    checked: ArtifactKind[int],
    under_18: int,
    other_count: int,
) -> int:
    """The checked count: the count, then the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(SOURCE.get(family, 2025, CONDITIONS), (UNDER_18, other), (), count)
    refused = CountRefusedByConditions(SOURCE.get(refused_family, 2025, CONDITIONS), count, checked)
    (result,) = counted.compute(
        (Artifact(UNDER_18, under_18), Artifact(other, other_count))
    ).outputs
    (done,) = refused.compute((result,)).outputs
    return int(done.value)


def test_2025_the_born_condition_is_both_counts_above_0() -> None:
    data = SOURCE.get(BORN_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1, (Condition(BORN_TEXT, (_more_than_0(1), _more_than_0(2))),)
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_aged_condition_is_both_counts_above_0() -> None:
    data = SOURCE.get(AGED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1, (Condition(AGED_TEXT, (_more_than_0(1), _more_than_0(2))),)
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_conditions_are_not_rounded_and_cite_the_worksheet() -> None:
    for family in (BORN_FAMILY, AGED_FAMILY, BORN_REFUSED_FAMILY, AGED_REFUSED_FAMILY):
        data = SOURCE.get(family, 2025, CONDITIONS)

        assert data.rounding == NO_ROUNDING, family
        assert WORKSHEET_TXT in data.sources, family
    assert FORM_TXT in SOURCE.get(BORN_FAMILY, 2025, CONDITIONS).sources
    assert GUIDE_TXT in SOURCE.get(AGED_FAMILY, 2025, CONDITIONS).sources


def test_2025_the_born_refusal_refuses_a_count_of_1_at_position_1_and_nothing_else() -> None:
    data = SOURCE.get(BORN_REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(1, (Condition(BORN_REFUSED_TEXT, (_equal_to_1(1),)),))
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_aged_refusal_refuses_a_count_of_1_at_position_1_and_nothing_else() -> None:
    data = SOURCE.get(AGED_REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(1, (Condition(AGED_REFUSED_TEXT, (_equal_to_1(1),)),))
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()


@pytest.mark.parametrize(
    ("under_18", "other", "count"),
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 1), (2, 1, 1)],
)
def test_the_born_count_is_1_only_when_under_18_and_born_in_1960_are_both_entered(
    under_18: int, other: int, count: int
) -> None:
    assert pair_count(BORN_FAMILY, BORN, UNDER_18_AND_BORN, under_18, other) == count


@pytest.mark.parametrize(
    ("under_18", "other", "count"),
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 1), (2, 1, 1)],
)
def test_the_aged_count_is_1_only_when_under_18_and_18_or_older_are_both_entered(
    under_18: int, other: int, count: int
) -> None:
    assert pair_count(AGED_FAMILY, AGED, UNDER_18_AND_AGED, under_18, other) == count


@pytest.mark.parametrize(("under_18", "other"), [(0, 0), (1, 0), (0, 1)])
def test_the_born_pair_is_not_refused_unless_both_are_entered(under_18: int, other: int) -> None:
    checked = pair_checked(
        BORN_FAMILY,
        BORN_REFUSED_FAMILY,
        BORN,
        UNDER_18_AND_BORN,
        UNDER_18_AND_BORN_CHECKED,
        under_18,
        other,
    )

    assert checked == 0


@pytest.mark.parametrize(("under_18", "other"), [(0, 0), (1, 0), (0, 1)])
def test_the_aged_pair_is_not_refused_unless_both_are_entered(under_18: int, other: int) -> None:
    checked = pair_checked(
        AGED_FAMILY,
        AGED_REFUSED_FAMILY,
        AGED,
        UNDER_18_AND_AGED,
        UNDER_18_AND_AGED_CHECKED,
        under_18,
        other,
    )

    assert checked == 0


def test_under_18_with_born_in_1960_or_earlier_is_refused_naming_both() -> None:
    message = f"{UNDER_18_AND_BORN.identifier} 1 is refused: {BORN_REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        pair_checked(
            BORN_FAMILY,
            BORN_REFUSED_FAMILY,
            BORN,
            UNDER_18_AND_BORN,
            UNDER_18_AND_BORN_CHECKED,
            1,
            1,
        )


def test_under_18_with_18_or_older_is_refused_naming_both() -> None:
    message = f"{UNDER_18_AND_AGED.identifier} 1 is refused: {AGED_REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        pair_checked(
            AGED_FAMILY,
            AGED_REFUSED_FAMILY,
            AGED,
            UNDER_18_AND_AGED,
            UNDER_18_AND_AGED_CHECKED,
            1,
            1,
        )
