"""CA-ON 2025 end to end: return gf."""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_ADJUSTED_TAXABLE_INCOME,
    AMT_MINIMUM_AMOUNT,
    AMT_PART_1_SUBTOTAL,
    NET_INCOME,
    NET_INCOME_SIGNED,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TAXABLE_INCOME_SIGNED,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_gf() -> Worksheet:
    """Employment income 400000 and other deductions 500000 (T1 line 23200), which are the resource
    expenditures of Form T691 Part 9 line 1, as in `returns/2025_return_gf.yaml`."""
    return compute(
        "400000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
        care_supporting_persons_adjusted_income="30000",
        other_deductions="500000",
        amt_resource_expenditures="500000",
        t4_cpp_pensionable_earnings_outside_quebec="400000",
        t2204_insurable_earnings="400000",
        t2204_premiums_deducted="1077.48",
        cpp_t4_base_and_first_additional_contributions="4034.10",
        cpp_t4_second_additional_contributions="396.00",
    )


def test_return_gf_net_income_below_zero_is_floored_for_taxable_income_but_not_for_line_1() -> None:
    # Total income is 400000 and the deductions from total income are 506074.00 (the other
    # deductions, line 23200, of 500000, the child care expenses deduction of 5000 and the CPP
    # enhanced contributions of 1074.00), so net income before adjustments is -106074.00. Line
    # 23600 "Line 54 minus line 55 (if negative, enter "0")" is 0, and line 26000 "Line 57 minus
    # line 68 (if negative, enter "0")" is 0 too. Form T691 Part 1 line 1 "Taxable income from line
    # 26000 of your return (or the amount you would have entered on line 26000 if the instructions
    # for lines 23600 and 26000 said "if negative, show in brackets")" is the signed -106074.00.
    worksheet = return_gf()

    assert worksheet.get(NET_INCOME_SIGNED).value == D("-106074.00")
    assert worksheet.get(NET_INCOME).value == D("0")
    assert worksheet.get(TAXABLE_INCOME_SIGNED).value == D("-106074.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("0")


def test_return_gf_t691_starts_the_minimum_tax_from_the_negative_line_1() -> None:
    # T691 Part 1 line 12 "Add lines 1, 4, 7, and 11." is -106074.00 (line 1 is the signed figure,
    # and the other lines are 0 here). Line 14, the resource property of Part 9 line 6 (the
    # resource expenditures of 500000 on line 1 less lines 2 to 4, 0), adds 500000: line 27 is
    # 393926.00 and so are lines 33 and 44. Line 80 is 50% of line 78, which is the 5000 of child
    # care expenses (line 52) and the 1074.00 of enhanced CPP contributions (line 58): 3037.00. The
    # adjusted taxable income (line 93) is 393926.00 + 3037.00 = 396963.00, line 95 is 396963.00
    # less 177882.00, 219081.00, and line 97 is 20.5% of it, 44911.605, half-up 44911.61. Line 102
    # is 50% of the 5533.57 of line 33800, 2766.785, half-up 2766.79, so the minimum amount is
    # 44911.61 - 2766.79 = 42144.82. The basic federal tax is negative, so Part 5 line 11 is the
    # whole minimum amount; the Ontario additional tax (24.63% of it, 10380.27, with the surtax
    # rates on it) is 12420.70 and the Ontario tax, after the LIFT credit of 875, is 11545.70. The
    # balance owing is 42144.82 + 11545.70 - 14163.00 of credits = 39527.52.
    worksheet = return_gf()

    assert worksheet.get(AMT_PART_1_SUBTOTAL).value == D("-106074.00")
    assert worksheet.get(AMT_ADJUSTED_TAXABLE_INCOME).value == D("396963.00")
    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("42144.82")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("39527.52")
