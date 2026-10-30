"""CA-ON 2025 end to end: return hk."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_INCOME,
    BUSINESS_LAND_ADDITIONS,
    BUSINESS_LAND_DISPOSITIONS,
    BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    GROSS_BUSINESS_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return HK's T2125 statement, as Guide T4002's chapter 3 example (D'Arcy): the building's
# capital cost is entered in the Area A additions column (the guide's Area C column 3), the land
# on Area F. The gross sales of 6483.33 are a chosen figure, so that the rent of 4900 and the
# claim of 1583.33 (the full maximum of Class 1) leave a net business income of 0.00; the land is
# 15833.33 on line 9923 and 0 on line 9924 (Guide T4002: "$15,833.33 ($15,000 + $833.33) on line
# 9923 of Area F as the capital cost of the land").
BUSINESS_HK: dict[str, str] = {
    "gross_sales": "6483.33",
    "rent": "4900",
    "land_additions": "15833.33",
}

# Area A, the one row, as in Return CE and Return EC: Class 1 (4%) with no UCC at the start of the
# year, an addition of 79166.67 (the building's capital cost), no proceeds, no immediate expensing,
# claimed at 1583.33 (the maximum: 39583.33 x 4%, the half-year rule applying), with no property
# left in the class, the half-year rule flag 0 and no personal part.
CLASS_1_ROW = ("1", "0", "79166.67", "0", "0", "0", "1583.33", 0, "0", "0", "0", 0, "0")


def run_hk(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return HK's inputs, as in `returns/2025_return_hk.yaml`: a single filer whose only income is
    the net business income of one business with one T2125 statement, for a full fiscal period
    (0 days entered), with the land of the purchase on Area F."""
    statement: dict[str, Any] = {
        "business": BUSINESS_HK,
        "business_cca_classes_rows": (CLASS_1_ROW,),
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


def test_return_hks_land_additions_are_15833_33_on_line_9923_and_0_on_line_9924() -> None:
    # Area F "Line 9923: Total cost of all land additions in the year" is the entered figure of
    # 15833.33; "Line 9924: Total proceeds from all land dispositions in the year" is 0 for
    # D'Arcy. Nothing earlier on the form computes either line, so both are carried through.
    statement = run_hk()["ca/t2125"][0]

    assert statement.get(BUSINESS_LAND_ADDITIONS).value == D("15833.33")
    assert statement.get(BUSINESS_LAND_DISPOSITIONS).value == D("0")


def test_a_land_disposition_of_20000_is_carried_through_and_changes_no_income_line() -> None:
    # Area F line 9924 entered as 20000.00 with no land additions: both lines are carried through
    # unchanged, and neither feeds the net business income, which stays 0.00 with T1 line 13500.
    result = run_hk(
        {"business": {**BUSINESS_HK, "land_additions": "0", "land_dispositions": "20000"}}
    )
    statement = result["ca/t2125"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(BUSINESS_LAND_DISPOSITIONS).value == D("20000")
    assert statement.get(BUSINESS_LAND_ADDITIONS).value == D("0")
    assert statement.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("0.00")
    assert worksheet.get(BUSINESS_INCOME).value == D("0.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0.00")


def test_return_hks_building_claim_is_the_maximum_1583_33_leaving_ucc_77583_34() -> None:
    # Guide T4002, chapter 3 example: column 7 is 79166.67 (no UCC at the start of the year); the
    # half-year rule gives column 18 39583.34 and column 19 39583.33, so the maximum is
    # 39583.33 x 4% = 1583.33, which is claimed (line 9936) because D'Arcy "wants to deduct as much
    # CCA as he can". Column 22 is 79166.67 - 1583.33 = 77583.34.
    statement = run_hk()["ca/t2125"][0]

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("1583.33")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("1583.33")
    (record,) = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert record[CCA_CLASS_NUMBER] == D("1")
    assert record[CCA_UCC_AT_END] == D("77583.34")


def test_return_hks_net_business_income_is_zero_on_t1_line_13500_with_gross_6483_33() -> None:
    # Line 8299 (gross business income, T1 line 13499) is the chosen 6483.33; total expenses are
    # 4900 + 1583.33 = 6483.33, so line 9369 and line 9946 are 0.00, which is T1 line 13500, and
    # with no other income in the return, the total income is 0.00.
    result = run_hk()
    statement = result["ca/t2125"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("0.00")
    assert worksheet.get(GROSS_BUSINESS_INCOME).value == D("6483.33")
    assert worksheet.get(BUSINESS_INCOME).value == D("0.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0.00")
