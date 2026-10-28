"""CA-ON 2025 end to end: return ES, the FHSA chain of Schedule 15 with the maximum participation
period ENDED.

Return ES is `returns/2025_return_es.yaml`: Step 2 is not completed, so line 40 and line 41 are the
printed 0, and each comparison of Step 3 takes its other branch. The excess designated withdrawals
floor at 0. The figures are chosen and worked out by hand from the form text, as no CRA example
exists for Schedule 15. The tests check the hand figure of each line; the tax figures are the
engine's and are checked in the YAML only.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS,
    FHSA_ANNUAL_LIMIT,
    FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD,
    FHSA_ANNUAL_LIMIT_FROM_STEP_2,
    FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
    FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_AVAILABLE,
    FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
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
    FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT,
    FHSA_TOTAL_ANNUAL_LIMITS,
    FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT,
    FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT,
    FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS,
    NET_INCOME,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_es() -> Worksheet:
    """The worksheet of return ES: the inputs of `returns/2025_return_es.yaml`, MPP ended."""
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="50000",
        fhsa_income="0",
        fhsa_contributions_in_2025="5000",
        fhsa_contributions_in_2025_after_first_qualifying_withdrawal="800",
        fhsa_variable_b_amount="700",
        fhsa_designated_withdrawals_in_2025="400",
        fhsa_contributions_in_2024="3000",
        fhsa_contributions_in_2024_before_first_qualifying_withdrawal="2800",
        fhsa_carryforward_for_2025="2000",
        fhsa_rrsp_transfers_in_2024_and_prior_years="20000",
        fhsa_rrsp_transfers_in_2025="1000",
        fhsa_designated_transfers_in_2024_and_prior_years="2000",
        fhsa_designated_transfers_in_2025="500",
        fhsa_variable_h_amount="3000",
        fhsa_carryforward_for_2024="500",
        fhsa_variable_f_amount="1500",
        fhsa_annual_limits_for_2024_and_prior_years="24000",
        fhsa_deductions_for_2024_and_prior_years="10000",
        fhsa_unused_contributions_brought_forward="2800",
        fhsa_contributions_deducted="6000",
        fhsa_maximum_participation_period_ended=1,
    )


def test_line_12_is_floored_at_0_so_line_13_is_the_full_4900() -> None:
    # Line 3: 5,000 - 800 = 4,200; line 5: 4,200 + 700 = 4,900; line 9: 3,000 - 2,800 = 200;
    # line 11: 200 + 800 = 1,000; line 12: 400 - 1,000 is negative, so 0 (the floor); line 13:
    # 4,900 - 0 = 4,900.
    worksheet = return_es()

    assert worksheet.get(FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL).value == D(
        "4200.00"
    )
    assert worksheet.get(FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT).value == D("4900.00")
    assert worksheet.get(FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL).value == D(
        "200.00"
    )
    assert worksheet.get(FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL).value == D("1000.00")
    assert worksheet.get(FHSA_EXCESS_DESIGNATED_WITHDRAWALS).value == D("0.00")
    assert worksheet.get(FHSA_CONTRIBUTIONS_LIMIT).value == D("4900.00")


def test_the_mpp_ended_prints_0_on_line_40_though_step_2_gives_1500() -> None:
    # The Step 2 introduction says "If your maximum participation period (MPP) ended in a prior
    # year, do not complete this step ... Enter "0" on line 40". The Step 2 result is still
    # computed by the engine as 1,500 (line 39: 10,000 - 8,500; the lesser of 4,900 and 1,500 is
    # 1,500), but line 40 and line 41 are the printed 0.
    worksheet = return_es()

    assert worksheet.get(FHSA_ANNUAL_LIMIT_FROM_STEP_2).value == D("1500.00")
    assert worksheet.get(FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD).value == D("0.00")
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("0.00")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS).value == D("1500.00")


def test_step_3_takes_the_other_branch_of_each_comparison_to_a_maximum_deduction_of_11500() -> None:
    # Line 27: 20,000 - 2,000 = 18,000; line 29: 18,000 - 3,000 = 15,000; line 33: the lesser of
    # 15,000 and line 32 (8,000 + 500 = 8,500) is 8,500; line 35: 8,500 + 1,500 = 10,000; line 36:
    # 18,500 - 10,000 = 8,500. Line 43: 0 + 24,000 = 24,000; line 45: 24,000 - 10,000 = 14,000; line
    # 48: 40,000 - 10,000 = 30,000; line 50: 30,000 - 18,500 = 11,500; line 51: the lesser of 14,000
    # and 11,500 is 11,500 (the second branch).
    worksheet = return_es()

    assert worksheet.get(FHSA_NET_RRSP_TRANSFER_AMOUNT).value == D("18500.00")
    assert worksheet.get(FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS).value == D(
        "18000.00"
    )
    assert worksheet.get(FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT).value == D("15000.00")
    assert worksheet.get(FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT).value == D("8500.00")
    assert worksheet.get(FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT).value == D("10000.00")
    assert worksheet.get(FHSA_TOTAL_ANNUAL_LIMITS).value == D("24000.00")
    assert worksheet.get(FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS).value == D("14000.00")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS).value == D("30000.00")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS).value == D("11500.00")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("11500.00")


def test_the_deduction_of_6000_is_carried_forward_as_1000_and_the_income_is_44000() -> None:
    # Line 54: 2,800 + 4,200 = 7,000; line 55: 0; line 56: 7,000; line 57: 6,000 is at most line 51
    # (11,500), the FHSA deduction on line 20805; line 58: 7,000 - 6,000 = 1,000. Total income is
    # 50,000 (no FHSA income); net and taxable income are 50,000 - 6,000 = 44,000.
    worksheet = return_es()

    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS).value == D("7000.00")
    assert worksheet.get(FHSA_CONTRIBUTIONS_AVAILABLE).value == D("7000.00")
    assert worksheet.get(FHSA_DEDUCTION).value == D("6000.00")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("1000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("50000.00")
    assert worksheet.get(NET_INCOME).value == D("44000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("44000.00")
