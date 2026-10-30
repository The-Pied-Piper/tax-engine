"""CA-ON 2025 end to end: return u."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import NoAmountForCountError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CANADA_EMPLOYMENT_AMOUNT,
    CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
    CPP_BASIC_EXEMPTION,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT,
    CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL,
    CPP_EARNINGS_SUBJECT_TO_SECOND_ADDITIONAL,
    CPP_EARNINGS_UP_TO_MAXIMUM,
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_MONTHS,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    CPP_PENSIONABLE_EARNINGS,
    CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM,
    CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    EI_EARNINGS_SUBJECT_TO_PREMIUM,
    EI_EXCLUDED_SLIPS_NET_INCOME,
    EI_INSURABLE_EARNINGS_REMAINING,
    EI_MAXIMUM_INSURABLE_EARNINGS,
    EI_NET_SELF_EMPLOYMENT_INCOME,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    EI_PREMIUMS_ON_SELF_EMPLOYMENT,
    EI_SELF_EMPLOYMENT_BEFORE_SLIPS,
    EI_SELF_EMPLOYMENT_EARNINGS,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    NET_FEDERAL_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS,
    REFUND_OR_BALANCE_OWING,
    SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS,
    SELF_EMPLOYED_CPP_BASE_CREDIT,
    SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE,
    SELF_EMPLOYED_CPP_DEDUCTION,
    SELF_EMPLOYED_CPP_ENHANCED_CONTRIBUTIONS,
    SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
    SELF_EMPLOYED_CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
    SELF_EMPLOYED_EI_PREMIUMS,
    TAXABLE_INCOME,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.catalog import (
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_REDUCTION,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, routed_statement

# Return U's inputs beyond the all-zero ones `compute` defaults: net business income (T1 line
# 13500, now T2125 line 9946) of 50000, entered as T2125 gross sales (amount 3A) of 50000 with no
# expenses, which is all of total income (line 15000, through line 27); Schedule 8 Part 4
# completed and the agreement for EI special benefits, each a count of 1.
RETURN_U: dict[str, Any] = {
    "business_income": "50000",
    "cpp_part_4_completed": 1,
    "ei_special_benefits_agreement": 1,
}


def business_statement(business_income: str) -> dict[str, str]:
    """A T2125 whose line 9946, and so T1 line 13500, is `business_income`: all gross sales (amount
    3A) for income, all advertising (amount 4B) for a loss."""
    amount = D(business_income)
    if amount >= 0:
        return {"gross_sales": business_income}
    return {"advertising": str(-amount)}


def farm_statement(farming_income: str) -> dict[str, str]:
    """A T2042 whose line 9946, and so T1 line 14100, is `farming_income`: all income (line 9371)
    for income, all other expenses for a loss."""
    amount = D(farming_income)
    if amount >= 0:
        return {"wheat": farming_income}
    return {"other_expenses": str(-amount)}


def fish_statement(fishing_income: str) -> dict[str, str]:
    """A T2121 whose line 9946, and so T1 line 14300, is `fishing_income`: all income (amount 3A,
    fish products) for income, all other expenses (line 9270, 4P) for a loss."""
    amount = D(fishing_income)
    if amount >= 0:
        return {"fish_products": fishing_income}
    return {"other_expenses": str(-amount)}


def self_employed(**changes: Any) -> Worksheet:
    """Return U's inputs, as in `returns/2025_return_u.yaml`, with `changes` to them;
    `business_income` is the net business income the T2125 is entered to give,
    `farming_income` the net farming income the T2042 is entered to give and `fishing_income`
    the net fishing income the T2121 is entered to give."""
    inputs = {**RETURN_U, **changes}
    business = business_statement(inputs.pop("business_income"))
    statements = [{"business": business}]
    if "professional_income" in inputs:
        statements.append(routed_statement(inputs.pop("professional_income"), 2))
    if "commission_income" in inputs:
        statements.append(routed_statement(inputs.pop("commission_income"), 3))
    farm = farm_statement(inputs.pop("farming_income", "0"))
    fish = fish_statement(inputs.pop("fishing_income", "0"))
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=tuple(statements),
        farm_statements=({"farm": farm},),
        fish_statements=({"fish": fish},),
        **inputs,
    )


def return_u() -> Worksheet:
    """Return U's inputs, as in `returns/2025_return_u.yaml`: self-employment income only."""
    return self_employed()


