"""The 2025 conditions datasets of Schedule 8 Part 4 completed with employment earnings, against
Schedule 8.

Schedule 8 (5000-S8, 2025), "Part 4 - Contributions on self-employment income and other earnings
only (no employment income)": Part 4 is for a filer with no employment income. Part 3 line 1 ("CPP
pensionable earnings outside Quebec from T4 slips",
`ca/t4_cpp_pensionable_earnings_outside_quebec`) is the employment input that Part 5 and Part 3
use. The count
(`ca/cpp_part_4_with_employment_earnings_conditions`) is 1 when Part 4 completed
(`ca/cpp_part_4_completed_checked`, 1 or more) and the T4 pensionable earnings are each more than 0,
two parts of one condition (both must hold), and 0 otherwise. The refused conditions
(`ca/cpp_part_4_with_employment_earnings_refused`) refuse a count of 1. The form prints no refusal;
it is the guard of this check. The two inputs are tested with made-up kinds.
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

WITH_FAMILY = "ca/cpp_part_4_with_employment_earnings_conditions"
REFUSED_FAMILY = "ca/cpp_part_4_with_employment_earnings_refused"

WITH_TEXT = "Part 4 is completed and CPP pensionable earnings from T4 slips are more than 0"
REFUSED_TEXT = (
    "Part 4 is completed, but Part 4 is for self-employment income and other earnings only (no "
    "employment income); use Part 5 when you also have employment income"
)

# Made up for this test and not registered: the Part 4 checked count, the T4 pensionable earnings
# outside Quebec, the count of Part 4 with employment earnings and its checked count.
PART_4 = ArtifactKind("ex/cpp_part_4_completed_checked", int)
T4 = ArtifactKind("ex/t4_cpp_pensionable_earnings_outside_quebec", Decimal)
WITH_EARNINGS = ArtifactKind("ex/cpp_part_4_with_employment_earnings", int)
WITH_EARNINGS_CHECKED = ArtifactKind("ex/cpp_part_4_with_employment_earnings_checked", int)


def _more_than_0_count(position: int) -> ConditionPart:
    """The part that the count at `position` is more than 0."""
    return ConditionPart((ConditionTest("count", position, "more_than", D("0"), None),))


def _more_than_0_amount(position: int) -> ConditionPart:
    """The part that the amount at `position` is more than 0."""
    return ConditionPart((ConditionTest("amount", position, "more_than", D("0"), None),))


def with_employment(part_4: int, t4: Decimal) -> int:
    """The count of Part 4 completed with employment earnings, Part 4 above 0 and the T4 earnings
    above 0."""
    capability = CountByConditions(
        SOURCE.get(WITH_FAMILY, 2025, CONDITIONS), (PART_4,), (T4,), WITH_EARNINGS
    )
    (count,) = capability.compute((Artifact(PART_4, part_4), Artifact(T4, t4))).outputs
    return int(count.value)


def with_employment_checked(part_4: int, t4: Decimal) -> int:
    """The checked count: the count, then the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(
        SOURCE.get(WITH_FAMILY, 2025, CONDITIONS), (PART_4,), (T4,), WITH_EARNINGS
    )
    refused = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), WITH_EARNINGS, WITH_EARNINGS_CHECKED
    )
    (count,) = counted.compute((Artifact(PART_4, part_4), Artifact(T4, t4))).outputs
    (checked,) = refused.compute((count,)).outputs
    return int(checked.value)


def test_2025_the_condition_is_part_4_completed_and_t4_earnings_each_more_than_0() -> None:
    data = SOURCE.get(WITH_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                WITH_TEXT,
                (_more_than_0_count(1), _more_than_0_amount(1)),
            ),
        ),
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset({1})


def test_2025_the_count_is_not_rounded_and_cites_schedule_8() -> None:
    data = SOURCE.get(WITH_FAMILY, 2025, CONDITIONS)

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
    ("part_4", "t4", "count"),
    [
        (0, D("0"), 0),
        (0, D("20000"), 0),
        (1, D("0"), 0),
        (1, D("0.01"), 1),
        (1, D("20000"), 1),
        (2, D("20000"), 1),
    ],
)
def test_the_count_is_1_only_when_part_4_is_completed_and_t4_earnings_are_more_than_0(
    part_4: int, t4: Decimal, count: int
) -> None:
    assert with_employment(part_4, t4) == count


@pytest.mark.parametrize(("part_4", "t4"), [(0, D("0")), (0, D("20000")), (1, D("0"))])
def test_part_4_without_employment_earnings_or_without_part_4_is_not_refused(
    part_4: int, t4: Decimal
) -> None:
    assert with_employment_checked(part_4, t4) == 0


@pytest.mark.parametrize(("part_4", "t4"), [(1, D("20000")), (2, D("20000"))])
def test_part_4_with_employment_earnings_is_refused_naming_the_condition_text(
    part_4: int, t4: Decimal
) -> None:
    message = f"{WITH_EARNINGS.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        with_employment_checked(part_4, t4)
