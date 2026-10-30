"""Unit tests for the ThresholdGate capability (`ca/threshold_gate`), with made-up kinds and values.

It serves T1 line 45200 (Refundable medical expense supplement), Federal Worksheet (form 5000-D1)
2025 e-text, section "Line 45200 - Refundable medical expense supplement": "In addition, the
total of the following two amounts must be $4,390 or more:" (employment income less deductions,
and net self-employment income). "or more" makes the gate inclusive at the threshold.

Its slots: one parameter slot `threshold` (an `amount` dataset), two consumed slots `amount` and
`gate` and one produced slot `output`. A gate at or above the threshold produces the amount
unchanged, keeping its scale; a gate below it produces 0. The result is rounded only with the
`threshold` dataset's rule (which defaults to no rounding). It records one `ThresholdGateLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.trace import ThresholdGateLine
from tax_engine.jurisdictions.ca.capabilities.threshold_gate import ThresholdGate

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

SUPPLEMENT_BASE = ArtifactKind("ex/supplement_base", Decimal)
WORKING_INCOME = ArtifactKind("ex/working_income", Decimal)
SUPPLEMENT = ArtifactKind("ex/supplement", Decimal)


def threshold(
    value: str = "4390", rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[Amount]:
    return ParameterDataset(
        "ex/some_threshold", 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/t",)
    )


def capability(data: ParameterDataset[Amount] | None = None) -> ThresholdGate:
    """By default the made-up base amount gated on working income of at least 4390, exact."""
    return ThresholdGate(data or threshold(), SUPPLEMENT_BASE, WORKING_INCOME, SUPPLEMENT)


def inputs(amount: str, gate: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(SUPPLEMENT_BASE, D(amount)), Artifact(WORKING_INCOME, D(gate)))


def compute(wired: ThresholdGate, amount: str, gate: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(amount, gate)).outputs
    return output


def test_is_registered_as_ca_threshold_gate() -> None:
    assert CapabilityRegistry.shared().get("ca/threshold_gate") is ThresholdGate


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "threshold_gate" in ca_capabilities.__all__
    assert ca_capabilities.threshold_gate.ThresholdGate is ThresholdGate


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({SUPPLEMENT_BASE, WORKING_INCOME})
    assert capability().produces == frozenset({SUPPLEMENT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ThresholdGate)
    assert "produces" not in vars(ThresholdGate)


def test_declares_its_slots() -> None:
    assert ThresholdGate.PARAMETERS == {"threshold": AMOUNT}
    assert ThresholdGate.PARAMETERS["threshold"] is AMOUNT
    assert ThresholdGate.CONSUMES == {"amount": Decimal, "gate": Decimal}
    assert ThresholdGate.PRODUCES == {"output": Decimal}
    assert not ThresholdGate.is_list_slot("amount")
    assert not ThresholdGate.is_list_slot("gate")


def test_its_slots_are_read_only() -> None:
    for slots in (ThresholdGate.PARAMETERS, ThresholdGate.CONSUMES, ThresholdGate.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ThresholdGate.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(ThresholdGate.CONSUMES, Mapping[str, type])
    assert_type(ThresholdGate.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ThresholdGate.PARAMETERS, ThresholdGate.CONSUMES, ThresholdGate.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ThresholdGate(
        threshold=threshold(), amount=SUPPLEMENT_BASE, gate=WORKING_INCOME, output=SUPPLEMENT
    )

    assert compute(wired, "1500", "4390") == Artifact(SUPPLEMENT, D("1500"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ThresholdGate(  # type: ignore[call-arg]
            threshold(), SUPPLEMENT_BASE, WORKING_INCOME, SUPPLEMENT, NO_ROUNDING
        )


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ThresholdGate") as raised:
        ThresholdGate(threshold(), SUPPLEMENT_BASE, WORKING_INCOME, SUPPLEMENT_BASE)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_gate_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ThresholdGate") as raised:
        ThresholdGate(threshold(), SUPPLEMENT_BASE, WORKING_INCOME, WORKING_INCOME)

    message = str(raised.value)
    assert "'gate'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="ThresholdGate.*'amount'"):
        ThresholdGate(
            threshold(),
            (SUPPLEMENT_BASE,),  # type: ignore[arg-type]
            WORKING_INCOME,
            SUPPLEMENT,
        )


def test_mypy_rejects_wiring_a_gate_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="ThresholdGate.*'gate'"):
        ThresholdGate(threshold(), SUPPLEMENT_BASE, count, SUPPLEMENT)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[Amount]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        ThresholdGate(rate, SUPPLEMENT_BASE, WORKING_INCOME, SUPPLEMENT)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ThresholdGate, "__type_params__", ())
    assert not getattr(ThresholdGate, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_gate_just_below_the_threshold_produces_zero() -> None:
    output = compute(capability(), "1500", "4389.99")

    assert output == Artifact(SUPPLEMENT, D("0"))
    assert type(output.value) is Decimal


def test_a_gate_at_the_threshold_passes_the_amount_through() -> None:
    # "must be $4,390 or more": inclusive at the threshold.
    assert compute(capability(), "1500", "4390") == Artifact(SUPPLEMENT, D("1500"))


def test_a_gate_just_above_the_threshold_passes_the_amount_through() -> None:
    assert compute(capability(), "1500", "4390.01") == Artifact(SUPPLEMENT, D("1500"))


def test_a_gate_far_above_the_threshold_passes_the_amount_through() -> None:
    assert compute(capability(), "1500", "90000") == Artifact(SUPPLEMENT, D("1500"))


def test_a_gate_far_below_the_threshold_produces_zero() -> None:
    assert compute(capability(), "1500", "100") == Artifact(SUPPLEMENT, D("0"))


def test_a_zero_gate_produces_zero() -> None:
    assert compute(capability(), "1500", "0") == Artifact(SUPPLEMENT, D("0"))


def test_a_negative_gate_produces_zero() -> None:
    assert compute(capability(), "1500", "-5") == Artifact(SUPPLEMENT, D("0"))


def test_a_gate_one_digit_short_of_the_threshold_produces_zero() -> None:
    assert compute(capability(), "1500", "4389.9999999999999999") == Artifact(SUPPLEMENT, D("0"))


def test_a_gate_one_digit_over_the_threshold_passes_the_amount_through() -> None:
    assert compute(capability(), "1500", "4390.0000000000000001") == Artifact(SUPPLEMENT, D("1500"))


def test_a_gate_equal_to_the_threshold_at_another_scale_passes_the_amount_through() -> None:
    assert compute(capability(threshold("4390.00")), "1500", "4390") == Artifact(
        SUPPLEMENT, D("1500")
    )
    assert compute(capability(threshold("4390")), "1500", "4390.00") == Artifact(
        SUPPLEMENT, D("1500")
    )


def test_the_threshold_dataset_supplies_the_threshold() -> None:
    assert compute(capability(threshold("5000")), "1500", "4390") == Artifact(SUPPLEMENT, D("0"))
    assert compute(capability(threshold("4000")), "1500", "4390") == Artifact(SUPPLEMENT, D("1500"))


def test_a_zero_threshold_passes_a_zero_gate_through() -> None:
    assert compute(capability(threshold("0")), "1500", "0") == Artifact(SUPPLEMENT, D("1500"))


def test_a_passed_amount_keeps_its_scale() -> None:
    assert str(compute(capability(), "1500.50", "4390").value) == "1500.50"
    assert str(compute(capability(), "1500.00", "9000").value) == "1500.00"


def test_a_passed_amount_is_not_changed_by_the_thresholds_scale() -> None:
    assert str(compute(capability(threshold("4390.00")), "1500", "9000").value) == "1500"


def test_keeps_the_amount_exact_without_rounding() -> None:
    assert compute(capability(), "123.456789", "4390") == Artifact(SUPPLEMENT, D("123.456789"))


def test_a_zero_amount_passes_through_as_zero() -> None:
    assert compute(capability(), "0", "9000") == Artifact(SUPPLEMENT, D("0"))


def test_a_negative_amount_passes_through_unchanged() -> None:
    # The gate only switches the amount on or off; nothing floors it.
    assert compute(capability(), "-5.25", "9000") == Artifact(SUPPLEMENT, D("-5.25"))


def test_the_amount_does_not_move_the_gate() -> None:
    assert compute(capability(), "9000", "4389.99") == Artifact(SUPPLEMENT, D("0"))
    assert compute(capability(), "0.01", "4390") == Artifact(SUPPLEMENT, D("0.01"))


def test_rounds_a_passed_amount_with_the_threshold_datasets_rule() -> None:
    wired = capability(threshold("4390", CENT))

    assert compute(wired, "400.005", "9000") == Artifact(SUPPLEMENT, D("400.01"))


def test_rounds_with_another_rule_of_the_threshold_dataset() -> None:
    wired = capability(threshold("4390", RoundTo(D("1"), RoundingMode.FLOOR)))

    assert compute(wired, "400.99", "9000") == Artifact(SUPPLEMENT, D("400"))


def test_a_rounded_zero_carries_the_increments_scale() -> None:
    wired = capability(threshold("4390", CENT))

    assert str(compute(wired, "1500", "100").value) == "0.00"


def test_a_rounded_amount_carries_the_increments_scale() -> None:
    wired = capability(threshold("4390", CENT))

    assert str(compute(wired, "7", "9000").value) == "7.00"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs("10", "4390")))

    assert result.outputs == (Artifact(SUPPLEMENT, D("10")),)


def test_takes_each_input_by_its_kind_not_its_position() -> None:
    result = capability().compute(tuple(reversed(inputs("1500", "4390"))))

    assert result.outputs == (Artifact(SUPPLEMENT, D("1500")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="supplement_base"):
        capability().compute((Artifact(WORKING_INCOME, D("4390")),))


def test_a_missing_gate_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="working_income"):
        capability().compute((Artifact(SUPPLEMENT_BASE, D("1500")),))


def test_no_inputs_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())


# --- worked example ---------------------------------------------------------------------------
#
# Lina, 30. Lines 21500 and 33200 total 6,000, giving 25% x 6,000 = 1,500 (line 13), under the
# maximum of 1,504 (line 14). Adjusted family net income 20,000, no reduction (line 15 is 0), so
# line 16 is 1,500. Working income 4,300: the supplement is 0. Working income 4,390: 1,500.


def test_lina_with_working_income_of_4300_gets_nothing() -> None:
    assert compute(capability(), "1500", "4300") == Artifact(SUPPLEMENT, D("0"))


def test_lina_with_working_income_of_4390_gets_1500() -> None:
    assert compute(capability(), "1500", "4390") == Artifact(SUPPLEMENT, D("1500"))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_threshold_gate_line() -> None:
    trace = capability().compute(inputs("1500", "4390")).trace

    assert trace == (
        ThresholdGateLine(
            output=SUPPLEMENT,
            amount_kind=SUPPLEMENT_BASE,
            amount_value=D("1500"),
            gate_kind=WORKING_INCOME,
            gate_value=D("4390"),
            threshold=Amount(D("4390")),
            rounding=NO_ROUNDING,
            result=D("1500"),
        ),
    )


def test_traces_a_gate_below_the_threshold_with_a_zero_result() -> None:
    trace = capability().compute(inputs("1500", "4389.99")).trace

    assert trace == (
        ThresholdGateLine(
            SUPPLEMENT,
            SUPPLEMENT_BASE,
            D("1500"),
            WORKING_INCOME,
            D("4389.99"),
            Amount(D("4390")),
            NO_ROUNDING,
            D("0"),
        ),
    )


def test_traces_the_threshold_as_given() -> None:
    trace = capability(threshold("4390.00")).compute(inputs("1500", "9000")).trace

    (line,) = trace
    assert isinstance(line, ThresholdGateLine)
    assert str(line.threshold.value) == "4390.00"


def test_traces_the_threshold_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(threshold("4390", CENT)).compute(inputs("400.005", "9000")).trace

    assert trace == (
        ThresholdGateLine(
            SUPPLEMENT,
            SUPPLEMENT_BASE,
            D("400.005"),
            WORKING_INCOME,
            D("9000"),
            Amount(D("4390")),
            CENT,
            D("400.01"),
        ),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(threshold("4390", CENT)).compute(inputs("400.005", "9000")).trace

    assert [line.amount for line in trace] == [D("400.01")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute(inputs("1500", "100"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, ThresholdGateLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("1500", "4390")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