def test_return_us_part_2_reads_the_12_month_row_of_the_monthly_proration_table() -> None:
    # Schedule 8 Part 2: box A "Enter the number of months that CPP applied in 2025" of 12, the
    # row "Number of months: 12" of the monthly proration table, as printed: line B $71,300.00,
    # line C $9,900.00, line D $81,200.00 and line E $3,500.00.
    worksheet = return_u()

    assert worksheet.get(CPP_MONTHS).value == 12
    assert worksheet.get(CPP_MAXIMUM_PENSIONABLE_EARNINGS).value == D("71300.00")
    assert worksheet.get(CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM).value == D("9900.00")
    assert worksheet.get(CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS).value == D("81200.00")
    assert worksheet.get(CPP_BASIC_EXEMPTION).value == D("3500.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    for line in (
        "cpp_maximum_pensionable_earnings: 71300 for cpp_months 12 (half-up to 0.01)",
        "cpp_second_additional_earnings_maximum: 9900 for cpp_months 12 (half-up to 0.01)",
        "cpp_additional_maximum_pensionable_earnings: 81200 for cpp_months 12 (half-up to 0.01)",
        "cpp_basic_exemption: 3500 for cpp_months 12 (half-up to 0.01)",
    ):
        assert line in rendered, line


def test_return_us_line_27_is_the_sum_of_lines_22_to_26_and_all_of_total_income() -> None:
    # T1 line 27 "Add lines 22 to 26. Net self-employment income": 50000 + 0 + 0 + 0 + 0. Line 28
    # is line 21 (0) plus line 27, and line 15000 adds line 27 to the other income lines (all 0),
    # so total income is 50000.00.
    worksheet = return_u()

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("50000")
    assert worksheet.get(TOTAL_INCOME).value == D("50000.00")
    assert (
        "net_self_employment_income: business_income 50000 + professional_income 0 "
        "+ commission_income 0 + farming_income 0 + fishing_income 0 = 50000"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_return_us_schedule_8_part_4_is_the_cra_worked_example() -> None:
    # Self-employed only, 12 months, line 27 of 50000 and no line 12200: Part 4 line 1 is 50000,
    # line 3 is 50000 + 0 and line 4 is the lesser of 81200 and 50000; line 6 is 50000 - 71300,
    # negative, so 0, line 7 is 50000 - 0 and line 9 is 50000 - 3500 = 46500. Line 10 is 46500 x
    # 9.9% = 4603.50, line 11 is 46500 x 2% = 930.00 and line 12 is 0 x 8% = 0; line 13 is 930.00
    # and line 14 is 4603.50 + 930.00 = 5533.50. Line 15 is 4603.50 x 50% = 2301.75 and line 17
    # is 2301.75 + 930.00 = 3231.75.
    worksheet = return_u()

    assert worksheet.get(PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS).value == D("50000")
    assert worksheet.get(CPP_PENSIONABLE_EARNINGS).value == D("50000")
    assert worksheet.get(CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM).value == D("50000")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_SECOND_ADDITIONAL).value == D("0")
    assert worksheet.get(CPP_EARNINGS_UP_TO_MAXIMUM).value == D("50000")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL).value == D("46500")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS).value == D("4603.50")
    assert worksheet.get(SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("930.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("0")
    assert worksheet.get(SELF_EMPLOYED_CPP_ENHANCED_CONTRIBUTIONS).value == D("930.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("5533.50")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CREDIT).value == D("2301.75")
    assert worksheet.get(SELF_EMPLOYED_CPP_DEDUCTION).value == D("3231.75")
    # Lines 42100, 31000 and 22200: lines 14, 15 and 17 once, for the "Part 4 completed" of 1.
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("5533.50")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT).value == D("2301.75")
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT).value == D("3231.75")


def test_return_us_schedule_8_part_4_is_explained_line_by_line() -> None:
    rendered = EnglishTraceRenderer().render_all(return_u().trace)

    for line in (
        "pensionable_net_self_employment_earnings: net_partnership_income 0 "
        "+ net_self_employment_income 50000 = 50000",
        "cpp_pensionable_earnings: pensionable_net_self_employment_earnings 50000 "
        "+ cpt20_earnings 0, not below 0 = 50000",
        "cpp_pensionable_earnings_up_to_additional_maximum: lesser of "
        "cpp_additional_maximum_pensionable_earnings 81200 and cpp_pensionable_earnings 50000 "
        "= 50000",
        "cpp_earnings_subject_to_second_additional: "
        "cpp_pensionable_earnings_up_to_additional_maximum 50000 "
        "less cpp_maximum_pensionable_earnings 71300, not below 0 = 0",
        "cpp_earnings_up_to_maximum: cpp_pensionable_earnings_up_to_additional_maximum 50000 "
        "less cpp_earnings_subject_to_second_additional 0, not below 0 = 50000",
        "cpp_earnings_subject_to_base_and_first_additional: cpp_earnings_up_to_maximum 50000 "
        "less cpp_basic_exemption 3500, not below 0 = 46500",
        "self_employed_cpp_base_contributions: 9.9% of "
        "cpp_earnings_subject_to_base_and_first_additional between 0 and 67800 (46500), "
        "at most 6712.2 (half-up to 0.01)",
        "self_employed_cpp_first_additional_contributions: 2% of "
        "cpp_earnings_subject_to_base_and_first_additional between 0 and 67800 (46500), "
        "at most 1356 (half-up to 0.01)",
        "self_employed_cpp_second_additional_contributions: 8% of "
        "cpp_earnings_subject_to_second_additional between 0 and 9900 (0), "
        "at most 792 (half-up to 0.01)",
        "self_employed_cpp_enhanced_contributions: "
        "self_employed_cpp_first_additional_contributions 930 "
        "+ self_employed_cpp_second_additional_contributions 0 = 930",
        "self_employed_cpp_contributions_payable: self_employed_cpp_base_contributions 4603.5 "
        "+ self_employed_cpp_enhanced_contributions 930 = 5533.5",
        "self_employed_cpp_base_credit: 50% of self_employed_cpp_base_contributions 4603.5 "
        "(half-up to 0.01)",
        "self_employed_cpp_deduction: self_employed_cpp_base_credit 2301.75 "
        "+ self_employed_cpp_enhanced_contributions 930 = 3231.75",
        "cpp_payable_on_self_employment: self_employed_cpp_contributions_payable 5533.5 "
        "for each of 1 cpp_part_4_completed_checked = 5533.5",
        "cpp_base_contributions_on_self_employment: self_employed_cpp_base_credit 2301.75 "
        "for each of 1 cpp_part_4_completed_checked = 2301.75",
        "cpp_deduction_on_self_employment: self_employed_cpp_deduction 3231.75 "
        "for each of 1 cpp_part_4_completed_checked = 3231.75",
    ):
        assert line in rendered, line


def test_return_us_schedule_13_is_the_cra_worked_example() -> None:
    # Schedule 13 on line 27 of 50000 with an agreement with the Commission: line 1 is 0 + 50000,
    # line 4 is 50000 + 0 + 0, line 5 is 65700.00, line 7 is 65700.00 - 0 and line 8 is the lesser
    # of 50000 and 65700.00; line 9 is 50000 x 1.64% = 820.00, lines 31217 and 42120.
    worksheet = return_u()

    assert worksheet.get(EI_SELF_EMPLOYMENT_BEFORE_SLIPS).value == D("50000")
    assert worksheet.get(EI_EXCLUDED_SLIPS_NET_INCOME).value == D("0")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("50000")
    assert worksheet.get(EI_NET_SELF_EMPLOYMENT_INCOME).value == D("50000")
    assert worksheet.get(EI_MAXIMUM_INSURABLE_EARNINGS).value == D("65700.00")
    assert worksheet.get(EI_INSURABLE_EARNINGS_REMAINING).value == D("65700.00")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("50000")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("820.00")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("820.00")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("820.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    for line in (
        "ei_self_employment_before_slips: net_partnership_income 0 "
        "+ net_self_employment_income 50000 = 50000",
        "ei_excluded_slips_net_income: no items = 0",
        "ei_self_employment_earnings: ei_self_employment_before_slips 50000 "
        "less ei_excluded_slips_net_income 0, not below 0 = 50000",
        "ei_net_self_employment_income: ei_self_employment_earnings 50000 "
        "+ ei_controlled_corporation_earnings 0 + ei_exempt_self_employment_income 0 = 50000",
        "ei_maximum_insurable_earnings: credit amount 65700 (half-up to 0.01)",
        "ei_insurable_earnings_remaining: ei_maximum_insurable_earnings 65700 "
        "less ei_insurable_earnings 0, not below 0 = 65700",
        "ei_earnings_subject_to_premium: lesser of ei_net_self_employment_income 50000 "
        "and ei_insurable_earnings_remaining 65700 = 50000",
        "self_employed_ei_premiums: 1.64% of ei_earnings_subject_to_premium between 0 and 65700 "
        "(50000), at most 1077.48 (half-up to 0.01)",
        "ei_premiums_on_self_employment: self_employed_ei_premiums 820 "
        "for each of 1 ei_special_benefits_agreement_checked = 820",
        "ei_payable_on_self_employment: self_employed_ei_premiums 820 "
        "for each of 1 ei_special_benefits_agreement_checked = 820",
    ):
        assert line in rendered, line


def test_return_us_new_lines_join_the_deductions_the_credit_amounts_and_the_total_payable() -> None:
    # Line 22200 (3231.75) is a deduction from total income (line 23300 "Add lines 35 to 52"), so
    # net income is 50000.00 - 3231.75 = 46768.25 and so is taxable income. The federal tax on it
    # is 46768.25 x 14.5% = 6781.39625, rounded half-up to the cent: 6781.40. Lines 31000
    # (2301.75) and 31217 (820.00) are credit amounts of the T1 (line 33500): 16129.00 + 0 + 0 + 0
    # + 0 + 0 + 0 + 2301.75 + 0 + 820.00 + 0 = 19250.75, times 14.5% = 2791.358750, rounded
    # half-up to the cent: 2791.36, so the federal tax after credits is 6781.40 - 2791.36 =
    # 3990.04. ON428's lines 58280 and 58305 copy lines 31000 and 31217, so its credit amounts
    # (line 58800) are 12747 + 0 + 0 + 0 + 0 + 2301.75 + 0 + 820.00 = 15868.75, 5.05% of which is
    # 801.371875, rounded half-up to the cent: 801.37. Ontario's tax on 46768.25 is 2361.80
    # (46768.25 x 5.05% = 2361.796625, rounded half-up to the cent: 2361.80), less the credits:
    # 1560.43; it is
    # above twice the reduction amounts (588.00), so there is no reduction. The health premium
    # row "more than $38,500 but not more than $48,000" is $450, so the
    # Ontario tax is 1560.43 + 450.00 = 2010.43. Lines 42100 and 42120 join lines 42000 and 42800
    # in line 43500: 3990.04 + 5533.50 + 820.00 + 2010.43 = 12353.97, with no tax deducted and no
    # credit, a balance owing.
    worksheet = return_u()

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("3231.75")
    assert worksheet.get(NET_INCOME).value == D("46768.25")
    assert worksheet.get(TAXABLE_INCOME).value == D("46768.25")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("6781.40")
    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("19250.75")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("2791.36")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3990.04")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15868.75")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("801.37")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1560.43")
    assert worksheet.get(ONTARIO_TAX_REDUCTION).value == D("0")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("450.00")
    assert worksheet.get(ONTARIO_TAX).value == D("2010.43")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("3990.04")
    assert worksheet.get(TOTAL_PAYABLE).value == D("12353.97")
    assert worksheet.get(TOTAL_CREDITS).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("12353.97")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    for line in (
        "deductions_from_total_income: rpp_deduction 0 + rrsp_deduction 0 "
        "+ fhsa_deduction 0 "
        "+ elected_split_pension_deduction 0 + union_dues 0 + uccb_repayment 0 "
        "+ child_care_expenses 0 + disability_supports_deduction 0 "
        "+ allowable_business_investment_loss 0 "
        "+ moving_expenses_deduction 0 "
        "+ support_payments_deduction_checked 0 "
        "+ carrying_charges_interest_expenses_and_other_expenses 0 "
        "+ cpp_deduction_on_self_employment_and_other_earnings 3231.75 + "
        "cpp_enhanced_contributions_on_return 0 "
        "+ exploration_and_development_expenses 0 "
        "+ other_employment_expenses 0 + clergy_residence_deduction 0 "
        "+ other_deductions 0 "
        "+ t746_deduction_on_return 0 "
        "+ t1043_deduction_on_return 0 "
        "+ foreign_property_tax_over_limit 0 "
        "+ total_split_income 0 = 3231.75",
        "non_refundable_credit_amounts: basic_personal_amount 16129 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 "
        "+ caregiver_amount_for_spouse_or_dependant 0 "
        "+ caregiver_amount 0 + infirm_children_amount 0 + cpp_base_contributions_on_return 0 "
        "+ cpp_base_contributions_on_self_employment_and_other_earnings 2301.75 + ei_premiums 0 "
        "+ ei_premiums_on_self_employment 820 + volunteer_firefighters_credit 0 + "
        "search_and_rescue_credit 0 + canada_employment_amount 0 "
        "+ home_buyers_credit 0 + home_accessibility_credit 0 + adoption_credit 0 + "
        "pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + federal_tuition_amount 0 + "
        "tuition_transferred_from_child_checked 0 + amounts_transferred_from_spouse 0 + "
        "medical_claim 0 = "
        "19250.75",
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 + caregiver_amount 0 "
        "+ cpp_base_contributions_on_return 0 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 2301.75 "
        "+ ei_premiums 0 + ei_premiums_on_self_employment 820 "
        "+ adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 + medical_claim 0 = 15868.75",
        "total_payable: net_federal_tax 3990.04 + "
        "cpp_payable_on_self_employment_and_other_earnings 5533.5 "
        "+ ei_payable_on_self_employment 820 + social_benefits_repayment_payable 0 "
        "+ ontario_tax 2010.43 = 12353.97",
    ):
        assert line in rendered, line


