"""Unit tests for Rate: a validated rate from 0 to 1, the `rate` kind's values.

A rate has its own kind and datasets so that one rate is stated once, whichever capabilities use
it. Like `Credit`, the value object checks itself: a rate outside 0..1 is an `InvalidRateError`.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_engine.domain.errors import DomainError, InvalidRateError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate

D = Decimal


def test_holds_its_value() -> None:
    assert Rate(value=D("0.125")).value == D("0.125")


def test_holds_the_value_only() -> None:
    assert [field.name for field in fields(Rate)] == ["value"]


def test_equal_values_are_equal_rates() -> None:
    assert Rate(D("0.1")) == Rate(D("0.10"))


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, Rate(D("0.1"))).value = D("0.2")


@pytest.mark.parametrize("value", ["0", "1", "0.0505"])
def test_accepts_rates_from_zero_to_one_inclusive(value: str) -> None:
    assert Rate(D(value)).value == D(value)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (D("1.5"), "rate must be between 0 and 1"),
        (D("-0.1"), "rate must be between 0 and 1"),
        (D("Infinity"), "rate must be finite"),
        (D("NaN"), "rate must be finite"),
    ],
)
def test_rejects_invalid_rates(value: Decimal, message: str) -> None:
    with pytest.raises(InvalidRateError, match=message):
        Rate(value)


@pytest.mark.parametrize("value", [1, 0.5, "0.5"])
def test_rejects_non_decimal_values(value: object) -> None:
    with pytest.raises(TypeError, match="must be a Decimal"):
        Rate(value)  # type: ignore[arg-type]


def test_rate_kind() -> None:
    assert RATE == ParameterKind("rate", Rate)
    assert RATE.name == "rate"
    assert RATE.value_type is Rate


def test_invalid_rate_is_a_domain_error() -> None:
    assert issubclass(InvalidRateError, DomainError)
