"""Unit tests for ContributionTier: a capped rate on a band, the `contribution_tier` kind's values.

A tier holds a `Rate`, the band's `lower` and `upper` bounds and the `maximum` contribution, all
exact. Like `Rate` and `Amount`, the value object checks itself: bounds that are negative, not
finite or out of order, or a negative maximum, are an `InvalidContributionTierError`. Values are
made up.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_engine.domain.errors import DomainError, InvalidContributionTierError
from tax_engine.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate

D = Decimal


def tier(
    rate: str = "0.05", lower: str = "3000", upper: str = "50000", maximum: str = "2350"
) -> ContributionTier:
    return ContributionTier(rate=Rate(D(rate)), lower=D(lower), upper=D(upper), maximum=D(maximum))


def test_holds_its_rate_bounds_and_maximum() -> None:
    held = tier()

    assert held.rate == Rate(D("0.05"))
    assert held.lower == D("3000")
    assert held.upper == D("50000")
    assert held.maximum == D("2350")


def test_holds_its_fields_in_order() -> None:
    assert [field.name for field in fields(ContributionTier)] == [
        "rate",
        "lower",
        "upper",
        "maximum",
    ]


def test_is_built_positionally_in_field_order() -> None:
    assert ContributionTier(Rate(D("0.05")), D("3000"), D("50000"), D("2350")) == tier()


def test_equal_values_are_equal_tiers() -> None:
    assert tier("0.05", "3000", "50000", "2350") == tier("0.050", "3000.00", "50000.0", "2350.00")


def test_tiers_differ_by_any_field() -> None:
    assert tier() != tier(rate="0.04")
    assert tier() != tier(lower="3500")
    assert tier() != tier(upper="60000")
    assert tier() != tier(maximum="2000")


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, tier()).maximum = D("1")


def test_is_hashable() -> None:
    assert hash(tier()) == hash(tier())


def test_keeps_its_figures_exactly_as_given() -> None:
    held = tier(lower="3000.50", upper="50000.00", maximum="2350.10")

    # No rounding, no normalising.
    assert (str(held.lower), str(held.upper), str(held.maximum)) == (
        "3000.50",
        "50000.00",
        "2350.10",
    )


def test_accepts_a_band_starting_at_zero() -> None:
    assert tier(lower="0").lower == D("0")


def test_accepts_a_zero_maximum() -> None:
    assert tier(maximum="0").maximum == D("0")


def test_accepts_a_narrow_band() -> None:
    held = tier(lower="100", upper="100.01")

    assert held.upper - held.lower == D("0.01")


@pytest.mark.parametrize("rate", ["0", "1"])
def test_accepts_the_rates_a_rate_accepts(rate: str) -> None:
    assert tier(rate=rate).rate == Rate(D(rate))


@pytest.mark.parametrize(
    ("lower", "upper", "maximum", "message"),
    [
        pytest.param("-1", "50000", "2350", "lower must not be negative", id="lower-negative"),
        pytest.param(
            "-0.01", "50000", "2350", "lower must not be negative", id="lower-slightly-negative"
        ),
        pytest.param("50000", "50000", "2350", "lower must be below upper", id="lower-at-upper"),
        pytest.param("60000", "50000", "2350", "lower must be below upper", id="lower-above"),
        pytest.param("3000", "-1", "2350", "lower must be below upper", id="upper-negative"),
        pytest.param("3000", "50000", "-1", "maximum must not be negative", id="max-negative"),
        pytest.param("3000", "50000", "-0.01", "maximum must not be negative", id="max-below-0"),
        pytest.param("Infinity", "50000", "2350", "lower must be finite", id="lower-infinite"),
        pytest.param("NaN", "50000", "2350", "lower must be finite", id="lower-nan"),
        pytest.param("3000", "Infinity", "2350", "upper must be finite", id="upper-infinite"),
        pytest.param("3000", "NaN", "2350", "upper must be finite", id="upper-nan"),
        pytest.param("3000", "50000", "Infinity", "maximum must be finite", id="max-infinite"),
        pytest.param("3000", "50000", "NaN", "maximum must be finite", id="max-nan"),
    ],
)
def test_rejects_invalid_tiers(lower: str, upper: str, maximum: str, message: str) -> None:
    with pytest.raises(InvalidContributionTierError, match=message):
        tier(lower=lower, upper=upper, maximum=maximum)


@pytest.mark.parametrize("field", ["lower", "upper", "maximum"])
@pytest.mark.parametrize("value", [1000, 0.5, "1000"])
def test_rejects_non_decimal_figures(field: str, value: object) -> None:
    figures: dict[str, object] = {"lower": D("3000"), "upper": D("50000"), "maximum": D("2350")}
    figures[field] = value

    with pytest.raises(TypeError, match=f"{field} must be a Decimal"):
        ContributionTier(rate=Rate(D("0.05")), **figures)  # type: ignore[arg-type]


@pytest.mark.parametrize("rate", [D("0.05"), "0.05", 0.05])
def test_rejects_a_rate_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate must be a Rate"):
        ContributionTier(
            rate=rate,  # type: ignore[arg-type]
            lower=D("3000"),
            upper=D("50000"),
            maximum=D("2350"),
        )


def test_contribution_tier_kind() -> None:
    assert CONTRIBUTION_TIER == ParameterKind("contribution_tier", ContributionTier)
    assert CONTRIBUTION_TIER.name == "contribution_tier"
    assert CONTRIBUTION_TIER.value_type is ContributionTier


def test_invalid_contribution_tier_is_a_domain_error() -> None:
    assert issubclass(InvalidContributionTierError, DomainError)
