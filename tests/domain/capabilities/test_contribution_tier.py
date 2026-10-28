"""Unit tests for the TieredContribution capability (`core/contribution_tier`), made-up values.

Its slots: one parameter slot `tier` (a `contribution_tier` dataset), one consumed slot `earnings`
and one produced slot `output`. The contributory earnings are the part of `earnings` inside the
tier's band, `max(min(earnings, upper) - lower, 0)`; the output is
`min(rounding.apply(contributory × rate), maximum)`, with the `tier` dataset's rule (which defaults
to no rounding). Negative earnings contribute nothing. It records one `ContributionTierLine`.

The class is `TieredContribution`, not `ContributionTier`, so it does not share a name with the
`ContributionTier` value object it reads.
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
from tax_calculator.domain.capabilities.contribution_tier import TieredContribution
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.trace import ContributionTierLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


EARNINGS = ArtifactKind("ex/earnings", Decimal)
CONTRIBUTION = ArtifactKind("ex/contribution", Decimal)


def values(
    rate: str = "0.05", lower: str = "3000", upper: str = "50000", maximum: str = "2350"
) -> ContributionTier:
    """By default 5% of the earnings between 3000 and 50000, at most 2350 (the full band's 5%)."""
    return ContributionTier(Rate(D(rate)), D(lower), D(upper), D(maximum))


def tier(
    tier_values: ContributionTier | None = None, rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[ContributionTier]:
    return ParameterDataset(
        "ex/some_tier",
        2025,
        CONTRIBUTION_TIER,
        tier_values or values(),
        rounding,
        ("https://example.org/t",),
    )


def capability(tier_data: ParameterDataset[ContributionTier] | None = None) -> TieredContribution:
    """By default the made-up earnings under the default tier, exact."""
    return TieredContribution(tier_data or tier(), EARNINGS, CONTRIBUTION)


def compute(wired: TieredContribution, earnings: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(EARNINGS, D(earnings)),)).outputs
    return output


def test_is_registered_as_core_contribution_tier() -> None:
    assert CapabilityRegistry.shared().get("core/contribution_tier") is TieredContribution


def test_is_exported_from_the_capabilities_package() -> None:
    assert "contribution_tier" in core.__all__
    assert core.contribution_tier.TieredContribution is TieredContribution


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({EARNINGS})
    assert capability().produces == frozenset({CONTRIBUTION})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TieredContribution)
    assert "produces" not in vars(TieredContribution)


def test_declares_its_slots() -> None:
    assert TieredContribution.PARAMETERS == {"tier": CONTRIBUTION_TIER}
    assert TieredContribution.PARAMETERS["tier"] is CONTRIBUTION_TIER
    assert TieredContribution.CONSUMES == {"earnings": Decimal}
    assert TieredContribution.PRODUCES == {"output": Decimal}
    assert not TieredContribution.is_list_slot("earnings")


