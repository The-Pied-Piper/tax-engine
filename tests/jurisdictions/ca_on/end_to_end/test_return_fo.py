"""CA-ON 2025 end to end: return FO, the minimum tax carryover and the investment tax credit.

Return FO is `returns/2025_return_fo.yaml`: an Ontario resident with employment income of 250000
who is not subject to alternative minimum tax in 2025, and who applies a minimum tax carryover
from earlier years (Form T691 Part 8) and an investment tax credit whose claim is limited by
amount I. The figures are chosen (no CRA example exists) and worked out by hand from the form
text, as the description of the return shows. The tests check the hand figure of each line named
below; the engine's other lines are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_ADDITIONAL_TAXES_FOR_CARRYOVER,
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_CARRYOVER_AVAILABLE_FOR_2026,
    AMT_CARRYOVER_BALANCE,
    AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES,
    AMT_MAXIMUM_CARRYOVER_APPLIED,
    AMT_MAXIMUM_CARRYOVER_CLAIM,
    AMT_MINIMUM_AMOUNT,
    AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS,
    AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM,
    AMT_NET_MINIMUM_TAX_PAYABLE,
    AMT_PART_5_LINE_11_IS_POSITIVE,
    AMT_PART_6_TAX_WITH_SURTAX,
    AMT_UNAPPLIED_2018_CARRYOVER,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LINE_41700,
    INVESTMENT_TAX_CREDIT,
    INVESTMENT_TAX_CREDIT_REFUND,
    ITC_AMOUNT_I,
    ITC_AMOUNT_J,
    ITC_AMOUNT_K,
    ITC_AMOUNT_L,
    ITC_AMOUNT_N,
    ITC_CLAIM_LIMIT,
    ITC_PART_D_AMOUNT_11_APPLIES,
    ITC_PART_E_AMOUNT_6,
    ITC_PART_E_AMOUNT_17,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_fo() -> Worksheet:
    """Return FO's worksheet: the inputs of `returns/2025_return_fo.yaml`."""
    # The inputs are those of the YAML. An input the file leaves out is blank,
    # so the share dispositions are none, the RRSP inputs and union dues are 0, and the federal
    # political contributions are the YAML's `ca/political_contributions`.
    inputs: dict[str, Any] = {
        "employment_income": "250000",
        "t4_cpp_pensionable_earnings_outside_quebec": "250000",
        "t2204_insurable_earnings": "65700",
        "t2204_premiums_deducted": "1077.48",
        "cpp_months": 12,
        "qpp_months": 12,
        "cpp_t4_base_and_first_additional_contributions": "4034.10",
        "cpp_t4_second_additional_contributions": "396.00",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "federal_political_contributions": "1275",
        "labour_sponsored_funds_net_cost": "2000",
        "amt_rental_property_cca_and_carrying_charges": "7000",
        "amt_rental_property_income_before_cca": "2000",
        "amt_minimum_tax_carryover_from_previous_years": "12000",
        "amt_minimum_tax_carryover_applied": "8000",
        "amt_unapplied_2018_carryover": "3000",
        "amt_investment_tax_credit_claim": "10000",
        "itc_opening_balance": "15000",
        "itc_sred_expenditures": "40000",
        "itc_qualified_property": "30000",
        "itc_critical_mineral_expenditures": "20000",
        "itc_graduated_rate_estate_allocation": "2000",
        "itc_claim": "10000",
        "itc_refund_designation": "5000",
        "resident_in_canada_throughout_2025": 1,
        "aged_18_or_older_at_end_of_2025": 1,
        "unapplied_net_capital_losses_2000": "0",
    }
    return compute(**inputs)


def test_taxable_income_is_248926_and_basic_federal_tax_is_46120_45() -> None:
    # T1 line 26000 is 248926.00 (250000.00 less the enhanced CPP deduction of 1074.00). Federal
    # tax on it is 57098.33 (5006-R column 4); the non-refundable credits at 14.5% are 2977.88.
    # The minimum tax carryover claimed on T1 line 40427 is 8000.00, so line 42900 is
    # 57098.33 - 2977.88 - 8000.00 = 46120.45.
    worksheet = return_fo()

    assert worksheet.get(TAXABLE_INCOME).value == D("248926.00")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("46120.45")


def test_minimum_amount_on_part_1_line_103_is_14210_17() -> None:
    # Part 1 line 97 is 20.5% x 76581.00 = 15699.11 (half-up); line 98 is 50% x 2977.88 = 1488.94,
    # and there is no other credit, so line 102 is 1488.94 and line 103 is 15699.11 - 1488.94 =
    # 14210.17.
    worksheet = return_fo()

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("14210.17")


def test_the_filer_is_not_subject_to_minimum_tax_as_part_5_line_11_is_0() -> None:
    # Part 5 line 3 is the minimum amount, 14210.17, as there is no special foreign tax credit.
    # Line 6 (the regular net tax) is 35170.45, and line 7 is 0.00, so line 11 is 0.00, and the
    # form says the filer is not subject to alternative minimum tax.
    worksheet = return_fo()

    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("14210.17")
    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 0
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0.00")


def test_part_6_tax_is_14210_17_but_t1_line_41700_is_the_regular_tax_of_35170_45() -> None:
    # Part 6 is not used, so its line 14 is the minimum amount, 14210.17. That figure enters T1
    # line 41700 only when Part 5 line 11 is positive. Here it is 0, so line 41700 is the regular
    # federal tax, line 134 less line 138: 46120.45 - 10950.00 = 35170.45.
    worksheet = return_fo()

    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("14210.17")
    assert worksheet.get(FEDERAL_TAX_LINE_41700).value == D("35170.45")


