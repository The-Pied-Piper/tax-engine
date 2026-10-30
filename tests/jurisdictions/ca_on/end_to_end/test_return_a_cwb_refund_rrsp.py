"""CA-ON 2025 end to end: return a cwb refund rrsp."""

from __future__ import annotations

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
    CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITH_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT,
    CWB_REDUCTION_WITH_DEPENDANT,
    CWB_REDUCTION_WITHOUT_DEPENDANT,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    REFUND_OR_BALANCE_OWING,
    RRSP_CONTRIBUTIONS_AVAILABLE,
    RRSP_DEDUCTION,
    RRSP_DEDUCTION_MAXIMUM,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
    UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD,
    WORKING_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def test_the_canada_workers_benefit_below_its_maximum_is_27_percent_over_3000() -> None:
    # Employment income of 8000, with no capital gain, no RRSP contributions and no union dues:
    # base CPP contributions 4.95% x (8000 - 3500) = 222.75, first additional 1% x 4500 = 45.00,
    # EI premiums 1.64% x 8000 = 131.20; net income 8000 - 45.00 = 7955.00. Each form's credits
    # exceed its tax, so nothing is payable. Schedule 6: the working income (line 5) is 8000,
    # line 18 is 8000 - 3000 = 5000 and line 20 5000 x 27% = 1350.00, less than the $1,633 of
    # line 21, so line 22 is 1350.00; the adjusted family net income (line 15) of 7955.00 is
    # below the $26,855 of line 24, so line 27 is 0 and line 28 (T1 line 45300) is 1350.00. With
    # an eligible dependant the same 1350.00, below its $2,813 and over nothing above its
    # $30,639. With no tax deducted, the total credits are 0 + 1350.00 and line 167 is
    # 0 - 1350.00 = -1350.00, a refund.
    worksheet = compute("8000", (), "0", "0", "1440", "0", "0")

    assert worksheet.get(NET_INCOME).value == D("7955.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(WORKING_INCOME).value == D("8000")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("7955.00")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT).value == D("1350.00")
    assert worksheet.get(CWB_REDUCTION_WITHOUT_DEPENDANT).value == D("0")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITH_DEPENDANT).value == D("1350.00")
    assert worksheet.get(CWB_REDUCTION_WITH_DEPENDANT).value == D("0")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1350.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("1350.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1350.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "cwb_before_reduction_without_dependant: 27% of cwb_family_working_income 8000 over 3000, "
        "at most 1633 (half-up to 0.01)"
    ) in rendered
    assert (
        "canada_workers_benefit_without_dependant: cwb_before_reduction_without_dependant 1350 "
        "less cwb_reduction_without_dependant 0, not below 0 = 1350"
    ) in rendered
    assert (
        "canada_workers_benefit_line_28: cwb_line_28_by_spouse 1350, "
        "chosen as cwb_eligible_dependants_checked is 0"
    ) in rendered


def test_an_eligible_dependant_takes_the_schedule_6_amounts_of_2813_and_30639() -> None:
    # Employment income of 35000 and one eligible dependant, a dependent child: base CPP
    # contributions 4.95% x (35000 - 3500) = 1559.25, first additional 1% x 31500 = 315.00, so
    # net income is 35000 - 315.00 = 34685.00. Schedule 6 lines 21 and 24, "If you had an
    # eligible spouse or an eligible dependant, enter $2,813. If not, enter $1,633." and "...
    # enter $30,639. If not, enter $26,855.": with no eligible spouse or dependant, line 22 is
    # 1633 (32000 x 27% = 8640.00 is more), line 27 (34685.00 - 26855) x 15% = 1174.50 and
    # line 28 458.50; with one, line 22 is 2813, line 27 (34685.00 - 30639) x 15% = 606.90
    # and line 28 2206.10, each rounded half-up to the cent, which changes none of them. The
    # count of 1 Schedule 6 eligible dependant (line 38100) chooses the second for line 45300, so
    # with no tax deducted the total credits are 2206.10.
    worksheet = compute(
        "35000",
        (),
        "0",
        "0",
        "6300",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
    )

    assert worksheet.get(NET_INCOME).value == D("34685.00")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT).value == D("1633")
    assert worksheet.get(CWB_REDUCTION_WITHOUT_DEPENDANT).value == D("1174.50")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT).value == D("458.50")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITH_DEPENDANT).value == D("2813")
    assert worksheet.get(CWB_REDUCTION_WITH_DEPENDANT).value == D("606.90")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("2206.10")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("2206.10")
    assert worksheet.get(TOTAL_CREDITS).value == D("2206.10")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "cwb_before_reduction_with_dependant: 27% of cwb_family_working_income 35000 over 3000, "
        "at most 2813 (half-up to 0.01)"
    ) in rendered
    assert (
        "cwb_reduction_with_dependant: 15% of adjusted_family_net_income 34685 over 30639 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "canada_workers_benefit_line_28: canada_workers_benefit_with_dependant 2206.1, "
        "chosen as cwb_eligible_dependants_checked is 1"
    ) in rendered