def test_line_27_of_90000_fills_the_second_additional_band_and_caps_every_line_at_its_maximum() -> (
    None
):
    # Line 4 is the lesser of 81200 and 90000, 81200; line 6 is 81200 - 71300 = 9900 and line 7 is
    # 81200 - 9900 = 71300, so line 9 is 71300 - 3500 = 67800. Line 10 is 67800 x 9.9% = 6712.20,
    # line 11 is 67800 x 2% = 1356.00 and line 12 is 9900 x 8% = 792.00 (each at its maximum);
    # line 13 is 1356.00 + 792.00 = 2148.00 and line 14 is 6712.20 + 2148.00 = 8860.20. Line 15 is
    # 6712.20 x 50% = 3356.10 and line 17 is 3356.10 + 2148.00 = 5504.10. Schedule 13: line 7 is
    # 65700.00, line 8 the lesser of 90000 and 65700.00, so line 9 is 65700.00 x 1.64% = 1077.48.
    worksheet = self_employed(business_income="90000")

    assert worksheet.get(CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM).value == D("81200")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_SECOND_ADDITIONAL).value == D("9900")
    assert worksheet.get(CPP_EARNINGS_UP_TO_MAXIMUM).value == D("71300")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL).value == D("67800")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS).value == D("6712.20")
    assert worksheet.get(SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("1356.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("792.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_ENHANCED_CONTRIBUTIONS).value == D("2148.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("8860.20")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CREDIT).value == D("3356.10")
    assert worksheet.get(SELF_EMPLOYED_CPP_DEDUCTION).value == D("5504.10")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("8860.20")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT).value == D("3356.10")
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT).value == D("5504.10")
    assert worksheet.get(EI_INSURABLE_EARNINGS_REMAINING).value == D("65700.00")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("65700.00")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("1077.48")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("1077.48")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("1077.48")


