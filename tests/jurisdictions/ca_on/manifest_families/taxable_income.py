"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.apply_ratio import ApplyRatio
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_calculator.jurisdictions.ca.capabilities.lesser_of_with_maximum import LesserOfWithMaximum
from tax_calculator.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS_TOTAL,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
    ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
    ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
    ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
    ADJUSTED_LOSSES_APPLIED_2000,
    ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
    ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987,
    ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989,
    ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
    ADJUSTED_LOSSES_LEFT_AFTER_2000,
    ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985,
    ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION,
    CAPITAL_GAINS_DEDUCTION,
    DEDUCTIONS_FROM_NET_INCOME,
    FARMING_INCOME,
    LIMITED_PARTNERSHIP_AT_RISK_AMOUNT,
    LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS,
    LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
    NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
    NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
    NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
    NET_CAPITAL_LOSS_BALANCE_2000,
    NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
    NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985,
    NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
    NET_CAPITAL_LOSS_TWICE_IR_2000,
    NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION,
    NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM,
    NET_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
    NET_CAPITAL_LOSSES_CLAIMED,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_FARMING_INCOME_NOT_BELOW_ZERO,
    NET_INCOME,
    NET_INCOME_SIGNED,
    NON_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NON_CAPITAL_LOSSES_ON_LINE_25200,
    NORTHERN_RESIDENTS_DEDUCTIONS,
    OTHER_PAYMENTS_DEDUCTION,
    PRE_1986_CAPITAL_LOSS_BALANCE,
    PRE_1986_DEDUCTIONS_1988_AND_1989,
    PRE_1986_DEDUCTIONS_1990_TO_1999,
    PRE_1986_DEDUCTIONS_2000,
    PRE_1986_DEDUCTIONS_2001_TO_2024,
    PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989,
    PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999,
    PRE_1986_DEDUCTIONS_ADJUSTED_2000,
    PRE_1986_DEDUCTIONS_BEFORE_1988,
    PRE_1986_DEDUCTIONS_TOTAL,
    QBT_CAPITAL_GAINS_DEDUCTION,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
    REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
    REMAINING_ADJUSTED_LOSSES_2000,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
    REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985,
    RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS,
    RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED,
    SECURITY_OPTIONS_DEDUCTIONS,
    T657_INCLUSION_RATE_2000,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TAXABLE_INCOME_SIGNED,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES,
    UNAPPLIED_NET_CAPITAL_LOSSES_1985_TO_1987,
    UNAPPLIED_NET_CAPITAL_LOSSES_1988_AND_1989,
    UNAPPLIED_NET_CAPITAL_LOSSES_1990_TO_1999,
    UNAPPLIED_NET_CAPITAL_LOSSES_2000,
    UNAPPLIED_NET_CAPITAL_LOSSES_2001_TO_2024,
)

INPUTS = frozenset(
    {
        "ca/limited_partnership_losses_of_other_years",
        "ca/limited_partnership_at_risk_amount",
        "ca/non_capital_losses_of_other_years",
        "ca/restricted_farm_losses_of_other_years",
        "ca/unapplied_net_capital_losses_1985_to_1987",
        "ca/unapplied_net_capital_losses_1988_and_1989",
        "ca/unapplied_net_capital_losses_1990_to_1999",
        "ca/unapplied_net_capital_losses_2000",
        "ca/unapplied_net_capital_losses_2001_to_2024",
        "ca/net_capital_losses_claimed",
        "ca/net_capital_losses_before_may_23_1985",
        "ca/pre_1986_deductions_before_1988",
        "ca/pre_1986_deductions_1988_and_1989",
        "ca/pre_1986_deductions_1990_to_1999",
        "ca/pre_1986_deductions_2000",
        "ca/pre_1986_deductions_2001_to_2024",
        "ca/additional_deductions",
        # Form T2209 note (3), net income, "minus any:" the part of line 25600 that is net
        # employment income from a prescribed international organization, foreign income exempt
        # under a tax treaty, or adult basic education tuition assistance; read by the foreign
        # tax credit alone.
        "ca/exempt_income_deductions",
    }
)

OUTPUTS = frozenset(
    {
        "ca/net_capital_loss_balance_before_may_23_1985",
        "ca/net_capital_loss_balance_1985_to_1987",
        "ca/net_capital_loss_balance_1988_and_1989",
        "ca/net_capital_loss_balance_1990_to_1999",
        "ca/net_capital_loss_balance_2000",
        "ca/net_capital_loss_balance_2001_to_2024",
    }
)

