"""Unit tests for AmountByCount: a printed table of amounts by count, the `amount_by_count` values.

A table holds rows, each a non-negative `int` count and the exact, finite, non-negative `Decimal`
amount the form prints against it, in the order given: `rows` is a tuple of `(count, amount)`
pairs. Like `Taper` and `SurchargeTiers`, the value object checks itself: an empty table, a count
listed twice, a count that is negative, an amount that is not finite or is negative is an
`InvalidAmountByCountError`; a count that is not an `int` (a `bool` included) or an amount that is
not a `Decimal` is a `TypeError`. Values are made up.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_calculator.domain.errors import DomainError, InvalidAmountByCountError
from tax_calculator.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_calculator.domain.parameters.kind import ParameterKind

D = Decimal


def table(*rows: tuple[int, str]) -> AmountByCount:
    """By default the made-up rows 1 to 4."""
    chosen = rows or ((1, "100"), (2, "200.50"), (3, "300"), (4, "400"))
    return AmountByCount(tuple((count, D(amount)) for count, amount in chosen))


def test_holds_its_rows() -> None:
    held = table()

    assert held.rows == ((1, D("100")), (2, D("200.50")), (3, D("300")), (4, D("400")))


def test_holds_its_rows_as_a_tuple_of_pairs() -> None:
    held = table()

    assert isinstance(held.rows, tuple)
    for count, amount in held.rows:
        assert type(count) is int
        assert type(amount) is Decimal


def test_holds_one_field() -> None:
    assert [field.name for field in fields(AmountByCount)] == ["rows"]


def test_is_built_positionally() -> None:
    assert AmountByCount(((1, D("100")),)) == table((1, "100"))


def test_keeps_the_order_of_its_rows() -> None:
    held = table((3, "300"), (1, "100"), (2, "200"))

    assert [count for count, _amount in held.rows] == [3, 1, 2]


def test_equal_values_are_equal_tables() -> None:
    assert table((1, "100"), (2, "200.50")) == table((1, "100.00"), (2, "2.0050E+2"))


def test_tables_differ_by_any_row() -> None:
    assert table() != table((1, "100"), (2, "200.50"), (3, "300"), (4, "401"))
    assert table() != table((1, "100"), (2, "200.50"), (3, "300"), (5, "400"))


def test_tables_differ_by_a_missing_row() -> None:
    assert table() != table((1, "100"), (2, "200.50"), (3, "300"))


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, table()).rows = ()


def test_is_hashable() -> None:
    assert hash(table()) == hash(table())


def test_keeps_its_figures_exactly_as_given() -> None:
    held = table((1, "100.50"), (2, "200.0"), (3, "0.000"))

    # No rounding, no normalising.
    assert [str(amount) for _count, amount in held.rows] == ["100.50", "200.0", "0.000"]


def test_accepts_a_single_row() -> None:
    assert table((7, "10")).rows == ((7, D("10")),)


def test_accepts_a_count_of_zero() -> None:
    assert table((0, "0"), (1, "100")).rows[0] == (0, D("0"))


def test_accepts_a_zero_amount() -> None:
    assert table((1, "0")).rows == ((1, D("0")),)


def test_accepts_counts_that_leave_gaps() -> None:
    assert [count for count, _amount in table((1, "1"), (5, "5"), (12, "12")).rows] == [1, 5, 12]


def test_accepts_a_very_large_count() -> None:
    assert table((10**30, "1")).rows == ((10**30, D("1")),)


def test_rejects_an_empty_table() -> None:
    with pytest.raises(InvalidAmountByCountError, match="must not be empty"):
        AmountByCount(())


@pytest.mark.parametrize(
    "rows",
    [
        pytest.param(((1, "100"), (1, "100")), id="same-amount"),
        pytest.param(((1, "100"), (2, "200"), (1, "300")), id="apart"),
    ],
)
def test_rejects_a_count_listed_twice(rows: tuple[tuple[int, str], ...]) -> None:
    with pytest.raises(InvalidAmountByCountError, match="duplicate count 1"):
        table(*rows)


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        pytest.param(((-1, "100"),), "count must not be negative", id="count-neg"),
        pytest.param(((1, "100"), (-5, "100")), "count must not be negative", id="count-neg-2nd"),
        pytest.param(((1, "-1"),), "amount must not be negative", id="amount-neg"),
        pytest.param(((1, "-0.01"),), "amount must not be negative", id="amount-slightly-neg"),
        pytest.param(((1, "Infinity"),), "amount must be finite", id="amount-inf"),
        pytest.param(((1, "-Infinity"),), "amount must be finite", id="amount-neg-inf"),
        pytest.param(((1, "NaN"),), "amount must be finite", id="amount-nan"),
    ],
)
def test_rejects_invalid_tables(rows: tuple[tuple[int, str], ...], message: str) -> None:
    with pytest.raises(InvalidAmountByCountError, match=message):
        table(*rows)


@pytest.mark.parametrize("count", [1.0, "1", None, True, False])
def test_rejects_a_count_that_is_not_an_int(count: object) -> None:
    with pytest.raises(TypeError, match="count must be an int"):
        AmountByCount(((count, D("100")),))  # type: ignore[arg-type]


@pytest.mark.parametrize("amount", [100, 100.5, "100", None])
def test_rejects_an_amount_that_is_not_a_decimal(amount: object) -> None:
    with pytest.raises(TypeError, match="amount must be a Decimal"):
        AmountByCount(((1, amount),))  # type: ignore[arg-type]


def test_amount_by_count_kind() -> None:
    assert AMOUNT_BY_COUNT == ParameterKind("amount_by_count", AmountByCount)
    assert AMOUNT_BY_COUNT.name == "amount_by_count"
    assert AMOUNT_BY_COUNT.value_type is AmountByCount


def test_invalid_amount_by_count_is_a_domain_error() -> None:
    assert issubclass(InvalidAmountByCountError, DomainError)


def test_a_negative_zero_amount_is_kept_as_a_plain_zero_with_its_scale() -> None:
    result = table((1, "-0.00"), (2, "5")).rows

    assert result[0][1].is_signed() is False
    assert str(result[0][1]) == "0.00"
    assert result[1][1] == D("5")
