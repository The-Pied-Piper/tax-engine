"""CA-ON 2025 end to end: Form ON-BEN Part B's residence rows, carried as entered and guarded.

Return AJ (`returns/2025_return_aj.yaml`) carries one row of 12 months. These tests give the table
other rows to a filer with no income: each row's months are at most the 12 months of the year, the
table has no row limit (the form says to use a separate sheet for more), rows are not added (a home
paid to several payees takes a row for each), and the long-term care tick is 0 or 1. The return
reads nothing of the form, so a row that passes the checks changes no return line.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca_on.catalog import (
    NET_REFUND,
    ON_BEN_RESIDENCE_AMOUNT,
    ON_BEN_RESIDENCE_LONG_TERM_CARE_CHECKED,
    ON_BEN_RESIDENCE_MONTHS_CHECKED,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, run


def filed(*rows: dict[str, Any]) -> Any:
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        cpp_months=12,
        qpp_months=12,
        applies_for_energy_and_property_tax_credit=1,
        on_ben_residence_rows=rows,
    )


def row(months: str, amount: str = "1000", long_term_care: int = 0) -> dict[str, Any]:
    return {"months": months, "amount": amount, "long_term_care": long_term_care}


def test_no_rows_is_filed() -> None:
    assert filed().get(NET_REFUND).value == filed(row("12")).get(NET_REFUND).value


def test_a_home_paid_to_three_payees_takes_three_rows_of_12_months() -> None:
    # Rent to a landlord, property tax to the municipality and reserve energy costs to a supplier
    # for the same home all year: a row for each payee, 12 months each.
    filed(row("12", "9600"), row("12", "2400"), row("12", "1800"))


def test_a_fifth_row_on_a_separate_sheet_is_accepted() -> None:
    # The form says "If you need more space, use a separate sheet of paper".
    filed(row("2"), row("2"), row("2"), row("2"), row("2"))


def test_12_months_and_fractions_of_a_month_in_a_row_are_accepted() -> None:
    filed(row("12"), row("6.5"))


def test_a_row_of_more_than_12_months_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=r"on_ben_residence_months 13 is above"):
        filed(row("13"))


def test_a_row_of_12_point_5_months_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        filed(row("5"), row("12.5"))


def test_a_long_term_care_tick_of_2_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        filed(row("12", long_term_care=2))


def test_each_row_exports_its_months_amount_and_checked_tick() -> None:
    # A long-term care home for 5 months ($77.50, ticked) and a rental for 12 months ($3, not).
    runs = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        cpp_months=12,
        qpp_months=12,
        on_ben_residence_rows=(row("5", "77.5", 1), row("12", "3")),
    )

    first, second = runs["ca-on/on_ben_residences"]
    assert first.get(ON_BEN_RESIDENCE_MONTHS_CHECKED).value == D("5")
    assert first.get(ON_BEN_RESIDENCE_AMOUNT).value == D("77.5")
    assert first.get(ON_BEN_RESIDENCE_LONG_TERM_CARE_CHECKED).value == 1
    assert second.get(ON_BEN_RESIDENCE_MONTHS_CHECKED).value == D("12")
    assert second.get(ON_BEN_RESIDENCE_AMOUNT).value == D("3")
    assert second.get(ON_BEN_RESIDENCE_LONG_TERM_CARE_CHECKED).value == 0