def test_with_no_eligible_dependant_the_same_income_takes_the_amounts_of_1633_and_26855() -> None:
    # The amounts of the test above with no eligible dependant claimed for, and no dependent
    # child: both family statuses are computed alike, and the count of 0 chooses the one
    # without an eligible dependant, 458.50.
    worksheet = compute("35000", (), "0", "0", "6300", "0", "0")

    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT).value == D("458.50")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("2206.10")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("458.50")
    assert worksheet.get(TOTAL_CREDITS).value == D("458.50")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "canada_workers_benefit_line_28: cwb_line_28_by_spouse 458.5, "
        "chosen as cwb_eligible_dependants_checked is 0"
    ) in rendered


def test_a_line_30400_dependant_who_is_not_schedule_6s_leaves_the_amounts_without_one() -> None:
    # The amounts of the tests above with one eligible dependant claimed for on T1 line 30400, a
    # parent, say, who is not Schedule 6's eligible dependant ("They were your or your spouse's
    # or common-law partner's child"): the Schedule 6 count of 0 (line 38100), not the line
    # 30400 count of 1, chooses the amounts with no eligible dependant, 458.50.
    worksheet = compute("35000", (), "0", "0", "6300", "0", "0", eligible_dependants=1)

    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT).value == D("458.50")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("2206.10")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("458.50")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "canada_workers_benefit_line_28: cwb_line_28_by_spouse 458.5, "
        "chosen as cwb_eligible_dependants_checked is 0"
    ) in rendered


def test_a_schedule_6_dependant_not_claimed_on_line_30400_takes_the_amounts_with_one() -> None:
    # The same income with a child under 19 who lived with the filer but is not claimed for on
    # T1 line 30400 (claimed by the other parent, say): the Schedule 6 count of 1 (line 38100)
    # chooses the amounts with an eligible dependant, 2206.10, though the line 30400 count is 0.
    worksheet = compute("35000", (), "0", "0", "6300", "0", "0", cwb_eligible_dependants=1)

    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT).value == D("458.50")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("2206.10")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("2206.10")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "canada_workers_benefit_line_28: canada_workers_benefit_with_dependant 2206.1, "
        "chosen as cwb_eligible_dependants_checked is 1"
    ) in rendered


def test_tax_deducted_above_the_total_payable_is_a_refund() -> None:
    # Return A's amounts with 30000 of income tax deducted (T1 line 43700): line 167 is the total
    # payable of 25897.15 less the total credits of 30000, -4102.85, negative, so a refund (line
    # 48400), in cents as every line before it is.
    worksheet = compute(
        "110000",
        (("20000", "0", "0"),),
        "0",
        "1926",
        "19800",
        "1926",
        "2000",
        income_tax_deducted="30000",
    )

    assert worksheet.get(TOTAL_PAYABLE).value == D("25897.15")
    assert worksheet.get(TOTAL_CREDITS).value == D("30000")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-4102.85")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "refund_or_balance_owing: total_payable 25897.15 less total_credits 30000 = -4102.85"
    ) in rendered


def test_tax_deducted_equal_to_the_total_payable_leaves_no_balance() -> None:
    worksheet = compute(
        "110000",
        (("20000", "0", "0"),),
        "0",
        "1926",
        "19800",
        "1926",
        "2000",
        income_tax_deducted="25897.15",
    )

    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_with_no_tax_payable_all_the_tax_deducted_is_refunded() -> None:
    # Employment income of 10000 leaves no federal and no Ontario tax and a Canada workers
    # benefit of 1633 (see the test of a credit larger than the tax), so the total payable is 0;
    # with 500 deducted, the total credits are 500 + 1633 = 2133 and line 167 is 0 - 2133 =
    # -2133, a refund of everything deducted and the benefit, not floored at zero.
    worksheet = compute("10000", (), "0", "0", "1800", "0", "0", income_tax_deducted="500")

    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1633")
    assert worksheet.get(TOTAL_CREDITS).value == D("2133")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2133")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "total_credits: income_tax_deducted_after_election 500 + cpp_overpayment 0 "
        "+ ei_overpayment 0 "
        "+ refundable_medical_expense_supplement 0 "
        "+ canada_workers_benefit 1633 "
        "+ canada_training_credit 0 + multigenerational_home_renovation_credit 0 "
        "+ investment_tax_credit_refund 0 + part_xii_2_tax_credit 0 + "
        "employee_and_partner_gst_hst_rebate 0 "
        "+ educator_school_supply_credit 0 + journalism_labour_tax_credit 0 "
        "+ fuel_charge_credit_farmers_total 0 "
        "+ tax_paid_by_instalments 0 + provincial_credits 0 = 2133"
    ) in rendered


