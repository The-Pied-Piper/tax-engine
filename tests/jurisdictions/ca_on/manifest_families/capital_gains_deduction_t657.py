"""The CA-ON manifest entries of Form T657 (line 25400): Steps 1 and 2, Charts 1, 2 and 2025
(see `test_manifest.py`).

The steps are in the manifest part `06b_capital_gains_deduction_t657.yaml`; line 25400 is added to
line 25700 in the `taxable_income` family. Step 3a (reserves on the 2016 to 2024 dispositions) is
out of this family.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_calculator.jurisdictions.ca.capabilities.chart_1_column_g_total import Chart1ColumnGTotal
from tax_calculator.jurisdictions.ca.catalog import (
    ABIL_AFTER_QBT_REDUCTION,
    ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025,
    ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    ALLOWABLE_BUSINESS_INVESTMENT_LOSS,
    ANNUAL_GAINS_LIMIT_2025,
    ANNUAL_GAINS_LINE_2,
    ANNUAL_GAINS_LINE_3,
    ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE,
    ANNUAL_GAINS_LINE_5,
    ANNUAL_GAINS_LINE_7,
    ANNUAL_GAINS_LINE_9,
    ANNUAL_GAINS_LINE_10,
    ANNUAL_GAINS_LINE_12,
    ANNUAL_GAINS_SCHEDULE_3_TOTAL,
    CAPITAL_GAINS_DEDUCTION,
    CAPITAL_GAINS_DEDUCTION_CLAIMED,
    CHART_1_COLUMN_G_TOTAL,
    CHART_2_LINE_3,
    CHART_2_LINE_4,
    CHART_2_LINE_5,
    CHART_2_LINE_7,
    CHART_2_LINE_8,
    CHART_2_LINE_9,
    CHART_2_LINE_11,
    CHART_2_LINE_12,
    CHART_2_LINE_13,
    CHART_2_LINE_14_OVER_TWICE_IR,
    CHART_2_LINE_15,
    CHART_2_LINE_16,
    CHART_2_LINE_17,
    CHART_2_LINE_19,
    CHART_2_NUMERATOR_ONE,
    CHART_2_TWICE_IR,
    CHART_2024_PERIOD_2_AMOUNT_N,
    CHART_2025_PART_1_AMOUNT_A,
    CHART_2025_PART_1_AMOUNT_C,
    CHART_2025_PART_1_AMOUNT_E,
    CHART_2025_PART_1_AMOUNT_K,
    CHART_2025_PART_1_AMOUNT_M,
    CHART_2025_PART_1_AMOUNT_N,
    CHART_2025_PART_1_AMOUNT_P,
    CHART_2025_PART_1_AMOUNT_Q,
    CHART_2025_PART_1_AMOUNTS_F_TO_J,
    CHART_2025_PART_2_AMOUNT_A,
    CHART_2025_PART_2_AMOUNT_C,
    CHART_2025_PART_2_AMOUNT_E,
    CHART_2025_PART_2_AMOUNT_F,
    CHART_2025_PART_2_AMOUNT_G,
    CHART_2025_PART_2_AMOUNT_H,
    CHART_2025_PART_2_AMOUNT_K,
    CHART_2025_PART_2_AMOUNT_M,
    CHART_2025_PART_2_AMOUNT_N,
    CHART_2025_PART_2_AMOUNT_P,
    CHART_2025_PART_2_AMOUNT_Q,
    CHART_2025_PART_2_AMOUNTS_F_TO_J,
    CHART_2025_PART_2_MAXIMUM_CLAIM,
    CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    CUMULATIVE_GAINS_LIMIT_2025,
    CUMULATIVE_LOSSES_AND_DEDUCTIONS,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025,
    INCLUDED_CAPITAL_GAIN,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    PARTNERSHIP_GAINS_AT_FULL_INCLUSION,
    QBT_ABIL_REDUCTION,
    QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    QFFP_FORECLOSURE_GAIN_OR_LOSS,
    QFFP_GAIN_OR_LOSS,
    QSBCS_GAIN_OR_LOSS,
    QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO,
    SCHEDULE_3_LINE_19900,
    T3_CAPITAL_GAINS_OR_LOSSES,
    T657_ABIL_CLAIMED_1985_TO_2024,
    T657_CAPITAL_LOSSES_CLAIMED_1985,
    T657_CHART_1_ROWS,
    T657_CHART_2_LINE_1,
    T657_CHART_2_LINE_2,
    T657_CHART_2_LINE_6,
    T657_CHART_2_LINE_10,
    T657_CHART_2_LINE_14,
    T657_CHART_2_LINE_18,
    T657_CUMULATIVE_NET_INVESTMENT_LOSS,
    T657_DEDUCTIONS_CLAIMED_1985_TO_2024,
    T657_GAINS_1985_TO_1991,
    T657_GAINS_1992_AND_1993,
    T657_GAINS_1994,
    T657_GAINS_1995,
    T657_GAINS_1996_TO_1999,
    T657_GAINS_2000,
    T657_GAINS_2001,
    T657_GAINS_2002_TO_2024,
    T657_INCLUSION_RATE_2000,
    T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    T657_PART_1_AMOUNT_F,
    T657_PART_1_AMOUNT_G,
    T657_PART_1_AMOUNT_H,
    T657_PART_1_AMOUNT_I,
    T657_PART_1_AMOUNT_J,
    T657_PART_1_AMOUNT_L,
    T657_PART_2_AMOUNT_I,
    T657_PART_2_AMOUNT_J,
    T657_PART_2_AMOUNT_L,
    T657_PART_2_EXCLUDED_F,
    T657_PART_2_EXCLUDED_G,
    T657_PART_2_EXCLUDED_H,
    T657_T2048_LINE_17217_FOR_2024,
    TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT,
)
from tests.jurisdictions.ca_on.manifest_families.t936 import CHART_A_LINE_14_EXPORT, CNIL_EXPORT
from tests.jurisdictions.ca_on.manifest_families.t2017_reserve import T2017_LINE_13_EXPORT

INPUTS = frozenset(
    {
        "ca/t657_gains_1985_to_1991",
        "ca/t657_gains_1992_and_1993",
        "ca/t657_gains_1994",
        "ca/t657_gains_1995",
        "ca/t657_gains_1996_to_1999",
        "ca/t657_gains_2000",
        "ca/t657_gains_2001",
        "ca/t657_gains_2002_to_2024",
        "ca/t657_capital_losses_claimed_1985",
        "ca/t657_abil_claimed_1985_to_2024",
        "ca/t657_t2048_line_17217_for_2024",
        "ca/t657_deductions_claimed_1985_to_2024",
        "ca/t657_chart_2_line_1",
        "ca/t657_chart_2_line_2",
        "ca/t657_chart_2_line_6",
        "ca/t657_chart_2_line_10",
        "ca/t657_chart_2_line_14",
        "ca/t657_inclusion_rate_2000",
        "ca/t657_chart_2_line_18",
        "ca/t657_part_1_amount_f",
        "ca/t657_part_1_amount_g",
        "ca/t657_part_1_amount_h",
        "ca/t657_part_1_amount_l",
        "ca/t657_part_2_excluded_f",
        "ca/t657_part_2_excluded_g",
        "ca/t657_part_2_excluded_h",
        "ca/t657_part_2_amount_l",
        "ca/capital_gains_deduction_claimed",
        "ca/t657_chart_1_rows",
    }
)

# Chart 2025 Part 1 amount Q: the maximum for line 25400 if no other QFFP or QSBCS is disposed of in
# 2025, which nothing reads (Part 2's amount Q is the cap on line 25400).
OUTPUTS = frozenset(
    {
        "ca/chart_2025_part_1_amount_q",
    }
)

STEPS = {
    # Form T657 Step 1 line 1 "Total of lines 10700, 11000, and 12400 of Schedule 3 (if negative,
    # show in brackets)": the gains or losses on QSBCS, QFFP and QFFP foreclosures (Schedule 3 lines
    # 10700, 11000 and 12400), signed.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/qsbcs_gain_or_loss",
                "ca/qffp_gain_or_loss",
                "ca/qffp_foreclosure_gain_or_loss",
            ),
        },
        produces={"output": "ca/annual_gains_schedule_3_total"},
    ),
    # Step 1 line 2 "Total amount from line 13 of Form T2017 (if negative, show in brackets)": the
    # record total of the summary form's line 13 (`ca/t2017.t2017_line_13`, one record).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2017.t2017_line_13"},
        produces={"output": "ca/annual_gains_line_2"},
    ),
    # Step 1 line 3 "Add lines 1 and 2 (if negative, show in brackets)." (line 2 is the total
    # above).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/annual_gains_schedule_3_total",
                "ca/annual_gains_line_2",
            ),
        },
        produces={"output": "ca/annual_gains_line_3"},
    ),
    # Step 1 line 4 "Inclusion rate × 1/2": line 3 multiplied by the 1/2, before line 5 floors it.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_annual_gains_inclusion_rate"},
        consumes={
            "base": "ca/annual_gains_line_3",
        },
        produces={"output": "ca/annual_gains_line_3_at_inclusion_rate"},
    ),
    # Step 1 line 5 "Line 3 multiplied by the inclusion rate on line 4 (if negative, enter "0")".
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": ("ca/annual_gains_line_3_at_inclusion_rate",),
        },
        produces={"output": "ca/annual_gains_line_5"},
    ),
    # Step 1 line 7 "Line 5 minus line 6" "Total taxable capital gains or losses for 2025 for
    # qualifying property" (line 6 "Amount from line 17216 of Form T2048"). The form prints no
    # floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/annual_gains_line_5",
            "less": "ca/qsbcs_qffp_taxable_gains_related_to_deduction",
        },
        produces={"output": "ca/annual_gains_line_7"},
    ),
    # Step 1 line 8 "Total taxable capital gains (or net capital losses) from line 19900 of Schedule
    # 3 (if negative, show in brackets)": Schedule 3 line 24 plus line 25, signed;
    # ca/taxable_capital_gains is the same figure floored at 0 for T1 line 12700.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/included_capital_gain",
                "ca/partnership_gains_at_full_inclusion",
            ),
        },
        produces={"output": "ca/schedule_3_line_19900"},
    ),
    # Step 1 line 9 "Amount from line 17600 of Schedule 3 (if negative, enter "0")".
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": ("ca/t3_capital_gains_or_losses",),
        },
        produces={"output": "ca/schedule_3_line_17600_not_below_zero"},
    ),
    # Step 1 line 9 "× 1/2 =".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_schedule_3_line_17600_fraction"},
        consumes={
            "base": "ca/schedule_3_line_17600_not_below_zero",
        },
        produces={"output": "ca/annual_gains_line_9"},
    ),
    # Step 1 line 10 "Line 8 minus line 9".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/schedule_3_line_19900",
            "less": "ca/annual_gains_line_9",
        },
        produces={"output": "ca/annual_gains_line_10"},
    ),
    # Step 1 line 12 "Line 10 minus line 11" (line 11 "Amount from line 17215 of Form T2048").
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/annual_gains_line_10",
            "less": "ca/qbt_taxable_gains_related_to_deduction",
        },
        produces={"output": "ca/annual_gains_line_12"},
    ),
    # Step 1 line 13 "Enter whichever is less: amount from line 7 or line 12." "Eligible taxable
    # capital gains for 2025".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_line_7",
                "ca/annual_gains_line_12",
            ),
        },
        produces={"output": "ca/eligible_taxable_capital_gains_2025"},
    ),
    # Form T657 Step 1 line 15 "Net non-eligible taxable capital gains in 2025 (line 14 of Chart A
    # of Form T936 for 2025)": the total of `ca/t936.t936_chart_a_line_14`, the form's export (one
    # record). Step 2 line 16 "Cumulative net investment loss to December 31, 2025: Amount from
    # line C in Part 3 of Form T936 for 2025": the total of `ca/t936.t936_cnil` (one record).
    # Neither is an input any more.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t936.t936_chart_a_line_14"},
        produces={"output": "ca/t657_net_non_eligible_taxable_capital_gains"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t936.t936_cnil"},
        produces={"output": "ca/t657_cumulative_net_investment_loss"},
    ),
    # Step 1 line 16 "Adjusted net capital losses of other years: Line 14 minus line 15 (if
    # negative, enter "0")" (line 14 "Net capital losses of other years deducted in 2025 (line 25300
    # of your 2025 return)", line 15 "Net non-eligible taxable capital gains in 2025 (line 14 of
    # Chart A of Form T936 for 2025)").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/net_capital_losses_of_other_years",
            "less": "ca/t657_net_non_eligible_taxable_capital_gains",
        },
        produces={"output": "ca/adjusted_net_capital_losses_of_other_years"},
    ),
    # Step 1 line 19 "Line 17 minus line 18" (line 17 "Allowable business investment losses from
    # line 21700 of your 2025 return.", line 18 "Amount from line 17217 of Form T2048"). The form
    # prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/allowable_business_investment_loss",
            "less": "ca/qbt_abil_reduction",
        },
        produces={"output": "ca/abil_after_qbt_reduction"},
    ),
    # Step 1 line 20 "Line 16 plus line 19" "Total losses for annual gains limit".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/adjusted_net_capital_losses_of_other_years",
                "ca/abil_after_qbt_reduction",
            ),
        },
        produces={"output": "ca/total_losses_for_annual_gains_limit"},
    ),
    # Step 1 line 21 "Line 13 minus line 20 (if negative, enter "0")" "Annual gains limit for 2025".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/eligible_taxable_capital_gains_2025",
            "less": "ca/total_losses_for_annual_gains_limit",
        },
        produces={"output": "ca/annual_gains_limit_2025"},
    ),
    # Chart 1 "Calculate your net capital losses of other years (line 14 of Step 2)": for each year
    # row, column E "(C – D) (If negative, enter "0")", column F "(B + E)" and column G "(A – F) (If
    # negative, enter "0")"; "Add the amounts in column G and enter the result on line 14 of Step
    # 2." One record for each printed row.
    CapabilitySelection(
        name="ca/chart_1_column_g_total",
        params={},
        consumes={
            "rows": "ca/t657_chart_1_rows",
        },
        produces={"total": "ca/chart_1_column_g_total"},
    ),
    # Step 2 line 8 "2002 to 2025 eligible taxable capital gains: Total amount from line 10 in Part
    # 1 of Form T657 for 2002 to 2017, line 8 in Part 1 of Form T657 for 2018 to 2023, line 12 in
    # Step 1 of Form T657 for 2024, and line 13 in Step 1 of Form T657 for 2025": the earlier years
    # are one input, 2025 is Step 1 line 13.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t657_gains_2002_to_2024",
                "ca/eligible_taxable_capital_gains_2025",
            ),
        },
        produces={"output": "ca/eligible_taxable_capital_gains_2002_to_2025"},
    ),
    # Step 2 line 9 "Add lines 1 to 8." "Cumulative eligible taxable capital gains".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t657_gains_1985_to_1991",
                "ca/t657_gains_1992_and_1993",
                "ca/t657_gains_1994",
                "ca/t657_gains_1995",
                "ca/t657_gains_1996_to_1999",
                "ca/t657_gains_2000",
                "ca/t657_gains_2001",
                "ca/eligible_taxable_capital_gains_2002_to_2025",
            ),
        },
        produces={"output": "ca/cumulative_eligible_taxable_capital_gains"},
    ),
    # Step 2 line 13 "Total allowable business investment losses claimed after 1984 and before 2025:
    # Line 11 minus line 12" (line 11 "Total amount from line 217 of your returns for 1985 to 2018
    # and line 21700 of your returns for 2019 to 2024", line 12 "Amount from line 17217 of Form
    # T2048 for 2024"). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t657_abil_claimed_1985_to_2024",
            "less": "ca/t657_t2048_line_17217_for_2024",
        },
        produces={"output": "ca/abil_claimed_after_1984_and_before_2025"},
    ),
    # Step 2 line 18 "Add lines 10 and 13 to 17." (line 10 allowable capital losses claimed in 1985,
    # line 13 above, line 14 "Total of amounts in column G in Chart 1", line 15 "Amount from line 20
    # in Step 1", line 16 "Amount from line C in Part 3 of Form T936 for 2025", line 17 "Total
    # amount from line 254 of your returns for 1985 to 2018 and line 25400 of your returns for 2019
    # to 2024").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t657_capital_losses_claimed_1985",
                "ca/abil_claimed_after_1984_and_before_2025",
                "ca/chart_1_column_g_total",
                "ca/total_losses_for_annual_gains_limit",
                "ca/t657_cumulative_net_investment_loss",
                "ca/t657_deductions_claimed_1985_to_2024",
            ),
        },
        produces={"output": "ca/cumulative_losses_and_deductions"},
    ),
    # Step 2 line 19 "Line 9 minus line 18 (if negative, enter "0")" "Cumulative gains limit for
    # 2025".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cumulative_eligible_taxable_capital_gains",
            "less": "ca/cumulative_losses_and_deductions",
        },
        produces={"output": "ca/cumulative_gains_limit_2025"},
    ),
    # Chart 2 line 3 "Line 1 plus line 2" (line 1 "Amount from line 254 of your 1985 to 1987
    # returns", line 2 "Amount from line 254 of your 1988 and 1989 returns minus any amounts
    # reported on lines 543 and 544 of Schedule 3 for 1988 and 1989 (if negative, enter "0")").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2_line_1",
                "ca/t657_chart_2_line_2",
            ),
        },
        produces={"output": "ca/chart_2_line_3"},
    ),
    # Chart 2 line 4 "Adjustment of 1988 and 1989 capital gains deductions excluding eligible
    # capital property: Amount from line 2 × 1/4".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2_line_4_fraction"},
        consumes={
            "base": "ca/t657_chart_2_line_2",
        },
        produces={"output": "ca/chart_2_line_4"},
    ),
    # Chart 2 line 5 "Line 3 minus line 4 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2_line_3",
            "less": "ca/chart_2_line_4",
        },
        produces={"output": "ca/chart_2_line_5"},
    ),
    # Chart 2 line 7 "Line 5 plus line 6" (line 6 "Capital gains deductions claimed in 1988 and 1989
    # for eligible capital property").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2_line_5",
                "ca/t657_chart_2_line_6",
            ),
        },
        produces={"output": "ca/chart_2_line_7"},
    ),
    # Chart 2 line 8 "Adjustment of 1988 and 1989 capital gains deductions for eligible capital
    # property: Amount from line 6 × 1/3".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2_line_8_fraction"},
        consumes={
            "base": "ca/t657_chart_2_line_6",
        },
        produces={"output": "ca/chart_2_line_8"},
    ),
    # Chart 2 line 9 "Line 7 minus line 8 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2_line_7",
            "less": "ca/chart_2_line_8",
        },
        produces={"output": "ca/chart_2_line_9"},
    ),
    # Chart 2 line 11 "Line 9 plus line 10" (line 10 "Total capital gains deductions claimed in 1990
    # to 1999: Amount from line 254 of your returns for 1990 to 1999").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2_line_9",
                "ca/t657_chart_2_line_10",
            ),
        },
        produces={"output": "ca/chart_2_line_11"},
    ),
    # Chart 2 line 12 "Adjustment of 1990 to 1999 capital gains deductions: Amount from line 10 ×
    # 1/3".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2_line_12_fraction"},
        consumes={
            "base": "ca/t657_chart_2_line_10",
        },
        produces={"output": "ca/chart_2_line_12"},
    ),
    # Chart 2 line 13 "Line 11 minus line 12 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2_line_11",
            "less": "ca/chart_2_line_12",
        },
        produces={"output": "ca/chart_2_line_13"},
    ),
    # Chart 2 line 15 "Line 13 plus line 14" (line 14 "Total capital gains deduction claimed in
    # 2000: Amount from line 254 of your 2000 return").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2_line_13",
                "ca/t657_chart_2_line_14",
            ),
        },
        produces={"output": "ca/chart_2_line_15"},
    ),
    # Chart 2 line 16 "Adjustment of 2000 capital gains deduction: Amount from line 14 × [ 1 – 1/(2
    # × IR)]", first the "2 × IR" (footnote (2) "Your "IR" is your inclusion rate for 2000 from line
    # 16 in Part 4 of your Schedule 3 for 2000 or on your notice of assessment or latest notice of
    # reassessment for 2000."): IR times 2, exact. IR must be entered when line 14 is not 0.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2_twice_ir_fraction"},
        consumes={
            "base": "ca/t657_inclusion_rate_2000",
        },
        produces={"output": "ca/chart_2_twice_ir"},
    ),
    # Chart 2 line 16, the 1 of "1/(2 × IR)": the printed 1 as an artifact.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2_numerator_one"},
        consumes={},
        produces={"output": "ca/chart_2_numerator_one"},
    ),
    # Chart 2 line 16, line 14 × 1 ÷ (2 × IR), rounded once; 0 when IR is 0.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t657_chart_2_line_16_rounding"},
        consumes={
            "amount": "ca/t657_chart_2_line_14",
            "numerator": "ca/chart_2_numerator_one",
            "denominator": "ca/chart_2_twice_ir",
        },
        produces={"output": "ca/chart_2_line_14_over_twice_ir"},
    ),
    # Chart 2 line 16 "Amount from line 14 × [ 1 – 1/(2 × IR)]": line 14 minus line 14 × 1/(2 × IR).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t657_chart_2_line_14",
            "less": "ca/chart_2_line_14_over_twice_ir",
        },
        produces={"output": "ca/chart_2_line_16"},
    ),
    # Chart 2 line 17 "Line 15 minus line 16 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2_line_15",
            "less": "ca/chart_2_line_16",
        },
        produces={"output": "ca/chart_2_line_17"},
    ),
    # Chart 2 line 19 "Capital gains deductions from previous years: Line 17 plus line 18 (if
    # negative, enter 0)" (line 18 "Total capital gains deduction claimed in 2001 to 2024: Amount
    # from line 254 of your 2001 to 2018 returns and line 25400 of your 2019 and later returns").
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/chart_2_line_17",
                "ca/t657_chart_2_line_18",
            ),
        },
        produces={"output": "ca/chart_2_line_19"},
    ),
    # Chart 2025 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS"
    # 522,145.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2025_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2025_part_1_amount_a"},
    ),
    # Chart 2025 Part 1 "Amount A minus amount B" C (B "Enter the last amount that you calculated
    # for "Total amount of capital gains included in 2025 income eligible for the capital gains
    # deduction"" from 2016 to 2024: Chart 2024 Period 2's amount N). The form prints no floor, so
    # the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2025_part_1_amount_a",
            "less": "ca/chart_2024_period_2_amount_n",
        },
        produces={"output": "ca/chart_2025_part_1_amount_c"},
    ),
    # Chart 2025 Part 1 amount E "Capital gains deduction available for QFFP and/or QSBCS ...:
    # amount C minus amount D (if negative, enter "0")" (D "Capital gains deductions from previous
    # years from line 19 of Chart 2").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2025_part_1_amount_c",
            "less": "ca/chart_2_line_19",
        },
        produces={"output": "ca/chart_2025_part_1_amount_e"},
    ),
    # Chart 2025 Part 1 "Add amounts F to J (if negative, enter "0")" (F box 57 of a T3 slip or box
    # 153 of a T5013 slip, G box 55 or box 154, H box 155 of a T5013 slip, I "Amount from line 6 of
    # Form T2017 ...", J "Amount from line 12 of Form T2017 ...", each for a disposition in Period 1
    # of 2024).
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_part_1_amount_f",
                "ca/t657_part_1_amount_g",
                "ca/t657_part_1_amount_h",
                "ca/t657_part_1_amount_i",
                "ca/t657_part_1_amount_j",
            ),
        },
        produces={"output": "ca/chart_2025_part_1_amounts_f_to_j"},
    ),
    # Chart 2025 Part 1 "= × 1/2 = K".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_part_1_k_fraction"},
        consumes={
            "base": "ca/chart_2025_part_1_amounts_f_to_j",
        },
        produces={"output": "ca/chart_2025_part_1_amount_k"},
    ),
    # Chart 2025 Part 1 "Amount K minus amount L" M (L "Portion of the amount from line 17216 of
    # Form T2048 in respect of a QFFP or QSBCS disposed of in the 2025 fiscal period of the
    # partnership but in Period 1 of 2024."). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2025_part_1_amount_k",
            "less": "ca/t657_part_1_amount_l",
        },
        produces={"output": "ca/chart_2025_part_1_amount_m"},
    ),
    # Chart 2025 Part 1 amount N "Enter whichever is less: amount E or amount M.".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2025_part_1_amount_e",
                "ca/chart_2025_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2025_part_1_amount_n"},
    ),
    # Chart 2025 Part 1 "Amount N plus amount O" P (O "Enter amount B from above.", Chart 2024
    # Period 2's amount N).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2025_part_1_amount_n",
                "ca/chart_2024_period_2_amount_n",
            ),
        },
        produces={"output": "ca/chart_2025_part_1_amount_p"},
    ),
    # Chart 2025 Part 1 amount Q "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or
    # amount P above. If you are not disposing of any other QFFP or QSBCS in 2025, this is the
    # maximum amount you can claim on line 25400 of your 2025 return."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2025_part_1_amount_p",
            ),
        },
        produces={"output": "ca/chart_2025_part_1_amount_q"},
    ),
    # Chart 2025 Part 2 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS"
    # 625,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2025_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2025_part_2_amount_a"},
    ),
    # Chart 2025 Part 2 "Amount A minus amount B" C (B "Enter the last amount that you calculated
    # for "Total amount of capital gains included in 2025 income eligible for the capital gains
    # deduction""). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2025_part_2_amount_a",
            "less": "ca/chart_2025_part_1_amount_p",
        },
        produces={"output": "ca/chart_2025_part_2_amount_c"},
    ),
    # Chart 2025 Part 2 amount E "Capital gains deduction available for QFFP and/or QSBCS ...:
    # amount C minus amount D (if negative, enter "0")" (D "Capital gains deductions from previous
    # years from line 19 of Chart 2").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2025_part_2_amount_c",
            "less": "ca/chart_2_line_19",
        },
        produces={"output": "ca/chart_2025_part_2_amount_e"},
    ),
    # Chart 2025 Part 2 amount F "Amount from line 10700 of Schedule 3 (do not include capital gains
    # reported in box 30 of a T3 slip relating to a disposition of QSBCS unless ...)": line 10700
    # less the amounts the filer enters as not to be included.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/qsbcs_gain_or_loss",
            "less": "ca/t657_part_2_excluded_f",
        },
        produces={"output": "ca/chart_2025_part_2_amount_f"},
    ),
    # Chart 2025 Part 2 amount G "Amount from line 11000 of Schedule 3 (do not include capital gains
    # reported in box 30 of a T3 slip relating to a disposition of QFFP unless ...)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/qffp_gain_or_loss",
            "less": "ca/t657_part_2_excluded_g",
        },
        produces={"output": "ca/chart_2025_part_2_amount_g"},
    ),
    # Chart 2025 Part 2 amount H "Amount from line 12400 of Schedule 3 (do not include capital gains
    # reported in box 155 of a T5013 slip)".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/qffp_foreclosure_gain_or_loss",
            "less": "ca/t657_part_2_excluded_h",
        },
        produces={"output": "ca/chart_2025_part_2_amount_h"},
    ),
    # Chart 2025 Part 2 "Add amounts F to J (if negative, enter "0")" (I "Amount from line 6 of Form
    # T2017 (do not include any reserves claimed on dispositions of QFFP before 2025 or in Period 1
    # of 2024 ...)", J "Amount from line 12 of Form T2017 (...)").
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/chart_2025_part_2_amount_f",
                "ca/chart_2025_part_2_amount_g",
                "ca/chart_2025_part_2_amount_h",
                "ca/t657_part_2_amount_i",
                "ca/t657_part_2_amount_j",
            ),
        },
        produces={"output": "ca/chart_2025_part_2_amounts_f_to_j"},
    ),
    # Chart 2025 Part 2 "= × 1/2 = K".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_part_2_k_fraction"},
        consumes={
            "base": "ca/chart_2025_part_2_amounts_f_to_j",
        },
        produces={"output": "ca/chart_2025_part_2_amount_k"},
    ),
    # Chart 2025 Part 2 "Amount K minus amount L" M (L "Portion of the amount from line 17216 of
    # Form T2048 in respect of a QFFP or QSBCS disposed of in 2025 or disposed of in the 2025 fiscal
    # period of the partnership but after June 24, 2024"). The form prints no floor, so the result
    # stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2025_part_2_amount_k",
            "less": "ca/t657_part_2_amount_l",
        },
        produces={"output": "ca/chart_2025_part_2_amount_m"},
    ),
    # Chart 2025 Part 2 amount N "Enter whichever is less: amount E or amount M.".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2025_part_2_amount_e",
                "ca/chart_2025_part_2_amount_m",
            ),
        },
        produces={"output": "ca/chart_2025_part_2_amount_n"},
    ),
    # Chart 2025 Part 2 "Amount N plus amount O" P (O "Enter amount B from above.", B being Part 1
    # amount P).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2025_part_2_amount_n",
                "ca/chart_2025_part_1_amount_p",
            ),
        },
        produces={"output": "ca/chart_2025_part_2_amount_p"},
    ),
    # Chart 2025 Part 2 amount Q "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or
    # amount P above. This is the maximum amount you can claim on line 25400 of your 2025 return.
    # However, you can choose to claim less."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2025_part_2_amount_p",
            ),
        },
        produces={"output": "ca/chart_2025_part_2_amount_q"},
    ),
    # Guide T4037 "Claiming the capital gains deduction": "You can claim any amount of the capital
    # gains deduction that you want to in a year, up to the maximum allowable amount that you
    # calculated." Part 2 amount Q is that maximum; when it is negative (the form prints no floor on
    # C or M) nothing can be claimed, so the limit on the claim is Q not below 0 and a claim of 0 is
    # still allowed.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/chart_2025_part_2_amount_q",)},
        produces={"output": "ca/chart_2025_part_2_maximum_claim"},
    ),
    # T1 line 65 and line 25400 "Capital gains deduction (complete Form T657)": the amount the filer
    # chooses, an input, which may not exceed the maximum claim (Part 2 amount Q not below 0)
    # ("However, you can choose to claim less.").
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/capital_gains_deduction_claimed",
            "bound": "ca/chart_2025_part_2_maximum_claim",
        },
        produces={"output": "ca/capital_gains_deduction"},
    ),
}

WIRING = {
    (
        Sum,
        frozenset({QSBCS_GAIN_OR_LOSS, QFFP_GAIN_OR_LOSS, QFFP_FORECLOSURE_GAIN_OR_LOSS}),
        frozenset({ANNUAL_GAINS_SCHEDULE_3_TOTAL}),
    ),
    (RecordTotal, frozenset({T2017_LINE_13_EXPORT}), frozenset({ANNUAL_GAINS_LINE_2})),
    (
        RecordTotal,
        frozenset({CHART_A_LINE_14_EXPORT}),
        frozenset({T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS}),
    ),
    (RecordTotal, frozenset({CNIL_EXPORT}), frozenset({T657_CUMULATIVE_NET_INVESTMENT_LOSS})),
    (
        Sum,
        frozenset({ANNUAL_GAINS_SCHEDULE_3_TOTAL, ANNUAL_GAINS_LINE_2}),
        frozenset({ANNUAL_GAINS_LINE_3}),
    ),
    (
        ApplyFraction,
        frozenset({ANNUAL_GAINS_LINE_3}),
        frozenset({ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE}),
    ),
    (
        SumNotBelowZero,
        frozenset({ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE}),
        frozenset({ANNUAL_GAINS_LINE_5}),
    ),
    (
        Subtract,
        frozenset({ANNUAL_GAINS_LINE_5, QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION}),
        frozenset({ANNUAL_GAINS_LINE_7}),
    ),
    (
        Sum,
        frozenset({INCLUDED_CAPITAL_GAIN, PARTNERSHIP_GAINS_AT_FULL_INCLUSION}),
        frozenset({SCHEDULE_3_LINE_19900}),
    ),
    (
        SumNotBelowZero,
        frozenset({T3_CAPITAL_GAINS_OR_LOSSES}),
        frozenset({SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO}),
    ),
    (
        ApplyFraction,
        frozenset({SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO}),
        frozenset({ANNUAL_GAINS_LINE_9}),
    ),
    (
        Subtract,
        frozenset({SCHEDULE_3_LINE_19900, ANNUAL_GAINS_LINE_9}),
        frozenset({ANNUAL_GAINS_LINE_10}),
    ),
    (
        Subtract,
        frozenset({ANNUAL_GAINS_LINE_10, QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION}),
        frozenset({ANNUAL_GAINS_LINE_12}),
    ),
    (
        LesserOf,
        frozenset({ANNUAL_GAINS_LINE_7, ANNUAL_GAINS_LINE_12}),
        frozenset({ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({NET_CAPITAL_LOSSES_OF_OTHER_YEARS, T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS}),
        frozenset({ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS}),
    ),
    (
        Subtract,
        frozenset({ALLOWABLE_BUSINESS_INVESTMENT_LOSS, QBT_ABIL_REDUCTION}),
        frozenset({ABIL_AFTER_QBT_REDUCTION}),
    ),
    (
        Sum,
        frozenset({ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS, ABIL_AFTER_QBT_REDUCTION}),
        frozenset({TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025, TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT}),
        frozenset({ANNUAL_GAINS_LIMIT_2025}),
    ),
    (
        Chart1ColumnGTotal,
        frozenset({T657_CHART_1_ROWS}),
        frozenset({CHART_1_COLUMN_G_TOTAL}),
    ),
    (
        Sum,
        frozenset({T657_GAINS_2002_TO_2024, ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025}),
        frozenset({ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025}),
    ),
    (
        Sum,
        frozenset(
            {
                T657_GAINS_1985_TO_1991,
                T657_GAINS_1992_AND_1993,
                T657_GAINS_1994,
                T657_GAINS_1995,
                T657_GAINS_1996_TO_1999,
                T657_GAINS_2000,
                T657_GAINS_2001,
                ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
            }
        ),
        frozenset({CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS}),
    ),
    (
        Subtract,
        frozenset({T657_ABIL_CLAIMED_1985_TO_2024, T657_T2048_LINE_17217_FOR_2024}),
        frozenset({ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025}),
    ),
    (
        Sum,
        frozenset(
            {
                T657_CAPITAL_LOSSES_CLAIMED_1985,
                ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025,
                CHART_1_COLUMN_G_TOTAL,
                TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT,
                T657_CUMULATIVE_NET_INVESTMENT_LOSS,
                T657_DEDUCTIONS_CLAIMED_1985_TO_2024,
            }
        ),
        frozenset({CUMULATIVE_LOSSES_AND_DEDUCTIONS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS, CUMULATIVE_LOSSES_AND_DEDUCTIONS}),
        frozenset({CUMULATIVE_GAINS_LIMIT_2025}),
    ),
    (
        Sum,
        frozenset({T657_CHART_2_LINE_1, T657_CHART_2_LINE_2}),
        frozenset({CHART_2_LINE_3}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2_LINE_2}),
        frozenset({CHART_2_LINE_4}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2_LINE_3, CHART_2_LINE_4}),
        frozenset({CHART_2_LINE_5}),
    ),
    (
        Sum,
        frozenset({CHART_2_LINE_5, T657_CHART_2_LINE_6}),
        frozenset({CHART_2_LINE_7}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2_LINE_6}),
        frozenset({CHART_2_LINE_8}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2_LINE_7, CHART_2_LINE_8}),
        frozenset({CHART_2_LINE_9}),
    ),
    (
        Sum,
        frozenset({CHART_2_LINE_9, T657_CHART_2_LINE_10}),
        frozenset({CHART_2_LINE_11}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2_LINE_10}),
        frozenset({CHART_2_LINE_12}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2_LINE_11, CHART_2_LINE_12}),
        frozenset({CHART_2_LINE_13}),
    ),
    (
        Sum,
        frozenset({CHART_2_LINE_13, T657_CHART_2_LINE_14}),
        frozenset({CHART_2_LINE_15}),
    ),
    (
        ApplyFraction,
        frozenset({T657_INCLUSION_RATE_2000}),
        frozenset({CHART_2_TWICE_IR}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2_NUMERATOR_ONE}),
    ),
    (
        ApplyRatioOrZero,
        frozenset({T657_CHART_2_LINE_14, CHART_2_NUMERATOR_ONE, CHART_2_TWICE_IR}),
        frozenset({CHART_2_LINE_14_OVER_TWICE_IR}),
    ),
    (
        Subtract,
        frozenset({T657_CHART_2_LINE_14, CHART_2_LINE_14_OVER_TWICE_IR}),
        frozenset({CHART_2_LINE_16}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2_LINE_15, CHART_2_LINE_16}),
        frozenset({CHART_2_LINE_17}),
    ),
    (
        SumNotBelowZero,
        frozenset({CHART_2_LINE_17, T657_CHART_2_LINE_18}),
        frozenset({CHART_2_LINE_19}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2025_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2025_PART_1_AMOUNT_A, CHART_2024_PERIOD_2_AMOUNT_N}),
        frozenset({CHART_2025_PART_1_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2025_PART_1_AMOUNT_C, CHART_2_LINE_19}),
        frozenset({CHART_2025_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_PART_1_AMOUNT_F,
                T657_PART_1_AMOUNT_G,
                T657_PART_1_AMOUNT_H,
                T657_PART_1_AMOUNT_I,
                T657_PART_1_AMOUNT_J,
            }
        ),
        frozenset({CHART_2025_PART_1_AMOUNTS_F_TO_J}),
    ),
    (
        ApplyFraction,
        frozenset({CHART_2025_PART_1_AMOUNTS_F_TO_J}),
        frozenset({CHART_2025_PART_1_AMOUNT_K}),
    ),
    (
        Subtract,
        frozenset({CHART_2025_PART_1_AMOUNT_K, T657_PART_1_AMOUNT_L}),
        frozenset({CHART_2025_PART_1_AMOUNT_M}),
    ),
    (
        LesserOf,
        frozenset({CHART_2025_PART_1_AMOUNT_E, CHART_2025_PART_1_AMOUNT_M}),
        frozenset({CHART_2025_PART_1_AMOUNT_N}),
    ),
    (
        Sum,
        frozenset({CHART_2025_PART_1_AMOUNT_N, CHART_2024_PERIOD_2_AMOUNT_N}),
        frozenset({CHART_2025_PART_1_AMOUNT_P}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2025_PART_1_AMOUNT_P}
        ),
        frozenset({CHART_2025_PART_1_AMOUNT_Q}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2025_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2025_PART_2_AMOUNT_A, CHART_2025_PART_1_AMOUNT_P}),
        frozenset({CHART_2025_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2025_PART_2_AMOUNT_C, CHART_2_LINE_19}),
        frozenset({CHART_2025_PART_2_AMOUNT_E}),
    ),
    (
        Subtract,
        frozenset({QSBCS_GAIN_OR_LOSS, T657_PART_2_EXCLUDED_F}),
        frozenset({CHART_2025_PART_2_AMOUNT_F}),
    ),
    (
        Subtract,
        frozenset({QFFP_GAIN_OR_LOSS, T657_PART_2_EXCLUDED_G}),
        frozenset({CHART_2025_PART_2_AMOUNT_G}),
    ),
    (
        Subtract,
        frozenset({QFFP_FORECLOSURE_GAIN_OR_LOSS, T657_PART_2_EXCLUDED_H}),
        frozenset({CHART_2025_PART_2_AMOUNT_H}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                CHART_2025_PART_2_AMOUNT_F,
                CHART_2025_PART_2_AMOUNT_G,
                CHART_2025_PART_2_AMOUNT_H,
                T657_PART_2_AMOUNT_I,
                T657_PART_2_AMOUNT_J,
            }
        ),
        frozenset({CHART_2025_PART_2_AMOUNTS_F_TO_J}),
    ),
    (
        ApplyFraction,
        frozenset({CHART_2025_PART_2_AMOUNTS_F_TO_J}),
        frozenset({CHART_2025_PART_2_AMOUNT_K}),
    ),
    (
        Subtract,
        frozenset({CHART_2025_PART_2_AMOUNT_K, T657_PART_2_AMOUNT_L}),
        frozenset({CHART_2025_PART_2_AMOUNT_M}),
    ),
    (
        LesserOf,
        frozenset({CHART_2025_PART_2_AMOUNT_E, CHART_2025_PART_2_AMOUNT_M}),
        frozenset({CHART_2025_PART_2_AMOUNT_N}),
    ),
    (
        Sum,
        frozenset({CHART_2025_PART_2_AMOUNT_N, CHART_2025_PART_1_AMOUNT_P}),
        frozenset({CHART_2025_PART_2_AMOUNT_P}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2025_PART_2_AMOUNT_P}
        ),
        frozenset({CHART_2025_PART_2_AMOUNT_Q}),
    ),
    (
        SumNotBelowZero,
        frozenset({CHART_2025_PART_2_AMOUNT_Q}),
        frozenset({CHART_2025_PART_2_MAXIMUM_CLAIM}),
    ),
    (
        AtMost,
        frozenset({CAPITAL_GAINS_DEDUCTION_CLAIMED, CHART_2025_PART_2_MAXIMUM_CLAIM}),
        frozenset({CAPITAL_GAINS_DEDUCTION}),
    ),
}