def test_a_loss_on_line_27_leaves_line_3_and_every_line_after_it_at_zero() -> None:
    # A net business loss of 5000 and net partnership income (line 12200) of 3000: Part 4 line 1 is
    # 3000 + -5000 = -2000 and line 3 "(if negative, enter "0")" is 0, so lines 4, 6, 7 and 9 are
    # 0 and every contribution is 0. Schedule 13 line 1 "(if negative, enter "0")" is 0 too.
    worksheet = self_employed(business_income="-5000", net_partnership_income="3000")

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("-5000")
    assert worksheet.get(PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS).value == D("-2000")
    assert worksheet.get(CPP_PENSIONABLE_EARNINGS).value == D("0")
    assert worksheet.get(CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM).value == D("0")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL).value == D("0")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("0")
    assert worksheet.get(SELF_EMPLOYED_CPP_DEDUCTION).value == D("0")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("0")
    assert worksheet.get(EI_NET_SELF_EMPLOYMENT_INCOME).value == D("0")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("0")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("0")
    assert (
        "cpp_pensionable_earnings: pensionable_net_self_employment_earnings -2000 "
        "+ cpt20_earnings 0, not below 0 = 0"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_cpt20_earnings_are_added_to_a_loss_on_part_4_line_3_but_not_to_schedule_13() -> None:
    # Part 4 line 2 (50373) "Employment earnings not shown on a T4 slip that you are electing to
    # pay additional CPP contributions on (complete Form CPT20)" of 5000 added to line 1 of -2000:
    # line 3 is 3000, below the 3500 exemption, so line 9 and the contributions are 0. Schedule 13
    # does not read line 2 of Part 4.
    worksheet = self_employed(
        business_income="-5000", net_partnership_income="3000", cpt20_earnings="5000"
    )

    assert worksheet.get(CPP_PENSIONABLE_EARNINGS).value == D("3000")
    assert worksheet.get(CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM).value == D("3000")
    assert worksheet.get(CPP_EARNINGS_UP_TO_MAXIMUM).value == D("3000")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL).value == D("0")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("0")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("0")


