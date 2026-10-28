"""Unit tests for the TieredSurcharge capability (`core/tiered_surcharge`), with made-up figures.

Its slots: one parameter slot `tiers` (a `surcharge_tiers` dataset), one consumed slot `base` and
one produced slot `output`. For each tier, part = the dataset's rule applied to
max(base − threshold, 0) × rate, at most the tier's maximum when it has one; the output is the sum
of the parts. It records one `SurchargeTierLine` per tier, in the dataset's order, whatever the
part, with the tier's maximum or `None`.
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
from tax_calculator.domain.capabilities.tiered_surcharge import TieredSurcharge
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
from tax_calculator.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)
from tax_calculator.domain.trace import SurchargeTierLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

TAX_SO_FAR = ArtifactKind("ex/tax_so_far", Decimal)
SURCHARGE = ArtifactKind("ex/surcharge", Decimal)

# 10% of the base over 100, plus 25% of the base over 300.
LOW = SurchargeTier(D(100), Rate(D("0.10")))
HIGH = SurchargeTier(D(300), Rate(D("0.25")))
# The same tiers, capped: at most 15 from the first and at most 20 from the second.
CAPPED_LOW = SurchargeTier(D(100), Rate(D("0.10")), D(15))
CAPPED_HIGH = SurchargeTier(D(300), Rate(D("0.25")), D(20))


def tiers(
    *given: SurchargeTier, rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[SurchargeTiers]:
    return ParameterDataset(
        "ex/surcharge_tiers",
        2025,
        SURCHARGE_TIERS,
        SurchargeTiers(given or (LOW, HIGH)),
        rounding,
        ("https://example.org/s",),
    )


def capability(data: ParameterDataset[SurchargeTiers] | None = None) -> TieredSurcharge:
    """By default the made-up two tiers on the made-up tax so far, exact."""
    return TieredSurcharge(data or tiers(), TAX_SO_FAR, SURCHARGE)


def compute(wired: TieredSurcharge, base: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(TAX_SO_FAR, D(base)),)).outputs
    return output


def trace_of(wired: TieredSurcharge, base: str) -> tuple[Any, ...]:
    return wired.compute((Artifact(TAX_SO_FAR, D(base)),)).trace


def test_is_registered_as_core_tiered_surcharge() -> None:
    assert CapabilityRegistry.shared().get("core/tiered_surcharge") is TieredSurcharge


def test_is_exported_from_the_capabilities_package() -> None:
    assert "tiered_surcharge" in core.__all__
    assert core.tiered_surcharge.TieredSurcharge is TieredSurcharge


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({TAX_SO_FAR})
    assert capability().produces == frozenset({SURCHARGE})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TieredSurcharge)
    assert "produces" not in vars(TieredSurcharge)


def test_declares_its_slots() -> None:
    assert TieredSurcharge.PARAMETERS == {"tiers": SURCHARGE_TIERS}
    assert TieredSurcharge.PARAMETERS["tiers"] is SURCHARGE_TIERS
    assert TieredSurcharge.CONSUMES == {"base": Decimal}
    assert TieredSurcharge.PRODUCES == {"output": Decimal}
    assert not TieredSurcharge.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    for slots in (TieredSurcharge.PARAMETERS, TieredSurcharge.CONSUMES, TieredSurcharge.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(TieredSurcharge.PARAMETERS, Mapping[str, ParameterKind[SurchargeTiers]])
    assert_type(TieredSurcharge.CONSUMES, Mapping[str, type])
    assert_type(TieredSurcharge.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (TieredSurcharge.PARAMETERS, TieredSurcharge.CONSUMES, TieredSurcharge.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TieredSurcharge(tiers=tiers(), base=TAX_SO_FAR, output=SURCHARGE)

    assert compute(wired, "400") == Artifact(SURCHARGE, D("55"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        TieredSurcharge(tiers(), TAX_SO_FAR, SURCHARGE, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TieredSurcharge") as raised:
        TieredSurcharge(tiers(), TAX_SO_FAR, TAX_SO_FAR)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="TieredSurcharge.*'base'"):
        TieredSurcharge(tiers(), (TAX_SO_FAR,), SURCHARGE)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="TieredSurcharge.*'base'"):
        TieredSurcharge(tiers(), count, SURCHARGE)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[SurchargeTiers]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        TieredSurcharge(rate, TAX_SO_FAR, SURCHARGE)  # type: ignore[arg-type]

    assert callable(wire)


def test_mypy_rejects_bare_tiers_without_their_dataset() -> None:
    def wire() -> None:  # type-checked, never run
        # Parameter slots take the dataset, which carries the rounding rule; never bare values.
        TieredSurcharge(SurchargeTiers((LOW,)), TAX_SO_FAR, SURCHARGE)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(TieredSurcharge, "__type_params__", ())
    assert not getattr(TieredSurcharge, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("base", "surcharge"),
    [
        pytest.param("0", "0", id="zero"),
        pytest.param("50", "0", id="below-the-first-threshold"),
        pytest.param("100", "0", id="at-the-first-threshold"),
        pytest.param("200", "10", id="between-the-thresholds"),  # 10% of 100
        pytest.param("300", "20", id="at-the-second-threshold"),  # 10% of 200
        pytest.param("400", "55", id="above-all-thresholds"),  # 10% of 300 + 25% of 100
        pytest.param("1000", "265", id="far-above"),  # 10% of 900 + 25% of 700
    ],
)
def test_charges_each_tiers_rate_on_the_base_over_its_threshold(base: str, surcharge: str) -> None:
    output = compute(capability(), base)

    assert output == Artifact(SURCHARGE, D(surcharge))
    assert type(output.value) is Decimal


def test_is_exact_without_rounding() -> None:
    # 10% of 0.01 over the first threshold, nothing over the second: no rounding anywhere.
    assert compute(capability(), "100.01") == Artifact(SURCHARGE, D("0.001"))


def test_is_exact_above_all_thresholds() -> None:
    # 10% of 200.333 + 25% of 0.333 = 20.0333 + 0.08325.
    assert compute(capability(), "300.333") == Artifact(SURCHARGE, D("20.11655"))


def test_a_negative_base_produces_zero() -> None:
    # The amount over each threshold is never below zero, so no part is negative.
    assert compute(capability(), "-50") == Artifact(SURCHARGE, D("0"))


def test_a_single_tier() -> None:
    wired = capability(tiers(SurchargeTier(D(50), Rate(D("0.5")))))

    assert compute(wired, "80") == Artifact(SURCHARGE, D("15"))
    assert compute(wired, "50") == Artifact(SURCHARGE, D("0"))


def test_a_tier_from_zero_charges_the_whole_base() -> None:
    wired = capability(tiers(SurchargeTier(D(0), Rate(D("0.2")))))

    assert compute(wired, "80") == Artifact(SURCHARGE, D("16"))


def test_the_dataset_supplies_the_tiers() -> None:
    wired = capability(
        tiers(SurchargeTier(D(1000), Rate(D("0.05"))), SurchargeTier(D(2000), Rate(D("0.5"))))
    )

    # 5% of 1500 + 50% of 500.
    assert compute(wired, "2500") == Artifact(SURCHARGE, D("325"))


def test_rounds_each_part_with_the_datasets_rule() -> None:
    wired = capability(tiers(rounding=CENT))

    # 10% of 200.06 = 20.006 -> 20.01, and 25% of 0.06 = 0.015 -> 0.02: 20.03.
    # Rounding the exact total 20.021 once would give 20.02.
    assert compute(wired, "300.06") == Artifact(SURCHARGE, D("20.03"))


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(tiers(rounding=RoundTo(D("1"), RoundingMode.FLOOR)))

    # 10% of 199.9 = 19.99 -> 19, and nothing over 300.
    assert compute(wired, "299.9") == Artifact(SURCHARGE, D("19"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(tiers(rounding=CENT))

    assert str(compute(wired, "400").value) == "55.00"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(TAX_SO_FAR, D("200"))))

    assert result.outputs == (Artifact(SURCHARGE, D("10")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="tax_so_far"):
        capability().compute(())


# --- tiers with a maximum -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("base", "surcharge"),
    [
        pytest.param("100", "0", id="at-the-first-threshold"),
        pytest.param("200", "10", id="under-the-first-maximum"),  # 10% of 100
        pytest.param("250", "15", id="reaching-the-first-maximum"),  # 10% of 150 = 15
        pytest.param("300", "15", id="on-the-first-plateau"),  # 10% of 200 = 20, at most 15
        pytest.param("350", "27.5", id="on-the-second-slope"),  # 15 + 25% of 50
        pytest.param("380", "35", id="reaching-the-second-maximum"),  # 15 + 25% of 80 = 20
        pytest.param("1000", "35", id="on-the-top-plateau"),  # 15 + 20
    ],
)
def test_charges_each_tiers_rate_over_its_threshold_at_most_its_maximum(
    base: str, surcharge: str
) -> None:
    output = compute(capability(tiers(CAPPED_LOW, CAPPED_HIGH)), base)

    assert output == Artifact(SURCHARGE, D(surcharge))


def test_caps_only_the_tiers_with_a_maximum() -> None:
    wired = capability(tiers(CAPPED_LOW, HIGH))

    # 10% of 900 = 90, at most 15; 25% of 700 = 175, uncapped.
    assert compute(wired, "1000") == Artifact(SURCHARGE, D("190"))


def test_a_zero_maximum_charges_nothing_for_its_tier() -> None:
    wired = capability(tiers(SurchargeTier(D(100), Rate(D("0.10")), D(0)), HIGH))

    # Nothing from the first tier; 25% of 100 from the second.
    assert compute(wired, "400") == Artifact(SURCHARGE, D("25"))


def test_rounds_a_capped_part_with_the_datasets_rule() -> None:
    wired = capability(tiers(SurchargeTier(D(100), Rate(D("0.10")), D("15.555")), rounding=CENT))

    # 10% of 900 = 90, at most 15.555; rounded half-up to the cent: 15.56.
    assert compute(wired, "1000") == Artifact(SURCHARGE, D("15.56"))


def test_rounds_a_part_under_its_maximum_with_the_datasets_rule() -> None:
    wired = capability(tiers(CAPPED_LOW, rounding=CENT))

    # 10% of 100.06 = 10.006 -> 10.01, under the maximum of 15.
    assert compute(wired, "200.06") == Artifact(SURCHARGE, D("10.01"))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_per_tier_in_order() -> None:
    assert trace_of(capability(), "400") == (
        SurchargeTierLine(
            output=SURCHARGE,
            base=TAX_SO_FAR,
            base_amount=D("400"),
            threshold=D(100),
            rate=Rate(D("0.10")),
            rounding=NO_ROUNDING,
            part=D("30"),
        ),
        SurchargeTierLine(
            output=SURCHARGE,
            base=TAX_SO_FAR,
            base_amount=D("400"),
            threshold=D(300),
            rate=Rate(D("0.25")),
            rounding=NO_ROUNDING,
            part=D("25"),
        ),
    )


def test_traces_a_tier_the_base_does_not_reach_with_a_zero_part() -> None:
    trace = trace_of(capability(), "200")

    assert len(trace) == 2
    assert trace[1] == SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("200"), D(300), Rate(D("0.25")), NO_ROUNDING, D("0")
    )


def test_traces_every_tier_below_the_first_threshold() -> None:
    trace = trace_of(capability(), "50")

    assert [line.threshold for line in trace] == [D(100), D(300)]
    assert [line.part for line in trace] == [D(0), D(0)]


def test_traces_one_line_for_a_single_tier() -> None:
    trace = trace_of(capability(tiers(SurchargeTier(D(50), Rate(D("0.5"))))), "80")

    assert trace == (
        SurchargeTierLine(
            SURCHARGE, TAX_SO_FAR, D("80"), D(50), Rate(D("0.5")), NO_ROUNDING, D("15")
        ),
    )


def test_traces_the_datasets_rounding_rule_and_each_rounded_part() -> None:
    trace = trace_of(capability(tiers(rounding=CENT)), "300.06")

    assert trace == (
        SurchargeTierLine(
            SURCHARGE, TAX_SO_FAR, D("300.06"), D(100), Rate(D("0.10")), CENT, D("20.01")
        ),
        SurchargeTierLine(
            SURCHARGE, TAX_SO_FAR, D("300.06"), D(300), Rate(D("0.25")), CENT, D("0.02")
        ),
    )


def test_traces_no_maximum_for_a_tier_without_one() -> None:
    assert [line.maximum for line in trace_of(capability(), "400")] == [None, None]


def test_traces_each_tiers_maximum_and_its_capped_part() -> None:
    trace = trace_of(capability(tiers(CAPPED_LOW, CAPPED_HIGH)), "1000")

    assert trace == (
        SurchargeTierLine(
            output=SURCHARGE,
            base=TAX_SO_FAR,
            base_amount=D("1000"),
            threshold=D(100),
            rate=Rate(D("0.10")),
            rounding=NO_ROUNDING,
            part=D("15"),
            maximum=D(15),
        ),
        SurchargeTierLine(
            output=SURCHARGE,
            base=TAX_SO_FAR,
            base_amount=D("1000"),
            threshold=D(300),
            rate=Rate(D("0.25")),
            rounding=NO_ROUNDING,
            part=D("20"),
            maximum=D(20),
        ),
    )


def test_traces_the_maximum_of_a_tier_the_base_does_not_reach() -> None:
    (low, high) = trace_of(capability(tiers(CAPPED_LOW, CAPPED_HIGH)), "200")

    assert (low.part, low.maximum) == (D("10"), D(15))
    assert (high.part, high.maximum) == (D("0"), D(20))


def test_traces_the_maximum_only_for_the_tiers_that_have_one() -> None:
    trace = trace_of(capability(tiers(CAPPED_LOW, HIGH)), "1000")

    assert [line.maximum for line in trace] == [D(15), None]


def test_the_capped_parts_in_the_trace_add_up_to_the_output() -> None:
    wired = capability(tiers(CAPPED_LOW, CAPPED_HIGH, rounding=CENT))
    result = wired.compute((Artifact(TAX_SO_FAR, D("350.01")),))

    (output,) = result.outputs
    assert sum((line.amount for line in result.trace), D(0)) == output.value
    assert output.value == D("27.50")


def test_trace_amounts_are_the_parts() -> None:
    assert [line.amount for line in trace_of(capability(), "1000")] == [D("90"), D("175")]


def test_the_parts_in_the_trace_add_up_to_the_output() -> None:
    result = capability(tiers(rounding=CENT)).compute((Artifact(TAX_SO_FAR, D("300.06")),))

    (output,) = result.outputs
    assert sum((line.amount for line in result.trace), D(0)) == output.value


def test_trace_holds_no_text() -> None:
    for line in trace_of(capability(), "400"):
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
