"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.catalog import (
    FHSA_ANNUAL_AMOUNT,
    FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS,
    FHSA_ANNUAL_AMOUNT_FOR_2024,
    FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD,
    FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD,
    FHSA_ANNUAL_LIMIT,
    FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD,
    FHSA_ANNUAL_LIMIT_FROM_STEP_2,
    FHSA_ANNUAL_LIMITS_FOR_2024_AND_PRIOR_YEARS,
    FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
    FHSA_CARRYFORWARD_FOR_2024,
    FHSA_CARRYFORWARD_FOR_2025,
    FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_AVAILABLE,
    FHSA_CONTRIBUTIONS_DEDUCTED,
    FHSA_CONTRIBUTIONS_IN_2024,
    FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_LIMIT,
    FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT,
    FHSA_DEDUCTION,
    FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS,
    FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED,
    FHSA_DESIGNATED_TRANSFERS_IN_2024_AND_PRIOR_YEARS,
    FHSA_DESIGNATED_TRANSFERS_IN_2025,
    FHSA_DESIGNATED_WITHDRAWALS_IN_2025,
    FHSA_EXCESS_DESIGNATED_WITHDRAWALS,
    FHSA_LIFETIME_LIMIT,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS,
    FHSA_MAXIMUM_DEDUCTION,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED,
    FHSA_NET_RRSP_TRANSFER_AMOUNT,
    FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT,
    FHSA_RRSP_TRANSFERS_IN_2024_AND_PRIOR_YEARS,
    FHSA_RRSP_TRANSFERS_IN_2025,
    FHSA_TOTAL_ANNUAL_LIMITS,
    FHSA_TOTAL_DESIGNATED_TRANSFERS,
    FHSA_TOTAL_RRSP_TRANSFERS,
    FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT,
    FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT,
    FHSA_UNUSED_CONTRIBUTIONS_BROUGHT_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS,
    FHSA_VARIABLE_B_AMOUNT,
    FHSA_VARIABLE_F_AMOUNT,
    FHSA_VARIABLE_H_AMOUNT,
    RRSP_AMOUNT_DEDUCTED,
    RRSP_CONTRIBUTIONS,
    RRSP_CONTRIBUTIONS_AVAILABLE,
    RRSP_DEDUCTION,
    RRSP_DEDUCTION_LIMIT,
    RRSP_DEDUCTION_MAXIMUM,
    UNUSED_RRSP_CONTRIBUTIONS,
    UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD,
)

INPUTS = frozenset(
    {
        "ca/unused_rrsp_contributions",
        "ca/rrsp_contributions",
        "ca/rrsp_deduction_limit",
        "ca/rrsp_amount_deducted",
        "ca/rpp_deduction",
        "ca/fhsa_contributions_in_2025",
        "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal",
        "ca/fhsa_variable_b_amount",
        "ca/fhsa_designated_withdrawals_in_2025",
        "ca/fhsa_contributions_in_2024",
        "ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal",
        "ca/fhsa_carryforward_for_2025",
        "ca/fhsa_rrsp_transfers_in_2024_and_prior_years",
        "ca/fhsa_rrsp_transfers_in_2025",
        "ca/fhsa_designated_transfers_in_2024_and_prior_years",
        "ca/fhsa_designated_transfers_in_2025",
        "ca/fhsa_variable_h_amount",
        "ca/fhsa_carryforward_for_2024",
        "ca/fhsa_variable_f_amount",
        "ca/fhsa_annual_limits_for_2024_and_prior_years",
        "ca/fhsa_deductions_for_2024_and_prior_years",
        "ca/fhsa_unused_contributions_brought_forward",
        "ca/fhsa_contributions_deducted",
        "ca/fhsa_maximum_participation_period_ended",
        # T1 line 20600 "Line 20600: Pension adjustment (box 52 of all T4 slips and box 034 of all
        # T4A slips)", Schedule 15 line 68930 "Line 68930: Tick this box if you opened your first
        # FHSA in 2025 or became a successor holder in 2025 and did not open another FHSA of your
        # own in 2025 or a prior year.", line 59 and line 68960 "Line 59 and line 68960: Total
        # amount of qualifying withdrawals made in 2025 (box 20 of your 2025 T4FHSA slips)" and line
        # 68965 "Line 68965: Tick this box if the address on page 1 of your return is the same as
        # the address of the home that you bought or built under the FHSA.": the form computes
        # nothing from them, so each is also an output.
        "ca/pension_adjustment",
        "ca/fhsa_first_opened_in_year",
        "ca/fhsa_qualifying_withdrawals",
        "ca/fhsa_home_address_same",
    }
)

