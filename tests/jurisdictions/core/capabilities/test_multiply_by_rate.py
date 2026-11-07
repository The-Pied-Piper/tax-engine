"""Unit tests for the MultiplyByRate capability (`core/multiply_by_rate`), made-up kinds and values.

Its slots: one parameter slot `rounding` (a `rounding_only` dataset, which carries only its
rounding rule), two consumed `Decimal` slots, `base` and `rate`, and one produced slot `output`.
The rate is an artifact, not a dataset's figure, and is a fraction (0.0915 is 9.15%), not a
percentage. The output is `rounding.apply(base × rate)`: the product is exact and rounded once by
the dataset's rule, which defaults to no rounding. A rate outside 0 to 1 is refused with
`InvalidRateError`, as a rate dataset would refuse it; the base is not capped. It records one
`MultipliedByRateLine`.

In the worked example (a Line 6 "Line 4 multiplied by the percentage from line 5" shape), the
figures are 16,449 × 0.0915 = 1,505.0835, rounded half-up to 1,505.08. The kinds and the dataset
family are made up.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import (
    InvalidCapabilityError,
    InvalidRateError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import MultipliedByRateLine
from tax_engine.jurisdictions.core.capabilities.multiply_by_rate import MultiplyByRate
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

BASE = AmountKind("ex/excess_income")
RATE_KIND = AmountKind("ex/column_rate")
OUTPUT = AmountKind("ex/excess_tax")


def rounding(rule: RoundingRule = NO_ROUNDING) -> ParameterDataset[RoundingOnly]:
    """By default no rounding."""
    return ParameterDataset(
        "ex/excess_tax_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> MultiplyByRate:
    """By default the made-up base × rate, exact."""
    return MultiplyByRate(rounding_data or rounding(), BASE, RATE_KIND, OUTPUT)


def inputs(base: str, rate: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(BASE, D(base)), Artifact(RATE_KIND, D(rate)))


def compute(wired: MultiplyByRate, base: str, rate: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(base, rate)).outputs
    return output


def test_is_registered_as_core_multiply_by_rate() -> None:
    assert bundled_capabilities().get("core/multiply_by_rate") is MultiplyByRate


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({BASE, RATE_KIND})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(MultiplyByRate)
    assert "produces" not in vars(MultiplyByRate)


def test_declares_its_slots() -> None:
    assert MultiplyByRate.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert MultiplyByRate.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert MultiplyByRate.CONSUMES == {"base": Decimal, "rate": Decimal}
    assert MultiplyByRate.PRODUCES == {"output": Decimal}
    assert not MultiplyByRate.is_list_slot("base")
    assert not MultiplyByRate.is_list_slot("rate")


def test_its_slots_are_read_only() -> None:
    for slots in (MultiplyByRate.PARAMETERS, MultiplyByRate.CONSUMES, MultiplyByRate.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(MultiplyByRate.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(MultiplyByRate.CONSUMES, Mapping[str, type])
    assert_type(MultiplyByRate.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (MultiplyByRate.PARAMETERS, MultiplyByRate.CONSUMES, MultiplyByRate.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = MultiplyByRate(
        rounding=rounding(),
        base=BASE,
        rate=RATE_KIND,
        output=OUTPUT,
    )

    assert compute(wired, "1000", "0.25") == Artifact(OUTPUT, D("250"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        MultiplyByRate(rounding(), BASE, RATE_KIND, OUTPUT, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultiplyByRate") as raised:
        MultiplyByRate(rounding(), BASE, RATE_KIND, BASE)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_base_and_rate() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultiplyByRate") as raised:
        MultiplyByRate(rounding(), BASE, BASE, OUTPUT)

    message = str(raised.value)
    assert "'base'" in message
    assert "'rate'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="MultiplyByRate.*'base'"):
        MultiplyByRate(rounding(), (BASE,), RATE_KIND, OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(MultiplyByRate, "__type_params__", ())
    assert not getattr(MultiplyByRate, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_the_worked_example_rounds_16449_times_0_0915_half_up_to_the_cent() -> None:
    # 16,449 × 0.0915 = 1,505.0835, which rounds half-up to 1,505.08.
    output = compute(capability(rounding(CENT)), "16449.00", "0.0915")

    assert output == Artifact(OUTPUT, D("1505.08"))
    assert type(output.value) is Decimal


def test_the_product_is_exact_under_no_rounding() -> None:
    # 19,835.00 × 0.0505 = 1,001.6675, kept whole: no rule, no rounding.
    output = compute(capability(), "19835.00", "0.0505")

    assert output == Artifact(OUTPUT, D("1001.6675"))
    assert str(output.value) == "1001.6675"


def test_the_rate_is_a_fraction_not_a_percentage() -> None:
    # 1,000 × 0.0915 is 91.5, not 0.915: nothing divides the rate by 100.
    assert compute(capability(), "1000", "0.0915") == Artifact(OUTPUT, D("91.5"))


def test_rounds_the_product_once_half_up_to_the_cent() -> None:
    wired = capability(rounding(CENT))

    # 19,835.00 × 0.0505 = 1,001.6675 rounds to 1,001.67;
    # 43,151.00 × 0.1116 = 4,815.6516 rounds to 4,815.65.
    assert compute(wired, "19835.00", "0.0505") == Artifact(OUTPUT, D("1001.67"))
    assert compute(wired, "43151.00", "0.1116") == Artifact(OUTPUT, D("4815.65"))


def test_a_product_exactly_on_a_half_cent_is_rounded_by_the_rule_alone() -> None:
    # 1.00 × 0.005 = 0.005 sits on the tie: half-up to 0.01, half-even to 0.00.
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert compute(capability(rounding(CENT)), "1.00", "0.005") == Artifact(OUTPUT, D("0.01"))
    assert compute(capability(rounding(half_even)), "1.00", "0.005") == Artifact(OUTPUT, D("0.00"))


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(rounding(RoundTo(D("1"), RoundingMode.CEILING)))

    # 1,000 × 0.0015 = 1.5, up to 2.
    assert compute(wired, "1000", "0.0015") == Artifact(OUTPUT, D("2"))


def test_a_rate_of_zero_gives_zero() -> None:
    output = compute(capability(rounding(CENT)), "14000", "0")

    assert output == Artifact(OUTPUT, D("0.00"))
    assert type(output.value) is Decimal


def test_a_rate_of_one_gives_the_base() -> None:
    assert compute(capability(), "1234.56", "1") == Artifact(OUTPUT, D("1234.56"))


def test_a_zero_base_gives_zero() -> None:
    assert compute(capability(), "0", "0.0915") == Artifact(OUTPUT, D("0"))


def test_the_base_is_not_capped() -> None:
    # A base of 150,000 at a rate of 0.5 is 75,000: nothing caps the product.
    assert compute(capability(), "150000", "0.5") == Artifact(OUTPUT, D("75000"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), *inputs("1000", "0.25")))

    assert result.outputs == (Artifact(OUTPUT, D("250")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="excess_income"):
        capability().compute(inputs("1000", "0.25")[1:])


def test_a_missing_rate_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="column_rate"):
        capability().compute(inputs("1000", "0.25")[:1])


# --- the rate's range -------------------------------------------------------------------------


def test_a_rate_of_zero_and_a_rate_of_one_are_accepted() -> None:
    assert compute(capability(), "1000", "0") == Artifact(OUTPUT, D("0"))
    assert compute(capability(), "1000", "1") == Artifact(OUTPUT, D("1000"))


def test_a_rate_above_one_is_refused_with_invalid_rate() -> None:
    with pytest.raises(InvalidRateError, match="between 0 and 1"):
        compute(capability(rounding(CENT)), "1000", "1.0001")


def test_a_rate_below_zero_is_refused_with_invalid_rate() -> None:
    with pytest.raises(InvalidRateError, match="between 0 and 1"):
        compute(capability(rounding(CENT)), "1000", "-0.0001")


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_multiplied_by_rate_line() -> None:
    trace = capability(rounding(CENT)).compute(inputs("16449.00", "0.0915")).trace

    assert trace == (
        MultipliedByRateLine(
            output=OUTPUT,
            base_kind=BASE,
            base_value=D("16449.00"),
            rate_kind=RATE_KIND,
            rate_value=D("0.0915"),
            rounding=CENT,
            result=D("1505.08"),
        ),
    )


def test_traces_no_rounding_and_the_unrounded_product() -> None:
    trace = capability().compute(inputs("19835.00", "0.0505")).trace

    assert trace == (
        MultipliedByRateLine(
            OUTPUT,
            BASE,
            D("19835.00"),
            RATE_KIND,
            D("0.0505"),
            NO_ROUNDING,
            D("1001.6675"),
        ),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("16449.00", "0.0915")).trace

    assert [line.amount for line in trace] == [D("1505.08")]


def test_trace_result_is_the_output() -> None:
    result = capability(rounding(CENT)).compute(inputs("43151.00", "0.1116"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, MultipliedByRateLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("19835.00", "0.0505")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
