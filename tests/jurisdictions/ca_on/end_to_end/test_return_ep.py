"""CA-ON 2025 end to end: return EP, Example 1 of Form T2222 (Northern Residents Deductions).

Return EP is `returns/2025_return_ep.yaml`: 292 days lived in a prescribed northern zone
(Yellowknife, Northwest Territories), the basic and the additional
residency amount of $11 a day each, with no trips, and a chosen $100,000 of other
income. The tests check the form's figure of $6,424.00.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    NET_INCOME,
    NORTHERN_RESIDENTS_DEDUCTIONS,
    RESIDENCY_AMOUNT,
    RESIDENCY_DEDUCTION,
    RESIDENCY_NET_INCOME_LIMIT,
    TAXABLE_INCOME,
    ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT,
    ZONE_A_BASIC_RESIDENCY_AMOUNT,
    ZONE_A_RESIDENCY_AMOUNT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ep() -> Worksheet:
    """The worksheet of the return EP: other income of $100,000 and the zone days of the example."""
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="100000",
        zone_a_days_lived=292,
        zone_a_additional_residency_days=292,
    )


def test_a_for_292_days_gives_the_basic_and_the_additional_amount_of_3212_each() -> None:
    # "You can claim $11 for each day that you lived in Yellowknife (292 days) and an additional
    # residency amount of $11 per day": 292 x 11 = 3,212.00 each, 6,424.00 together.
    worksheet = return_ep()

    assert worksheet.get(ZONE_A_BASIC_RESIDENCY_AMOUNT).value == D("3212.00")
    assert worksheet.get(ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT).value == D("3212.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AMOUNT).value == D("6424.00")


def test_the_northern_residents_deductions_are_6424_below_the_20_percent_limit() -> None:
    # Net income 100,000 makes line 12 20,000.00, above the residency amount, so the residency
    # deduction, the northern residents deductions (line 25500) and the line 25700 deduction
    # are all 6,424.00, and taxable income is 100,000 - 6,424.00 = 93,576.00.
    worksheet = return_ep()

    assert worksheet.get(NET_INCOME).value == D("100000.00")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("6424.00")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("20000.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("6424.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("6424.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("93576.00")