def test_cpt20_earnings_alone_are_pensionable_earnings_under_part_4() -> None:
    # No line 27, and CPT20 earnings of 10000 (line 2): line 3 is 10000, line 9 is 10000 - 3500 =
    # 6500; line 10 is 6500 x 9.9% = 643.50, line 11 is 6500 x 2% = 130.00 and line 14 is 773.50;
    # line 15 is 643.50 x 50% = 321.75 and line 17 is 321.75 + 130.00 = 451.75.
    worksheet = self_employed(business_income="0", cpt20_earnings="10000")

    assert worksheet.get(CPP_PENSIONABLE_EARNINGS).value == D("10000")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS).value == D("643.50")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("773.50")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("773.50")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT).value == D("321.75")
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT).value == D("451.75")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("0")


def test_net_partnership_income_is_added_to_line_27_in_both_schedules() -> None:
    # Part 4 line 1 and Schedule 13 line 1 are "amount from line 12200 of your return plus line 27
    # of your return": 20000 + 30000 = 50000, the same lines as Return U's.
    worksheet = self_employed(business_income="30000", net_partnership_income="20000")

    assert worksheet.get(PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS).value == D("50000")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("50000")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("5533.50")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT).value == D("2301.75")
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT).value == D("3231.75")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("820.00")