def test_the_maximum_carryover_claim_is_12000_and_8000_is_applied_on_t1_line_40427() -> None:
    # Part 8 line 1 is 12000.00 (the carryover from 2018 to 2024). Line 12 is the lesser of line 1
    # and line 11, 12000.00 (the maximum claim). The filer claims 8000.00, which is the amount
    # carried to Part 2 line 6 and entered on T1 line 40427.
    worksheet = return_fo()

    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS).value == D("12000.00")
    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_CLAIM).value == D("12000.00")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM).value == D("8000.00")


def test_the_maximum_carryover_that_can_be_applied_in_2025_is_28960_28() -> None:
    # Part 8 line 11 is line 9 less line 10, 43170.45 - 14210.17 = 28960.28, not below zero.
    worksheet = return_fo()

    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_APPLIED).value == D("28960.28")


def test_the_carryover_balance_is_4000_and_the_total_for_2026_is_1000() -> None:
    # Part 8 line 13 is line 1 less line 12, 12000.00 - 8000.00 = 4000.00. Line 14, the additional
    # taxes for the carryover, is 0.00, so line 15 is 4000.00. Line 17 is line 15 less the unapplied
    # 2018 carryover of 3000.00 (line 16): 1000.00 is available for 2026.
    worksheet = return_fo()

    assert worksheet.get(AMT_CARRYOVER_BALANCE).value == D("4000.00")
    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("0.00")
    assert worksheet.get(AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES).value == D("4000.00")
    assert worksheet.get(AMT_UNAPPLIED_2018_CARRYOVER).value == D("3000.00")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("1000.00")


def test_claim_limit_is_amount_i_28000_as_amount_11_does_not_apply() -> None:
    # Amount G is 30000.00 - 2000.00 (graduated rate estate allocation) = 28000.00. Amount H is
    # 45170.45 and amount I, the lesser of G and H, is 28000.00. Amount J is 30960.28 and amount K
    # is 28000.00, but the filer is not subject to alternative minimum tax, so amount 11 does not
    # apply and the claim is limited by I (T2038(IND) Part D amount 15).
    worksheet = return_fo()

    assert worksheet.get(ITC_AMOUNT_I).value == D("28000.00")
    assert worksheet.get(ITC_AMOUNT_J).value == D("30960.28")
    assert worksheet.get(ITC_AMOUNT_K).value == D("28000.00")
    assert worksheet.get(ITC_PART_D_AMOUNT_11_APPLIES).value == 0
    assert worksheet.get(ITC_CLAIM_LIMIT).value == D("28000.00")


def test_the_investment_tax_credit_claimed_is_10000_on_t1_line_41200() -> None:
    # The filer claims 10000.00 (amount 15, at most I of 28000.00), which is T1 line 41200.
    worksheet = return_fo()

    assert worksheet.get(INVESTMENT_TAX_CREDIT).value == D("10000.00")


def test_part_e_carries_nothing_back_and_designates_a_refund_of_2000_on_t1_line_45400() -> None:
    # Amount 3 is 28000.00 - 15000.00 = 13000.00, and amount 6 is I less the opening balance,
    # 13000.00, so amount L is 0.00 and no carryback is requested. Amount N is 7000.00 and the
    # filer designates 5000.00 (amount 17), so the refund is 5000.00 x 0.40 = 2000.00 (T1 line
    # 45400).
    worksheet = return_fo()

    assert worksheet.get(ITC_PART_E_AMOUNT_6).value == D("13000.00")
    assert worksheet.get(ITC_AMOUNT_L).value == D("0.00")
    assert worksheet.get(ITC_AMOUNT_N).value == D("7000.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_17).value == D("5000.00")
    assert worksheet.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("2000.00")


def test_ontario_additional_tax_for_minimum_tax_is_0_on_on428_line_72() -> None:
    # The filer is not subject to alternative minimum tax: line 1 of Worksheet ON428 is the amount
    # from line 11 of Part 5 of Form T691, 0.00, so line 9, the amount for ON428 line 72, is 0.00.
    worksheet = return_fo()

    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("0.00")


def test_ontario_minimum_tax_carryover_credit_is_1970_40_on_on428_line_61540() -> None:
    # ON428 line 59 is the minimum tax carryover claimed on T1 line 40427 (8000.00) times 24.63%,
    # 1970.40. Line 60 and line 61540 are the lesser of line 58 (23896.64) and line 59, so the
    # credit is 1970.40, and line 61 is 23896.64 - 1970.40 = 21926.24.
    worksheet = return_fo()

    assert worksheet.get(ontario.MINIMUM_TAX_CARRYOVER_CREDIT).value == D("1970.40")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER).value == D("21926.24")


def test_ontario_tax_is_31332_42_on_t1_line_42800() -> None:
    # ON428 line 81 is 30432.42 (no provincial foreign tax credit and no tax reduction), and the
    # Ontario health premium of 900.00 on ON428 line 89 gives line 90 of 31332.42, which is T1 line
    # 42800.
    worksheet = return_fo()

    assert worksheet.get(ontario.ONTARIO_TAX).value == D("31332.42")


def test_refund_or_balance_owing_is_64502_87_the_balance_owing() -> None:
    # The total payable is the net federal tax 35170.45 (T1 line 42000) plus the Ontario tax
    # 31332.42 (line 42800), 66502.87. The one credit among lines 150 to 165 is the refund of
    # investment tax credit of 2000.00 (line 45400), so line 167 is 66502.87 - 2000.00 = 64502.87
    # owing.
    worksheet = return_fo()

    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("64502.87")
