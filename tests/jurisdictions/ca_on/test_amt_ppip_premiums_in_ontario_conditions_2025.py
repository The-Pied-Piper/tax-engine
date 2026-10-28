"""The 2025 conditions datasets of Form T691 Part 1 line 59, checked against the form.

Form T691 (2025), Part 1: "Deduction for PPIP premiums on self-employment income from line 22300 of
your return (Quebec only) (59)". An Ontario resident has no Quebec line 22300, so a line 59 above 0
is an input error, not a deduction added to line 63.

The count (`ca/amt_ppip_premiums_in_ontario_conditions`) is 1 when line 59 is more than 0 and the
count of not being a resident of Ontario on December 31, 2025 is 0 (two parts of one test each, the
parts must both hold), and 0 otherwise. The refused conditions
(`ca/amt_ppip_premiums_in_ontario_refused`) refuse a count of 1. The form prints no refusal; it is
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
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"

IN_ONTARIO_FAMILY = "ca/amt_ppip_premiums_in_ontario_conditions"
REFUSED_FAMILY = "ca/amt_ppip_premiums_in_ontario_refused"

IN_ONTARIO_TEXT = "line 59 is more than 0 and the filer lived in Ontario on December 31, 2025"
REFUSED_TEXT = "line 59 is Quebec only, but the filer lived in Ontario on December 31, 2025"

# Made up for this test and not registered: line 59, the not-resident count, the count of line 59
# for a resident of Ontario and its checked count.
LINE_59 = ArtifactKind("ex/amt_line_59", Decimal)
NOT_RESIDENT = ArtifactKind("ex/not_resident_of_ontario", int)
IN_ONTARIO = ArtifactKind("ex/amt_line_59_in_ontario", int)
IN_ONTARIO_CHECKED = ArtifactKind("ex/amt_line_59_in_ontario_checked", int)


def _test(reads: str, relation: str, than: str) -> ConditionPart:
    """The part with one test of the amount or count at position 1."""
    return ConditionPart((ConditionTest(reads, 1, relation, D(than), None),))


def counted(line_59: str, not_resident: int) -> Artifact[int]:
    """The count of line 59 above 0 for a resident of Ontario."""
    capability = CountByConditions(
        SOURCE.get(IN_ONTARIO_FAMILY, 2025, CONDITIONS), (NOT_RESIDENT,), (LINE_59,), IN_ONTARIO
    )
    (count,) = capability.compute(
        (Artifact(NOT_RESIDENT, not_resident), Artifact(LINE_59, D(line_59)))
    ).outputs
    return count


def in_ontario(line_59: str, not_resident: int) -> int:
    return int(counted(line_59, not_resident).value)


def in_ontario_checked(line_59: str, not_resident: int) -> int:
    """The checked count: the count, then the refusal of a count of 1 (which raises)."""
    refused = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), IN_ONTARIO, IN_ONTARIO_CHECKED
    )
    (checked,) = refused.compute((counted(line_59, not_resident),)).outputs
    return int(checked.value)


def test_2025_the_condition_is_line_59_above_0_and_a_resident_of_ontario() -> None:
    data = SOURCE.get(IN_ONTARIO_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                IN_ONTARIO_TEXT,
                (_test("amount", "more_than", "0"), _test("count", "equal_to", "0")),
            ),
        ),
    )
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    assert data.values.amount_positions_read == frozenset({1})
    assert data.values.count_positions_read == frozenset({1})


def test_2025_the_count_is_not_rounded_and_cites_the_form() -> None:
    data = SOURCE.get(IN_ONTARIO_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert T691_PDF in data.sources


def test_2025_the_refusal_refuses_a_count_of_1_at_position_1_and_nothing_else() -> None:
    data = SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1, (Condition(REFUSED_TEXT, (_test("count", "equal_to", "1"),)),)
    )
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    assert data.rounding == NO_ROUNDING
    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("line_59", "not_resident", "count"),
    [
        ("0", 0, 0),
        ("0", 1, 0),
        ("100000", 1, 0),
        ("100000", 0, 1),
        ("0.01", 0, 1),
    ],
)
def test_the_count_is_1_only_for_line_59_above_0_and_a_resident_of_ontario(
    line_59: str, not_resident: int, count: int
) -> None:
    assert in_ontario(line_59, not_resident) == count


@pytest.mark.parametrize(("line_59", "not_resident"), [("0", 0), ("0", 1), ("100000", 1)])
def test_no_line_59_or_a_filer_who_is_not_a_resident_of_ontario_is_not_refused(
    line_59: str, not_resident: int
) -> None:
    assert in_ontario_checked(line_59, not_resident) == 0


@pytest.mark.parametrize("line_59", ["100000", "0.01"])
def test_line_59_for_a_resident_of_ontario_is_refused_naming_the_condition_text(
    line_59: str,
) -> None:
    message = f"{IN_ONTARIO.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        in_ontario_checked(line_59, 0)
