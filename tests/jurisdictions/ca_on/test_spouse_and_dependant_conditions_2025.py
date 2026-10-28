"""The 2025 conditions datasets of T1 lines 30300 and 30400 claimed together, against Schedule 5.

Schedule 5 (5000-S5, 2025), line 30400: "If you did not claim an amount on line 30300 of your
return, you may be able to claim the amount for one eligible dependant if, at any time in the year,
you met all the following conditions:", and "You cannot claim this amount if any of the following
applies: The person you want to claim this amount for is your spouse or common-law partner."

The count (`ca/spouse_and_dependant_both_conditions`) is 1 when the spouse or common-law partner
amount (`ca/spouses_claimed`, 1 or more) and the eligible dependant amount
(`ca/eligible_dependants_checked`, 1 or more) are each more than 0, two parts of one test each (the
parts must both hold), and 0 otherwise. The refused conditions
(`ca/spouse_and_dependant_both_refused`) refuse a count of 1. The schedule prints no refusal; it is
the guard of this check. The two counts together are tested with made-up kinds.
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.errors import InputOutOfRangeError
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
SCHEDULE_5_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s5/5000-s5-25e.txt"

BOTH_FAMILY = "ca/spouse_and_dependant_both_conditions"
REFUSED_FAMILY = "ca/spouse_and_dependant_both_refused"

BOTH_TEXT = "line 30300 and line 30400 are both more than 0"
REFUSED_TEXT = (
    "line 30300 and line 30400 are both claimed, but line 30400 applies only if you did not claim "
    "an amount on line 30300 of your return"
)

# Made up for this test and not registered: the spouse count, the dependant count, the count of
# both and its checked count.
SPOUSES = ArtifactKind("ex/spouses_claimed", int)
DEPENDANTS = ArtifactKind("ex/eligible_dependants_checked", int)
BOTH = ArtifactKind("ex/spouse_and_dependant_both", int)
BOTH_CHECKED = ArtifactKind("ex/spouse_and_dependant_both_checked", int)


def _more_than_0(position: int) -> ConditionPart:
    """The part that the count at `position` is more than 0."""
    return ConditionPart((ConditionTest("count", position, "more_than", D("0"), None),))


def both(spouses: int, dependants: int) -> int:
    """The count of the spouse amount and the eligible dependant amount both above 0."""
    capability = CountByConditions(
        SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS), (SPOUSES, DEPENDANTS), (), BOTH
    )
    (count,) = capability.compute(
        (Artifact(SPOUSES, spouses), Artifact(DEPENDANTS, dependants))
    ).outputs
    return int(count.value)


def both_checked(spouses: int, dependants: int) -> int:
    """The checked count: the count of both, then the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(
        SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS), (SPOUSES, DEPENDANTS), (), BOTH
    )
    refused = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), BOTH, BOTH_CHECKED
    )
    (count,) = counted.compute(
        (Artifact(SPOUSES, spouses), Artifact(DEPENDANTS, dependants))
    ).outputs
    (checked,) = refused.compute((count,)).outputs
    return int(checked.value)


def test_2025_the_both_condition_is_the_spouse_and_the_dependant_each_more_than_0() -> None:
    data = SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1, (Condition(BOTH_TEXT, (_more_than_0(1), _more_than_0(2))),)
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_both_count_is_not_rounded_and_cites_schedule_5() -> None:
    data = SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert SCHEDULE_5_TXT in data.sources


def test_2025_the_refusal_refuses_a_count_of_1_at_position_1_and_nothing_else() -> None:
    data = SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                REFUSED_TEXT,
                (ConditionPart((ConditionTest("count", 1, "equal_to", D("1"), None),)),),
            ),
        ),
    )
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    assert data.rounding == NO_ROUNDING
    assert SCHEDULE_5_TXT in data.sources


@pytest.mark.parametrize(
    ("spouses", "dependants", "count"),
    [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (1, 1, 1),
        (2, 1, 1),
    ],
)
def test_the_count_is_1_only_when_the_spouse_and_the_dependant_are_both_claimed(
    spouses: int, dependants: int, count: int
) -> None:
    assert both(spouses, dependants) == count


@pytest.mark.parametrize(("spouses", "dependants"), [(0, 0), (1, 0), (0, 1)])
def test_a_spouse_alone_or_a_dependant_alone_or_neither_is_not_refused(
    spouses: int, dependants: int
) -> None:
    assert both_checked(spouses, dependants) == 0


@pytest.mark.parametrize(("spouses", "dependants"), [(1, 1), (2, 1)])
def test_both_claimed_is_refused_naming_the_condition_text(spouses: int, dependants: int) -> None:
    message = f"{BOTH.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        both_checked(spouses, dependants)
