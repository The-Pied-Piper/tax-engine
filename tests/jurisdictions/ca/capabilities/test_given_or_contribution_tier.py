"""Unit tests for the GivenOrTieredContribution capability (`ca/given_or_contribution_tier`).

A form line that is given on the form when the filer has it, and computed from the earnings when
left blank, such as T2204 line 4. Its slots: one parameter slot `tier` (a `contribution_tier`
dataset), two consumed slots `given` (may be blank) and `earnings`, and one produced slot `output`.
Its `given` slot is in `BLANK_ALLOWED`, so a manifest may give it a `COMPUTE` rule; `earnings` may
never be blank.

A given figure is the output, unchanged: no rounding, no cap, its scale kept. A blank `given` is the
tier result on `earnings`, computed exactly as `TieredContribution` computes it, and records the
same `ContributionTierLine`. A given figure records one `GivenAmountLine`.

The class shares a parent class with `TieredContribution`, not `Capability` alone; the
capability's own contract is tested here, the calculation in `test_contribution_tier.py`.
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK, COMPUTE
from tax_engine.domain.capability import Capability
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.jurisdictions.ca.capabilities.contribution_tier import TieredContribution
from tax_engine.jurisdictions.ca.capabilities.given_or_contribution_tier import (
    GivenOrTieredContribution,
)
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)
from tax_engine.jurisdictions.ca.trace import ContributionTierLine, GivenAmountLine
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


GIVEN = AmountKind("ex/given")
EARNINGS = AmountKind("ex/earnings")
OUTPUT = AmountKind("ex/premiums_deducted")


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


def capability(
    tier_data: ParameterDataset[ContributionTier] | None = None,
) -> GivenOrTieredContribution:
    """By default the made-up earnings under the default tier, exact."""
    return GivenOrTieredContribution(tier_data or tier(), GIVEN, EARNINGS, OUTPUT)


def pair(given: str | None, earnings: str | None) -> tuple[Artifact[Any], ...]:
    """The inputs for `given` and `earnings`; None is a blank."""
    return (
        Artifact(GIVEN, BLANK if given is None else D(given)),
        Artifact(EARNINGS, BLANK if earnings is None else D(earnings)),
    )


def run_blank_computed(wired: GivenOrTieredContribution, earnings: str) -> Artifact[Any]:
    """Run `wired` with `given` blank and rule COMPUTE, and return its output."""
    (output,) = wired.with_blank_rules({"given": COMPUTE}).run(pair(None, earnings)).outputs
    return output


def compute_given(wired: GivenOrTieredContribution, given: str, earnings: str) -> Artifact[Any]:
    (output,) = wired.compute(pair(given, earnings)).outputs
    return output


def test_is_registered_as_ca_given_or_contribution_tier() -> None:
    assert bundled_capabilities().get("ca/given_or_contribution_tier") is GivenOrTieredContribution


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({GIVEN, EARNINGS})
    assert capability().produces == frozenset({OUTPUT})


def test_declares_its_slots() -> None:
    assert GivenOrTieredContribution.PARAMETERS == {"tier": CONTRIBUTION_TIER}
    assert GivenOrTieredContribution.PARAMETERS["tier"] is CONTRIBUTION_TIER
    assert GivenOrTieredContribution.CONSUMES == {"given": Decimal, "earnings": Decimal}
    assert GivenOrTieredContribution.PRODUCES == {"output": Decimal}
    assert not GivenOrTieredContribution.is_list_slot("given")
    assert not GivenOrTieredContribution.is_list_slot("earnings")


def test_declares_that_only_given_may_be_blank() -> None:
    assert GivenOrTieredContribution.BLANK_ALLOWED == frozenset({"given"})


def test_its_slots_are_read_only() -> None:
    for slots in (
        GivenOrTieredContribution.PARAMETERS,
        GivenOrTieredContribution.CONSUMES,
        GivenOrTieredContribution.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(GivenOrTieredContribution.PARAMETERS, Mapping[str, ParameterKind[ContributionTier]])
    assert_type(GivenOrTieredContribution.CONSUMES, Mapping[str, type])
    assert_type(GivenOrTieredContribution.PRODUCES, Mapping[str, type])


def test_shares_a_parent_class_with_tiered_contribution() -> None:
    shared = set(GivenOrTieredContribution.__mro__) & set(TieredContribution.__mro__)
    parents = shared - {GivenOrTieredContribution, TieredContribution, Capability, ABC, object}

    assert len(parents) == 1
    (parent,) = parents
    assert issubclass(GivenOrTieredContribution, parent)
    assert issubclass(TieredContribution, parent)


def test_the_shared_parent_is_not_a_registered_capability() -> None:
    shared = set(GivenOrTieredContribution.__mro__) & set(TieredContribution.__mro__)
    parents = shared - {GivenOrTieredContribution, TieredContribution, Capability, ABC, object}

    (parent,) = parents
    assert getattr(parent, "IDENTIFIER", None) is None


def test_tiered_contribution_keeps_its_identifier_and_slots() -> None:
    assert bundled_capabilities().get("ca/contribution_tier") is TieredContribution
    assert TieredContribution.PARAMETERS == {"tier": CONTRIBUTION_TIER}
    assert TieredContribution.CONSUMES == {"earnings": Decimal}
    assert TieredContribution.PRODUCES == {"output": Decimal}


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = GivenOrTieredContribution(tier=tier(), given=GIVEN, earnings=EARNINGS, output=OUTPUT)

    assert compute_given(wired, "1148.00", "23000") == Artifact(OUTPUT, D("1148.00"))


def test_rejects_one_kind_as_both_given_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="GivenOrTieredContribution") as raised:
        GivenOrTieredContribution(tier(), GIVEN, EARNINGS, GIVEN)

    message = str(raised.value)
    assert "'given'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_earnings_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="GivenOrTieredContribution") as raised:
        GivenOrTieredContribution(tier(), GIVEN, EARNINGS, EARNINGS)

    message = str(raised.value)
    assert "'earnings'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_given() -> None:
    with pytest.raises(InvalidCapabilityError, match="GivenOrTieredContribution.*'given'"):
        GivenOrTieredContribution(tier(), (GIVEN,), EARNINGS, OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_earnings() -> None:
    with pytest.raises(InvalidCapabilityError, match="GivenOrTieredContribution.*'earnings'"):
        GivenOrTieredContribution(tier(), GIVEN, (EARNINGS,), OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(GivenOrTieredContribution, "__type_params__", ())
    assert not getattr(GivenOrTieredContribution, "__parameters__", ())


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        GivenOrTieredContribution(tier(), GIVEN, EARNINGS, OUTPUT, NO_ROUNDING)  # type: ignore[call-arg]


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        GivenOrTieredContribution.PARAMETERS,
        GivenOrTieredContribution.CONSUMES,
        GivenOrTieredContribution.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


# --- a given figure ---------------------------------------------------------------------------


def test_a_given_figure_is_the_output_unchanged() -> None:
    output = compute_given(capability(), "1148.00", "70000")

    assert output == Artifact(OUTPUT, D("1148.00"))
    assert type(output.value) is Decimal
    assert str(output.value) == "1148.00"


def test_a_given_figure_is_not_computed_from_the_earnings() -> None:
    # The earnings would compute 1000; the given figure wins.
    assert compute_given(capability(), "500", "23000") == Artifact(OUTPUT, D("500"))


def test_a_given_figure_is_not_limited_by_the_band() -> None:
    # Far above the upper bound and the maximum: the given figure is not capped.
    assert compute_given(capability(), "9999", "1000000") == Artifact(OUTPUT, D("9999"))


def test_a_given_figure_is_not_capped_by_the_maximum() -> None:
    wired = capability(tier(values(maximum="2000")))

    assert str(compute_given(wired, "2100.00", "80000").value) == "2100.00"


def test_a_given_figure_is_not_rounded_by_the_tier_rule() -> None:
    wired = capability(tier(rounding=CENT))

    assert str(compute_given(wired, "1148.123", "23000").value) == "1148.123"


def test_a_given_zero_is_zero() -> None:
    assert compute_given(capability(), "0", "23000") == Artifact(OUTPUT, D("0"))


def test_a_given_figure_below_the_band_is_unchanged() -> None:
    assert compute_given(capability(), "100", "2000") == Artifact(OUTPUT, D("100"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute(
        (Artifact(other, D("9")), Artifact(GIVEN, D("1148")), Artifact(EARNINGS, D("23000")))
    )

    assert result.outputs == (Artifact(OUTPUT, D("1148")),)


# --- a blank given, left to compute -----------------------------------------------------------


@pytest.mark.parametrize(
    ("earnings", "expected"),
    [
        # Below the band, at its lower bound and at zero: nothing, as TieredContribution gives.
        ("2000", "0"),
        ("3000", "0"),
        ("0", "0"),
        # Inside the band: 5% of the part above 3000.
        ("23000", "1000"),
        # Above the upper bound: only the band counts, 5% of 47000 is 2350.
        ("80000", "2350"),
    ],
)
def test_a_blank_given_is_the_tier_result_on_the_earnings(earnings: str, expected: str) -> None:
    assert run_blank_computed(capability(), earnings) == Artifact(OUTPUT, D(expected))


def test_a_blank_given_is_capped_at_the_tier_maximum() -> None:
    wired = capability(tier(values(maximum="2000")))

    assert run_blank_computed(wired, "80000") == Artifact(OUTPUT, D("2000"))


def test_a_blank_given_rounds_with_the_tier_rule() -> None:
    wired = capability(tier(rounding=CENT))

    # (23000.10 - 3000) × 5% = 1000.005, half-up to 1000.01.
    assert run_blank_computed(wired, "23000.10") == Artifact(OUTPUT, D("1000.01"))


@pytest.mark.parametrize("earnings", ["0", "2000", "3000", "23000", "23000.10", "80000"])
def test_a_blank_given_matches_tiered_contribution_on_the_same_earnings(earnings: str) -> None:
    wired = capability(tier(rounding=CENT, tier_values=values(maximum="2000")))
    tiered = TieredContribution(
        tier(rounding=CENT, tier_values=values(maximum="2000")), EARNINGS, OUTPUT
    )

    expected = tiered.compute((Artifact(EARNINGS, D(earnings)),)).outputs

    assert run_blank_computed(wired, earnings) == expected[0]


def test_a_blank_given_traces_the_contribution_tier_line_tiered_contribution_traces() -> None:
    wired = capability(tier(values(maximum="2000"), rounding=CENT))

    trace = wired.with_blank_rules({"given": COMPUTE}).run(pair(None, "23000.10")).trace

    assert trace == (
        ContributionTierLine(
            OUTPUT,
            EARNINGS,
            D("23000.10"),
            values(maximum="2000"),
            CENT,
            D("20000.10"),
            D("1000.01"),
        ),
    )


def test_a_blank_given_traces_the_same_lines_as_tiered_contribution() -> None:
    wired = capability()
    tiered = TieredContribution(tier(), EARNINGS, OUTPUT)

    blank_trace = wired.with_blank_rules({"given": COMPUTE}).run(pair(None, "23000")).trace
    tiered_trace = tiered.compute((Artifact(EARNINGS, D("23000")),)).trace

    assert blank_trace == tiered_trace


def test_a_blank_given_records_no_given_amount_line() -> None:
    trace = capability().with_blank_rules({"given": COMPUTE}).run(pair(None, "23000")).trace

    assert not any(isinstance(line, GivenAmountLine) for line in trace)


# --- refusals ---------------------------------------------------------------------------------


def test_a_blank_given_without_a_rule_is_refused() -> None:
    with pytest.raises(BlankNotAllowedError, match="may not be blank"):
        capability().run(pair(None, "23000"))


def test_a_blank_earnings_is_refused() -> None:
    with pytest.raises(BlankNotAllowedError, match="may not be blank"):
        capability().run(pair("1148", None))


def test_a_blank_earnings_is_refused_when_given_is_left_to_compute() -> None:
    with pytest.raises(BlankNotAllowedError, match="may not be blank"):
        capability().with_blank_rules({"given": COMPUTE}).run(pair(None, None))


def test_a_blank_earnings_is_refused_even_with_a_given_figure() -> None:
    with pytest.raises(BlankNotAllowedError):
        capability().with_blank_rules({"given": COMPUTE}).run(pair("1148", None))


def test_a_missing_given_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="given"):
        capability().compute((Artifact(EARNINGS, D("23000")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_given_amount_line_for_a_given_figure() -> None:
    trace = capability().compute(pair("1148.00", "70000")).trace

    assert trace == (GivenAmountLine(output=OUTPUT, given=GIVEN, given_amount=D("1148.00")),)


def test_trace_amount_is_the_given_figure() -> None:
    trace = capability().compute(pair("1148.00", "70000")).trace

    assert [line.amount for line in trace] == [D("1148.00")]


def test_the_given_amount_line_renders_in_english() -> None:
    trace = capability().compute(pair("1148.00", "70000")).trace

    rendered = EnglishTraceRenderer().render_all(trace)

    assert rendered == ("given (1148.00), as given.",)


def test_trace_holds_no_text_for_a_given_figure() -> None:
    trace = capability().compute(pair("1148.00", "70000")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_trace_holds_no_text_for_a_computed_figure() -> None:
    trace = capability().with_blank_rules({"given": COMPUTE}).run(pair(None, "23000")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
