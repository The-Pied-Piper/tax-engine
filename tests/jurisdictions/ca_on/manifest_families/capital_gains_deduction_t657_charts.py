"""The CA-ON manifest entries of Form T657 Chart 2024, Period 1 and Period 2 (`test_manifest.py`).

The steps are in the manifest part `06c_capital_gains_deduction_t657_charts.yaml`. Each period's
chart is chained into Chart 2025: Chart 2025 Part 1's amount B reads Period 2's amount N, which is
in the `capital_gains_deduction_t657` family; Period 2's amount B reads Period 1's amount N. Period
1's amount B reads Chart 2023's total carried (`capital_gains_deduction_t657_charts_2021_to_2023`).
"""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LIMIT_2025,
    CHART_2_LINE_19,
    CHART_2023_TOTAL_CARRIED,
    CHART_2024_PERIOD_1_AMOUNT_A,
    CHART_2024_PERIOD_1_AMOUNT_C,
    CHART_2024_PERIOD_1_AMOUNT_E,
    CHART_2024_PERIOD_1_AMOUNT_I,
    CHART_2024_PERIOD_1_AMOUNT_K,
    CHART_2024_PERIOD_1_AMOUNT_L,
    CHART_2024_PERIOD_1_AMOUNT_N,
    CHART_2024_PERIOD_1_AMOUNT_O,
    CHART_2024_PERIOD_1_AMOUNTS_F_TO_H,
    CHART_2024_PERIOD_2_AMOUNT_A,
    CHART_2024_PERIOD_2_AMOUNT_C,
    CHART_2024_PERIOD_2_AMOUNT_E,
    CHART_2024_PERIOD_2_AMOUNT_I,
    CHART_2024_PERIOD_2_AMOUNT_K,
    CHART_2024_PERIOD_2_AMOUNT_L,
    CHART_2024_PERIOD_2_AMOUNT_N,
    CHART_2024_PERIOD_2_AMOUNT_O,
    CHART_2024_PERIOD_2_AMOUNTS_F_TO_H,
    CUMULATIVE_GAINS_LIMIT_2025,
    T657_CHART_2024_PERIOD_1_AMOUNT_F,
    T657_CHART_2024_PERIOD_1_AMOUNT_G,
    T657_CHART_2024_PERIOD_1_AMOUNT_H,
    T657_CHART_2024_PERIOD_1_AMOUNT_J,
    T657_CHART_2024_PERIOD_2_AMOUNT_F,
    T657_CHART_2024_PERIOD_2_AMOUNT_G,
    T657_CHART_2024_PERIOD_2_AMOUNT_H,
    T657_CHART_2024_PERIOD_2_AMOUNT_J,
)

INPUTS = frozenset(
    {
        "ca/t657_chart_2024_period_1_amount_h",
        "ca/t657_chart_2024_period_1_amount_j",
        "ca/t657_chart_2024_period_2_amount_h",
        "ca/t657_chart_2024_period_2_amount_j",
    }
)

# Chart 2024 amount O of each period: the maximum for line 25400 if no later reserve or disposition
# is reported, which nothing reads (Chart 2025 reads Period 2's amount N, not O).
OUTPUTS = frozenset(
    {
        "ca/chart_2024_period_1_amount_o",
        "ca/chart_2024_period_2_amount_o",
    }
)

