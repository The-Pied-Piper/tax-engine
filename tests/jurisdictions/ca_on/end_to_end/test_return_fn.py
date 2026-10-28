"""CA-ON 2025 end to end: return FN, the alternative minimum tax and the investment tax credit.

Return FN is `returns/2025_return_fn.yaml`: a single filer, not resident in Canada throughout 2025
and a deemed resident, with employment income, a capital gain and foreign income, and amounts on
the Form T691 Part 1 lines that no other return sets, so that the minimum tax binds: Part 5 line
11 is 24998.75 and the investment tax credit (Form T2038(IND)) is limited by amount K, not amount
I. The figures are chosen (no CRA example exists) and worked out by hand from the form text, as
the description of the return shows. The tests check the hand figure of each line named below;
the engine's other lines are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_ADDITIONAL_TAXES_FOR_CARRYOVER,
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_CARRYOVER_AVAILABLE_FOR_2026,
    AMT_FEDERAL_SURTAX,
    AMT_MAXIMUM_CARRYOVER_CLAIM,
    AMT_MINIMUM_AMOUNT,
    AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM,
    AMT_NET_MINIMUM_TAX_PAYABLE,
    AMT_PART_5_LINE_11_IS_POSITIVE,
    AMT_PART_6_TAX_WITH_SURTAX,
    AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE,
    AMT_PART_7_FOREIGN_CREDIT_SHARE,
    AMT_PART_8_ADDITIONAL_TAXES,
    AMT_SPECIAL_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LINE_41700,
    INVESTMENT_TAX_CREDIT,
    INVESTMENT_TAX_CREDIT_REFUND,
    ITC_AMOUNT_H,
    ITC_AMOUNT_I,
    ITC_AMOUNT_J,
    ITC_AMOUNT_K,
    ITC_AMOUNT_L,
    ITC_AMOUNT_M,
    ITC_AMOUNT_N,
    ITC_CLAIM_LIMIT,
    ITC_PART_D_AMOUNT_11_APPLIES,
    ITC_PART_E_AMOUNT_17,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_fn() -> Worksheet:
    """Return FN's worksheet: the inputs of `returns/2025_return_fn.yaml`."""
    # The inputs are those of the YAML. An input the file leaves out is blank,
    # so the RRSP inputs that `starting(...)` requires are 0.
    inputs: dict[str, Any] = {
        "employment_income": "310000",
        "t4_cpp_pensionable_earnings_outside_quebec": "300000",
        "t2204_insurable_earnings": "65700",
        "t2204_premiums_deducted": "1077.48",
        "cpp_months": 12,
        "qpp_months": 12,
        "cpp_t4_base_and_first_additional_contributions": "4034.10",
        "cpp_t4_second_additional_contributions": "396.00",
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "other_income": "40000",
        "foreign_investment_income": "20000",
        "share_dispositions": (("600000", "100000", "0"),),
        "union_dues": "1000",
        "total_carrying_charges": "12000",
        "t777_other_expenses": "12000",
        "limited_partnership_losses_of_other_years": "40000",
        "limited_partnership_at_risk_amount": "40000",
        "non_capital_losses_of_other_years": "60000",
        "unapplied_net_capital_losses_2001_to_2024": "30000",
        "net_capital_losses_claimed": "30000",
        "additional_deductions": "20000",
        "exempt_income_deductions": "20000",
        "federal_political_contributions": "400",
        "labour_sponsored_funds_net_cost": "5000",
        "foreign_tax_countries_rows": (("3000", "20000", "20000", "0", "40000", "0"),),
        "amt_non_resident_or_deemed_resident": 1,
        "amt_subject_to_minimum_tax": 1,
        "amt_treaty_exempt_capital_gains": "20000",
        "amt_graduated_rate_estate_capital_gains": "15000",
        "amt_publicly_listed_gifts_total": "30000",
        "amt_publicly_listed_gifts_t1170_line_68231": "10000",
        "t4_security_options_boxes_39_and_91": "60000",
        "t1212_line_1_opening_balance": "40000",
        "t1212_line_2_benefits_no_longer_deferred": "40000",
        "amt_security_option_publicly_listed_gifts": "10000",
        "t4_security_options_boxes_41_and_92": "30000",
        "amt_prospector_or_grubstaker_deduction": "5000",
        "amt_deferred_profit_sharing_plan_deduction": "2000",
        "amt_limited_partnership_difference_election": "25000",
        "amt_non_capital_losses_difference": "15000",
        "amt_net_capital_losses_difference": "8000",
        "amt_non_deductible_interest": "4000",
        "amt_life_insurance_premiums_as_collateral": "1000",
        "amt_financing_expenses": "3000",
        "amt_investment_counsel_fees": "2000",
        "amt_commission_employment_expenses": "3000",
        "amt_legal_and_accounting_expenses": "2000",
        "amt_repayment_of_salary_and_wages": "1500",
        "amt_excess_epsp_amounts": "500",
        "amt_forfeited_salary_deferral_amounts": "400",
        "amt_repayment_of_wage_loss_replacement": "300",
        "amt_section_119_former_resident_credit": "1500",
        "amt_foreign_business_income": "40000",
        "amt_foreign_capital_gains_non_taxable_claim": "50000",
        "amt_investment_tax_credit_claim": "20000",
        "itc_opening_balance": "8000",
        "itc_sred_expenditures": "60000",
        "itc_sred_partnership_allocation": "500",
        "itc_qualified_property": "20000",
        "itc_mineral_exploration_expenditures": "10000",
        "itc_graduated_rate_estate_allocation": "1000",
        "itc_claim": "353.80",
        "itc_carryback_third_previous_year": "500",
        "itc_carryback_second_previous_year": "1500",
        "itc_carryback_first_previous_year": "2000",
        "itc_refund_designation": "7500",
        "resident_in_canada_throughout_2025": 0,
        "aged_18_or_older_at_end_of_2025": 1,
        "unapplied_net_capital_losses_2000": "0",
    }
    return compute(**inputs)


