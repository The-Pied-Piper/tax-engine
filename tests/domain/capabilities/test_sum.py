"""Unit tests for the Sum capability (`core/sum`), with made-up kinds.

Its slots: one consumed list slot `parts` (a tuple of money kinds, possibly empty), one produced
slot `output`, no parameter slots. It adds the parts' values exactly, with no rounding (a sum has
no dataset), and records one `SumLine` holding each part in the order it was wired.
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
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import SumLine

D = Decimal


PART_ONE = ArtifactKind("ex/part_one", Decimal)
PART_TWO = ArtifactKind("ex/part_two", Decimal)
PART_THREE = ArtifactKind("ex/part_three", Decimal)
TOTAL = ArtifactKind("ex/total", Decimal)


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
    assert CapabilityRegistry.shared().get("core/sum") is Sum


def test_is_exported_from_the_capabilities_package() -> None:
    assert "sum" in core.__all__
    assert core.sum.Sum is Sum


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
    count = ArtifactKind("ex/count", int)

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