def test_the_five_lines_of_self_employment_income_add_to_line_27() -> None:
    # 20000 + 15000 + 10000 + 4000 + 1000 = 50000, so the same lines as Return U's.
    worksheet = self_employed(
        business_income="20000",
        professional_income="15000",
        commission_income="10000",
        farming_income="4000",
        fishing_income="1000",
    )

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("50000")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("5533.50")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("820.00")


def test_a_loss_on_one_line_is_set_against_the_gains_on_the_others() -> None:
    # Line 27 is signed: a farming loss of 10000 against a business income of 60000 is 50000.
    worksheet = self_employed(business_income="60000", farming_income="-10000")

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("50000")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("5533.50")


def test_six_months_take_the_six_month_row_of_the_proration_table() -> None:
    # Box A of 6: line B $35,650.00, line C $4,950.00, line D $40,600.00, line E $1,750.00. On line
    # 27 of 50000, line 4 is the lesser of 40600.00 and 50000; line 6 is 40600.00 - 35650.00 =
    # 4950.00 and line 7 is 40600.00 - 4950.00 = 35650.00, so line 9 is 35650.00 - 1750.00 =
    # 33900.00. Line 10 is 33900.00 x 9.9% = 3356.10, line 11 is 33900.00 x 2% = 678.00 and line
    # 12 is 4950.00 x 8% = 396.00; line 13 is 1074.00, line 14 is 4430.10, line 15 is 3356.10 x
    # 50% = 1678.05 and line 17 is 1678.05 + 1074.00 = 2752.05. Schedule 13 does not read box A.
    worksheet = self_employed(cpp_months=6)

    assert worksheet.get(CPP_MAXIMUM_PENSIONABLE_EARNINGS).value == D("35650.00")
    assert worksheet.get(CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM).value == D("4950.00")
    assert worksheet.get(CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS).value == D("40600.00")
    assert worksheet.get(CPP_BASIC_EXEMPTION).value == D("1750.00")
    assert worksheet.get(CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM).value == D("40600.00")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_SECOND_ADDITIONAL).value == D("4950.00")
    assert worksheet.get(CPP_EARNINGS_UP_TO_MAXIMUM).value == D("35650.00")
    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL).value == D("33900.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS).value == D("3356.10")
    assert worksheet.get(SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("678.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("396.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_ENHANCED_CONTRIBUTIONS).value == D("1074.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("4430.10")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CREDIT).value == D("1678.05")
    assert worksheet.get(SELF_EMPLOYED_CPP_DEDUCTION).value == D("2752.05")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("4430.10")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT).value == D("1678.05")
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT).value == D("2752.05")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("820.00")


def test_one_month_rounds_each_line_half_up_to_the_cent() -> None:
    # Box A of 1: line B $5,941.67, line C $825.00, line D $6,766.67, line E $291.67. On line 27 of
    # 80000, line 4 is 6766.67; line 6 is 6766.67 - 5941.67 = 825.00, line 7 is 5941.67 and line
    # 9 is 5941.67 - 291.67 = 5650.00. Line 10 is 5650.00 x 9.9% = 559.35, line 11 is 113.00 and
    # line 12 is 825.00 x 8% = 66.00; line 15 is 559.35 x 50% = 279.675, a tie, rounded half-up to
    # the cent: 279.68, and line 17 is 279.68 + 179.00 = 458.68.
    worksheet = self_employed(business_income="80000", cpp_months=1)

    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL).value == D("5650.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS).value == D("559.35")
    assert worksheet.get(SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("113.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("66.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("738.35")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CREDIT).value == D("279.68")
    assert worksheet.get(SELF_EMPLOYED_CPP_DEDUCTION).value == D("458.68")


def test_line_15_rounds_half_up_to_the_cent_on_its_own() -> None:
    # Line 27 of 3500.10: line 9 is 3500.10 - 3500.00 = 0.10, line 10 is 0.10 x 9.9% = 0.0099,
    # rounded half-up to the cent: 0.01; line 11 is 0.10 x 2% = 0.002, rounded: 0.00. Line 15 is
    # 0.01 x 50% = 0.005, a tie, rounded half-up to the cent: 0.01, and line 17 is 0.01 + 0.00.
    # Schedule 13 line 9 is 3500.10 x 1.64% = 57.40164, rounded half-up to the cent: 57.40.
    worksheet = self_employed(business_income="3500.10")

    assert worksheet.get(CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL).value == D("0.10")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS).value == D("0.01")
    assert worksheet.get(SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("0.00")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CREDIT).value == D("0.01")
    assert worksheet.get(SELF_EMPLOYED_CPP_DEDUCTION).value == D("0.01")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("57.40")


def test_schedule_13_line_9_rounds_a_tie_half_up_to_the_cent() -> None:
    # Line 27 of 12.50: 12.50 x 1.64% = 0.205, a tie, rounded half-up to the cent: 0.21. Below the
    # exemption, Part 4 has nothing to contribute.
    worksheet = self_employed(business_income="12.50")

    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("0.21")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("0.21")
    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("0")


def test_a_month_count_with_no_row_in_the_proration_table_is_refused() -> None:
    # The printed table has rows for 1 to 12 months. Box A's instructions say "Enter "0" on line
    # A" in some cases, but the table has no row for 0, and none for 13: neither is guessed at.
    for months in (0, 13):
        with pytest.raises(NoAmountForCountError, match=rf"no amount for count {months} of ca/"):
            self_employed(cpp_months=months, qpp_months=max(months, 12))


def test_part_4_not_completed_leaves_lines_42100_31000_and_22200_at_zero() -> None:
    # Part 4 is for "reporting only self-employment income": a filer who does not complete it
    # (count 0) carries nothing to lines 42100, 31000 and 22200, though the lines of Part 4 are
    # still worked out; the EI lines are the agreement's, not Part 4's.
    worksheet = self_employed(cpp_part_4_completed=0)

    assert worksheet.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value == D("5533.50")
    assert worksheet.get(SELF_EMPLOYED_CPP_BASE_CREDIT).value == D("2301.75")
    assert worksheet.get(SELF_EMPLOYED_CPP_DEDUCTION).value == D("3231.75")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("820.00")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("820.00")
    # No deduction of 3231.75: net income is the 50000.00 of total income, and the payable is the
    # taxes (12353.97 above, less the 5533.50 of line 42100 and the tax saved by 22200).
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0")
    assert worksheet.get(NET_INCOME).value == D("50000.00")


def test_no_agreement_with_the_commission_leaves_lines_31217_and_42120_at_zero() -> None:
    # Schedule 13 is for a filer who "has entered into an agreement with the Canada Employment
    # Insurance Commission": without one (count 0), line 9 is worked out but not carried.
    worksheet = self_employed(ei_special_benefits_agreement=0)

    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("820.00")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("0")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("5533.50")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("18430.75")


def test_schedule_13_lines_2_3_and_6_move_lines_4_and_7() -> None:
    # Line 2 (controlled corporation, box 14) of 5000 and line 3 (tax-exempt self-employment income
    # on a reserve) of 2000 add to line 1 of 50000: line 4 is 57000. Line 6 (total EI insurable
    # earnings) of 30000 comes off line 5: line 7 is 65700.00 - 30000 = 35700.00, below line 4,
    # so line 8 is 35700.00 and line 9 is 35700.00 x 1.64% = 585.48. Part 4 does not read them.
    worksheet = self_employed(
        ei_controlled_corporation_earnings="5000",
        ei_exempt_self_employment_income="2000",
        ei_insurable_earnings="30000",
    )

    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("50000")
    assert worksheet.get(EI_NET_SELF_EMPLOYMENT_INCOME).value == D("57000")
    assert worksheet.get(EI_INSURABLE_EARNINGS_REMAINING).value == D("35700.00")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("35700.00")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("585.48")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("585.48")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("585.48")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("5533.50")


def test_insurable_earnings_above_the_maximum_leave_no_room_for_a_premium() -> None:
    # Line 6 of 70000 is above line 5, 65700.00: line 7 "(if negative, enter "0")" is 0, so line
    # 8 is 0 and line 9 is 0.
    worksheet = self_employed(ei_insurable_earnings="70000")

    assert worksheet.get(EI_INSURABLE_EARNINGS_REMAINING).value == D("0")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("0")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("0")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("0")