def test_taxable_income_is_316926_and_basic_federal_tax_is_76394_64() -> None:
    # T1 line 26000 is 316926.00: line 23600 593926.00 (620000.00 less 26074.00 of deductions from
    # total income, including the 12000.00 of line 22900) less the deductions from net income of
    # 277000.00, which include the 127000.00 of line 24900 (the total of Form T691 lines 28, 29, 31,
    # 35, 36 and 37: 60000.00 + 20000.00 + 10000.00 + 30000.00 + 5000.00 + 2000.00). Federal tax on
    # it is 79358.81 (5006-R column 5); the non-refundable credits at 14.5% are 2964.17; so line
    # 42900 is 79358.81 - 2964.17 = 76394.64. The 12000.00 deduction lowers taxable income by
    # 12000.00 and the federal tax by 3960.00 (33% x 12000.00).
    worksheet = return_fn()

    assert worksheet.get(TAXABLE_INCOME).value == D("316926.00")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("76394.64")


def test_minimum_amount_on_part_1_line_103_is_111660_27() -> None:
    # Part 1 line 97 is 20.5% x 559231.00 = 114642.36 (half-up); line 98 is 50% x 2964.17 =
    # 1482.09 (half-up); line 102 is 1482.09 + 1500.00 (line 101, section 119) = 2982.09; so line
    # 103 is 114642.36 - 2982.09 = 111660.27.
    worksheet = return_fn()

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("111660.27")


def test_part_5_line_11_minimum_tax_payable_is_24998_75_so_the_minimum_tax_binds() -> None:
    # Part 5 line 3 is 111660.27 - 22000.00 (special foreign tax credit, Part 4 line 11) =
    # 89660.27. Line 6 is 81684.75 - 36669.43 = 45015.32, so line 7 is 89660.27 - 45015.32 =
    # 44644.95. Line 10 is amount I less the Part D claim, 20000.00 - 353.80 = 19646.20, so line 11
    # is 44644.95 - 19646.20 = 24998.75, which is positive.
    worksheet = return_fn()

    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("89660.27")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("24998.75")
    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 1


