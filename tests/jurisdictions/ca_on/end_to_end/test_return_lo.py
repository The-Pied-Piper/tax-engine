"""CA-ON 2025 end to end: return lo, Guide T4044's "Eligible leasing costs" chart for T777 line 27.

The worked return `returns/2025_return_lo.yaml` (the Guide's car lease example, leased in 2025) is
checked by `test_worked_returns.py`. This module computes the chart's other cases on its own: a
list price above line 5, a lease entered into in an earlier year (the footnoted amounts), a
payment deducted before 2025 (line 2), and the refusals.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    T777_LEASE_LINE_5,
    T777_LEASE_LINE_6,
    T777_LEASE_LINE_7,
    T777_LEASE_LINE_8,
    T777_VEHICLE_LEASING_COSTS,
    T777_VEHICLE_TOTAL_EXPENSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D
from tests.jurisdictions.ca_on.end_to_end.test_return_hi import t777_form


def lease(
    year: str, price: str, charges: str, days: str, before: str = "0", passenger: str = "1"
) -> dict[str, str]:
    """The chart's lines 1 to 4, the year of the lease, whether it is a passenger vehicle (not
    given: yes) and the HST rate of 13%."""
    return {
        "lease_charges": charges,
        "lease_payments_before": before,
        "lease_days": days,
        "lease_list_price": price,
        "lease_year": year,
        "passenger_vehicle": passenger,
        "vehicle_sales_tax_rate": "13",
    }


def test_a_list_price_above_line_5_is_line_6_at_85_percent_and_line_8_is_the_lower() -> None:
    # Line 6 is 60,000 x 85% = 51,000.00; line 7 is 1,243.00 x 365 / 30 = 15,123.17 and line 8 is
    # 42,940.00 x 8,000 / 51,000.00 = 6,735.69, the lower: line 27 and so line 29.
    form = t777_form(**lease("2025", "60000", "8000", "365"))

    assert form.get(T777_LEASE_LINE_5).value == D("50517.78")
    assert form.get(T777_LEASE_LINE_6).value == D("51000.00")
    assert form.get(T777_LEASE_LINE_7).value == D("15123.17")
    assert form.get(T777_LEASE_LINE_8).value == D("6735.69")
    assert form.get(T777_VEHICLE_LEASING_COSTS).value == D("6735.69")
    assert form.get(T777_VEHICLE_TOTAL_EXPENSES).value == D("6735.69")


def test_a_lease_entered_into_in_2023_uses_the_footnoted_amounts_and_line_2_lowers_line_7() -> None:
    # 2023: 42,353 + 5,505.89 = 47,858.89 (line 5), x 85% = 40,680.06 (line 6); (950 + 123.50) x 400
    # / 30 = 14,313.33 less 14,000 = 313.33 (line 7); (36,000 + 4,680.00) x 5,000 / 40,680.06 =
    # 4,999.99 (line 8): the lower is line 7.
    form = t777_form(**lease("2023", "10000", "5000", "400", before="14000"))

    assert form.get(T777_LEASE_LINE_5).value == D("47858.89")
    assert form.get(T777_LEASE_LINE_6).value == D("40680.06")
    assert form.get(T777_LEASE_LINE_7).value == D("313.33")
    assert form.get(T777_LEASE_LINE_8).value == D("4999.99")
    assert form.get(T777_VEHICLE_LEASING_COSTS).value == D("313.33")


def test_a_lease_entered_into_in_2021_or_before_uses_the_oldest_amounts() -> None:
    # 35,294 + 4,588.22 = 39,882.22, x 85% = 33,899.89; (800 + 104) x 365 / 30 = 10,998.67;
    # (30,000 + 3,900.00) x 8,000 / 33,899.89 = 8,000.03 (rounded half-up).
    form = t777_form(**lease("2021", "20000", "8000", "365"))

    assert form.get(T777_LEASE_LINE_6).value == D("33899.89")
    assert form.get(T777_LEASE_LINE_7).value == D("10998.67")
    assert form.get(T777_VEHICLE_LEASING_COSTS).value == D("8000.03")


def test_a_line_2_above_the_divided_by_30_figure_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        t777_form(**lease("2023", "10000", "5000", "400", before="20000"))


def test_a_lease_entered_into_after_2025_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="2026"):
        t777_form(**lease("2026", "10000", "5000", "400"))


def test_a_vehicle_that_is_not_a_passenger_vehicle_deducts_the_lease_charges_paid() -> None:
    # The chart is for a passenger vehicle: a truck with 24,000 of lease charges, 365 days and a
    # 70,000 list price would be limited to 15,123.17 by the chart, but there is no limit for it.
    form = t777_form(**lease("2025", "70000", "24000", "365", passenger="0"))

    assert form.get(T777_VEHICLE_LEASING_COSTS).value == D("24000")
    assert form.get(T777_VEHICLE_TOTAL_EXPENSES).value == D("24000")


def test_a_passenger_vehicle_answer_above_1_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        t777_form(**lease("2025", "70000", "24000", "365", passenger="2"))
