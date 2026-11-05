"""Unit tests for the SubtractNotBelowZero capability (`core/subtract_not_below_zero`), made up.

Its slots are those of `core/subtract`: two consumed single slots, `amount` and `less`, one
produced slot `output`, no parameter slots. The output is max(amount − less, 0), exact, with no
rounding (it has no dataset): the floor of a line the form prints with "if negative, enter 0".
It records one `SubtractedNotBelowZeroLine`, whether or not the floor applied. Either consumed
slot may be blank (`BLANK_ALLOWED`); the rules the manifest gives decide what a blank does there.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import SubtractedLine, SubtractedNotBelowZeroLine
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine
from tests.capabilities import bundled_capabilities

D = Decimal


GROSS = AmountKind("ex/gross_amount")
REDUCTION = AmountKind("ex/reduction")
NET = AmountKind("ex/net_amount")


def capability() -> SubtractNotBelowZero:
    """By default the made-up gross amount less the made-up reduction, not below zero."""
    return SubtractNotBelowZero(GROSS, REDUCTION, NET)


def inputs(amount: str, less: str) -> tuple[Artifact[Decimal], ...]:
    return (Artifact(GROSS, D(amount)), Artifact(REDUCTION, D(less)))


def compute(amount: str, less: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(amount, less)).outputs
    return output


def test_is_registered_as_core_subtract_not_below_zero() -> None:
    assert bundled_capabilities().get("core/subtract_not_below_zero") is SubtractNotBelowZero


def test_leaves_core_subtract_registered_as_the_unfloored_subtraction() -> None:
    assert bundled_capabilities().get("core/subtract") is Subtract


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({GROSS, REDUCTION})
    assert capability().produces == frozenset({NET})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(SubtractNotBelowZero)
    assert "produces" not in vars(SubtractNotBelowZero)


def test_declares_the_slots_of_core_subtract() -> None:
    assert SubtractNotBelowZero.PARAMETERS == {}
    assert SubtractNotBelowZero.CONSUMES == {"amount": Decimal, "less": Decimal}
    assert SubtractNotBelowZero.PRODUCES == {"output": Decimal}
    assert not SubtractNotBelowZero.is_list_slot("amount")
    assert not SubtractNotBelowZero.is_list_slot("less")
    assert not SubtractNotBelowZero.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (
        SubtractNotBelowZero.PARAMETERS,
        SubtractNotBelowZero.CONSUMES,
        SubtractNotBelowZero.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(SubtractNotBelowZero.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(SubtractNotBelowZero.CONSUMES, Mapping[str, type])
    assert_type(SubtractNotBelowZero.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        SubtractNotBelowZero.PARAMETERS,
        SubtractNotBelowZero.CONSUMES,
        SubtractNotBelowZero.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = SubtractNotBelowZero(amount=GROSS, less=REDUCTION, output=NET)

    result = wired.compute(inputs("100", "30"))

    assert result.outputs == (Artifact(NET, D("70")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        SubtractNotBelowZero(GROSS, REDUCTION, NET, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_amount_and_less() -> None:
    with pytest.raises(InvalidCapabilityError, match="SubtractNotBelowZero") as raised:
        SubtractNotBelowZero(GROSS, GROSS, NET)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'less'" in message


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="SubtractNotBelowZero") as raised:
        SubtractNotBelowZero(GROSS, REDUCTION, GROSS)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_less_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="SubtractNotBelowZero") as raised:
        SubtractNotBelowZero(GROSS, REDUCTION, REDUCTION)

    message = str(raised.value)
    assert "'less'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="SubtractNotBelowZero.*'amount'"):
        SubtractNotBelowZero((GROSS,), REDUCTION, NET)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_what_it_takes_off() -> None:
    with pytest.raises(InvalidCapabilityError, match="SubtractNotBelowZero.*'less'"):
        SubtractNotBelowZero(GROSS, (REDUCTION,), NET)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="SubtractNotBelowZero.*'less'"):
        SubtractNotBelowZero(GROSS, count, NET)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(SubtractNotBelowZero, "__type_params__", ())
    assert not getattr(SubtractNotBelowZero, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_positive_difference_is_produced_unchanged() -> None:
    assert compute("100.25", "40") == Artifact(NET, D("60.25"))


def test_equal_amounts_produce_zero() -> None:
    output = compute("40.50", "40.50")

    assert output == Artifact(NET, D("0"))
    assert type(output.value) is Decimal


def test_taking_off_zero_produces_the_amount() -> None:
    assert compute("1234.56", "0") == Artifact(NET, D("1234.56"))


def test_a_larger_less_is_floored_at_zero() -> None:
    output = compute("10", "25.5")

    assert output == Artifact(NET, D("0"))
    assert type(output.value) is Decimal


def test_the_floor_is_a_plain_decimal_zero() -> None:
    # Settled on #67: when the floor applies, the output is `Decimal(0)`, not the difference's
    # scale (no "0.0") and never a negative zero.
    value = compute("10.00", "25.50").value

    assert type(value) is Decimal
    assert str(value) == "0"
    assert not value.is_signed()


def test_a_difference_just_below_zero_is_floored() -> None:
    assert compute("0.0000000000000001", "0.0000000000000002") == Artifact(NET, D("0"))


def test_a_zero_amount_less_a_positive_one_is_floored() -> None:
    assert compute("0", "1") == Artifact(NET, D("0"))


def test_takes_a_negative_amount_off_as_is() -> None:
    assert compute("100", "-20") == Artifact(NET, D("120"))


def test_a_negative_amount_is_floored_at_zero() -> None:
    assert compute("-5", "0") == Artifact(NET, D("0"))


def test_subtracts_exactly_with_many_decimals() -> None:
    output = compute("1234567.0000000000000003", "0.0000000000000001")

    assert output == Artifact(NET, D("1234567.0000000000000002"))
    assert type(output.value) is Decimal


def test_subtracts_decimals_float_would_not() -> None:
    assert compute("0.3", "0.1") == Artifact(NET, D("0.2"))


def test_does_not_round_the_difference() -> None:
    assert compute("0.005", "0.0049") == Artifact(NET, D("0.0001"))


def test_keeps_the_scale_of_a_positive_difference() -> None:
    assert str(compute("100.00", "40").value) == "60.00"


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs("100", "30"))))

    assert result.outputs == (Artifact(NET, D("70")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), *inputs("10", "4")))

    assert result.outputs == (Artifact(NET, D("6")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="gross_amount"):
        capability().compute((Artifact(REDUCTION, D("1")),))


def test_a_missing_less_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="reduction"):
        capability().compute((Artifact(GROSS, D("1")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_subtracted_not_below_zero_line() -> None:
    trace = capability().compute(inputs("100.25", "40")).trace

    assert trace == (
        SubtractedNotBelowZeroLine(
            output=NET,
            minuend=GROSS,
            minuend_amount=D("100.25"),
            subtrahend=REDUCTION,
            subtrahend_amount=D("40"),
            result=D("60.25"),
        ),
    )


def test_traces_the_floored_result() -> None:
    trace = capability().compute(inputs("10", "25.5")).trace

    assert trace == (SubtractedNotBelowZeroLine(NET, GROSS, D("10"), REDUCTION, D("25.5"), D("0")),)


def test_traces_a_floored_line_not_a_plain_subtracted_line() -> None:
    (line,) = capability().compute(inputs("10", "25.5")).trace

    assert type(line) is SubtractedNotBelowZeroLine
    assert cast(Any, line) != SubtractedLine(NET, GROSS, D("10"), REDUCTION, D("25.5"), D("0"))


def test_trace_amount_is_the_floored_result() -> None:
    trace = capability().compute(inputs("10", "25.5")).trace

    assert [line.amount for line in trace] == [D("0")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute(inputs("100.25", "40"))

    assert [line.amount for line in result.trace] == [output.value for output in result.outputs]


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("10", "25.5")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- a blank in either slot ---------------------------------------------------------------------


def blank_input(kind: ArtifactKind[Decimal]) -> Artifact[Any]:
    return Artifact(kind, BLANK)


def test_declares_that_either_slot_may_be_blank() -> None:
    assert SubtractNotBelowZero.BLANK_ALLOWED == frozenset({"amount", "less"})


def test_without_rules_a_blank_amount_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'gross_amount'.*'amount'"):
        capability().run((blank_input(GROSS), Artifact(REDUCTION, D(1))))


def test_without_rules_a_blank_less_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'reduction'.*'less'"):
        capability().run((Artifact(GROSS, D(1)), blank_input(REDUCTION)))


def test_pass_on_in_either_slot_blanks_the_output_without_applying_the_floor() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "less": PASS_ON})

    for given in (
        (blank_input(GROSS), Artifact(REDUCTION, D(1))),
        (Artifact(GROSS, D(1)), blank_input(REDUCTION)),
    ):
        result = passing.run(given)
        assert result.outputs == (Artifact(NET, BLANK),)
        assert isinstance(result.trace[0], BlankPassedOnLine)
        assert not any(isinstance(line, SubtractedNotBelowZeroLine) for line in result.trace)


def test_a_blank_in_both_slots_passes_on_once() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "less": PASS_ON})

    result = passing.run((blank_input(GROSS), blank_input(REDUCTION)))

    assert result.outputs == (Artifact(NET, BLANK),)
    assert result.trace == (BlankPassedOnLine(NET, (GROSS, REDUCTION)),)


def test_a_fallback_for_less_is_applied_and_the_floor_still_applies() -> None:
    carried = capability().with_blank_rules({"less": D(0)})

    kept = carried.run((Artifact(GROSS, D(508418)), blank_input(REDUCTION)))
    assert kept.outputs == (Artifact(NET, D(508418)),)
    assert kept.trace == (
        BlankFallbackLine(REDUCTION, D(0)),
        SubtractedNotBelowZeroLine(NET, GROSS, D(508418), REDUCTION, D(0), D(508418)),
    )

    floored = (
        capability()
        .with_blank_rules({"less": D(5)})
        .run((Artifact(GROSS, D(2)), blank_input(REDUCTION)))
    )
    assert floored.outputs == (Artifact(NET, D(0)),)


def test_a_fallback_for_less_does_not_cover_a_blank_amount() -> None:
    carried = capability().with_blank_rules({"less": D(0)})

    with pytest.raises(BlankNotAllowedError, match="'amount'"):
        carried.run((blank_input(GROSS), Artifact(REDUCTION, D(1))))


def test_pass_on_wins_over_a_fallback_in_the_other_slot() -> None:
    mixed = capability().with_blank_rules({"amount": PASS_ON, "less": D(0)})

    result = mixed.run((blank_input(GROSS), blank_input(REDUCTION)))

    assert result.outputs == (Artifact(NET, BLANK),)


def test_filled_values_are_floored_as_before_when_pass_on_is_declared() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "less": PASS_ON})

    assert passing.run(inputs("2", "5")).outputs == (Artifact(NET, D(0)),)
    assert passing.run(inputs("5", "2")).outputs == (Artifact(NET, D(3)),)


def test_a_rule_for_a_slot_that_is_not_consumed_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="'output'"):
        capability().with_blank_rules({"output": PASS_ON})