def test_federal_surtax_on_part_3_line_4_is_36669_43_as_a_deemed_resident() -> None:
    # Part 3 line 2 is 48% x 76394.64 = 36669.4272, half-up 36669.43. There is no Form T2203
    # percentage, and as a deemed resident line 4 is line 2, so the surtax is 36669.43.
    worksheet = return_fn()

    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("36669.43")


def test_part_6_tax_is_143257_20_and_t1_line_41700_is_the_same_figure() -> None:
    # Part 6 line 9 is 48% x 111660.27 = 53596.93 (half-up) and line 12 is 89660.27 + 53596.93 =
    # 143257.20. Line 14 is the federal tax of T1 line 41700, which is the amount because Part 5
    # line 11 is positive.
    worksheet = return_fn()

    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("143257.20")
    assert worksheet.get(FEDERAL_TAX_LINE_41700).value == D("143257.20")


def test_part_7_foreign_credit_share_is_11163_26_and_the_carryover_is_25506_17() -> None:
    # Part 4 line 11 (special foreign tax credit) is 22000.00, so Part 7 line 11 is 22000.00 -
    # 10329.32 = 11670.68, and line 12 is 11670.68 x 22000.00 / 23000.00 = 11163.26. Line 14 is
    # the minimum amount less line 13: 111660.27 - 86154.10 = 25506.17, the additional tax for the
    # carryover. With no earlier carryover it is the whole balance for 2026 (Part 8 line 17).
    worksheet = return_fn()

    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("22000.00")
    assert worksheet.get(AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE).value == D("11670.68")
    assert worksheet.get(AMT_PART_7_FOREIGN_CREDIT_SHARE).value == D("11163.26")
    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("25506.17")
    # Part 5 line 11 is positive, so Part 7 is completed and Part 8 line 14 is its line 14.
    assert worksheet.get(AMT_PART_8_ADDITIONAL_TAXES).value == D("25506.17")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("25506.17")


def test_no_earlier_minimum_tax_carryover_so_t1_line_40427_is_0() -> None:
    # Part 8 line 12 is the lesser of line 1 (0, no carryover from earlier years) and line 11, so
    # both the maximum claim and the claim entered on T1 line 40427 are 0.00.
    worksheet = return_fn()

    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_CLAIM).value == D("0.00")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM).value == D("0.00")


def test_federal_foreign_tax_credit_is_10493_57_from_form_t2209() -> None:
    # Form T2209 line 3 is 3000.00 (the non-business country) and line 11 is 7329.32 (the business
    # country, 76394.64 x 40000.00 / 416926.00 - see the description); their total on line 13 is
    # 10329.32, the federal foreign tax credit on T1 line 40500.
    worksheet = return_fn()

    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("10329.32")


def test_the_claim_limit_is_amount_k_353_80_as_amount_11_applies() -> None:
    # Amount H is 101684.75 (Part D amount 9, 102434.75, less the labour-sponsored credit 750.00).
    # Amount I is the lesser of G (20000.00) and H, 20000.00. Amount J is H + foreign tax credit
    # 10329.32 - minimum amount 111660.27 = 353.80; amount K is the lesser of G and J, 353.80.
    # Part 5 line 7 is positive, so amount 11 applies and the limit is K, not I (T2038(IND) Part D
    # amount 15, "up to, but not more than I or K, whichever applies"). K was 3754.60 before the
    # 12000.00 deduction: amount 13 fell by 5860.80 and the minimum amount by 2460.00.
    worksheet = return_fn()

    assert worksheet.get(ITC_AMOUNT_H).value == D("101684.75")
    assert worksheet.get(ITC_AMOUNT_I).value == D("20000.00")
    assert worksheet.get(ITC_AMOUNT_J).value == D("353.80")
    assert worksheet.get(ITC_AMOUNT_K).value == D("353.80")
    assert worksheet.get(ITC_PART_D_AMOUNT_11_APPLIES).value == 1
    assert worksheet.get(ITC_CLAIM_LIMIT).value == D("353.80")