OUTPUTS = frozenset(
    {
        "ca/unused_rrsp_contributions_carried_forward",
        "ca/fhsa_unused_contributions_carried_forward",
        "ca/pension_adjustment",
        "ca/fhsa_first_opened_in_year",
        "ca/fhsa_qualifying_withdrawals",
        "ca/fhsa_home_address_same",
    }
)

STEPS = {
    # Schedule 7 line 5 "Line 1 plus line 4 ... Total contributions", line 6 "Total
    # contributions from line 5" and line 10 "Line 6 minus line 9 Contributions available to
    # deduct": with no HBP or LLP repayments (line 9), line 10 is line 5. In line 5's order:
    # the unused contributions (line 1), then the contributions (line 4).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/unused_rrsp_contributions", "ca/rrsp_contributions")},
        produces={"output": "ca/rrsp_contributions_available"},
    ),
    # Schedule 7 line 17 "Enter whichever is less: amount from line 13 or line 16.": with no
    # employer PRPP contributions (line 12) and no transfers (line 15), line 13 is the limit
    # and line 16 the contributions available to deduct. The parts keep line 20's order (line
    # 10, then the limit).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/rrsp_contributions_available", "ca/rrsp_deduction_limit")},
        produces={"output": "ca/rrsp_deduction_maximum"},
    ),
    # Schedule 7 line 18 "Enter your RRSP, PRPP, or SPP contributions you are deducting for
    # 2025 (cannot be more than the amount on line 17).", line 19 "Line 15 plus line 18" and
    # line 20 "Enter whichever is less: amount from line 10 or line 19. Enter this amount on
    # line 20800 of your return. RRSP deduction": with no transfers (line 15), line 19 is
    # line 18, at most line 17 and so at most line 10, and line 20 is line 18 itself. A
    # claim above line 17 is refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/rrsp_amount_deducted", "bound": "ca/rrsp_deduction_maximum"},
        produces={"output": "ca/rrsp_deduction"},
    ),
    # Schedule 7 line 23 "Line 21 minus line 22 Your unused contributions available to carry
    # forward to a future year": line 21 "Enter your contributions available to deduct from
    # line 10 of the previous page." less line 22 "Enter your RRSP deduction from line 20 of
    # the previous page."; never negative, as line 20 is at most line 10.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/rrsp_contributions_available", "less": "ca/rrsp_deduction"},
        produces={"output": "ca/unused_rrsp_contributions_carried_forward"},
    ),
    # Schedule 15 line 2 "Total contributions made to your FHSAs in 2025 after your first qualifying
    # withdrawal" is the part of line 1 "Total contributions made to your FHSAs in 2025" made after
    # the first qualifying withdrawal, so it is at most line 1: a line 2 above line 1 is an input
    # error, not capped, and the checked amount is the one that line 3 and line 11 read.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal",
            "bound": "ca/fhsa_contributions_in_2025",
        },
        produces={
            "output": "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked"
        },
    ),
    # Schedule 15 (form 5000-S15) Step 2 "Calculate your annual FHSA limit for 2025": line 1 and
    # line 68935 "Total contributions made to your FHSAs in 2025 (box 18 of your 2025 T4FHSA
    # slips)" and line 2 and line 68940 "Total contributions made to your FHSAs in 2025 after
    # your first qualifying withdrawal" are starting amounts; line 3 "Line 1 minus line 2 ="
    # prints no "(if negative, enter "0")", so it may be negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2025",
            "less": "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked",
        },
        produces={"output": "ca/fhsa_contributions_in_2025_before_first_qualifying_withdrawal"},
    ),
    # Line 4 "Variable "B" amount of your annual FHSA limit for 2024 (from your 2025 FHSA
    # participation room statement)" is a starting amount; line 5 "Line 3 plus line 4 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_contributions_in_2025_before_first_qualifying_withdrawal",
                "ca/fhsa_variable_b_amount",
            )
        },
        produces={"output": "ca/fhsa_contributions_plus_variable_b_amount"},
    ),
    # Schedule 15 line 8 "Contributions to your FHSAs in 2024 before your first qualifying
    # withdrawal" is the part of line 7 "Total contributions made to your FHSAs in 2024" made
    # before the first qualifying withdrawal, so it is at most line 7: a line 8 above line 7 is an
    # input error, not capped, and line 9 reads the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal",
            "bound": "ca/fhsa_contributions_in_2024",
        },
        produces={
            "output": "ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal_checked"
        },
    ),
    # Line 6 and line 68945 "Total designated withdrawals from your FHSAs in 2025 (box 38 of
    # your 2025 T4FHSA slips)", line 7 "Total contributions made to your FHSAs in 2024 (from
    # your 2025 FHSA participation room statement)" and line 8 "Contributions to your FHSAs in
    # 2024 before your first qualifying withdrawal (from your 2025 FHSA participation room
    # statement)" are starting amounts; line 9 "Line 7 minus line 8 =" prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2024",
            "less": "ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal_checked",
        },
        produces={"output": "ca/fhsa_contributions_in_2024_after_first_qualifying_withdrawal"},
    ),
    # Line 10 "Amount from line 2" is the same artifact as line 2; line 11 "Line 9 plus line 10
    # =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_contributions_in_2024_after_first_qualifying_withdrawal",
                "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked",
            )
        },
        produces={"output": "ca/fhsa_contributions_after_first_qualifying_withdrawal"},
    ),
    # Line 12 "Line 6 minus line 11 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_designated_withdrawals_in_2025",
            "less": "ca/fhsa_contributions_after_first_qualifying_withdrawal",
        },
        produces={"output": "ca/fhsa_excess_designated_withdrawals"},
    ),
    # Line 13 "Line 5 minus line 12 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_plus_variable_b_amount",
            "less": "ca/fhsa_excess_designated_withdrawals",
        },
        produces={"output": "ca/fhsa_contributions_limit"},
    ),
    # Line 14 "8,000.00", the dataset as an artifact of the same name; line 30 "8,000.00" is the
    # same figure, read again below.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_annual_amount"},
        consumes={},
        produces={"output": "ca/fhsa_annual_amount"},
    ),
    # Line 15 "Your FHSA carryforward for 2025 (from your 2025 FHSA participation room
    # statement)" is a starting amount; line 16 "Line 14 plus line 15 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fhsa_annual_amount", "ca/fhsa_carryforward_for_2025")},
        produces={"output": "ca/fhsa_annual_amount_with_carryforward"},
    ),
    # Line 17 "Total transfers from your RRSPs to your FHSAs in 2024 and prior years (from your
    # 2025 FHSA participation room statement)" and line 18 and line 68950 "Total transfers from
    # your RRSPs to your FHSAs in 2025 (boxes 32 and 34 of your 2025 T4FHSA slips)" are starting
    # amounts; line 19 "Line 17 plus line 18 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_rrsp_transfers_in_2024_and_prior_years",
                "ca/fhsa_rrsp_transfers_in_2025",
            )
        },
        produces={"output": "ca/fhsa_total_rrsp_transfers"},
    ),
    # Line 20 "Total designated transfers from your FHSAs to your RRSPs or RRIFs in 2024 and
    # prior years (from your 2025 FHSA participation room statement)" and line 21 and line 68955
    # "Total designated transfers from your FHSAs to your RRSPs or RRIFs in 2025 (box 36 of your
    # 2025 T4FHSA slips)" are starting amounts; line 22 "Line 20 plus line 21 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_designated_transfers_in_2024_and_prior_years",
                "ca/fhsa_designated_transfers_in_2025",
            )
        },
        produces={"output": "ca/fhsa_total_designated_transfers"},
    ),
    # Line 23 "Line 19 minus line 22 Net RRSP-to-FHSA transfer amount =" prints no floor. Line
    # 24 "Amount from line 23 of the previous page" is the same artifact.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_total_rrsp_transfers",
            "less": "ca/fhsa_total_designated_transfers",
        },
        produces={"output": "ca/fhsa_net_rrsp_transfer_amount"},
    ),
    # Step 2 (continued): line 25 "Amount from line 17 of the previous page" and line 26 "Amount
    # from line 20 of the previous page" are the same artifacts; line 27 "Net RRSP-to-FHSA
    # transfer amount for 2024 and prior years: Line 25 minus line 26 =" prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_rrsp_transfers_in_2024_and_prior_years",
            "less": "ca/fhsa_designated_transfers_in_2024_and_prior_years",
        },
        produces={"output": "ca/fhsa_net_rrsp_transfer_amount_for_2024_and_prior_years"},
    ),
    # Line 28 "Variable "H" amount of your annual FHSA limit for 2024 (from your 2025 FHSA
    # participation room statement)" is a starting amount; line 29 "Line 27 minus line 28 (if
    # negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_net_rrsp_transfer_amount_for_2024_and_prior_years",
            "less": "ca/fhsa_variable_h_amount",
        },
        produces={"output": "ca/fhsa_net_transfer_amount_less_variable_h_amount"},
    ),
    # Line 30 "8,000.00", the same dataset as line 14, read by its own step.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_annual_amount"},
        consumes={},
        produces={"output": "ca/fhsa_annual_amount_for_2024"},
    ),
    # Line 31 "Your FHSA carryforward for 2024 (from your 2024 FHSA participation room
    # statement)" is a starting amount; line 32 "Line 30 plus line 31 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fhsa_annual_amount_for_2024", "ca/fhsa_carryforward_for_2024")},
        produces={"output": "ca/fhsa_annual_amount_for_2024_with_carryforward"},
    ),
    # Line 33 "Enter whichever is less: amount from line 29 or line 32.", in that order.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/fhsa_net_transfer_amount_less_variable_h_amount",
                "ca/fhsa_annual_amount_for_2024_with_carryforward",
            )
        },
        produces={"output": "ca/fhsa_transfer_amount_at_most_limit"},
    ),
    # Line 34 "Variable "F" amount of your annual FHSA limit for 2024 (from your 2025 FHSA
    # participation room statement)" is a starting amount; line 35 "Line 33 plus line 34 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fhsa_transfer_amount_at_most_limit", "ca/fhsa_variable_f_amount")},
        produces={"output": "ca/fhsa_transfer_amount_plus_variable_f_amount"},
    ),
    # Line 36 "Line 24 minus line 35 =" (line 24 "Amount from line 23 of the previous page")
    # prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_net_rrsp_transfer_amount",
            "less": "ca/fhsa_transfer_amount_plus_variable_f_amount",
        },
        produces={"output": "ca/fhsa_net_transfer_amount_after_prior_years"},
    ),
    # Line 37 "Amount from line 16 of the previous page" and line 38 "Amount from line 36" are
    # the same artifacts; line 39 "Line 37 minus line 38 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_annual_amount_with_carryforward",
            "less": "ca/fhsa_net_transfer_amount_after_prior_years",
        },
        produces={"output": "ca/fhsa_annual_amount_after_transfers"},
    ),
    # Line 40 "Enter whichever is less: amount from line 13 of the previous page or line 39.
    # Annual FHSA limit for 2025", in that order, when the maximum participation period has not
    # ended.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/fhsa_contributions_limit", "ca/fhsa_annual_amount_after_transfers")
        },
        produces={"output": "ca/fhsa_annual_limit_from_step_2"},
    ),
    # "If your maximum participation period (MPP) ended in a prior year, do not complete this
    # step. Your 2025 annual FHSA limit is "0". Enter "0" on line 40 and continue at Step 3.":
    # the printed 0, the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_annual_limit_after_maximum_participation_period"},
        consumes={},
        produces={"output": "ca/fhsa_annual_limit_after_maximum_participation_period"},
    ),
    # A count of 1 when the maximum participation period ended in a prior year (a caller's 0 or
    # 1) chooses the printed 0 over the result of Step 2 for line 40 (and so for line 41 "Annual
    # FHSA limit from line 40").
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/fhsa_maximum_participation_period_ended_checked",
            "when_none": "ca/fhsa_annual_limit_from_step_2",
            "when_any": "ca/fhsa_annual_limit_after_maximum_participation_period",
        },
        produces={"output": "ca/fhsa_annual_limit"},
    ),
    # Step 3 "Calculate your FHSA deduction and unused FHSA contributions available to deduct in
    # future years": line 42 "Your total annual FHSA limits for 2024 and prior years (from your
    # 2025 FHSA participation room statement)" is a starting amount; line 43 "Line 41 plus line
    # 42 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/fhsa_annual_limit", "ca/fhsa_annual_limits_for_2024_and_prior_years")
        },
        produces={"output": "ca/fhsa_total_annual_limits"},
    ),
    # Schedule 15 line 44 "Your total FHSA deductions for 2024 and prior years" is at most line 42
    # "Your total annual FHSA limits for 2024 and prior years": the deductions are made against
    # those limits. The form implies that reading and prints no number for it, so the bound is
    # the reading, not a printed figure. A line 44 above line 42 is an input error, not capped,
    # and lines 45 and 48 read the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/fhsa_deductions_for_2024_and_prior_years",
            "bound": "ca/fhsa_annual_limits_for_2024_and_prior_years",
        },
        produces={"output": "ca/fhsa_deductions_for_2024_and_prior_years_checked"},
    ),
    # Line 44 "Your total FHSA deductions for 2024 and prior years (from your 2025 FHSA
    # participation room statement)" is a starting amount; line 45 "Line 43 minus line 44 ="
    # prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_total_annual_limits",
            "less": "ca/fhsa_deductions_for_2024_and_prior_years_checked",
        },
        produces={"output": "ca/fhsa_annual_limits_less_deductions"},
    ),
    # Line 46 "Lifetime FHSA limit 40,000.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_lifetime_limit"},
        consumes={},
        produces={"output": "ca/fhsa_lifetime_limit"},
    ),
    # Line 47 "Your FHSA deduction from line 44" is the same artifact as line 44; line 48 "Line
    # 46 minus line 47 =" prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_lifetime_limit",
            "less": "ca/fhsa_deductions_for_2024_and_prior_years_checked",
        },
        produces={"output": "ca/fhsa_lifetime_limit_less_deductions"},
    ),
    # Line 49 "Net RRSP-to-FHSA transfer amount from line 24" is the same artifact as line 23;
    # line 50 "Line 48 minus line 49 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_lifetime_limit_less_deductions",
            "less": "ca/fhsa_net_rrsp_transfer_amount",
        },
        produces={"output": "ca/fhsa_lifetime_limit_less_deductions_and_transfers"},
    ),
    # Line 51 "Enter whichever is less: amount from line 45 or line 50. Maximum FHSA deduction
    # available for 2025", in that order.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/fhsa_annual_limits_less_deductions",
                "ca/fhsa_lifetime_limit_less_deductions_and_transfers",
            )
        },
        produces={"output": "ca/fhsa_maximum_deduction"},
    ),
    # Line 52 "Your unused FHSA contributions available to deduct in future years (from your
    # 2025 FHSA participation room statement)" is a starting amount; line 53 "Amount from line 3
    # of page 2" is the same artifact as line 3; line 54 "Line 52 plus line 53 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_unused_contributions_brought_forward",
                "ca/fhsa_contributions_in_2025_before_first_qualifying_withdrawal",
            )
        },
        produces={"output": "ca/fhsa_unused_contributions_plus_contributions"},
    ),
    # Line 55 "Amount from line 12 of page 2" is the same artifact as line 12; line 56 "Line 54
    # minus line 55 =" prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_unused_contributions_plus_contributions",
            "less": "ca/fhsa_excess_designated_withdrawals",
        },
        produces={"output": "ca/fhsa_contributions_available"},
    ),
    # Line 57 "Enter the FHSA contributions you are deducting for 2025 (cannot be more than the
    # amount on line 51 of the previous page). Enter this amount on line 20805 of your return.
    # FHSA deduction for 2025": the amount the filer chooses to deduct, a starting amount,
    # refused when above line 51, not capped (as Schedule 7 line 18 is refused above line 17);
    # T1 line 37 and line 20805 is that amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_deducted",
            "bound": "ca/fhsa_maximum_deduction",
        },
        produces={"output": "ca/fhsa_deduction"},
    ),
    # Line 58 "Line 56 minus line 57 Your unused FHSA contributions available to deduct in
    # future years =", a product of the return for the next year's line 52; it prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/fhsa_contributions_available", "less": "ca/fhsa_deduction"},
        produces={"output": "ca/fhsa_unused_contributions_carried_forward"},
    ),
}

