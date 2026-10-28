"""Unit tests for Amount: a plain money value from data, the `amount` kind's values.

An amount has no further meaning: unlike a `Credit`, nothing multiplies it by a rate; it is a cap
or another fixed figure a form states. Like `Rate`, the value object checks itself: a non-finite
or negative amount is an `InvalidAmountError`.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_calculator.domain.errors import DomainError, InvalidAmountError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.kind import ParameterKind

D = Decimal


def test_holds_its_value() -> None:
    assert Amount(value=D("1234.56")).value == D("1234.56")


def test_holds_the_value_only() -> None:
    assert [field.name for field in fields(Amount)] == ["value"]


def test_equal_values_are_equal_amounts() -> None:
    assert Amount(D("1000")) == Amount(D("1000.00"))


def test_keeps_the_value_exactly_as_given() -> None:
    value = Amount(D("1000.50")).value

    assert str(value) == "1000.50"  # no rounding, no normalising


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, Amount(D("1000"))).value = D("2000")


@pytest.mark.parametrize("value", ["0", "-0", "1", "1234.56", "999999999.99"])
def test_accepts_amounts_from_zero_up(value: str) -> None:
    assert Amount(D(value)).value == D(value)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (D("-1"), "amount must not be negative"),
        (D("-0.01"), "amount must not be negative"),
        (D("Infinity"), "amount must be finite"),
        (D("-Infinity"), "amount must be finite"),
        (D("NaN"), "amount must be finite"),
        (D("sNaN"), "amount must be finite"),
    ],
)
def test_rejects_invalid_amounts(value: Decimal, message: str) -> None:
    with pytest.raises(InvalidAmountError, match=message):
        Amount(value)


@pytest.mark.parametrize("value", [1000, 0.5, "1000"])
def test_rejects_non_decimal_values(value: object) -> None:
    with pytest.raises(TypeError, match="must be a Decimal"):
        Amount(value)  # type: ignore[arg-type]


def test_amount_kind() -> None:
    assert AMOUNT == ParameterKind("amount", Amount)
    assert AMOUNT.name == "amount"
    assert AMOUNT.value_type is Amount


def test_invalid_amount_is_a_domain_error() -> None:
    assert issubclass(InvalidAmountError, DomainError)
