"""Unit tests for the ApplyRatio capability (`core/apply_ratio`), made-up kinds and values.

Its slots: one parameter slot `rounding` (a `rounding_only` dataset, which carries only its
rounding rule), three consumed `Decimal` slots, `amount`, `numerator` and `denominator`, and one
produced slot `output`. The output is `rounding.apply(amount × numerator / denominator)`: the
product is formed first and divided once, as an exact `fractions.Fraction`, and rounded once by
the dataset's rule. Under `rounding: none` a quotient with no finite decimal expansion raises
`decimal.Inexact` instead of being carried to 28 digits. A zero denominator is refused with a
`ValidationError` naming the three kinds. A ratio above 1 is not capped. It records one
`RatioAppliedLine`.

In the worked example (a foreign tax credit: tax otherwise payable × foreign income / worldwide
income), 14,000 × 10,000 / 100,000 is 1,400. The artifact kinds and the dataset family are made
up.
"""

from __future__ import annotations

import decimal
from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.domain.capabilities as core
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_ratio import ApplyRatio
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    ValidationError,
)
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
from tax_engine.domain.trace import RatioAppliedLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

TAX_PAYABLE = ArtifactKind("ex/tax_payable", Decimal)
FOREIGN_INCOME = ArtifactKind("ex/foreign_income", Decimal)
WORLD_INCOME = ArtifactKind("ex/worldwide_income", Decimal)
CREDIT_SHARE = ArtifactKind("ex/credit_share", Decimal)


def rounding(rule: RoundingRule = NO_ROUNDING) -> ParameterDataset[RoundingOnly]:
    """By default no rounding."""
    return ParameterDataset(
        "ex/credit_share_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> ApplyRatio:
    """By default the made-up tax × foreign income / worldwide income, exact."""
    return ApplyRatio(
        rounding_data or rounding(), TAX_PAYABLE, FOREIGN_INCOME, WORLD_INCOME, CREDIT_SHARE
    )


def inputs(amount: str, numerator: str, denominator: str) -> tuple[Artifact[Any], ...]:
    return (
        Artifact(TAX_PAYABLE, D(amount)),
        Artifact(FOREIGN_INCOME, D(numerator)),
        Artifact(WORLD_INCOME, D(denominator)),
    )


def compute(wired: ApplyRatio, amount: str, numerator: str, denominator: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(amount, numerator, denominator)).outputs
    return output


def test_is_registered_as_core_apply_ratio() -> None:
    assert CapabilityRegistry.shared().get("core/apply_ratio") is ApplyRatio


def test_is_exported_from_the_capabilities_package() -> None:
    assert "apply_ratio" in core.__all__
    assert core.apply_ratio.ApplyRatio is ApplyRatio


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({TAX_PAYABLE, FOREIGN_INCOME, WORLD_INCOME})
    assert capability().produces == frozenset({CREDIT_SHARE})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ApplyRatio)
    assert "produces" not in vars(ApplyRatio)


def test_declares_its_slots() -> None:
    assert ApplyRatio.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert ApplyRatio.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert ApplyRatio.CONSUMES == {"amount": Decimal, "numerator": Decimal, "denominator": Decimal}
    assert ApplyRatio.PRODUCES == {"output": Decimal}
    assert not ApplyRatio.is_list_slot("amount")
    assert not ApplyRatio.is_list_slot("numerator")
    assert not ApplyRatio.is_list_slot("denominator")


