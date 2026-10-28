"""Unit tests for the TaperedAmount capability (`core/tapered_amount`), made-up values.

Its slots: one parameter slot `taper` (a `taper` dataset), one consumed slot `base` (the figure the
taper is measured against) and one produced slot `output`. The reduction is
`supplement × max(base − threshold, 0) / range`, computed as an exact `fractions.Fraction` and
never carried as a 28-digit Decimal: under `rounding: none` a reduction with no finite decimal
expansion raises `decimal.Inexact`; the output is
`rounding.apply(taper.base + max(supplement − reduction, 0))`, with the `taper` dataset's rule
(which defaults to no rounding), applied once. At or below the threshold the output is base +
supplement; at or above threshold + range it is the base. It records one `TaperedAmountLine`,
whose `reduction` is the exact `fractions.Fraction` before the floor at zero.

The class is `TaperedAmount`, not `Taper`, so it does not share a name with the `Taper` value
object it reads.
"""

from __future__ import annotations

import decimal
from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from fractions import Fraction as ExactFraction
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.domain.capabilities as core
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.tapered_amount import TaperedAmount
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.parameters.taper import TAPER, Taper
from tax_calculator.domain.trace import TaperedAmountLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


INCOME = ArtifactKind("ex/income", Decimal)
PERSONAL_AMOUNT = ArtifactKind("ex/personal_amount", Decimal)


def values(
    base: str = "1000", supplement: str = "500", threshold: str = "20000", range: str = "10000"
) -> Taper:
    """By default 1000 plus 500, the 500 reduced to nothing between incomes of 20000 and 30000."""
    return Taper(D(base), D(supplement), D(threshold), D(range))


def taper(
    taper_values: Taper | None = None, rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[Taper]:
    return ParameterDataset(
        "ex/some_taper",
        2025,
        TAPER,
        taper_values or values(),
        rounding,
        ("https://example.org/t",),
    )


def capability(taper_data: ParameterDataset[Taper] | None = None) -> TaperedAmount:
    """By default the made-up income under the default taper, exact."""
    return TaperedAmount(taper_data or taper(), INCOME, PERSONAL_AMOUNT)


def compute(wired: TaperedAmount, income: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(INCOME, D(income)),)).outputs
    return output


