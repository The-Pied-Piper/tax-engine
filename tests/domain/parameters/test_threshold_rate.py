"""Unit tests for ThresholdRate: the `threshold_rate` kind's values.

A threshold and a rate: a form line that passes an amount through when it is at or below the
`threshold`, and otherwise divides another figure by the `rate`. Like `Rate`, the value object
checks itself: a non-finite or negative threshold is an `InvalidThresholdRateError`, and so is a
rate of 0, because the rate is a divisor.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_engine.domain.errors import DomainError, InvalidRateError, InvalidThresholdRateError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate

D = Decimal
RATE = Rate(D("0.0505"))


def test_holds_its_threshold_and_rate() -> None:
    limit = ThresholdRate(rate=RATE, threshold=D("52886"))

    assert limit.threshold == D("52886")
    assert limit.rate == RATE


def test_holds_these_fields_in_order() -> None:
    assert [field.name for field in fields(ThresholdRate)] == ["rate", "threshold"]


def test_equal_figures_are_equal_limits() -> None:
    assert ThresholdRate(RATE, D("52886")) == ThresholdRate(Rate(D("0.05050")), D("52886.00"))


def test_different_figures_are_different_limits() -> None:
    assert ThresholdRate(RATE, D("52886")) != ThresholdRate(RATE, D("57375"))
    assert ThresholdRate(RATE, D("52886")) != ThresholdRate(Rate(D("0.145")), D("52886"))


def test_keeps_the_figures_exactly_as_given() -> None:
    limit = ThresholdRate(RATE, D("52886.50"))

    assert str(limit.threshold) == "52886.50"  # no rounding, no normalising


def test_is_frozen() -> None:
    limit = ThresholdRate(RATE, D("52886"))

    with pytest.raises(FrozenInstanceError):
        cast(Any, limit).threshold = D("1")
    with pytest.raises(FrozenInstanceError):
        cast(Any, limit).rate = Rate(D("0.5"))


def test_is_hashable() -> None:
    assert hash(ThresholdRate(RATE, D("52886"))) == hash(ThresholdRate(RATE, D("52886")))


@pytest.mark.parametrize("threshold", ["0", "-0", "1", "52886", "52886.50"])
def test_accepts_thresholds_from_zero_up(threshold: str) -> None:
    assert ThresholdRate(RATE, D(threshold)).threshold == D(threshold)


@pytest.mark.parametrize("rate", ["0.0001", "0.0505", "0.145", "1"])
def test_accepts_rates_above_zero_up_to_one(rate: str) -> None:
    assert ThresholdRate(Rate(D(rate)), D("52886")).rate == Rate(D(rate))


@pytest.mark.parametrize(
    ("threshold", "message"),
    [
        (D("-1"), "threshold must not be negative"),
        (D("-0.01"), "threshold must not be negative"),
        (D("Infinity"), "threshold must be finite"),
        (D("-Infinity"), "threshold must be finite"),
        (D("NaN"), "threshold must be finite"),
        (D("sNaN"), "threshold must be finite"),
    ],
)
def test_rejects_an_invalid_threshold(threshold: Decimal, message: str) -> None:
    with pytest.raises(InvalidThresholdRateError, match=message):
        ThresholdRate(RATE, threshold)


@pytest.mark.parametrize("rate", ["0", "-0", "0.00"])
def test_rejects_a_rate_of_zero_because_it_is_a_divisor(rate: str) -> None:
    with pytest.raises(InvalidThresholdRateError, match="rate must not be zero"):
        ThresholdRate(Rate(D(rate)), D("52886"))


def test_a_rate_of_zero_is_a_threshold_rate_error_not_a_rate_error() -> None:
    with pytest.raises(InvalidThresholdRateError) as raised:
        ThresholdRate(Rate(D("0")), D("52886"))

    assert not isinstance(raised.value, InvalidRateError)


@pytest.mark.parametrize("threshold", [52886, 0.5, "52886", None])
def test_rejects_a_non_decimal_threshold(threshold: object) -> None:
    with pytest.raises(TypeError, match="threshold must be a Decimal"):
        ThresholdRate(RATE, threshold)  # type: ignore[arg-type]


@pytest.mark.parametrize("rate", [D("0.0505"), 0.0505, "0.0505", None])
def test_rejects_a_rate_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate must be a Rate"):
        ThresholdRate(rate, D("52886"))  # type: ignore[arg-type]


def test_threshold_rate_kind() -> None:
    assert THRESHOLD_RATE == ParameterKind("threshold_rate", ThresholdRate)
    assert THRESHOLD_RATE.name == "threshold_rate"
    assert THRESHOLD_RATE.value_type is ThresholdRate


def test_invalid_threshold_rate_is_a_domain_error() -> None:
    assert issubclass(InvalidThresholdRateError, DomainError)
