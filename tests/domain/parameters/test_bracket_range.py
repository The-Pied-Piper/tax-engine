"""Unit tests for the range a BracketSchedule covers (made-up values).

The first bracket's `from` is where the range starts ("more than"): a first bracket above 0 must
carry a printed `tax_at_start`, and 0 itself is then not covered. An optional `up_to` is the
inclusive last amount covered; it must lie above the last bracket's `from`. `covers(amount)` says
whether the schedule answers for an amount, and `column_for` / `tax_on` refuse an amount it does
not cover with AmountOutsideBracketRangeError. A schedule with no `up_to` and a first bracket at 0
behaves as it always did.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.errors import (
    AmountOutsideBracketRangeError,
    DomainError,
    InvalidBracketScheduleError,
)
from tax_engine.domain.parameters.brackets import Bracket, BracketSchedule

D = Decimal

# The table "more than 100": 30% over 100 on top of a printed 25.00, 40% over 200 on top of 55.00.
UPPER = BracketSchedule(
    (
        Bracket(D(100), D("0.30"), D("25.00")),
        Bracket(D(200), D("0.40"), D("55.00")),
    )
)
# The table "0 to 100": 10% to 50, 20% above it.
LOWER = BracketSchedule((Bracket(D(0), D("0.10")), Bracket(D(50), D("0.20"))), up_to=D(100))
# As today: from 0, no upper end.
OPEN = BracketSchedule((Bracket(D(0), D("0.10")), Bracket(D(100), D("0.20"))))


def test_a_schedule_has_no_upper_end_by_default() -> None:
    assert OPEN.up_to is None
    assert UPPER.up_to is None


def test_a_schedule_holds_the_up_to_it_is_given() -> None:
    assert LOWER.up_to == D(100)


def test_schedules_differing_only_in_up_to_differ() -> None:
    assert LOWER != BracketSchedule(LOWER.brackets)
    assert LOWER == BracketSchedule(LOWER.brackets, up_to=D(100))


# --- covers ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "covered"),
    [
        ("0", True),
        ("0.01", True),
        ("1000000", True),
        ("-0.01", False),
    ],
)
def test_a_schedule_from_zero_with_no_up_to_covers_every_amount_from_zero(
    amount: str, covered: bool
) -> None:
    assert OPEN.covers(D(amount)) is covered


@pytest.mark.parametrize(
    ("amount", "covered"),
    [
        ("0", True),  # a first bracket at 0 covers 0 itself
        ("99.99", True),
        ("100", True),  # up_to is inclusive
        ("100.01", False),
        ("-1", False),
    ],
)
def test_up_to_is_the_inclusive_last_amount_covered(amount: str, covered: bool) -> None:
    assert LOWER.covers(D(amount)) is covered


@pytest.mark.parametrize(
    ("amount", "covered"),
    [
        ("0", False),
        ("99.99", False),
        ("100", False),  # "more than 100": the start itself is not covered
        ("100.01", True),
        ("250", True),
        ("1000000", True),
    ],
)
def test_a_first_bracket_above_zero_covers_only_amounts_more_than_its_from(
    amount: str, covered: bool
) -> None:
    assert UPPER.covers(D(amount)) is covered


def test_a_range_may_have_both_a_start_above_zero_and_an_up_to() -> None:
    both = BracketSchedule(UPPER.brackets, up_to=D(300))

    assert [both.covers(D(a)) for a in ("100", "100.01", "300", "300.01")] == [
        False,
        True,
        True,
        False,
    ]


def test_two_adjacent_tables_cover_a_boundary_amount_once() -> None:
    assert LOWER.covers(D(100)) and not UPPER.covers(D(100))
    assert UPPER.covers(D("100.01")) and not LOWER.covers(D("100.01"))


# --- column_for and tax_on ---------------------------------------------------------------------


def test_the_first_bracket_of_a_range_above_zero_is_the_column_just_over_its_from() -> None:
    column = UPPER.column_for(D("100.01"))

    assert (column.lower, column.rate, column.excess) == (D(100), D("0.30"), D("0.01"))
    assert column.tax_at_start == D("25.00")
    assert column.tax == D("25.0030")


def test_the_later_bracket_of_a_range_above_zero_uses_its_printed_tax_at_start() -> None:
    column = UPPER.column_for(D(250))

    assert (column.lower, column.rate, column.excess) == (D(200), D("0.40"), D(50))
    assert column.tax_at_start == D("55.00")
    assert UPPER.tax_on(D(250)) == D("75.00")


def test_an_amount_at_a_threshold_inside_a_range_falls_in_the_lower_column() -> None:
    assert UPPER.column_for(D(200)).lower == D(100)


def test_an_amount_at_up_to_falls_in_the_last_column() -> None:
    column = LOWER.column_for(D(100))

    assert (column.lower, column.rate, column.excess) == (D(50), D("0.20"), D(50))
    assert column.tax_at_start == D("5.0")
    assert LOWER.tax_on(D(100)) == D("15.00")


def test_a_schedule_from_zero_with_no_up_to_answers_as_it_always_did() -> None:
    assert OPEN.column_for(D(0)).lower == D(0)
    assert OPEN.tax_on(D(1000)) == D("190.0")


@pytest.mark.parametrize("amount", ["0", "50", "100"])
def test_column_for_an_amount_not_more_than_the_start_is_outside_the_range(amount: str) -> None:
    with pytest.raises(AmountOutsideBracketRangeError):
        UPPER.column_for(D(amount))


@pytest.mark.parametrize("amount", ["100.01", "70000"])
def test_column_for_an_amount_over_up_to_is_outside_the_range(amount: str) -> None:
    with pytest.raises(AmountOutsideBracketRangeError):
        LOWER.column_for(D(amount))


def test_tax_on_an_amount_outside_the_range_is_refused_too() -> None:
    with pytest.raises(AmountOutsideBracketRangeError):
        LOWER.tax_on(D(101))
    with pytest.raises(AmountOutsideBracketRangeError):
        UPPER.tax_on(D(100))


def test_a_negative_amount_in_a_schedule_from_zero_with_no_up_to_is_still_a_value_error() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        OPEN.column_for(D(-1))


def test_the_outside_range_error_is_a_domain_error() -> None:
    assert issubclass(AmountOutsideBracketRangeError, DomainError)


# --- invalid schedules -------------------------------------------------------------------------


def test_a_first_bracket_above_zero_without_a_printed_tax_at_start_is_refused() -> None:
    with pytest.raises(InvalidBracketScheduleError, match="tax_at_start"):
        BracketSchedule((Bracket(D(100), D("0.30")), Bracket(D(200), D("0.40"), D("55.00"))))


def test_a_first_bracket_above_zero_with_a_printed_tax_at_start_is_accepted() -> None:
    assert BracketSchedule((Bracket(D(100), D("0.30"), D("25.00")),)).brackets[0].lower == D(100)


@pytest.mark.parametrize("up_to", ["100", "99.99", "0"])
def test_up_to_must_be_above_the_last_brackets_from(up_to: str) -> None:
    with pytest.raises(InvalidBracketScheduleError, match="up_to"):
        BracketSchedule((Bracket(D(0), D("0.10")), Bracket(D(100), D("0.20"))), up_to=D(up_to))


def test_up_to_must_be_above_the_only_brackets_from() -> None:
    with pytest.raises(InvalidBracketScheduleError, match="up_to"):
        BracketSchedule((Bracket(D(0), D("0.10")),), up_to=D(0))
    with pytest.raises(InvalidBracketScheduleError, match="up_to"):
        BracketSchedule((Bracket(D(100), D("0.10"), D(5)),), up_to=D(100))


def test_up_to_just_above_the_last_brackets_from_is_accepted() -> None:
    schedule = BracketSchedule((Bracket(D(0), D("0.10")),), up_to=D("0.01"))

    assert schedule.covers(D("0.01"))
    assert not schedule.covers(D("0.02"))
