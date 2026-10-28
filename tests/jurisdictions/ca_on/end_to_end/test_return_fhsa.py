"""CA-ON 2025 end to end: return fhsa."""

from __future__ import annotations

import re

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    FHSA_ANNUAL_AMOUNT,
    FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS,
    FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD,
    FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD,
    FHSA_ANNUAL_LIMIT,
    FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD,
    FHSA_ANNUAL_LIMIT_FROM_STEP_2,
    FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
    FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_AVAILABLE,
    FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_LIMIT,
    FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT,
    FHSA_DEDUCTION,
    FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED,
    FHSA_EXCESS_DESIGNATED_WITHDRAWALS,
    FHSA_LIFETIME_LIMIT,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS,
    FHSA_MAXIMUM_DEDUCTION,
    FHSA_NET_RRSP_TRANSFER_AMOUNT,
    FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT,
    FHSA_TOTAL_ANNUAL_LIMITS,
    FHSA_TOTAL_DESIGNATED_TRANSFERS,
    FHSA_TOTAL_RRSP_TRANSFERS,
    FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT,
    FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT,
    FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, step_3


def test_a_first_fhsa_with_8000_contributed_and_deducted_gives_20805_of_8000() -> None:
    # Schedule 15: a first FHSA opened in 2025, 8000 contributed (line 1), no statement figures,
    # all 8000 deducted (line 57). Line 3 is 8000 - 0, line 5 8000 + 0, line 13 8000; line 16 is
    # 8000.00 + 0; line 39 is 8000.00 - 0, so line 40 is the lesser of 8000 and 8000.00, 8000.
    # Step 3: line 43 is 8000 + 0, line 45 8000 - 0, line 48 is 40000.00 - 0 and line 50 the same;
    # line 51 is the lesser of 8000 and 40000.00: 8000. Line 57 is 8000, at most line 51, line
    # 20805; line 56 is 0 + 8000 - 0, so line 58 is 0.
    worksheet = step_3(fhsa_contributions_in_2025="8000", fhsa_contributions_deducted="8000")

    assert worksheet.get(FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL).value == D(
        "8000"
    )
    assert worksheet.get(FHSA_CONTRIBUTIONS_LIMIT).value == D("8000.00")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT).value == D("8000.00")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD).value == D("8000.00")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS).value == D("8000.00")
    assert worksheet.get(FHSA_ANNUAL_LIMIT_FROM_STEP_2).value == D("8000.00")
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("8000.00")
    assert worksheet.get(FHSA_TOTAL_ANNUAL_LIMITS).value == D("8000.00")
    assert worksheet.get(FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS).value == D("8000.00")
    assert worksheet.get(FHSA_LIFETIME_LIMIT).value == D("40000.00")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS).value == D("40000.00")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("8000.00")
    assert worksheet.get(FHSA_CONTRIBUTIONS_AVAILABLE).value == D("8000")
    assert worksheet.get(FHSA_DEDUCTION).value == D("8000")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("0")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("8000")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "fhsa_annual_amount: credit amount 8000 (half-up to 0.01)" in rendered
    assert "fhsa_annual_amount_for_2024: credit amount 8000 (half-up to 0.01)" in rendered
    assert "fhsa_lifetime_limit: credit amount 40000 (half-up to 0.01)" in rendered
    assert (
        "fhsa_annual_limit: fhsa_annual_limit_from_step_2 8000, "
        "chosen as fhsa_maximum_participation_period_ended_checked is 0"
    ) in rendered
    assert (
        "fhsa_maximum_deduction: lesser of fhsa_annual_limits_less_deductions 8000 "
        "and fhsa_lifetime_limit_less_deductions_and_transfers 40000 = 8000"
    ) in rendered
    assert (
        "fhsa_deduction: fhsa_contributions_deducted 8000, at most fhsa_maximum_deduction 8000"
    ) in rendered
    assert (
        "fhsa_unused_contributions_carried_forward: fhsa_contributions_available 8000 "
        "less fhsa_deduction 8000 = 0"
    ) in rendered