def test_is_registered_as_core_tapered_amount() -> None:
    assert CapabilityRegistry.shared().get("core/tapered_amount") is TaperedAmount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "tapered_amount" in core.__all__
    assert core.tapered_amount.TaperedAmount is TaperedAmount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({INCOME})
    assert capability().produces == frozenset({PERSONAL_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TaperedAmount)
    assert "produces" not in vars(TaperedAmount)


def test_declares_its_slots() -> None:
    assert TaperedAmount.PARAMETERS == {"taper": TAPER}
    assert TaperedAmount.PARAMETERS["taper"] is TAPER
    assert TaperedAmount.CONSUMES == {"base": Decimal}
    assert TaperedAmount.PRODUCES == {"output": Decimal}
    assert not TaperedAmount.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    for slots in (TaperedAmount.PARAMETERS, TaperedAmount.CONSUMES, TaperedAmount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(TaperedAmount.PARAMETERS, Mapping[str, ParameterKind[Taper]])
    assert_type(TaperedAmount.CONSUMES, Mapping[str, type])
    assert_type(TaperedAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (TaperedAmount.PARAMETERS, TaperedAmount.CONSUMES, TaperedAmount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TaperedAmount(taper=taper(), base=INCOME, output=PERSONAL_AMOUNT)

    assert compute(wired, "22000") == Artifact(PERSONAL_AMOUNT, D("1400"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        TaperedAmount(taper(), INCOME, PERSONAL_AMOUNT, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaperedAmount") as raised:
        TaperedAmount(taper(), INCOME, INCOME)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaperedAmount.*'base'"):
        TaperedAmount(taper(), (INCOME,), PERSONAL_AMOUNT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="TaperedAmount.*'base'"):
        TaperedAmount(taper(), count, PERSONAL_AMOUNT)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[Taper]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        TaperedAmount(rate, INCOME, PERSONAL_AMOUNT)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(TaperedAmount, "__type_params__", ())
    assert not getattr(TaperedAmount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_base_below_the_threshold_gets_the_full_amount() -> None:
    output = compute(capability(), "15000")

    # 1000 + 500, nothing reduced.
    assert output == Artifact(PERSONAL_AMOUNT, D("1500"))
    assert type(output.value) is Decimal


def test_a_base_at_the_threshold_gets_the_full_amount() -> None:
    assert compute(capability(), "20000") == Artifact(PERSONAL_AMOUNT, D("1500"))


def test_a_zero_base_gets_the_full_amount() -> None:
    assert compute(capability(), "0") == Artifact(PERSONAL_AMOUNT, D("1500"))


def test_a_negative_base_gets_the_full_amount() -> None:
    # max(base − threshold, 0): a negative base reduces nothing and never adds to the amount.
    assert compute(capability(), "-500") == Artifact(PERSONAL_AMOUNT, D("1500"))


def test_a_base_just_above_the_threshold_reduces_the_supplement_by_its_share() -> None:
    # 500 × 0.01 / 10000 = 0.0005, so 1000 + (500 − 0.0005) = 1499.9995, exact.
    assert compute(capability(), "20000.01") == Artifact(PERSONAL_AMOUNT, D("1499.9995"))


def test_a_base_inside_the_range_reduces_the_supplement_in_proportion() -> None:
    # 500 × 2000 / 10000 = 100, so 1000 + (500 − 100) = 1400.
    assert compute(capability(), "22000") == Artifact(PERSONAL_AMOUNT, D("1400"))


def test_a_base_halfway_through_the_range_keeps_half_the_supplement() -> None:
    # 500 × 5000 / 10000 = 250, so 1000 + 250 = 1250.
    assert compute(capability(), "25000") == Artifact(PERSONAL_AMOUNT, D("1250"))


def test_a_base_just_below_the_end_of_the_range_keeps_a_sliver_of_the_supplement() -> None:
    # 500 × 9999.99 / 10000 = 499.9995, so 1000 + 0.0005 = 1000.0005.
    assert compute(capability(), "29999.99") == Artifact(PERSONAL_AMOUNT, D("1000.0005"))


def test_a_base_at_the_end_of_the_range_gets_the_base_amount() -> None:
    # threshold + range = 30000: the whole supplement is reduced.
    assert compute(capability(), "30000") == Artifact(PERSONAL_AMOUNT, D("1000"))


def test_a_base_above_the_end_of_the_range_gets_the_base_amount() -> None:
    # The supplement is reduced to nothing, never below: the base amount however far above.
    assert compute(capability(), "30000.01") == Artifact(PERSONAL_AMOUNT, D("1000"))
    assert compute(capability(), "80000") == Artifact(PERSONAL_AMOUNT, D("1000"))
    assert compute(capability(), "1000000") == Artifact(PERSONAL_AMOUNT, D("1000"))


def test_a_zero_supplement_always_gives_the_base_amount() -> None:
    wired = capability(taper(values(supplement="0")))

    assert compute(wired, "15000") == Artifact(PERSONAL_AMOUNT, D("1000"))
    assert compute(wired, "25000") == Artifact(PERSONAL_AMOUNT, D("1000"))
    assert compute(wired, "80000") == Artifact(PERSONAL_AMOUNT, D("1000"))


def test_a_zero_base_amount_tapers_the_supplement_to_zero() -> None:
    wired = capability(taper(values(base="0")))

    assert compute(wired, "15000") == Artifact(PERSONAL_AMOUNT, D("500"))
    assert compute(wired, "25000") == Artifact(PERSONAL_AMOUNT, D("250"))
    assert compute(wired, "80000") == Artifact(PERSONAL_AMOUNT, D("0"))


def test_a_zero_threshold_reduces_from_the_first_unit() -> None:
    wired = capability(taper(values(threshold="0")))

    # 500 × 5000 / 10000 = 250, so 1000 + 250 = 1250.
    assert compute(wired, "5000") == Artifact(PERSONAL_AMOUNT, D("1250"))
    assert compute(wired, "0") == Artifact(PERSONAL_AMOUNT, D("1500"))


def test_the_taper_dataset_supplies_all_four_figures() -> None:
    wired = capability(taper(values(base="200", supplement="80", threshold="5000", range="4000")))

    # 80 × 1000 / 4000 = 20, so 200 + (80 − 20) = 260.
    assert compute(wired, "6000") == Artifact(PERSONAL_AMOUNT, D("260"))


def test_the_full_amount_is_produced_from_the_figures_as_given() -> None:
    # Computed as an exact fraction, so without a rounding rule the figure has no fixed scale.
    wired = capability(taper(values(base="1000.00")))

    assert str(compute(wired, "15000").value) == "1500"
    assert str(compute(wired, "80000").value) == "1000"


def test_keeps_the_amount_exact_without_rounding() -> None:
    # 500 × 2000.5 / 10000 = 100.025, so 1000 + 399.975 = 1399.975, not rounded.
    assert compute(capability(), "22000.5") == Artifact(PERSONAL_AMOUNT, D("1399.975"))


def test_an_inexact_reduction_without_a_rounding_rule_raises_inexact() -> None:
    # 500 × 1000 / 7000 = 500/7 = 71.428571... has no finite expansion. Under `rounding: none` it
    # used to be carried to 28 digits and added to the base, rounding no dataset asked for.
    wired = capability(taper(values(range="7000")))

    with pytest.raises(decimal.Inexact):
        compute(wired, "21000")


def test_the_federal_style_taper_with_a_cent_rule_is_unchanged() -> None:
    # Return E: 14538 + (1591 − 1591 × (198926 − 177882) / 75532) = 15685.7308..., half-up to the
    # cent, once. The quotient is 33481004 / 75532, which does not terminate.
    federal = values(base="14538", supplement="1591", threshold="177882", range="75532")

    assert compute(capability(taper(federal, CENT)), "198926") == Artifact(
        PERSONAL_AMOUNT, D("15685.73")
    )
    with pytest.raises(decimal.Inexact):
        compute(capability(taper(federal)), "198926")


def test_the_reduction_is_divided_exactly_so_a_long_base_keeps_every_digit() -> None:
    # The base is 29 digits, so base + the supplement does not fit a 28-digit context.
    wired = capability(taper(values(base="12345678901234567890123456789", supplement="1"), CENT))

    assert compute(wired, "15000") == Artifact(
        PERSONAL_AMOUNT, D("12345678901234567890123456790.00")
    )
    assert str(compute(wired, "15000").value) == "12345678901234567890123456790.00"


def test_an_even_quotient_stays_exact() -> None:
    # 3 × 1 / 3 = 1 exactly; dividing first (1 / 3 × 3) would not.
    wired = capability(taper(values(supplement="3", threshold="0", range="3")))

    result = wired.compute((Artifact(INCOME, D("1")),))

    (line,) = result.trace
    assert isinstance(line, TaperedAmountLine)
    assert line.reduction == ExactFraction(1)
    assert isinstance(line.reduction, ExactFraction)
    assert result.outputs == (Artifact(PERSONAL_AMOUNT, D("1002")),)


def test_rounds_with_the_taper_datasets_rule() -> None:
    wired = capability(taper(rounding=CENT))

    # 1499.9995 half-up to 1500.00.
    assert compute(wired, "20000.01") == Artifact(PERSONAL_AMOUNT, D("1500.00"))
    # 1399.975 half-up to 1399.98.
    assert compute(wired, "22000.5") == Artifact(PERSONAL_AMOUNT, D("1399.98"))


def test_rounds_an_inexact_quotient_once_with_the_taper_datasets_rule() -> None:
    wired = capability(taper(values(range="7000"), rounding=CENT))

    # 1428.571428571428571428571429 half-up to 1428.57.
    assert compute(wired, "21000") == Artifact(PERSONAL_AMOUNT, D("1428.57"))


def test_rounds_with_another_rule_of_the_taper_dataset() -> None:
    wired = capability(taper(rounding=RoundTo(D("1"), RoundingMode.FLOOR)))

    # 500 × 5000.5 / 10000 = 250.025, so 1249.975, floored to 1249.
    assert compute(wired, "25000.5") == Artifact(PERSONAL_AMOUNT, D("1249"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(taper(rounding=CENT))

    assert str(compute(wired, "15000").value) == "1500.00"
    assert str(compute(wired, "22000").value) == "1400.00"
    assert str(compute(wired, "80000").value) == "1000.00"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(INCOME, D("22000"))))

    assert result.outputs == (Artifact(PERSONAL_AMOUNT, D("1400")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="income"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------
#
# The line's `reduction` is an exact `fractions.Fraction` (it can have no finite decimal form), the
# supplement's share before the floor at zero.


def test_traces_one_tapered_amount_line() -> None:
    trace = capability().compute((Artifact(INCOME, D("22000")),)).trace

    assert trace == (
        TaperedAmountLine(
            output=PERSONAL_AMOUNT,
            base=INCOME,
            base_amount=D("22000"),
            taper=values(),
            rounding=NO_ROUNDING,
            reduction=ExactFraction(100),
            result=D("1400"),
        ),
    )
    assert isinstance(trace[0], TaperedAmountLine)
    assert isinstance(trace[0].reduction, ExactFraction)


def test_traces_a_zero_reduction_at_or_below_the_threshold() -> None:
    for income in ("15000", "20000", "-500"):
        (line,) = capability().compute((Artifact(INCOME, D(income)),)).trace

        assert isinstance(line, TaperedAmountLine)
        assert line.base_amount == D(income)
        assert line.reduction == ExactFraction(0)
        assert isinstance(line.reduction, ExactFraction)
        assert line.result == D("1500")


def test_traces_the_reduction_before_the_floor_above_the_end_of_the_range() -> None:
    # 500 × 60000 / 10000 = 3000, more than the supplement: the line records 3000, the output
    # keeps the base amount.
    trace = capability().compute((Artifact(INCOME, D("80000")),)).trace

    assert trace == (
        TaperedAmountLine(
            PERSONAL_AMOUNT,
            INCOME,
            D("80000"),
            values(),
            NO_ROUNDING,
            ExactFraction(3000),
            D("1000"),
        ),
    )
    assert isinstance(trace[0], TaperedAmountLine)
    assert isinstance(trace[0].reduction, ExactFraction)


def test_traces_the_exact_reduction_and_the_rounded_result() -> None:
    wired = capability(taper(values(range="7000"), rounding=CENT))

    trace = wired.compute((Artifact(INCOME, D("21000")),)).trace

    # 500 × 1000 / 7000 = 500/7, exactly; the result is 1000 + (500 − 500/7), half-up to the cent.
    assert trace == (
        TaperedAmountLine(
            PERSONAL_AMOUNT,
            INCOME,
            D("21000"),
            values(range="7000"),
            CENT,
            ExactFraction(500, 7),
            D("1428.57"),
        ),
    )
    assert isinstance(trace[0], TaperedAmountLine)
    assert trace[0].reduction == ExactFraction(500, 7)
    assert trace[0].reduction.denominator == 7


def test_traces_a_reduction_with_a_finite_expansion_exactly() -> None:
    # 500 × 2000.5 / 10000 = 100.025 = 4001/40.
    trace = capability().compute((Artifact(INCOME, D("22000.5")),)).trace

    (line,) = trace
    assert isinstance(line, TaperedAmountLine)
    assert line.reduction == ExactFraction(4001, 40)
    assert isinstance(line.reduction, ExactFraction)


def test_trace_amount_is_the_result() -> None:
    trace = capability(taper(rounding=CENT)).compute((Artifact(INCOME, D("22000.5")),)).trace

    assert [line.amount for line in trace] == [D("1399.98")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute((Artifact(INCOME, D("25000")),))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, TaperedAmountLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(INCOME, D("22000")),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
