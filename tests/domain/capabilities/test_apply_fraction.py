"""Unit tests for the ApplyFraction capability (`core/apply_fraction`), made-up kinds and values.

Its slots: one parameter slot `fraction` (a `fraction` dataset), one consumed slot `base` and one
produced slot `output`. The output is `rounding.apply(base × numerator / denominator)` with the
division done as an exact `fractions.Fraction` and rounded once by the `fraction` dataset's rule:
under `rounding: none` a quotient with no finite decimal expansion raises `decimal.Inexact`
instead of being carried to 28 digits. It records one `FractionAppliedLine`.
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
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.trace import BlankPassedOnLine, FractionAppliedLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


EARNED = ArtifactKind("ex/earned_income", Decimal)
PORTION = ArtifactKind("ex/earned_portion", Decimal)


def fraction(
    numerator: int = 2, denominator: int = 3, rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[Fraction]:
    """By default two-thirds, exact."""
    return ParameterDataset(
        "ex/portion_fraction",
        2025,
        FRACTION,
        Fraction(numerator, denominator),
        rounding,
        ("https://example.org/f",),
    )


def capability(fraction_data: ParameterDataset[Fraction] | None = None) -> ApplyFraction:
    """By default two-thirds of the made-up earned income, exact."""
    return ApplyFraction(fraction_data or fraction(), EARNED, PORTION)


def compute(wired: ApplyFraction, base: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(EARNED, D(base)),)).outputs
    return output


def test_is_registered_as_core_apply_fraction() -> None:
    assert CapabilityRegistry.shared().get("core/apply_fraction") is ApplyFraction


def test_is_exported_from_the_capabilities_package() -> None:
    assert "apply_fraction" in core.__all__
    assert core.apply_fraction.ApplyFraction is ApplyFraction


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({EARNED})
    assert capability().produces == frozenset({PORTION})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ApplyFraction)
    assert "produces" not in vars(ApplyFraction)


def test_declares_its_slots() -> None:
    assert ApplyFraction.PARAMETERS == {"fraction": FRACTION}
    assert ApplyFraction.PARAMETERS["fraction"] is FRACTION
    assert ApplyFraction.CONSUMES == {"base": Decimal}
    assert ApplyFraction.PRODUCES == {"output": Decimal}
    assert not ApplyFraction.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    for slots in (ApplyFraction.PARAMETERS, ApplyFraction.CONSUMES, ApplyFraction.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ApplyFraction.PARAMETERS, Mapping[str, ParameterKind[Fraction]])
    assert_type(ApplyFraction.CONSUMES, Mapping[str, type])
    assert_type(ApplyFraction.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ApplyFraction.PARAMETERS, ApplyFraction.CONSUMES, ApplyFraction.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ApplyFraction(fraction=fraction(), base=EARNED, output=PORTION)

    assert compute(wired, "60000") == Artifact(PORTION, D("40000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ApplyFraction(fraction(), EARNED, PORTION, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyFraction") as raised:
        ApplyFraction(fraction(), EARNED, EARNED)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyFraction.*'base'"):
        ApplyFraction(fraction(), (EARNED,), PORTION)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="ApplyFraction.*'base'"):
        ApplyFraction(fraction(), count, PORTION)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[Fraction]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        ApplyFraction(rate, EARNED, PORTION)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ApplyFraction, "__type_params__", ())
    assert not getattr(ApplyFraction, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_base_times_the_fraction() -> None:
    # 60000 × 2 / 3 = 40000, exactly.
    output = compute(capability(), "60000")

    assert output == Artifact(PORTION, D("40000"))
    assert str(output.value) == "40000"
    assert type(output.value) is Decimal


def test_an_inexact_quotient_without_a_rounding_rule_raises_inexact() -> None:
    # 50000 × 2 / 3 = 33333.333... has no finite expansion. Under `rounding: none` it used to be
    # carried to 28 digits (33333.33333333333333333333333), rounding no dataset asked for.
    with pytest.raises(decimal.Inexact):
        compute(capability(), "50000")


def test_an_inexact_quotient_is_inexact_whatever_the_base_scale() -> None:
    with pytest.raises(decimal.Inexact):
        compute(capability(), "50000.00")
    with pytest.raises(decimal.Inexact):
        compute(capability(fraction(1, 7)), "1")


def test_divides_as_an_exact_fraction_so_a_long_base_keeps_every_digit() -> None:
    # 3/3 of a 30-digit base: base × 3 would not fit the 28-digit context, the exact fraction does.
    base = "1234567890123456789012345678.90"

    assert compute(capability(fraction(3, 3, CENT)), base) == Artifact(PORTION, D(base))
    assert str(compute(capability(fraction(3, 3, CENT)), base).value) == base


def test_rounds_an_exact_quotient_once_half_up_to_the_cent() -> None:
    # 42275 × 2 / 3 = 28183.333... rounds once, half-up, to 28183.33.
    assert compute(capability(fraction(rounding=CENT)), "42275") == Artifact(PORTION, D("28183.33"))
    # 5.5 × 2 / 3 = 3.666... half-up to 3.67.
    assert compute(capability(fraction(rounding=CENT)), "5.5") == Artifact(PORTION, D("3.67"))


def test_a_quotient_exactly_on_a_half_cent_is_rounded_by_the_rule_alone() -> None:
    # 1.005 × 1 / 1 sits on the tie: half-up to 1.01, half-even to 1.00.
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert compute(capability(fraction(1, 1, CENT)), "1.005") == Artifact(PORTION, D("1.01"))
    assert compute(capability(fraction(1, 1, half_even)), "1.005") == Artifact(PORTION, D("1.00"))


def test_multiplies_before_it_divides_so_an_even_quotient_stays_exact() -> None:
    # 3 × 1 / 3 = 1 exactly; dividing first (3 × (1 / 3)) would give 0.9999999999999999999999999999.
    output = compute(capability(fraction(1, 3)), "3")

    assert output == Artifact(PORTION, D("1"))
    assert str(output.value) == "1"


def test_keeps_the_product_exact_without_rounding() -> None:
    # 1000.05 × 2 / 3 = 666.7, exact, not rounded.
    assert compute(capability(), "1000.05") == Artifact(PORTION, D("666.7"))


def test_rounds_with_the_fraction_datasets_rule() -> None:
    wired = capability(fraction(rounding=CENT))

    # 33333.33333333333333333333333 half-up to 33333.33.
    assert compute(wired, "50000") == Artifact(PORTION, D("33333.33"))


def test_rounds_with_another_rule_of_the_fraction_dataset() -> None:
    wired = capability(fraction(rounding=RoundTo(D("1"), RoundingMode.CEILING)))

    # 33333.333... up to 33334.
    assert compute(wired, "50000") == Artifact(PORTION, D("33334"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(fraction(rounding=CENT))

    assert str(compute(wired, "60000").value) == "40000.00"


def test_a_fraction_of_one_produces_the_base() -> None:
    assert compute(capability(fraction(3, 3)), "1234.56") == Artifact(PORTION, D("1234.56"))


def test_a_fraction_above_one_multiplies_up() -> None:
    assert compute(capability(fraction(3, 2)), "1000") == Artifact(PORTION, D("1500"))


def test_three_sixths_and_one_half_give_equal_results() -> None:
    # 3/6 is one half; 1000 × 3 / 6 is the same quotient as 1000 × 1 / 2.
    assert compute(capability(fraction(3, 6)), "1000") == compute(
        capability(fraction(1, 2)), "1000"
    )


def test_a_zero_base_produces_zero() -> None:
    output = compute(capability(), "0")

    assert output == Artifact(PORTION, D("0"))
    assert type(output.value) is Decimal


def test_the_fraction_dataset_supplies_the_fraction() -> None:
    assert compute(capability(fraction(1, 4)), "1000") == Artifact(PORTION, D("250"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(EARNED, D("60000"))))

    assert result.outputs == (Artifact(PORTION, D("40000")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="earned_income"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_fraction_applied_line() -> None:
    trace = capability().compute((Artifact(EARNED, D("60000")),)).trace

    assert trace == (
        FractionAppliedLine(
            output=PORTION,
            base=EARNED,
            base_amount=D("60000"),
            fraction=Fraction(2, 3),
            rounding=NO_ROUNDING,
            result=D("40000"),
        ),
    )


def test_traces_the_fraction_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(fraction(rounding=CENT)).compute((Artifact(EARNED, D("50000")),)).trace

    assert trace == (
        FractionAppliedLine(PORTION, EARNED, D("50000"), Fraction(2, 3), CENT, D("33333.33")),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(fraction(rounding=CENT)).compute((Artifact(EARNED, D("50000")),)).trace

    assert [line.amount for line in trace] == [D("33333.33")]


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(EARNED, D("60000")),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- a blank base ---------------------------------------------------------------------------


def test_allows_a_blank_only_in_its_base() -> None:
    assert ApplyFraction.BLANK_ALLOWED == frozenset({"base"})


def test_a_blank_base_with_no_rule_is_refused_naming_the_line() -> None:
    with pytest.raises(BlankNotAllowedError, match="'earned_income'.*'base'"):
        capability().run((Artifact(EARNED, BLANK),))


def test_a_blank_base_passed_on_gives_a_blank_output_and_no_rounding() -> None:
    # A rounding rule that would raise on any figure shows that nothing is rounded.
    wired = capability(fraction(rounding=CENT)).with_blank_rules({"base": PASS_ON})

    result = wired.run((Artifact(EARNED, BLANK),))

    assert result.outputs == (Artifact(PORTION, BLANK),)
    assert result.trace == (BlankPassedOnLine(PORTION, (EARNED,)),)


def test_a_filled_base_is_the_same_with_or_without_the_blank_rule() -> None:
    plain = capability().run((Artifact(EARNED, D("60000")),))
    ruled = capability().with_blank_rules({"base": PASS_ON}).run((Artifact(EARNED, D("60000")),))

    assert plain == ruled
    assert plain.outputs == (Artifact(PORTION, D("40000")),)
    assert len(plain.trace) == 1
    assert isinstance(plain.trace[0], FractionAppliedLine)


def test_a_zero_base_is_not_blank() -> None:
    wired = capability().with_blank_rules({"base": PASS_ON})

    assert wired.run((Artifact(EARNED, D(0)),)).outputs == (Artifact(PORTION, D(0)),)
