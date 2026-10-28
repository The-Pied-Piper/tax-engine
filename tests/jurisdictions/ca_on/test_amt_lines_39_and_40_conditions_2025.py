"""The 2025 conditions datasets of Form T691 Part 1 lines 39 and 40, checked against the form.

Form T691 (2025), Part 1: "If you claimed limited partnership losses incurred in another year on
line 25100 of your 2025 return, complete line 39 or 40 depending on your situation: If you have not
filed an election, enter the difference [...] (39)", "If you have filed an election, enter the
difference [...] (40)". Lines 43 and 46 add both lines, so a filer who completes both has the
second counted on top of the first.

The count (`ca/amt_lines_39_and_40_both_conditions`) is 1 when line 39 and line 40 are each more
than 0, two parts of one test each (the parts must both hold), and 0 otherwise. The refused
conditions (`ca/amt_lines_39_and_40_both_refused`) refuse a count of 1. The form prints no refusal;
it is the guard of this check. The two counts together are tested with made-up kinds.
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
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"

BOTH_FAMILY = "ca/amt_lines_39_and_40_both_conditions"
REFUSED_FAMILY = "ca/amt_lines_39_and_40_both_refused"

BOTH_TEXT = "line 39 and line 40 are both more than 0"
REFUSED_TEXT = "line 39 and line 40 are both filled in, but the form says to complete line 39 or 40"

# Made up for this test and not registered: line 39, line 40, the count and its checked count.
LINE_39 = ArtifactKind("ex/amt_line_39", Decimal)
LINE_40 = ArtifactKind("ex/amt_line_40", Decimal)
BOTH = ArtifactKind("ex/amt_lines_39_and_40_both", int)
BOTH_CHECKED = ArtifactKind("ex/amt_lines_39_and_40_both_checked", int)


def _positive(position: int) -> ConditionPart:
    """The part that the amount at `position` is more than 0."""
    return ConditionPart((ConditionTest("amount", position, "more_than", D("0"), None),))


def both(line_39: str, line_40: str) -> int:
    """The count of lines 39 and 40 both above 0."""
    capability = CountByConditions(
        SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS), (), (LINE_39, LINE_40), BOTH
    )
    (count,) = capability.compute(
        (Artifact(LINE_39, D(line_39)), Artifact(LINE_40, D(line_40)))
    ).outputs
    return int(count.value)


def both_checked(line_39: str, line_40: str) -> int:
    """The checked count: the count of both, then the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(
        SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS), (), (LINE_39, LINE_40), BOTH
    )
    refused = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), BOTH, BOTH_CHECKED
    )
    (count,) = counted.compute(
        (Artifact(LINE_39, D(line_39)), Artifact(LINE_40, D(line_40)))
    ).outputs
    (checked,) = refused.compute((count,)).outputs
    return int(checked.value)


def test_2025_the_both_condition_is_line_39_and_line_40_each_more_than_0() -> None:
    data = SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(1, (Condition(BOTH_TEXT, (_positive(1), _positive(2))),))
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.amount_positions_read == frozenset({1, 2})
    assert data.values.count_positions_read == frozenset()


def test_2025_the_both_count_is_not_rounded_and_cites_the_form() -> None:
    data = SOURCE.get(BOTH_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert T691_PDF in data.sources


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
    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("line_39", "line_40", "count"),
    [
        ("0", "0", 0),
        ("100000", "0", 0),
        ("0", "100000", 0),
        ("100000", "100000", 1),
        ("0.01", "0.01", 1),
    ],
)
def test_the_count_is_1_only_when_both_lines_are_more_than_0(
    line_39: str, line_40: str, count: int
) -> None:
    assert both(line_39, line_40) == count


@pytest.mark.parametrize(("line_39", "line_40"), [("0", "0"), ("100000", "0"), ("0", "100000")])
def test_one_line_or_none_is_not_refused(line_39: str, line_40: str) -> None:
    assert both_checked(line_39, line_40) == 0


@pytest.mark.parametrize(("line_39", "line_40"), [("100000", "100000"), ("0.01", "25000")])
def test_both_lines_filled_in_are_refused_naming_the_condition_text(
    line_39: str, line_40: str
) -> None:
    message = f"{BOTH.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        both_checked(line_39, line_40)
