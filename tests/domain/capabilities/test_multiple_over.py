"""Unit tests for the MultipleOver capability (`core/multiple_over`), made-up values.

Its slots: one parameter slot `factor` (a `factor` dataset), two consumed single slots, `amount`
(the figure multiplied) and `less` (the figure taken off), and one produced slot `output`. The
output is `rounding.apply(max(factor × amount − less, 0))`, with the `factor` dataset's rule (which
defaults to no rounding), applied once; a difference at or below zero is a plain `Decimal(0)`. It
records one `MultipleOverLine`.

The line's figures are `base` and `base_amount` for the consumed `amount` (a field named `amount`
would hide the `amount` every trace line has) and `less` and `less_amount` for the consumed `less`.
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
from tax_calculator.domain.capabilities.multiple_over import MultipleOver
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.factor import FACTOR, Factor
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.trace import MultipleOverLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


AMOUNTS = ArtifactKind("ex/reduction_amounts", Decimal)
TAX = ArtifactKind("ex/tax_so_far", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)


def factor(value: str = "2", rounding: RoundingRule = NO_ROUNDING) -> ParameterDataset[Factor]:
    """By default a made-up factor of 2, exact."""
    return ParameterDataset(
        "ex/some_factor", 2025, FACTOR, Factor(D(value)), rounding, ("https://example.org/f",)
    )


def capability(factor_data: ParameterDataset[Factor] | None = None) -> MultipleOver:
    """By default twice the made-up reduction amounts over the made-up tax, not below zero."""
    return MultipleOver(factor_data or factor(), AMOUNTS, TAX, REDUCTION)


def inputs(amount: str, less: str) -> tuple[Artifact[Decimal], ...]:
    return (Artifact(AMOUNTS, D(amount)), Artifact(TAX, D(less)))


def compute(wired: MultipleOver, amount: str, less: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(amount, less)).outputs
    return output


def test_is_registered_as_core_multiple_over() -> None:
    assert CapabilityRegistry.shared().get("core/multiple_over") is MultipleOver


def test_is_exported_from_the_capabilities_package() -> None:
    assert "multiple_over" in core.__all__
    assert core.multiple_over.MultipleOver is MultipleOver


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({AMOUNTS, TAX})
    assert capability().produces == frozenset({REDUCTION})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(MultipleOver)
    assert "produces" not in vars(MultipleOver)


def test_declares_its_slots() -> None:
    assert MultipleOver.PARAMETERS == {"factor": FACTOR}
    assert MultipleOver.PARAMETERS["factor"] is FACTOR
    assert MultipleOver.CONSUMES == {"amount": Decimal, "less": Decimal}
    assert MultipleOver.PRODUCES == {"output": Decimal}
    assert not MultipleOver.is_list_slot("amount")
    assert not MultipleOver.is_list_slot("less")


def test_its_slots_are_read_only() -> None:
    for slots in (MultipleOver.PARAMETERS, MultipleOver.CONSUMES, MultipleOver.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(MultipleOver.PARAMETERS, Mapping[str, ParameterKind[Factor]])
    assert_type(MultipleOver.CONSUMES, Mapping[str, type])
    assert_type(MultipleOver.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (MultipleOver.PARAMETERS, MultipleOver.CONSUMES, MultipleOver.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = MultipleOver(factor=factor(), amount=AMOUNTS, less=TAX, output=REDUCTION)

    assert compute(wired, "294", "100") == Artifact(REDUCTION, D("488"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        MultipleOver(factor(), AMOUNTS, TAX, REDUCTION, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_amount_and_less() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultipleOver") as raised:
        MultipleOver(factor(), AMOUNTS, AMOUNTS, REDUCTION)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'less'" in message


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultipleOver") as raised:
        MultipleOver(factor(), AMOUNTS, TAX, AMOUNTS)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_less_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultipleOver") as raised:
        MultipleOver(factor(), AMOUNTS, TAX, TAX)

    message = str(raised.value)
    assert "'less'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultipleOver.*'amount'"):
        MultipleOver(factor(), (AMOUNTS,), TAX, REDUCTION)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="MultipleOver.*'less'"):
        MultipleOver(factor(), AMOUNTS, count, REDUCTION)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[Factor]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        MultipleOver(rate, AMOUNTS, TAX, REDUCTION)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(MultipleOver, "__type_params__", ())
    assert not getattr(MultipleOver, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_the_multiple_over_a_smaller_figure_is_the_difference() -> None:
    output = compute(capability(), "294", "100")

    # 2 × 294 = 588, less 100 = 488.
    assert output == Artifact(REDUCTION, D("488"))
    assert type(output.value) is Decimal


def test_a_figure_above_the_multiple_gives_zero() -> None:
    output = compute(capability(), "294", "8195.7644476")

    # 588 − 8195.7644476 is below zero: a plain 0.
    assert output == Artifact(REDUCTION, D("0"))
    assert str(output.value) == "0"


def test_a_figure_equal_to_the_multiple_gives_a_plain_zero() -> None:
    output = compute(capability(), "294.00", "588.00")

    # A tie at zero is a plain 0: no scale, never a signed zero.
    assert str(output.value) == "0"
    assert not output.value.is_signed()


def test_a_figure_just_below_the_multiple_gives_the_sliver() -> None:
    assert compute(capability(), "294", "587.99") == Artifact(REDUCTION, D("0.01"))


def test_a_figure_just_above_the_multiple_gives_zero() -> None:
    assert compute(capability(), "294", "588.01") == Artifact(REDUCTION, D("0"))


def test_a_zero_figure_gives_the_whole_multiple() -> None:
    assert compute(capability(), "294", "0") == Artifact(REDUCTION, D("588"))


def test_a_negative_figure_adds_to_the_multiple() -> None:
    # Like the floored subtraction, the figure taken off is used as given: 588 − (−12) = 600.
    assert compute(capability(), "294", "-12") == Artifact(REDUCTION, D("600"))


def test_a_zero_amount_gives_zero() -> None:
    assert compute(capability(), "0", "100") == Artifact(REDUCTION, D("0"))
    assert compute(capability(), "0", "0") == Artifact(REDUCTION, D("0"))


def test_a_negative_amount_gives_zero_when_nothing_is_taken_off() -> None:
    assert compute(capability(), "-10", "0") == Artifact(REDUCTION, D("0"))


def test_the_factor_dataset_supplies_the_multiplier() -> None:
    # 3 × 294 = 882, less 100 = 782.
    assert compute(capability(factor("3")), "294", "100") == Artifact(REDUCTION, D("782"))


def test_a_factor_of_one_is_the_floored_difference() -> None:
    assert compute(capability(factor("1")), "294", "100") == Artifact(REDUCTION, D("194"))


def test_a_factor_of_zero_gives_zero() -> None:
    assert compute(capability(factor("0")), "294", "100") == Artifact(REDUCTION, D("0"))


def test_a_fractional_factor_multiplies_exactly() -> None:
    # 2.5 × 294 = 735, less 100.5 = 634.5.
    assert compute(capability(factor("2.5")), "294", "100.5") == Artifact(REDUCTION, D("634.5"))


def test_keeps_the_result_exact_without_rounding() -> None:
    # 2 × 294.005 = 588.010, less 0.0001 = 588.0099, not rounded.
    assert compute(capability(), "294.005", "0.0001") == Artifact(REDUCTION, D("588.0099"))


def test_keeps_the_scale_of_the_exact_result() -> None:
    assert str(compute(capability(), "294.00", "100").value) == "488.00"


def test_rounds_with_the_factor_datasets_rule() -> None:
    wired = capability(factor(rounding=CENT))

    # 588.0099 half-up to 588.01.
    assert compute(wired, "294.005", "0.0001") == Artifact(REDUCTION, D("588.01"))
    # 488 to 488.00.
    assert str(compute(wired, "294", "100").value) == "488.00"


def test_rounds_with_another_rule_of_the_factor_dataset() -> None:
    wired = capability(factor(rounding=RoundTo(D("1"), RoundingMode.FLOOR)))

    # 588 − 100.5 = 487.5, floored to 487.
    assert compute(wired, "294", "100.5") == Artifact(REDUCTION, D("487"))


def test_rounds_once_after_the_floor() -> None:
    wired = capability(factor(rounding=CENT))

    # Below zero: floored to 0 first, then rounded to 0.00.
    output = compute(wired, "294", "8195.7644476")
    assert output == Artifact(REDUCTION, D("0"))
    assert str(output.value) == "0.00"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs("294", "100")))

    assert result.outputs == (Artifact(REDUCTION, D("488")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="reduction_amounts"):
        capability().compute((Artifact(TAX, D("100")),))


def test_a_missing_less_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="tax_so_far"):
        capability().compute((Artifact(AMOUNTS, D("294")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_multiple_over_line() -> None:
    trace = capability().compute(inputs("294", "100")).trace

    assert trace == (
        MultipleOverLine(
            output=REDUCTION,
            base=AMOUNTS,
            base_amount=D("294"),
            factor=Factor(D("2")),
            less=TAX,
            less_amount=D("100"),
            rounding=NO_ROUNDING,
            result=D("488"),
        ),
    )


def test_traces_a_floored_result_as_zero() -> None:
    trace = capability().compute(inputs("294", "8195.7644476")).trace

    assert trace == (
        MultipleOverLine(
            REDUCTION,
            AMOUNTS,
            D("294"),
            Factor(D("2")),
            TAX,
            D("8195.7644476"),
            NO_ROUNDING,
            D("0"),
        ),
    )


def test_traces_the_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(factor(rounding=CENT)).compute(inputs("294.005", "0.0001")).trace

    assert trace == (
        MultipleOverLine(
            REDUCTION,
            AMOUNTS,
            D("294.005"),
            Factor(D("2")),
            TAX,
            D("0.0001"),
            CENT,
            D("588.01"),
        ),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(factor(rounding=CENT)).compute(inputs("294.005", "0.0001")).trace

    assert [line.amount for line in trace] == [D("588.01")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute(inputs("294", "100"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, MultipleOverLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("294", "100")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
