"""Unit tests for the TimesCount capability (`core/times_count`), with made-up kinds and values.

Its slots: two consumed single slots, `amount` (a `Decimal` artifact, the amount for each person)
and `count` (an `int` artifact, the number of persons), one produced slot `output`, no parameter
slots. The output is `amount × count`, exact, with the amount's scale kept; it has no dataset, so
it never rounds. A count of 0 gives a plain zero (no scale, never a signed zero). It records one
`TimesCountLine` holding the amount's kind and value, the count's kind, the count and the result.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.domain.capabilities as core
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import PerUnitAmountLine, TimesCountLine

D = Decimal


EACH = ArtifactKind("ex/amount_each", Decimal)
PERSONS = ArtifactKind("ex/person_count", int)
CLAIMED = ArtifactKind("ex/amount_claimed", Decimal)


def capability() -> TimesCount:
    """By default the made-up amount for each person, times the made-up count of persons."""
    return TimesCount(EACH, PERSONS, CLAIMED)


def inputs(amount: str, count: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(EACH, D(amount)), Artifact(PERSONS, count))


def compute(amount: str, count: int) -> Artifact[Any]:
    (output,) = capability().compute(inputs(amount, count)).outputs
    return output


def test_is_registered_as_core_times_count() -> None:
    assert CapabilityRegistry.shared().get("core/times_count") is TimesCount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "times_count" in core.__all__
    assert core.times_count.TimesCount is TimesCount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({EACH, PERSONS})
    assert capability().produces == frozenset({CLAIMED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TimesCount)
    assert "produces" not in vars(TimesCount)


def test_declares_its_slots() -> None:
    assert TimesCount.PARAMETERS == {}
    assert TimesCount.CONSUMES == {"amount": Decimal, "count": int}
    assert TimesCount.CONSUMES["count"] is int
    assert TimesCount.PRODUCES == {"output": Decimal}
    assert not TimesCount.is_list_slot("amount")
    assert not TimesCount.is_list_slot("count")
    assert not TimesCount.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (TimesCount.PARAMETERS, TimesCount.CONSUMES, TimesCount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(TimesCount.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(TimesCount.CONSUMES, Mapping[str, type])
    assert_type(TimesCount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (TimesCount.PARAMETERS, TimesCount.CONSUMES, TimesCount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TimesCount(amount=EACH, count=PERSONS, output=CLAIMED)

    result = wired.compute(inputs("16129", 2))

    assert result.outputs == (Artifact(CLAIMED, D("32258")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        TimesCount(EACH, PERSONS, CLAIMED, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TimesCount") as raised:
        TimesCount(EACH, PERSONS, EACH)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'amount'"):
        TimesCount((EACH,), PERSONS, CLAIMED)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'count'"):
        TimesCount(EACH, (PERSONS,), CLAIMED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_its_count() -> None:
    money = ArtifactKind("ex/money_count", Decimal)
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'count'"):
        TimesCount(EACH, money, CLAIMED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_amount() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'amount'"):
        TimesCount(other_count, PERSONS, CLAIMED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_output() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'output'"):
        TimesCount(EACH, PERSONS, other_count)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(TimesCount, "__type_params__", ())
    assert not getattr(TimesCount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_count_of_one_gets_the_amount() -> None:
    output = compute("16129", 1)

    assert output == Artifact(CLAIMED, D("16129"))
    assert type(output.value) is Decimal


def test_a_count_of_two_gets_twice_the_amount() -> None:
    # 16129 × 2 = 32258.
    assert compute("16129", 2) == Artifact(CLAIMED, D("32258"))


def test_a_larger_count_multiplies_the_amount() -> None:
    # 544 × 7 = 3808.
    assert compute("544", 7) == Artifact(CLAIMED, D("3808"))


def test_a_count_of_zero_gets_zero() -> None:
    output = compute("16129", 0)

    assert output == Artifact(CLAIMED, D("0"))
    assert type(output.value) is Decimal


def test_a_count_of_zero_gets_a_plain_zero() -> None:
    output = compute("16129.50", 0)

    # Not the amount's scale (no "0.00") and never a signed zero.
    assert str(output.value) == "0"
    assert not output.value.is_signed()


def test_a_count_of_zero_of_a_negative_amount_gets_a_plain_zero() -> None:
    output = compute("-250.75", 0)

    assert str(output.value) == "0"
    assert not output.value.is_signed()


def test_a_zero_amount_gets_zero_for_any_count() -> None:
    assert compute("0", 0) == Artifact(CLAIMED, D("0"))
    assert compute("0", 3) == Artifact(CLAIMED, D("0"))
    assert not compute("0", 3).value.is_signed()


def test_a_negative_amount_is_multiplied_as_is_without_a_floor() -> None:
    # -250.75 × 2 = -501.50: the amount is not floored at zero first, nor the product.
    assert compute("-250.75", 2) == Artifact(CLAIMED, D("-501.50"))


def test_keeps_the_amounts_scale() -> None:
    assert str(compute("16129.50", 1).value) == "16129.50"
    assert str(compute("16129.50", 2).value) == "32259.00"


def test_keeps_fractions_of_a_cent_exactly() -> None:
    # 0.333 × 3 = 0.999, not rounded.
    assert str(compute("0.333", 3).value) == "0.999"


def test_keeps_the_product_exact_without_rounding() -> None:
    output = compute("1234567.0000000000000001", 3)

    assert str(output.value) == "3703701.0000000000000003"


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs("16129", 2))))

    assert result.outputs == (Artifact(CLAIMED, D("32258")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs("16129", 2)))

    assert result.outputs == (Artifact(CLAIMED, D("32258")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="amount_each"):
        capability().compute((Artifact(PERSONS, 1),))


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="person_count"):
        capability().compute((Artifact(EACH, D("16129")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_times_count_line() -> None:
    trace = capability().compute(inputs("16129", 1)).trace

    assert trace == (
        TimesCountLine(
            output=CLAIMED,
            amount_kind=EACH,
            amount_value=D("16129"),
            count_kind=PERSONS,
            count=1,
            result=D("16129"),
        ),
    )


def test_traces_a_count_of_zero() -> None:
    trace = capability().compute(inputs("16129.50", 0)).trace

    assert trace == (TimesCountLine(CLAIMED, EACH, D("16129.50"), PERSONS, 0, D("0")),)


def test_traces_the_amount_with_its_own_scale() -> None:
    (line,) = capability().compute(inputs("16129.50", 2)).trace

    assert isinstance(line, TimesCountLine)
    assert str(line.amount_value) == "16129.50"
    assert str(line.result) == "32259.00"


def test_traces_the_count_as_an_int() -> None:
    (line,) = capability().compute(inputs("16129", 3)).trace

    assert isinstance(line, TimesCountLine)
    assert type(line.count) is int
    assert line.count == 3


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute(inputs("16129", 2)).trace

    assert [line.amount for line in trace] == [D("32258")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute(inputs("16129.50", 2))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, TimesCountLine)
    assert line.result == output.value
    assert str(line.result) == str(output.value)


def test_traces_no_per_unit_amount_line() -> None:
    (line,) = capability().compute(inputs("16129", 1)).trace

    assert not isinstance(line, PerUnitAmountLine)


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("16129", 1)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
