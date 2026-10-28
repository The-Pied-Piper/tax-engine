"""Unit tests for the AtMost capability (`core/at_most`), with made-up kinds and values.

Its slots: two consumed single slots, `amount` and `bound`, one produced slot `output`, no
parameter slots. The output is the amount, unchanged and exact, when it is at most the bound (it
has no dataset, so it never rounds, and no floor); an amount above the bound is an input error,
`InputAboveBoundError`, naming both kinds and their values, not capped. It records one
`AtMostLine` holding the amount and the bound.
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
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    DomainError,
    InputAboveBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import AtMostLine

D = Decimal


CLAIMED = ArtifactKind("ex/claimed_amount", Decimal)
LIMIT = ArtifactKind("ex/claim_limit", Decimal)
ALLOWED = ArtifactKind("ex/allowed_amount", Decimal)


def capability() -> AtMost:
    """By default the made-up claimed amount, at most the made-up claim limit."""
    return AtMost(CLAIMED, LIMIT, ALLOWED)


def inputs(amount: str, bound: str) -> tuple[Artifact[Decimal], ...]:
    return (Artifact(CLAIMED, D(amount)), Artifact(LIMIT, D(bound)))


def compute(amount: str, bound: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(amount, bound)).outputs
    return output


def test_is_registered_as_core_at_most() -> None:
    assert CapabilityRegistry.shared().get("core/at_most") is AtMost


def test_is_exported_from_the_capabilities_package() -> None:
    assert "at_most" in core.__all__
    assert core.at_most.AtMost is AtMost


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLAIMED, LIMIT})
    assert capability().produces == frozenset({ALLOWED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(AtMost)
    assert "produces" not in vars(AtMost)


def test_declares_its_slots() -> None:
    assert AtMost.PARAMETERS == {}
    assert AtMost.CONSUMES == {"amount": Decimal, "bound": Decimal}
    assert AtMost.PRODUCES == {"output": Decimal}
    assert not AtMost.is_list_slot("amount")
    assert not AtMost.is_list_slot("bound")
    assert not AtMost.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (AtMost.PARAMETERS, AtMost.CONSUMES, AtMost.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(AtMost.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(AtMost.CONSUMES, Mapping[str, type])
    assert_type(AtMost.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (AtMost.PARAMETERS, AtMost.CONSUMES, AtMost.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = AtMost(amount=CLAIMED, bound=LIMIT, output=ALLOWED)

    result = wired.compute(inputs("40", "100"))

    assert result.outputs == (Artifact(ALLOWED, D("40")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        AtMost(CLAIMED, LIMIT, ALLOWED, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_amount_and_bound() -> None:
    with pytest.raises(InvalidCapabilityError, match="AtMost") as raised:
        AtMost(CLAIMED, CLAIMED, ALLOWED)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'bound'" in message


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="AtMost") as raised:
        AtMost(CLAIMED, LIMIT, CLAIMED)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_bound_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="AtMost") as raised:
        AtMost(CLAIMED, LIMIT, LIMIT)

    message = str(raised.value)
    assert "'bound'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="AtMost.*'amount'"):
        AtMost((CLAIMED,), LIMIT, ALLOWED)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_bound() -> None:
    with pytest.raises(InvalidCapabilityError, match="AtMost.*'bound'"):
        AtMost(CLAIMED, (LIMIT,), ALLOWED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="AtMost.*'bound'"):
        AtMost(CLAIMED, count, ALLOWED)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(AtMost, "__type_params__", ())
    assert not getattr(AtMost, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_an_amount_below_the_bound_is_produced_unchanged() -> None:
    assert compute("40", "100") == Artifact(ALLOWED, D("40"))


def test_an_amount_equal_to_the_bound_is_produced_unchanged() -> None:
    assert compute("1926", "1926") == Artifact(ALLOWED, D("1926"))


def test_an_amount_equal_to_the_bound_at_another_scale_keeps_its_own_scale() -> None:
    output = compute("40.50", "40.5")

    assert output == Artifact(ALLOWED, D("40.50"))
    assert str(output.value) == "40.50"


def test_an_amount_equal_to_the_bound_is_produced_not_the_bound() -> None:
    assert str(compute("40.5", "40.50").value) == "40.5"


def test_a_zero_amount_is_produced_unchanged() -> None:
    output = compute("0", "1926")

    assert output == Artifact(ALLOWED, D("0"))
    assert type(output.value) is Decimal


def test_a_zero_amount_is_at_most_a_zero_bound() -> None:
    assert compute("0", "0") == Artifact(ALLOWED, D("0"))


def test_a_negative_amount_is_produced_as_is_without_a_floor() -> None:
    assert compute("-15.5", "0") == Artifact(ALLOWED, D("-15.5"))


def test_the_amount_keeps_its_scale() -> None:
    assert str(compute("100.10", "200").value) == "100.10"


def test_keeps_the_amount_exact_without_rounding() -> None:
    output = compute("1234567.0000000000000001", "1234567.0000000000000002")

    assert str(output.value) == "1234567.0000000000000001"


def test_does_not_round_the_amount() -> None:
    assert str(compute("0.0049", "0.005").value) == "0.0049"


def test_produces_a_decimal() -> None:
    assert type(compute("1", "2").value) is Decimal


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs("40", "100"))))

    assert result.outputs == (Artifact(ALLOWED, D("40")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("1")), *inputs("40", "100")))

    assert result.outputs == (Artifact(ALLOWED, D("40")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="claimed_amount"):
        capability().compute((Artifact(LIMIT, D("1")),))


def test_a_missing_bound_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="claim_limit"):
        capability().compute((Artifact(CLAIMED, D("1")),))


# --- an amount above the bound ----------------------------------------------------------------


def test_an_amount_above_the_bound_is_an_input_above_bound_error() -> None:
    with pytest.raises(InputAboveBoundError):
        compute("3000", "1926")


def test_the_error_names_both_kinds_and_their_values() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute("3000", "1926")

    assert str(raised.value) == "ex/claimed_amount 3000 is above ex/claim_limit 1926"


def test_the_error_gives_both_values_as_they_were_given() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute("40.51", "40.50")

    assert str(raised.value) == "ex/claimed_amount 40.51 is above ex/claim_limit 40.50"


def test_an_amount_just_above_the_bound_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ex/claimed_amount.*ex/claim_limit"):
        compute("100.0000000000000001", "100")


def test_a_positive_amount_above_a_zero_bound_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ex/claimed_amount 0.01 .*ex/claim_limit 0"):
        compute("0.01", "0")


def test_an_amount_above_a_negative_bound_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ex/claimed_amount 0 .*ex/claim_limit -1"):
        compute("0", "-1")


def test_the_amount_is_not_capped_at_the_bound() -> None:
    with pytest.raises(InputAboveBoundError):
        capability().compute(inputs("1926.01", "1926"))


def test_an_input_above_bound_error_is_a_domain_error() -> None:
    assert issubclass(InputAboveBoundError, DomainError)


def test_an_input_above_bound_error_is_not_a_wiring_error() -> None:
    assert not issubclass(InputAboveBoundError, InvalidCapabilityError)


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_at_most_line() -> None:
    trace = capability().compute(inputs("40", "100")).trace

    assert trace == (
        AtMostLine(
            output=ALLOWED,
            amount_kind=CLAIMED,
            amount_value=D("40"),
            bound=LIMIT,
            bound_value=D("100"),
        ),
    )


def test_traces_an_amount_equal_to_the_bound() -> None:
    trace = capability().compute(inputs("1926", "1926")).trace

    assert trace == (AtMostLine(ALLOWED, CLAIMED, D("1926"), LIMIT, D("1926")),)


def test_traces_both_values_with_their_own_scale() -> None:
    (line,) = capability().compute(inputs("40.5", "40.50")).trace

    assert isinstance(line, AtMostLine)
    assert str(line.amount_value) == "40.5"
    assert str(line.bound_value) == "40.50"


def test_trace_amount_is_the_amount() -> None:
    trace = capability().compute(inputs("40", "100")).trace

    assert [line.amount for line in trace] == [D("40")]


def test_trace_amount_is_the_output() -> None:
    result = capability().compute(inputs("7.25", "8"))

    (output,) = result.outputs
    (line,) = result.trace
    assert line.amount == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("40", "100")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
