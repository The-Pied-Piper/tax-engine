"""Unit tests for the Sum capability (`core/sum`), with made-up kinds.

Its slots: one consumed list slot `parts` (a tuple of money kinds, possibly empty), one produced
slot `output`, no parameter slots. It adds the parts' values exactly, with no rounding (a sum has
no dataset), and records one `SumLine` holding each part in the order it was wired. Any part may be
blank (`BLANK_ALLOWED`), and the rules the manifest gives decide what a blank does, for the whole
list or for one part (`BLANK_PER_ITEM`).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import SumLine
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine
from tax_engine.jurisdictions.core.capabilities.sum import Sum
from tests.capabilities import bundled_capabilities

D = Decimal


PART_ONE = AmountKind("ex/part_one")
PART_TWO = AmountKind("ex/part_two")
PART_THREE = AmountKind("ex/part_three")
TOTAL = AmountKind("ex/total")


def capability() -> Sum:
    """By default the three made-up parts, in order one, two, three."""
    return Sum((PART_ONE, PART_TWO, PART_THREE), TOTAL)


def three_parts() -> tuple[Artifact[Decimal], ...]:
    return (
        Artifact(PART_ONE, D("100.25")),
        Artifact(PART_TWO, D("40")),
        Artifact(PART_THREE, D("9.75")),
    )


def test_is_registered_as_core_sum() -> None:
    assert bundled_capabilities().get("core/sum") is Sum


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({PART_ONE, PART_TWO, PART_THREE})
    assert capability().produces == frozenset({TOTAL})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(Sum)
    assert "produces" not in vars(Sum)


def test_declares_its_slots() -> None:
    assert Sum.PARAMETERS == {}
    assert Sum.CONSUMES == {"parts": list[Decimal]}
    assert Sum.PRODUCES == {"output": Decimal}
    assert Sum.is_list_slot("parts")
    assert not Sum.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (Sum.PARAMETERS, Sum.CONSUMES, Sum.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(Sum.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(Sum.CONSUMES, Mapping[str, type])
    assert_type(Sum.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (Sum.PARAMETERS, Sum.CONSUMES, Sum.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = Sum(parts=(PART_ONE, PART_TWO, PART_THREE), output=TOTAL)

    result = wired.compute(three_parts())

    assert result.outputs == (Artifact(TOTAL, D("150.00")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        Sum((PART_ONE,), TOTAL, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_a_part_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="Sum") as raised:
        Sum((PART_ONE, TOTAL), TOTAL)

    message = str(raised.value)
    assert "'parts'" in message
    assert "'output'" in message


def test_rejects_a_part_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="Sum.*'parts'"):
        Sum((PART_ONE, PART_TWO, PART_ONE), TOTAL)


def test_rejects_a_single_kind_for_its_parts() -> None:
    with pytest.raises(InvalidCapabilityError, match="Sum.*'parts'"):
        Sum(PART_ONE, TOTAL)  # type: ignore[arg-type]


def test_rejects_a_part_of_another_value_type() -> None:
    count = CountKind("ex/count")

    with pytest.raises(InvalidCapabilityError, match="Sum.*'parts'"):
        Sum((PART_ONE, count), TOTAL)  # type: ignore[arg-type]


# --- computing --------------------------------------------------------------------------------


def test_adds_three_parts() -> None:
    result = capability().compute(three_parts())

    assert result.outputs == (Artifact(TOTAL, D("150.00")),)


def test_one_part_is_its_own_total() -> None:
    wired = Sum((PART_TWO,), TOTAL)

    result = wired.compute((Artifact(PART_TWO, D("40.5")),))

    assert result.outputs == (Artifact(TOTAL, D("40.5")),)


def test_zero_parts_sum_to_zero() -> None:
    wired = Sum((), TOTAL)

    result = wired.compute(())

    assert result.outputs == (Artifact(TOTAL, D(0)),)
    assert type(result.outputs[0].value) is Decimal
    assert wired.consumes == frozenset()


def test_adds_exactly_with_many_decimals() -> None:
    wired = Sum((PART_ONE, PART_TWO, PART_THREE), TOTAL)

    result = wired.compute(
        (
            Artifact(PART_ONE, D("0.1")),
            Artifact(PART_TWO, D("0.2")),
            Artifact(PART_THREE, D("1234567.0000000000000001")),
        )
    )

    assert result.outputs == (Artifact(TOTAL, D("1234567.3000000000000001")),)


def test_does_not_round_the_total() -> None:
    wired = Sum((PART_ONE, PART_TWO), TOTAL)

    result = wired.compute((Artifact(PART_ONE, D("0.005")), Artifact(PART_TWO, D("0.0049"))))

    assert result.outputs == (Artifact(TOTAL, D("0.0099")),)


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(three_parts())))

    assert result.outputs == (Artifact(TOTAL, D("150.00")),)


def test_a_missing_part_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="part_three"):
        capability().compute(three_parts()[:2])


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_with_each_part_and_the_total() -> None:
    trace = capability().compute(three_parts()).trace

    assert trace == (
        SumLine(
            output=TOTAL,
            parts=((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))),
            total=D("150.00"),
        ),
    )


def test_traces_the_parts_in_the_order_they_were_wired() -> None:
    wired = Sum((PART_THREE, PART_ONE, PART_TWO), TOTAL)

    trace = wired.compute(three_parts()).trace

    assert trace == (
        SumLine(
            TOTAL,
            ((PART_THREE, D("9.75")), (PART_ONE, D("100.25")), (PART_TWO, D("40"))),
            D("150.00"),
        ),
    )


def test_traces_zero_parts() -> None:
    trace = Sum((), TOTAL).compute(()).trace

    assert trace == (SumLine(TOTAL, (), D(0)),)


def test_trace_amount_is_the_total() -> None:
    trace = capability().compute(three_parts()).trace

    assert [line.amount for line in trace] == [D("150.00")]


def test_trace_holds_no_text() -> None:
    trace = capability().compute(three_parts()).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(Sum, "__type_params__", ())
    assert not getattr(Sum, "__parameters__", ())


# --- a blank part ---------------------------------------------------------------------------
# The list is one slot, `parts`. A rule for the slot covers every part; a rule for one part, by its
# kind, replaces the slot's rule for that part alone.


def with_blank(*blanked: AmountKind) -> tuple[Artifact[Any], ...]:
    """The three made-up parts, with each kind in `blanked` left blank."""
    return tuple(
        Artifact(artifact.kind, BLANK) if artifact.kind in blanked else artifact
        for artifact in three_parts()
    )


def test_declares_that_the_parts_may_be_blank_one_by_one() -> None:
    assert Sum.BLANK_ALLOWED == frozenset({"parts"})
    assert Sum.BLANK_PER_ITEM == frozenset({"parts"})


def test_without_rules_a_blank_part_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'part_two'.*'parts'"):
        capability().run(with_blank(PART_TWO))


def test_a_rule_for_the_slot_covers_every_part() -> None:
    passing = capability().with_blank_rules({"parts": PASS_ON})

    for blanked in (PART_ONE, PART_TWO, PART_THREE):
        assert passing.run(with_blank(blanked)).outputs == (Artifact(TOTAL, BLANK),)


def test_a_fallback_for_the_slot_adds_it_in_place_of_each_blank_part() -> None:
    result = capability().with_blank_rules({"parts": D(0)}).run(with_blank(PART_TWO, PART_THREE))

    assert result.outputs == (Artifact(TOTAL, D("100.25")),)
    assert result.trace[:2] == (
        BlankFallbackLine(PART_THREE, D(0)),
        BlankFallbackLine(PART_TWO, D(0)),
    )
    assert result.trace[2] == SumLine(
        TOTAL, ((PART_ONE, D("100.25")), (PART_TWO, D(0)), (PART_THREE, D(0))), D("100.25")
    )


def test_a_rule_for_one_part_leaves_the_other_parts_refusing_a_blank() -> None:
    one = capability().with_blank_rules({}, {PART_TWO: PASS_ON})

    assert one.run(with_blank(PART_TWO)).outputs == (Artifact(TOTAL, BLANK),)
    with pytest.raises(BlankNotAllowedError, match="'part_three'.*'parts'"):
        one.run(with_blank(PART_THREE))


def test_a_part_can_pass_a_blank_on_while_another_counts_as_zero() -> None:
    mixed = capability().with_blank_rules({}, {PART_ONE: PASS_ON, PART_THREE: D(0)})

    zeroed = mixed.run(with_blank(PART_THREE))
    passed = mixed.run(with_blank(PART_ONE))

    assert zeroed.outputs == (Artifact(TOTAL, D("140.25")),)
    assert zeroed.trace[0] == BlankFallbackLine(PART_THREE, D(0))
    assert passed.outputs == (Artifact(TOTAL, BLANK),)
    assert passed.trace == (BlankPassedOnLine(TOTAL, (PART_ONE,)),)


def test_pass_on_wins_over_a_fallback_when_both_parts_are_blank() -> None:
    mixed = capability().with_blank_rules({}, {PART_ONE: PASS_ON, PART_THREE: D(0)})

    result = mixed.run(with_blank(PART_ONE, PART_THREE))

    assert result.outputs == (Artifact(TOTAL, BLANK),)
    assert result.trace == (BlankPassedOnLine(TOTAL, (PART_ONE,)),)


def test_a_rule_for_a_part_replaces_the_slots_rule_for_that_part_only() -> None:
    mixed = capability().with_blank_rules({"parts": PASS_ON}, {PART_TWO: D(0)})

    assert mixed.run(with_blank(PART_TWO)).outputs == (Artifact(TOTAL, D("110.00")),)
    assert mixed.run(with_blank(PART_ONE)).outputs == (Artifact(TOTAL, BLANK),)


def test_filled_parts_are_added_as_before_when_rules_are_declared() -> None:
    mixed = capability().with_blank_rules({"parts": PASS_ON}, {PART_TWO: D(0)})

    assert mixed.run(three_parts()).outputs == (Artifact(TOTAL, D("150.00")),)


def test_a_typed_zero_is_not_a_blank() -> None:
    passing = capability().with_blank_rules({"parts": PASS_ON})
    given = (Artifact(PART_ONE, D(0)), *three_parts()[1:])

    assert passing.run(given).outputs == (Artifact(TOTAL, D("49.75")),)


def test_a_rule_for_a_kind_the_sum_does_not_add_is_refused() -> None:
    elsewhere = AmountKind("ex/elsewhere")

    with pytest.raises(InvalidCapabilityError, match="'ex/elsewhere' is not consumed"):
        capability().with_blank_rules({}, {elsewhere: PASS_ON})


def test_a_rule_for_a_part_is_checked_against_that_part() -> None:
    with pytest.raises(InvalidCapabilityError, match="blank rule for slot 'parts'.*'lots'"):
        capability().with_blank_rules({}, {PART_ONE: "lots"})  # type: ignore[dict-item]