def test_contributions_above_the_deduction_limit_deduct_the_limit() -> None:
    # Schedule 7 line 17 "Enter whichever is less: amount from line 13 or line 16.": Return A's
    # amounts with contributions of 25000, above the deduction limit of 19800, so the most that
    # may be deducted is the limit, and deducting all of it (line 18) makes it the deduction;
    # total deductions are 19800 + 2000 + 1074.00 = 22874.00. Line 23 carries 25000 - 19800 =
    # 5200 forward.
    worksheet = compute("110000", (("20000", "0", "0"),), "0", "25000", "19800", "19800", "2000")

    assert worksheet.get(RRSP_DEDUCTION_MAXIMUM).value == D("19800")
    assert worksheet.get(RRSP_DEDUCTION).value == D("19800")
    assert worksheet.get(UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD).value == D("5200")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("22874.00")
    assert worksheet.get(NET_INCOME).value == D("97126.00")


def test_unused_contributions_and_no_new_ones_still_deduct() -> None:
    # Schedule 7 line 5 "Line 1 plus line 4 ... Total contributions" and line 17 "Enter
    # whichever is less: amount from line 13 or line 16.": Return A's amounts with unused
    # contributions of 5000 from earlier years (line 1) and no new contributions (line 4), so
    # the contributions available to deduct (line 10) are 5000 + 0 = 5000, below the deduction
    # limit of 19800; all 5000 is deducted (line 18); total deductions are 5000 + 2000 + 1074.00
    # = 8074.00.
    worksheet = compute("110000", (("20000", "0", "0"),), "5000", "0", "19800", "5000", "2000")

    assert worksheet.get(RRSP_CONTRIBUTIONS_AVAILABLE).value == D("5000")
    assert worksheet.get(RRSP_DEDUCTION_MAXIMUM).value == D("5000")
    assert worksheet.get(RRSP_DEDUCTION).value == D("5000")
    assert worksheet.get(UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD).value == D("0")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("8074.00")
    assert worksheet.get(NET_INCOME).value == D("111926.00")


def test_a_claim_below_the_maximum_deducts_the_claim_and_carries_the_rest_forward() -> None:
    # Schedule 7 line 18 "Enter your RRSP, PRPP, or SPP contributions you are deducting for 2025
    # (cannot be more than the amount on line 17).": Return A's amounts deducting 1000 of the
    # 1926 that line 17 allows, so the deduction (line 20) is 1000, and line 23 "Line 21 minus
    # line 22 Your unused contributions available to carry forward to a future year" is 1926 -
    # 1000 = 926. Total deductions are 1000 + 2000 + 1074.00 = 4074.00, and net income
    # 120000 - 4074.00 = 115926.00.
    worksheet = compute("110000", (("20000", "0", "0"),), "0", "1926", "19800", "1000", "2000")

    assert worksheet.get(RRSP_DEDUCTION_MAXIMUM).value == D("1926")
    assert worksheet.get(RRSP_DEDUCTION).value == D("1000")
    assert worksheet.get(UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD).value == D("926")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("4074.00")
    assert worksheet.get(NET_INCOME).value == D("115926.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "rrsp_deduction: rrsp_amount_deducted 1000, at most rrsp_deduction_maximum 1926" in (
        rendered
    )
    assert (
        "unused_rrsp_contributions_carried_forward: rrsp_contributions_available 1926 "
        "less rrsp_deduction 1000 = 926"
    ) in rendered


def test_a_claim_above_the_maximum_is_refused_naming_both_kinds() -> None:
    # Line 18 "cannot be more than the amount on line 17": Return A's amounts claiming 3000
    # against a line 17 of 1926 is an input error, not capped to 1926.
    with pytest.raises(InputAboveBoundError) as raised:
        compute("110000", (("20000", "0", "0"),), "0", "1926", "19800", "3000", "2000")

    assert str(raised.value) == (
        "ca-on/return, instance 1: "
        "ca/rrsp_amount_deducted 3000 is above ca/rrsp_deduction_maximum 1926"
    )