def test_a_deduction_below_line_51_carries_the_rest_forward_as_line_58() -> None:
    # Line 57 of 5000 against a line 51 of 8000: line 20805 is 5000, and line 58 "Line 56 minus
    # line 57 Your unused FHSA contributions available to deduct in future years" is 8000 - 5000.
    worksheet = step_3(fhsa_contributions_in_2025="8000", fhsa_contributions_deducted="5000")

    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("8000")
    assert worksheet.get(FHSA_DEDUCTION).value == D("5000")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("3000")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("5000")


def test_a_claim_above_line_51_is_refused_naming_both_kinds() -> None:
    # Line 57 "(cannot be more than the amount on line 51 of the previous page)": 8000.01 against a
    # line 51 of 8000 is an input error, not capped to 8000.
    with pytest.raises(InputAboveBoundError) as raised:
        step_3(fhsa_contributions_in_2025="8000", fhsa_contributions_deducted="8000.01")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/fhsa_contributions_deducted 8000.01 is above ca/fhsa_maximum_deduction 8000"
    )


def test_any_claim_is_refused_when_line_51_is_0() -> None:
    # No contributions and no room: line 51 is 0, so a claim of 1 is above it.
    with pytest.raises(InputAboveBoundError) as raised:
        step_3(fhsa_contributions_deducted="1")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/fhsa_contributions_deducted 1 is above ca/fhsa_maximum_deduction 0"
    )


def test_a_maximum_participation_period_ended_in_a_prior_year_sets_line_40_to_0() -> None:
    # Step 2: "If your maximum participation period (MPP) ended in a prior year, do not complete
    # this step. Your 2025 annual FHSA limit is "0". Enter "0" on line 40 and continue at Step 3."
    # With 8000 contributed Step 2 would give 8000 (the count 0), but with the count 1 line 40 is
    # the printed 0, so lines 43 and 45 are 0 + 0 - 0, line 51 is the lesser of 0 and 40000.00:
    # 0, and 8000 is carried forward (line 58 is 8000 + 0 - 0 - 0).
    worksheet = step_3(
        fhsa_contributions_in_2025="8000",
        fhsa_maximum_participation_period_ended=1,
        fhsa_contributions_deducted="0",
    )

    assert worksheet.get(FHSA_ANNUAL_LIMIT_FROM_STEP_2).value == D("8000")
    assert worksheet.get(FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD).value == D("0")
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("0")
    assert worksheet.get(FHSA_TOTAL_ANNUAL_LIMITS).value == D("0")
    assert worksheet.get(FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS).value == D("0")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("0")
    assert worksheet.get(FHSA_DEDUCTION).value == D("0")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("8000")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "fhsa_annual_limit_after_maximum_participation_period: credit amount 0 (half-up to 0.01)"
    ) in rendered
    assert (
        "fhsa_annual_limit: fhsa_annual_limit_after_maximum_participation_period 0, "
        "chosen as fhsa_maximum_participation_period_ended_checked is 1"
    ) in rendered


def test_a_claim_is_refused_once_the_maximum_participation_period_has_ended() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        step_3(
            fhsa_contributions_in_2025="8000",
            fhsa_maximum_participation_period_ended=1,
            fhsa_contributions_deducted="1000",
        )

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/fhsa_contributions_deducted 1000 is above ca/fhsa_maximum_deduction 0"
    )


def test_a_second_year_adds_the_statements_totals_to_the_new_annual_limit() -> None:
    # An FHSA opened in 2024 with 8000 contributed and deducted that year. The 2025 participation
    # room statement gives line 7 (contributions in 2024) 8000, line 8 (before a first qualifying
    # withdrawal) 8000, line 42 (total annual limits for 2024 and prior years) 8000 and line 44
    # (total deductions for 2024 and prior years) 8000. With 8000 contributed in 2025 the annual
    # limit (line 40) is 8000, line 43 is 8000 + 8000 = 16000, line 45 16000 - 8000 = 8000, line
    # 48 is 40000.00 - 8000 = 32000.00 and line 51 the lesser of 8000 and 32000.00: 8000.
    worksheet = step_3(
        fhsa_contributions_in_2025="8000",
        fhsa_contributions_in_2024="8000",
        fhsa_contributions_in_2024_before_first_qualifying_withdrawal="8000",
        fhsa_annual_limits_for_2024_and_prior_years="8000",
        fhsa_deductions_for_2024_and_prior_years="8000",
        fhsa_contributions_deducted="8000",
    )

    assert worksheet.get(FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL).value == D(
        "0"
    )
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("8000")
    assert worksheet.get(FHSA_TOTAL_ANNUAL_LIMITS).value == D("16000")
    assert worksheet.get(FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS).value == D("8000")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS).value == D("32000")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("8000")
    assert worksheet.get(FHSA_DEDUCTION).value == D("8000")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("0")


