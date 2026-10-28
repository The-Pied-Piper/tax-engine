"""CA-ON 2025 end to end: return EQ, Example 2 of Form T2222 (Northern Residents Deductions).

Return EQ is `returns/2025_return_eq.yaml`: 292 days lived in a prescribed intermediate zone
(Vanrena, Alberta), the basic and the additional
residency amount of $5.50 a day each, with no trips, and a chosen $100,000 of other
income. The tests check the form's figure of $3,212.00.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    NET_INCOME,
    NORTHERN_RESIDENTS_DEDUCTIONS,
    RESIDENCY_AMOUNT,
    RESIDENCY_DEDUCTION,
    RESIDENCY_NET_INCOME_LIMIT,
    TAXABLE_INCOME,
    ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT,
    ZONE_B_BASIC_RESIDENCY_AMOUNT,
    ZONE_B_RESIDENCY_AMOUNT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_eq() -> Worksheet:
    """The worksheet of the return EQ: other income of $100,000 and the zone days of the example."""
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="100000",
        zone_b_days_lived=292,
        zone_b_additional_residency_days=292,
    )


def test_b_for_292_days_gives_the_basic_and_the_additional_amount_of_1606_each() -> None:
    # "You can claim $5.50 for each day that you lived in Vanrena (292 days) and an additional
    # residency amount of $5.50 per day": 292 x 5.50 = 1,606.00 each, 3,212.00 together.
    worksheet = return_eq()

    assert worksheet.get(ZONE_B_BASIC_RESIDENCY_AMOUNT).value == D("1606.00")
    assert worksheet.get(ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT).value == D("1606.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AMOUNT).value == D("3212.00")


def test_the_northern_residents_deductions_are_3212_below_the_20_percent_limit() -> None:
    # Net income 100,000 makes line 12 20,000.00, above the residency amount, so the residency
    # deduction, the northern residents deductions (line 25500) and the line 25700 deduction
    # are all 3,212.00, and taxable income is 100,000 - 3,212.00 = 96,788.00.
    worksheet = return_eq()

    assert worksheet.get(NET_INCOME).value == D("100000.00")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("3212.00")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("20000.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("3212.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("3212.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("96788.00")
