"""Unit tests for the TieredContributionRate capability (`ca/contribution_tier_rate`).

The output is the tier's rate while the earnings are at or over its lower bound and under its
upper bound, 0 at the upper bound and outside: the rate of a further dollar of the earnings. It
records one `ContributionTierRateLine`, and its English text names the band and the rate.
"""

from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType
from typing import Any, cast

import pytest

import tax_engine.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.contribution_tier_rate import TieredContributionRate
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)
from tax_engine.jurisdictions.ca.trace.contribution_tier_rate import ContributionTierRateLine
from tests.capabilities import bundled_capabilities

D = Decimal
EARNINGS = AmountKind("ex/earnings")
RATE_OUT = AmountKind("ex/rate")
TIER = ParameterDataset(
    "ex/some_tier",
    2025,
    CONTRIBUTION_TIER,
    ContributionTier(Rate(D("0.05")), D("3000"), D("50000"), D("2350")),
    NO_ROUNDING,
    ("https://example.org/t",),
)


def compute(earnings: str) -> Any:
    wired = TieredContributionRate(TIER, EARNINGS, RATE_OUT)
    return wired.compute((Artifact(EARNINGS, D(earnings)),))


def test_is_registered_as_ca_contribution_tier_rate() -> None:
    assert bundled_capabilities().get("ca/contribution_tier_rate") is TieredContributionRate


def test_declares_its_slots() -> None:
    assert TieredContributionRate.PARAMETERS == {"tier": CONTRIBUTION_TIER}
    assert TieredContributionRate.CONSUMES == {"earnings": Decimal}
    assert TieredContributionRate.PRODUCES == {"output": Decimal}


@pytest.mark.parametrize(
    ("earnings", "rate"),
    [
        ("0", "0"),
        ("2999.99", "0"),
        ("3000", "0.05"),
        ("3000.01", "0.05"),
        ("23000", "0.05"),
        ("49999.99", "0.05"),
        ("50000", "0"),
        ("90000", "0"),
    ],
)
def test_is_the_tier_rate_from_its_lower_bound_up_to_its_upper_bound(
    earnings: str, rate: str
) -> None:
    (output,) = compute(earnings).outputs

    assert output == Artifact(RATE_OUT, D(rate))


def test_records_one_line_and_explains_it_in_english() -> None:
    result = compute("23000")
    (line,) = result.trace

    assert isinstance(line, ContributionTierRateLine)
    assert line.amount == D("0.05")
    text = EnglishTraceRenderer().render(line)
    assert "5%" in text
    assert "is at least 3000.00 and under 50000.00" in text


# --- the contract -----------------------------------------------------------------------------


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TieredContributionRate)
    assert "produces" not in vars(TieredContributionRate)


def test_its_slots_are_read_only() -> None:
    for slots in (
        TieredContributionRate.CONSUMES,
        TieredContributionRate.PRODUCES,
        TieredContributionRate.PARAMETERS,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        TieredContributionRate.CONSUMES,
        TieredContributionRate.PRODUCES,
        TieredContributionRate.PARAMETERS,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TieredContributionRate(tier=TIER, earnings=EARNINGS, output=RATE_OUT)

    assert isinstance(wired, TieredContributionRate)


def test_rejects_one_kind_as_both_earnings_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TieredContributionRate"):
        TieredContributionRate(TIER, EARNINGS, EARNINGS)


def test_rejects_a_list_of_kinds_for_its_earnings() -> None:
    with pytest.raises(InvalidCapabilityError, match="TieredContributionRate"):
        TieredContributionRate(TIER, (EARNINGS,), RATE_OUT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # The ignore fails under mypy (warn_unused_ignores) if wiring a kind of another value type is
    # ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="TieredContributionRate"):
        TieredContributionRate(TIER, count, RATE_OUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(TieredContributionRate, "__type_params__", ())
    assert not getattr(TieredContributionRate, "__parameters__", ())


def test_a_missing_earnings_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError):
        TieredContributionRate(TIER, EARNINGS, RATE_OUT).compute(())
