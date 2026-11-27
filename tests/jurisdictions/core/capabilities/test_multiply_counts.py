"""Unit tests for the MultiplyCounts capability (`core/multiply_counts`), with made-up kinds.

Schedule 8 Part 2 line A: the months a filer typed in times two 0-or-1 flags from the year of
birth. Its slots: one consumed list slot `counts` (count kinds, at least one, since there is no
product of nothing), one produced slot `output`, no parameters. One `MultiplyCountsLine` records
each count in wiring order. The `counts` slot may be blank, with one rule for each kind.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.trace import BlankFallbackLine, BlankPassedOnLine, MultiplyCountsLine
from tax_engine.jurisdictions.core.capabilities.multiply_counts import MultiplyCounts
from tests.capabilities import bundled_capabilities

MONTHS = CountKind("ex/months")
FLAG_ONE = CountKind("ex/flag_one")
FLAG_TWO = CountKind("ex/flag_two")
PRODUCT = CountKind("ex/product_months")


def capability() -> MultiplyCounts:
    return MultiplyCounts((MONTHS, FLAG_ONE, FLAG_TWO), PRODUCT)


def product(*values: tuple[ArtifactKind[int], int]) -> Artifact[Any]:
    (output,) = capability().compute(tuple(Artifact(kind, v) for kind, v in values)).outputs
    return output


def test_is_registered_as_core_multiply_counts() -> None:
    assert bundled_capabilities().get("core/multiply_counts") is MultiplyCounts


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({MONTHS, FLAG_ONE, FLAG_TWO})
    assert capability().produces == frozenset({PRODUCT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(MultiplyCounts)
    assert "produces" not in vars(MultiplyCounts)


def test_declares_its_slots() -> None:
    assert MultiplyCounts.CONSUMES == {"counts": list[int]}
    assert MultiplyCounts.PRODUCES == {"output": int}
    assert MultiplyCounts.is_list_slot("counts")
    assert "counts" in MultiplyCounts.BLANK_ALLOWED
    assert "counts" in MultiplyCounts.BLANK_PER_ITEM


@pytest.mark.parametrize(
    ("months", "one", "two", "expected"),
    [(12, 1, 1, 12), (7, 1, 1, 7), (12, 0, 1, 0), (12, 1, 0, 0), (0, 1, 1, 0)],
)
def test_the_product_is_the_months_times_the_flags(
    months: int, one: int, two: int, expected: int
) -> None:
    assert product((MONTHS, months), (FLAG_ONE, one), (FLAG_TWO, two)) == Artifact(
        PRODUCT, expected
    )


def test_one_count_is_its_own_product() -> None:
    wired = MultiplyCounts((MONTHS,), PRODUCT)

    assert wired.compute((Artifact(MONTHS, 5),)).outputs == (Artifact(PRODUCT, 5),)


def test_rejects_one_kind_as_both_a_count_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultiplyCounts") as raised:
        MultiplyCounts((MONTHS, PRODUCT), PRODUCT)

    message = str(raised.value)
    assert "'counts'" in message
    assert "'output'" in message


def test_rejects_a_count_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultiplyCounts.*'counts'"):
        MultiplyCounts((MONTHS, FLAG_ONE, MONTHS), PRODUCT)


def test_rejects_a_single_kind_for_its_counts() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultiplyCounts.*'counts'"):
        MultiplyCounts(MONTHS, PRODUCT)  # type: ignore[arg-type]


def test_rejects_a_count_of_another_value_type() -> None:
    amount = AmountKind("ex/amount")

    with pytest.raises(InvalidCapabilityError, match="MultiplyCounts.*'counts'"):
        MultiplyCounts((MONTHS, amount), PRODUCT)  # type: ignore[arg-type]


def test_an_empty_list_of_kinds_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="at least one kind"):
        MultiplyCounts((), PRODUCT)


def test_a_blank_flag_may_take_a_fallback_for_its_kind_alone() -> None:
    result = (
        capability()
        .with_blank_rules({}, per_item={FLAG_ONE: 1, FLAG_TWO: 1})
        .run((Artifact(MONTHS, 12), Artifact(FLAG_ONE, BLANK), Artifact(FLAG_TWO, BLANK)))
    )

    assert result.outputs == (Artifact(PRODUCT, 12),)


def test_a_blank_count_may_be_passed_on() -> None:
    result = (
        capability()
        .with_blank_rules({"counts": PASS_ON})
        .run((Artifact(MONTHS, 12), Artifact(FLAG_ONE, BLANK), Artifact(FLAG_TWO, 1)))
    )

    assert result.outputs == (Artifact(PRODUCT, BLANK),)


def test_records_one_trace_line_with_each_count_and_the_product() -> None:
    result = capability().compute(
        (Artifact(MONTHS, 12), Artifact(FLAG_ONE, 0), Artifact(FLAG_TWO, 1))
    )

    assert result.trace == (
        MultiplyCountsLine(PRODUCT, ((MONTHS, 12), (FLAG_ONE, 0), (FLAG_TWO, 1)), 0),
    )
    (text,) = EnglishTraceRenderer().render_all(result.trace)
    assert "multiplied give" in text


def test_its_slots_are_read_only() -> None:
    for slots in (MultiplyCounts.CONSUMES, MultiplyCounts.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(MultiplyCounts.CONSUMES, Mapping[str, type])
    assert_type(MultiplyCounts.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (MultiplyCounts.CONSUMES, MultiplyCounts.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = MultiplyCounts(counts=(MONTHS, FLAG_ONE), output=PRODUCT)

    result = wired.compute((Artifact(MONTHS, 6), Artifact(FLAG_ONE, 1)))

    assert result.outputs == (Artifact(PRODUCT, 6),)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(MultiplyCounts, "__type_params__", ())
    assert not getattr(MultiplyCounts, "__parameters__", ())


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = CountKind("ex/other")

    result = capability().compute(
        (
            Artifact(other, 9),
            Artifact(MONTHS, 12),
            Artifact(FLAG_ONE, 1),
            Artifact(FLAG_TWO, 1),
        )
    )

    assert result.outputs == (Artifact(PRODUCT, 12),)


def test_the_order_of_the_inputs_does_not_matter() -> None:
    given = (Artifact(MONTHS, 12), Artifact(FLAG_ONE, 0), Artifact(FLAG_TWO, 1))

    result = capability().compute(tuple(reversed(given)))

    assert result.outputs == (Artifact(PRODUCT, 0),)


def test_traces_the_counts_in_the_order_they_were_wired() -> None:
    wired = MultiplyCounts((FLAG_TWO, MONTHS, FLAG_ONE), PRODUCT)
    given = (Artifact(MONTHS, 12), Artifact(FLAG_ONE, 1), Artifact(FLAG_TWO, 1))

    assert wired.compute(given).trace == (
        MultiplyCountsLine(PRODUCT, ((FLAG_TWO, 1), (MONTHS, 12), (FLAG_ONE, 1)), 12),
    )


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="flag_two"):
        capability().compute((Artifact(MONTHS, 12), Artifact(FLAG_ONE, 1)))


# --- a blank count ----------------------------------------------------------------------------


def with_blank_flag() -> tuple[Artifact[Any], ...]:
    return (Artifact(MONTHS, 12), Artifact(FLAG_ONE, BLANK), Artifact(FLAG_TWO, 1))


def test_without_rules_a_blank_count_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'flag_one'.*'counts'"):
        capability().run(with_blank_flag())


def test_a_rule_for_the_slot_covers_every_count() -> None:
    passing = capability().with_blank_rules({"counts": PASS_ON})

    assert passing.run(with_blank_flag()).outputs == (Artifact(PRODUCT, BLANK),)


def test_a_rule_for_one_kind_leaves_the_other_counts_refusing_a_blank() -> None:
    one = capability().with_blank_rules({}, per_item={FLAG_ONE: 1})
    blank_months = (Artifact(MONTHS, BLANK), Artifact(FLAG_ONE, 1), Artifact(FLAG_TWO, 1))

    assert one.run(with_blank_flag()).outputs == (Artifact(PRODUCT, 12),)
    with pytest.raises(BlankNotAllowedError, match="'months'.*'counts'"):
        one.run(blank_months)


def test_a_kind_rule_of_pass_on_beats_a_fallback_for_another_kind() -> None:
    mixed = capability().with_blank_rules({}, per_item={FLAG_ONE: PASS_ON, FLAG_TWO: 1})

    assert mixed.run(with_blank_flag()).outputs == (Artifact(PRODUCT, BLANK),)


def test_a_fallback_for_the_slot_multiplies_in_place_of_each_blank_count() -> None:
    result = capability().with_blank_rules({"counts": 1}).run(with_blank_flag())

    assert result.outputs == (Artifact(PRODUCT, 12),)
    assert result.trace[0] == BlankFallbackLine(FLAG_ONE, 1)
    assert result.trace[1] == MultiplyCountsLine(
        PRODUCT, ((MONTHS, 12), (FLAG_ONE, 1), (FLAG_TWO, 1)), 12
    )


def test_a_passed_on_blank_leaves_a_pass_on_trace_line() -> None:
    result = capability().with_blank_rules({"counts": PASS_ON}).run(with_blank_flag())

    assert result.trace == (BlankPassedOnLine(PRODUCT, (FLAG_ONE,)),)


def test_a_rule_for_a_kind_replaces_the_slots_rule_for_that_kind_only() -> None:
    mixed = capability().with_blank_rules({"counts": PASS_ON}, per_item={FLAG_ONE: 1})

    assert mixed.run(with_blank_flag()).outputs == (Artifact(PRODUCT, 12),)
    blank_two = (Artifact(MONTHS, 12), Artifact(FLAG_ONE, 1), Artifact(FLAG_TWO, BLANK))
    assert mixed.run(blank_two).outputs == (Artifact(PRODUCT, BLANK),)


def test_filled_counts_are_multiplied_as_before_when_rules_are_declared() -> None:
    mixed = capability().with_blank_rules({"counts": PASS_ON}, per_item={FLAG_ONE: 1})
    given = (Artifact(MONTHS, 5), Artifact(FLAG_ONE, 1), Artifact(FLAG_TWO, 1))

    assert mixed.run(given).outputs == (Artifact(PRODUCT, 5),)


def test_a_rule_for_a_kind_the_capability_does_not_multiply_is_refused() -> None:
    elsewhere = CountKind("ex/elsewhere")

    with pytest.raises(InvalidCapabilityError, match="'ex/elsewhere' is not consumed"):
        capability().with_blank_rules({}, per_item={elsewhere: PASS_ON})


def test_a_rule_for_a_count_is_checked_against_that_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="blank rule for slot 'counts'.*'lots'"):
        capability().with_blank_rules({}, per_item={FLAG_ONE: "lots"})  # type: ignore[dict-item]


def test_a_typed_zero_is_not_a_blank() -> None:
    zero = (Artifact(MONTHS, 12), Artifact(FLAG_ONE, 0), Artifact(FLAG_TWO, 1))

    assert capability().run(zero).outputs == (Artifact(PRODUCT, 0),)


# --- trace ------------------------------------------------------------------------------------


def test_trace_amount_is_the_result() -> None:
    trace = (
        capability()
        .compute((Artifact(MONTHS, 7), Artifact(FLAG_ONE, 1), Artifact(FLAG_TWO, 1)))
        .trace
    )

    assert [line.amount for line in trace] == [7]


def test_trace_result_is_the_output() -> None:
    result = capability().compute(
        (Artifact(MONTHS, 7), Artifact(FLAG_ONE, 0), Artifact(FLAG_TWO, 1))
    )

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, MultiplyCountsLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = (
        capability()
        .compute((Artifact(MONTHS, 12), Artifact(FLAG_ONE, 1), Artifact(FLAG_TWO, 1)))
        .trace
    )

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
