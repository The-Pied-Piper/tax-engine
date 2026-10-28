"""Unit tests for Fraction: a fraction of whole numbers, the `fraction` kind's values.

A form line such as "multiplied by two-thirds" multiplies by a fraction that is not a finite
decimal, so it cannot be a `Rate`: the fraction is carried as its `numerator`, a whole number of
zero or more (a form can print a factor of 0), and its `denominator`, a positive whole number, and
the one division is left to the capability that applies it. Like `Rate`, the value object checks
itself: a negative numerator, or a denominator that is zero or negative, is an
`InvalidFractionError`, and a part that is not an `int` (a bool, a Decimal, a float, a string) is
a `TypeError`. The parts are kept as given, never reduced. Values are made up.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_calculator.domain.errors import DomainError, InvalidFractionError
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.kind import ParameterKind

D = Decimal


def test_holds_its_numerator_and_denominator() -> None:
    held = Fraction(numerator=2, denominator=3)

    assert held.numerator == 2
    assert held.denominator == 3


def test_holds_its_fields_in_order() -> None:
    assert [field.name for field in fields(Fraction)] == ["numerator", "denominator"]


def test_is_built_positionally_in_field_order() -> None:
    assert Fraction(2, 3) == Fraction(numerator=2, denominator=3)


def test_equal_parts_are_equal_fractions() -> None:
    assert Fraction(2, 3) == Fraction(2, 3)


def test_fractions_differ_by_either_part() -> None:
    assert Fraction(2, 3) != Fraction(1, 3)
    assert Fraction(2, 3) != Fraction(2, 5)


def test_keeps_its_parts_as_given() -> None:
    # Not reduced: the fraction is the one the form prints.
    held = Fraction(4, 6)

    assert (held.numerator, held.denominator) == (4, 6)


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, Fraction(2, 3)).numerator = 1


def test_is_hashable() -> None:
    assert hash(Fraction(2, 3)) == hash(Fraction(2, 3))


@pytest.mark.parametrize(
    ("numerator", "denominator"), [(1, 1), (2, 3), (1, 3), (3, 2), (1, 1000000)]
)
def test_accepts_positive_whole_parts(numerator: int, denominator: int) -> None:
    held = Fraction(numerator, denominator)

    assert (held.numerator, held.denominator) == (numerator, denominator)


@pytest.mark.parametrize(("numerator", "denominator"), [(0, 1), (0, 3), (0, 1000000)])
def test_accepts_a_numerator_of_zero(numerator: int, denominator: int) -> None:
    # A form can print a factor of 0; the denominator is still positive.
    held = Fraction(numerator, denominator)

    assert (held.numerator, held.denominator) == (numerator, denominator)


def test_a_zero_fraction_keeps_its_denominator_as_given() -> None:
    # Not reduced: 0/3 is not 0/1.
    assert Fraction(0, 3) != Fraction(0, 1)


@pytest.mark.parametrize(
    ("numerator", "denominator", "message"),
    [
        pytest.param(-2, 3, "fraction numerator must not be negative, got -2", id="numerator-neg"),
        pytest.param(-1, 1, "fraction numerator must not be negative, got -1", id="minus-one"),
        pytest.param(2, 0, "fraction denominator must be positive, got 0", id="denominator-zero"),
        pytest.param(2, -3, "fraction denominator must be positive, got -3", id="denominator-neg"),
        pytest.param(0, 0, "fraction denominator must be positive, got 0", id="both-zero"),
        pytest.param(0, -3, "fraction denominator must be positive, got -3", id="zero-over-neg"),
    ],
)
def test_rejects_a_negative_numerator_or_a_denominator_that_is_not_positive(
    numerator: int, denominator: int, message: str
) -> None:
    with pytest.raises(InvalidFractionError, match=message):
        Fraction(numerator, denominator)


@pytest.mark.parametrize("part", ["numerator", "denominator"])
@pytest.mark.parametrize(
    ("value", "type_name"),
    [
        (True, "bool"),
        (D("2"), "Decimal"),
        (D("2.5"), "Decimal"),
        (2.0, "float"),
        ("2", "str"),
    ],
)
def test_rejects_parts_that_are_not_ints(part: str, value: object, type_name: str) -> None:
    parts: dict[str, object] = {"numerator": 2, "denominator": 3}
    parts[part] = value

    with pytest.raises(TypeError, match=f"fraction {part} must be an int, got {type_name}"):
        Fraction(**parts)  # type: ignore[arg-type]


def test_fraction_kind() -> None:
    assert FRACTION == ParameterKind("fraction", Fraction)
    assert FRACTION.name == "fraction"
    assert FRACTION.value_type is Fraction


def test_invalid_fraction_is_a_domain_error() -> None:
    assert issubclass(InvalidFractionError, DomainError)
