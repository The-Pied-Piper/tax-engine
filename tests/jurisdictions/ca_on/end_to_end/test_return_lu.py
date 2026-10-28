"""CA-ON 2025 end to end: return lu (a passenger vehicle, interest above the Guide T4044 limit)."""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    T777_INTEREST_AVAILABLE,
    T777_INTEREST_LIMIT,
    T777_LINE_3,
    T777_LINE_17,
    T777_LINE_26,
    T777_VEHICLE_TOTAL_EXPENSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D
from tests.jurisdictions.ca_on.end_to_end.test_return_hi import t777_form

CAR = {
    "employment_kilometres": "10000",
    "total_kilometres": "10000",
    "vehicle_fuel": "2000",
    "vehicle_interest": "5000",
    "passenger_vehicle": "1",
    "interest_days": "100",
}


def lu_form(**car: str) -> Worksheet:
    """Form T777 with Return LU's car; `car` replaces any of its figures."""
    return t777_form(**{**CAR, **car})


def test_a_passenger_vehicle_s_interest_of_5000_is_limited_to_10_a_day_for_100_days() -> None:
    # Line A 5,000; line B 10 x 100 = 1,000; the lesser, 1,000, is line 26.
    form = lu_form()
    assert form.get(T777_INTEREST_LIMIT).value == D("1000.00")
    assert form.get(T777_INTEREST_AVAILABLE).value == D("1000.00")
    assert form.get(T777_LINE_26).value == D("1000.00")
    # Line 29 is 2,000 + 1,000; all kilometres are for employment, so lines 3 and 17 are 3,000.
    assert form.get(T777_VEHICLE_TOTAL_EXPENSES).value == D("3000.00")
    assert form.get(T777_LINE_3).value == D("3000.00")
    assert form.get(T777_LINE_17).value == D("3000.00")


def test_interest_below_line_b_is_line_26_whole() -> None:
    # Line A 800 is less than line B 1,000.
    assert lu_form(vehicle_interest="800").get(T777_LINE_26).value == D("800.00")


def test_a_vehicle_that_is_not_a_passenger_vehicle_has_no_limit() -> None:
    form = lu_form(passenger_vehicle="0", interest_days="0")
    assert form.get(T777_LINE_26).value == D("5000.00")
    assert form.get(T777_VEHICLE_TOTAL_EXPENSES).value == D("7000.00")


def test_a_passenger_vehicle_with_no_interest_days_has_no_interest() -> None:
    assert lu_form(interest_days="0").get(T777_LINE_26).value == D("0.00")


def test_a_passenger_vehicle_answer_above_1_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="t777_passenger_vehicle"):
        lu_form(passenger_vehicle="2")


def test_interest_days_above_the_365_of_a_year_are_used_as_typed() -> None:
    # Line B prints "$10 multiplied by the number of days for which interest was paid" with no
    # maximum: 366 days is line B 3,660, the lesser of line A 5,000 and 3,660 is line 26.
    form = lu_form(interest_days="366")
    assert form.get(T777_INTEREST_LIMIT).value == D("3660.00")
    assert form.get(T777_LINE_26).value == D("3660.00")


def test_400_interest_days_give_line_b_of_4000() -> None:
    form = lu_form(interest_days="400")
    assert form.get(T777_INTEREST_LIMIT).value == D("4000.00")
    assert form.get(T777_LINE_26).value == D("4000.00")


def test_a_full_year_of_365_days_gives_line_b_of_3650() -> None:
    form = lu_form(vehicle_interest="4000", interest_days="365")
    assert form.get(T777_INTEREST_LIMIT).value == D("3650.00")
    assert form.get(T777_LINE_26).value == D("3650.00")


def test_interest_equal_to_line_b_is_line_26() -> None:
    assert lu_form(vehicle_interest="1000").get(T777_LINE_26).value == D("1000.00")


def test_days_above_365_are_not_refused_when_the_vehicle_is_not_a_passenger_vehicle() -> None:
    form = lu_form(passenger_vehicle="0", interest_days="366")
    assert form.get(T777_LINE_26).value == D("5000.00")