STEPS = {
    # Form T1436 (Capital Gains Worksheet), "Line 25300 - Net capital loss of other years (if
    # you have pre-1986 capital loss balance)" and its "Chart A - Adjustment calculation for
    # carry-forward losses": each cell of the printed rows "Before May 23, 1985", "After May
    # 22, 1985, and before 1988", "In 1988 and 1989", "After 1989 and before 2000", "In 2000" and
    # "After 2000 and before 2025" is its own step. Column (A) "Amount of your unapplied net
    # capital losses" is a starting amount per row, as the form takes it (the row "Before May
    # 23, 1985" takes line 3 of the pre-1986 calculation above it).
    # Form T1436 "Calculating your pre-1986 capital loss balance available for 2025, if any":
    # line 1 "Balance of unapplied net capital losses you had before May 23, 1985" and the
    # capital gains deductions claimed, "Before 1988" (A), "In 1988 and 1989" (B), "From 1990 to
    # 1999" (C), "In 2000" (D) and "From 2001 to 2024" (E), are starting amounts.
    # "In 1988 and 1989" (B), "x 0.75" being 3/4.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/pre_1986_deductions_factor_1988_and_1989"},
        consumes={"base": "ca/pre_1986_deductions_1988_and_1989"},
        produces={"output": "ca/pre_1986_deductions_adjusted_1988_and_1989"},
    ),
    # "From 1990 to 1999" (C), "x 0.6667" being 2/3.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/pre_1986_deductions_factor_1990_to_1999"},
        consumes={"base": "ca/pre_1986_deductions_1990_to_1999"},
        produces={"output": "ca/pre_1986_deductions_adjusted_1990_to_1999"},
    ),
    # "In 2000" (D), "x 1/(IR x 2)": the deductions times the same factor as the Chart A row "In
    # 2000" column (B), that is divided by 2 x IR, rounded half-up to the cent once; 0 when IR
    # is 0.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/pre_1986_deductions_adjusted_2000_rounding"},
        consumes={
            "amount": "ca/pre_1986_deductions_2000",
            "numerator": "ca/net_capital_loss_numerator_one_2000",
            "denominator": "ca/net_capital_loss_twice_ir_2000",
        },
        produces={"output": "ca/pre_1986_deductions_adjusted_2000"},
    ),
    # "Total capital gains deductions after adjustment: add amounts A to E." (line 2).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/pre_1986_deductions_before_1988",
                "ca/pre_1986_deductions_adjusted_1988_and_1989",
                "ca/pre_1986_deductions_adjusted_1990_to_1999",
                "ca/pre_1986_deductions_adjusted_2000",
                "ca/pre_1986_deductions_2001_to_2024",
            ),
        },
        produces={"output": "ca/pre_1986_deductions_total"},
    ),
    # Line 3 "Pre-1986 capital loss balance available for 2025: line 1 minus line 2".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/net_capital_losses_before_may_23_1985",
            "less": "ca/pre_1986_deductions_total",
        },
        produces={"output": "ca/pre_1986_capital_loss_balance"},
    ),
    # Row "Before May 23, 1985", column (A) being line 3, column (C) "Adjusted gross capital
    # losses (column A multiplied by column B)", column (B) "Adjustment factor (for the
    # inclusion rate)" being 1.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_before_may_23_1985"},
        consumes={"base": "ca/pre_1986_capital_loss_balance"},
        produces={"output": "ca/adjusted_gross_capital_losses_before_may_23_1985"},
    ),
    # Row "After May 22, 1985, and before 1988", column (C) "Adjusted gross capital losses
    # (column A multiplied by column B)", column (B) "Adjustment factor (for the inclusion
    # rate)" being 1.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_1985_to_1987"},
        consumes={"base": "ca/unapplied_net_capital_losses_1985_to_1987"},
        produces={"output": "ca/adjusted_gross_capital_losses_1985_to_1987"},
    ),
    # Row "In 1988 and 1989", column (C) "Adjusted gross capital losses (column A multiplied by
    # column B)", column (B) "Adjustment factor (for the inclusion rate)" being 3/4 (printed
    # 0.75).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_1988_and_1989"},
        consumes={"base": "ca/unapplied_net_capital_losses_1988_and_1989"},
        produces={"output": "ca/adjusted_gross_capital_losses_1988_and_1989"},
    ),
    # Row "After 1989 and before 2000", column (C) "Adjusted gross capital losses (column A
    # multiplied by column B)", column (B) "Adjustment factor (for the inclusion rate)" being
    # 2/3 (printed 0.6667).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_1990_to_1999"},
        consumes={"base": "ca/unapplied_net_capital_losses_1990_to_1999"},
        produces={"output": "ca/adjusted_gross_capital_losses_1990_to_1999"},
    ),
    # Row "After 2000 and before 2025", column (C) "Adjusted gross capital losses (column A
    # multiplied by column B)", column (B) "Adjustment factor (for the inclusion rate)" being 1.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_2001_to_2024"},
        consumes={"base": "ca/unapplied_net_capital_losses_2001_to_2024"},
        produces={"output": "ca/adjusted_gross_capital_losses_2001_to_2024"},
    ),
    # Line 4 "Total of column C from Chart A".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/adjusted_gross_capital_losses_before_may_23_1985",
                "ca/adjusted_gross_capital_losses_1985_to_1987",
                "ca/adjusted_gross_capital_losses_1988_and_1989",
                "ca/adjusted_gross_capital_losses_1990_to_1999",
                "ca/adjusted_gross_capital_losses_2000",
                "ca/adjusted_gross_capital_losses_2001_to_2024",
            ),
        },
        produces={"output": "ca/total_adjusted_net_capital_losses"},
    ),
    # Line 5 "Taxable capital gains from line 12700 of your 2025 return", then line 6 "Enter
    # whichever is less: amount from line 4 or line 5.", in that order.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/total_adjusted_net_capital_losses",
                "ca/taxable_capital_gains",
            ),
        },
        produces={"output": "ca/net_capital_losses_available_to_claim"},
    ),
    # Line 7 "Enter the amount of losses you want to claim (3).", note (3) "You can apply all or
    # part of the amount from line 6 against your taxable capital gains in 2025.": the amount
    # the filer chooses to claim, a starting amount, refused when above line 6, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/net_capital_losses_claimed",
            "bound": "ca/net_capital_losses_available_to_claim",
        },
        produces={"output": "ca/adjusted_net_capital_losses_applied"},
    ),
    # Line 8 "Balance of unapplied adjusted net capital losses of other years not used to reduce
    # taxable capital gains: line 4 minus line 7".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/total_adjusted_net_capital_losses",
            "less": "ca/adjusted_net_capital_losses_applied",
        },
        produces={"output": "ca/unapplied_adjusted_net_capital_losses"},
    ),
    # Line 9 "Enter whichever is less: amount from line 3, line 8, or $2,000.".
    CapabilitySelection(
        name="ca/lesser_of_with_maximum",
        params={"maximum": "ca/net_capital_losses_additional_deduction_maximum"},
        consumes={
            "amounts": (
                "ca/pre_1986_capital_loss_balance",
                "ca/unapplied_adjusted_net_capital_losses",
            ),
        },
        produces={"output": "ca/net_capital_losses_additional_deduction"},
    ),
    # Line 10 "Line 7 plus line 9", "Deduction in 2025 for net capital losses of other years":
    # T1 line 63 and line 25300 "Net capital losses of other years".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/adjusted_net_capital_losses_applied",
                "ca/net_capital_losses_additional_deduction",
            ),
        },
        produces={"output": "ca/net_capital_losses_of_other_years"},
    ),
    # Lines 11 "Amount from line 7" and 12 "Amount from line 9" are copies; line 13 "Line 11 plus
    # line 12", "Total adjusted net capital losses of other years applied in 2025", which note
    # (4) makes the total of column D.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/adjusted_net_capital_losses_applied",
                "ca/net_capital_losses_additional_deduction",
            ),
        },
        produces={"output": "ca/total_adjusted_net_capital_losses_applied"},
    ),
    # Row "Before May 23, 1985", column (D): the lesser of column C and line 13, the oldest row
    # first.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/adjusted_gross_capital_losses_before_may_23_1985",
                "ca/total_adjusted_net_capital_losses_applied",
            ),
        },
        produces={"output": "ca/adjusted_losses_applied_before_may_23_1985"},
    ),
    # What is left of line 13 after the row "Before May 23, 1985": line 13 less its column D.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/total_adjusted_net_capital_losses_applied",
            "less": "ca/adjusted_losses_applied_before_may_23_1985",
        },
        produces={"output": "ca/adjusted_losses_left_after_before_may_23_1985"},
    ),
    # Row "Before May 23, 1985", column (E) "Remaining adjusted net capital losses (column C minus
    # column D)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_gross_capital_losses_before_may_23_1985",
            "less": "ca/adjusted_losses_applied_before_may_23_1985",
        },
        produces={"output": "ca/remaining_adjusted_losses_before_may_23_1985"},
    ),
    # Row "Before May 23, 1985", column (G) "Net capital loss balance available to carry forward
    # (column E multiplied by column F)", column (F) "Adjustment factor (for carry-forward
    # losses)" being 1.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_carry_forward_factor_before_may_23_1985"},
        consumes={"base": "ca/remaining_adjusted_losses_before_may_23_1985"},
        produces={"output": "ca/net_capital_loss_balance_before_may_23_1985"},
    ),
    # Row "After May 22, 1985, and before 1988", column (D) "Total adjusted net capital losses
    # applied against taxable capital gains in 2025": the lesser of column C and what is left
    # of line 13 after the row "Before May 23, 1985", as "You have to apply net capital losses of
    # earlier years before you apply net capital losses of later years." (Guide T4037) puts the
    # oldest row first.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/adjusted_gross_capital_losses_1985_to_1987",
                "ca/adjusted_losses_left_after_before_may_23_1985",
            ),
        },
        produces={"output": "ca/adjusted_losses_applied_1985_to_1987"},
    ),
    # What is left of line 13 after the row "After May 22, 1985, and before 1988": the amount
    # left after the row before it less its column D.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_losses_left_after_before_may_23_1985",
            "less": "ca/adjusted_losses_applied_1985_to_1987",
        },
        produces={"output": "ca/adjusted_losses_left_after_1985_to_1987"},
    ),
    # Row "After May 22, 1985, and before 1988", column (E) "Remaining adjusted net capital
    # losses (column C minus column D)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_gross_capital_losses_1985_to_1987",
            "less": "ca/adjusted_losses_applied_1985_to_1987",
        },
        produces={"output": "ca/remaining_adjusted_losses_1985_to_1987"},
    ),
    # Row "After May 22, 1985, and before 1988", column (G) "Net capital loss balance available
    # to carry forward (column E multiplied by column F)", column (F) "Adjustment factor (for
    # carry-forward losses)" being 1.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_carry_forward_factor_1985_to_1987"},
        consumes={"base": "ca/remaining_adjusted_losses_1985_to_1987"},
        produces={"output": "ca/net_capital_loss_balance_1985_to_1987"},
    ),
    # Row "In 1988 and 1989", column (D): the lesser of column C and what is left of line 13
    # after the older rows.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/adjusted_gross_capital_losses_1988_and_1989",
                "ca/adjusted_losses_left_after_1985_to_1987",
            ),
        },
        produces={"output": "ca/adjusted_losses_applied_1988_and_1989"},
    ),
    # What is left of line 13 after the row "In 1988 and 1989": the amount before it less its
    # column D.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_losses_left_after_1985_to_1987",
            "less": "ca/adjusted_losses_applied_1988_and_1989",
        },
        produces={"output": "ca/adjusted_losses_left_after_1988_and_1989"},
    ),
    # Row "In 1988 and 1989", column (E) "Remaining adjusted net capital losses (column C minus
    # column D)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_gross_capital_losses_1988_and_1989",
            "less": "ca/adjusted_losses_applied_1988_and_1989",
        },
        produces={"output": "ca/remaining_adjusted_losses_1988_and_1989"},
    ),
    # Row "In 1988 and 1989", column (G) "Net capital loss balance available to carry forward
    # (column E multiplied by column F)", column (F) "Adjustment factor (for carry-forward
    # losses)" being 4/3 (printed 1.33).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_carry_forward_factor_1988_and_1989"},
        consumes={"base": "ca/remaining_adjusted_losses_1988_and_1989"},
        produces={"output": "ca/net_capital_loss_balance_1988_and_1989"},
    ),
    # Row "After 1989 and before 2000", column (D): the lesser of column C and what is left of
    # line 13 after the older rows.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/adjusted_gross_capital_losses_1990_to_1999",
                "ca/adjusted_losses_left_after_1988_and_1989",
            ),
        },
        produces={"output": "ca/adjusted_losses_applied_1990_to_1999"},
    ),
    # What is left of line 13 after the row "After 1989 and before 2000": the amount before it
    # less its column D.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_losses_left_after_1988_and_1989",
            "less": "ca/adjusted_losses_applied_1990_to_1999",
        },
        produces={"output": "ca/adjusted_losses_left_after_1990_to_1999"},
    ),
    # Row "After 1989 and before 2000", column (E) "Remaining adjusted net capital losses
    # (column C minus column D)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_gross_capital_losses_1990_to_1999",
            "less": "ca/adjusted_losses_applied_1990_to_1999",
        },
        produces={"output": "ca/remaining_adjusted_losses_1990_to_1999"},
    ),
    # Row "After 1989 and before 2000", column (G) "Net capital loss balance available to carry
    # forward (column E multiplied by column F)", column (F) "Adjustment factor (for
    # carry-forward losses)" being 3/2 (printed 1.5).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_carry_forward_factor_1990_to_1999"},
        consumes={"base": "ca/remaining_adjusted_losses_1990_to_1999"},
        produces={"output": "ca/net_capital_loss_balance_1990_to_1999"},
    ),
    # Row "In 2000", column (F) "2 × IR" (footnote (2): "IR" is the inclusion rate for 2000, from
    # line 16 in Part 4 of Schedule 3 for 2000, or from the notice of assessment), IR times 2,
    # exact and not rounded. IR is the 2000 inclusion rate that Form T657 Chart 2 reads.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_twice_ir_fraction_2000"},
        consumes={"base": "ca/t657_inclusion_rate_2000"},
        produces={"output": "ca/net_capital_loss_twice_ir_2000"},
    ),
    # Row "In 2000", column (B) "1/(IR × 2)": the printed 1 of the factor, as an artifact.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/net_capital_loss_numerator_one_2000"},
        consumes={},
        produces={"output": "ca/net_capital_loss_numerator_one_2000"},
    ),
    # Row "In 2000", column (C) "Adjusted gross capital losses (column A multiplied by column
    # B)": column A times 1/(IR × 2), that is column A divided by column F, rounded half-up to
    # the cent once; 0 when IR is 0.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/adjusted_gross_capital_losses_2000_rounding"},
        consumes={
            "amount": "ca/unapplied_net_capital_losses_2000",
            "numerator": "ca/net_capital_loss_numerator_one_2000",
            "denominator": "ca/net_capital_loss_twice_ir_2000",
        },
        produces={"output": "ca/adjusted_gross_capital_losses_2000"},
    ),
    # Row "In 2000", column (D) "Total adjusted net capital losses applied against taxable capital
    # gains in 2025": the lesser of column C and what is left of line 13 after the older rows,
    # the rows before it taken first.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/adjusted_gross_capital_losses_2000",
                "ca/adjusted_losses_left_after_1990_to_1999",
            ),
        },
        produces={"output": "ca/adjusted_losses_applied_2000"},
    ),
    # What is left of line 13 after the row "In 2000": the amount before it less its column D.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_losses_left_after_1990_to_1999",
            "less": "ca/adjusted_losses_applied_2000",
        },
        produces={"output": "ca/adjusted_losses_left_after_2000"},
    ),
    # Row "In 2000", column (E) "Remaining adjusted net capital losses (column C minus column D)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_gross_capital_losses_2000",
            "less": "ca/adjusted_losses_applied_2000",
        },
        produces={"output": "ca/remaining_adjusted_losses_2000"},
    ),
    # Row "In 2000", column (G) "Net capital loss balance available to carry forward (column E
    # multiplied by column F)": column E times column F (2 × IR), rounded half-up to the cent
    # once, over the printed 1 of column B.
    CapabilitySelection(
        name="core/apply_ratio",
        params={"rounding": "ca/net_capital_loss_balance_2000_rounding"},
        consumes={
            "amount": "ca/remaining_adjusted_losses_2000",
            "numerator": "ca/net_capital_loss_twice_ir_2000",
            "denominator": "ca/net_capital_loss_numerator_one_2000",
        },
        produces={"output": "ca/net_capital_loss_balance_2000"},
    ),
    # Row "After 2000 and before 2025", column (D): the lesser of column C and what is left of
    # line 13 after the older rows.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/adjusted_gross_capital_losses_2001_to_2024",
                "ca/adjusted_losses_left_after_2000",
            ),
        },
        produces={"output": "ca/adjusted_losses_applied_2001_to_2024"},
    ),
    # Row "After 2000 and before 2025", column (E) "Remaining adjusted net capital losses
    # (column C minus column D)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/adjusted_gross_capital_losses_2001_to_2024",
            "less": "ca/adjusted_losses_applied_2001_to_2024",
        },
        produces={"output": "ca/remaining_adjusted_losses_2001_to_2024"},
    ),
    # Row "After 2000 and before 2025", column (G) "Net capital loss balance available to carry
    # forward (column E multiplied by column F)", column (F) "Adjustment factor (for
    # carry-forward losses)" being 1.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_carry_forward_factor_2001_to_2024"},
        consumes={"base": "ca/remaining_adjusted_losses_2001_to_2024"},
        produces={"output": "ca/net_capital_loss_balance_2001_to_2024"},
    ),
    # Guide T4002 "you can only apply them up to the amount of your net farming income in 2025": T1
    # line 14100 (`ca/farming_income`), a net farm loss counting as 0.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/farming_income",)},
        produces={"output": "ca/net_farming_income_not_below_zero"},
    ),
    # The restricted farm losses of other years claimed are at most the net farming income: an
    # amount above it is an input error, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/restricted_farm_losses_of_other_years",
            "bound": "ca/net_farming_income_not_below_zero",
        },
        produces={"output": "ca/restricted_farm_losses_of_other_years_checked"},
    ),
    # Guide 5000-G line 25100 "You can only deduct this loss if there is an amount in box 105": the
    # limited partnership losses of other years claimed are at most the T5013 box 105 amount: an
    # amount above it is an input error, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/limited_partnership_losses_of_other_years",
            "bound": "ca/limited_partnership_at_risk_amount",
        },
        produces={"output": "ca/limited_partnership_losses_of_other_years_checked"},
    ),
    # T1 line 62 and line 25200 "Non-capital losses of other years": "Claim this amount on line
    # 25200", added to the non-capital losses of other years claimed there.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/non_capital_losses_of_other_years",
                "ca/restricted_farm_losses_of_other_years_checked",
            )
        },
        produces={"output": "ca/non_capital_losses_on_line_25200"},
    ),
    # T1 line 68 and line 25700 "Add lines 58 to 67.": lines 58, 59, 60, 61, 62, 63, 64, 65, 66 and
    # 67 (lines 24400, 24900, 25000, 25100, 25200, 25300, 25395, 25400, 25500 and 25600), in line
    # order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/canadian_armed_forces_and_police_deduction",
                "ca/security_options_deductions",
                "ca/other_payments_deduction",
                "ca/limited_partnership_losses_of_other_years_checked",
                "ca/non_capital_losses_on_line_25200",
                "ca/net_capital_losses_of_other_years",
                "ca/qbt_capital_gains_deduction",
                "ca/capital_gains_deduction",
                "ca/northern_residents_deductions",
                "ca/additional_deductions_total",
            )
        },
        produces={"output": "ca/deductions_from_net_income"},
    ),
    # Form T691 Part 1 line 1 "Taxable income from line 26000 of your return (or the amount you
    # would have entered on line 26000 if the instructions for lines 23600 and 26000 said "if
    # negative, show in brackets") (1)": line 57 minus line 68 of T1 line 26000, with line 57 the
    # net income signed (`ca/net_income_signed`, line 23600) and line 68 the deductions from net
    # income (line 25700), before the floor at 0 that `ca/taxable_income` takes.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/net_income_signed",
            "less": "ca/deductions_from_net_income",
        },
        produces={"output": "ca/taxable_income_signed"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/net_income", "less": "ca/deductions_from_net_income"},
        produces={"output": "ca/taxable_income"},
    ),
}

