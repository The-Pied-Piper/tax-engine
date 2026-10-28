"""Unit tests for the SumNotBelowZero capability (`core/sum_not_below_zero`), made-up kinds.

Its slots are those of `core/sum`: one consumed list slot `parts` (a tuple of money kinds,
possibly empty), one produced slot `output`, no parameter slots. The output is
max(sum of the parts, 0), exact, with no rounding (it has no dataset): the floor of a line the
form prints with "if negative, enter 0" after adding. It records one `SumNotBelowZeroLine`
holding each part in the order it was wired, whether or not the floor applied.
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
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import SumLine, SumNotBelowZeroLine

D = Decimal


PART_ONE = ArtifactKind("ex/part_one", Decimal)
PART_TWO = ArtifactKind("ex/part_two", Decimal)
PART_THREE = ArtifactKind("ex/part_three", Decimal)
TOTAL = ArtifactKind("ex/total", Decimal)


def capability() -> SumNotBelowZero:
    """By default the three made-up parts, in order one, two, three."""
    return SumNotBelowZero((PART_ONE, PART_TWO, PART_THREE), TOTAL)


def parts(one: str, two: str, three: str) -> tuple[Artifact[Decimal], ...]:
    return (
        Artifact(PART_ONE, D(one)),
        Artifact(PART_TWO, D(two)),
        Artifact(PART_THREE, D(three)),
    )


def compute(one: str, two: str, three: str) -> Artifact[Any]:
    (output,) = capability().compute(parts(one, two, three)).outputs
    return output


def test_is_registered_as_core_sum_not_below_zero() -> None:
    assert CapabilityRegistry.shared().get("core/sum_not_below_zero") is SumNotBelowZero


def test_leaves_core_sum_registered_as_the_unfloored_sum() -> None:
    assert CapabilityRegistry.shared().get("core/sum") is Sum


def test_is_exported_from_the_capabilities_package() -> None:
    assert "sum_not_below_zero" in core.__all__
    assert core.sum_not_below_zero.SumNotBelowZero is SumNotBelowZero


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({PART_ONE, PART_TWO, PART_THREE})
    assert capability().produces == frozenset({TOTAL})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(SumNotBelowZero)
    assert "produces" not in vars(SumNotBelowZero)


def test_declares_the_slots_of_core_sum() -> None:
    assert SumNotBelowZero.PARAMETERS == {}
    assert SumNotBelowZero.CONSUMES == {"parts": list[Decimal]}
    assert SumNotBelowZero.PRODUCES == {"output": Decimal}
    assert SumNotBelowZero.is_list_slot("parts")
    assert not SumNotBelowZero.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (
        SumNotBelowZero.PARAMETERS,
        SumNotBelowZero.CONSUMES,
        SumNotBelowZero.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(SumNotBelowZero.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(SumNotBelowZero.CONSUMES, Mapping[str, type])
    assert_type(SumNotBelowZero.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        SumNotBelowZero.PARAMETERS,
        SumNotBelowZero.CONSUMES,
        SumNotBelowZero.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = SumNotBelowZero(parts=(PART_ONE, PART_TWO, PART_THREE), output=TOTAL)

    result = wired.compute(parts("100.25", "40", "9.75"))

    assert result.outputs == (Artifact(TOTAL, D("150.00")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        SumNotBelowZero((PART_ONE,), TOTAL, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_a_part_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero") as raised:
        SumNotBelowZero((PART_ONE, TOTAL), TOTAL)

    message = str(raised.value)
    assert "'parts'" in message
    assert "'output'" in message


def test_rejects_a_part_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero.*'parts'"):
        SumNotBelowZero((PART_ONE, PART_TWO, PART_ONE), TOTAL)


def test_rejects_a_single_kind_for_its_parts() -> None:
    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero.*'parts'"):
        SumNotBelowZero(PART_ONE, TOTAL)  # type: ignore[arg-type]


def test_rejects_a_part_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero.*'parts'"):
        SumNotBelowZero((PART_ONE, count), TOTAL)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(SumNotBelowZero, "__type_params__", ())
    assert not getattr(SumNotBelowZero, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_positive_total_is_produced_unchanged() -> None:
    assert compute("100.25", "40", "9.75") == Artifact(TOTAL, D("150.00"))


def test_keeps_the_scale_of_a_positive_total() -> None:
    assert str(compute("100.25", "40", "9.75").value) == "150.00"


def test_negative_parts_are_added_as_they_are() -> None:
    assert compute("100", "-30", "-20.5") == Artifact(TOTAL, D("49.5"))


def test_one_part_is_its_own_total() -> None:
    wired = SumNotBelowZero((PART_TWO,), TOTAL)

    result = wired.compute((Artifact(PART_TWO, D("40.5")),))

    assert result.outputs == (Artifact(TOTAL, D("40.5")),)


def test_one_negative_part_is_floored_at_zero() -> None:
    wired = SumNotBelowZero((PART_TWO,), TOTAL)

    result = wired.compute((Artifact(PART_TWO, D("-40.5")),))

    assert result.outputs == (Artifact(TOTAL, D("0")),)


def test_a_negative_total_is_floored_at_zero() -> None:
    output = compute("10", "-25.5", "5")

    assert output == Artifact(TOTAL, D("0"))
    assert type(output.value) is Decimal


def test_the_floor_is_a_plain_decimal_zero() -> None:
    # Like `core/subtract_not_below_zero`: when the floor applies, the output is `Decimal(0)`,
    # not the sum's scale (no "0.00") and never a negative zero.
    value = compute("10.00", "-25.50", "5.00").value

    assert type(value) is Decimal
    assert str(value) == "0"
    assert not value.is_signed()


def test_a_total_of_exactly_zero_is_a_plain_zero() -> None:
    # A tie at zero is never signed: -0.00 + 0.00 style sums give a plain 0.
    value = compute("40.50", "-40.50", "0.00").value

    assert value == D("0")
    assert str(value) == "0"
    assert not value.is_signed()


def test_negative_zero_parts_give_a_plain_zero() -> None:
    value = compute("-0", "-0.00", "0").value

    assert str(value) == "0"
    assert not value.is_signed()


def test_a_total_just_below_zero_is_floored() -> None:
    assert compute("0.0000000000000001", "-0.0000000000000002", "0") == Artifact(TOTAL, D("0"))


def test_zero_parts_sum_to_zero() -> None:
    wired = SumNotBelowZero((), TOTAL)

    result = wired.compute(())

    assert result.outputs == (Artifact(TOTAL, D(0)),)
    assert type(result.outputs[0].value) is Decimal
    assert str(result.outputs[0].value) == "0"
    assert wired.consumes == frozenset()


def test_adds_exactly_with_many_decimals() -> None:
    output = compute("0.1", "0.2", "1234567.0000000000000001")

    assert output == Artifact(TOTAL, D("1234567.3000000000000001"))


def test_adds_decimals_float_would_not() -> None:
    assert compute("0.1", "0.2", "0") == Artifact(TOTAL, D("0.3"))


def test_does_not_round_the_total() -> None:
    wired = SumNotBelowZero((PART_ONE, PART_TWO), TOTAL)

    result = wired.compute((Artifact(PART_ONE, D("0.005")), Artifact(PART_TWO, D("0.0049"))))

    assert result.outputs == (Artifact(TOTAL, D("0.0099")),)


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(parts("100.25", "40", "9.75"))))

    assert result.outputs == (Artifact(TOTAL, D("150.00")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *parts("1", "2", "3")))

    assert result.outputs == (Artifact(TOTAL, D("6")),)


def test_a_missing_part_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="part_three"):
        capability().compute(parts("1", "2", "3")[:2])


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_with_each_part_and_the_total() -> None:
    trace = capability().compute(parts("100.25", "40", "9.75")).trace

    assert trace == (
        SumNotBelowZeroLine(
            output=TOTAL,
            parts=((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))),
            total=D("150.00"),
        ),
    )


def test_traces_the_floored_total() -> None:
    trace = capability().compute(parts("10", "-25.5", "5")).trace

    assert trace == (
        SumNotBelowZeroLine(
            TOTAL,
            ((PART_ONE, D("10")), (PART_TWO, D("-25.5")), (PART_THREE, D("5"))),
            D("0"),
        ),
    )


def test_traces_the_parts_in_the_order_they_were_wired() -> None:
    wired = SumNotBelowZero((PART_THREE, PART_ONE, PART_TWO), TOTAL)

    trace = wired.compute(parts("100.25", "40", "9.75")).trace

    assert trace == (
        SumNotBelowZeroLine(
            TOTAL,
            ((PART_THREE, D("9.75")), (PART_ONE, D("100.25")), (PART_TWO, D("40"))),
            D("150.00"),
        ),
    )


def test_traces_zero_parts() -> None:
    trace = SumNotBelowZero((), TOTAL).compute(()).trace

    assert trace == (SumNotBelowZeroLine(TOTAL, (), D(0)),)


def test_traces_a_floored_line_not_a_plain_sum_line() -> None:
    (line,) = capability().compute(parts("10", "-25.5", "5")).trace

    assert type(line) is SumNotBelowZeroLine
    assert cast(Any, line) != SumLine(
        TOTAL, ((PART_ONE, D("10")), (PART_TWO, D("-25.5")), (PART_THREE, D("5"))), D("0")
    )


def test_trace_amount_is_the_floored_total() -> None:
    trace = capability().compute(parts("10", "-25.5", "5")).trace

    assert [line.amount for line in trace] == [D("0")]


def test_trace_total_is_the_output() -> None:
    result = capability().compute(parts("100.25", "40", "9.75"))

    assert [line.amount for line in result.trace] == [output.value for output in result.outputs]


def test_trace_holds_no_text() -> None:
    trace = capability().compute(parts("10", "-25.5", "5")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