WIRING = {
    (
        Sum,
        frozenset({UNUSED_RRSP_CONTRIBUTIONS, RRSP_CONTRIBUTIONS}),
        frozenset({RRSP_CONTRIBUTIONS_AVAILABLE}),
    ),
    (
        LesserOf,
        frozenset({RRSP_CONTRIBUTIONS_AVAILABLE, RRSP_DEDUCTION_LIMIT}),
        frozenset({RRSP_DEDUCTION_MAXIMUM}),
    ),
    (
        AtMost,
        frozenset({RRSP_AMOUNT_DEDUCTED, RRSP_DEDUCTION_MAXIMUM}),
        frozenset({RRSP_DEDUCTION}),
    ),
    (
        Subtract,
        frozenset({RRSP_CONTRIBUTIONS_AVAILABLE, RRSP_DEDUCTION}),
        frozenset({UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD}),
    ),
    (
        AtMost,
        frozenset(
            {
                FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
                FHSA_CONTRIBUTIONS_IN_2025,
            }
        ),
        frozenset({FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED}),
    ),
    (
        Subtract,
        frozenset(
            {
                FHSA_CONTRIBUTIONS_IN_2025,
                FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
            }
        ),
        frozenset({FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL}),
    ),
    (
        Sum,
        frozenset(
            {
                FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
                FHSA_VARIABLE_B_AMOUNT,
            }
        ),
        frozenset({FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT}),
    ),
    (
        AtMost,
        frozenset(
            {
                FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
                FHSA_CONTRIBUTIONS_IN_2024,
            }
        ),
        frozenset({FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED}),
    ),
    (
        Subtract,
        frozenset(
            {
                FHSA_CONTRIBUTIONS_IN_2024,
                FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
            }
        ),
        frozenset({FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL}),
    ),
    (
        Sum,
        frozenset(
            {
                FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
                FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
            }
        ),
        frozenset({FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                FHSA_DESIGNATED_WITHDRAWALS_IN_2025,
                FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
            }
        ),
        frozenset({FHSA_EXCESS_DESIGNATED_WITHDRAWALS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT, FHSA_EXCESS_DESIGNATED_WITHDRAWALS}),
        frozenset({FHSA_CONTRIBUTIONS_LIMIT}),
    ),
    (CreditAmount, frozenset(), frozenset({FHSA_ANNUAL_AMOUNT})),
    (
        Sum,
        frozenset({FHSA_ANNUAL_AMOUNT, FHSA_CARRYFORWARD_FOR_2025}),
        frozenset({FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD}),
    ),
    (
        Sum,
        frozenset({FHSA_RRSP_TRANSFERS_IN_2024_AND_PRIOR_YEARS, FHSA_RRSP_TRANSFERS_IN_2025}),
        frozenset({FHSA_TOTAL_RRSP_TRANSFERS}),
    ),
    (
        Sum,
        frozenset(
            {
                FHSA_DESIGNATED_TRANSFERS_IN_2024_AND_PRIOR_YEARS,
                FHSA_DESIGNATED_TRANSFERS_IN_2025,
            }
        ),
        frozenset({FHSA_TOTAL_DESIGNATED_TRANSFERS}),
    ),
    (
        Subtract,
        frozenset({FHSA_TOTAL_RRSP_TRANSFERS, FHSA_TOTAL_DESIGNATED_TRANSFERS}),
        frozenset({FHSA_NET_RRSP_TRANSFER_AMOUNT}),
    ),
    (
        Subtract,
        frozenset(
            {
                FHSA_RRSP_TRANSFERS_IN_2024_AND_PRIOR_YEARS,
                FHSA_DESIGNATED_TRANSFERS_IN_2024_AND_PRIOR_YEARS,
            }
        ),
        frozenset({FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS, FHSA_VARIABLE_H_AMOUNT}),
        frozenset({FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT}),
    ),
    (CreditAmount, frozenset(), frozenset({FHSA_ANNUAL_AMOUNT_FOR_2024})),
    (
        Sum,
        frozenset({FHSA_ANNUAL_AMOUNT_FOR_2024, FHSA_CARRYFORWARD_FOR_2024}),
        frozenset({FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD}),
    ),
    (
        LesserOf,
        frozenset(
            {
                FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT,
                FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD,
            }
        ),
        frozenset({FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT}),
    ),
    (
        Sum,
        frozenset({FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT, FHSA_VARIABLE_F_AMOUNT}),
        frozenset({FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT}),
    ),
    (
        Subtract,
        frozenset({FHSA_NET_RRSP_TRANSFER_AMOUNT, FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT}),
        frozenset({FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD, FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS}
        ),
        frozenset({FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS}),
    ),
    (
        LesserOf,
        frozenset({FHSA_CONTRIBUTIONS_LIMIT, FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS}),
        frozenset({FHSA_ANNUAL_LIMIT_FROM_STEP_2}),
    ),
    (
        CreditAmount,
        frozenset(),
        frozenset({FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED,
                FHSA_ANNUAL_LIMIT_FROM_STEP_2,
                FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD,
            }
        ),
        frozenset({FHSA_ANNUAL_LIMIT}),
    ),
    (
        Sum,
        frozenset({FHSA_ANNUAL_LIMIT, FHSA_ANNUAL_LIMITS_FOR_2024_AND_PRIOR_YEARS}),
        frozenset({FHSA_TOTAL_ANNUAL_LIMITS}),
    ),
    (
        AtMost,
        frozenset(
            {
                FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS,
                FHSA_ANNUAL_LIMITS_FOR_2024_AND_PRIOR_YEARS,
            }
        ),
        frozenset({FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED}),
    ),
    (
        Subtract,
        frozenset({FHSA_TOTAL_ANNUAL_LIMITS, FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED}),
        frozenset({FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS}),
    ),
    (CreditAmount, frozenset(), frozenset({FHSA_LIFETIME_LIMIT})),
    (
        Subtract,
        frozenset({FHSA_LIFETIME_LIMIT, FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED}),
        frozenset({FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS, FHSA_NET_RRSP_TRANSFER_AMOUNT}),
        frozenset({FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS}),
    ),
    (
        LesserOf,
        frozenset(
            {
                FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
                FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS,
            }
        ),
        frozenset({FHSA_MAXIMUM_DEDUCTION}),
    ),
    (
        Sum,
        frozenset(
            {
                FHSA_UNUSED_CONTRIBUTIONS_BROUGHT_FORWARD,
                FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
            }
        ),
        frozenset({FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS}),
    ),
    (
        Subtract,
        frozenset(
            {FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS, FHSA_EXCESS_DESIGNATED_WITHDRAWALS}
        ),
        frozenset({FHSA_CONTRIBUTIONS_AVAILABLE}),
    ),
    (
        AtMost,
        frozenset({FHSA_CONTRIBUTIONS_DEDUCTED, FHSA_MAXIMUM_DEDUCTION}),
        frozenset({FHSA_DEDUCTION}),
    ),
    (
        Subtract,
        frozenset({FHSA_CONTRIBUTIONS_AVAILABLE, FHSA_DEDUCTION}),
        frozenset({FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD}),
    ),
}
