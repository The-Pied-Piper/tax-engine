"""CA-ON 2025 end to end: return a child care."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CHILD_CARE_BASIC_LIMIT,
    CHILD_CARE_EARNED_INCOME,
    CHILD_CARE_EARNED_INCOME_LIMIT,
    CHILD_CARE_EXPENSES,
    CHILD_CARE_LIMIT_FOR_CHILDREN_SEVEN_TO_SIXTEEN,
    CHILD_CARE_LIMIT_FOR_CHILDREN_UNDER_SEVEN,
    CHILD_CARE_LIMIT_FOR_CHILDREN_WITH_DISABILITY,
    CHILDREN_SEVEN_TO_SIXTEEN,
    CWB_REDUCTION_WITH_DEPENDANT,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    TAXABLE_INCOME,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT,
    LIFT_REDUCTION,
    ONTARIO_BASIC_TAX,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def test_the_child_care_expenses_deduction_is_5000_for_one_child_and_lowers_net_income() -> None:
    # Return F, Form T778: the child, born in 2015, is counted on Part B line 3, so line 1 is 0
    # x 8000 = 0, line 2 0 x 11000 = 0 and line 3 1 x 5000 = 5000; line 4 is 0 + 0 + 5000 =
    # 5000; line 5 is the 6000 paid; line 6 is two-thirds of the earned income, the employment
    # income of 60000: 40000. Line 7 is the least of 5000, 6000 and 40000: 5000, line 21400. T1
    # line 23300 is 0 + 0 + 5000 + 565.00 = 5565.00, and net income 60000 - 5565.00 =
    # 54435.00, which the LIFT reduction (5% of 54435.00 over 32500 = 1096.75) and Schedule 6
    # (15% of 54435.00 over 30639 = 3569.40, with the eligible dependant) read; the federal and
    # Ontario taxes on it are 7893.075 and 2812.4735, rounded half-up to the cent.
    worksheet = compute(
        "60000",
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
    )

    assert worksheet.get(CHILDREN_SEVEN_TO_SIXTEEN).value == 1
    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_UNDER_SEVEN).value == D("0")
    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_WITH_DISABILITY).value == D("0")
    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_SEVEN_TO_SIXTEEN).value == D("5000")
    assert worksheet.get(CHILD_CARE_BASIC_LIMIT).value == D("5000")
    assert worksheet.get(CHILD_CARE_EARNED_INCOME).value == D("60000")
    assert worksheet.get(CHILD_CARE_EARNED_INCOME_LIMIT).value == D("40000")
    assert worksheet.get(CHILD_CARE_EXPENSES).value == D("5000")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("5565.00")
    assert worksheet.get(NET_INCOME).value == D("54435.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("54435.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("7893.08")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("2812.47")
    assert worksheet.get(LIFT_REDUCTION).value == D("1096.75")
    assert worksheet.get(LIFT_CREDIT).value == D("0")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("54435.00")
    assert worksheet.get(CWB_REDUCTION_WITH_DEPENDANT).value == D("3569.40")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "child_care_limit_for_children_seven_to_sixteen: 5000 for each of 1 "
        "children_seven_to_sixteen = 5000 (half-up to 0.01)"
    ) in rendered
    assert (
        "child_care_earned_income_limit: 2/3 of child_care_earned_income 60000 (half-up to 0.01)"
    ) in rendered
    assert (
        "child_care_expenses: lesser of child_care_basic_limit 5000 and child_care_expenses_paid "
        "6000 and child_care_earned_income_limit 40000 = 5000"
    ) in rendered
    assert (
        "deductions_from_total_income: rpp_deduction 0 + rrsp_deduction 0 "
        "+ fhsa_deduction 0 "
        "+ elected_split_pension_deduction 0 + union_dues 0 + uccb_repayment 0 "
        "+ child_care_expenses 5000 + disability_supports_deduction 0 "
        "+ allowable_business_investment_loss 0 "
        "+ moving_expenses_deduction 0 "
        "+ support_payments_deduction_checked 0 "
        "+ carrying_charges_interest_expenses_and_other_expenses 0 "
        "+ cpp_deduction_on_self_employment_and_other_earnings 0 "
        "+ cpp_enhanced_contributions_on_return 565 + exploration_and_development_expenses 0 "
        "+ other_employment_expenses 0 "
        "+ clergy_residence_deduction 0 "
        "+ other_deductions 0 + t746_deduction_on_return 0 "
        "+ t1043_deduction_on_return 0 "
        "+ foreign_property_tax_over_limit 0 + total_split_income 0 = 5565"
    ) in rendered


def test_expenses_paid_below_the_basic_limit_are_deducted_whole() -> None:
    # Return F with 3500 paid (T778 line 5): the least of 5000, 3500 and 40000 is 3500, so T1
    # line 23300 is 3500 + 565.00 = 4065.00 and net income 60000 - 4065.00 = 55935.00.
    worksheet = compute(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="3500",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
    )

    assert worksheet.get(CHILD_CARE_EXPENSES).value == D("3500")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("4065.00")
    assert worksheet.get(NET_INCOME).value == D("55935.00")


def test_the_limits_for_each_kind_of_eligible_child_add_up() -> None:
    # Return F with one child on each of T778 Part B lines 1, 2 and 3 and 30000 paid: line 4 is
    # 8000 + 11000 + 5000 = 24000, below the 30000 paid and the 40000 of line 6, so the
    # deduction is 24000, T1 line 23300 is 24000 + 565.00 = 24565.00 and net income 60000 -
    # 24565.00 = 35435.00.
    worksheet = compute(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="30000",
        children_under_seven=1,
        children_with_disability=1,
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
    )

    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_UNDER_SEVEN).value == D("8000")
    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_WITH_DISABILITY).value == D("11000")
    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_SEVEN_TO_SIXTEEN).value == D("5000")
    assert worksheet.get(CHILD_CARE_BASIC_LIMIT).value == D("24000")
    assert worksheet.get(CHILD_CARE_EXPENSES).value == D("24000")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("24565.00")
    assert worksheet.get(NET_INCOME).value == D("35435.00")


def test_two_thirds_of_a_low_earned_income_caps_the_deduction() -> None:
    # Employment income of 9000, two children born in 2019 or later and 12000 paid: line 4 is 2
    # x 8000 = 16000, line 5 12000, line 6 two-thirds of 9000 = 6000, the least, so the
    # deduction is 6000. The first additional CPP contribution is 1% x (9000 - 3500) = 55.00, so
    # T1 line 23300 is 6000 + 55.00 = 6055.00 and net income 9000 - 6055.00 = 2945.00.
    worksheet = compute(
        "9000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        child_care_expenses_paid="12000",
        children_under_seven=2,
    )

    assert worksheet.get(CHILD_CARE_BASIC_LIMIT).value == D("16000")
    assert worksheet.get(CHILD_CARE_EARNED_INCOME_LIMIT).value == D("6000")
    assert worksheet.get(CHILD_CARE_EXPENSES).value == D("6000")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("6055.00")
    assert worksheet.get(NET_INCOME).value == D("2945.00")
