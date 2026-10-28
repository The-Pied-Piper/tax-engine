"""Unit tests for the PerUnitAmount capability (`core/per_unit_amount`), made-up values.

Its slots: one parameter slot `amount` (an `amount` dataset, the amount for each unit), one
consumed slot `count` (an `int` artifact, the number of units) and one produced slot `output`.
The output is `rounding.apply(amount × count)`: the product of a Decimal and an int, rounded once
with the `amount` dataset's rule (which defaults to no rounding), like `core/credit_amount`; the
per-unit amount itself is never rounded first. It records one `PerUnitAmountLine` holding the
count's kind, the count, the per-unit amount, the rounding rule and the result.
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
from tax_calculator.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.trace import PerUnitAmountLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


CHILDREN = ArtifactKind("ex/child_count", int)
CHILD_AMOUNT = ArtifactKind("ex/child_amount", Decimal)


def per_unit(value: str = "544", rounding: RoundingRule = NO_ROUNDING) -> ParameterDataset[Amount]:
    """By default a made-up 544 for each unit, exact."""
    return ParameterDataset(
        "ex/some_amount_per_unit",
        2025,
        AMOUNT,
        Amount(D(value)),
        rounding,
        ("https://example.org/p",),
    )


def capability(amount: ParameterDataset[Amount] | None = None) -> PerUnitAmount:
    """By default the made-up count of children at 544 each."""
    return PerUnitAmount(amount or per_unit(), CHILDREN, CHILD_AMOUNT)


def compute(wired: PerUnitAmount, count: int) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(CHILDREN, count),)).outputs
    return output


def test_is_registered_as_core_per_unit_amount() -> None:
    assert CapabilityRegistry.shared().get("core/per_unit_amount") is PerUnitAmount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "per_unit_amount" in core.__all__
    assert core.per_unit_amount.PerUnitAmount is PerUnitAmount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CHILDREN})
    assert capability().produces == frozenset({CHILD_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(PerUnitAmount)
    assert "produces" not in vars(PerUnitAmount)


def test_declares_its_slots() -> None:
    assert PerUnitAmount.PARAMETERS == {"amount": AMOUNT}
    assert PerUnitAmount.PARAMETERS["amount"] is AMOUNT
    assert PerUnitAmount.CONSUMES == {"count": int}
    assert PerUnitAmount.CONSUMES["count"] is int
    assert PerUnitAmount.PRODUCES == {"output": Decimal}
    assert not PerUnitAmount.is_list_slot("count")


def test_its_slots_are_read_only() -> None:
    for slots in (PerUnitAmount.PARAMETERS, PerUnitAmount.CONSUMES, PerUnitAmount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(PerUnitAmount.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(PerUnitAmount.CONSUMES, Mapping[str, type])
    assert_type(PerUnitAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (PerUnitAmount.PARAMETERS, PerUnitAmount.CONSUMES, PerUnitAmount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = PerUnitAmount(amount=per_unit(), count=CHILDREN, output=CHILD_AMOUNT)

    assert compute(wired, 2) == Artifact(CHILD_AMOUNT, D("1088"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        PerUnitAmount(per_unit(), CHILDREN, CHILD_AMOUNT, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="PerUnitAmount.*'count'"):
        PerUnitAmount(per_unit(), (CHILDREN,), CHILD_AMOUNT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_its_count() -> None:
    money = ArtifactKind("ex/money_count", Decimal)
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="PerUnitAmount.*'count'"):
        PerUnitAmount(per_unit(), money, CHILD_AMOUNT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_int_kind_for_its_output() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="PerUnitAmount.*'output'"):
        PerUnitAmount(per_unit(), CHILDREN, other_count)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[Amount]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        PerUnitAmount(rate, CHILDREN, CHILD_AMOUNT)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(PerUnitAmount, "__type_params__", ())
    assert not getattr(PerUnitAmount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_count_of_one_gets_the_amount() -> None:
    output = compute(capability(), 1)

    assert output == Artifact(CHILD_AMOUNT, D("544"))
    assert type(output.value) is Decimal


def test_a_count_of_two_gets_twice_the_amount() -> None:
    # 544 × 2 = 1088.
    assert compute(capability(), 2) == Artifact(CHILD_AMOUNT, D("1088"))


def test_a_larger_count_multiplies_the_amount() -> None:
    # 544 × 7 = 3808.
    assert compute(capability(), 7) == Artifact(CHILD_AMOUNT, D("3808"))


def test_a_count_of_zero_gets_zero() -> None:
    output = compute(capability(), 0)

    assert output == Artifact(CHILD_AMOUNT, D("0"))
    assert type(output.value) is Decimal


def test_a_zero_amount_gets_zero_for_any_count() -> None:
    wired = capability(per_unit("0"))

    assert compute(wired, 0) == Artifact(CHILD_AMOUNT, D("0"))
    assert compute(wired, 3) == Artifact(CHILD_AMOUNT, D("0"))


def test_the_amount_dataset_supplies_the_amount_for_each_unit() -> None:
    # 12.5 × 3 = 37.5.
    assert compute(capability(per_unit("12.5")), 3) == Artifact(CHILD_AMOUNT, D("37.5"))


def test_keeps_the_amount_exact_and_its_scale() -> None:
    wired = capability(per_unit("544.00"))

    assert str(compute(wired, 2).value) == "1088.00"
    assert str(compute(wired, 1).value) == "544.00"


def test_keeps_fractions_of_a_cent_exactly() -> None:
    # 0.333 × 3 = 0.999, not rounded.
    assert compute(capability(per_unit("0.333")), 3) == Artifact(CHILD_AMOUNT, D("0.999"))


def test_rounds_the_product_with_the_amount_datasets_rule() -> None:
    wired = capability(per_unit("0.333", rounding=CENT))

    # 0.333 × 3 = 0.999, half-up to 1.00.
    assert compute(wired, 3) == Artifact(CHILD_AMOUNT, D("1.00"))
    assert str(compute(wired, 3).value) == "1.00"


def test_rounds_the_product_not_the_amount_for_each_unit() -> None:
    wired = capability(per_unit("0.333", rounding=CENT))

    # Rounding 0.333 first would give 0.33 × 3 = 0.99; the rule applies once, to 0.999.
    assert compute(wired, 3).value != D("0.99")
    assert compute(wired, 3).value == D("1")


def test_rounds_with_another_rule_of_the_amount_dataset() -> None:
    wired = capability(per_unit("12.5", rounding=RoundTo(D("1"), RoundingMode.FLOOR)))

    # 12.5 × 3 = 37.5, floored to 37.
    assert compute(wired, 3) == Artifact(CHILD_AMOUNT, D("37"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(per_unit(rounding=CENT))

    assert str(compute(wired, 2).value) == "1088.00"
    assert str(compute(wired, 0).value) == "0.00"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(CHILDREN, 2)))

    assert result.outputs == (Artifact(CHILD_AMOUNT, D("1088")),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="child_count"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_per_unit_amount_line() -> None:
    trace = capability().compute((Artifact(CHILDREN, 2),)).trace

    assert trace == (
        PerUnitAmountLine(
            output=CHILD_AMOUNT,
            count_kind=CHILDREN,
            count=2,
            per_unit=Amount(D("544")),
            rounding=NO_ROUNDING,
            result=D("1088"),
        ),
    )


def test_traces_a_count_of_zero() -> None:
    trace = capability().compute((Artifact(CHILDREN, 0),)).trace

    assert trace == (
        PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 0, Amount(D("544")), NO_ROUNDING, D("0")),
    )


def test_traces_the_rounding_rule_and_the_rounded_result() -> None:
    wired = capability(per_unit("0.333", rounding=CENT))

    trace = wired.compute((Artifact(CHILDREN, 3),)).trace

    assert trace == (
        PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 3, Amount(D("0.333")), CENT, D("1.00")),
    )


def test_traces_the_count_as_an_int() -> None:
    (line,) = capability().compute((Artifact(CHILDREN, 3),)).trace

    assert isinstance(line, PerUnitAmountLine)
    assert type(line.count) is int
    assert line.count == 3


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute((Artifact(CHILDREN, 2),)).trace

    assert [line.amount for line in trace] == [D("1088")]


def test_trace_result_is_the_output() -> None:
    result = capability(per_unit("544.00")).compute((Artifact(CHILDREN, 2),))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, PerUnitAmountLine)
    assert line.result == output.value
    assert str(line.result) == "1088.00"


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(CHILDREN, 2),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