def test_an_rrsp_transfer_in_2025_lowers_the_annual_limit_and_the_lifetime_room() -> None:
    # Line 18 (transfers from RRSPs to FHSAs in 2025) of 3000: lines 19 and 23 are 3000; line 36
    # is line 24 (3000) less line 35 (0); line 39 is 8000.00 - 3000 = 5000.00, so line 40, the
    # lesser of line 13 (8000) and 5000.00, is 5000.00. Line 50 is 40000.00 - 0 - 3000 =
    # 37000.00, so line 51 is the lesser of 5000.00 and 37000.00: 5000.00. A deduction of 5000
    # leaves 8000 - 5000 = 3000 as line 58.
    worksheet = step_3(
        fhsa_contributions_in_2025="8000",
        fhsa_rrsp_transfers_in_2025="3000",
        fhsa_contributions_deducted="5000",
    )

    assert worksheet.get(FHSA_TOTAL_RRSP_TRANSFERS).value == D("3000")
    assert worksheet.get(FHSA_NET_RRSP_TRANSFER_AMOUNT).value == D("3000")
    assert worksheet.get(FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS).value == D("3000")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS).value == D("5000")
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("5000")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS).value == D("37000")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("5000")
    assert worksheet.get(FHSA_DEDUCTION).value == D("5000")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("3000")
    with pytest.raises(InputAboveBoundError):
        step_3(
            fhsa_contributions_in_2025="8000",
            fhsa_rrsp_transfers_in_2025="3000",
            fhsa_contributions_deducted="5000.01",
        )


def test_a_designated_withdrawal_lowers_line_13_and_comes_off_line_56() -> None:
    # Line 6 (designated withdrawals in 2025) of 1000 against contributions after a first
    # qualifying withdrawal (line 11) of 0: line 12 is 1000, line 13 is 8000 - 1000 = 7000, so
    # line 40 is 7000 and line 51 7000; line 56 is 0 + 8000 - 1000 = 7000, and a deduction of
    # 7000 leaves 0 as line 58.
    worksheet = step_3(
        fhsa_contributions_in_2025="8000",
        fhsa_designated_withdrawals_in_2025="1000",
        fhsa_contributions_deducted="7000",
    )

    assert worksheet.get(FHSA_EXCESS_DESIGNATED_WITHDRAWALS).value == D("1000")
    assert worksheet.get(FHSA_CONTRIBUTIONS_LIMIT).value == D("7000")
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("7000")
    assert worksheet.get(FHSA_CONTRIBUTIONS_AVAILABLE).value == D("7000")
    assert worksheet.get(FHSA_DEDUCTION).value == D("7000")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("0")


def test_contributions_after_a_first_qualifying_withdrawal_count_against_the_withdrawals() -> None:
    # Lines 1 and 2: 8000 contributed in 2025, of which 600 after the first qualifying withdrawal,
    # so line 3 is 7400; designated withdrawals (line 6) of 1000 less line 11 (0 for 2024 + 600
    # after the withdrawal in 2025) is line 12, 400, and line 13 is 7400 - 400 = 7000.
    worksheet = step_3(
        fhsa_contributions_in_2025="8000",
        fhsa_contributions_in_2025_after_first_qualifying_withdrawal="600",
        fhsa_designated_withdrawals_in_2025="1000",
    )

    assert worksheet.get(FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL).value == D(
        "7400"
    )
    assert worksheet.get(FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL).value == D("600")
    assert worksheet.get(FHSA_EXCESS_DESIGNATED_WITHDRAWALS).value == D("400")
    assert worksheet.get(FHSA_CONTRIBUTIONS_LIMIT).value == D("7000")


