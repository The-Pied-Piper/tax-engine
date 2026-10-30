"""CA-ON 2025 end to end: return GD, the focused flow-through share credit for a non-resident.

Return GD is `returns/2025_return_gd.yaml`: a simple Ontario filer who was not a resident of
Ontario on December 31, 2025, with two flow-through share slips of 8000 and 3500 (chosen figures).
Form T1221 says "You must be a resident of Ontario on the last day of the tax year to claim this
credit.", so the line 4 total of 11500 is not claimed and ON479 line 17 is 0. The second test is
the resident variant of the same return (the count at 0), where the total is claimed and line 17
is 11500 x 5% = 575.00. Return BU covers the not-resident case with the slips 6000 and 4000 on a
larger return; GD differs by its unequal slips and its simple filer, and adds the resident
variant's 5% on the sum of them. The tax figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_NET_INCOME,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    FLOW_THROUGH_SHARE_CLAIMABLE,
    FLOW_THROUGH_SHARE_CREDIT,
    FLOW_THROUGH_SHARE_EXPENSES,
    FLOW_THROUGH_SHARE_EXPENSES_CLAIMED,
    ONTARIO_CREDITS_SUBTOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_gd(*, resident: bool) -> Worksheet:
    """The worksheet of return GD, the inputs of `returns/2025_return_gd.yaml`.

    The filer has other income of 40000 and income tax deducted of 6000, with no employment income.
    The two slips carry qualifying expenses of 8000 and 3500. The count of "not a resident of
    Ontario on December 31, 2025" is 1 when `resident` is False (return GD itself) and 0 when it is
    True.
    """
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
        other_income="40000",
        income_tax_deducted="6000",
        not_resident_of_ontario_at_year_end=0 if resident else 1,
        flow_through_share_slips=("8000", "3500"),
    )


def test_total_income_is_40000_and_net_income_before_adjustments_is_40000() -> None:
    # Total income: other income of 40,000 (line 15000), since there is no employment income.
    # There are no deductions from total income (line 23300 is 0), so line 23400 is 40,000.
    worksheet = return_gd(resident=False)

    assert worksheet.get(TOTAL_INCOME).value == D("40000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("40000.00")


def test_net_income_and_taxable_income_are_40000_with_no_deductions() -> None:
    # Net income (line 23600) is 40,000, with no deduction from net income, so taxable income
    # (line 26000) is 40,000 - 0 = 40,000.
    worksheet = return_gd(resident=False)

    assert worksheet.get(NET_INCOME).value == D("40000.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")
    assert worksheet.get(TAXABLE_INCOME).value == D("40000.00")


def test_t1221_line_4_is_11500_but_not_claimed_by_a_non_resident() -> None:
    # T1221 lines 1 to 3: 8,000 + 3,500 = 11,500 (line 4, entered on line 63220). The count of 1
    # for "not a resident of Ontario on December 31, 2025" makes the claimable count 0, so the
    # expenses claimed are 11,500 x 0 = 0.
    worksheet = return_gd(resident=False)

    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES).value == D("11500")
    assert worksheet.get(FLOW_THROUGH_SHARE_CLAIMABLE).value == 0
    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES_CLAIMED).value == D("0")


def test_on479_line_17_and_the_ontario_credits_subtotal_are_0_for_a_non_resident() -> None:
    # ON479 line 17: 0 x 5% = 0.00. Line 18 and line 21 (the Ontario credits subtotal) carry no
    # other credit here, so they are 0.00.
    worksheet = return_gd(resident=False)

    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("0.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("0.00")


def test_a_resident_on_the_last_day_claims_11500_and_line_17_is_575() -> None:
    # The same return with the count at 0 (a resident of Ontario on December 31, 2025). The
    # claimable count is 1, so the expenses claimed are the whole 11,500. ON479 line 17: 11,500 x
    # 5% = 575.00, which is the Ontario credits subtotal (no other credit is claimed).
    worksheet = return_gd(resident=True)

    assert worksheet.get(FLOW_THROUGH_SHARE_CLAIMABLE).value == 1
    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES_CLAIMED).value == D("11500")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("575.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("575.00")


def test_the_resident_variant_has_the_same_income_as_return_gd() -> None:
    # The residence count moves the credit only: total income, net income and taxable income stay
    # at 40,000, as in return GD.
    worksheet = return_gd(resident=True)

    assert worksheet.get(TOTAL_INCOME).value == D("40000.00")
    assert worksheet.get(NET_INCOME).value == D("40000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("40000.00")