def test_its_slots_are_read_only() -> None:
    for slots in (ApplyRatio.PARAMETERS, ApplyRatio.CONSUMES, ApplyRatio.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ApplyRatio.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(ApplyRatio.CONSUMES, Mapping[str, type])
    assert_type(ApplyRatio.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ApplyRatio.PARAMETERS, ApplyRatio.CONSUMES, ApplyRatio.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ApplyRatio(
        rounding=rounding(),
        amount=TAX_PAYABLE,
        numerator=FOREIGN_INCOME,
        denominator=WORLD_INCOME,
        output=CREDIT_SHARE,
    )

    assert compute(wired, "14000", "10000", "100000") == Artifact(CREDIT_SHARE, D("1400"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ApplyRatio(
            rounding(),
            TAX_PAYABLE,
            FOREIGN_INCOME,
            WORLD_INCOME,
            CREDIT_SHARE,
            NO_ROUNDING,  # type: ignore[call-arg]
        )


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyRatio") as raised:
        ApplyRatio(rounding(), TAX_PAYABLE, FOREIGN_INCOME, WORLD_INCOME, TAX_PAYABLE)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_numerator_and_denominator() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyRatio") as raised:
        ApplyRatio(rounding(), TAX_PAYABLE, FOREIGN_INCOME, FOREIGN_INCOME, CREDIT_SHARE)

    message = str(raised.value)
    assert "'numerator'" in message
    assert "'denominator'" in message


def test_rejects_a_rate_kind_for_its_numerator() -> None:
    rate = ArtifactKind("ex/rate_as_numerator", Rate)

    with pytest.raises(InvalidCapabilityError, match="ApplyRatio.*'numerator'"):
        ApplyRatio(
            rounding(),
            TAX_PAYABLE,
            rate,  # type: ignore[arg-type]
            WORLD_INCOME,
            CREDIT_SHARE,
        )


def test_rejects_a_rate_kind_for_its_denominator() -> None:
    rate = ArtifactKind("ex/rate_as_denominator", Rate)

    with pytest.raises(InvalidCapabilityError, match="ApplyRatio.*'denominator'"):
        ApplyRatio(
            rounding(),
            TAX_PAYABLE,
            FOREIGN_INCOME,
            rate,  # type: ignore[arg-type]
            CREDIT_SHARE,
        )


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyRatio.*'amount'"):
        ApplyRatio(
            rounding(),
            (TAX_PAYABLE,),  # type: ignore[arg-type]
            FOREIGN_INCOME,
            WORLD_INCOME,
            CREDIT_SHARE,
        )


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[RoundingOnly]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        ApplyRatio(
            rate,  # type: ignore[arg-type]
            TAX_PAYABLE,
            FOREIGN_INCOME,
            WORLD_INCOME,
            CREDIT_SHARE,
        )

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ApplyRatio, "__type_params__", ())
    assert not getattr(ApplyRatio, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_the_worked_example_gives_exactly_1400() -> None:
    # 14,000 × 10,000 / 100,000 = 1,400.
    output = compute(capability(), "14000", "10000", "100000")

    assert output == Artifact(CREDIT_SHARE, D("1400"))
    assert str(output.value) == "1400"
    assert type(output.value) is Decimal


def test_an_inexact_quotient_without_a_rounding_rule_raises_inexact() -> None:
    # 1000 × 1 / 3 = 333.333... has no finite expansion; under `rounding: none` it is refused, not
    # carried to 28 digits.
    with pytest.raises(decimal.Inexact):
        compute(capability(), "1000", "1", "3")


def test_an_inexact_quotient_is_inexact_whatever_the_scale() -> None:
    with pytest.raises(decimal.Inexact):
        compute(capability(), "1000.00", "1.00", "3.00")
    with pytest.raises(decimal.Inexact):
        compute(capability(), "1", "1", "7")


def test_rounds_an_exact_quotient_once_half_up_to_the_cent() -> None:
    wired = capability(rounding(CENT))

    # 1000 × 1 / 3 = 333.333... half-up to 333.33; 1000 × 2 / 3 = 666.666... to 666.67.
    assert compute(wired, "1000", "1", "3") == Artifact(CREDIT_SHARE, D("333.33"))
    assert compute(wired, "1000", "2", "3") == Artifact(CREDIT_SHARE, D("666.67"))


def test_a_quotient_exactly_on_a_half_cent_is_rounded_by_the_rule_alone() -> None:
    # 1.005 × 1 / 1 sits on the tie: half-up to 1.01, half-even to 1.00.
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert compute(capability(rounding(CENT)), "1.005", "1", "1") == Artifact(
        CREDIT_SHARE, D("1.01")
    )
    assert compute(capability(rounding(half_even)), "1.005", "1", "1") == Artifact(
        CREDIT_SHARE, D("1.00")
    )


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(rounding(RoundTo(D("1"), RoundingMode.CEILING)))

    # 333.333... up to 334.
    assert compute(wired, "1000", "1", "3") == Artifact(CREDIT_SHARE, D("334"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    assert str(compute(capability(rounding(CENT)), "14000", "10000", "100000").value) == "1400.00"


def test_multiplies_before_it_divides_so_an_even_quotient_stays_exact() -> None:
    # 3 × 1 / 3 = 1 exactly; dividing first (3 × (1 / 3)) would give 0.9999999999999999999999999999.
    output = compute(capability(), "3", "1", "3")

    assert output == Artifact(CREDIT_SHARE, D("1"))
    assert str(output.value) == "1"


def test_a_quotient_that_is_exact_after_multiplying_needs_no_rounding_rule() -> None:
    # 1 × 3 / 3 and 7 × 3 / 21 are whole; (1 / 3) × 3 would not be, in decimal arithmetic.
    assert compute(capability(), "1", "3", "3") == Artifact(CREDIT_SHARE, D("1"))
    assert compute(capability(), "7", "3", "21") == Artifact(CREDIT_SHARE, D("1"))


def test_keeps_a_finite_quotient_exact_without_rounding() -> None:
    # 14000.50 × 10000 / 100000 = 1400.05, exact, not rounded.
    assert compute(capability(), "14000.50", "10000", "100000") == Artifact(
        CREDIT_SHARE, D("1400.05")
    )


def test_the_quotient_is_exact_so_a_long_amount_keeps_every_digit() -> None:
    # 29 digits × 5 / 5: the product has 30 digits, more than a 28-digit context holds.
    amount = "12345678901234567890123456789"

    assert str(compute(capability(), amount, "5", "5").value) == amount


def test_the_quotient_is_exact_under_a_context_that_traps_inexact() -> None:
    # The engine runs capabilities under a context trapping Inexact; only the rule may round.
    amount = "12345678901234567890123456789"
    with decimal.localcontext() as context:
        context.traps[decimal.Inexact] = True
        output = compute(capability(), amount, "5", "5")

    assert str(output.value) == amount


def test_a_ratio_above_one_is_not_capped() -> None:
    # Foreign income above worldwide income: 14000 × 150000 / 100000 = 21000, more than the amount.
    assert compute(capability(), "14000", "150000", "100000") == Artifact(CREDIT_SHARE, D("21000"))


def test_a_ratio_of_one_gives_the_amount() -> None:
    assert compute(capability(), "1234.56", "7", "7") == Artifact(CREDIT_SHARE, D("1234.56"))


def test_a_zero_numerator_gives_zero() -> None:
    output = compute(capability(), "14000", "0", "100000")

    assert output == Artifact(CREDIT_SHARE, D("0"))
    assert type(output.value) is Decimal


def test_a_zero_amount_gives_zero() -> None:
    assert compute(capability(), "0", "10000", "100000") == Artifact(CREDIT_SHARE, D("0"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs("14000", "10000", "100000")))

    assert result.outputs == (Artifact(CREDIT_SHARE, D("1400")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="tax_payable"):
        capability().compute(inputs("14000", "10000", "100000")[1:])


def test_a_missing_numerator_is_a_missing_artifact() -> None:
    given = inputs("14000", "10000", "100000")

    with pytest.raises(MissingArtifactError, match="foreign_income"):
        capability().compute((given[0], given[2]))


def test_a_missing_denominator_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="worldwide_income"):
        capability().compute(inputs("14000", "10000", "100000")[:2])


# --- a zero denominator -----------------------------------------------------------------------


def test_a_zero_denominator_is_a_validation_error_naming_the_three_kinds() -> None:
    with pytest.raises(ValidationError) as raised:
        compute(capability(), "14000", "10000", "0")

    message = str(raised.value)
    assert type(raised.value) is ValidationError
    assert "ex/tax_payable" in message
    assert "ex/foreign_income" in message
    assert "ex/worldwide_income" in message


def test_a_zero_denominator_is_refused_whatever_its_scale() -> None:
    with pytest.raises(ValidationError):
        compute(capability(), "14000", "10000", "0.00")
    with pytest.raises(ValidationError):
        compute(capability(), "14000", "10000", "-0")


def test_a_zero_denominator_is_refused_even_with_a_zero_numerator() -> None:
    with pytest.raises(ValidationError):
        compute(capability(), "14000", "0", "0")


def test_a_zero_denominator_is_refused_even_with_a_zero_amount() -> None:
    with pytest.raises(ValidationError):
        compute(capability(rounding(CENT)), "0", "10000", "0")


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_ratio_applied_line() -> None:
    trace = capability().compute(inputs("14000", "10000", "100000")).trace

    assert trace == (
        RatioAppliedLine(
            output=CREDIT_SHARE,
            amount_kind=TAX_PAYABLE,
            amount_value=D("14000"),
            numerator_kind=FOREIGN_INCOME,
            numerator_value=D("10000"),
            denominator_kind=WORLD_INCOME,
            denominator_value=D("100000"),
            rounding=NO_ROUNDING,
            result=D("1400"),
        ),
    )


def test_traces_the_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("1000", "1", "3")).trace

    assert trace == (
        RatioAppliedLine(
            CREDIT_SHARE,
            TAX_PAYABLE,
            D("1000"),
            FOREIGN_INCOME,
            D("1"),
            WORLD_INCOME,
            D("3"),
            CENT,
            D("333.33"),
        ),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("1000", "1", "3")).trace

    assert [line.amount for line in trace] == [D("333.33")]


def test_trace_result_is_the_output() -> None:
    result = capability(rounding(CENT)).compute(inputs("4321", "37", "91"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, RatioAppliedLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("14000", "10000", "100000")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- the shared ratio method ----------------------------------------------------------------
# `ApplyRatio.ratio_of(amount, numerator, denominator, rounding)` is the one place the arithmetic
# lives; capabilities that work a ratio per item call it
# instead of copying it. It is a static method: no instance, no artifacts, just the figures.


def test_ratio_of_multiplies_first_divides_once_and_rounds_once() -> None:
    assert ApplyRatio.ratio_of(D("14000"), D("10000"), D("100000"), CENT) == D("1400.00")
    assert ApplyRatio.ratio_of(D("1000"), D("1"), D("3"), CENT) == D("333.33")
    # 0.015 x 1 / 3 is exactly 0.005; dividing first would round down.
    assert ApplyRatio.ratio_of(D("0.015"), D("1"), D("3"), CENT) == D("0.01")


def test_ratio_of_uses_the_rule_it_is_given() -> None:
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert ApplyRatio.ratio_of(D("1.005"), D("1"), D("1"), half_even) == D("1.00")


def test_ratio_of_under_no_rounding_raises_inexact_on_an_infinite_expansion() -> None:
    with pytest.raises(decimal.Inexact):
        ApplyRatio.ratio_of(D("1000"), D("1"), D("3"), NO_ROUNDING)


def test_ratio_of_refuses_a_zero_denominator() -> None:
    with pytest.raises(ValidationError):
        ApplyRatio.ratio_of(D("1"), D("1"), D("0"), CENT)


def test_ratio_of_is_a_static_method() -> None:
    assert isinstance(ApplyRatio.__dict__["ratio_of"], staticmethod)


def test_compute_gives_what_ratio_of_gives(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[Decimal, Decimal, Decimal, RoundingRule]] = []

    def spy(
        amount: Decimal, numerator: Decimal, denominator: Decimal, rule: RoundingRule
    ) -> Decimal:
        calls.append((amount, numerator, denominator, rule))
        return D("42")

    monkeypatch.setattr(ApplyRatio, "ratio_of", staticmethod(spy))

    output = compute(capability(rounding(CENT)), "14000", "10000", "100000")

    assert calls == [(D("14000"), D("10000"), D("100000"), CENT)]
    assert output.value == D("42")