def test_the_investment_tax_credit_claimed_is_353_80_on_t1_line_41200() -> None:
    # The filer claims 353.80 (amount 15, at most K of 353.80), which is T1 line 41200. The claim
    # was 3000.00 before the 12000.00 deduction; it is cut to K so that the engine accepts it.
    worksheet = return_fn()

    assert worksheet.get(INVESTMENT_TAX_CREDIT).value == D("353.80")


def test_carryback_and_refund_designation_on_t2038_part_e() -> None:
    # Amount 3 is G less the opening balance: 20000.00 - 8000.00 = 12000.00, so amount L is 12000.00
    # (amount 6, K less the opening balance, is 0.00). The filer carries back 500.00, 1500.00 and
    # 2000.00, amount M, 4000.00. Amount 9 is 11500.00 - 1000.00 = 10500.00, which is amount N, and
    # the filer designates 7500.00 (amount 17) as a refund.
    worksheet = return_fn()

    assert worksheet.get(ITC_AMOUNT_L).value == D("12000.00")
    assert worksheet.get(ITC_AMOUNT_M).value == D("4000.00")
    assert worksheet.get(ITC_AMOUNT_N).value == D("10500.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_17).value == D("7500.00")


def test_refund_of_investment_tax_credit_is_3000_on_t1_line_45400() -> None:
    # Amount O is amount 17 times the refundable rate 0.40: 7500.00 x 0.40 = 3000.00, which is T1
    # line 45400, the one credit among lines 150 to 165 that this return has.
    worksheet = return_fn()

    assert worksheet.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("3000.00")


def test_ontario_additional_tax_for_minimum_tax_is_10108_74_on_on428_line_72() -> None:
    # Worksheet ON428 line 1 is 24.63% x 24998.75 = 6157.19 (half-up), line 7 is ON428 line 68,
    # 14620.93, and line 9, the amount for ON428 line 72, is 6157.19 + (18068.96 - 14620.93) =
    # 6157.19 + 3448.03 = 9605.22.
    worksheet = return_fn()

    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("6157.19")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_7).value == D("14620.93")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("9605.22")


def test_no_minimum_tax_carryover_credit_on_on428_line_61540() -> None:
    # ON428 line 60 and line 61540 are the lesser of line 58 and line 59 (the minimum tax carryover
    # times 24.63%, line 59 from T1 line 40427). T1 line 40427 is 0.00 here, so the credit is 0.00.
    worksheet = return_fn()

    assert worksheet.get(ontario.MINIMUM_TAX_CARRYOVER_CREDIT).value == D("0.00")


def test_ontario_tax_is_57841_15_on_t1_line_42800() -> None:
    # ON428 line 83 is 56941.15 (line 81, 57071.59, less the provincial foreign tax credit 130.44);
    # with the Ontario health premium of 900.00 the Ontario tax (T1 line 42800) is 57841.15.
    worksheet = return_fn()

    assert worksheet.get(ontario.ONTARIO_TAX).value == D("57841.15")


def test_refund_or_balance_owing_is_198098_35_the_balance_owing() -> None:
    # Net federal tax (T1 line 42000) is 143257.20 and the Ontario tax (line 42800) is 57841.15, so
    # the total payable (line 43500) is 201098.35. The one credit among lines 150 to 165 is the
    # refund of investment tax credit of 3000.00 (line 45400), so line 167 is 201098.35 - 3000.00 =
    # 198098.35 owing. Against 204706.22 before the 12000.00 deduction, the balance falls by
    # 6607.87 = 3640.80 (line 41700) + 2967.07 (Ontario tax).
    worksheet = return_fn()

    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("198098.35")
