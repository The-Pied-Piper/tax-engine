"""Unit tests for the Subtract capability (`core/subtract`), with made-up kinds and values.

Its slots: two consumed single slots, `amount` and `less`, one produced slot `output`, no
parameter slots. The output is amount − less, exact, with no rounding (a subtraction has no
dataset) and no floor: a negative difference is produced as is. It records one `SubtractedLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.domain.capabilities as core
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import SubtractedLine

D = Decimal


GROSS = ArtifactKind("ex/gross_amount", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)
NET = ArtifactKind("ex/net_amount", Decimal)


def capability() -> Subtract:
    """By default the made-up gross amount less the made-up reduction."""
    return Subtract(GROSS, REDUCTION, NET)


def inputs(amount: str, less: str) -> tuple[Artifact[Decimal], ...]:
    return (Artifact(GROSS, D(amount)), Artifact(REDUCTION, D(less)))


def compute(amount: str, less: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(amount, less)).outputs
    return output


def test_is_registered_as_core_subtract() -> None:
    assert CapabilityRegistry.shared().get("core/subtract") is Subtract


def test_is_exported_from_the_capabilities_package() -> None:
    assert "subtract" in core.__all__
    assert core.subtract.Subtract is Subtract


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({GROSS, REDUCTION})
    assert capability().produces == frozenset({NET})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(Subtract)
    assert "produces" not in vars(Subtract)


def test_declares_its_slots() -> None:
    assert Subtract.PARAMETERS == {}
    assert Subtract.CONSUMES == {"amount": Decimal, "less": Decimal}
    assert Subtract.PRODUCES == {"output": Decimal}
    assert not Subtract.is_list_slot("amount")
    assert not Subtract.is_list_slot("less")
    assert not Subtract.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (Subtract.PARAMETERS, Subtract.CONSUMES, Subtract.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(Subtract.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(Subtract.CONSUMES, Mapping[str, type])
    assert_type(Subtract.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (Subtract.PARAMETERS, Subtract.CONSUMES, Subtract.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = Subtract(amount=GROSS, less=REDUCTION, output=NET)

    result = wired.compute(inputs("100", "30"))

    assert result.outputs == (Artifact(NET, D("70")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        Subtract(GROSS, REDUCTION, NET, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_amount_and_less() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract") as raised:
        Subtract(GROSS, GROSS, NET)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'less'" in message


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract") as raised:
        Subtract(GROSS, REDUCTION, GROSS)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_less_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract") as raised:
        Subtract(GROSS, REDUCTION, REDUCTION)

    message = str(raised.value)
    assert "'less'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract.*'amount'"):
        Subtract((GROSS,), REDUCTION, NET)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_what_it_takes_off() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract.*'less'"):
        Subtract(GROSS, (REDUCTION,), NET)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="Subtract.*'less'"):
        Subtract(GROSS, count, NET)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(Subtract, "__type_params__", ())
    assert not getattr(Subtract, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_amount_less_the_other() -> None:
    assert compute("100.25", "40") == Artifact(NET, D("60.25"))


def test_equal_amounts_produce_zero() -> None:
    output = compute("40.50", "40.50")

    assert output == Artifact(NET, D("0"))
    assert type(output.value) is Decimal


def test_taking_off_zero_produces_the_amount() -> None:
    assert compute("1234.56", "0") == Artifact(NET, D("1234.56"))


def test_a_larger_less_produces_a_negative_result_without_a_floor() -> None:
    output = compute("10", "25.5")

    assert output == Artifact(NET, D("-15.5"))
    assert output.value < 0


def test_takes_a_negative_amount_off_as_is() -> None:
    assert compute("100", "-20") == Artifact(NET, D("120"))


def test_subtracts_exactly_with_many_decimals() -> None:
    output = compute("1234567.0000000000000003", "0.0000000000000001")

    assert output == Artifact(NET, D("1234567.0000000000000002"))
    assert type(output.value) is Decimal


def test_subtracts_decimals_float_would_not() -> None:
    assert compute("0.3", "0.1") == Artifact(NET, D("0.2"))


def test_does_not_round_the_difference() -> None:
    assert compute("0.005", "0.0049") == Artifact(NET, D("0.0001"))


def test_keeps_the_scale_of_the_exact_difference() -> None:
    assert str(compute("100.00", "40").value) == "60.00"


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs("100", "30"))))

    assert result.outputs == (Artifact(NET, D("70")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs("10", "4")))

    assert result.outputs == (Artifact(NET, D("6")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="gross_amount"):
        capability().compute((Artifact(REDUCTION, D("1")),))


def test_a_missing_less_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="reduction"):
        capability().compute((Artifact(GROSS, D("1")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_subtracted_line() -> None:
    trace = capability().compute(inputs("100.25", "40")).trace

    assert trace == (
        SubtractedLine(
            output=NET,
            minuend=GROSS,
            minuend_amount=D("100.25"),
            subtrahend=REDUCTION,
            subtrahend_amount=D("40"),
            result=D("60.25"),
        ),
    )


def test_traces_a_negative_result() -> None:
    trace = capability().compute(inputs("10", "25.5")).trace

    assert trace == (SubtractedLine(NET, GROSS, D("10"), REDUCTION, D("25.5"), D("-15.5")),)


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute(inputs("10", "25.5")).trace

    assert [line.amount for line in trace] == [D("-15.5")]


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("100", "30")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