STEPS = {
    # Chart 2024 Period 1 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS disposed
    # of in 2024 for Period 1" 508,418.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2024_period_1_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2024_period_1_amount_a"},
    ),
    # Chart 2024 Period 1 "Amount A minus amount B" C (B "Enter the last amount that you calculated
    # for "Total amount of capital gains included in 2025 income eligible for capital gains
    # deduction" from 2016 to 2023. If you did not complete charts for 2016 to 2023, enter "0".").
    # The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2024_period_1_amount_a",
            "less": "ca/chart_2023_total_carried",
        },
        produces={"output": "ca/chart_2024_period_1_amount_c"},
    ),
    # Chart 2024 Period 1 "Capital gains deduction available for dispositions of QFFP and/or QSBCS:
    # amount C minus amount D (if negative, enter "0")" E (D "Capital gains deductions from previous
    # years from line 19 of Chart 2").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2024_period_1_amount_c",
            "less": "ca/chart_2_line_19",
        },
        produces={"output": "ca/chart_2024_period_1_amount_e"},
    ),
    # Chart 2024 Period 1 "Add amounts F to H (if negative, enter "0")": F "Amount from line 6 of
    # Form T2017 (do not include reserves from dispositions of QFFP in any year or period other than
    # Period 1 of 2024)", G "Amount from line 12 of Form T2017 (do not include reserves from
    # dispositions of QSBCS in any year or period other than Period 1 of 2024)", H "Amount included
    # in box 30 of a 2025 T3 slip and the footnote area indicates it is a reserve from property
    # disposed of in Period 1 of 2024."
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2024_period_1_amount_f",
                "ca/t657_chart_2024_period_1_amount_g",
                "ca/t657_chart_2024_period_1_amount_h",
            ),
        },
        produces={"output": "ca/chart_2024_period_1_amounts_f_to_h"},
    ),
    # Chart 2024 Period 1 "× 1/2 = I" (the amounts F to H, times the 1/2 printed on the form).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2024_period_1_i_fraction"},
        consumes={
            "base": "ca/chart_2024_period_1_amounts_f_to_h",
        },
        produces={"output": "ca/chart_2024_period_1_amount_i"},
    ),
    # Chart 2024 Period 1 "Amount I minus amount J" K (J "Portion of the amount from line 17216 of
    # Form T2048 in respect of a reserve for a property disposed of in Period 1 of 2024"). The form
    # prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2024_period_1_amount_i",
            "less": "ca/t657_chart_2024_period_1_amount_j",
        },
        produces={"output": "ca/chart_2024_period_1_amount_k"},
    ),
    # Chart 2024 Period 1 "Enter whichever is less: amount E or amount K." L.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2024_period_1_amount_e",
                "ca/chart_2024_period_1_amount_k",
            ),
        },
        produces={"output": "ca/chart_2024_period_1_amount_l"},
    ),
    # Chart 2024 Period 1 "Amount L plus amount M" N (M "Enter amount B from above.", Chart 2023's
    # total carried).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2024_period_1_amount_l",
                "ca/chart_2023_total_carried",
            ),
        },
        produces={"output": "ca/chart_2024_period_1_amount_n"},
    ),
    # Chart 2024 Period 1 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2 or amount N
    # above." O, the maximum for line 25400 when no later reserve or disposition is reported.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2024_period_1_amount_n",
            ),
        },
        produces={"output": "ca/chart_2024_period_1_amount_o"},
    ),
    # Chart 2024 Period 2 amount A: "Maximum capital gains deduction for QFFP and/or QSBCS disposed
    # of in 2024 for Period 2" 625,000.00, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/chart_2024_period_2_amount_a"},
        consumes={},
        produces={"output": "ca/chart_2024_period_2_amount_a"},
    ),
    # Chart 2024 Period 2 "Amount A minus amount B" C (B "Enter the last amount that you calculated
    # for "Total amount of capital gains included in 2025 income eligible for capital gains
    # deduction" from 2016 to 2024." is Period 1's amount N, the total carried into Period 2).
    # The form prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2024_period_2_amount_a",
            "less": "ca/chart_2024_period_1_amount_n",
        },
        produces={"output": "ca/chart_2024_period_2_amount_c"},
    ),
    # Chart 2024 Period 2 "Amount C minus amount D (if negative, enter "0")" E (D "Capital gains
    # deductions from previous years from line 19 of Chart 2").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/chart_2024_period_2_amount_c",
            "less": "ca/chart_2_line_19",
        },
        produces={"output": "ca/chart_2024_period_2_amount_e"},
    ),
    # Chart 2024 Period 2 "Add amounts F to H (if negative, enter "0")": F, G and H as Period 1's,
    # for a disposition in Period 2 of 2024 ("Amount from line 6 of Form T2017 (do not include
    # reserves from dispositions of QFFP in any year or period other than Period 2 of 2024)").
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t657_chart_2024_period_2_amount_f",
                "ca/t657_chart_2024_period_2_amount_g",
                "ca/t657_chart_2024_period_2_amount_h",
            ),
        },
        produces={"output": "ca/chart_2024_period_2_amounts_f_to_h"},
    ),
    # Chart 2024 Period 2 "× 1/2 = I".
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t657_chart_2024_period_2_i_fraction"},
        consumes={
            "base": "ca/chart_2024_period_2_amounts_f_to_h",
        },
        produces={"output": "ca/chart_2024_period_2_amount_i"},
    ),
    # Chart 2024 Period 2 "Amount I minus amount J" K (J "Portion of the amount from line 17216 of
    # Form T2048 in respect of a reserve for a property disposed of in Period 2 of 2024"). The form
    # prints no floor, so the result stays signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/chart_2024_period_2_amount_i",
            "less": "ca/t657_chart_2024_period_2_amount_j",
        },
        produces={"output": "ca/chart_2024_period_2_amount_k"},
    ),
    # Chart 2024 Period 2 "Enter whichever is less: amount E or amount K." L.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/chart_2024_period_2_amount_e",
                "ca/chart_2024_period_2_amount_k",
            ),
        },
        produces={"output": "ca/chart_2024_period_2_amount_l"},
    ),
    # Chart 2024 Period 2 "Amount L plus amount M" N (M "Enter amount B from above.", Period 1's N).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/chart_2024_period_2_amount_l",
                "ca/chart_2024_period_1_amount_n",
            ),
        },
        produces={"output": "ca/chart_2024_period_2_amount_n"},
    ),
    # Chart 2024 Period 2 "Enter whichever is less: line 21 of Step 1, line 19 of Step 2, or amount
    # N
    # above." O, the maximum for line 25400 when no other disposition is reported.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/annual_gains_limit_2025",
                "ca/cumulative_gains_limit_2025",
                "ca/chart_2024_period_2_amount_n",
            ),
        },
        produces={"output": "ca/chart_2024_period_2_amount_o"},
    ),
}

