"""The 2025 conditions datasets of the Canada caregiver amount without the amount it builds on,
against Schedule 5.

Schedule 5 (5000-S5, 2025), line 30425: "You may be able to claim this amount if you can claim an
amount for your spouse or common-law partner on line 30300 of your return, or for an eligible
dependant 18 years of age or older on line 30400 of your return." and "Complete this calculation
only if you entered $2,687 on line 51090 or line 51100 of this schedule".

Two pairs, one for the spouse (`ca/spouse_caregiver_without_spouse_amount_conditions`: line 51090
entered and no amount on line 30300) and one for the eligible dependant
(`ca/dependant_caregiver_without_dependant_amount_conditions`: line 51100 entered and no amount on
line 30400). Each count is 1 when the caregiver flag (`ca/spouse_caregiver_eligible` or
`ca/dependant_caregiver_eligible`, 1 or more) is more than 0 and the claim it builds on
(`ca/spouses_claimed` or `ca/eligible_dependants_checked`) is 0, two parts of one test each (the
parts must both hold), and 0 otherwise. The refused conditions
(`..._refused`) refuse a count of 1. The schedule prints no refusal; it is the guard of this check.
The counts together are tested with made-up kinds.
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

SPOUSE_WITHOUT_FAMILY = "ca/spouse_caregiver_without_spouse_amount_conditions"
SPOUSE_REFUSED_FAMILY = "ca/spouse_caregiver_without_spouse_amount_refused"
DEPENDANT_WITHOUT_FAMILY = "ca/dependant_caregiver_without_dependant_amount_conditions"
DEPENDANT_REFUSED_FAMILY = "ca/dependant_caregiver_without_dependant_amount_refused"

SPOUSE_WITHOUT_TEXT = "line 51090 is entered ($2,687) and no amount is claimed on line 30300"
SPOUSE_REFUSED_TEXT = (
    "line 51090 is entered (the Canada caregiver amount for the spouse) but line 30300 is nil, and "
    "line 30425 applies only if you can claim an amount for your spouse or common-law partner on "
    "line 30300 of your return"
)
DEPENDANT_WITHOUT_TEXT = "line 51100 is entered ($2,687) and no amount is claimed on line 30400"
DEPENDANT_REFUSED_TEXT = (
    "line 51100 is entered (the Canada caregiver amount for a dependant) but line 30400 is nil, "
    "and line 30425 applies only if you can claim an amount for an eligible dependant 18 years of "
    "age or older on line 30400 of your return"
)

# Made up for this test and not registered: the two caregiver flags, the two claims they build on,
# and the counts of each pair and their checked counts.
SPOUSE_CAREGIVER = ArtifactKind("ex/spouse_caregiver_eligible", int)
SPOUSES = ArtifactKind("ex/spouses_claimed", int)
DEPENDANT_CAREGIVER = ArtifactKind("ex/dependant_caregiver_eligible", int)
DEPENDANTS = ArtifactKind("ex/eligible_dependants_checked", int)
SPOUSE_WITHOUT = ArtifactKind("ex/spouse_caregiver_without_spouse_amount", int)
SPOUSE_WITHOUT_CHECKED = ArtifactKind("ex/spouse_caregiver_without_spouse_amount_checked", int)
DEPENDANT_WITHOUT = ArtifactKind("ex/dependant_caregiver_without_dependant_amount", int)
DEPENDANT_WITHOUT_CHECKED = ArtifactKind(
    "ex/dependant_caregiver_without_dependant_amount_checked", int
)


def _more_than_0(position: int) -> ConditionPart:
    """The part that the count at `position` is more than 0."""
    return ConditionPart((ConditionTest("count", position, "more_than", D("0"), None),))


def _equal_to_0(position: int) -> ConditionPart:
    """The part that the count at `position` is 0."""
    return ConditionPart((ConditionTest("count", position, "equal_to", D("0"), None),))


def _equal_to_1(position: int) -> ConditionPart:
    """The part that the count at `position` is 1."""
    return ConditionPart((ConditionTest("count", position, "equal_to", D("1"), None),))


def spouse_without(caregiver: int, spouses: int) -> int:
    """The count of the spouse caregiver amount claimed without the spouse amount."""
    capability = CountByConditions(
        SOURCE.get(SPOUSE_WITHOUT_FAMILY, 2025, CONDITIONS),
        (SPOUSE_CAREGIVER, SPOUSES),
        (),
        SPOUSE_WITHOUT,
    )
    (count,) = capability.compute(
        (Artifact(SPOUSE_CAREGIVER, caregiver), Artifact(SPOUSES, spouses))
    ).outputs
    return int(count.value)


def spouse_without_checked(caregiver: int, spouses: int) -> int:
    """The checked count: the count, then the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(
        SOURCE.get(SPOUSE_WITHOUT_FAMILY, 2025, CONDITIONS),
        (SPOUSE_CAREGIVER, SPOUSES),
        (),
        SPOUSE_WITHOUT,
    )
    refused = CountRefusedByConditions(
        SOURCE.get(SPOUSE_REFUSED_FAMILY, 2025, CONDITIONS), SPOUSE_WITHOUT, SPOUSE_WITHOUT_CHECKED
    )
    (count,) = counted.compute(
        (Artifact(SPOUSE_CAREGIVER, caregiver), Artifact(SPOUSES, spouses))
    ).outputs
    (checked,) = refused.compute((count,)).outputs
    return int(checked.value)


