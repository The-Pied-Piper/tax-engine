"""CA-ON 2025 end to end: return hm (Guide T4002's Vivienne, two passenger vehicles)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_CLASSES_CHECKED,
    BUSINESS_CLOSING_UCC,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    GROSS_BUSINESS_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import BusinessCcaRow, D, run

# Return HM's T2125 statement, as Guide T4002's Class 10.1 (30%) example (Vivienne, page 81):
# the
# sales tax rate is 13, the GST of 5% and the PST of 8% of the example. Gross sales are a chosen
# $11,187.00, the CCA claimed in full, so the net business income is $0.00 (as in Return HK).
BUSINESS_HM: dict[str, str] = {
    "gross_sales": "11187.00",
    "vehicle_sales_tax_rate": "13",
}

# Vehicle 1: Class 10.1, bought in 2025 at $39,000 before tax (its cost, the proceeds adjustment's
# actual cost), entered in column 3 at the capped $42,940 ($38,000 + 13%). Half-year rule: 42940 x
# 50% x 30% = 6441.00, claimed in full. Vehicle 2: Class 10, $28,000 before tax, $31,640 with tax in
# column 3; 31640 x 50% x 30% = 4746.00, claimed in full. The vehicle fields are the year of the
# vehicle (2025 for Class 10.1, 0 for Class 10), its cost and its government assistance.
VEHICLE_10_1: BusinessCcaRow = (
    "10.1",
    "0",
    "42940.00",
    "0",
    "0",
    "0",
    "6441.00",
    0,
    "0",
    "0",
    "0",
    0,
    "0",
    2025,
    "39000",
    "0",
    (),
)
VEHICLE_10: BusinessCcaRow = (
    "10",
    "0",
    "31640.00",
    "0",
    "0",
    "0",
    "4746.00",
    0,
    "0",
    "0",
    "0",
    0,
    "0",
    0,
    "0",
    "0",
    (),
)
# The Class 10.1 vehicle entered at Vivienne's cost with tax, $44,070, which the check refuses.
UNCAPPED_VEHICLE_10_1: BusinessCcaRow = (
    "10.1",
    "0",
    "44070.00",
    "0",
    "0",
    "0",
    "6441.00",
    0,
    "0",
    "0",
    "0",
    0,
    "0",
    2025,
    "39000",
    "0",
    (),
)


def run_hm(
    *rows: BusinessCcaRow,
    changes: Mapping[str, Any] | None = None,
    **overrides: Any,
) -> dict[str, tuple[Worksheet, ...]]:
    """Return HM's inputs, as in `returns/2025_return_hm.yaml`: a single filer whose only income is
    the net business income of one business with the two vehicles (Area A, `rows`, by default
    Vivienne's two), for a full fiscal period (0 days entered)."""
    statement: dict[str, Any] = {
        "business": BUSINESS_HM,
        "business_cca_classes_rows": rows or (VEHICLE_10_1, VEHICLE_10),
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def test_return_hms_two_vehicles_are_checked_and_passed_on_as_entered() -> None:
    # Vivienne's Class 10.1 vehicle at the capped $42,940 is accepted (at the limit, not over it),
    # and her Class 10 vehicle at $31,640 is not limited: both rows pass on unchanged.
    statement = run_hm()["ca/t2125"][0]

    checked = statement.get(BUSINESS_CCA_CLASSES_CHECKED).value
    assert [record[CCA_CLASS_NUMBER] for record in checked.records] == [D("10.1"), D("10")]
    assert [record[CCA_ADDITIONS] for record in checked.records] == [
        D("42940.00"),
        D("31640.00"),
    ]


def test_return_hms_class_10_1_vehicle_at_44070_is_refused_naming_the_row() -> None:
    # Vivienne's $44,070 (the vehicle with its GST and PST) in column 3 of Class 10.1 is refused:
    # the form asks for the capped amount, $42,940.
    with pytest.raises(InvalidRecordError) as error:
        run_hm(UNCAPPED_VEHICLE_10_1, VEHICLE_10)

    assert str(error.value).endswith(
        "item 1: additions (44070.00) are more than the Class 10.1 limit with tax (42940.00) "
        "at a sales tax rate of 13%, which is GST plus PST, or HST"
    )


def test_return_hms_half_year_claims_are_11187_00_leaving_ucc_of_36499_and_26894() -> None:
    # The half-year rule: Class 10.1 42940.00 x 50% x 30% = 6441.00 and Class 10 31640.00 x 50% x
    # 30% = 4746.00, claimed in full; the total claim is 11187.00,
    # and the UCC at the end of the year
    # is 42940.00 - 6441.00 = 36499.00 and 31640.00 - 4746.00 = 26894.00.
    statement = run_hm()["ca/t2125"][0]

    assert statement.get(BUSINESS_CCA_CLAIM).value == D("11187.00")
    ucc_at_end = {
        record[CCA_CLASS_NUMBER]: record[CCA_UCC_AT_END]
        for record in statement.get(BUSINESS_CLOSING_UCC).value.records
    }
    assert ucc_at_end == {D("10.1"): D("36499.00"), D("10"): D("26894.00")}


def test_return_hms_net_business_income_is_zero_on_t1_line_13500_with_gross_11187_00() -> None:
    # Gross sales of 11187.00 (line 8299, T1 line 13499) less the 11187.00 of CCA, so line 9946 and
    # T1 line 13500 are 0.00 and, with no other income, the total income is 0.00.
    result = run_hm()
    statement = result["ca/t2125"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("0.00")
    assert worksheet.get(GROSS_BUSINESS_INCOME).value == D("11187.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0.00")
