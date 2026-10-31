"""The CA-ON manifest entries of Form T657 Charts 2016 to 2020, Part 1 and Part 2 each
(`test_manifest.py`).
The steps are in the manifest parts `06e_capital_gains_deduction_t657_charts_2016_to_2018.yaml` and
`06f_capital_gains_deduction_t657_charts_2019_to_2020.yaml`.
The steps are in the manifest part `06e_capital_gains_deduction_t657_charts_2016_to_2020.yaml`.
The charts are computed in the form's year order: Chart 2016 reads the amount B choice (the
line 19 of Chart 2 or the (2016-1) calculation) and nothing carried in; each of Charts 2017 to 2020
reads the last total carried from the chart before it (Chart 2017 reads Chart 2016's total). Each
chart's total carried is Part 2's amount J when Part 2 is completed, else Part 1's amount G (Chart
2016) or K (Charts 2017 to 2020). Chart 2021 reads Chart 2020's total, in the family
`capital_gains_deduction_t657_charts_2021_to_2023`.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LIMIT_2025,
    CHART_2_LINE_19,
    CHART_2016_AMOUNT_B,
    CHART_2016_PART_1_AMOUNT_A,
    CHART_2016_PART_1_AMOUNT_C,
    CHART_2016_PART_1_AMOUNT_F,
    CHART_2016_PART_1_AMOUNT_G,
    CHART_2016_PART_1_AMOUNT_H,
    CHART_2016_PART_1_AMOUNTS_D_AND_E,
    CHART_2016_PART_2_AMOUNT_A,
    CHART_2016_PART_2_AMOUNT_C,
    CHART_2016_PART_2_AMOUNT_E,
    CHART_2016_PART_2_AMOUNT_F,
    CHART_2016_PART_2_AMOUNT_G,
    CHART_2016_PART_2_AMOUNT_I,
    CHART_2016_PART_2_AMOUNT_J,
    CHART_2016_PART_2_AMOUNT_K,
    CHART_2016_PART_2_APPLIES,
    CHART_2016_TOTAL_CARRIED,
    CHART_2017_AMOUNT_D,
    CHART_2017_PART_1_AMOUNT_A,
    CHART_2017_PART_1_AMOUNT_C,
    CHART_2017_PART_1_AMOUNT_E,
    CHART_2017_PART_1_AMOUNT_H,
    CHART_2017_PART_1_AMOUNT_I,
    CHART_2017_PART_1_AMOUNT_K,
    CHART_2017_PART_1_AMOUNT_L,
    CHART_2017_PART_1_AMOUNTS_F_AND_G,
    CHART_2017_PART_2_AMOUNT_A,
    CHART_2017_PART_2_AMOUNT_C,
    CHART_2017_PART_2_AMOUNT_E,
    CHART_2017_PART_2_AMOUNT_F,
    CHART_2017_PART_2_AMOUNT_G,
    CHART_2017_PART_2_AMOUNT_I,
    CHART_2017_PART_2_AMOUNT_J,
    CHART_2017_PART_2_AMOUNT_K,
    CHART_2017_PART_2_APPLIES,
    CHART_2017_TOTAL_CARRIED,
    CHART_2018_AMOUNT_D,
    CHART_2018_PART_1_AMOUNT_A,
    CHART_2018_PART_1_AMOUNT_C,
    CHART_2018_PART_1_AMOUNT_E,
    CHART_2018_PART_1_AMOUNT_H,
    CHART_2018_PART_1_AMOUNT_I,
    CHART_2018_PART_1_AMOUNT_K,
    CHART_2018_PART_1_AMOUNT_L,
    CHART_2018_PART_1_AMOUNTS_F_AND_G,
    CHART_2018_PART_2_AMOUNT_A,
    CHART_2018_PART_2_AMOUNT_C,
    CHART_2018_PART_2_AMOUNT_E,
    CHART_2018_PART_2_AMOUNT_F,
    CHART_2018_PART_2_AMOUNT_G,
    CHART_2018_PART_2_AMOUNT_I,
    CHART_2018_PART_2_AMOUNT_J,
    CHART_2018_PART_2_AMOUNT_K,
    CHART_2018_PART_2_APPLIES,
    CHART_2018_TOTAL_CARRIED,
    CHART_2019_AMOUNT_D,
    CHART_2019_PART_1_AMOUNT_A,
    CHART_2019_PART_1_AMOUNT_C,
    CHART_2019_PART_1_AMOUNT_E,
    CHART_2019_PART_1_AMOUNT_H,
    CHART_2019_PART_1_AMOUNT_I,
    CHART_2019_PART_1_AMOUNT_K,
    CHART_2019_PART_1_AMOUNT_L,
    CHART_2019_PART_1_AMOUNTS_F_AND_G,
    CHART_2019_PART_2_AMOUNT_A,
    CHART_2019_PART_2_AMOUNT_C,
    CHART_2019_PART_2_AMOUNT_E,
    CHART_2019_PART_2_AMOUNT_F,
    CHART_2019_PART_2_AMOUNT_G,
    CHART_2019_PART_2_AMOUNT_I,
    CHART_2019_PART_2_AMOUNT_J,
    CHART_2019_PART_2_AMOUNT_K,
    CHART_2019_PART_2_APPLIES,
    CHART_2019_TOTAL_CARRIED,
    CHART_2020_AMOUNT_D,
    CHART_2020_PART_1_AMOUNT_A,
    CHART_2020_PART_1_AMOUNT_C,
    CHART_2020_PART_1_AMOUNT_E,
    CHART_2020_PART_1_AMOUNT_H,
    CHART_2020_PART_1_AMOUNT_I,
    CHART_2020_PART_1_AMOUNT_K,
    CHART_2020_PART_1_AMOUNT_L,
    CHART_2020_PART_1_AMOUNTS_F_AND_G,
    CHART_2020_PART_2_AMOUNT_A,
    CHART_2020_PART_2_AMOUNT_C,
    CHART_2020_PART_2_AMOUNT_E,
    CHART_2020_PART_2_AMOUNT_F,
    CHART_2020_PART_2_AMOUNT_G,
    CHART_2020_PART_2_AMOUNT_I,
    CHART_2020_PART_2_AMOUNT_J,
    CHART_2020_PART_2_AMOUNT_K,
    CHART_2020_PART_2_APPLIES,
    CHART_2020_TOTAL_CARRIED,
    CUMULATIVE_GAINS_LIMIT_2025,
    T657_CHART_2016_AMOUNT_B_INSTEAD,
    T657_CHART_2016_AMOUNT_D,
    T657_CHART_2016_AMOUNT_E,
    T657_CHART_2016_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2016_USES_D_INSTEAD_CHECKED,
    T657_CHART_2017_AMOUNT_D_INSTEAD,
    T657_CHART_2017_AMOUNT_F,
    T657_CHART_2017_AMOUNT_G,
    T657_CHART_2017_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2017_USES_D_INSTEAD_CHECKED,
    T657_CHART_2018_AMOUNT_D_INSTEAD,
    T657_CHART_2018_AMOUNT_F,
    T657_CHART_2018_AMOUNT_G,
    T657_CHART_2018_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2018_USES_D_INSTEAD_CHECKED,
    T657_CHART_2019_AMOUNT_D_INSTEAD,
    T657_CHART_2019_AMOUNT_F,
    T657_CHART_2019_AMOUNT_G,
    T657_CHART_2019_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2019_USES_D_INSTEAD_CHECKED,
    T657_CHART_2020_AMOUNT_D_INSTEAD,
    T657_CHART_2020_AMOUNT_F,
    T657_CHART_2020_AMOUNT_G,
    T657_CHART_2020_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2020_USES_D_INSTEAD_CHECKED,
)

INPUTS = frozenset(
    {
        "ca/t657_chart_2016_uses_d_instead",
        "ca/t657_chart_2016_amount_b_instead",
        "ca/t657_chart_2016_claims_additional_deduction",
        "ca/t657_chart_2017_uses_d_instead",
        "ca/t657_chart_2017_amount_d_instead",
        "ca/t657_chart_2017_claims_additional_deduction",
        "ca/t657_chart_2018_uses_d_instead",
        "ca/t657_chart_2018_amount_d_instead",
        "ca/t657_chart_2018_claims_additional_deduction",
        "ca/t657_chart_2019_uses_d_instead",
        "ca/t657_chart_2019_amount_d_instead",
        "ca/t657_chart_2019_claims_additional_deduction",
        "ca/t657_chart_2020_uses_d_instead",
        "ca/t657_chart_2020_amount_d_instead",
        "ca/t657_chart_2020_claims_additional_deduction",
    }
)

# Amount H of Part 1 and amount K of Part 2 of each chart: the maximum for line 25400 if no later
# reserve is reported, which nothing reads (the carried total is the chart's total carried).
OUTPUTS = frozenset(
    {
        "ca/chart_2016_part_1_amount_h",
        "ca/chart_2016_part_2_amount_k",
        "ca/chart_2017_part_1_amount_l",
        "ca/chart_2018_part_1_amount_l",
        "ca/chart_2019_part_1_amount_l",
        "ca/chart_2020_part_1_amount_l",
        "ca/chart_2017_part_2_amount_k",
        "ca/chart_2018_part_2_amount_k",
        "ca/chart_2019_part_2_amount_k",
        "ca/chart_2020_part_2_amount_k",
    }
)

STEPS = {
    # Chart 2016 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS
    # disposed of in 2016" 412,088.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2016_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2016_part_1_amount_a"},
    ),
    # Chart 2016 Part 1 "Amount A minus amount B" C (B: the amount from line 19 of
    # Chart 2, 2016-1). The form prints "(if negative, enter "0")", so the line is floored
    # at 0.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2016_part_1_amount_a",
            "less": "ca/chart_2016_amount_b",
        },
        produces={"output": "ca/chart_2016_part_1_amount_c"},
    ),
    # Chart 2016 Part 1 amount B: "Capital gains deductions from previous years from line 19
    # of Chart 2 (2016-1)", or the (2016-1) calculation, whose result the caller enters
    # (uses_d_instead 1). Part 2 reads the same amount as its amount D.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2016_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2016_amount_b_instead",
        },
        blank={"count": "0"},
        produces={"output": "ca/chart_2016_amount_b"},
    ),
    # Chart 2016 Part 1 "Taxable capital gains from a reserve on QFFP and/or QSBCS disposed of
    # in 2016 included in your 2025 income: amount D plus amount E (if negative, enter "0")":
    # D is line 6 of Form T2017 and E is line 12 of Form T2017 (signed).
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2016_amount_d",
                "ca/t657_chart_2016_amount_e",
            ),
        },
        produces={"output": "ca/chart_2016_part_1_amounts_d_and_e"},
    ),
    # Chart 2016 Part 1 "× 1/2 =" F (amounts D and E, times the 1/2 printed on the form).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2016_part_1_f_fraction"},
        consumes={
            "base": "ca/chart_2016_part_1_amounts_d_and_e",
        },
        produces={"output": "ca/chart_2016_part_1_amount_f"},
    ),
    # Chart 2016 Part 1 "Enter whichever is less: amount C or amount F." G, the total amount of
    # capital gains included in 2025 income eligible for the capital gains deduction.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2016_part_1_amount_c",
                "ca/chart_2016_part_1_amount_f",
            ),
        },
        produces={"output": "ca/chart_2016_part_1_amount_g"},
    ),
    # Chart 2016 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount G
    # above." H, the maximum for line 25400 if no other reserve is reported (nothing reads it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2016_part_1_amount_g",
            ),
        },
        produces={"output": "ca/chart_2016_part_1_amount_h"},
    ),
    # Chart 2016 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2016"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2016_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2016_part_2_amount_a"},
    ),
    # Chart 2016 Part 2 "Amount A minus amount B" C (B: Part 1 amount G, "Total amount of capital
    # gains included in your 2025 income eligible for capital gains deduction from amount G in
    # Part 1 for 2016"). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2016_part_2_amount_a",
            "less": "ca/chart_2016_part_1_amount_g",
        },
        produces={"output": "ca/chart_2016_part_2_amount_c"},
    ),
    # Chart 2016 Part 2 "Capital gains deduction available for QFFP disposed of in 2016 included
    # in
    # your 2025 income: amount C minus amount D (if negative, enter "0")" E (D: amount B of Part
    # 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2016_part_2_amount_c",
            "less": "ca/chart_2016_amount_b",
        },
        produces={"output": "ca/chart_2016_part_2_amount_e"},
    ),
    # Chart 2016 Part 2 "Amount from line 6 of Form T2017 ... × 1/2 =" F (the line 6 amount,
    # halved).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2016_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2016_amount_d",
        },
        produces={"output": "ca/chart_2016_part_2_amount_f"},
    ),
    # Chart 2016 Part 2 "Enter whichever is less: amount E or amount F." G.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2016_part_2_amount_e",
                "ca/chart_2016_part_2_amount_f",
            ),
        },
        produces={"output": "ca/chart_2016_part_2_amount_g"},
    ),
    # Chart 2016 Part 2 "Amount G plus amount H" I (H "Enter amount B from above.": Part 1 amount
    # G).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2016_part_2_amount_g",
                "ca/chart_2016_part_1_amount_g",
            ),
        },
        produces={"output": "ca/chart_2016_part_2_amount_i"},
    ),
    # Chart 2016 Part 2 "Enter whichever is less: amount F or amount I." J, the total amount of
    # capital gains included in 2025 income eligible for capital gains deduction.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2016_part_2_amount_f",
                "ca/chart_2016_part_2_amount_i",
            ),
        },
        produces={"output": "ca/chart_2016_part_2_amount_j"},
    ),
    # Chart 2016 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount J
    # above." K, the maximum for line 25400 if no other disposition is reported (nothing reads
    # it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2016_part_2_amount_j",
            ),
        },
        produces={"output": "ca/chart_2016_part_2_amount_k"},
    ),
    # Chart 2016 Part 2 is completed only when the filer reports a QFFP reserve and "you want to
    # claim
    # the additional deduction, complete Part 2", and amount C of Part 1 is equal to or less than
    # the
    # three amounts the form names. The count is 1 when none of its conditions applies, else 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2016_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2016_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2016_part_1_amount_c",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2016_part_1_amount_g",
            ),
        },
        produces={"output": "ca/chart_2016_part_2_applies"},
    ),
    # The total carried forward: Part 2 amount J when Part 2 is completed, else Part 1 amount G
    # (the form: "Enter the last amount that you calculated" for the charts that follow).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2016_part_2_applies",
            "when_none": "ca/chart_2016_part_1_amount_g",
            "when_any": "ca/chart_2016_part_2_amount_j",
        },
        blank={"count": "0", "when_none": "pass_on", "when_any": "pass_on"},
        produces={"output": "ca/chart_2016_total_carried"},
    ),
    # Chart 2017 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS
    # disposed of in 2017" 417,858.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2017_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2017_part_1_amount_a"},
    ),
    # Chart 2017 Part 1 "Amount A minus amount B" C (B: the last total carried from the chart
    # before
    # it). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2017_part_1_amount_a",
            "less": "ca/chart_2016_total_carried",
        },
        produces={"output": "ca/chart_2017_part_1_amount_c"},
    ),
    # Chart 2017 amount D: "Capital gains deductions from previous years from line 19 of Chart 2
    # (2017-1)", or, when the filer claimed a deduction for other eligible capital gains from
    # 2017 to 2024, the (2017-1) calculation, whose result the caller enters (uses_d_instead 1).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2017_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2017_amount_d_instead",
        },
        blank={"count": "0"},
        produces={"output": "ca/chart_2017_amount_d"},
    ),
    # Chart 2017 Part 1 "Capital gains deduction available for QFFP and/or QSBCS disposed of in
    # 2017 and included in your 2025 income: amount C minus amount D (if negative, enter "0")" E.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2017_part_1_amount_c",
            "less": "ca/chart_2017_amount_d",
        },
        produces={"output": "ca/chart_2017_part_1_amount_e"},
    ),
    # Chart 2017 Part 1 "Taxable capital gains from a reserve on QFFP and/or QSBCS disposed of in
    # 2017 included in your 2025 income: amount F plus amount G (if negative, enter "0")", F
    # "Amount
    # from line 6 of Form T2017" and G "Amount from line 12 of Form T2017" (signed: a loss is
    # negative).
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2017_amount_f",
                "ca/t657_chart_2017_amount_g",
            ),
        },
        produces={"output": "ca/chart_2017_part_1_amounts_f_and_g"},
    ),
    # Chart 2017 Part 1 "× 1/2 =" H (the amounts F and G, times the 1/2 printed on the form).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2017_part_1_h_fraction"},
        consumes={
            "base": "ca/chart_2017_part_1_amounts_f_and_g",
        },
        produces={"output": "ca/chart_2017_part_1_amount_h"},
    ),
    # Chart 2017 Part 1 "Enter whichever is less: amount E or amount H." I.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2017_part_1_amount_e",
                "ca/chart_2017_part_1_amount_h",
            ),
        },
        produces={"output": "ca/chart_2017_part_1_amount_i"},
    ),
    # Chart 2017 Part 1 "Amount I plus amount J" K (J "Enter amount B from above.": the last total
    # carried in from the chart before it).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2017_part_1_amount_i",
                "ca/chart_2016_total_carried",
            ),
        },
        produces={"output": "ca/chart_2017_part_1_amount_k"},
    ),
    # Chart 2017 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount K
    # above." L, the maximum for line 25400 if no other reserve is reported (nothing reads it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2017_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2017_part_1_amount_l"},
    ),
    # Chart 2017 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2017"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2017_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2017_part_2_amount_a"},
    ),
    # Chart 2017 Part 2 "Amount A minus amount B" C (B "Enter amount K from Part 1 of Chart
    # 2017.").
    # The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2017_part_2_amount_a",
            "less": "ca/chart_2017_part_1_amount_k",
        },
        produces={"output": "ca/chart_2017_part_2_amount_c"},
    ),
    # Chart 2017 Part 2 "Capital gains deduction available for QFFP disposed of in 2017 included
    # in
    # your 2025 income: amount C minus amount D (if negative, enter "0")" E (D as in Part 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2017_part_2_amount_c",
            "less": "ca/chart_2017_amount_d",
        },
        produces={"output": "ca/chart_2017_part_2_amount_e"},
    ),
    # Chart 2017 Part 2 "Amount from line 6 of Form T2017 ... × 1/2 = F" (Part 1's F input,
    # halved).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2017_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2017_amount_f",
        },
        produces={"output": "ca/chart_2017_part_2_amount_f"},
    ),
    # Chart 2017 Part 2 "Enter whichever is less: amount E or amount F." G.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2017_part_2_amount_e",
                "ca/chart_2017_part_2_amount_f",
            ),
        },
        produces={"output": "ca/chart_2017_part_2_amount_g"},
    ),
    # Chart 2017 Part 2 "Amount G plus amount H" I (H "Enter amount B from above.": Part 1 amount
    # K).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2017_part_2_amount_g",
                "ca/chart_2017_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2017_part_2_amount_i"},
    ),
    # Chart 2017 Part 2 "Enter whichever is less: amount F or amount I." J, the total amount of
    # capital gains included in 2025 income eligible for capital gains deduction.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2017_part_2_amount_f",
                "ca/chart_2017_part_2_amount_i",
            ),
        },
        produces={"output": "ca/chart_2017_part_2_amount_j"},
    ),
    # Chart 2017 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount J
    # above." K, the maximum for line 25400 if no other disposition is reported (nothing reads
    # it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2017_part_2_amount_j",
            ),
        },
        produces={"output": "ca/chart_2017_part_2_amount_k"},
    ),
    # Chart 2017 Part 2 is completed only when the filer reports a QFFP reserve and "you want to
    # claim
    # the additional deduction, complete Part 2", and amount E of Part 1 is equal to or less than
    # the
    # three amounts the form names. The count is 1 when none of its conditions applies, else 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2017_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2017_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2017_part_1_amount_e",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2017_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2017_part_2_applies"},
    ),
    # The total carried forward: Part 2 amount J when Part 2 is completed, else Part 1 amount K
    # (the form: "Enter the last amount that you calculated" for the charts that follow).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2017_part_2_applies",
            "when_none": "ca/chart_2017_part_1_amount_k",
            "when_any": "ca/chart_2017_part_2_amount_j",
        },
        blank={"count": "0", "when_none": "pass_on", "when_any": "pass_on"},
        produces={"output": "ca/chart_2017_total_carried"},
    ),
    # Chart 2018 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS
    # disposed of in 2018" 424,126.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2018_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2018_part_1_amount_a"},
    ),
    # Chart 2018 Part 1 "Amount A minus amount B" C (B: the last total carried from the chart
    # before
    # it). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2018_part_1_amount_a",
            "less": "ca/chart_2017_total_carried",
        },
        produces={"output": "ca/chart_2018_part_1_amount_c"},
    ),
    # Chart 2018 amount D: "Capital gains deductions from previous years from line 19 of Chart 2
    # (2018-1)", or, when the filer claimed a deduction for other eligible capital gains from
    # 2018 to 2024, the (2018-1) calculation, whose result the caller enters (uses_d_instead 1).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2018_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2018_amount_d_instead",
        },
        blank={"count": "0"},
        produces={"output": "ca/chart_2018_amount_d"},
    ),
    # Chart 2018 Part 1 "Capital gains deduction available for QFFP and/or QSBCS disposed of in
    # 2018 and included in your 2025 income: amount C minus amount D (if negative, enter "0")" E.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2018_part_1_amount_c",
            "less": "ca/chart_2018_amount_d",
        },
        produces={"output": "ca/chart_2018_part_1_amount_e"},
    ),
    # Chart 2018 Part 1 "Taxable capital gains from a reserve on QFFP and/or QSBCS disposed of in
    # 2018 included in your 2025 income: amount F plus amount G (if negative, enter "0")", F
    # "Amount
    # from line 6 of Form T2017" and G "Amount from line 12 of Form T2017" (signed: a loss is
    # negative).
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2018_amount_f",
                "ca/t657_chart_2018_amount_g",
            ),
        },
        produces={"output": "ca/chart_2018_part_1_amounts_f_and_g"},
    ),
    # Chart 2018 Part 1 "× 1/2 =" H (the amounts F and G, times the 1/2 printed on the form).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2018_part_1_h_fraction"},
        consumes={
            "base": "ca/chart_2018_part_1_amounts_f_and_g",
        },
        produces={"output": "ca/chart_2018_part_1_amount_h"},
    ),
    # Chart 2018 Part 1 "Enter whichever is less: amount E or amount H." I.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2018_part_1_amount_e",
                "ca/chart_2018_part_1_amount_h",
            ),
        },
        produces={"output": "ca/chart_2018_part_1_amount_i"},
    ),
    # Chart 2018 Part 1 "Amount I plus amount J" K (J "Enter amount B from above.": the last total
    # carried in from the chart before it).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2018_part_1_amount_i",
                "ca/chart_2017_total_carried",
            ),
        },
        produces={"output": "ca/chart_2018_part_1_amount_k"},
    ),
    # Chart 2018 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount K
    # above." L, the maximum for line 25400 if no other reserve is reported (nothing reads it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2018_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2018_part_1_amount_l"},
    ),
    # Chart 2018 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2018"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2018_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2018_part_2_amount_a"},
    ),
    # Chart 2018 Part 2 "Amount A minus amount B" C (B "Enter amount K from Part 1 of Chart
    # 2018.").
    # The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2018_part_2_amount_a",
            "less": "ca/chart_2018_part_1_amount_k",
        },
        produces={"output": "ca/chart_2018_part_2_amount_c"},
    ),
    # Chart 2018 Part 2 "Capital gains deduction available for QFFP disposed of in 2018 included
    # in
    # your 2025 income: amount C minus amount D (if negative, enter "0")" E (D as in Part 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2018_part_2_amount_c",
            "less": "ca/chart_2018_amount_d",
        },
        produces={"output": "ca/chart_2018_part_2_amount_e"},
    ),
    # Chart 2018 Part 2 "Amount from line 6 of Form T2017 ... × 1/2 = F" (Part 1's F input,
    # halved).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2018_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2018_amount_f",
        },
        produces={"output": "ca/chart_2018_part_2_amount_f"},
    ),
    # Chart 2018 Part 2 "Enter whichever is less: amount E or amount F." G.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2018_part_2_amount_e",
                "ca/chart_2018_part_2_amount_f",
            ),
        },
        produces={"output": "ca/chart_2018_part_2_amount_g"},
    ),
    # Chart 2018 Part 2 "Amount G plus amount H" I (H "Enter amount B from above.": Part 1 amount
    # K).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2018_part_2_amount_g",
                "ca/chart_2018_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2018_part_2_amount_i"},
    ),
    # Chart 2018 Part 2 "Enter whichever is less: amount F or amount I." J, the total amount of
    # capital gains included in 2025 income eligible for capital gains deduction.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2018_part_2_amount_f",
                "ca/chart_2018_part_2_amount_i",
            ),
        },
        produces={"output": "ca/chart_2018_part_2_amount_j"},
    ),
    # Chart 2018 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount J
    # above." K, the maximum for line 25400 if no other disposition is reported (nothing reads
    # it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2018_part_2_amount_j",
            ),
        },
        produces={"output": "ca/chart_2018_part_2_amount_k"},
    ),
    # Chart 2018 Part 2 is completed only when the filer reports a QFFP reserve and "you want to
    # claim
    # the additional deduction, complete Part 2", and amount E of Part 1 is equal to or less than
    # the
    # three amounts the form names. The count is 1 when none of its conditions applies, else 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2018_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2018_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2018_part_1_amount_e",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2018_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2018_part_2_applies"},
    ),
    # The total carried forward: Part 2 amount J when Part 2 is completed, else Part 1 amount K
    # (the form: "Enter the last amount that you calculated" for the charts that follow).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2018_part_2_applies",
            "when_none": "ca/chart_2018_part_1_amount_k",
            "when_any": "ca/chart_2018_part_2_amount_j",
        },
        blank={"count": "0", "when_none": "pass_on", "when_any": "pass_on"},
        produces={"output": "ca/chart_2018_total_carried"},
    ),
    # Chart 2019 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS
    # disposed of in 2019" 433,456.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2019_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2019_part_1_amount_a"},
    ),
    # Chart 2019 Part 1 "Amount A minus amount B" C (B: the last total carried from the chart
    # before
    # it). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2019_part_1_amount_a",
            "less": "ca/chart_2018_total_carried",
        },
        produces={"output": "ca/chart_2019_part_1_amount_c"},
    ),
    # Chart 2019 amount D: "Capital gains deductions from previous years from line 19 of Chart 2
    # (2019-1)", or, when the filer claimed a deduction for other eligible capital gains from
    # 2019 to 2024, the (2019-1) calculation, whose result the caller enters (uses_d_instead 1).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2019_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2019_amount_d_instead",
        },
        blank={"count": "0"},
        produces={"output": "ca/chart_2019_amount_d"},
    ),
    # Chart 2019 Part 1 "Capital gains deduction available for QFFP and/or QSBCS disposed of in
    # 2019 and included in your 2025 income: amount C minus amount D (if negative, enter "0")" E.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2019_part_1_amount_c",
            "less": "ca/chart_2019_amount_d",
        },
        produces={"output": "ca/chart_2019_part_1_amount_e"},
    ),
    # Chart 2019 Part 1 "Taxable capital gains from a reserve on QFFP and/or QSBCS disposed of in
    # 2019 included in your 2025 income: amount F plus amount G (if negative, enter "0")", F
    # "Amount
    # from line 6 of Form T2017" and G "Amount from line 12 of Form T2017" (signed: a loss is
    # negative).
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2019_amount_f",
                "ca/t657_chart_2019_amount_g",
            ),
        },
        produces={"output": "ca/chart_2019_part_1_amounts_f_and_g"},
    ),
    # Chart 2019 Part 1 "× 1/2 =" H (the amounts F and G, times the 1/2 printed on the form).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2019_part_1_h_fraction"},
        consumes={
            "base": "ca/chart_2019_part_1_amounts_f_and_g",
        },
        produces={"output": "ca/chart_2019_part_1_amount_h"},
    ),
    # Chart 2019 Part 1 "Enter whichever is less: amount E or amount H." I.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2019_part_1_amount_e",
                "ca/chart_2019_part_1_amount_h",
            ),
        },
        produces={"output": "ca/chart_2019_part_1_amount_i"},
    ),
    # Chart 2019 Part 1 "Amount I plus amount J" K (J "Enter amount B from above.": the last total
    # carried in from the chart before it).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2019_part_1_amount_i",
                "ca/chart_2018_total_carried",
            ),
        },
        produces={"output": "ca/chart_2019_part_1_amount_k"},
    ),
    # Chart 2019 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount K
    # above." L, the maximum for line 25400 if no other reserve is reported (nothing reads it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2019_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2019_part_1_amount_l"},
    ),
    # Chart 2019 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2019"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2019_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2019_part_2_amount_a"},
    ),
    # Chart 2019 Part 2 "Amount A minus amount B" C (B "Enter amount K from Part 1 of Chart
    # 2019.").
    # The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2019_part_2_amount_a",
            "less": "ca/chart_2019_part_1_amount_k",
        },
        produces={"output": "ca/chart_2019_part_2_amount_c"},
    ),
    # Chart 2019 Part 2 "Capital gains deduction available for QFFP disposed of in 2019 included
    # in
    # your 2025 income: amount C minus amount D (if negative, enter "0")" E (D as in Part 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2019_part_2_amount_c",
            "less": "ca/chart_2019_amount_d",
        },
        produces={"output": "ca/chart_2019_part_2_amount_e"},
    ),
    # Chart 2019 Part 2 "Amount from line 6 of Form T2017 ... × 1/2 = F" (Part 1's F input,
    # halved).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2019_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2019_amount_f",
        },
        produces={"output": "ca/chart_2019_part_2_amount_f"},
    ),
    # Chart 2019 Part 2 "Enter whichever is less: amount E or amount F." G.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2019_part_2_amount_e",
                "ca/chart_2019_part_2_amount_f",
            ),
        },
        produces={"output": "ca/chart_2019_part_2_amount_g"},
    ),
    # Chart 2019 Part 2 "Amount G plus amount H" I (H "Enter amount B from above.": Part 1 amount
    # K).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2019_part_2_amount_g",
                "ca/chart_2019_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2019_part_2_amount_i"},
    ),
    # Chart 2019 Part 2 "Enter whichever is less: amount F or amount I." J, the total amount of
    # capital gains included in 2025 income eligible for capital gains deduction.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2019_part_2_amount_f",
                "ca/chart_2019_part_2_amount_i",
            ),
        },
        produces={"output": "ca/chart_2019_part_2_amount_j"},
    ),
    # Chart 2019 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount J
    # above." K, the maximum for line 25400 if no other disposition is reported (nothing reads
    # it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2019_part_2_amount_j",
            ),
        },
        produces={"output": "ca/chart_2019_part_2_amount_k"},
    ),
    # Chart 2019 Part 2 is completed only when the filer reports a QFFP reserve and "you want to
    # claim
    # the additional deduction, complete Part 2", and amount E of Part 1 is equal to or less than
    # the
    # three amounts the form names. The count is 1 when none of its conditions applies, else 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2019_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2019_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2019_part_1_amount_e",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2019_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2019_part_2_applies"},
    ),
    # The total carried forward: Part 2 amount J when Part 2 is completed, else Part 1 amount K
    # (the form: "Enter the last amount that you calculated" for the charts that follow).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2019_part_2_applies",
            "when_none": "ca/chart_2019_part_1_amount_k",
            "when_any": "ca/chart_2019_part_2_amount_j",
        },
        blank={"count": "0", "when_none": "pass_on", "when_any": "pass_on"},
        produces={"output": "ca/chart_2019_total_carried"},
    ),
    # Chart 2020 Part 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS
    # disposed of in 2020" 441,692.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2020_part_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2020_part_1_amount_a"},
    ),
    # Chart 2020 Part 1 "Amount A minus amount B" C (B: the last total carried from the chart
    # before
    # it). The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2020_part_1_amount_a",
            "less": "ca/chart_2019_total_carried",
        },
        produces={"output": "ca/chart_2020_part_1_amount_c"},
    ),
    # Chart 2020 amount D: "Capital gains deductions from previous years from line 19 of Chart 2
    # (2020-1)", or, when the filer claimed a deduction for other eligible capital gains from
    # 2020 to 2024, the (2020-1) calculation, whose result the caller enters (uses_d_instead 1).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t657_chart_2020_uses_d_instead_checked",
            "when_none": "ca/chart_2_line_19",
            "when_any": "ca/t657_chart_2020_amount_d_instead",
        },
        blank={"count": "0"},
        produces={"output": "ca/chart_2020_amount_d"},
    ),
    # Chart 2020 Part 1 "Capital gains deduction available for QFFP and/or QSBCS disposed of in
    # 2020 and included in your 2025 income: amount C minus amount D (if negative, enter "0")" E.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2020_part_1_amount_c",
            "less": "ca/chart_2020_amount_d",
        },
        produces={"output": "ca/chart_2020_part_1_amount_e"},
    ),
    # Chart 2020 Part 1 "Taxable capital gains from a reserve on QFFP and/or QSBCS disposed of in
    # 2020 included in your 2025 income: amount F plus amount G (if negative, enter "0")", F
    # "Amount
    # from line 6 of Form T2017" and G "Amount from line 12 of Form T2017" (signed: a loss is
    # negative).
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2020_amount_f",
                "ca/t657_chart_2020_amount_g",
            ),
        },
        produces={"output": "ca/chart_2020_part_1_amounts_f_and_g"},
    ),
    # Chart 2020 Part 1 "× 1/2 =" H (the amounts F and G, times the 1/2 printed on the form).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2020_part_1_h_fraction"},
        consumes={
            "base": "ca/chart_2020_part_1_amounts_f_and_g",
        },
        produces={"output": "ca/chart_2020_part_1_amount_h"},
    ),
    # Chart 2020 Part 1 "Enter whichever is less: amount E or amount H." I.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2020_part_1_amount_e",
                "ca/chart_2020_part_1_amount_h",
            ),
        },
        produces={"output": "ca/chart_2020_part_1_amount_i"},
    ),
    # Chart 2020 Part 1 "Amount I plus amount J" K (J "Enter amount B from above.": the last total
    # carried in from the chart before it).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2020_part_1_amount_i",
                "ca/chart_2019_total_carried",
            ),
        },
        produces={"output": "ca/chart_2020_part_1_amount_k"},
    ),
    # Chart 2020 Part 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount K
    # above." L, the maximum for line 25400 if no other reserve is reported (nothing reads it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2020_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2020_part_1_amount_l"},
    ),
    # Chart 2020 Part 2 amount A: "Maximum capital gains deduction for QFFP disposed of in 2020"
    # 500,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2020_part_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2020_part_2_amount_a"},
    ),
    # Chart 2020 Part 2 "Amount A minus amount B" C (B "Enter amount K from Part 1 of Chart
    # 2020.").
    # The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2020_part_2_amount_a",
            "less": "ca/chart_2020_part_1_amount_k",
        },
        produces={"output": "ca/chart_2020_part_2_amount_c"},
    ),
    # Chart 2020 Part 2 "Capital gains deduction available for QFFP disposed of in 2020 included
    # in
    # your 2025 income: amount C minus amount D (if negative, enter "0")" E (D as in Part 1).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2020_part_2_amount_c",
            "less": "ca/chart_2020_amount_d",
        },
        produces={"output": "ca/chart_2020_part_2_amount_e"},
    ),
    # Chart 2020 Part 2 "Amount from line 6 of Form T2017 ... × 1/2 = F" (Part 1's F input,
    # halved).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2020_part_2_f_fraction"},
        consumes={
            "base": "ca/t657_chart_2020_amount_f",
        },
        produces={"output": "ca/chart_2020_part_2_amount_f"},
    ),
    # Chart 2020 Part 2 "Enter whichever is less: amount E or amount F." G.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2020_part_2_amount_e",
                "ca/chart_2020_part_2_amount_f",
            ),
        },
        produces={"output": "ca/chart_2020_part_2_amount_g"},
    ),
    # Chart 2020 Part 2 "Amount G plus amount H" I (H "Enter amount B from above.": Part 1 amount
    # K).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2020_part_2_amount_g",
                "ca/chart_2020_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2020_part_2_amount_i"},
    ),
    # Chart 2020 Part 2 "Enter whichever is less: amount F or amount I." J, the total amount of
    # capital gains included in 2025 income eligible for capital gains deduction.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2020_part_2_amount_f",
                "ca/chart_2020_part_2_amount_i",
            ),
        },
        produces={"output": "ca/chart_2020_part_2_amount_j"},
    ),
    # Chart 2020 Part 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount J
    # above." K, the maximum for line 25400 if no other disposition is reported (nothing reads
    # it).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2020_part_2_amount_j",
            ),
        },
        produces={"output": "ca/chart_2020_part_2_amount_k"},
    ),
    # Chart 2020 Part 2 is completed only when the filer reports a QFFP reserve and "you want to
    # claim
    # the additional deduction, complete Part 2", and amount E of Part 1 is equal to or less than
    # the
    # three amounts the form names. The count is 1 when none of its conditions applies, else 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t657_chart_2020_part_2_conditions"},
        consumes={
            "counts": ("ca/t657_chart_2020_claims_additional_deduction",),
            "amounts": (
                "ca/chart_2020_part_1_amount_e",
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2020_part_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2020_part_2_applies"},
    ),
    # The total carried forward: Part 2 amount J when Part 2 is completed, else Part 1 amount K
    # (the form: "Enter the last amount that you calculated" for the charts that follow).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/chart_2020_part_2_applies",
            "when_none": "ca/chart_2020_part_1_amount_k",
            "when_any": "ca/chart_2020_part_2_amount_j",
        },
        blank={"count": "0", "when_none": "pass_on", "when_any": "pass_on"},
        produces={"output": "ca/chart_2020_total_carried"},
    ),
}

WIRING = {
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2016_PART_1_AMOUNT_A}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2016_AMOUNT_B,
                CHART_2016_PART_1_AMOUNT_A,
            }
        ),
        frozenset({CHART_2016_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2_LINE_19,
                T657_CHART_2016_AMOUNT_B_INSTEAD,
                T657_CHART_2016_USES_D_INSTEAD_CHECKED,
            }
        ),
        frozenset({CHART_2016_AMOUNT_B}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_CHART_2016_AMOUNT_D,
                T657_CHART_2016_AMOUNT_E,
            }
        ),
        frozenset({CHART_2016_PART_1_AMOUNTS_D_AND_E}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                CHART_2016_PART_1_AMOUNTS_D_AND_E,
            }
        ),
        frozenset({CHART_2016_PART_1_AMOUNT_F}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2016_PART_1_AMOUNT_C,
                CHART_2016_PART_1_AMOUNT_F,
            }
        ),
        frozenset({CHART_2016_PART_1_AMOUNT_G}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2016_PART_1_AMOUNT_G,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2016_PART_1_AMOUNT_H}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2016_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2016_PART_1_AMOUNT_G,
                CHART_2016_PART_2_AMOUNT_A,
            }
        ),
        frozenset({CHART_2016_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2016_AMOUNT_B,
                CHART_2016_PART_2_AMOUNT_C,
            }
        ),
        frozenset({CHART_2016_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                T657_CHART_2016_AMOUNT_D,
            }
        ),
        frozenset({CHART_2016_PART_2_AMOUNT_F}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2016_PART_2_AMOUNT_E,
                CHART_2016_PART_2_AMOUNT_F,
            }
        ),
        frozenset({CHART_2016_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2016_PART_1_AMOUNT_G,
                CHART_2016_PART_2_AMOUNT_G,
            }
        ),
        frozenset({CHART_2016_PART_2_AMOUNT_I}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2016_PART_2_AMOUNT_F,
                CHART_2016_PART_2_AMOUNT_I,
            }
        ),
        frozenset({CHART_2016_PART_2_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2016_PART_2_AMOUNT_J,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2016_PART_2_AMOUNT_K}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2016_PART_1_AMOUNT_C,
                CHART_2016_PART_1_AMOUNT_G,
                CUMULATIVE_GAINS_LIMIT_2025,
                T657_CHART_2016_CLAIMS_ADDITIONAL_DEDUCTION,
            }
        ),
        frozenset({CHART_2016_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2016_PART_1_AMOUNT_G,
                CHART_2016_PART_2_AMOUNT_J,
                CHART_2016_PART_2_APPLIES,
            }
        ),
        frozenset({CHART_2016_TOTAL_CARRIED}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2017_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2016_TOTAL_CARRIED,
                CHART_2017_PART_1_AMOUNT_A,
            }
        ),
        frozenset({CHART_2017_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2_LINE_19,
                T657_CHART_2017_AMOUNT_D_INSTEAD,
                T657_CHART_2017_USES_D_INSTEAD_CHECKED,
            }
        ),
        frozenset({CHART_2017_AMOUNT_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2017_AMOUNT_D,
                CHART_2017_PART_1_AMOUNT_C,
            }
        ),
        frozenset({CHART_2017_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_CHART_2017_AMOUNT_F,
                T657_CHART_2017_AMOUNT_G,
            }
        ),
        frozenset({CHART_2017_PART_1_AMOUNTS_F_AND_G}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                CHART_2017_PART_1_AMOUNTS_F_AND_G,
            }
        ),
        frozenset({CHART_2017_PART_1_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2017_PART_1_AMOUNT_E,
                CHART_2017_PART_1_AMOUNT_H,
            }
        ),
        frozenset({CHART_2017_PART_1_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2016_TOTAL_CARRIED,
                CHART_2017_PART_1_AMOUNT_I,
            }
        ),
        frozenset({CHART_2017_PART_1_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2017_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2017_PART_1_AMOUNT_L}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2017_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2017_PART_1_AMOUNT_K,
                CHART_2017_PART_2_AMOUNT_A,
            }
        ),
        frozenset({CHART_2017_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2017_AMOUNT_D,
                CHART_2017_PART_2_AMOUNT_C,
            }
        ),
        frozenset({CHART_2017_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                T657_CHART_2017_AMOUNT_F,
            }
        ),
        frozenset({CHART_2017_PART_2_AMOUNT_F}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2017_PART_2_AMOUNT_E,
                CHART_2017_PART_2_AMOUNT_F,
            }
        ),
        frozenset({CHART_2017_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2017_PART_1_AMOUNT_K,
                CHART_2017_PART_2_AMOUNT_G,
            }
        ),
        frozenset({CHART_2017_PART_2_AMOUNT_I}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2017_PART_2_AMOUNT_F,
                CHART_2017_PART_2_AMOUNT_I,
            }
        ),
        frozenset({CHART_2017_PART_2_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2017_PART_2_AMOUNT_J,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2017_PART_2_AMOUNT_K}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2017_PART_1_AMOUNT_E,
                CHART_2017_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
                T657_CHART_2017_CLAIMS_ADDITIONAL_DEDUCTION,
            }
        ),
        frozenset({CHART_2017_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2017_PART_1_AMOUNT_K,
                CHART_2017_PART_2_AMOUNT_J,
                CHART_2017_PART_2_APPLIES,
            }
        ),
        frozenset({CHART_2017_TOTAL_CARRIED}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2018_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2017_TOTAL_CARRIED,
                CHART_2018_PART_1_AMOUNT_A,
            }
        ),
        frozenset({CHART_2018_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2_LINE_19,
                T657_CHART_2018_AMOUNT_D_INSTEAD,
                T657_CHART_2018_USES_D_INSTEAD_CHECKED,
            }
        ),
        frozenset({CHART_2018_AMOUNT_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2018_AMOUNT_D,
                CHART_2018_PART_1_AMOUNT_C,
            }
        ),
        frozenset({CHART_2018_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_CHART_2018_AMOUNT_F,
                T657_CHART_2018_AMOUNT_G,
            }
        ),
        frozenset({CHART_2018_PART_1_AMOUNTS_F_AND_G}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                CHART_2018_PART_1_AMOUNTS_F_AND_G,
            }
        ),
        frozenset({CHART_2018_PART_1_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2018_PART_1_AMOUNT_E,
                CHART_2018_PART_1_AMOUNT_H,
            }
        ),
        frozenset({CHART_2018_PART_1_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2017_TOTAL_CARRIED,
                CHART_2018_PART_1_AMOUNT_I,
            }
        ),
        frozenset({CHART_2018_PART_1_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2018_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2018_PART_1_AMOUNT_L}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2018_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2018_PART_1_AMOUNT_K,
                CHART_2018_PART_2_AMOUNT_A,
            }
        ),
        frozenset({CHART_2018_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2018_AMOUNT_D,
                CHART_2018_PART_2_AMOUNT_C,
            }
        ),
        frozenset({CHART_2018_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                T657_CHART_2018_AMOUNT_F,
            }
        ),
        frozenset({CHART_2018_PART_2_AMOUNT_F}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2018_PART_2_AMOUNT_E,
                CHART_2018_PART_2_AMOUNT_F,
            }
        ),
        frozenset({CHART_2018_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2018_PART_1_AMOUNT_K,
                CHART_2018_PART_2_AMOUNT_G,
            }
        ),
        frozenset({CHART_2018_PART_2_AMOUNT_I}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2018_PART_2_AMOUNT_F,
                CHART_2018_PART_2_AMOUNT_I,
            }
        ),
        frozenset({CHART_2018_PART_2_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2018_PART_2_AMOUNT_J,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2018_PART_2_AMOUNT_K}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2018_PART_1_AMOUNT_E,
                CHART_2018_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
                T657_CHART_2018_CLAIMS_ADDITIONAL_DEDUCTION,
            }
        ),
        frozenset({CHART_2018_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2018_PART_1_AMOUNT_K,
                CHART_2018_PART_2_AMOUNT_J,
                CHART_2018_PART_2_APPLIES,
            }
        ),
        frozenset({CHART_2018_TOTAL_CARRIED}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2019_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2018_TOTAL_CARRIED,
                CHART_2019_PART_1_AMOUNT_A,
            }
        ),
        frozenset({CHART_2019_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2_LINE_19,
                T657_CHART_2019_AMOUNT_D_INSTEAD,
                T657_CHART_2019_USES_D_INSTEAD_CHECKED,
            }
        ),
        frozenset({CHART_2019_AMOUNT_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2019_AMOUNT_D,
                CHART_2019_PART_1_AMOUNT_C,
            }
        ),
        frozenset({CHART_2019_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_CHART_2019_AMOUNT_F,
                T657_CHART_2019_AMOUNT_G,
            }
        ),
        frozenset({CHART_2019_PART_1_AMOUNTS_F_AND_G}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                CHART_2019_PART_1_AMOUNTS_F_AND_G,
            }
        ),
        frozenset({CHART_2019_PART_1_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2019_PART_1_AMOUNT_E,
                CHART_2019_PART_1_AMOUNT_H,
            }
        ),
        frozenset({CHART_2019_PART_1_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2018_TOTAL_CARRIED,
                CHART_2019_PART_1_AMOUNT_I,
            }
        ),
        frozenset({CHART_2019_PART_1_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2019_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2019_PART_1_AMOUNT_L}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2019_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2019_PART_1_AMOUNT_K,
                CHART_2019_PART_2_AMOUNT_A,
            }
        ),
        frozenset({CHART_2019_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2019_AMOUNT_D,
                CHART_2019_PART_2_AMOUNT_C,
            }
        ),
        frozenset({CHART_2019_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                T657_CHART_2019_AMOUNT_F,
            }
        ),
        frozenset({CHART_2019_PART_2_AMOUNT_F}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2019_PART_2_AMOUNT_E,
                CHART_2019_PART_2_AMOUNT_F,
            }
        ),
        frozenset({CHART_2019_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2019_PART_1_AMOUNT_K,
                CHART_2019_PART_2_AMOUNT_G,
            }
        ),
        frozenset({CHART_2019_PART_2_AMOUNT_I}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2019_PART_2_AMOUNT_F,
                CHART_2019_PART_2_AMOUNT_I,
            }
        ),
        frozenset({CHART_2019_PART_2_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2019_PART_2_AMOUNT_J,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2019_PART_2_AMOUNT_K}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2019_PART_1_AMOUNT_E,
                CHART_2019_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
                T657_CHART_2019_CLAIMS_ADDITIONAL_DEDUCTION,
            }
        ),
        frozenset({CHART_2019_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2019_PART_1_AMOUNT_K,
                CHART_2019_PART_2_AMOUNT_J,
                CHART_2019_PART_2_APPLIES,
            }
        ),
        frozenset({CHART_2019_TOTAL_CARRIED}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2020_PART_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2019_TOTAL_CARRIED,
                CHART_2020_PART_1_AMOUNT_A,
            }
        ),
        frozenset({CHART_2020_PART_1_AMOUNT_C}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2_LINE_19,
                T657_CHART_2020_AMOUNT_D_INSTEAD,
                T657_CHART_2020_USES_D_INSTEAD_CHECKED,
            }
        ),
        frozenset({CHART_2020_AMOUNT_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2020_AMOUNT_D,
                CHART_2020_PART_1_AMOUNT_C,
            }
        ),
        frozenset({CHART_2020_PART_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_CHART_2020_AMOUNT_F,
                T657_CHART_2020_AMOUNT_G,
            }
        ),
        frozenset({CHART_2020_PART_1_AMOUNTS_F_AND_G}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                CHART_2020_PART_1_AMOUNTS_F_AND_G,
            }
        ),
        frozenset({CHART_2020_PART_1_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2020_PART_1_AMOUNT_E,
                CHART_2020_PART_1_AMOUNT_H,
            }
        ),
        frozenset({CHART_2020_PART_1_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2019_TOTAL_CARRIED,
                CHART_2020_PART_1_AMOUNT_I,
            }
        ),
        frozenset({CHART_2020_PART_1_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2020_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2020_PART_1_AMOUNT_L}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2020_PART_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset(
            {
                CHART_2020_PART_1_AMOUNT_K,
                CHART_2020_PART_2_AMOUNT_A,
            }
        ),
        frozenset({CHART_2020_PART_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                CHART_2020_AMOUNT_D,
                CHART_2020_PART_2_AMOUNT_C,
            }
        ),
        frozenset({CHART_2020_PART_2_AMOUNT_E}),
    ),
    (
        ApplyFraction,
        frozenset(
            {
                T657_CHART_2020_AMOUNT_F,
            }
        ),
        frozenset({CHART_2020_PART_2_AMOUNT_F}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2020_PART_2_AMOUNT_E,
                CHART_2020_PART_2_AMOUNT_F,
            }
        ),
        frozenset({CHART_2020_PART_2_AMOUNT_G}),
    ),
    (
        Sum,
        frozenset(
            {
                CHART_2020_PART_1_AMOUNT_K,
                CHART_2020_PART_2_AMOUNT_G,
            }
        ),
        frozenset({CHART_2020_PART_2_AMOUNT_I}),
    ),
    (
        LesserOf,
        frozenset(
            {
                CHART_2020_PART_2_AMOUNT_F,
                CHART_2020_PART_2_AMOUNT_I,
            }
        ),
        frozenset({CHART_2020_PART_2_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2020_PART_2_AMOUNT_J,
                CUMULATIVE_GAINS_LIMIT_2025,
            }
        ),
        frozenset({CHART_2020_PART_2_AMOUNT_K}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                ANNUAL_GAINS_LIMIT_2025,
                CHART_2020_PART_1_AMOUNT_E,
                CHART_2020_PART_1_AMOUNT_K,
                CUMULATIVE_GAINS_LIMIT_2025,
                T657_CHART_2020_CLAIMS_ADDITIONAL_DEDUCTION,
            }
        ),
        frozenset({CHART_2020_PART_2_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CHART_2020_PART_1_AMOUNT_K,
                CHART_2020_PART_2_AMOUNT_J,
                CHART_2020_PART_2_APPLIES,
            }
        ),
        frozenset({CHART_2020_TOTAL_CARRIED}),
    ),
}
