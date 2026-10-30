"""Unit tests for the ApplyRate capability (`core/apply_rate`), with made-up kinds and values.

Its slots: one parameter slot `rate` (a `rate` dataset), one consumed slot `base` and one produced
slot `output`. The output is base × rate, exact, rounded only with the `rate` dataset's rule
(which defaults to no rounding); it records one `RateAppliedLine`.
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
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.trace import RateAppliedLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


GROSS = ArtifactKind("ex/gross_amount", Decimal)
RATED = ArtifactKind("ex/rated_amount", Decimal)


def rate(value: str = "0.5", rounding: RoundingRule = NO_ROUNDING) -> ParameterDataset[Rate]:
    return ParameterDataset(
        "ex/portion_rate", 2025, RATE, Rate(D(value)), rounding, ("https://example.org/r",)
    )


def capability(rate_data: ParameterDataset[Rate] | None = None) -> ApplyRate:
    """By default 50% of the made-up gross amount, exact."""
    return ApplyRate(rate_data or rate(), GROSS, RATED)


def compute(wired: ApplyRate, base: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(GROSS, D(base)),)).outputs
    return output


def test_is_registered_as_core_apply_rate() -> None:
    assert CapabilityRegistry.shared().get("core/apply_rate") is ApplyRate


def test_is_exported_from_the_capabilities_package() -> None:
    assert "apply_rate" in core.__all__
    assert core.apply_rate.ApplyRate is ApplyRate


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({GROSS})
    assert capability().produces == frozenset({RATED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ApplyRate)
    assert "produces" not in vars(ApplyRate)


def test_declares_its_slots() -> None:
    assert ApplyRate.PARAMETERS == {"rate": RATE}
    assert ApplyRate.PARAMETERS["rate"] is RATE
    assert ApplyRate.CONSUMES == {"base": Decimal}
    assert ApplyRate.PRODUCES == {"output": Decimal}
    assert not ApplyRate.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    for slots in (ApplyRate.PARAMETERS, ApplyRate.CONSUMES, ApplyRate.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ApplyRate.PARAMETERS, Mapping[str, ParameterKind[Rate]])
    assert_type(ApplyRate.CONSUMES, Mapping[str, type])
    assert_type(ApplyRate.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ApplyRate.PARAMETERS, ApplyRate.CONSUMES, ApplyRate.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ApplyRate(rate=rate(), base=GROSS, output=RATED)

    assert compute(wired, "1000") == Artifact(RATED, D("500.0"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ApplyRate(rate(), GROSS, RATED, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyRate") as raised:
        ApplyRate(rate(), GROSS, GROSS)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyRate.*'base'"):
        ApplyRate(rate(), (GROSS,), RATED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="ApplyRate.*'base'"):
        ApplyRate(rate(), count, RATED)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A credit dataset is not a ParameterDataset[Rate]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        credit = ParameterDataset(
            "ex/some_credit", 2025, CREDIT, Credit(D("1")), NO_ROUNDING, ("https://example.org/c",)
        )
        ApplyRate(credit, GROSS, RATED)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ApplyRate, "__type_params__", ())
    assert not getattr(ApplyRate, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_base_times_the_rate() -> None:
    assert compute(capability(), "1000") == Artifact(RATED, D("500.0"))


def test_keeps_the_product_exact_without_rounding() -> None:
    wired = capability(rate("0.125"))

    assert compute(wired, "1000.05") == Artifact(RATED, D("125.00625"))


def test_multiplies_exactly_with_many_decimals() -> None:
    wired = capability(rate("0.3"))

    output = compute(wired, "1234567.0000000000000001")

    assert output == Artifact(RATED, D("370370.10000000000000003"))
    assert type(output.value) is Decimal


def test_multiplies_decimals_float_would_not() -> None:
    assert compute(capability(rate("0.1")), "0.3") == Artifact(RATED, D("0.03"))


def test_rounds_with_the_rate_datasets_rule() -> None:
    wired = capability(rate("0.5", CENT))  # 100.005

    assert compute(wired, "200.01") == Artifact(RATED, D("100.01"))


def test_rounds_with_another_rule_of_the_rate_dataset() -> None:
    wired = capability(rate("0.5", RoundTo(D("1"), RoundingMode.FLOOR)))  # 100.995

    assert compute(wired, "201.99") == Artifact(RATED, D("100"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(rate("0.5", CENT))

    assert str(compute(wired, "14").value) == "7.00"


def test_a_zero_rate_produces_zero() -> None:
    output = compute(capability(rate("0")), "1234.56")

    assert output == Artifact(RATED, D("0"))
    assert type(output.value) is Decimal


def test_a_rate_of_one_produces_the_base() -> None:
    assert compute(capability(rate("1")), "1234.56") == Artifact(RATED, D("1234.56"))


def test_a_zero_base_produces_zero() -> None:
    assert compute(capability(), "0") == Artifact(RATED, D("0"))


def test_the_rate_dataset_supplies_the_rate() -> None:
    assert compute(capability(rate("0.75")), "1000") == Artifact(RATED, D("750"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(GROSS, D("10"))))

    assert result.outputs == (Artifact(RATED, D("5.0")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="gross_amount"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_rate_applied_line() -> None:
    trace = capability().compute((Artifact(GROSS, D("1000")),)).trace

    assert trace == (
        RateAppliedLine(
            output=RATED,
            base=GROSS,
            base_amount=D("1000"),
            rate=Rate(D("0.5")),
            rounding=NO_ROUNDING,
            result=D("500.0"),
        ),
    )


def test_traces_the_rate_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(rate("0.5", CENT)).compute((Artifact(GROSS, D("200.01")),)).trace

    assert trace == (RateAppliedLine(RATED, GROSS, D("200.01"), Rate(D("0.5")), CENT, D("100.01")),)


def test_trace_amount_is_the_result() -> None:
    trace = capability(rate("0.5", CENT)).compute((Artifact(GROSS, D("200.01")),)).trace

    assert [line.amount for line in trace] == [D("100.01")]


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(GROSS, D("1000")),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