def dependant_without(caregiver: int, dependants: int) -> int:
    """The count of the dependant caregiver amount claimed without the eligible dependant amount."""
    capability = CountByConditions(
        SOURCE.get(DEPENDANT_WITHOUT_FAMILY, 2025, CONDITIONS),
        (DEPENDANT_CAREGIVER, DEPENDANTS),
        (),
        DEPENDANT_WITHOUT,
    )
    (count,) = capability.compute(
        (Artifact(DEPENDANT_CAREGIVER, caregiver), Artifact(DEPENDANTS, dependants))
    ).outputs
    return int(count.value)


def dependant_without_checked(caregiver: int, dependants: int) -> int:
    """The checked count: the count, then the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(
        SOURCE.get(DEPENDANT_WITHOUT_FAMILY, 2025, CONDITIONS),
        (DEPENDANT_CAREGIVER, DEPENDANTS),
        (),
        DEPENDANT_WITHOUT,
    )
    refused = CountRefusedByConditions(
        SOURCE.get(DEPENDANT_REFUSED_FAMILY, 2025, CONDITIONS),
        DEPENDANT_WITHOUT,
        DEPENDANT_WITHOUT_CHECKED,
    )
    (count,) = counted.compute(
        (Artifact(DEPENDANT_CAREGIVER, caregiver), Artifact(DEPENDANTS, dependants))
    ).outputs
    (checked,) = refused.compute((count,)).outputs
    return int(checked.value)


def test_2025_the_spouse_without_condition_is_the_caregiver_and_no_spouse_amount() -> None:
    data = SOURCE.get(SPOUSE_WITHOUT_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1, (Condition(SPOUSE_WITHOUT_TEXT, (_more_than_0(1), _equal_to_0(2))),)
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_dependant_without_condition_is_the_caregiver_and_no_dependant_amount() -> None:
    data = SOURCE.get(DEPENDANT_WITHOUT_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1, (Condition(DEPENDANT_WITHOUT_TEXT, (_more_than_0(1), _equal_to_0(2))),)
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_without_counts_are_not_rounded_and_cite_schedule_5() -> None:
    for family in (SPOUSE_WITHOUT_FAMILY, DEPENDANT_WITHOUT_FAMILY):
        data = SOURCE.get(family, 2025, CONDITIONS)

        assert data.rounding == NO_ROUNDING, family
        assert SCHEDULE_5_TXT in data.sources, family


def test_2025_the_spouse_refusal_refuses_a_count_of_1_at_position_1_and_nothing_else() -> None:
    data = SOURCE.get(SPOUSE_REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(1, (Condition(SPOUSE_REFUSED_TEXT, (_equal_to_1(1),)),))
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    assert data.rounding == NO_ROUNDING
    assert SCHEDULE_5_TXT in data.sources


def test_2025_the_dependant_refusal_refuses_a_count_of_1_at_position_1_and_nothing_else() -> None:
    data = SOURCE.get(DEPENDANT_REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(1, (Condition(DEPENDANT_REFUSED_TEXT, (_equal_to_1(1),)),))
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    assert data.rounding == NO_ROUNDING
    assert SCHEDULE_5_TXT in data.sources


@pytest.mark.parametrize(
    ("caregiver", "spouses", "count"),
    [
        (0, 0, 0),
        (1, 0, 1),
        (0, 1, 0),
        (1, 1, 0),
    ],
)
def test_the_spouse_count_is_1_only_when_the_caregiver_is_claimed_without_the_spouse_amount(
    caregiver: int, spouses: int, count: int
) -> None:
    assert spouse_without(caregiver, spouses) == count


@pytest.mark.parametrize(
    ("caregiver", "dependants", "count"),
    [
        (0, 0, 0),
        (1, 0, 1),
        (0, 1, 0),
        (1, 1, 0),
    ],
)
def test_the_dependant_count_is_1_only_when_the_caregiver_is_claimed_without_the_dependant_amount(
    caregiver: int, dependants: int, count: int
) -> None:
    assert dependant_without(caregiver, dependants) == count


@pytest.mark.parametrize(("caregiver", "spouses"), [(0, 0), (0, 1), (1, 1)])
def test_the_spouse_pair_is_not_refused_unless_the_caregiver_is_alone(
    caregiver: int, spouses: int
) -> None:
    assert spouse_without_checked(caregiver, spouses) == 0


@pytest.mark.parametrize(("caregiver", "dependants"), [(0, 0), (0, 1), (1, 1)])
def test_the_dependant_pair_is_not_refused_unless_the_caregiver_is_alone(
    caregiver: int, dependants: int
) -> None:
    assert dependant_without_checked(caregiver, dependants) == 0


def test_the_spouse_caregiver_alone_is_refused_naming_both_lines() -> None:
    message = f"{SPOUSE_WITHOUT.identifier} 1 is refused: {SPOUSE_REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        spouse_without_checked(1, 0)


def test_the_dependant_caregiver_alone_is_refused_naming_both_lines() -> None:
    message = f"{DEPENDANT_WITHOUT.identifier} 1 is refused: {DEPENDANT_REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        dependant_without_checked(1, 0)
