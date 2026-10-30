"""The 2025 conditions datasets of Schedule 8 Parts 4 and 5 completed together, against Schedule 8.

Schedule 8 (5000-S8, 2025), "Parts you have to complete": "Part 4 - Complete this part if you are
reporting only self-employment income or other earnings you are electing to pay CPP contributions
on. If not, leave this part blank.", and "Part 5 - Complete this part if you are reporting both:"
with "employment income (complete Part 3 first)" and "self-employment income or other earnings that
you are electing to pay CPP contributions on".

The two parts are alternatives: Part 4 for a filer reporting self-employment income only, Part 5 for
a filer reporting employment income as well. The count (`ca/cpp_part_4_and_part_5_both_conditions`)
is 1 when Part 4 completed (`ca/cpp_part_4_completed_checked`, 1 or more) and Part 5 completed
(`ca/cpp_part_5_completed_checked`, 1 or more) are each more than 0, two parts of one test each (the
parts must both hold), and 0 otherwise. The refused conditions
(`ca/cpp_part_4_and_part_5_both_refused`) refuse a count of 1. The form prints no refusal; it is the
guard of this check. The two counts together are tested with made-up kinds.
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
SCHEDULE_8_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"

BOTH_FAMILY = "ca/cpp_part_4_and_part_5_both_conditions"
REFUSED_FAMILY = "ca/cpp_part_4_and_part_5_both_refused"

BOTH_TEXT = "Part 4 and Part 5 are both completed"
REFUSED_TEXT = (
    "Part 4 and Part 5 of Schedule 8 are both completed, but Part 4 is for self-employment income "
    "only and Part 5 for employment income as well"
)

# Made up for this test and not registered: the Part 4 count, the Part 5 count, the count of both
# and its checked count.
PART_4 = ArtifactKind("ex/cpp_part_4_completed_checked", int)
PART_5 = ArtifactKind("ex/cpp_part_5_completed_checked", int)
BOTH = ArtifactKind("ex/cpp_part_4_and_part_5_both", int)
BOTH_CHECKED = ArtifactKind("ex/cpp_part_4_and_part_5_both_checked", int)


def _more_than_0(position: int) -> ConditionPart:
    """The part that the count at `position` is more than 0."""
    return ConditionPart((ConditionTest("count", position, "more_than", D("0"), None),))


def both(part_4: int, part_5: int) -> int:
    """The count of Part 4 and Part 5 both completed, each above 0."""
    capability = CountByConditions(
        SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS), (PART_4, PART_5), (), BOTH
    )
    (count,) = capability.compute((Artifact(PART_4, part_4), Artifact(PART_5, part_5))).outputs
    return int(count.value)


def both_checked(part_4: int, part_5: int) -> int:
    """The checked count: the count of both, then the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(
        SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS), (PART_4, PART_5), (), BOTH
    )
    refused = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), BOTH, BOTH_CHECKED
    )
    (count,) = counted.compute((Artifact(PART_4, part_4), Artifact(PART_5, part_5))).outputs
    (checked,) = refused.compute((count,)).outputs
    return int(checked.value)


def test_2025_the_both_condition_is_part_4_and_part_5_each_more_than_0() -> None:
    data = SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1, (Condition(BOTH_TEXT, (_more_than_0(1), _more_than_0(2))),)
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_both_count_is_not_rounded_and_cites_schedule_8() -> None:
    data = SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert SCHEDULE_8_TXT in data.sources


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
    assert SCHEDULE_8_TXT in data.sources


@pytest.mark.parametrize(
    ("part_4", "part_5", "count"),
    [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (1, 1, 1),
        (2, 1, 1),
    ],
)
def test_the_count_is_1_only_when_part_4_and_part_5_are_both_completed(
    part_4: int, part_5: int, count: int
) -> None:
    assert both(part_4, part_5) == count


@pytest.mark.parametrize(("part_4", "part_5"), [(0, 0), (1, 0), (0, 1)])
def test_part_4_alone_or_part_5_alone_or_neither_is_not_refused(part_4: int, part_5: int) -> None:
    assert both_checked(part_4, part_5) == 0


@pytest.mark.parametrize(("part_4", "part_5"), [(1, 1), (2, 1)])
def test_both_completed_is_refused_naming_the_condition_text(part_4: int, part_5: int) -> None:
    message = f"{BOTH.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        both_checked(part_4, part_5)