def test_line_2_above_line_1_is_refused_so_line_3_is_never_negative() -> None:
    # Schedule 15 line 2 is the part of line 1 made after the first qualifying withdrawal, so 500
    # above line 1 of 100 is an input error, not a negative line 3 "Line 1 minus line 2 =" carried
    # into line 5 and line 13.
    with pytest.raises(InputAboveBoundError) as raised:
        step_3(
            fhsa_contributions_in_2025="100",
            fhsa_contributions_in_2025_after_first_qualifying_withdrawal="500",
        )

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal 500 is above "
        "ca/fhsa_contributions_in_2025 100"
    )


def test_the_statements_carryforwards_and_variables_each_enter_their_line_once() -> None:
    # One distinct figure for each statement figure, so a figure left out or added twice changes
    # the result: line 4 ("B") 1, line 15 (carryforward for 2025) 10, line 17 100, line 20 1000,
    # line 28 ("H") 5, line 31 (carryforward for 2024) 20 and line 34 ("F") 50. Line 3 is 0, so
    # line 5 is 0 + 1 = 1 and line 13 is 1. Line 16 is 8000.00 + 10 = 8010.00. Line 19 is 100 + 0
    # and line 22 is 1000 + 0, so line 23 (and line 24) is 100 - 1000 = -900, and line 27 (line 25
    # minus line 26) is 100 - 1000 = -900 too; line 29 is -900 - 5 floored at 0, line 32 is
    # 8000.00 + 20 = 8020.00, line 33 is the lesser of 0 and 8020.00, 0, line 35 is 0 + 50 = 50 and
    # line 36 is -900 - 50 = -950. Line 39 is 8010.00 - (-950) = 8960.00 and line 40 the lesser of
    # line 13 (1) and 8960.00: 1.
    worksheet = step_3(
        fhsa_variable_b_amount="1",
        fhsa_carryforward_for_2025="10",
        fhsa_rrsp_transfers_in_2024_and_prior_years="100",
        fhsa_designated_transfers_in_2024_and_prior_years="1000",
        fhsa_variable_h_amount="5",
        fhsa_carryforward_for_2024="20",
        fhsa_variable_f_amount="50",
    )

    assert worksheet.get(FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT).value == D("1")
    assert worksheet.get(FHSA_CONTRIBUTIONS_LIMIT).value == D("1")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD).value == D("8010")
    assert worksheet.get(FHSA_TOTAL_RRSP_TRANSFERS).value == D("100")
    assert worksheet.get(FHSA_TOTAL_DESIGNATED_TRANSFERS).value == D("1000")
    assert worksheet.get(FHSA_NET_RRSP_TRANSFER_AMOUNT).value == D("-900")
    assert worksheet.get(FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS).value == D("-900")
    assert worksheet.get(FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT).value == D("0")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD).value == D("8020")
    assert worksheet.get(FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT).value == D("0")
    assert worksheet.get(FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT).value == D("50")
    assert worksheet.get(FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS).value == D("-950")
    assert worksheet.get(FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS).value == D("8960")
    assert worksheet.get(FHSA_ANNUAL_LIMIT).value == D("1")


def test_the_unused_contributions_from_the_statement_add_to_line_56() -> None:
    # Line 52 (unused contributions available to deduct, from the statement) of 2500 and 8000
    # contributed in 2025: line 54 is 2500 + 8000 = 10500 and line 56 is 10500 - 0. The annual
    # limit is 8000, so line 51 is 8000 and 8000 is deducted: line 58 is 10500 - 8000 = 2500.
    worksheet = step_3(
        fhsa_contributions_in_2025="8000",
        fhsa_unused_contributions_brought_forward="2500",
        fhsa_contributions_deducted="8000",
    )

    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS).value == D("10500")
    assert worksheet.get(FHSA_CONTRIBUTIONS_AVAILABLE).value == D("10500")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("8000")
    assert worksheet.get(FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD).value == D("2500")


def test_the_lifetime_limit_caps_the_maximum_deduction() -> None:
    # Total deductions for 2024 and prior years (line 44) of 38000 and total annual limits (line
    # 42) of 38000: line 45 is 8000 + 38000 - 38000 = 8000 but line 48 is 40000.00 - 38000 =
    # 2000.00, so line 51 is the lesser of 8000 and 2000.00: 2000.00.
    worksheet = step_3(
        fhsa_contributions_in_2025="8000",
        fhsa_annual_limits_for_2024_and_prior_years="38000",
        fhsa_deductions_for_2024_and_prior_years="38000",
    )

    assert worksheet.get(FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS).value == D("8000")
    assert worksheet.get(FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS).value == D("2000")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("2000")


