"""Unit tests for Factor: a multiplier from data, the `factor` kind's values.

A factor is the number a form multiplies an amount by ("multiplied by 2"). Unlike a `Rate` it has
no upper bound of 1: any finite value from zero up. Like `Amount`, the value object checks itself:
a non-finite or negative factor is an `InvalidFactorError`. Values are made up.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_calculator.domain.errors import DomainError, InvalidFactorError
from tax_calculator.domain.parameters.factor import FACTOR, Factor
from tax_calculator.domain.parameters.kind import ParameterKind

D = Decimal


def test_holds_its_value() -> None:
    assert Factor(value=D("2")).value == D("2")


def test_holds_the_value_only() -> None:
    assert [field.name for field in fields(Factor)] == ["value"]


def test_equal_values_are_equal_factors() -> None:
    assert Factor(D("2")) == Factor(D("2.00"))


def test_factors_differ_by_value() -> None:
    assert Factor(D("2")) != Factor(D("3"))


def test_keeps_the_value_exactly_as_given() -> None:
    value = Factor(D("2.50")).value

    assert str(value) == "2.50"  # no rounding, no normalising


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, Factor(D("2"))).value = D("3")


def test_is_hashable() -> None:
    assert hash(Factor(D("2"))) == hash(Factor(D("2")))


@pytest.mark.parametrize("value", ["0", "-0", "0.5", "1", "2", "2.5", "1000000"])
def test_accepts_factors_from_zero_up(value: str) -> None:
    assert Factor(D(value)).value == D(value)


def test_has_no_upper_bound_unlike_a_rate() -> None:
    # A rate stops at 1; the form's "multiplied by 2" needs more.
    assert Factor(D("2")).value > 1
    assert Factor(D("1E+6")).value == D("1000000")


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (D("-1"), "factor must not be negative"),
        (D("-0.01"), "factor must not be negative"),
        (D("Infinity"), "factor must be finite"),
        (D("-Infinity"), "factor must be finite"),
        (D("NaN"), "factor must be finite"),
        (D("sNaN"), "factor must be finite"),
    ],
)
def test_rejects_invalid_factors(value: Decimal, message: str) -> None:
    with pytest.raises(InvalidFactorError, match=message):
        Factor(value)


@pytest.mark.parametrize("value", [2, 0.5, "2"])
def test_rejects_non_decimal_values(value: object) -> None:
    with pytest.raises(TypeError, match="factor must be a Decimal"):
        Factor(value)  # type: ignore[arg-type]


def test_factor_kind() -> None:
    assert FACTOR == ParameterKind("factor", Factor)
    assert FACTOR.name == "factor"
    assert FACTOR.value_type is Factor


def test_invalid_factor_is_a_domain_error() -> None:
    assert issubclass(InvalidFactorError, DomainError)
