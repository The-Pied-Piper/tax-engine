"""CA-ON 2025 end to end: return ly (a leased passenger vehicle with refundable deposits of $800,
so there is no imputed interest and the Guide T4044 leasing chart is worked)."""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_calculator.jurisdictions.ca.catalog import T777_VEHICLE_LEASING_COSTS
from tests.jurisdictions.ca_on.end_to_end.support import D
from tests.jurisdictions.ca_on.end_to_end.test_return_hi import t777_form

CAR = {
    "lease_charges": "5500",
    "lease_payments_before": "0",
    "lease_days": "335",
    "lease_list_price": "28000",
    "lease_year": "2025",
    "passenger_vehicle": "1",
    "vehicle_sales_tax_rate": "13",
    "lease_deposits_made": "1",
    "lease_deposits_refundable": "1",
    "lease_deposits_total": "800",
}


def ly_costs(**car: str) -> object:
    """Form T777 line 27 with Return LY's car; `car` replaces any of its figures."""
    return t777_form(**{**CAR, **car}).get(T777_VEHICLE_LEASING_COSTS).value


def test_deposits_of_800_are_not_more_than_1000_so_the_chart_gives_5499_99() -> None:
    # The third condition fails, so no imputed interest: line 8 is 42,940.00 x 5,500 / 42,940.11.
    assert ly_costs() == D("5499.99")


def test_deposits_of_exactly_1000_are_not_more_than_1000_so_the_chart_is_worked() -> None:
    assert ly_costs(lease_deposits_total="1000") == D("5499.99")


def test_deposits_of_1000_01_made_and_all_refundable_mean_imputed_interest() -> None:
    # All three conditions apply, so the chart cannot be used (contact the CRA).
    with pytest.raises(InputOutOfRangeError, match=r"t777_lease_chart_conflict 1 is refused"):
        ly_costs(lease_deposits_total="1000.01")


def test_a_deposit_that_is_not_refundable_leaves_no_imputed_interest() -> None:
    # "All deposits are refundable" fails: the answer is no, whatever the total.
    assert ly_costs(lease_deposits_refundable="0", lease_deposits_total="5000") == D("5499.99")


def test_no_deposits_made_leaves_no_imputed_interest_whatever_the_total() -> None:
    # Each condition is read as typed; the guide prints no link between them.
    assert ly_costs(lease_deposits_made="0", lease_deposits_total="5000") == D("5499.99")


def test_a_repayment_owing_means_the_chart_cannot_be_used() -> None:
    with pytest.raises(InputOutOfRangeError, match=r"t777_lease_chart_conflict 1 is refused"):
        ly_costs(lease_repayment_owing="1")


def test_a_vehicle_that_is_not_a_passenger_vehicle_is_not_refused() -> None:
    # The chart is for a passenger vehicle: line 27 is the lease charges paid (line 1).
    form = ly_costs(passenger_vehicle="0", lease_repayment_owing="1", lease_deposits_total="5000")
    assert form == D("5500.00")


@pytest.mark.parametrize("name", ["lease_repayment_owing", "lease_deposits_made"])
def test_a_yes_or_no_answer_above_1_is_refused(name: str) -> None:
    with pytest.raises(InputAboveBoundError, match=f"t777_{name}"):
        ly_costs(**{name: "2"})


def test_deposits_refundable_above_1_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="t777_lease_deposits_refundable"):
        ly_costs(lease_deposits_refundable="2")
