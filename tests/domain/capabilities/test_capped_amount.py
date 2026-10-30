"""Unit tests for the CappedAmount capability (`core/capped_amount`), with made-up kinds and values.

Its slots: one parameter slot `cap` (an `amount` dataset), one consumed slot `base` and one
produced slot `output`. The output is min(base, cap), exact, then rounded only with the `cap`
dataset's rule (which defaults to no rounding): a base at or below the cap is produced unchanged,
keeping its scale; above it, the cap's value. It records one `CappedAmountLine`.
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
from tax_engine.domain.capabilities.capped_amount import CappedAmount
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
from tax_engine.domain.trace import CappedAmountLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


GROSS = ArtifactKind("ex/gross_amount", Decimal)
CAPPED = ArtifactKind("ex/capped_amount", Decimal)


def cap(value: str = "1000", rounding: RoundingRule = NO_ROUNDING) -> ParameterDataset[Amount]:
    return ParameterDataset(
        "ex/some_cap", 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/c",)
    )


def capability(cap_data: ParameterDataset[Amount] | None = None) -> CappedAmount:
    """By default the made-up gross amount capped at 1000, exact."""
    return CappedAmount(cap_data or cap(), GROSS, CAPPED)


def compute(wired: CappedAmount, base: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(GROSS, D(base)),)).outputs
    return output


def test_is_registered_as_core_capped_amount() -> None:
    assert CapabilityRegistry.shared().get("core/capped_amount") is CappedAmount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "capped_amount" in core.__all__
    assert core.capped_amount.CappedAmount is CappedAmount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({GROSS})
    assert capability().produces == frozenset({CAPPED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CappedAmount)
    assert "produces" not in vars(CappedAmount)


def test_declares_its_slots() -> None:
    assert CappedAmount.PARAMETERS == {"cap": AMOUNT}
    assert CappedAmount.PARAMETERS["cap"] is AMOUNT
    assert CappedAmount.CONSUMES == {"base": Decimal}
    assert CappedAmount.PRODUCES == {"output": Decimal}
    assert not CappedAmount.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    for slots in (CappedAmount.PARAMETERS, CappedAmount.CONSUMES, CappedAmount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CappedAmount.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(CappedAmount.CONSUMES, Mapping[str, type])
    assert_type(CappedAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (CappedAmount.PARAMETERS, CappedAmount.CONSUMES, CappedAmount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CappedAmount(cap=cap(), base=GROSS, output=CAPPED)

    assert compute(wired, "1500") == Artifact(CAPPED, D("1000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        CappedAmount(cap(), GROSS, CAPPED, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CappedAmount") as raised:
        CappedAmount(cap(), GROSS, GROSS)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="CappedAmount.*'base'"):
        CappedAmount(cap(), (GROSS,), CAPPED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="CappedAmount.*'base'"):
        CappedAmount(cap(), count, CAPPED)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[Amount]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        CappedAmount(rate, GROSS, CAPPED)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CappedAmount, "__type_params__", ())
    assert not getattr(CappedAmount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_base_below_the_cap_is_produced_unchanged() -> None:
    assert compute(capability(), "400.25") == Artifact(CAPPED, D("400.25"))


def test_a_base_above_the_cap_produces_the_cap() -> None:
    output = compute(capability(), "1500")

    assert output == Artifact(CAPPED, D("1000"))
    assert type(output.value) is Decimal


def test_a_base_at_the_cap_produces_the_cap() -> None:
    assert compute(capability(), "1000") == Artifact(CAPPED, D("1000"))


def test_a_base_below_the_cap_keeps_its_scale() -> None:
    assert str(compute(capability(), "400.50").value) == "400.50"


def test_a_base_at_the_cap_keeps_its_own_scale() -> None:
    # Settled on #72: at or below the cap the base is produced unchanged, scale and all.
    assert str(compute(capability(cap("1000")), "1000.00").value) == "1000.00"


def test_a_base_above_the_cap_produces_the_caps_value_as_given() -> None:
    assert str(compute(capability(cap("1000.00")), "1500").value) == "1000.00"


def test_a_base_just_above_the_cap_produces_the_cap() -> None:
    assert compute(capability(), "1000.0000000000000001") == Artifact(CAPPED, D("1000"))


def test_a_base_just_below_the_cap_is_produced_unchanged() -> None:
    output = compute(capability(), "999.9999999999999999")

    assert output == Artifact(CAPPED, D("999.9999999999999999"))


def test_keeps_the_lesser_exact_without_rounding() -> None:
    assert compute(capability(), "123.456789") == Artifact(CAPPED, D("123.456789"))


def test_a_zero_base_produces_zero() -> None:
    assert compute(capability(), "0") == Artifact(CAPPED, D("0"))


def test_a_zero_cap_produces_zero() -> None:
    assert compute(capability(cap("0")), "1234.56") == Artifact(CAPPED, D("0"))


def test_a_negative_base_is_produced_unchanged() -> None:
    # The lesser of a negative base and a cap of zero or more is the base: nothing floors it.
    assert compute(capability(), "-5.25") == Artifact(CAPPED, D("-5.25"))


def test_the_cap_dataset_supplies_the_cap() -> None:
    assert compute(capability(cap("1471")), "2000") == Artifact(CAPPED, D("1471"))


def test_rounds_a_base_below_the_cap_with_the_cap_datasets_rule() -> None:
    wired = capability(cap("1000", CENT))

    assert compute(wired, "400.005") == Artifact(CAPPED, D("400.01"))


def test_rounds_the_cap_with_the_cap_datasets_rule() -> None:
    wired = capability(cap("1000.005", CENT))

    assert compute(wired, "1500") == Artifact(CAPPED, D("1000.01"))


def test_rounds_with_another_rule_of_the_cap_dataset() -> None:
    wired = capability(cap("1000", RoundTo(D("1"), RoundingMode.FLOOR)))

    assert compute(wired, "400.99") == Artifact(CAPPED, D("400"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(cap("1000", CENT))

    assert str(compute(wired, "1500").value) == "1000.00"
    assert str(compute(wired, "7").value) == "7.00"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(GROSS, D("10"))))

    assert result.outputs == (Artifact(CAPPED, D("10")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="gross_amount"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_capped_amount_line() -> None:
    trace = capability().compute((Artifact(GROSS, D("1500")),)).trace

    assert trace == (
        CappedAmountLine(
            output=CAPPED,
            base=GROSS,
            base_amount=D("1500"),
            cap=Amount(D("1000")),
            rounding=NO_ROUNDING,
            result=D("1000"),
        ),
    )


def test_traces_a_base_below_the_cap() -> None:
    trace = capability().compute((Artifact(GROSS, D("400.25")),)).trace

    assert trace == (
        CappedAmountLine(CAPPED, GROSS, D("400.25"), Amount(D("1000")), NO_ROUNDING, D("400.25")),
    )


def test_traces_the_cap_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(cap("1000", CENT)).compute((Artifact(GROSS, D("400.005")),)).trace

    assert trace == (
        CappedAmountLine(CAPPED, GROSS, D("400.005"), Amount(D("1000")), CENT, D("400.01")),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(cap("1000", CENT)).compute((Artifact(GROSS, D("400.005")),)).trace

    assert [line.amount for line in trace] == [D("400.01")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute((Artifact(GROSS, D("1500")),))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, CappedAmountLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(GROSS, D("1500")),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
