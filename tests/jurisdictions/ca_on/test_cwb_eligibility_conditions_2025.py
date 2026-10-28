"""The 2025 conditions dataset of who may claim the Canada workers benefit, against Schedule 6.

Schedule 6 (5000-S6): "Complete this schedule if you met all of the following conditions in 2025:
You were a resident of Canada throughout the year ... You were, at the end of the year, 19 years
of age or older, or you resided with your spouse or common-law partner or your child" and "You
cannot claim the CWB for 2025 if any of the following conditions apply to you". The count is 0 when
any condition applies and 1 otherwise; the counts read, in order, are the residence, 19 or older,
resided with a spouse or child, the eligible dependants of line 38100, a full-time student for more
than 13 weeks, prison and officer of another country. The counts are made-up kinds.
"""

from __future__ import annotations

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.conditions import CONDITIONS
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
FAMILY = "ca/cwb_eligibility_conditions"
SCHEDULE_6_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"

NAMES = (
    "resident",
    "aged_19",
    "resided_with",
    "dependants",
    "student",
    "prison",
    "foreign_officer",
)
KINDS = tuple(ArtifactKind(f"ex/{name}", int) for name in NAMES)
ELIGIBLE = ArtifactKind("ex/cwb_eligible", int)

# The counts that meet every condition: resident, 19 or older, no one resided with, no dependant,
# not a student, not in prison, not an officer of another country.
MEETS = (1, 1, 0, 0, 0, 0, 0)


def eligible(**changes: int) -> int:
    counts = dict(zip(NAMES, MEETS, strict=True))
    counts.update(changes)
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), KINDS, (), ELIGIBLE)
    inputs = tuple(Artifact(kind, counts[name]) for kind, name in zip(KINDS, NAMES, strict=True))
    (result,) = capability.compute(inputs).outputs
    return int(result.value)


def test_2025_the_dataset_gives_0_when_any_condition_applies_and_cites_schedule_6() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values.count_when_any_applies == 0
    assert data.values.count_when_none_applies == 1
    assert data.values.count_positions_read == frozenset(range(1, 8))
    assert data.values.amount_positions_read == frozenset()
    assert data.rounding == NO_ROUNDING
    assert SCHEDULE_6_TXT in data.sources
    assert len(data.values.conditions) == 5


def test_a_filer_who_meets_every_condition_is_eligible() -> None:
    assert eligible() == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"resident": 0},
        {"aged_19": 0},
        {"student": 1},
        {"prison": 1},
        {"foreign_officer": 1},
    ],
)
def test_each_failed_condition_alone_makes_the_filer_ineligible(changes: dict[str, int]) -> None:
    assert eligible(**changes) == 0


@pytest.mark.parametrize(
    "changes",
    [
        {"aged_19": 0, "resided_with": 1},
        {"aged_19": 0, "dependants": 1},
        {"aged_19": 1, "resided_with": 1},
        {"student": 1, "dependants": 1},
    ],
)
def test_the_exceptions_of_schedule_6_keep_the_filer_eligible(changes: dict[str, int]) -> None:
    assert eligible(**changes) == 1


def test_a_student_with_a_dependant_who_is_in_prison_is_still_ineligible() -> None:
    assert eligible(student=1, dependants=1, prison=1) == 0
