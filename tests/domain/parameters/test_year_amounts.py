"""Unit tests for YearAmounts: the `year_amounts` kind's values.

A table of named figures by year, newest row first. A row's `from_year` N means "year N or later";
only the last row may leave it out (None), meaning "any earlier year". `row_for(year)` gives the
first row that applies, or None when the form prints nothing for that year. The value objects
check themselves: an invalid table is an `InvalidYearAmountsError`.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_calculator.domain.errors import DomainError, InvalidYearAmountsError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts, YearAmountsRow

D = Decimal


def row(from_year: int | None, **amounts: str) -> YearAmountsRow:
    return YearAmountsRow(from_year, {name: D(value) for name, value in amounts.items()})


# The Chart B figures: $350 from 2024, $300 from 2001, nothing printed for 2000 or earlier.
INTEREST = YearAmounts((row(2024, interest_limit="350"), row(2001, interest_limit="300")))

# The Chart C figures: five sets, the last open-ended ("before 2022").
LEASE = YearAmounts(
    (
        row(2025, list_price="44706", charge="1100", cost="38000"),
        row(2024, list_price="43529", charge="1050", cost="37000"),
        row(2023, list_price="42353", charge="950", cost="36000"),
        row(2022, list_price="40000", charge="900", cost="34000"),
        row(None, list_price="35294", charge="800", cost="30000"),
    )
)


def test_a_row_holds_its_year_and_amounts() -> None:
    entry = row(2024, interest_limit="350")

    assert entry.from_year == 2024
    assert entry.amounts == {"interest_limit": D("350")}


def test_a_row_holds_these_fields_in_order() -> None:
    assert [field.name for field in fields(YearAmountsRow)] == ["from_year", "amounts"]


def test_a_table_holds_these_fields() -> None:
    assert [field.name for field in fields(YearAmounts)] == ["rows"]


def test_a_table_holds_its_rows_in_order() -> None:
    assert [entry.from_year for entry in LEASE.rows] == [2025, 2024, 2023, 2022, None]


def test_equal_tables_are_equal() -> None:
    assert INTEREST == YearAmounts(
        (row(2024, interest_limit="350.00"), row(2001, interest_limit="300"))
    )


def test_different_tables_are_different() -> None:
    assert INTEREST != YearAmounts(
        (row(2024, interest_limit="350"), row(2000, interest_limit="300"))
    )
    assert INTEREST != YearAmounts(
        (row(2024, interest_limit="350"), row(2001, interest_limit="301"))
    )


def test_keeps_the_figures_exactly_as_given() -> None:
    entry = row(2024, interest_limit="350.50")

    assert str(entry.amount("interest_limit")) == "350.50"


def test_is_frozen() -> None:
    entry = row(2024, interest_limit="350")

    with pytest.raises(FrozenInstanceError):
        cast(Any, entry).from_year = 2023
    with pytest.raises(FrozenInstanceError):
        cast(Any, INTEREST).rows = ()


def test_a_single_open_ended_row_is_a_table() -> None:
    table = YearAmounts((row(None, interest_limit="300"),))

    assert table.row_for(1990) == row(None, interest_limit="300")
    assert table.row_for(2025) == row(None, interest_limit="300")


def test_a_single_dated_row_is_a_table() -> None:
    table = YearAmounts((row(2024, interest_limit="350"),))

    assert table.row_for(2024) == row(2024, interest_limit="350")
    assert table.row_for(2023) is None


@pytest.mark.parametrize("value", ["0", "-0", "0.00", "350", "350.50"])
def test_accepts_amounts_from_zero_up(value: str) -> None:
    assert row(2024, interest_limit=value).amount("interest_limit") == D(value)


# row_for: the interest table, boundary by boundary.


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2026, "350"),
        (2025, "350"),
        (2024, "350"),
        (2023, "300"),
        (2022, "300"),
        (2002, "300"),
        (2001, "300"),
        (2000, None),
        (1999, None),
        (0, None),
        (-1, None),
    ],
)
def test_row_for_the_interest_table(year: int, expected: str | None) -> None:
    found = INTEREST.row_for(year)

    if expected is None:
        assert found is None
    else:
        assert found is not None
        assert found.amount("interest_limit") == D(expected)


# row_for: the lease table, with an open-ended last row.


@pytest.mark.parametrize(
    ("year", "list_price", "charge", "cost"),
    [
        (2030, "44706", "1100", "38000"),
        (2025, "44706", "1100", "38000"),
        (2024, "43529", "1050", "37000"),
        (2023, "42353", "950", "36000"),
        (2022, "40000", "900", "34000"),
        (2021, "35294", "800", "30000"),
        (2001, "35294", "800", "30000"),
        (2000, "35294", "800", "30000"),
        (0, "35294", "800", "30000"),
        (-5, "35294", "800", "30000"),
    ],
)
def test_row_for_the_lease_table(year: int, list_price: str, charge: str, cost: str) -> None:
    found = LEASE.row_for(year)

    assert found is not None
    assert found.amount("list_price") == D(list_price)
    assert found.amount("charge") == D(charge)
    assert found.amount("cost") == D(cost)


def test_row_for_gives_the_first_row_that_applies() -> None:
    assert INTEREST.row_for(2024) is INTEREST.rows[0]
    assert INTEREST.row_for(2023) is INTEREST.rows[1]
    assert LEASE.row_for(2021) is LEASE.rows[4]


def test_row_for_gives_none_when_no_row_applies() -> None:
    assert INTEREST.row_for(2000) is None


def test_a_row_names_its_amount() -> None:
    assert LEASE.rows[0].amount("charge") == D("1100")


@pytest.mark.parametrize("name", ["", "Charge", "charges", "interest_limit"])
def test_an_unknown_amount_name_is_refused(name: str) -> None:
    with pytest.raises(InvalidYearAmountsError, match="no amount named"):
        LEASE.rows[0].amount(name)


# Validation.


def test_rejects_a_table_with_no_rows() -> None:
    with pytest.raises(InvalidYearAmountsError, match="at least one row"):
        YearAmounts(())


@pytest.mark.parametrize(
    "years",
    [
        pytest.param([2024, 2024], id="equal"),
        pytest.param([2023, 2024], id="ascending"),
        pytest.param([2025, 2023, 2024], id="out-of-order-in-the-middle"),
        pytest.param([2025, 2024, 2024, 2023], id="repeat-in-the-middle"),
    ],
)
def test_rejects_years_that_are_not_strictly_descending(years: list[int]) -> None:
    rows = tuple(row(year, interest_limit="1") for year in years)

    with pytest.raises(InvalidYearAmountsError, match="strictly descending"):
        YearAmounts(rows)


def test_rejects_an_open_ended_row_that_is_not_last() -> None:
    rows = (row(None, interest_limit="1"), row(2024, interest_limit="2"))

    with pytest.raises(InvalidYearAmountsError, match="only the last row"):
        YearAmounts(rows)


def test_rejects_two_open_ended_rows() -> None:
    rows = (row(None, interest_limit="1"), row(None, interest_limit="2"))

    with pytest.raises(InvalidYearAmountsError, match="only the last row"):
        YearAmounts(rows)


def test_rejects_an_open_ended_row_in_the_middle() -> None:
    rows = (
        row(2025, interest_limit="1"),
        row(None, interest_limit="2"),
        row(2020, interest_limit="3"),
    )

    with pytest.raises(InvalidYearAmountsError, match="only the last row"):
        YearAmounts(rows)


def test_rejects_rows_with_different_amount_names() -> None:
    rows = (row(2024, interest_limit="350"), row(2001, interest_cap="300"))

    with pytest.raises(InvalidYearAmountsError, match="same amount names"):
        YearAmounts(rows)


def test_rejects_a_row_with_an_extra_amount_name() -> None:
    rows = (row(2024, a="1", b="2"), row(2001, a="1"))

    with pytest.raises(InvalidYearAmountsError, match="same amount names"):
        YearAmounts(rows)


def test_rejects_a_row_with_no_amounts() -> None:
    with pytest.raises(InvalidYearAmountsError, match="at least one amount"):
        YearAmountsRow(2024, {})


def test_rejects_an_empty_amount_name() -> None:
    with pytest.raises(InvalidYearAmountsError, match="amount name"):
        YearAmountsRow(2024, {"": D("1")})


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (D("-1"), "must not be negative"),
        (D("-0.01"), "must not be negative"),
        (D("Infinity"), "must be finite"),
        (D("-Infinity"), "must be finite"),
        (D("NaN"), "must be finite"),
        (D("sNaN"), "must be finite"),
    ],
)
def test_rejects_an_invalid_amount(value: Decimal, message: str) -> None:
    with pytest.raises(InvalidYearAmountsError, match=message):
        YearAmountsRow(2024, {"interest_limit": value})


def test_an_invalid_amount_names_the_amount() -> None:
    with pytest.raises(InvalidYearAmountsError, match="interest_limit"):
        YearAmountsRow(2024, {"interest_limit": D("-1")})


@pytest.mark.parametrize("value", [350, 350.0, "350", None])
def test_rejects_a_non_decimal_amount(value: object) -> None:
    with pytest.raises(TypeError, match="Decimal"):
        YearAmountsRow(2024, {"interest_limit": value})  # type: ignore[dict-item]


@pytest.mark.parametrize("from_year", [2024.0, "2024", True])
def test_rejects_a_from_year_that_is_not_an_int(from_year: object) -> None:
    with pytest.raises(TypeError, match="from_year"):
        YearAmountsRow(from_year, {"interest_limit": D("1")})  # type: ignore[arg-type]


def test_rejects_rows_that_are_not_rows() -> None:
    with pytest.raises(TypeError, match="row"):
        YearAmounts((cast(Any, {"from_year": 2024}),))


def test_row_for_rejects_a_year_that_is_not_an_int() -> None:
    with pytest.raises(TypeError, match="year"):
        INTEREST.row_for("2024")  # type: ignore[arg-type]


def test_year_amounts_kind() -> None:
    assert YEAR_AMOUNTS == ParameterKind("year_amounts", YearAmounts)
    assert YEAR_AMOUNTS.name == "year_amounts"
    assert YEAR_AMOUNTS.value_type is YearAmounts


def test_invalid_year_amounts_is_a_domain_error() -> None:
    assert issubclass(InvalidYearAmountsError, DomainError)
