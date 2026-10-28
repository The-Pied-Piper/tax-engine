"""Unit tests for Credit: a credit amount, the `credit` kind's values.

The rate that turns the amount into tax relief is its own parameter (`rate` kind), so a Credit
holds the amount only: one fact in one home.
"""

from __future__ import annotations

from dataclasses import fields
from decimal import Decimal

import pytest

from tax_calculator.domain.errors import DomainError, InvalidCreditError
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.kind import ParameterKind

D = Decimal


def test_holds_its_amount() -> None:
    assert Credit(amount=D("1000")).amount == D("1000")


def test_holds_the_amount_only() -> None:
    assert [field.name for field in fields(Credit)] == ["amount"]


def test_equal_amounts_are_equal_credits() -> None:
    assert Credit(D("1000")) == Credit(D("1000.0"))


@pytest.mark.parametrize(
    ("amount", "message"),
    [
        (D("-1"), "amount must not be negative"),
        (D("Infinity"), "must be finite"),
        (D("NaN"), "must be finite"),
    ],
)
def test_rejects_invalid_amounts(amount: Decimal, message: str) -> None:
    with pytest.raises(InvalidCreditError, match=message):
        Credit(amount=amount)


def test_accepts_a_zero_amount() -> None:
    assert Credit(amount=D(0)).amount == 0


@pytest.mark.parametrize("amount", [1000, 0.5, "1000"])
def test_rejects_non_decimal_amounts(amount: object) -> None:
    with pytest.raises(TypeError, match="must be a Decimal"):
        Credit(amount=amount)  # type: ignore[arg-type]


def test_credit_kind() -> None:
    assert CREDIT == ParameterKind("credit", Credit)


def test_invalid_credit_is_a_domain_error() -> None:
    assert issubclass(InvalidCreditError, DomainError)
