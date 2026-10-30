"""Unit tests for RateTable: a form's table of rates by bands of a figure, the `rate_table` kind.

A rate table is the form's table copied row for row: each `RateTableRow` holds the figure it is
`more_than`, the figure it is `not_more_than` (absent, `None`, on the last row only) and its
`rate`, a `Rate`; the table also holds `rate_at_zero`, the rate a form gives a figure of exactly
zero. Like `SurchargeTiers`, the value objects only hold and check the table: at least one row,
the first row more than 0, `more_than` strictly increasing, each `not_more_than` above its own
`more_than`, no gap between a row's `not_more_than` and the next row's `more_than` (an overlap,
as a form's typo can print, is kept as printed), and an upper bound on every row but the last.
A figure of zero takes no row and `rate_at_zero`; above zero it falls in the last row whose
`more_than` it exceeds. Values are made up.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_engine.domain.errors import DomainError, InvalidRateTableError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rate_table import RATE_TABLE, RateTable, RateTableRow

D = Decimal


def row(more_than: str, not_more_than: str | None, rate: str) -> RateTableRow:
    upper = None if not_more_than is None else D(not_more_than)
    return RateTableRow(more_than=D(more_than), not_more_than=upper, rate=Rate(D(rate)))


def first() -> RateTableRow:
    return row("0", "1000", "0.30")


def middle() -> RateTableRow:
    return row("1000", "2500", "0.20")


def last() -> RateTableRow:
    return row("2500", None, "0")


def table(*rows: RateTableRow, rate_at_zero: str = "0.30") -> RateTable:
    return RateTable(rate_at_zero=Rate(D(rate_at_zero)), rows=rows or (first(), middle(), last()))


# --- one row ----------------------------------------------------------------------------------


def test_a_row_holds_its_bounds_and_rate() -> None:
    held = row("1000.50", "2500.25", "0.125")

    assert held.more_than == D("1000.50")
    assert held.not_more_than == D("2500.25")
    assert held.rate == Rate(D("0.125"))


def test_a_row_holds_its_more_than_not_more_than_and_rate_only_in_that_order() -> None:
    assert [field.name for field in fields(RateTableRow)] == ["more_than", "not_more_than", "rate"]


def test_a_row_is_built_positionally_in_field_order() -> None:
    assert RateTableRow(D(1000), D(2500), Rate(D("0.20"))) == middle()


def test_a_row_may_have_no_upper_bound() -> None:
    assert last().not_more_than is None


def test_a_row_keeps_its_bounds_exact() -> None:
    held = row("1000.50", "2500.00", "0.20")

    assert (str(held.more_than), str(held.not_more_than)) == ("1000.50", "2500.00")


def test_equal_rows_are_equal() -> None:
    assert row("1000", "2500", "0.2") == row("1000.00", "2500.0", "0.20")
    assert row("1000", "2500", "0.2") != row("1000", "2500", "0.3")
    assert row("1000", "2500", "0.2") != row("1000", None, "0.2")


def test_a_row_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, middle()).rate = Rate(D("0.5"))


def test_a_row_is_hashable() -> None:
    assert hash(middle()) == hash(middle())


@pytest.mark.parametrize("value", [1000, 0.5, "1000"])
def test_rejects_a_more_than_that_is_not_a_decimal(value: object) -> None:
    with pytest.raises(TypeError, match="more_than must be a Decimal"):
        RateTableRow(value, D(2500), Rate(D("0.2")))  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [2500, 0.5, "2500"])
def test_rejects_a_not_more_than_that_is_not_a_decimal(value: object) -> None:
    with pytest.raises(TypeError, match="not_more_than must be a Decimal"):
        RateTableRow(D(1000), value, Rate(D("0.2")))  # type: ignore[arg-type]


@pytest.mark.parametrize("rate", [D("0.2"), 0.2, "0.2"])
def test_rejects_a_rate_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate must be a Rate"):
        RateTableRow(D(1000), D(2500), rate)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("more_than", "not_more_than", "message"),
    [
        pytest.param("Infinity", "2500", "more_than must be finite", id="more-than-inf"),
        pytest.param("NaN", "2500", "more_than must be finite", id="more-than-nan"),
        pytest.param("1000", "Infinity", "not_more_than must be finite", id="upper-inf"),
        pytest.param("1000", "NaN", "not_more_than must be finite", id="upper-nan"),
    ],
)
def test_rejects_bounds_that_are_not_finite(
    more_than: str, not_more_than: str, message: str
) -> None:
    with pytest.raises(InvalidRateTableError, match=message):
        table(first(), row(more_than, not_more_than, "0.2"), last())


@pytest.mark.parametrize(
    "not_more_than",
    [pytest.param("1000", id="equal"), pytest.param("999.99", id="below")],
)
def test_rejects_a_row_whose_upper_bound_is_not_above_its_more_than(not_more_than: str) -> None:
    with pytest.raises(InvalidRateTableError, match="not_more_than must be above its more_than"):
        table(first(), row("1000", not_more_than, "0.2"), row("1000.01", None, "0"))


# --- the table --------------------------------------------------------------------------------


def test_holds_its_rate_at_zero_and_its_rows_in_order() -> None:
    held = table()

    assert held.rate_at_zero == Rate(D("0.30"))
    assert held.rows == (first(), middle(), last())


def test_holds_its_rate_at_zero_and_rows_only_in_that_order() -> None:
    assert [field.name for field in fields(RateTable)] == ["rate_at_zero", "rows"]


def test_is_built_positionally_in_field_order() -> None:
    assert RateTable(Rate(D("0.30")), (first(), middle(), last())) == table()


def test_a_single_unbounded_row_is_enough() -> None:
    only = row("0", None, "0.1")

    assert table(only).rows == (only,)


def test_the_rate_at_zero_need_not_be_the_first_rows_rate() -> None:
    assert table(rate_at_zero="0.5").rate_at_zero == Rate(D("0.5"))


def test_rates_need_not_fall() -> None:
    rising = (row("0", "1000", "0.1"), row("1000", None, "0.2"))

    assert table(*rising).rows == rising


def test_keeps_an_overlap_as_printed() -> None:
    # A form's typo: the middle row ends at 2600 while the next row starts at 2500. The table is
    # copied as printed; the capability picks the later row in the overlap.
    overlapping = (first(), row("1000", "2600", "0.20"), row("2500", None, "0"))

    assert table(*overlapping).rows == overlapping


def test_equal_tables_are_equal() -> None:
    assert table() == table(
        row("0", "1000.00", "0.3"), row("1000.0", "2500", "0.2"), row("2500", None, "0.00")
    )
    assert table() != table(rate_at_zero="0.31")
    assert table() != table(first(), row("1000", None, "0.2"))


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, table()).rows = (last(),)


def test_is_hashable() -> None:
    assert hash(table()) == hash(table())


def test_rejects_no_rows() -> None:
    with pytest.raises(InvalidRateTableError, match="at least one row"):
        RateTable(Rate(D("0.3")), ())


@pytest.mark.parametrize(
    "more_than", [pytest.param("100", id="above"), pytest.param("-1", id="below")]
)
def test_rejects_a_first_row_that_is_not_more_than_zero(more_than: str) -> None:
    with pytest.raises(InvalidRateTableError, match="first row must be more than 0"):
        table(row(more_than, "1000", "0.3"), middle(), last())


@pytest.mark.parametrize(
    "rows",
    [
        pytest.param(
            lambda: (first(), row("0", "2500", "0.2"), last()),
            id="equal",
        ),
        pytest.param(
            lambda: (row("0", "3000", "0.3"), row("2500", "4000", "0.2"), row("1000", None, "0")),
            id="descending",
        ),
    ],
)
def test_rejects_more_than_figures_that_are_not_strictly_increasing(rows: Any) -> None:
    with pytest.raises(InvalidRateTableError, match="strictly increasing"):
        table(*rows())


def test_rejects_a_gap_between_rows() -> None:
    with pytest.raises(InvalidRateTableError, match="gap between 1000 and 1200"):
        table(first(), row("1200", "2500", "0.2"), last())


def test_rejects_an_upper_bound_missing_before_the_last_row() -> None:
    with pytest.raises(InvalidRateTableError, match="every row but the last must have"):
        table(first(), row("1000", None, "0.2"), last())


def test_rejects_an_upper_bound_on_the_last_row() -> None:
    with pytest.raises(InvalidRateTableError, match="last row must have no not_more_than"):
        table(first(), middle(), row("2500", "5000", "0"))


@pytest.mark.parametrize("rows", [[first(), last()], "rows", None])
def test_rejects_rows_that_are_not_a_tuple(rows: object) -> None:
    with pytest.raises(TypeError, match="rows must be a tuple"):
        RateTable(Rate(D("0.3")), rows)  # type: ignore[arg-type]


@pytest.mark.parametrize("rate", [D("0.3"), 0.3, "0.3"])
def test_rejects_a_rate_at_zero_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate_at_zero must be a Rate"):
        RateTable(rate, (first(), middle(), last()))  # type: ignore[arg-type]


# --- choosing a row ---------------------------------------------------------------------------


def test_a_figure_of_zero_takes_no_row_and_the_rate_at_zero() -> None:
    held = table(rate_at_zero="0.40")

    assert held.row_for(D("0")) is None
    assert held.row_for(D("-0.00")) is None
    assert held.rate_for(None) == Rate(D("0.40"))


@pytest.mark.parametrize(
    ("figure", "chosen"),
    [("0.01", first()), ("1000", first()), ("1000.01", middle()), ("2500", middle())],
)
def test_a_figure_falls_in_the_row_whose_bounds_hold_it(figure: str, chosen: RateTableRow) -> None:
    held = table()

    assert held.row_for(D(figure)) == chosen
    assert held.rate_for(chosen) == chosen.rate


def test_a_figure_above_the_last_lower_bound_falls_in_the_last_row() -> None:
    assert table().row_for(D("2500.01")) == last()
    assert table().row_for(D("1E+9")) == last()


def test_in_an_overlap_the_later_row_applies() -> None:
    overlapping = table(row("0", "1200", "0.30"), row("1000", "2500", "0.20"), last())

    assert overlapping.row_for(D("1000")) == row("0", "1200", "0.30")
    assert overlapping.row_for(D("1000.01")) == row("1000", "2500", "0.20")
    assert overlapping.row_for(D("1200")) == row("1000", "2500", "0.20")


# --- the kind ---------------------------------------------------------------------------------


def test_rate_table_kind() -> None:
    assert RATE_TABLE == ParameterKind("rate_table", RateTable)
    assert RATE_TABLE.name == "rate_table"
    assert RATE_TABLE.value_type is RateTable


def test_invalid_rate_table_is_a_domain_error() -> None:
    assert issubclass(InvalidRateTableError, DomainError)
