"""The CA-ON manifest entries of the Form T1206 section "Dispositions of certain capital property -
shares subject to TOSI" (see `test_manifest_t1206_share_dispositions.py`).

The section is two forms of its own, as Form RC359 and Form T777 are forms of their own:
- `ca/t1206_share_dispositions` runs once: lines A to G, the under-18 dividend amount, the 50%
  amount of the 18-or-older branch. It has no instances.
- `ca/t1206_share_reserve` runs once for each disposition of `ca/t1206_share_reserve_rows` (any
  number, none included). Its maximum is the lesser of the two printed calculations "Calculation of
  reserve" (i) and (ii); the reserve claimed for the row, up to that maximum, is its export.

The dispositions form reads the row reserves through the record total of the reserve form's export.
The return selects no step of the forms; it totals two of the dispositions form's exports
(`core/record_total`, in `03_income.yaml`) and adds them where the T1 reads them.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.amount_by_count import AmountForCount
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_engine.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    AGED_18_OR_OLDER_AT_END_OF_2025,
    T1206_AGED_18_OR_OLDER_CHECKED,
    T1206_CAPITAL_GAIN_ON_DISPOSITIONS,
    T1206_LINE_C,
    T1206_LINE_C_CHECKED,
    T1206_LINE_D,
    T1206_LINE_E,
    T1206_LINE_G,
    T1206_LINES_A_AND_B,
    T1206_PART_1_LINE_3_AMOUNT,
    T1206_PART_1_LINE_3_PERCENT,
    T1206_RESERVE_2024,
    T1206_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
    T1206_RESERVE_APPLICABLE_PERCENTAGE,
    T1206_RESERVE_BY_PAYMENT,
    T1206_RESERVE_BY_PERCENTAGE,
    T1206_RESERVE_CAPITAL_GAIN,
    T1206_RESERVE_CLAIMED,
    T1206_RESERVE_MAXIMUM,
    T1206_RESERVE_PAYABLE_CHECKED,
    T1206_RESERVE_PROCEEDS,
    T1206_RESERVE_YEARS_AFTER_SALE,
    T1206_ROW_RESERVE,
    T1206_T3_BOX_21_CAPITAL_GAINS,
    T1206_UNDER_18_DIVIDEND_AMOUNT,
    T1206_UNDER_18_PERCENT,
)

DISPOSITIONS_FORM = "ca/t1206_share_dispositions"
RESERVE_FORM = "ca/t1206_share_reserve"

# The starting inputs of the section, in `01h_t1206_inputs.yaml`: lines A, B and F, and the list of
# dispositions with a reserve (one record for each, the instances of the reserve form).
INPUTS = frozenset(
    {
        "ca/t1206_capital_gain_on_dispositions",
        "ca/t1206_reserve_2024",
        "ca/t1206_t3_box_21_capital_gains",
        "ca/t1206_share_reserve_rows",
    }
)

# The fields of one record of `ca/t1206_share_reserve_rows`: the reserve form's inputs, read once
# for each row. They are not inputs of the return.
RESERVE_FIELDS = frozenset(
    {
        "ca/t1206_reserve_capital_gain",
        "ca/t1206_reserve_amount_payable_after_year_end",
        "ca/t1206_reserve_proceeds",
        "ca/t1206_reserve_years_after_sale",
        "ca/t1206_reserve_claimed",
    }
)

# The datasets the steps of the two forms read: the reserve percentages, the under-18 and the
# 18-or-older percentages, and the rounding rule of the dollars-and-cents calculations.
DATASETS = frozenset(
    {
        "ca/t1206_reserve_percentage",
        "ca/t1206_under_18_percentage",
        "ca/t1206_aged_18_or_older_percentage",
        "ca/t1206_rounding",
    }
)

# The exports of the dispositions form, in the order the form prints them: line C, line G, the
# under-18 dividend amount and the Part 1 line 3 amount.
DISPOSITIONS_EXPORTS = (
    "ca/t1206_line_c",
    "ca/t1206_line_g",
    "ca/t1206_under_18_dividend_amount",
    "ca/t1206_part_1_line_3_amount",
)

# The exports the return, the Form T929 and the Form T2048 read: the under-18 dividend amount, the
# Part 1 line 3 amount, by their names without the form's prefix.
CONSUMED_EXPORTS = (
    "t1206_under_18_dividend_amount",
    "t1206_part_1_line_3_amount",
)

# The export of the reserve form, one for each row: the row's reserve, the claim up to the maximum.
RESERVE_EXPORTS = ("ca/t1206_row_reserve",)

# The reserve copies' export, read by the dispositions form as the record list `ca/t1206_share_
# reserve.t1206_row_reserve` (one record for each row), the way a form reads a form's copies.
RESERVE_ROW_RESERVES = RecordListKind(
    "ca/t1206_share_reserve.t1206_row_reserve", fields=(T1206_ROW_RESERVE,)
)

# The return declares no output for the section and selects no step of its own for it.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

# The selections of the dispositions form, one for each line that computes (the form has eleven).
DISPOSITIONS_STEPS = {
    # Line C "Amount of 2025 reserve (calculated below)": the total of the reserves of the rows,
    # "Complete this calculation and include the total amount of your 2025 reserve on line C above."
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1206_share_reserve.t1206_row_reserve"},
        produces={"output": "ca/t1206_line_c"},
    ),
    # T1206 "Dispositions of certain capital property - shares subject to TOSI", the check of the
    # age answer: "If you were under 18 years of age at the end of the year" and "If you were 18
    # years of age or older at the end of the year", one answer of 0 or 1.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/aged_18_or_older_at_end_of_2025"},
        produces={"output": "ca/t1206_aged_18_or_older_checked"},
    ),
    # Lines A and B: "Capital gain on dispositions in 2025" (A) and "Amount of 2024 reserve" (B),
    # the total that line C may not exceed.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1206_capital_gain_on_dispositions", "ca/t1206_reserve_2024")},
        produces={"output": "ca/t1206_lines_a_and_b"},
    ),
    # Line C "Amount of 2025 reserve (calculated below)" checked against lines A and B: the form
    # prints no bound, so a line C above the sum is refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/t1206_line_c", "bound": "ca/t1206_lines_a_and_b"},
        produces={"output": "ca/t1206_line_c_checked"},
    ),
    # Line D "Line B minus line C (if negative, show in brackets)": signed, no floor is printed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1206_reserve_2024", "less": "ca/t1206_line_c_checked"},
        produces={"output": "ca/t1206_line_d"},
    ),
    # Line E "Line A plus line D" with "Net capital gain".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1206_capital_gain_on_dispositions", "ca/t1206_line_d")},
        produces={"output": "ca/t1206_line_e"},
    ),
    # Line G "Line E plus line F", where F is "Capital gains from box 21 of your T3 slip(s)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1206_line_e", "ca/t1206_t3_box_21_capital_gains")},
        produces={"output": "ca/t1206_line_g"},
    ),
    # Under 18: "Multiply the amount from line G by 1.15", the percentage of the age answer.
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/t1206_under_18_percentage"},
        consumes={"count": "ca/t1206_aged_18_or_older_checked"},
        produces={"output": "ca/t1206_under_18_percent"},
    ),
    # Under 18: line G at that percentage, the amount deemed to be a dividend.
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/t1206_rounding"},
        consumes={"amount": "ca/t1206_line_g", "percentage": "ca/t1206_under_18_percent"},
        produces={"output": "ca/t1206_under_18_dividend_amount"},
    ),
    # 18 or older: "multiply the capital gain ... by 50%", the percentage of the age answer.
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/t1206_aged_18_or_older_percentage"},
        consumes={"count": "ca/t1206_aged_18_or_older_checked"},
        produces={"output": "ca/t1206_part_1_line_3_percent"},
    ),
    # 18 or older: line G at 50% (or 0%), the Part 1 line 3 amount.
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/t1206_rounding"},
        consumes={"amount": "ca/t1206_line_g", "percentage": "ca/t1206_part_1_line_3_percent"},
        produces={"output": "ca/t1206_part_1_line_3_amount"},
    ),
}

# The selections of the reserve form, one for each row: the calculation of reserve (i) and (ii).
RESERVE_STEPS = {
    # "Amount payable after the end of the year" / "Proceeds of disposition": the form prints no
    # bound, so a payable amount above the proceeds is refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1206_reserve_amount_payable_after_year_end",
            "bound": "ca/t1206_reserve_proceeds",
        },
        produces={"output": "ca/t1206_reserve_payable_checked"},
    ),
    # (i) "Capital gain x Amount payable after the end of the year / Proceeds of disposition", zero
    # when the proceeds are zero.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1206_rounding"},
        consumes={
            "amount": "ca/t1206_reserve_capital_gain",
            "numerator": "ca/t1206_reserve_payable_checked",
            "denominator": "ca/t1206_reserve_proceeds",
        },
        produces={"output": "ca/t1206_reserve_by_payment"},
    ),
    # "Applicable percentage for year of sale or year after sale (1)": 80%, 60%, 40%, 20%, 0%.
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/t1206_reserve_percentage"},
        consumes={"count": "ca/t1206_reserve_years_after_sale"},
        produces={"output": "ca/t1206_reserve_applicable_percentage"},
    ),
    # (ii) "Capital gain x Applicable percentage for year of sale or year after sale".
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/t1206_rounding"},
        consumes={
            "amount": "ca/t1206_reserve_capital_gain",
            "percentage": "ca/t1206_reserve_applicable_percentage",
        },
        produces={"output": "ca/t1206_reserve_by_percentage"},
    ),
    # "Your reserve in each year cannot be more than whichever of the following two calculations is
    # less": the lesser of (i) and (ii), the most the reserve can be.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1206_reserve_by_payment", "ca/t1206_reserve_by_percentage")},
        produces={"output": "ca/t1206_reserve_maximum"},
    ),
    # "Complete this calculation and include the total amount of your 2025 reserve on line C above":
    # the reserve claimed, up to the maximum. A claim above the maximum is refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/t1206_reserve_claimed", "bound": "ca/t1206_reserve_maximum"},
        produces={"output": "ca/t1206_row_reserve"},
    ),
}

DISPOSITIONS_WIRING = {
    (
        YesOrNoCount,
        frozenset({AGED_18_OR_OLDER_AT_END_OF_2025}),
        frozenset({T1206_AGED_18_OR_OLDER_CHECKED}),
    ),
    (RecordTotal, frozenset({RESERVE_ROW_RESERVES}), frozenset({T1206_LINE_C})),
    (
        Sum,
        frozenset({T1206_CAPITAL_GAIN_ON_DISPOSITIONS, T1206_RESERVE_2024}),
        frozenset({T1206_LINES_A_AND_B}),
    ),
    (AtMost, frozenset({T1206_LINE_C, T1206_LINES_A_AND_B}), frozenset({T1206_LINE_C_CHECKED})),
    (Subtract, frozenset({T1206_RESERVE_2024, T1206_LINE_C_CHECKED}), frozenset({T1206_LINE_D})),
    (Sum, frozenset({T1206_CAPITAL_GAIN_ON_DISPOSITIONS, T1206_LINE_D}), frozenset({T1206_LINE_E})),
    (
        Sum,
        frozenset({T1206_LINE_E, T1206_T3_BOX_21_CAPITAL_GAINS}),
        frozenset({T1206_LINE_G}),
    ),
    (
        AmountForCount,
        frozenset({T1206_AGED_18_OR_OLDER_CHECKED}),
        frozenset({T1206_UNDER_18_PERCENT}),
    ),
    (
        ApplyPercentage,
        frozenset({T1206_LINE_G, T1206_UNDER_18_PERCENT}),
        frozenset({T1206_UNDER_18_DIVIDEND_AMOUNT}),
    ),
    (
        AmountForCount,
        frozenset({T1206_AGED_18_OR_OLDER_CHECKED}),
        frozenset({T1206_PART_1_LINE_3_PERCENT}),
    ),
    (
        ApplyPercentage,
        frozenset({T1206_LINE_G, T1206_PART_1_LINE_3_PERCENT}),
        frozenset({T1206_PART_1_LINE_3_AMOUNT}),
    ),
}

RESERVE_WIRING = {
    (
        AtMost,
        frozenset({T1206_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END, T1206_RESERVE_PROCEEDS}),
        frozenset({T1206_RESERVE_PAYABLE_CHECKED}),
    ),
    (
        ApplyRatioOrZero,
        frozenset(
            {T1206_RESERVE_CAPITAL_GAIN, T1206_RESERVE_PAYABLE_CHECKED, T1206_RESERVE_PROCEEDS}
        ),
        frozenset({T1206_RESERVE_BY_PAYMENT}),
    ),
    (
        AmountForCount,
        frozenset({T1206_RESERVE_YEARS_AFTER_SALE}),
        frozenset({T1206_RESERVE_APPLICABLE_PERCENTAGE}),
    ),
    (
        ApplyPercentage,
        frozenset({T1206_RESERVE_CAPITAL_GAIN, T1206_RESERVE_APPLICABLE_PERCENTAGE}),
        frozenset({T1206_RESERVE_BY_PERCENTAGE}),
    ),
    (
        LesserOf,
        frozenset({T1206_RESERVE_BY_PAYMENT, T1206_RESERVE_BY_PERCENTAGE}),
        frozenset({T1206_RESERVE_MAXIMUM}),
    ),
    (
        AtMost,
        frozenset({T1206_RESERVE_CLAIMED, T1206_RESERVE_MAXIMUM}),
        frozenset({T1206_ROW_RESERVE}),
    ),
}
