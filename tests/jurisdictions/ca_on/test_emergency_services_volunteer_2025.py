"""The 2025 datasets of the emergency services volunteers' conflict, checked against Form 5000-G.

Form 5000-G "Emergency services volunteers": "If you are eligible for the $1,000 exemption on line
10100 of your return and the VFA or SRVA (lines 31220 and 31240 of your return), you must choose
which one you want to claim." The exemption is the exempt part of a payment shown in box 87 of the
T4 slip, reported on line 10105 of the return (the guide's words: "Report the exempt part of the
payment from box 87 of your T4 slips on line 10105 of your return"). The VFA and the SRVA are each
a condition met, a yes or no answer checked to be 0 or 1 (`ca/volunteer_firefighters_conditions_met`
and `ca/search_and_rescue_conditions_met`).

A volunteer who claims the exemption does not claim the VFA or the SRVA, so a return with an
exemption above 0 and either flag at 1 is a conflict. The conditions of
`ca/emergency_services_volunteer_conflicts` say so: one condition, two parts, and it applies when
every part holds. The first part is the exemption not equal to 0; the second is either flag not
equal to 0. The count is 1 when the condition applies, else 0. The conflict is refused when it is 1
(`ca/emergency_services_volunteer_conflict_refused`): an input error, not a rule the guide prints.

The conditions are tested with made-up kinds, as the other conditions datasets are, and not
registered.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

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
GUIDE_5000_G = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"

CONFLICTS_FAMILY = "ca/emergency_services_volunteer_conflicts"
REFUSED_FAMILY = "ca/emergency_services_volunteer_conflict_refused"

# The condition texts, as the dataset holds them, and the refusal's text.
CONFLICT_TEXT = "the $1,000 exemption (line 10105) is claimed with the VFA or SRVA"
REFUSED_TEXT = "the $1,000 exemption (line 10105) and the VFA or SRVA are both claimed"

# Made up for this test and not registered: the VFA and SRVA flags (counts 1 and 2), the exemption
# (amount 1), the count of the conflicts and its checked count.
VFA = ArtifactKind("ex/volunteer_firefighters_flag", int)
SRVA = ArtifactKind("ex/search_and_rescue_flag", int)
EXEMPT = ArtifactKind("ex/emergency_services_volunteer_exempt", Decimal)
CONFLICT = ArtifactKind("ex/emergency_services_volunteer_conflict", int)
CONFLICT_CHECKED = ArtifactKind("ex/emergency_services_volunteer_conflict_checked", int)


def _conflicts() -> CountByConditions:
    """The count of the conflicts, built from the 2025 conditions dataset."""
    return CountByConditions(
        SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS),
        (VFA, SRVA),
        (EXEMPT,),
        CONFLICT,
    )


def _conflict(vfa: int, srva: int, exempt: str) -> int:
    """The count of the conflicts for the two flags and the exemption given."""
    inputs: tuple[Artifact[Any], ...] = (
        Artifact(VFA, vfa),
        Artifact(SRVA, srva),
        Artifact(EXEMPT, D(exempt)),
    )
    (count,) = _conflicts().compute(inputs).outputs
    return int(count.value)


def _refused(count: int) -> tuple[Artifact[Any], ...]:
    """The checked count of the conflicts for a count given, which is refused when it is 1."""
    capability = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), CONFLICT, CONFLICT_CHECKED
    )
    return capability.compute((Artifact(CONFLICT, count),)).outputs


def _test(kind: str, position: int, relation: str, than: str) -> ConditionTest:
    """A test of the count or amount at `position`."""
    return ConditionTest(kind, position, relation, D(than), None)


# --- the conflicts dataset -----------------------------------------------------------------------


def test_2025_the_conflict_is_one_condition_of_two_parts_in_the_order_of_the_guide() -> None:
    data = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                CONFLICT_TEXT,
                (
                    ConditionPart((_test("amount", 1, "not_equal_to", "0"),)),
                    ConditionPart(
                        (
                            _test("count", 1, "not_equal_to", "0"),
                            _test("count", 2, "not_equal_to", "0"),
                        )
                    ),
                ),
            ),
        ),
    )


def test_2025_a_conflict_is_1_when_a_condition_applies_and_0_when_none_does() -> None:
    values = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS).values

    assert values.count_when_any_applies == 1
    assert values.count_when_none_applies == 0


def test_2025_the_conflicts_read_the_two_flags_and_the_exemption() -> None:
    values = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS).values

    assert values.count_positions_read == frozenset({1, 2})
    assert values.amount_positions_read == frozenset({1})


def test_2025_the_conflicts_are_not_rounded_and_cite_the_5000_g_guide() -> None:
    data = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert GUIDE_5000_G in data.sources


@pytest.mark.parametrize(
    ("vfa", "srva", "exempt", "expected"),
    [
        (1, 0, "1000", 1),  # the exemption with the VFA
        (0, 1, "1000", 1),  # the exemption with the SRVA
        (1, 1, "1000", 1),  # the exemption with both flags
        (1, 0, "0", 0),  # no exemption: the VFA alone is not a conflict
        (0, 1, "0", 0),  # no exemption: the SRVA alone is not a conflict
        (0, 0, "1000", 0),  # the exemption alone is not a conflict
        (0, 0, "0", 0),  # nothing claimed
    ],
)
def test_the_exemption_with_a_volunteer_flag_is_a_conflict(
    vfa: int, srva: int, exempt: str, expected: int
) -> None:
    assert _conflict(vfa, srva, exempt) == expected


# --- the refused conflicts dataset ---------------------------------------------------------------


def test_2025_the_refused_conflict_is_one_condition_of_a_count_of_1() -> None:
    data = SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                REFUSED_TEXT,
                (ConditionPart((_test("count", 1, "equal_to", "1"),)),),
            ),
        ),
    )


def test_2025_the_refused_conflict_reads_only_the_one_count_and_no_amount() -> None:
    values = SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS).values

    assert values.count_positions_read == frozenset({1})
    assert values.amount_positions_read == frozenset()
    assert values.count_when_none_applies == 0


def test_2025_the_refused_conflict_is_not_rounded_and_cites_the_5000_g_guide() -> None:
    data = SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert GUIDE_5000_G in data.sources


def test_a_conflict_of_1_is_refused_naming_the_kind_and_the_condition() -> None:
    message = f"{CONFLICT.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        _refused(1)


def test_a_conflict_of_0_is_passed_on_unchanged() -> None:
    assert [artifact.value for artifact in _refused(0)] == [0]
