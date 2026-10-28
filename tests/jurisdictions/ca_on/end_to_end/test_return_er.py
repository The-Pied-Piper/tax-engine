"""CA-ON 2025 end to end: return ER, the FHSA chain of Schedule 15 with the maximum participation
period NOT ended.

Return ER is `returns/2025_return_er.yaml`: every comparison of Steps 2 and 3 takes its first (own)
branch, so each line the return reaches is non-zero. The figures are chosen and worked out by hand
from the form text, as no CRA example exists for Schedule 15. The tests check the hand figure of
each line; the tax figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD,
    FHSA_ANNUAL_LIMIT,
    FHSA_ANNUAL_LIMIT_FROM_STEP_2,
    FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
    FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_AVAILABLE,
    FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_LIMIT,
    FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT,
    FHSA_DEDUCTION,
    FHSA_EXCESS_DESIGNATED_WITHDRAWALS,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS,
    FHSA_MAXIMUM_DEDUCTION,
    FHSA_NET_RRSP_TRANSFER_AMOUNT,
    FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS,
    FHSA_TOTAL_ANNUAL_LIMITS,
    FHSA_TOTAL_DESIGNATED_TRANSFERS,
    FHSA_TOTAL_RRSP_TRANSFERS,
    FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT,
    FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT,
    FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS,
    NET_INCOME,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_er() -> Worksheet:
    """The worksheet of return ER: the inputs of `returns/2025_return_er.yaml`, MPP not ended."""
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="60000",
        fhsa_income="700",
        other_fhsa_income="300",
        fhsa_contributions_in_2025="6000",
        fhsa_contributions_in_2025_after_first_qualifying_withdrawal="1000",
        fhsa_variable_b_amount="500",
        fhsa_designated_withdrawals_in_2025="1800",
        fhsa_contributions_in_2024="4000",
        fhsa_contributions_in_2024_before_first_qualifying_withdrawal="3500",
        fhsa_carryforward_for_2025="2000",
        fhsa_rrsp_transfers_in_2024_and_prior_years="3000",
        fhsa_rrsp_transfers_in_2025="1500",
        fhsa_designated_transfers_in_2024_and_prior_years="500",
        fhsa_designated_transfers_in_2025="400",
        fhsa_variable_h_amount="800",
        fhsa_carryforward_for_2024="1000",
        fhsa_variable_f_amount="300",
        fhsa_annual_limits_for_2024_and_prior_years="9000",
        fhsa_deductions_for_2024_and_prior_years="6000",
        fhsa_unused_contributions_brought_forward="2500",
        fhsa_contributions_deducted="5000",
        fhsa_maximum_participation_period_ended=0,
    )


def test_lines_3_to_23_take_the_contributions_and_the_rrsp_transfers_to_3600() -> None:
    # Line 3: 6,000 - 1,000 = 5,000; line 5: 5,000 + 500 = 5,500; line 9: 4,000 - 3,500 = 500;
    # line 11: 500 + 1,000 = 1,500; line 12: 1,800 - 1,500 = 300 (positive, not floored); line 13:
    # 5,500 - 300 = 5,200; line 16: 8,000 + 2,000 = 10,000; line 19: 3,000 + 1,500 = 4,500; line 22:
    # 500 + 400 = 900; line 23: 4,500 - 900 = 3,600.
    worksheet = return_er()

    assert worksheet.get(FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL).value == D(
        "5000.00"
    )
    assert worksheet.get(FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT).value == D("5500.00")
    assert worksheet.get(FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL).value == D("1500.00")
    assert worksheet.get(FHSA_EXCESS_DESIGNATED_WITHDRAWALS).value == D("300.00")
    assert worksheet.get(FHSA_CONTRIBUTIONS_LIMIT).value == D("5200.00")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD).value == D("10000.00")
    assert worksheet.get(FHSA_TOTAL_RRSP_TRANSFERS).value == D("4500.00")
    assert worksheet.get(FHSA_TOTAL_DESIGNATED_TRANSFERS).value == D("900.00")
    assert worksheet.get(FHSA_NET_RRSP_TRANSFER_AMOUNT).value == D("3600.00")


def test_step_2_takes_the_first_branch_of_each_comparison_to_a_limit_of_5200() -> None:
    # Line 27: 3,000 - 500 = 2,500; line 29: 2,500 - 800 = 1,700; line 33: the lesser of 1,700 and
    # 9,000 (line 32: 8,000 + 1,000) is 1,700; line 35: 1,700 + 300 = 2,000; line 36:
    # 3,600 - 2,000 = 1,600; line 39: 10,000 - 1,600 = 8,400; line 40: the lesser of line 13
    # (5,200) and line 39 (8,400) is 5,200, and the MPP not ended keeps it as line 41.
    worksheet = return_er()

    assert worksheet.get(FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS).value == D(
        "2500.00"
    )
    assert worksheet.get(FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS).value == D("1600.00")
    assert worksheet.get(FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT).value == D("1700.00")
    assert worksheet.get(FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT).value == D("2000.00")
    assert worksheet.get(FHSA_ANNUAL_LIMIT_FROM_STEP_2).value == D("5200.00")
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("5200.00")


def test_step_3_gives_a_maximum_deduction_of_8200_below_the_lifetime_limit() -> None:
    # Line 43: 5,200 + 9,000 = 14,200; line 45: 14,200 - 6,000 = 8,200; line 48: 40,000 - 6,000 =
    # 34,000; line 50: 34,000 - 3,600 = 30,400; line 51: the lesser of 8,200 and 30,400 is 8,200.
    worksheet = return_er()

    assert worksheet.get(FHSA_TOTAL_ANNUAL_LIMITS).value == D("14200.00")
    assert worksheet.get(FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS).value == D("8200.00")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS).value == D("34000.00")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS).value == D("30400.00")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("8200.00")


def test_the_deduction_of_5000_is_carried_forward_as_2200_and_the_income_is_56000() -> None:
    # Line 54: 2,500 + 5,000 = 7,500; line 56: 7,500 - 300 = 7,200; line 57: 5,000 is at most line
    # 51 (8,200), the FHSA deduction on line 20805; line 58: 7,200 - 5,000 = 2,200. Total income is
    # 60,000 + 700 + 300 = 61,000; net and taxable income are 61,000 - 5,000 = 56,000.
    worksheet = return_er()

    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS).value == D("7500.00")
    assert worksheet.get(FHSA_CONTRIBUTIONS_AVAILABLE).value == D("7200.00")
    assert worksheet.get(FHSA_DEDUCTION).value == D("5000.00")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("2200.00")
    assert worksheet.get(TOTAL_INCOME).value == D("61000.00")
    assert worksheet.get(NET_INCOME).value == D("56000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("56000.00")
