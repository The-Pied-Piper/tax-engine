"""The CA-ON manifest entries of Form T657 Charts 2021, 2022 and 2023, Part 1 and Part 2 each
(`test_manifest.py`).

The steps are in the manifest part `06d_capital_gains_deduction_t657_charts_2021_to_2023.yaml`.
The charts are computed in the form's year order: each chart's amount B is the last total carried
in from the chart before it (Chart 2021 reads Chart 2020's total carried,
`ca/chart_2020_total_carried`; Chart 2022
reads Chart 2021's total; Chart 2023 reads Chart 2022's). Each chart's total carried is Part 2's
amount L when Part 2 is completed, else Part 1's amount M. Chart 2024 Period 1 reads Chart 2023's
total, and that family is `capital_gains_deduction_t657_charts`.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LIMIT_2025,
    CHART_2_LINE_19,
    CHART_2020_TOTAL_CARRIED,
    CHART_2021_AMOUNT_D,
    CHART_2021_PART_1_AMOUNT_A,
    CHART_2021_PART_1_AMOUNT_C,
    CHART_2021_PART_1_AMOUNT_E,
    CHART_2021_PART_1_AMOUNT_H,
    CHART_2021_PART_1_AMOUNT_I,
    CHART_2021_PART_1_AMOUNT_J,
    CHART_2021_PART_1_AMOUNT_K,
    CHART_2021_PART_1_AMOUNT_M,
    CHART_2021_PART_1_AMOUNT_N,
    CHART_2021_PART_1_AMOUNTS_F_AND_G,
    CHART_2021_PART_2_AMOUNT_A,
    CHART_2021_PART_2_AMOUNT_C,
    CHART_2021_PART_2_AMOUNT_E,
    CHART_2021_PART_2_AMOUNT_F,
    CHART_2021_PART_2_AMOUNT_G,
    CHART_2021_PART_2_AMOUNT_H,
    CHART_2021_PART_2_AMOUNT_I,
    CHART_2021_PART_2_AMOUNT_K,
    CHART_2021_PART_2_AMOUNT_L,
    CHART_2021_PART_2_AMOUNT_M,
    CHART_2021_PART_2_APPLIES,
    CHART_2021_TOTAL_CARRIED,
    CHART_2022_AMOUNT_D,
    CHART_2022_PART_1_AMOUNT_A,
    CHART_2022_PART_1_AMOUNT_C,
    CHART_2022_PART_1_AMOUNT_E,
    CHART_2022_PART_1_AMOUNT_H,
    CHART_2022_PART_1_AMOUNT_I,
    CHART_2022_PART_1_AMOUNT_J,
    CHART_2022_PART_1_AMOUNT_K,
    CHART_2022_PART_1_AMOUNT_M,
    CHART_2022_PART_1_AMOUNT_N,
    CHART_2022_PART_1_AMOUNTS_F_AND_G,
    CHART_2022_PART_2_AMOUNT_A,
    CHART_2022_PART_2_AMOUNT_C,
    CHART_2022_PART_2_AMOUNT_E,
    CHART_2022_PART_2_AMOUNT_F,
    CHART_2022_PART_2_AMOUNT_G,
    CHART_2022_PART_2_AMOUNT_H,
    CHART_2022_PART_2_AMOUNT_I,
    CHART_2022_PART_2_AMOUNT_K,
    CHART_2022_PART_2_AMOUNT_L,
    CHART_2022_PART_2_AMOUNT_M,
    CHART_2022_PART_2_APPLIES,
    CHART_2022_TOTAL_CARRIED,
    CHART_2023_AMOUNT_D,
    CHART_2023_PART_1_AMOUNT_A,
    CHART_2023_PART_1_AMOUNT_C,
    CHART_2023_PART_1_AMOUNT_E,
    CHART_2023_PART_1_AMOUNT_H,
    CHART_2023_PART_1_AMOUNT_I,
    CHART_2023_PART_1_AMOUNT_J,
    CHART_2023_PART_1_AMOUNT_K,
    CHART_2023_PART_1_AMOUNT_M,
    CHART_2023_PART_1_AMOUNT_N,
    CHART_2023_PART_1_AMOUNTS_F_AND_G,
    CHART_2023_PART_2_AMOUNT_A,
    CHART_2023_PART_2_AMOUNT_C,
    CHART_2023_PART_2_AMOUNT_E,
    CHART_2023_PART_2_AMOUNT_F,
    CHART_2023_PART_2_AMOUNT_G,
    CHART_2023_PART_2_AMOUNT_H,
    CHART_2023_PART_2_AMOUNT_I,
    CHART_2023_PART_2_AMOUNT_K,
    CHART_2023_PART_2_AMOUNT_L,
    CHART_2023_PART_2_AMOUNT_M,
    CHART_2023_PART_2_APPLIES,
    CHART_2023_TOTAL_CARRIED,
    CUMULATIVE_GAINS_LIMIT_2025,
    T657_CHART_2021_AMOUNT_D_INSTEAD,
    T657_CHART_2021_AMOUNT_F,
    T657_CHART_2021_AMOUNT_G,
    T657_CHART_2021_AMOUNT_I,
    T657_CHART_2021_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2021_PART_2_AMOUNT_G,
    T657_CHART_2021_USES_D_INSTEAD_CHECKED,
    T657_CHART_2022_AMOUNT_D_INSTEAD,
    T657_CHART_2022_AMOUNT_F,
    T657_CHART_2022_AMOUNT_G,
    T657_CHART_2022_AMOUNT_I,
    T657_CHART_2022_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2022_PART_2_AMOUNT_G,
    T657_CHART_2022_USES_D_INSTEAD_CHECKED,
    T657_CHART_2023_AMOUNT_D_INSTEAD,
    T657_CHART_2023_AMOUNT_F,
    T657_CHART_2023_AMOUNT_G,
    T657_CHART_2023_AMOUNT_I,
    T657_CHART_2023_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2023_PART_2_AMOUNT_G,
    T657_CHART_2023_USES_D_INSTEAD_CHECKED,
)

INPUTS = frozenset(
    {
        "ca/t657_chart_2021_uses_d_instead",
        "ca/t657_chart_2021_amount_d_instead",
        "ca/t657_chart_2021_amount_i",
        "ca/t657_chart_2021_part_2_amount_g",
        "ca/t657_chart_2021_claims_additional_deduction",
        "ca/t657_chart_2022_uses_d_instead",
        "ca/t657_chart_2022_amount_d_instead",
        "ca/t657_chart_2022_amount_i",
        "ca/t657_chart_2022_part_2_amount_g",
        "ca/t657_chart_2022_claims_additional_deduction",
        "ca/t657_chart_2023_uses_d_instead",
        "ca/t657_chart_2023_amount_d_instead",
        "ca/t657_chart_2023_amount_i",
        "ca/t657_chart_2023_part_2_amount_g",
        "ca/t657_chart_2023_claims_additional_deduction",
    }
)

# Amount N of Part 1 and amount M of Part 2 of each chart: the maximum for line 25400 if no later
# reserve is reported, which nothing reads (the carried total is the chart's total carried).
OUTPUTS = frozenset(
    {
        "ca/chart_2021_part_1_amount_n",
        "ca/chart_2021_part_2_amount_m",
        "ca/chart_2022_part_1_amount_n",
        "ca/chart_2022_part_2_amount_m",
        "ca/chart_2023_part_1_amount_n",
        "ca/chart_2023_part_2_amount_m",
    }
)

STEPS = {
    # --- Chart 2021 Part 1 ---
    # Chart 2021 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS disposed of
    # in 2021" 446,109.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2021_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2021_part_1_amount_a"},
    ),
    # Chart 2021 Part 1 "Amount A minus amount B" C (B "Enter the last amount that you calculated
    # for
    # "Total amount of capital gains included in 2025 income eligible for the capital gains
    # deduction" from 2016 to 2020. If you did not complete charts for 2016 to 2020, enter "0".").
    # The
    # form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2021_part_1_amount_a",
            "less": "ca/chart_2020_total_carried",
        },
        produces={"output": "ca/chart_2021_part_1_amount_c"},
    ),
    # Chart 2021 amount D: "Capital gains deductions from previous years from line 19 of Chart 2
    # (2021-1)", or, when the filer claimed a deduction for other eligible capital gains from 2021
    # to
    # 2024, the "(2021-1)" calculation, whose result the caller enters at amount D (uses_d_instead
    # 1).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2021_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2021_amount_d_instead",
        },
        produces={"output": "ca/chart_2021_amount_d"},
    ),
    # Chart 2021 Part 1 "Capital gains deduction available for QFFP and/or QSBCS disposed of in 2021
    # and included in your 2025 income: amount C minus amount D (if negative, enter "0")" E.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2021_part_1_amount_c",
            "less": "ca/chart_2021_amount_d",
        },
        produces={"output": "ca/chart_2021_part_1_amount_e"},
    ),
    # Chart 2021 Part 1 "Taxable capital gains from a reserve on QFFP and/or QSBCS disposed of in
    # 2021
    # included in your 2025 income: amount F plus amount G (if negative, enter "0")", F "Amount from
    # line 6 of Form T2017" and G "Amount from line 12 of Form T2017".
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2021_amount_f",
                "ca/t657_chart_2021_amount_g",
            ),
        },
        produces={"output": "ca/chart_2021_part_1_amounts_f_and_g"},
    ),
    # Chart 2021 Part 1 "× 1/2 = H" (the amounts F and G, times the 1/2 printed on the form).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2021_part_1_h_fraction"},
        consumes={
            "base": "ca/chart_2021_part_1_amounts_f_and_g",
        },
        produces={"output": "ca/chart_2021_part_1_amount_h"},
    ),
    # Chart 2021 Part 1 "Amount included in box 30 of a 2025 T3 slip and the footnote area indicates
    # the property was disposed of in 2021 × 1/2 = +" I (the caller's box 30 amount).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2021_part_1_i_fraction"},
        consumes={
            "base": "ca/t657_chart_2021_amount_i",
        },
        produces={"output": "ca/chart_2021_part_1_amount_i"},
    ),
    # Chart 2021 Part 1 "Amount H plus amount I" J.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2021_part_1_amount_h",
                "ca/chart_2021_part_1_amount_i",
            ),
        },
        produces={"output": "ca/chart_2021_part_1_amount_j"},
    ),
    # Chart 2021 Part 1 "Enter whichever is less: amount E or amount J." K.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2021_part_1_amount_e",
                "ca/chart_2021_part_1_amount_j",
            ),
        },
        produces={"output": "ca/chart_2021_part_1_amount_k"},
    ),
    # Chart 2021 Part 1 "Amount K plus amount L" M (L "Enter amount B from above.").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2021_part_1_amount_k",
                "ca/chart_2020_total_carried",
            ),
        },
        produces={"output": "ca/chart_2021_part_1_amount_m"},
    ),
    # Chart 2021 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount M
    # above." N, the maximum for line 25400 if no other reserve is reported.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2021_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2021_part_1_amount_n"},
    ),
    # --- Chart 2021 Part 2 ---
    # Chart 2021 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2021"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2021_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2021_part_2_amount_a"},
    ),
    # Chart 2021 Part 2 "Amount A minus amount B" C (B "Enter amount M from Part 1 of Chart 2021.").
    # The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2021_part_2_amount_a",
            "less": "ca/chart_2021_part_1_amount_m",
        },
        produces={"output": "ca/chart_2021_part_2_amount_c"},
    ),
    # Chart 2021 Part 2 "Capital gains deduction available for QFFP disposed of in 2021 included in
    # your 2025 income: amount C minus amount D (if negative, enter "0")" E (D as in Part 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2021_part_2_amount_c",
            "less": "ca/chart_2021_amount_d",
        },
        produces={"output": "ca/chart_2021_part_2_amount_e"},
    ),
    # Chart 2021 Part 2 "Amount from line 6 of Form T2017 ... × 1/2 = F" (Part 1's F input).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2021_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2021_amount_f",
        },
        produces={"output": "ca/chart_2021_part_2_amount_f"},
    ),
    # Chart 2021 Part 2 "Amount included in box 30 of a 2025 T3 slip ... QFFP ... × 1/2 = G".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2021_part_2_g_fraction"},
        consumes={
            "base": "ca/t657_chart_2021_part_2_amount_g",
        },
        produces={"output": "ca/chart_2021_part_2_amount_g"},
    ),
    # Chart 2021 Part 2 "Amount F plus amount G" H.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2021_part_2_amount_f",
                "ca/chart_2021_part_2_amount_g",
            ),
        },
        produces={"output": "ca/chart_2021_part_2_amount_h"},
    ),
    # Chart 2021 Part 2 "Enter whichever is less: amount E or amount H." I.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2021_part_2_amount_e",
                "ca/chart_2021_part_2_amount_h",
            ),
        },
        produces={"output": "ca/chart_2021_part_2_amount_i"},
    ),
    # Chart 2021 Part 2 "Amount I plus amount J" K (J "Enter amount B from above.", Part 1's M).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2021_part_2_amount_i",
                "ca/chart_2021_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2021_part_2_amount_k"},
    ),
    # Chart 2021 Part 2 "Enter whichever is less: amount H or amount K." L.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2021_part_2_amount_h",
                "ca/chart_2021_part_2_amount_k",
            ),
        },
        produces={"output": "ca/chart_2021_part_2_amount_l"},
    ),
    # Chart 2021 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount L
    # above." M, the maximum for line 25400 if no other disposition is reported.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2021_part_2_amount_l",
            ),
        },
        produces={"output": "ca/chart_2021_part_2_amount_m"},
    ),
    # Chart 2021 Part 2 is completed only when the filer reports a QFFP reserve and "you want to
    # claim the additional deduction, complete Part 2", and amount E of Part 1 is equal to or less
    # than the three amounts the form names. The count is 1 when none of its conditions applies,
    # else 0 (the `t657_chart_2021_part_2_conditions` dataset).
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2021_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2021_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2021_part_1_amount_e",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2021_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2021_part_2_applies"},
    ),
    # The total carried forward: Part 2's amount L when Part 2 is completed, else Part 1's amount M
    # (the form: "Enter the last amount that you calculated" for the charts that follow).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2021_part_2_applies",
            "when_none": "ca/chart_2021_part_1_amount_m",
            "when_any": "ca/chart_2021_part_2_amount_l",
        },
        produces={"output": "ca/chart_2021_total_carried"},
    ),
    # --- Chart 2022 Part 1 ---
    # Chart 2022 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS disposed of
    # in 2022" 456,815.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2022_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2022_part_1_amount_a"},
    ),
    # Chart 2022 Part 1 "Amount A minus amount B" C (B is Chart 2021's total carried).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2022_part_1_amount_a",
            "less": "ca/chart_2021_total_carried",
        },
        produces={"output": "ca/chart_2022_part_1_amount_c"},
    ),
    # Chart 2022 amount D: "Capital gains deductions from previous years from line 19 of Chart 2
    # (2022-1)", or the "(2022-1)" calculation's result when uses_d_instead is 1.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2022_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2022_amount_d_instead",
        },
        produces={"output": "ca/chart_2022_amount_d"},
    ),
    # Chart 2022 Part 1 amount E "amount C minus amount D (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2022_part_1_amount_c",
            "less": "ca/chart_2022_amount_d",
        },
        produces={"output": "ca/chart_2022_part_1_amount_e"},
    ),
    # Chart 2022 Part 1 "amount F plus amount G (if negative, enter "0")".
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2022_amount_f",
                "ca/t657_chart_2022_amount_g",
            ),
        },
        produces={"output": "ca/chart_2022_part_1_amounts_f_and_g"},
    ),
    # Chart 2022 Part 1 "× 1/2 = H".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2022_part_1_h_fraction"},
        consumes={
            "base": "ca/chart_2022_part_1_amounts_f_and_g",
        },
        produces={"output": "ca/chart_2022_part_1_amount_h"},
    ),
    # Chart 2022 Part 1 box 30 amount "× 1/2 = +" I.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2022_part_1_i_fraction"},
        consumes={
            "base": "ca/t657_chart_2022_amount_i",
        },
        produces={"output": "ca/chart_2022_part_1_amount_i"},
    ),
    # Chart 2022 Part 1 "Amount H plus amount I" J.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2022_part_1_amount_h",
                "ca/chart_2022_part_1_amount_i",
            ),
        },
        produces={"output": "ca/chart_2022_part_1_amount_j"},
    ),
    # Chart 2022 Part 1 "Enter whichever is less: amount E or amount J." K.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2022_part_1_amount_e",
                "ca/chart_2022_part_1_amount_j",
            ),
        },
        produces={"output": "ca/chart_2022_part_1_amount_k"},
    ),
    # Chart 2022 Part 1 "Amount K plus amount L" M (L is Chart 2021's total carried).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2022_part_1_amount_k",
                "ca/chart_2021_total_carried",
            ),
        },
        produces={"output": "ca/chart_2022_part_1_amount_m"},
    ),
    # Chart 2022 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount M
    # above." N.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2022_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2022_part_1_amount_n"},
    ),
    # --- Chart 2022 Part 2 ---
    # Chart 2022 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2022"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2022_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2022_part_2_amount_a"},
    ),
    # Chart 2022 Part 2 "Amount A minus amount B" C (B "Enter amount M from Part 1 of Chart 2022.").
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2022_part_2_amount_a",
            "less": "ca/chart_2022_part_1_amount_m",
        },
        produces={"output": "ca/chart_2022_part_2_amount_c"},
    ),
    # Chart 2022 Part 2 amount E "amount C minus amount D (if negative, enter "0")" (D as in Part
    # 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2022_part_2_amount_c",
            "less": "ca/chart_2022_amount_d",
        },
        produces={"output": "ca/chart_2022_part_2_amount_e"},
    ),
    # Chart 2022 Part 2 "× 1/2 = F" (Part 1's F input).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2022_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2022_amount_f",
        },
        produces={"output": "ca/chart_2022_part_2_amount_f"},
    ),
    # Chart 2022 Part 2 box 30 QFFP amount "× 1/2 = G".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2022_part_2_g_fraction"},
        consumes={
            "base": "ca/t657_chart_2022_part_2_amount_g",
        },
        produces={"output": "ca/chart_2022_part_2_amount_g"},
    ),
    # Chart 2022 Part 2 "Amount F plus amount G" H.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2022_part_2_amount_f",
                "ca/chart_2022_part_2_amount_g",
            ),
        },
        produces={"output": "ca/chart_2022_part_2_amount_h"},
    ),
    # Chart 2022 Part 2 "Enter whichever is less: amount E or amount H." I.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2022_part_2_amount_e",
                "ca/chart_2022_part_2_amount_h",
            ),
        },
        produces={"output": "ca/chart_2022_part_2_amount_i"},
    ),
    # Chart 2022 Part 2 "Amount I plus amount J" K (J "Enter amount B from above.", Part 1's M).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2022_part_2_amount_i",
                "ca/chart_2022_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2022_part_2_amount_k"},
    ),
    # Chart 2022 Part 2 "Enter whichever is less: amount H or amount K." L.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2022_part_2_amount_h",
                "ca/chart_2022_part_2_amount_k",
            ),
        },
        produces={"output": "ca/chart_2022_part_2_amount_l"},
    ),
    # Chart 2022 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount L
    # above." M.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2022_part_2_amount_l",
            ),
        },
        produces={"output": "ca/chart_2022_part_2_amount_m"},
    ),
    # Chart 2022 gate: Part 2 is completed on the same conditions as Chart 2021's (the
    # `t657_chart_2022_part_2_conditions` dataset).
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2022_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2022_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2022_part_1_amount_e",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2022_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2022_part_2_applies"},
    ),
    # Chart 2022 total carried: Part 2's amount L when Part 2 is completed, else Part 1's amount M.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2022_part_2_applies",
            "when_none": "ca/chart_2022_part_1_amount_m",
            "when_any": "ca/chart_2022_part_2_amount_l",
        },
        produces={"output": "ca/chart_2022_total_carried"},
    ),
    # --- Chart 2023 Part 1 ---
    # Chart 2023 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS disposed of
    # in 2023" 485,595.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2023_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2023_part_1_amount_a"},
    ),
    # Chart 2023 Part 1 "Amount A minus amount B" C (B is Chart 2022's total carried).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2023_part_1_amount_a",
            "less": "ca/chart_2022_total_carried",
        },
        produces={"output": "ca/chart_2023_part_1_amount_c"},
    ),
    # Chart 2023 amount D: "Capital gains deductions from previous years from line 19 of Chart 2
    # (2023-1)", or the "(2023-1)" calculation's result when uses_d_instead is 1.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2023_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2023_amount_d_instead",
        },
        produces={"output": "ca/chart_2023_amount_d"},
    ),
    # Chart 2023 Part 1 amount E "amount C minus amount D (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2023_part_1_amount_c",
            "less": "ca/chart_2023_amount_d",
        },
        produces={"output": "ca/chart_2023_part_1_amount_e"},
    ),
    # Chart 2023 Part 1 "amount F plus amount G (if negative, enter "0")".
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2023_amount_f",
                "ca/t657_chart_2023_amount_g",
            ),
        },
        produces={"output": "ca/chart_2023_part_1_amounts_f_and_g"},
    ),
    # Chart 2023 Part 1 "× 1/2 = H".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2023_part_1_h_fraction"},
        consumes={
            "base": "ca/chart_2023_part_1_amounts_f_and_g",
        },
        produces={"output": "ca/chart_2023_part_1_amount_h"},
    ),
    # Chart 2023 Part 1 box 30 amount "× 1/2 = +" I.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2023_part_1_i_fraction"},
        consumes={
            "base": "ca/t657_chart_2023_amount_i",
        },
        produces={"output": "ca/chart_2023_part_1_amount_i"},
    ),
    # Chart 2023 Part 1 "Amount H plus amount I" J.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2023_part_1_amount_h",
                "ca/chart_2023_part_1_amount_i",
            ),
        },
        produces={"output": "ca/chart_2023_part_1_amount_j"},
    ),
    # Chart 2023 Part 1 "Enter whichever is less: amount E or amount J." K.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2023_part_1_amount_e",
                "ca/chart_2023_part_1_amount_j",
            ),
        },
        produces={"output": "ca/chart_2023_part_1_amount_k"},
    ),
    # Chart 2023 Part 1 "Amount K plus amount L" M (L is Chart 2022's total carried).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2023_part_1_amount_k",
                "ca/chart_2022_total_carried",
            ),
        },
        produces={"output": "ca/chart_2023_part_1_amount_m"},
    ),
    # Chart 2023 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount M
    # above." N.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2023_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2023_part_1_amount_n"},
    ),
    # --- Chart 2023 Part 2 ---
    # Chart 2023 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2023"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2023_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2023_part_2_amount_a"},
    ),
    # Chart 2023 Part 2 "Amount A minus amount B" C (B "Enter amount M from Part 1 of Chart 2023.").
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2023_part_2_amount_a",
            "less": "ca/chart_2023_part_1_amount_m",
        },
        produces={"output": "ca/chart_2023_part_2_amount_c"},
    ),
    # Chart 2023 Part 2 amount E "amount C minus amount D (if negative, enter "0")" (D as in Part
    # 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2023_part_2_amount_c",
            "less": "ca/chart_2023_amount_d",
        },
        produces={"output": "ca/chart_2023_part_2_amount_e"},
    ),
    # Chart 2023 Part 2 "× 1/2 = F" (Part 1's F input).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2023_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2023_amount_f",
        },
        produces={"output": "ca/chart_2023_part_2_amount_f"},
    ),
    # Chart 2023 Part 2 box 30 QFFP amount "× 1/2 = G".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2023_part_2_g_fraction"},
        consumes={
            "base": "ca/t657_chart_2023_part_2_amount_g",
        },
        produces={"output": "ca/chart_2023_part_2_amount_g"},
    ),
    # Chart 2023 Part 2 "Amount F plus amount G" H.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2023_part_2_amount_f",
                "ca/chart_2023_part_2_amount_g",
            ),
        },
        produces={"output": "ca/chart_2023_part_2_amount_h"},
    ),
    # Chart 2023 Part 2 "Enter whichever is less: amount E or amount H." I.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2023_part_2_amount_e",
                "ca/chart_2023_part_2_amount_h",
            ),
        },
        produces={"output": "ca/chart_2023_part_2_amount_i"},
    ),
    # Chart 2023 Part 2 "Amount I plus amount J" K (J "Enter amount B from above.", Part 1's M).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2023_part_2_amount_i",
                "ca/chart_2023_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2023_part_2_amount_k"},
    ),
    # Chart 2023 Part 2 "Enter whichever is less: amount H or amount K." L.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2023_part_2_amount_h",
                "ca/chart_2023_part_2_amount_k",
            ),
        },
        produces={"output": "ca/chart_2023_part_2_amount_l"},
    ),
    # Chart 2023 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount L
    # above." M.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2023_part_2_amount_l",
            ),
        },
        produces={"output": "ca/chart_2023_part_2_amount_m"},
    ),
    # Chart 2023 gate (the `t657_chart_2023_part_2_conditions` dataset, as Chart 2021's).
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2023_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2023_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2023_part_1_amount_e",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2023_part_1_amount_m",
            ),
        },
        produces={"output": "ca/chart_2023_part_2_applies"},
    ),
    # Chart 2023 total carried: Part 2's amount L when Part 2 is completed, else Part 1's amount M.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2023_part_2_applies",
            "when_none": "ca/chart_2023_part_1_amount_m",
            "when_any": "ca/chart_2023_part_2_amount_l",
        },
        produces={"output": "ca/chart_2023_total_carried"},
    ),
}

WIRING = {
    # Chart 2021 Part 1.
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2021_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2021_PART_1_AMOUNT_A, CHART_2020_TOTAL_CARRIED}),
        frozenset({CHART_2021_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                T657_CHART_2021_USES_D_INSTEAD_CHECKED,
                CHART_2_LINE_19,
                T657_CHART_2021_AMOUNT_D_INSTEAD,
            }
        ),
        frozenset({CHART_2021_AMOUNT_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2021_PART_1_AMOUNT_C, CHART_2021_AMOUNT_D}),
        frozenset({CHART_2021_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset({T657_CHART_2021_AMOUNT_F, T657_CHART_2021_AMOUNT_G}),
        frozenset({CHART_2021_PART_1_AMOUNTS_F_AND_G}),
    ),
    (
        ApplyFraction,
        frozenset({CHART_2021_PART_1_AMOUNTS_F_AND_G}),
        frozenset({CHART_2021_PART_1_AMOUNT_H}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2021_AMOUNT_I}),
        frozenset({CHART_2021_PART_1_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset({CHART_2021_PART_1_AMOUNT_H, CHART_2021_PART_1_AMOUNT_I}),
        frozenset({CHART_2021_PART_1_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset({CHART_2021_PART_1_AMOUNT_E, CHART_2021_PART_1_AMOUNT_J}),
        frozenset({CHART_2021_PART_1_AMOUNT_K}),
    ),
    (
        Sum,
        frozenset({CHART_2021_PART_1_AMOUNT_K, CHART_2020_TOTAL_CARRIED}),
        frozenset({CHART_2021_PART_1_AMOUNT_M}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2021_PART_1_AMOUNT_M}
        ),
        frozenset({CHART_2021_PART_1_AMOUNT_N}),
    ),
    # Chart 2021 Part 2.
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2021_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2021_PART_2_AMOUNT_A, CHART_2021_PART_1_AMOUNT_M}),
        frozenset({CHART_2021_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2021_PART_2_AMOUNT_C, CHART_2021_AMOUNT_D}),
        frozenset({CHART_2021_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2021_AMOUNT_F}),
        frozenset({CHART_2021_PART_2_AMOUNT_F}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2021_PART_2_AMOUNT_G}),
        frozenset({CHART_2021_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset({CHART_2021_PART_2_AMOUNT_F, CHART_2021_PART_2_AMOUNT_G}),
        frozenset({CHART_2021_PART_2_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset({CHART_2021_PART_2_AMOUNT_E, CHART_2021_PART_2_AMOUNT_H}),
        frozenset({CHART_2021_PART_2_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset({CHART_2021_PART_2_AMOUNT_I, CHART_2021_PART_1_AMOUNT_M}),
        frozenset({CHART_2021_PART_2_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset({CHART_2021_PART_2_AMOUNT_H, CHART_2021_PART_2_AMOUNT_K}),
        frozenset({CHART_2021_PART_2_AMOUNT_L}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2021_PART_2_AMOUNT_L}
        ),
        frozenset({CHART_2021_PART_2_AMOUNT_M}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                T657_CHART_2021_CLAIMS_ADDITIONAL_DEDUCTION,
                CHART_2021_PART_1_AMOUNT_E,
                ANNUAL_GAINS_LIMIT_2025,
                CUMULATIVE_GAINS_LIMIT_2025,
                CHART_2021_PART_1_AMOUNT_M,
            }
        ),
        frozenset({CHART_2021_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CHART_2021_PART_2_APPLIES, CHART_2021_PART_1_AMOUNT_M, CHART_2021_PART_2_AMOUNT_L}
        ),
        frozenset({CHART_2021_TOTAL_CARRIED}),
    ),
    # Chart 2022 Part 1 (B is Chart 2021's total carried).
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2022_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2022_PART_1_AMOUNT_A, CHART_2021_TOTAL_CARRIED}),
        frozenset({CHART_2022_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                T657_CHART_2022_USES_D_INSTEAD_CHECKED,
                CHART_2_LINE_19,
                T657_CHART_2022_AMOUNT_D_INSTEAD,
            }
        ),
        frozenset({CHART_2022_AMOUNT_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2022_PART_1_AMOUNT_C, CHART_2022_AMOUNT_D}),
        frozenset({CHART_2022_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset({T657_CHART_2022_AMOUNT_F, T657_CHART_2022_AMOUNT_G}),
        frozenset({CHART_2022_PART_1_AMOUNTS_F_AND_G}),
    ),
    (
        ApplyFraction,
        frozenset({CHART_2022_PART_1_AMOUNTS_F_AND_G}),
        frozenset({CHART_2022_PART_1_AMOUNT_H}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2022_AMOUNT_I}),
        frozenset({CHART_2022_PART_1_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset({CHART_2022_PART_1_AMOUNT_H, CHART_2022_PART_1_AMOUNT_I}),
        frozenset({CHART_2022_PART_1_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset({CHART_2022_PART_1_AMOUNT_E, CHART_2022_PART_1_AMOUNT_J}),
        frozenset({CHART_2022_PART_1_AMOUNT_K}),
    ),
    (
        Sum,
        frozenset({CHART_2022_PART_1_AMOUNT_K, CHART_2021_TOTAL_CARRIED}),
        frozenset({CHART_2022_PART_1_AMOUNT_M}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2022_PART_1_AMOUNT_M}
        ),
        frozenset({CHART_2022_PART_1_AMOUNT_N}),
    ),
    # Chart 2022 Part 2.
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2022_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2022_PART_2_AMOUNT_A, CHART_2022_PART_1_AMOUNT_M}),
        frozenset({CHART_2022_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2022_PART_2_AMOUNT_C, CHART_2022_AMOUNT_D}),
        frozenset({CHART_2022_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2022_AMOUNT_F}),
        frozenset({CHART_2022_PART_2_AMOUNT_F}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2022_PART_2_AMOUNT_G}),
        frozenset({CHART_2022_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset({CHART_2022_PART_2_AMOUNT_F, CHART_2022_PART_2_AMOUNT_G}),
        frozenset({CHART_2022_PART_2_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset({CHART_2022_PART_2_AMOUNT_E, CHART_2022_PART_2_AMOUNT_H}),
        frozenset({CHART_2022_PART_2_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset({CHART_2022_PART_2_AMOUNT_I, CHART_2022_PART_1_AMOUNT_M}),
        frozenset({CHART_2022_PART_2_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset({CHART_2022_PART_2_AMOUNT_H, CHART_2022_PART_2_AMOUNT_K}),
        frozenset({CHART_2022_PART_2_AMOUNT_L}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2022_PART_2_AMOUNT_L}
        ),
        frozenset({CHART_2022_PART_2_AMOUNT_M}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                T657_CHART_2022_CLAIMS_ADDITIONAL_DEDUCTION,
                CHART_2022_PART_1_AMOUNT_E,
                ANNUAL_GAINS_LIMIT_2025,
                CUMULATIVE_GAINS_LIMIT_2025,
                CHART_2022_PART_1_AMOUNT_M,
            }
        ),
        frozenset({CHART_2022_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CHART_2022_PART_2_APPLIES, CHART_2022_PART_1_AMOUNT_M, CHART_2022_PART_2_AMOUNT_L}
        ),
        frozenset({CHART_2022_TOTAL_CARRIED}),
    ),
    # Chart 2023 Part 1 (B is Chart 2022's total carried).
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2023_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2023_PART_1_AMOUNT_A, CHART_2022_TOTAL_CARRIED}),
        frozenset({CHART_2023_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                T657_CHART_2023_USES_D_INSTEAD_CHECKED,
                CHART_2_LINE_19,
                T657_CHART_2023_AMOUNT_D_INSTEAD,
            }
        ),
        frozenset({CHART_2023_AMOUNT_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2023_PART_1_AMOUNT_C, CHART_2023_AMOUNT_D}),
        frozenset({CHART_2023_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset({T657_CHART_2023_AMOUNT_F, T657_CHART_2023_AMOUNT_G}),
        frozenset({CHART_2023_PART_1_AMOUNTS_F_AND_G}),
    ),
    (
        ApplyFraction,
        frozenset({CHART_2023_PART_1_AMOUNTS_F_AND_G}),
        frozenset({CHART_2023_PART_1_AMOUNT_H}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2023_AMOUNT_I}),
        frozenset({CHART_2023_PART_1_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset({CHART_2023_PART_1_AMOUNT_H, CHART_2023_PART_1_AMOUNT_I}),
        frozenset({CHART_2023_PART_1_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset({CHART_2023_PART_1_AMOUNT_E, CHART_2023_PART_1_AMOUNT_J}),
        frozenset({CHART_2023_PART_1_AMOUNT_K}),
    ),
    (
        Sum,
        frozenset({CHART_2023_PART_1_AMOUNT_K, CHART_2022_TOTAL_CARRIED}),
        frozenset({CHART_2023_PART_1_AMOUNT_M}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2023_PART_1_AMOUNT_M}
        ),
        frozenset({CHART_2023_PART_1_AMOUNT_N}),
    ),
    # Chart 2023 Part 2.
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2023_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2023_PART_2_AMOUNT_A, CHART_2023_PART_1_AMOUNT_M}),
        frozenset({CHART_2023_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2023_PART_2_AMOUNT_C, CHART_2023_AMOUNT_D}),
        frozenset({CHART_2023_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2023_AMOUNT_F}),
        frozenset({CHART_2023_PART_2_AMOUNT_F}),
    ),
    (
        ApplyFraction,
        frozenset({T657_CHART_2023_PART_2_AMOUNT_G}),
        frozenset({CHART_2023_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset({CHART_2023_PART_2_AMOUNT_F, CHART_2023_PART_2_AMOUNT_G}),
        frozenset({CHART_2023_PART_2_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset({CHART_2023_PART_2_AMOUNT_E, CHART_2023_PART_2_AMOUNT_H}),
        frozenset({CHART_2023_PART_2_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset({CHART_2023_PART_2_AMOUNT_I, CHART_2023_PART_1_AMOUNT_M}),
        frozenset({CHART_2023_PART_2_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset({CHART_2023_PART_2_AMOUNT_H, CHART_2023_PART_2_AMOUNT_K}),
        frozenset({CHART_2023_PART_2_AMOUNT_L}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2023_PART_2_AMOUNT_L}
        ),
        frozenset({CHART_2023_PART_2_AMOUNT_M}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                T657_CHART_2023_CLAIMS_ADDITIONAL_DEDUCTION,
                CHART_2023_PART_1_AMOUNT_E,
                ANNUAL_GAINS_LIMIT_2025,
                CUMULATIVE_GAINS_LIMIT_2025,
                CHART_2023_PART_1_AMOUNT_M,
            }
        ),
        frozenset({CHART_2023_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CHART_2023_PART_2_APPLIES, CHART_2023_PART_1_AMOUNT_M, CHART_2023_PART_2_AMOUNT_L}
        ),
        frozenset({CHART_2023_TOTAL_CARRIED}),
    ),
}
