"""CA-ON 2025 end to end: return f."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.trace import (
    ChosenByCountLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    BASIC_PERSONAL_AMOUNT,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_LINE_28,
    CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
    CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITH_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT,
    CWB_ELIGIBLE_DEPENDANTS_CHECKED,
    CWB_REDUCTION_WITH_DEPENDANT,
    CWB_REDUCTION_WITHOUT_DEPENDANT,
    ELIGIBLE_DEPENDANT_AMOUNT,
    ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT,
    FEDERAL_TAX_AFTER_CREDITS,
    INFIRM_CHILDREN_AMOUNT,
    NET_INCOME,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
    WORKING_INCOME,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM,
    ELIGIBLE_DEPENDANT_BASE,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_REDUCTION,
    TAX_REDUCTION_AMOUNTS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def test_an_eligible_dependant_with_no_income_adds_the_basic_personal_amount_and_10823() -> None:
    # Return F: employment income of 60000, one dependent child who is an eligible dependant with
    # no net income, and the child care expenses deduction of 5000 (T1 line 21400), so net
    # income is 60000 - (5000 + 565.00) = 54435.00. Schedule 5 line 5 is its line 30000 of
    # 16129.00 less 0, claimed for 1 eligible dependant: line 30400 is 16129.00. ON428 line 16
    # is 11905.00 less 0, at most 10823: line 58160 is 10823. Line 33500 is 16129 + 16129.00 + 0
    # + 2796.75 + 984.00 + 1471 = 37509.75, and line 35000 37509.75 x 14.5% = 5438.91375,
    # rounded half-up to the cent: 5438.91, so the federal tax after credits is 14.5% x 54435.00
    # = 7893.075, rounded half-up to the cent: 7893.08, less it, 2454.17. ON428 line 58800 is
    # 12747 + 10823 + 2796.75 + 984.00 = 27350.75, and line 61500 27350.75 x 5.05% =
    # 1381.212875, rounded half-up to the cent: 1381.21, so the Ontario tax after credits is
    # 2670.74 + 9.15% x (54435.00 - 52886) = 2812.4735, rounded half-up to the cent: 2812.47,
    # less it, 1431.26. The child is a dependent child for the Ontario tax reduction: 294.00 +
    # 544 = 838.00, twice it 1676.00, less 1431.26 is a reduction of 244.74, leaving 1186.52.
    # With the health premium of 600 the Ontario tax is 1786.52, the total payable 2454.17 +
    # 1786.52 = 4240.69. Schedule ON479-A: line 4 is 54435.00 + 5000 = 59435.00, which is the
    # family adjusted income (line 5) with no supporting person, in "more than $55,000 but not
    # more than $60,000: 51%", so the care credit (line 8) is 5000 x 51% = 2550.00. The total
    # credits are 8000 + 2550.00 = 10550.00 and line 167 is 4240.69 - 10550.00 = -6309.31, a
    # refund.
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

    assert worksheet.get(NET_INCOME).value == D("54435.00")
    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("16129.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT).value == D("16129.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("16129.00")
    assert worksheet.get(INFIRM_CHILDREN_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("37509.75")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("5438.91")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("2454.17")
    assert worksheet.get(ELIGIBLE_DEPENDANT_BASE).value == D("11905.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM).value == D("11905.00")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT).value == D("10823")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("10823")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("27350.75")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("1381.21")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1431.26")
    assert worksheet.get(TAX_REDUCTION_AMOUNTS).value == D("838.00")
    assert worksheet.get(ONTARIO_TAX_REDUCTION).value == D("244.74")
    assert worksheet.get(ONTARIO_TAX).value == D("1786.52")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4240.69")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6309.31")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "eligible_dependant_amount: eligible_dependant_amount_before_count 16129 "
        "for each of 1 eligible_dependants_checked = 16129"
    ) in rendered
    assert (
        "eligible_dependant_amount: eligible_dependant_amount_before_count 10823 "
        "for each of 1 eligible_dependants_checked = 10823"
    ) in rendered
    assert (
        "non_refundable_credit_amounts: basic_personal_amount 16129 "
        "+ age_amount 0 + spouse_amount 0 "
        "+ eligible_dependant_amount 16129 "
        "+ caregiver_amount_for_spouse_or_dependant 0 + caregiver_amount 0 "
        "+ infirm_children_amount 0 "
        "+ cpp_base_contributions_on_return 2796.75 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 984 + ei_premiums_on_self_employment 0 "
        "+ volunteer_firefighters_credit 0 + search_and_rescue_credit 0 + "
        "canada_employment_amount 1471 + home_buyers_credit 0 + home_accessibility_credit 0 + "
        "adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 "
        "+ student_loan_interest 0 + federal_tuition_amount 0 + "
        "tuition_transferred_from_child_checked 0 + "
        "amounts_transferred_from_spouse 0 + medical_claim 0 = 37509.75"
    ) in rendered
    assert (
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 10823 + caregiver_amount 0 "
        "+ cpp_base_contributions_on_return 2796.75 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 984 + ei_premiums_on_self_employment 0 "
        "+ adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 + medical_claim 0 = 27350.75"
    ) in rendered


def test_return_fs_canada_workers_benefit_is_zero_with_an_eligible_dependant() -> None:
    # Return F, Schedule 6: working income 60000 (line 5) and adjusted family net income
    # 54435.00 (line 15). With the eligible dependant, line 22 is the lesser of (60000 - 3000) x
    # 27% = 15390.00 and 2813: 2813; line 27 is (54435.00 - 30639) x 15% = 3569.40; line 28 is
    # 2813 - 3569.40, negative, so 0. Without an eligible dependant, line 22 1633 and line 27
    # (54435.00 - 26855) x 15% = 4137.00, is computed too and is also 0; the count of 1
    # Schedule 6 eligible dependant (line 38100) chooses the amounts with one for T1 line 45300.
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

    assert worksheet.get(WORKING_INCOME).value == D("60000")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("54435.00")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITH_DEPENDANT).value == D("2813")
    assert worksheet.get(CWB_REDUCTION_WITH_DEPENDANT).value == D("3569.40")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("0")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT).value == D("1633")
    assert worksheet.get(CWB_REDUCTION_WITHOUT_DEPENDANT).value == D("4137.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT).value == D("0")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(TOTAL_CREDITS).value == D("10550.00")
    (chosen,) = [
        line
        for line in worksheet.trace
        if isinstance(line, ChosenByCountLine) and line.output == CANADA_WORKERS_BENEFIT_LINE_28
    ]
    assert chosen == ChosenByCountLine(
        output=CANADA_WORKERS_BENEFIT_LINE_28,
        count_kind=CWB_ELIGIBLE_DEPENDANTS_CHECKED,
        count=1,
        chosen_kind=CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
        chosen_value=D("0"),
    )
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "canada_workers_benefit_with_dependant: cwb_before_reduction_with_dependant 2813 "
        "less cwb_reduction_with_dependant 3569.4, not below 0 = 0"
    ) in rendered
    assert (
        "canada_workers_benefit_line_28: canada_workers_benefit_with_dependant 0, "
        "chosen as cwb_eligible_dependants_checked is 1"
    ) in rendered
