"""Unit tests for ClaimReduction: the `claim_reduction` kind's values.

A claim reduction is what a form takes off an expense claim before it counts: the lesser of a
`ceiling` and a `rate` of a figure (here a person's net income), with an optional per-claim
`maximum` on what is left. Like `Rate`, the value object checks itself: a non-finite or negative
ceiling or maximum is an `InvalidClaimReductionError`.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_engine.domain.errors import DomainError, InvalidClaimReductionError
from tax_engine.domain.parameters.claim_reduction import CLAIM_REDUCTION, ClaimReduction
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate

D = Decimal
RATE = Rate(D("0.03"))


def test_holds_its_rate_ceiling_and_maximum() -> None:
    reduction = ClaimReduction(rate=RATE, ceiling=D("2834"), maximum=D("15551"))

    assert reduction.rate == RATE
    assert reduction.ceiling == D("2834")
    assert reduction.maximum == D("15551")


def test_holds_these_fields_in_order() -> None:
    assert [field.name for field in fields(ClaimReduction)] == ["rate", "ceiling", "maximum"]


def test_the_maximum_is_optional_and_defaults_to_none() -> None:
    reduction = ClaimReduction(RATE, D("2834"))

    assert reduction.maximum is None
    assert reduction == ClaimReduction(RATE, D("2834"), None)


def test_a_reduction_with_a_maximum_differs_from_one_without() -> None:
    assert ClaimReduction(RATE, D("2834"), D("15551")) != ClaimReduction(RATE, D("2834"))


def test_equal_figures_are_equal_reductions() -> None:
    assert ClaimReduction(RATE, D("2834")) == ClaimReduction(Rate(D("0.030")), D("2834.00"))


def test_keeps_the_figures_exactly_as_given() -> None:
    reduction = ClaimReduction(RATE, D("2834.50"), D("15551.00"))

    assert str(reduction.ceiling) == "2834.50"
    assert str(reduction.maximum) == "15551.00"  # no rounding, no normalising


def test_is_frozen() -> None:
    reduction = ClaimReduction(RATE, D("2834"))

    with pytest.raises(FrozenInstanceError):
        cast(Any, reduction).ceiling = D("1")
    with pytest.raises(FrozenInstanceError):
        cast(Any, reduction).maximum = D("1")


def test_is_hashable() -> None:
    assert hash(ClaimReduction(RATE, D("2834"), None)) == hash(ClaimReduction(RATE, D("2834")))


@pytest.mark.parametrize("ceiling", ["0", "-0", "1", "2834", "2834.50"])
def test_accepts_ceilings_from_zero_up(ceiling: str) -> None:
    assert ClaimReduction(RATE, D(ceiling)).ceiling == D(ceiling)


@pytest.mark.parametrize("maximum", ["0", "-0", "1", "15551", "15551.50"])
def test_accepts_maximums_from_zero_up(maximum: str) -> None:
    assert ClaimReduction(RATE, D("2834"), D(maximum)).maximum == D(maximum)


@pytest.mark.parametrize("rate", ["0", "1"])
def test_accepts_the_edge_rates(rate: str) -> None:
    assert ClaimReduction(Rate(D(rate)), D("2834")).rate == Rate(D(rate))


@pytest.mark.parametrize(
    ("ceiling", "message"),
    [
        (D("-1"), "ceiling must not be negative"),
        (D("-0.01"), "ceiling must not be negative"),
        (D("Infinity"), "ceiling must be finite"),
        (D("-Infinity"), "ceiling must be finite"),
        (D("NaN"), "ceiling must be finite"),
        (D("sNaN"), "ceiling must be finite"),
    ],
)
def test_rejects_an_invalid_ceiling(ceiling: Decimal, message: str) -> None:
    with pytest.raises(InvalidClaimReductionError, match=message):
        ClaimReduction(RATE, ceiling)


@pytest.mark.parametrize(
    ("maximum", "message"),
    [
        (D("-1"), "maximum must not be negative"),
        (D("-0.01"), "maximum must not be negative"),
        (D("Infinity"), "maximum must be finite"),
        (D("-Infinity"), "maximum must be finite"),
        (D("NaN"), "maximum must be finite"),
        (D("sNaN"), "maximum must be finite"),
    ],
)
def test_rejects_an_invalid_maximum(maximum: Decimal, message: str) -> None:
    with pytest.raises(InvalidClaimReductionError, match=message):
        ClaimReduction(RATE, D("2834"), maximum)


@pytest.mark.parametrize("ceiling", [2834, 0.5, "2834", None])
def test_rejects_a_non_decimal_ceiling(ceiling: object) -> None:
    with pytest.raises(TypeError, match="ceiling must be a Decimal"):
        ClaimReduction(RATE, ceiling)  # type: ignore[arg-type]


@pytest.mark.parametrize("maximum", [15551, 0.5, "15551"])
def test_rejects_a_non_decimal_maximum(maximum: object) -> None:
    with pytest.raises(TypeError, match="maximum must be a Decimal"):
        ClaimReduction(RATE, D("2834"), maximum)  # type: ignore[arg-type]


@pytest.mark.parametrize("rate", [D("0.03"), 0.03, "0.03", None])
def test_rejects_a_rate_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate must be a Rate"):
        ClaimReduction(rate, D("2834"))  # type: ignore[arg-type]


def test_claim_reduction_kind() -> None:
    assert CLAIM_REDUCTION == ParameterKind("claim_reduction", ClaimReduction)
    assert CLAIM_REDUCTION.name == "claim_reduction"
    assert CLAIM_REDUCTION.value_type is ClaimReduction


def test_invalid_claim_reduction_is_a_domain_error() -> None:
    assert issubclass(InvalidClaimReductionError, DomainError)
