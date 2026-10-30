"""Unit tests for ConditionList: the `conditions` kind's values, a form's list of conditions.

A form line that is switched on or off by a list of conditions (enter 0 if any of them applies, or
complete a chart if any applies) is copied condition by condition, in the form's order and wording.
A `ConditionList` holds `count_when_any_applies` (0 or 1) and one or more `Condition`s. A
`Condition` holds its printed `text`, word for word, and `parts`, a tuple of `ConditionPart`s that
must all hold; a `ConditionPart` holds `tests`, a tuple of `ConditionTest`s of which any one holds.
A `ConditionTest` holds `reads` (`count` or `amount`), the `position` (from 1) of the figure it
reads in the capability's list of counts or of amounts, a `relation` (`equal_to`, `not_equal_to` or
`more_than`) and exactly one of `than` (a printed figure, an exact Decimal) and `against` (the
position, from 1, of another amount in the list of amounts, for a comparison of two amounts; only
with `reads` of `amount`, and never its own `position`). When no condition applies the count is the
other one of 0 and 1.

A capability checks its selection against what the list reads: `highest_count_position` and
`highest_amount_position` (0 when the list reads none of that kind) and `count_positions_read` and
`amount_positions_read` (frozensets of positions; an `against` position is an amount position
read).
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from decimal import Decimal

import pytest

from tax_engine.domain.errors import DomainError, InvalidConditionsError
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.kind import ParameterKind

D = Decimal
ONE = D(1)


def a_test(
    reads: str = "count",
    position: int = 1,
    relation: str = "equal_to",
    than: Decimal | None = ONE,
    against: int | None = None,
) -> ConditionTest:
    return ConditionTest(reads, position, relation, than, against)


def condition(
    text: str = "You were bankrupt at any time in 2025", *tests: ConditionTest
) -> Condition:
    return Condition(text, (ConditionPart(tests or (a_test(),)),))


def conditions(count_when_any_applies: int = 0, *entries: Condition) -> ConditionList:
    return ConditionList(count_when_any_applies, entries or (condition(),))


# --- the kind -----------------------------------------------------------------------------------


def test_conditions_kind() -> None:
    assert CONDITIONS == ParameterKind("conditions", ConditionList)
    assert CONDITIONS.name == "conditions"
    assert CONDITIONS.value_type is ConditionList


@pytest.mark.parametrize("value_type", [ConditionList, Condition, ConditionPart, ConditionTest])
def test_values_are_frozen_dataclasses(value_type: type) -> None:
    assert is_dataclass(value_type)
    assert value_type.__dataclass_params__.frozen  # type: ignore[attr-defined]


def test_fields_in_order() -> None:
    assert [f.name for f in fields(ConditionList)] == ["count_when_any_applies", "conditions"]
    assert [f.name for f in fields(Condition)] == ["text", "parts"]
    assert [f.name for f in fields(ConditionPart)] == ["tests"]
    assert [f.name for f in fields(ConditionTest)] == [
        "reads",
        "position",
        "relation",
        "than",
        "against",
    ]


def test_holds_what_it_is_given() -> None:
    one = condition("There is an amount on line 72", a_test("amount", 1, "not_equal_to", D(0)))
    listed = ConditionList(0, (one,))

    assert listed.count_when_any_applies == 0
    assert listed.conditions == (one,)
    assert one.text == "There is an amount on line 72"
    assert one.parts[0].tests[0] == ConditionTest("amount", 1, "not_equal_to", D(0), None)


def test_equal_lists_are_equal_and_hashable() -> None:
    assert conditions() == conditions()
    assert hash(conditions()) == hash(conditions())
    assert conditions(0) != conditions(1)
    assert conditions() != conditions(0, condition("You were bankrupt at any time in 2024"))
    assert conditions() != conditions(
        0, condition("You were bankrupt at any time in 2025", a_test(position=2))
    )


def test_keeps_a_figure_as_printed() -> None:
    assert str(a_test("amount", 1, "more_than", D("82125.00")).than) == "82125.00"


def test_a_test_against_another_amount() -> None:
    against = ConditionTest("amount", 1, "more_than", None, 2)

    assert against.than is None
    assert against.against == 2


# --- what a list reads --------------------------------------------------------------------------


def test_a_list_that_reads_one_count() -> None:
    listed = conditions(0, condition("a", a_test("count", 1)))

    assert listed.highest_count_position == 1
    assert listed.highest_amount_position == 0
    assert listed.count_positions_read == frozenset({1})
    assert listed.amount_positions_read == frozenset()


def test_a_list_that_reads_one_amount_against_a_figure() -> None:
    listed = conditions(0, condition("a", a_test("amount", 1, "not_equal_to", D(0))))

    assert listed.highest_count_position == 0
    assert listed.highest_amount_position == 1
    assert listed.count_positions_read == frozenset()
    assert listed.amount_positions_read == frozenset({1})


def test_an_against_position_is_an_amount_position_read() -> None:
    listed = conditions(1, condition("a", a_test("amount", 1, "more_than", None, 2)))

    assert listed.highest_amount_position == 2
    assert listed.amount_positions_read == frozenset({1, 2})


def test_the_same_position_read_twice_is_one_position() -> None:
    listed = conditions(
        1,
        condition("a", a_test("amount", 1, "more_than", D(5))),
        condition("b", a_test("amount", 1, "more_than", D(9))),
    )

    assert listed.amount_positions_read == frozenset({1})
    assert listed.highest_amount_position == 1


def test_positions_read_may_skip_a_position() -> None:
    listed = conditions(0, condition("a", a_test("count", 1), a_test("count", 3)))

    assert listed.count_positions_read == frozenset({1, 3})
    assert listed.highest_count_position == 3


def test_reads_every_test_of_every_part_of_every_condition() -> None:
    chart = ConditionList(
        1,
        (
            Condition(
                "first",
                (
                    ConditionPart((a_test("count", 1, "equal_to", D(1)),)),
                    ConditionPart((a_test("amount", 1, "more_than", D("82125")),)),
                ),
            ),
            Condition(
                "second",
                (
                    ConditionPart(
                        (a_test("count", 2, "equal_to", D(1)), a_test("count", 3, "equal_to", D(1)))
                    ),
                    ConditionPart((a_test("amount", 1, "more_than", D("93454")),)),
                ),
            ),
        ),
    )

    assert chart.count_positions_read == frozenset({1, 2, 3})
    assert chart.highest_count_position == 3
    assert chart.amount_positions_read == frozenset({1})
    assert chart.highest_amount_position == 1


# --- refusals -----------------------------------------------------------------------------------


def test_an_invalid_conditions_error_is_a_domain_error() -> None:
    assert issubclass(InvalidConditionsError, DomainError)


@pytest.mark.parametrize("value", [-1, 2, 10])
def test_count_when_any_applies_must_be_0_or_1(value: int) -> None:
    with pytest.raises(InvalidConditionsError, match="count_when_any_applies must be 0 or 1"):
        ConditionList(value, (condition(),))


@pytest.mark.parametrize("value", [True, "0", 0.0, None])
def test_count_when_any_applies_must_be_an_int(value: object) -> None:
    with pytest.raises(TypeError, match="count_when_any_applies must be an int"):
        ConditionList(value, (condition(),))  # type: ignore[arg-type]


def test_needs_at_least_one_condition() -> None:
    with pytest.raises(InvalidConditionsError, match="at least one condition"):
        ConditionList(0, ())


def test_conditions_must_be_a_tuple_of_conditions() -> None:
    with pytest.raises(TypeError, match="conditions must be a tuple"):
        ConditionList(0, [condition()])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"conditions\[0\] must be a Condition"):
        ConditionList(0, ("text",))  # type: ignore[arg-type]


def test_a_condition_needs_its_printed_text() -> None:
    with pytest.raises(InvalidConditionsError, match="text must not be empty"):
        Condition("", (ConditionPart((a_test(),)),))
    with pytest.raises(TypeError, match="text must be a str"):
        Condition(None, (ConditionPart((a_test(),)),))  # type: ignore[arg-type]


def test_a_condition_needs_at_least_one_part() -> None:
    with pytest.raises(InvalidConditionsError, match="at least one part"):
        Condition("a", ())


def test_parts_must_be_a_tuple_of_parts() -> None:
    with pytest.raises(TypeError, match="parts must be a tuple"):
        Condition("a", [ConditionPart((a_test(),))])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"parts\[0\] must be a ConditionPart"):
        Condition("a", (a_test(),))  # type: ignore[arg-type]


def test_a_part_needs_at_least_one_test() -> None:
    with pytest.raises(InvalidConditionsError, match="at least one test"):
        ConditionPart(())


def test_tests_must_be_a_tuple_of_tests() -> None:
    with pytest.raises(TypeError, match="tests must be a tuple"):
        ConditionPart([a_test()])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"tests\[0\] must be a ConditionTest"):
        ConditionPart(("count",))  # type: ignore[arg-type]


@pytest.mark.parametrize("reads", ["", "money", "Count", "counts"])
def test_a_test_reads_a_count_or_an_amount(reads: str) -> None:
    with pytest.raises(InvalidConditionsError, match="reads must be 'count' or 'amount'"):
        a_test(reads)


@pytest.mark.parametrize("position", [0, -1])
def test_a_position_starts_at_1(position: int) -> None:
    with pytest.raises(InvalidConditionsError, match="position must be 1 or more"):
        a_test(position=position)


@pytest.mark.parametrize("position", [True, "1", 1.0, None])
def test_a_position_must_be_an_int(position: object) -> None:
    with pytest.raises(TypeError, match="position must be an int"):
        a_test(position=position)  # type: ignore[arg-type]


@pytest.mark.parametrize("relation", ["", "less_than", "at_least", "more", "=="])
def test_a_test_uses_one_of_the_three_relations(relation: str) -> None:
    with pytest.raises(
        InvalidConditionsError, match="relation must be 'equal_to', 'not_equal_to' or 'more_than'"
    ):
        a_test(relation=relation)


def test_a_test_needs_exactly_one_of_than_and_against() -> None:
    with pytest.raises(InvalidConditionsError, match="exactly one of than and against"):
        a_test("amount", 1, "more_than", None, None)
    with pytest.raises(InvalidConditionsError, match="exactly one of than and against"):
        a_test("amount", 1, "more_than", D(1), 2)


@pytest.mark.parametrize("against", [0, -2])
def test_against_is_a_position_from_1(against: int) -> None:
    with pytest.raises(InvalidConditionsError, match="against must be 1 or more"):
        a_test("amount", 1, "more_than", None, against)


@pytest.mark.parametrize("against", [True, "2", 2.0])
def test_against_must_be_an_int(against: object) -> None:
    with pytest.raises(TypeError, match="against must be an int"):
        a_test("amount", 1, "more_than", None, against)  # type: ignore[arg-type]


def test_only_an_amount_is_read_against_an_amount() -> None:
    with pytest.raises(InvalidConditionsError, match="against needs reads 'amount'"):
        a_test("count", 1, "more_than", None, 2)


def test_an_amount_is_never_compared_against_itself() -> None:
    with pytest.raises(InvalidConditionsError, match="against must name another amount"):
        a_test("amount", 2, "more_than", None, 2)


@pytest.mark.parametrize("figure", [D("NaN"), D("Infinity"), D("-Infinity")])
def test_than_must_be_finite(figure: Decimal) -> None:
    with pytest.raises(InvalidConditionsError, match="than must be finite"):
        a_test(than=figure)


def test_than_must_be_a_decimal() -> None:
    with pytest.raises(TypeError, match="than must be a Decimal"):
        a_test(than=1)  # type: ignore[arg-type]


def test_reads_and_relation_must_be_strings() -> None:
    with pytest.raises(TypeError, match="reads must be a str"):
        a_test(reads=1)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="relation must be a str"):
        a_test(relation=None)  # type: ignore[arg-type]