def test_its_slots_are_read_only() -> None:
    for slots in (
        TieredContribution.PARAMETERS,
        TieredContribution.CONSUMES,
        TieredContribution.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(TieredContribution.PARAMETERS, Mapping[str, ParameterKind[ContributionTier]])
    assert_type(TieredContribution.CONSUMES, Mapping[str, type])
    assert_type(TieredContribution.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        TieredContribution.PARAMETERS,
        TieredContribution.CONSUMES,
        TieredContribution.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TieredContribution(tier=tier(), earnings=EARNINGS, output=CONTRIBUTION)

    assert compute(wired, "23000") == Artifact(CONTRIBUTION, D("1000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        TieredContribution(tier(), EARNINGS, CONTRIBUTION, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_earnings_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TieredContribution") as raised:
        TieredContribution(tier(), EARNINGS, EARNINGS)

    message = str(raised.value)
    assert "'earnings'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_earnings() -> None:
    with pytest.raises(InvalidCapabilityError, match="TieredContribution.*'earnings'"):
        TieredContribution(tier(), (EARNINGS,), CONTRIBUTION)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="TieredContribution.*'earnings'"):
        TieredContribution(tier(), count, CONTRIBUTION)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[ContributionTier]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        TieredContribution(rate, EARNINGS, CONTRIBUTION)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(TieredContribution, "__type_params__", ())
    assert not getattr(TieredContribution, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_earnings_below_the_lower_bound_contribute_nothing() -> None:
    output = compute(capability(), "2000")

    assert output == Artifact(CONTRIBUTION, D("0"))
    assert type(output.value) is Decimal


def test_earnings_at_the_lower_bound_contribute_nothing() -> None:
    assert compute(capability(), "3000") == Artifact(CONTRIBUTION, D("0"))


def test_zero_earnings_contribute_nothing() -> None:
    assert compute(capability(), "0") == Artifact(CONTRIBUTION, D("0"))


def test_negative_earnings_contribute_nothing() -> None:
    # max(min(earnings, upper) - lower, 0): negative earnings are zero contributory earnings.
    assert compute(capability(), "-500") == Artifact(CONTRIBUTION, D("0"))


def test_negative_earnings_under_a_band_from_zero_contribute_nothing() -> None:
    wired = capability(tier(values(lower="0")))

    assert compute(wired, "-500") == Artifact(CONTRIBUTION, D("0"))


def test_earnings_inside_the_band_pay_the_rate_on_the_part_above_the_lower_bound() -> None:
    # (23000 - 3000) × 5% = 1000.
    assert compute(capability(), "23000") == Artifact(CONTRIBUTION, D("1000"))


def test_earnings_just_above_the_lower_bound_pay_on_that_part_only() -> None:
    # (3000.01 - 3000) × 5% = 0.0005, exact.
    assert compute(capability(), "3000.01") == Artifact(CONTRIBUTION, D("0.0005"))


def test_earnings_at_the_upper_bound_pay_the_rate_on_the_whole_band() -> None:
    # (50000 - 3000) × 5% = 2350.
    assert compute(capability(), "50000") == Artifact(CONTRIBUTION, D("2350"))


def test_earnings_above_the_upper_bound_are_capped_at_the_band() -> None:
    # Only the band counts: (50000 - 3000) × 5% = 2350, however far above the upper bound.
    assert compute(capability(), "80000") == Artifact(CONTRIBUTION, D("2350"))
    assert compute(capability(), "1000000") == Artifact(CONTRIBUTION, D("2350"))


def test_the_upper_bound_caps_the_band_below_the_maximum() -> None:
    # A maximum above the full band's figure never binds: (50000 - 3000) × 5% = 2350 < 9999.
    wired = capability(tier(values(maximum="9999")))

    assert compute(wired, "80000") == Artifact(CONTRIBUTION, D("2350"))


def test_the_maximum_binds_above_the_upper_bound() -> None:
    wired = capability(tier(values(maximum="2000")))

    assert compute(wired, "80000") == Artifact(CONTRIBUTION, D("2000"))


def test_the_maximum_binds_inside_the_band() -> None:
    # (45000 - 3000) × 5% = 2100 > 2000.
    wired = capability(tier(values(maximum="2000")))

    assert compute(wired, "45000") == Artifact(CONTRIBUTION, D("2000"))


def test_below_the_maximum_the_rated_band_is_produced() -> None:
    # (40000 - 3000) × 5% = 1850 < 2000.
    wired = capability(tier(values(maximum="2000")))

    assert compute(wired, "40000") == Artifact(CONTRIBUTION, D("1850"))


def test_a_binding_maximum_is_produced_as_given() -> None:
    wired = capability(tier(values(maximum="2000.00")))

    assert str(compute(wired, "80000").value) == "2000.00"


def test_a_zero_maximum_produces_zero() -> None:
    wired = capability(tier(values(maximum="0")))

    assert compute(wired, "23000") == Artifact(CONTRIBUTION, D("0"))


def test_a_zero_rate_produces_zero() -> None:
    wired = capability(tier(values(rate="0")))

    assert compute(wired, "23000") == Artifact(CONTRIBUTION, D("0"))


def test_a_band_from_zero_rates_all_earnings_up_to_the_upper_bound() -> None:
    wired = capability(tier(values(rate="0.1", lower="0", upper="1000", maximum="100")))

    assert compute(wired, "400") == Artifact(CONTRIBUTION, D("40"))
    assert compute(wired, "4000") == Artifact(CONTRIBUTION, D("100"))


def test_the_tier_dataset_supplies_the_rate_and_the_bounds() -> None:
    wired = capability(tier(values(rate="0.04", lower="10000", upper="20000", maximum="400")))

    # (15000 - 10000) × 4% = 200.
    assert compute(wired, "15000") == Artifact(CONTRIBUTION, D("200"))


def test_keeps_the_product_exact_without_rounding() -> None:
    # (23000.10 - 3000) × 5% = 1000.0050, not rounded.
    output = compute(capability(), "23000.10")

    assert output == Artifact(CONTRIBUTION, D("1000.005"))
    assert str(output.value) == "1000.0050"


def test_keeps_a_tiny_contribution_exact() -> None:
    output = compute(capability(), "3000.0000000000000001")

    assert output == Artifact(CONTRIBUTION, D("5E-18"))


def test_rounds_with_the_tier_datasets_rule() -> None:
    wired = capability(tier(rounding=CENT))

    # (23000.10 - 3000) × 5% = 1000.005, half-up to 1000.01.
    assert compute(wired, "23000.10") == Artifact(CONTRIBUTION, D("1000.01"))


def test_rounds_with_another_rule_of_the_tier_dataset() -> None:
    wired = capability(tier(rounding=RoundTo(D("1"), RoundingMode.FLOOR)))

    # (23019.99 - 3000) × 5% = 1000.9995, floored to 1000.
    assert compute(wired, "23019.99") == Artifact(CONTRIBUTION, D("1000"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(tier(rounding=CENT))

    assert str(compute(wired, "23000").value) == "1000.00"
    assert str(compute(wired, "2000").value) == "0.00"


def test_the_maximum_applies_after_rounding_and_is_not_rounded() -> None:
    # min(rounding.apply(contributory × rate), maximum): the product 1000.006 rounds half-up to
    # 1000.01, then the maximum 1000.005 binds as given.
    wired = capability(tier(values(maximum="1000.005"), rounding=CENT))

    output = compute(wired, "23000.12")

    assert output == Artifact(CONTRIBUTION, D("1000.005"))


def test_rounding_alone_can_reach_the_maximum() -> None:
    # The product 1999.996 rounds half-up to 2000.00, which equals the maximum.
    wired = capability(tier(values(maximum="2000"), rounding=CENT))

    assert compute(wired, "42999.92") == Artifact(CONTRIBUTION, D("2000"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(EARNINGS, D("23000"))))

    assert result.outputs == (Artifact(CONTRIBUTION, D("1000")),)


def test_a_missing_earnings_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="earnings"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_contribution_tier_line() -> None:
    trace = capability().compute((Artifact(EARNINGS, D("23000")),)).trace

    assert trace == (
        ContributionTierLine(
            output=CONTRIBUTION,
            earnings=EARNINGS,
            earnings_amount=D("23000"),
            tier=values(),
            rounding=NO_ROUNDING,
            contributory=D("20000"),
            result=D("1000"),
        ),
    )


def test_traces_the_band_as_the_contributory_earnings_above_the_upper_bound() -> None:
    wired = capability(tier(values(maximum="2000")))

    trace = wired.compute((Artifact(EARNINGS, D("80000")),)).trace

    assert trace == (
        ContributionTierLine(
            CONTRIBUTION,
            EARNINGS,
            D("80000"),
            values(maximum="2000"),
            NO_ROUNDING,
            D("47000"),
            D("2000"),
        ),
    )


def test_traces_zero_contributory_earnings_below_the_lower_bound() -> None:
    trace = capability().compute((Artifact(EARNINGS, D("-500")),)).trace

    (line,) = trace
    assert isinstance(line, ContributionTierLine)
    assert line.earnings_amount == D("-500")
    assert line.contributory == D("0")
    assert line.result == D("0")


def test_traces_the_tier_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(tier(rounding=CENT)).compute((Artifact(EARNINGS, D("23000.10")),)).trace

    assert trace == (
        ContributionTierLine(
            CONTRIBUTION, EARNINGS, D("23000.10"), values(), CENT, D("20000.10"), D("1000.01")
        ),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability(tier(rounding=CENT)).compute((Artifact(EARNINGS, D("23000.10")),)).trace

    assert [line.amount for line in trace] == [D("1000.01")]


def test_trace_result_is_the_output() -> None:
    result = capability(tier(values(maximum="2000"))).compute((Artifact(EARNINGS, D("80000")),))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, ContributionTierLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(EARNINGS, D("23000")),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
