"""Unit tests for the Multiply capability (`core/multiply`), made-up kinds and values.

Its slots: one parameter slot `rounding` (a `rounding_only` dataset, which carries only its
rounding rule), two consumed `Decimal` slots, `multiplicand` and `multiplier`, and one produced slot
`output`. The output is `rounding.apply(Fraction(multiplicand) * Fraction(multiplier))`: the product
is formed once as an exact `fractions.Fraction` and rounded once by the dataset's rule. The product
of two finite decimals always has a finite expansion, so `rounding: none` never raises. Unlike
`core/multiply_by_rate`, the multiplier is any figure, not a rate limited to 0 to 1: a multiplier
above one works. It records one `ProductLine`.

In the worked example (a made-up amount times a made-up factor: 14,000 x 1.25) the product is
17,500. The artifact kinds and the dataset family are made up.
"""

from __future__ import annotations

import decimal
from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.kinds import AmountKind, RateKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import ProductLine
from tax_engine.jurisdictions.core.capabilities.multiply import Multiply
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
TEN_THOUSANDTH = RoundTo(D("0.0001"), RoundingMode.HALF_UP)

AMOUNT = AmountKind("ex/amount")
FACTOR = AmountKind("ex/factor")
PRODUCT = AmountKind("ex/product")


def rounding(rule: RoundingRule = NO_ROUNDING) -> ParameterDataset[RoundingOnly]:
    """By default no rounding."""
    return ParameterDataset(
        "ex/product_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> Multiply:
    """By default the made-up total tax / total pay, exact."""
    return Multiply(rounding_data or rounding(), AMOUNT, FACTOR, PRODUCT)


def inputs(multiplicand: str, multiplier: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(AMOUNT, D(multiplicand)), Artifact(FACTOR, D(multiplier)))


def compute(wired: Multiply, multiplicand: str, multiplier: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(multiplicand, multiplier)).outputs
    return output


def test_is_registered_as_core_multiply() -> None:
    assert bundled_capabilities().get("core/multiply") is Multiply


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({AMOUNT, FACTOR})
    assert capability().produces == frozenset({PRODUCT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(Multiply)
    assert "produces" not in vars(Multiply)


def test_declares_its_slots() -> None:
    assert Multiply.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert Multiply.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert Multiply.CONSUMES == {"multiplicand": Decimal, "multiplier": Decimal}
    assert Multiply.PRODUCES == {"output": Decimal}
    assert not Multiply.is_list_slot("multiplicand")
    assert not Multiply.is_list_slot("multiplier")


def test_its_slots_are_read_only() -> None:
    for slots in (Multiply.PARAMETERS, Multiply.CONSUMES, Multiply.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(Multiply.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(Multiply.CONSUMES, Mapping[str, type])
    assert_type(Multiply.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (Multiply.PARAMETERS, Multiply.CONSUMES, Multiply.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = Multiply(rounding=rounding(), multiplicand=AMOUNT, multiplier=FACTOR, output=PRODUCT)

    assert compute(wired, "14000", "1.25") == Artifact(PRODUCT, D("17500"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        Multiply(rounding(), AMOUNT, FACTOR, PRODUCT, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_multiplicand_and_multiplier() -> None:
    with pytest.raises(InvalidCapabilityError, match="Multiply") as raised:
        Multiply(rounding(), AMOUNT, AMOUNT, PRODUCT)

    message = str(raised.value)
    assert "'multiplicand'" in message
    assert "'multiplier'" in message


def test_rejects_one_kind_as_both_multiplicand_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="Multiply") as raised:
        Multiply(rounding(), AMOUNT, FACTOR, AMOUNT)

    message = str(raised.value)
    assert "'multiplicand'" in message
    assert "'output'" in message


def test_rejects_a_rate_kind_for_its_multiplicand() -> None:
    rate = RateKind("ex/rate_as_multiplicand")

    with pytest.raises(InvalidCapabilityError, match="Multiply.*'multiplicand'"):
        Multiply(rounding(), rate, FACTOR, PRODUCT)  # type: ignore[arg-type]


def test_rejects_a_rate_kind_for_its_multiplier() -> None:
    rate = RateKind("ex/rate_as_multiplier")

    with pytest.raises(InvalidCapabilityError, match="Multiply.*'multiplier'"):
        Multiply(rounding(), AMOUNT, rate, PRODUCT)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_multiplicand() -> None:
    with pytest.raises(InvalidCapabilityError, match="Multiply.*'multiplicand'"):
        Multiply(rounding(), (AMOUNT,), FACTOR, PRODUCT)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[RoundingOnly]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        Multiply(rate, AMOUNT, FACTOR, PRODUCT)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(Multiply, "__type_params__", ())
    assert not getattr(Multiply, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_an_exact_product_is_kept_exact() -> None:
    # 14,000 x 1.25 = 17,500 exactly.
    output = compute(capability(), "14000", "1.25")

    assert output == Artifact(PRODUCT, D("17500"))
    assert type(output.value) is Decimal


def test_a_product_with_decimals_is_kept_exact_without_a_rounding_rule() -> None:
    # The product of two finite decimals always terminates: nothing to refuse.
    assert compute(capability(), "0.49463", "15780.00").value == D("7805.2614")


def test_a_multiplier_above_one_is_not_capped() -> None:
    # `core/multiply_by_rate` refuses a rate above 1; this capability does not.
    assert compute(capability(), "15780.00", "1.24463") == Artifact(PRODUCT, D("19640.2614"))
    assert compute(capability(), "100", "250") == Artifact(PRODUCT, D("25000"))


def test_a_multiplier_between_zero_and_one_works_too() -> None:
    assert compute(capability(), "15780.00", "0.25") == Artifact(PRODUCT, D("3945.0000"))


def test_rounds_a_product_once_half_up() -> None:
    wired = capability(rounding(CENT))

    # 0.333 x 0.5 = 0.1665 half-up to 0.17; 0.329 x 0.5 = 0.1645 half-up to 0.16.
    assert compute(wired, "0.333", "0.5") == Artifact(PRODUCT, D("0.17"))
    assert compute(wired, "0.329", "0.5") == Artifact(PRODUCT, D("0.16"))


def test_the_worked_product_rounds_to_the_cent() -> None:
    # 0.49463 x 15,780.00 = 7,805.2614, half-up to 7,805.26.
    output = compute(capability(rounding(CENT)), "0.49463", "15780.00")

    assert output == Artifact(PRODUCT, D("7805.26"))
    assert str(output.value) == "7805.26"


def test_a_product_exactly_on_a_half_is_rounded_by_the_rule_alone() -> None:
    # 1.005 x 1 sits on the tie: half-up to 1.01, half-even to 1.00.
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert compute(capability(rounding(CENT)), "1.005", "1") == Artifact(PRODUCT, D("1.01"))
    assert compute(capability(rounding(half_even)), "1.005", "1") == Artifact(PRODUCT, D("1.00"))


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(rounding(RoundTo(D("1"), RoundingMode.CEILING)))

    assert compute(wired, "1.1", "1.1") == Artifact(PRODUCT, D("2"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    assert str(compute(capability(rounding(CENT)), "14000", "1.25").value) == "17500.00"
    assert str(compute(capability(rounding(TEN_THOUSANDTH)), "1", "0.25").value) == "0.2500"


def test_the_product_is_exact_under_a_context_that_traps_inexact() -> None:
    # The engine runs capabilities under a context trapping Inexact; only the rule may round.
    with decimal.localcontext() as context:
        context.traps[decimal.Inexact] = True
        output = compute(capability(rounding(CENT)), "0.49463", "15780.00")

    assert output.value == D("7805.26")


def test_the_product_keeps_every_digit_of_a_long_multiplicand() -> None:
    multiplicand = "12345678901234567890123456789"

    assert str(compute(capability(), multiplicand, "1").value) == multiplicand


def test_the_product_is_not_cut_at_28_digits() -> None:
    # 28 nines x 28 nines needs 56 digits; a default-context multiply would round it.
    nines = "9" * 28

    assert compute(capability(), nines, nines).value == D(int(nines) ** 2)


def test_a_zero_multiplicand_gives_zero() -> None:
    output = compute(capability(), "0", "1.25")

    assert output == Artifact(PRODUCT, D("0"))
    assert type(output.value) is Decimal


def test_a_zero_multiplier_gives_zero() -> None:
    assert compute(capability(), "14000", "0").value == D("0")
    assert compute(capability(rounding(CENT)), "14000", "0.00").value == D("0")


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), *inputs("14000", "1.25")))

    assert result.outputs == (Artifact(PRODUCT, D("17500")),)


def test_a_missing_multiplicand_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="amount"):
        capability().compute(inputs("14000", "1.25")[1:])


def test_a_missing_multiplier_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="factor"):
        capability().compute(inputs("14000", "1.25")[:1])


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_product_line() -> None:
    trace = capability().compute(inputs("14000", "1.25")).trace

    assert trace == (
        ProductLine(
            output=PRODUCT,
            multiplicand=AMOUNT,
            multiplicand_amount=D("14000"),
            multiplier=FACTOR,
            multiplier_amount=D("1.25"),
            rounding=NO_ROUNDING,
            result=D("17500"),
        ),
    )


def test_traces_the_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("0.49463", "15780.00")).trace

    assert trace == (
        ProductLine(PRODUCT, AMOUNT, D("0.49463"), FACTOR, D("15780.00"), CENT, D("7805.26")),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("0.49463", "15780.00")).trace

    assert [line.amount for line in trace] == [D("7805.26")]


def test_trace_result_is_the_output() -> None:
    result = capability(rounding(CENT)).compute(inputs("4321.5", "91.37"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, ProductLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("14000", "1.25")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