WIRING = {
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2024_PERIOD_1_AMOUNT_A, CHART_2023_TOTAL_CARRIED}),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2024_PERIOD_1_AMOUNT_C, CHART_2_LINE_19}),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_CHART_2024_PERIOD_1_AMOUNT_F,
                T657_CHART_2024_PERIOD_1_AMOUNT_G,
                T657_CHART_2024_PERIOD_1_AMOUNT_H,
            }
        ),
        frozenset({CHART_2024_PERIOD_1_AMOUNTS_F_TO_H}),
    ),
    (
        ApplyFraction,
        frozenset({CHART_2024_PERIOD_1_AMOUNTS_F_TO_H}),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_I}),
    ),
    (
        Subtract,
        frozenset({CHART_2024_PERIOD_1_AMOUNT_I, T657_CHART_2024_PERIOD_1_AMOUNT_J}),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset({CHART_2024_PERIOD_1_AMOUNT_E, CHART_2024_PERIOD_1_AMOUNT_K}),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_L}),
    ),
    (
        Sum,
        frozenset({CHART_2024_PERIOD_1_AMOUNT_L, CHART_2023_TOTAL_CARRIED}),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_N}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2024_PERIOD_1_AMOUNT_N}
        ),
        frozenset({CHART_2024_PERIOD_1_AMOUNT_O}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_A}),
    ),
    (
        Subtract,
        frozenset({CHART_2024_PERIOD_2_AMOUNT_A, CHART_2024_PERIOD_1_AMOUNT_N}),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_C}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CHART_2024_PERIOD_2_AMOUNT_C, CHART_2_LINE_19}),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_E}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                T657_CHART_2024_PERIOD_2_AMOUNT_F,
                T657_CHART_2024_PERIOD_2_AMOUNT_G,
                T657_CHART_2024_PERIOD_2_AMOUNT_H,
            }
        ),
        frozenset({CHART_2024_PERIOD_2_AMOUNTS_F_TO_H}),
    ),
    (
        ApplyFraction,
        frozenset({CHART_2024_PERIOD_2_AMOUNTS_F_TO_H}),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_I}),
    ),
    (
        Subtract,
        frozenset({CHART_2024_PERIOD_2_AMOUNT_I, T657_CHART_2024_PERIOD_2_AMOUNT_J}),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_K}),
    ),
    (
        LesserOf,
        frozenset({CHART_2024_PERIOD_2_AMOUNT_E, CHART_2024_PERIOD_2_AMOUNT_K}),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_L}),
    ),
    (
        Sum,
        frozenset({CHART_2024_PERIOD_2_AMOUNT_L, CHART_2024_PERIOD_1_AMOUNT_N}),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_N}),
    ),
    (
        LesserOf,
        frozenset(
            {ANNUAL_GAINS_LIMIT_2025, CUMULATIVE_GAINS_LIMIT_2025, CHART_2024_PERIOD_2_AMOUNT_N}
        ),
        frozenset({CHART_2024_PERIOD_2_AMOUNT_O}),
    ),
}