WIRING = {
    (
        ApplyFraction,
        frozenset({PRE_1986_DEDUCTIONS_1988_AND_1989}),
        frozenset({PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989}),
    ),
    (
        ApplyFraction,
        frozenset({PRE_1986_DEDUCTIONS_1990_TO_1999}),
        frozenset({PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999}),
    ),
    (
        ApplyRatioOrZero,
        frozenset(
            {
                PRE_1986_DEDUCTIONS_2000,
                NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
                NET_CAPITAL_LOSS_TWICE_IR_2000,
            }
        ),
        frozenset({PRE_1986_DEDUCTIONS_ADJUSTED_2000}),
    ),
    (
        Sum,
        frozenset(
            {
                PRE_1986_DEDUCTIONS_BEFORE_1988,
                PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989,
                PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999,
                PRE_1986_DEDUCTIONS_ADJUSTED_2000,
                PRE_1986_DEDUCTIONS_2001_TO_2024,
            }
        ),
        frozenset({PRE_1986_DEDUCTIONS_TOTAL}),
    ),
    (
        Subtract,
        frozenset({NET_CAPITAL_LOSSES_BEFORE_MAY_23_1985, PRE_1986_DEDUCTIONS_TOTAL}),
        frozenset({PRE_1986_CAPITAL_LOSS_BALANCE}),
    ),
    (
        ApplyFraction,
        frozenset({PRE_1986_CAPITAL_LOSS_BALANCE}),
        frozenset({ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985}),
    ),
    (
        Subtract,
        frozenset({TOTAL_ADJUSTED_NET_CAPITAL_LOSSES, ADJUSTED_NET_CAPITAL_LOSSES_APPLIED}),
        frozenset({UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES}),
    ),
    (
        LesserOfWithMaximum,
        frozenset({PRE_1986_CAPITAL_LOSS_BALANCE, UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES}),
        frozenset({NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION}),
    ),
    (
        Sum,
        frozenset({ADJUSTED_NET_CAPITAL_LOSSES_APPLIED, NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION}),
        frozenset({NET_CAPITAL_LOSSES_OF_OTHER_YEARS}),
    ),
    (
        Sum,
        frozenset({ADJUSTED_NET_CAPITAL_LOSSES_APPLIED, NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION}),
        frozenset({TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
                TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
            }
        ),
        frozenset({ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985}),
    ),
    (
        Subtract,
        frozenset(
            {TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED, ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985}
        ),
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985}),
    ),
    (
        Subtract,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
                ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985,
            }
        ),
        frozenset({REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985}),
    ),
    (
        ApplyFraction,
        frozenset({REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985}),
        frozenset({NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985}),
    ),
    (
        ApplyFraction,
        frozenset({UNAPPLIED_NET_CAPITAL_LOSSES_1985_TO_1987}),
        frozenset({ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987}),
    ),
    (
        ApplyFraction,
        frozenset({UNAPPLIED_NET_CAPITAL_LOSSES_1988_AND_1989}),
        frozenset({ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989}),
    ),
    (
        ApplyFraction,
        frozenset({UNAPPLIED_NET_CAPITAL_LOSSES_1990_TO_1999}),
        frozenset({ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999}),
    ),
    (
        ApplyFraction,
        frozenset({UNAPPLIED_NET_CAPITAL_LOSSES_2001_TO_2024}),
        frozenset({ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024}),
    ),
    (
        Sum,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
                ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
                ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
                ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
                ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
                ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
            }
        ),
        frozenset({TOTAL_ADJUSTED_NET_CAPITAL_LOSSES}),
    ),
    (
        LesserOf,
        frozenset({TOTAL_ADJUSTED_NET_CAPITAL_LOSSES, TAXABLE_CAPITAL_GAINS}),
        frozenset({NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM}),
    ),
    (
        AtMost,
        frozenset({NET_CAPITAL_LOSSES_CLAIMED, NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM}),
        frozenset({ADJUSTED_NET_CAPITAL_LOSSES_APPLIED}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
                ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985,
            }
        ),
        frozenset({ADJUSTED_LOSSES_APPLIED_1985_TO_1987}),
    ),
    (
        Subtract,
        frozenset(
            {ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985, ADJUSTED_LOSSES_APPLIED_1985_TO_1987}
        ),
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987}),
    ),
    (
        Subtract,
        frozenset(
            {ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987, ADJUSTED_LOSSES_APPLIED_1985_TO_1987}
        ),
        frozenset({REMAINING_ADJUSTED_LOSSES_1985_TO_1987}),
    ),
    (
        ApplyFraction,
        frozenset({REMAINING_ADJUSTED_LOSSES_1985_TO_1987}),
        frozenset({NET_CAPITAL_LOSS_BALANCE_1985_TO_1987}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
                ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987,
            }
        ),
        frozenset({ADJUSTED_LOSSES_APPLIED_1988_AND_1989}),
    ),
    (
        Subtract,
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987, ADJUSTED_LOSSES_APPLIED_1988_AND_1989}),
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989}),
    ),
    (
        Subtract,
        frozenset(
            {ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989, ADJUSTED_LOSSES_APPLIED_1988_AND_1989}
        ),
        frozenset({REMAINING_ADJUSTED_LOSSES_1988_AND_1989}),
    ),
    (
        ApplyFraction,
        frozenset({REMAINING_ADJUSTED_LOSSES_1988_AND_1989}),
        frozenset({NET_CAPITAL_LOSS_BALANCE_1988_AND_1989}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
                ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989,
            }
        ),
        frozenset({ADJUSTED_LOSSES_APPLIED_1990_TO_1999}),
    ),
    (
        Subtract,
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989, ADJUSTED_LOSSES_APPLIED_1990_TO_1999}),
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999}),
    ),
    (
        Subtract,
        frozenset(
            {ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999, ADJUSTED_LOSSES_APPLIED_1990_TO_1999}
        ),
        frozenset({REMAINING_ADJUSTED_LOSSES_1990_TO_1999}),
    ),
    (
        ApplyFraction,
        frozenset({REMAINING_ADJUSTED_LOSSES_1990_TO_1999}),
        frozenset({NET_CAPITAL_LOSS_BALANCE_1990_TO_1999}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
                ADJUSTED_LOSSES_LEFT_AFTER_2000,
            }
        ),
        frozenset({ADJUSTED_LOSSES_APPLIED_2001_TO_2024}),
    ),
    (
        Subtract,
        frozenset(
            {ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024, ADJUSTED_LOSSES_APPLIED_2001_TO_2024}
        ),
        frozenset({REMAINING_ADJUSTED_LOSSES_2001_TO_2024}),
    ),
    (
        ApplyFraction,
        frozenset({REMAINING_ADJUSTED_LOSSES_2001_TO_2024}),
        frozenset({NET_CAPITAL_LOSS_BALANCE_2001_TO_2024}),
    ),
    (
        ApplyFraction,
        frozenset({T657_INCLUSION_RATE_2000}),
        frozenset({NET_CAPITAL_LOSS_TWICE_IR_2000}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({NET_CAPITAL_LOSS_NUMERATOR_ONE_2000}),
    ),
    (
        ApplyRatioOrZero,
        frozenset(
            {
                UNAPPLIED_NET_CAPITAL_LOSSES_2000,
                NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
                NET_CAPITAL_LOSS_TWICE_IR_2000,
            }
        ),
        frozenset({ADJUSTED_GROSS_CAPITAL_LOSSES_2000}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
                ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
            }
        ),
        frozenset({ADJUSTED_LOSSES_APPLIED_2000}),
    ),
    (
        Subtract,
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999, ADJUSTED_LOSSES_APPLIED_2000}),
        frozenset({ADJUSTED_LOSSES_LEFT_AFTER_2000}),
    ),
    (
        Subtract,
        frozenset({ADJUSTED_GROSS_CAPITAL_LOSSES_2000, ADJUSTED_LOSSES_APPLIED_2000}),
        frozenset({REMAINING_ADJUSTED_LOSSES_2000}),
    ),
    (
        ApplyRatio,
        frozenset(
            {
                REMAINING_ADJUSTED_LOSSES_2000,
                NET_CAPITAL_LOSS_TWICE_IR_2000,
                NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
            }
        ),
        frozenset({NET_CAPITAL_LOSS_BALANCE_2000}),
    ),
    (
        Sum,
        frozenset(
            {
                CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION,
                SECURITY_OPTIONS_DEDUCTIONS,
                OTHER_PAYMENTS_DEDUCTION,
                LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
                NON_CAPITAL_LOSSES_ON_LINE_25200,
                NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
                QBT_CAPITAL_GAINS_DEDUCTION,
                CAPITAL_GAINS_DEDUCTION,
                NORTHERN_RESIDENTS_DEDUCTIONS,
                ADDITIONAL_DEDUCTIONS_TOTAL,
            }
        ),
        frozenset({DEDUCTIONS_FROM_NET_INCOME}),
    ),
    (SumNotBelowZero, frozenset({FARMING_INCOME}), frozenset({NET_FARMING_INCOME_NOT_BELOW_ZERO})),
    (
        AtMost,
        frozenset({LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS, LIMITED_PARTNERSHIP_AT_RISK_AMOUNT}),
        frozenset({LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED}),
    ),
    (
        AtMost,
        frozenset({RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS, NET_FARMING_INCOME_NOT_BELOW_ZERO}),
        frozenset({RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {NON_CAPITAL_LOSSES_OF_OTHER_YEARS, RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED}
        ),
        frozenset({NON_CAPITAL_LOSSES_ON_LINE_25200}),
    ),
    (
        Subtract,
        frozenset({NET_INCOME_SIGNED, DEDUCTIONS_FROM_NET_INCOME}),
        frozenset({TAXABLE_INCOME_SIGNED}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({NET_INCOME, DEDUCTIONS_FROM_NET_INCOME}),
        frozenset({TAXABLE_INCOME}),
    ),
}