def test_line_2_equal_to_line_1_is_accepted_and_the_maximum_deduction_is_8000() -> None:
    # Schedule 15 line 1 and line 2 are both 2000, so the checked line 2 is 2000 and line 3 is
    # 2000 - 2000 = 0. Line 5 is 0 + the variable "B" amount of 8000, so line 13 is 8000 and line
    # 41 is 8000 too; line 45 is 8000 and line 51, the lesser of line 45 and line 50 (40000.00), is
    # the maximum FHSA deduction of 8000.
    worksheet = step_3(
        fhsa_contributions_in_2025="2000",
        fhsa_contributions_in_2025_after_first_qualifying_withdrawal="2000",
        fhsa_variable_b_amount="8000",
    )

    assert worksheet.get(
        FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED
    ).value == D("2000")
    assert worksheet.get(FHSA_MAXIMUM_DEDUCTION).value == D("8000")


def test_line_8_equal_to_line_7_is_accepted_and_line_9_is_0() -> None:
    # Schedule 15 line 7 and line 8 are both 1000, so the checked line 8 is 1000 and line 9
    # "Line 7 minus line 8 =" is 1000 - 1000 = 0.
    worksheet = step_3(
        fhsa_contributions_in_2024="1000",
        fhsa_contributions_in_2024_before_first_qualifying_withdrawal="1000",
    )

    assert worksheet.get(
        FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED
    ).value == D("1000")
    assert worksheet.get(FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL).value == D(
        "0"
    )


def test_line_44_equal_to_line_42_is_accepted_and_line_45_is_0() -> None:
    # Schedule 15 line 42 and line 44 are both 8000 (the reading that deductions are made against
    # the limits of 2024 and prior years, which the form prints no number for): the checked line 44
    # is 8000, and line 45 "Line 43 minus line 44 =" is (0 + 8000) - 8000 = 0.
    worksheet = step_3(
        fhsa_annual_limits_for_2024_and_prior_years="8000",
        fhsa_deductions_for_2024_and_prior_years="8000",
    )

    assert worksheet.get(FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED).value == D("8000")
    assert worksheet.get(FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS).value == D("0")


@pytest.mark.parametrize(
    ("amount_field", "amount", "bound_field", "bound"),
    [
        # Line 2 one cent above line 1, and the 9000 of the example above line 1 of 2000.
        (
            "fhsa_contributions_in_2025_after_first_qualifying_withdrawal",
            "2000.01",
            "fhsa_contributions_in_2025",
            "2000",
        ),
        (
            "fhsa_contributions_in_2025_after_first_qualifying_withdrawal",
            "9000",
            "fhsa_contributions_in_2025",
            "2000",
        ),
        # Line 8 one cent above line 7.
        (
            "fhsa_contributions_in_2024_before_first_qualifying_withdrawal",
            "1000.01",
            "fhsa_contributions_in_2024",
            "1000",
        ),
        (
            "fhsa_contributions_in_2024_before_first_qualifying_withdrawal",
            "9000",
            "fhsa_contributions_in_2024",
            "1000",
        ),
        # Line 44 one cent above line 42, and 20000 above line 42 of 8000.
        (
            "fhsa_deductions_for_2024_and_prior_years",
            "8000.01",
            "fhsa_annual_limits_for_2024_and_prior_years",
            "8000",
        ),
        (
            "fhsa_deductions_for_2024_and_prior_years",
            "20000",
            "fhsa_annual_limits_for_2024_and_prior_years",
            "8000",
        ),
    ],
)
def test_a_part_above_its_whole_is_refused_not_capped(
    amount_field: str, amount: str, bound_field: str, bound: str
) -> None:
    # Schedule 15 line 2 is a part of line 1, line 8 of line 7 and line 44 is made against line 42:
    # an amount above its whole is an input error (not capped), so it does not reach line 3, 9 or
    # 45, and the message names the input that is wrong.
    message = f"ca/{amount_field} {amount} is above ca/{bound_field} {bound}"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        step_3(**{amount_field: amount, bound_field: bound})
