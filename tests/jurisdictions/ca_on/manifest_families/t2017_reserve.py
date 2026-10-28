"""The CA-ON manifest entries of Form T2017 (2025), "Summary of Reserves on Dispositions of Capital
Property", Part 1 (see `test_manifest_t2017_reserve.py`).

The form is eleven forms of its own:
- ten row forms, `ca/t2017_line_N_reserve`, one for each 2025 reserve line that takes a list of
  dispositions (N is 2, 3, 4, 8, 9, 10, 17, 21, 24 and 27). Each runs once for each record of
  `ca/t2017_line_N_reserve_rows` (any number, none included), and is the same calculation: the
  maximum is the lesser of calculations (i) and (ii), and the reserve claimed for the record, up to
  that maximum, is its export `ca/t2017_row_reserve`. In a year after the disposition the claim is
  also bounded by the reserve claimed for the property in the previous year (the claim limit).
  The period differs by line: lines 3, 4, 9, 10, 17, 21 and 24 use the nine-year table, line 27
  the four-year table, and lines 2 and 8 take the nine-year table for a disposition of the nine-
  year kind and the four-year table otherwise (the nine_year answer of the record, a yes or no
  answer of 0 or 1).
- `ca/t2017` runs once: the summary of Part 1, which reads each row form's total through the record
  total of its export and adds the lines of the form.
The starting inputs (the 2024 figures, and line 14, which no step reads) and the ten lists are in
`01j_t2017_inputs.yaml`. Line 26 is the 2024 figure less line 23, a step of the summary.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.amount_by_count import AmountForCount
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca.catalog import (
    T2017_LINE_1,
    T2017_LINE_2,
    T2017_LINE_2_RESERVE_ROWS,
    T2017_LINE_3,
    T2017_LINE_3_RESERVE_ROWS,
    T2017_LINE_4,
    T2017_LINE_4_RESERVE_ROWS,
    T2017_LINE_5,
    T2017_LINE_6,
    T2017_LINE_7,
    T2017_LINE_8,
    T2017_LINE_8_RESERVE_ROWS,
    T2017_LINE_9,
    T2017_LINE_9_RESERVE_ROWS,
    T2017_LINE_10,
    T2017_LINE_10_RESERVE_ROWS,
    T2017_LINE_11,
    T2017_LINE_12,
    T2017_LINE_13,
    T2017_LINE_16,
    T2017_LINE_17,
    T2017_LINE_17_RESERVE_ROWS,
    T2017_LINE_18,
    T2017_LINE_19,
    T2017_LINE_20,
    T2017_LINE_21,
    T2017_LINE_21_RESERVE_ROWS,
    T2017_LINE_22,
    T2017_LINE_23,
    T2017_LINE_24,
    T2017_LINE_24_RESERVE_ROWS,
    T2017_LINE_25,
    T2017_LINE_26,
    T2017_LINE_27,
    T2017_LINE_27_RESERVE_ROWS,
    T2017_LINE_28,
    T2017_LINE_29,
    T2017_LINE_30,
    T2017_LINE_31,
    T2017_LINES_66990_AND_67058_FOR_2024,
    T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
    T2017_RESERVE_APPLICABLE_PERCENTAGE,
    T2017_RESERVE_BY_PAYMENT,
    T2017_RESERVE_BY_PERCENTAGE,
    T2017_RESERVE_CAPITAL_GAIN,
    T2017_RESERVE_CLAIM_LIMIT,
    T2017_RESERVE_CLAIMED,
    T2017_RESERVE_FOUR_YEAR_PERCENTAGE,
    T2017_RESERVE_LATER_YEAR,
    T2017_RESERVE_LATER_YEAR_MAXIMUM,
    T2017_RESERVE_MAXIMUM,
    T2017_RESERVE_NINE_YEAR,
    T2017_RESERVE_NINE_YEAR_CHECKED,
    T2017_RESERVE_NINE_YEAR_PERCENTAGE,
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024_CHECKED,
    T2017_RESERVE_PAYABLE_CHECKED,
    T2017_RESERVE_PERIOD_1_OF_2024,
    T2017_RESERVE_PERIOD_1_OF_2024_CHECKED,
    T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    T2017_RESERVE_PROCEEDS,
    T2017_RESERVE_REPORTED_ON_SLIP,
    T2017_RESERVE_REPORTED_ON_SLIP_CHECKED,
    T2017_RESERVE_YEARS_AFTER_DISPOSITION,
    T2017_ROW_CHANGE,
    T2017_ROW_PREVIOUS_RESERVE,
    T2017_ROW_RESERVE,
)

SUMMARY_FORM = "ca/t2017"

# The row forms, by line: the lines that use the nine-year table, the four-year table, and the two
# lines that choose between them by the nine_year answer of each record.
NINE_YEAR_LINES = (3, 4, 9, 10, 17, 21, 24)
FOUR_YEAR_LINES = (27,)
CHOOSING_LINES = (2, 8)
ROW_LINES = (*CHOOSING_LINES, *NINE_YEAR_LINES, *FOUR_YEAR_LINES)
# The lines of QFFP (2 to 4) and QSBCS (8 to 10) reserves, which Form T657 reads: their row forms
# also export the change in the reserve and the three answers the chart totals ask.
T657_LINES = (2, 3, 4, 8, 9, 10)

ROW_FORMS = {line: f"ca/t2017_line_{line}_reserve" for line in ROW_LINES}
ROW_LISTS = {
    2: T2017_LINE_2_RESERVE_ROWS,
    3: T2017_LINE_3_RESERVE_ROWS,
    4: T2017_LINE_4_RESERVE_ROWS,
    8: T2017_LINE_8_RESERVE_ROWS,
    9: T2017_LINE_9_RESERVE_ROWS,
    10: T2017_LINE_10_RESERVE_ROWS,
    17: T2017_LINE_17_RESERVE_ROWS,
    21: T2017_LINE_21_RESERVE_ROWS,
    24: T2017_LINE_24_RESERVE_ROWS,
    27: T2017_LINE_27_RESERVE_ROWS,
}

# The starting inputs of Part 1: the 2024 figures of lines 1, 7, 16, 20, 23 and 30, and the 2024
# figure that line 26 is computed from (lines 66990 and 67058 of the 2024 form). Line 26 itself is
# a step of the summary, not an input.
STARTING_INPUTS = frozenset(
    {
        "ca/t2017_line_1",
        "ca/t2017_line_7",
        "ca/t2017_line_16",
        "ca/t2017_line_20",
        "ca/t2017_line_23",
        "ca/t2017_lines_66990_and_67058_for_2024",
        "ca/t2017_line_30",
    }
)
# The input that no step reads: line 14 is entered as printed and the form computes nothing from it.
ENTERED_INPUTS = frozenset({"ca/t2017_line_14"})
INPUTS = (
    STARTING_INPUTS | ENTERED_INPUTS | frozenset(each.identifier for each in ROW_LISTS.values())
)

# The fields of one record: the five the calculation reads, the reserve claimed for the property in
# the previous year, and the nine-year answer, which only the records of lines 2 and 8 hold. They
# are the row forms' inputs, not the return's.
RESERVE_FIELDS = frozenset(
    {
        "ca/t2017_reserve_capital_gain",
        "ca/t2017_reserve_amount_payable_after_year_end",
        "ca/t2017_reserve_proceeds",
        "ca/t2017_reserve_years_after_disposition",
        "ca/t2017_reserve_claimed",
        "ca/t2017_reserve_previous_year_claim",
    }
)
# The three yes or no answers of a record of a T657 line, which Form T657 and Guide T4037 read (the
# row forms of the other lines do not hold them).
T657_RESERVE_FIELDS = frozenset(
    {
        "ca/t2017_reserve_period_1_of_2024",
        "ca/t2017_reserve_reported_on_slip",
        "ca/t2017_reserve_partnership_year_began_before_june_25_2024",
    }
)

# The datasets the steps read: the two period tables, the rounding rule, and the condition of a
# later year (Year B).
DATASETS = frozenset(
    {
        "ca/t2017_four_year_percentage",
        "ca/t2017_nine_year_percentage",
        "ca/t2017_rounding",
        "ca/t2017_later_year_conditions",
    }
)

# The summary form's exports that the return reads. A form's export is read by any form as the
# record list `ca/t2017.<export>`, one record for the form run once: line 13 by the T657 Step 1
# line 2 total (`ca/annual_gains_line_2`), line 31 by the Schedule 3 line 19200 total
# (`ca/schedule_3_line_19200`).
T2017_LINE_13_EXPORT = RecordListKind("ca/t2017.t2017_line_13", fields=(T2017_LINE_13,))
T2017_LINE_31_EXPORT = RecordListKind("ca/t2017.t2017_line_31", fields=(T2017_LINE_31,))

# The exports of the row forms: the claim of each record, up to its maximum, and for the T657 lines
# the change in the reserve (previous year's claim less the claim) and the three answers Form T657
# and Guide T4037 ask of the disposition.
ROW_EXPORTS = ("ca/t2017_row_reserve",)
T657_ROW_EXPORTS = (
    *ROW_EXPORTS,
    "ca/t2017_row_change",
    "ca/t2017_reserve_period_1_of_2024_checked",
    "ca/t2017_reserve_reported_on_slip_checked",
    "ca/t2017_reserve_partnership_year_began_before_june_25_2024_checked",
)


def row_exports(line: int) -> tuple[str, ...]:
    """The exports of the row form of `line`."""
    return T657_ROW_EXPORTS if line in T657_LINES else ROW_EXPORTS


# The exports of the summary form: lines 6, 12, 13 and 31, the lines the return reads of it, and
# line 14, the entered amount carried as it is (the form reads no input that it does not use).
SUMMARY_EXPORTS = (
    "ca/t2017_line_6",
    "ca/t2017_line_12",
    "ca/t2017_line_13",
    "ca/t2017_line_31",
    "ca/t2017_line_14",
)

# The row totals the summary reads, as the record totals of each row form's export, read by the
# form name qualified with the export: `ca/t2017_line_N_reserve.t2017_row_reserve`.
ROW_RESERVES = {
    line: RecordListKind(f"{ROW_FORMS[line]}.t2017_row_reserve", fields=(T2017_ROW_RESERVE,))
    for line in ROW_LINES
}

# The change in the reserve of each T657 line's row form, read by the form name qualified with the
# export: `ca/t2017_line_N_reserve.t2017_row_change`.
ROW_CHANGES = {
    line: RecordListKind(f"{ROW_FORMS[line]}.t2017_row_change", fields=(T2017_ROW_CHANGE,))
    for line in T657_LINES
}

# The family has no steps of its own: the return selects none of the forms' steps.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()


def row_steps(line: int) -> set[CapabilitySelection]:
    """The selections of the row form of `line`: the calculation of reserve, run once for each
    record. The period is the nine-year table, the four-year table, or (lines 2 and 8) the table
    chosen by the record's nine_year answer."""
    steps = {
        # "Amount payable after the end of the year" over "Proceeds of disposition": the form
        # prints no bound, so a payable amount above the proceeds is refused, not capped.
        CapabilitySelection(
            name="core/at_most",
            params={},
            consumes={
                "amount": "ca/t2017_reserve_amount_payable_after_year_end",
                "bound": "ca/t2017_reserve_proceeds",
            },
            produces={"output": "ca/t2017_reserve_payable_checked"},
        ),
        # (i) "Capital gain x Amount payable after the end of the year / Proceeds of disposition".
        CapabilitySelection(
            name="ca/apply_ratio_or_zero",
            params={"rounding": "ca/t2017_rounding"},
            consumes={
                "amount": "ca/t2017_reserve_capital_gain",
                "numerator": "ca/t2017_reserve_payable_checked",
                "denominator": "ca/t2017_reserve_proceeds",
            },
            produces={"output": "ca/t2017_reserve_by_payment"},
        ),
        # (ii) "Capital gain x Enter the applicable percentage from the table", by the years after
        # the disposition.
        *period_steps(line),
        CapabilitySelection(
            name="ca/apply_percentage",
            params={"rounding": "ca/t2017_rounding"},
            consumes={
                "amount": "ca/t2017_reserve_capital_gain",
                "percentage": "ca/t2017_reserve_applicable_percentage",
            },
            produces={"output": "ca/t2017_reserve_by_percentage"},
        ),
        # "Your reserve for the year cannot be more than the lesser of the following": (i) and (ii).
        CapabilitySelection(
            name="core/lesser_of",
            params={},
            consumes={"amounts": ("ca/t2017_reserve_by_payment", "ca/t2017_reserve_by_percentage")},
            produces={"output": "ca/t2017_reserve_maximum"},
        ),
        # "You do not have to claim the maximum reserve in a tax year (Year A). However, the amount
        # you claim in a later year (Year B) cannot be more than the amount you claimed for that
        # property in the previous year (Year A)": 1 for a year after the disposition, else 0.
        CapabilitySelection(
            name="ca/count_by_conditions",
            params={"conditions": "ca/t2017_later_year_conditions"},
            consumes={"counts": ("ca/t2017_reserve_years_after_disposition",), "amounts": ()},
            produces={"output": "ca/t2017_reserve_later_year"},
        ),
        # The maximum of a later year: the lesser of the maximum and the previous year's claim.
        CapabilitySelection(
            name="core/lesser_of",
            params={},
            consumes={
                "amounts": ("ca/t2017_reserve_maximum", "ca/t2017_reserve_previous_year_claim"),
            },
            produces={"output": "ca/t2017_reserve_later_year_maximum"},
        ),
        # The claim limit: the maximum in the year of disposition, the later-year maximum after it.
        CapabilitySelection(
            name="core/choose_by_count",
            params={},
            consumes={
                "count": "ca/t2017_reserve_later_year",
                "when_none": "ca/t2017_reserve_maximum",
                "when_any": "ca/t2017_reserve_later_year_maximum",
            },
            produces={"output": "ca/t2017_reserve_claim_limit"},
        ),
        # The reserve claimed, up to the claim limit. A claim above it is refused, not capped.
        CapabilitySelection(
            name="core/at_most",
            params={},
            consumes={
                "amount": "ca/t2017_reserve_claimed",
                "bound": "ca/t2017_reserve_claim_limit",
            },
            produces={"output": "ca/t2017_row_reserve"},
        ),
    }
    if line in T657_LINES:
        steps |= {
            # Form T657 asks whether the disposition was made in Period 1 of 2024 and whether the
            # reserve is reported on a T5013 slip: 1 for yes, else 0, exported for the chart totals.
            CapabilitySelection(
                name="ca/yes_or_no_count",
                params={},
                consumes={"count": "ca/t2017_reserve_period_1_of_2024"},
                produces={"output": "ca/t2017_reserve_period_1_of_2024_checked"},
            ),
            CapabilitySelection(
                name="ca/yes_or_no_count",
                params={},
                consumes={"count": "ca/t2017_reserve_reported_on_slip"},
                produces={"output": "ca/t2017_reserve_reported_on_slip_checked"},
            ),
            # Guide T4037 sends a Period 1 of 2024 reserve a partnership reports to Part 1 of Chart
            # 2025 or to Period 1 of Chart 2024 by when the partnership's fiscal period began: 1 for
            # yes.
            CapabilitySelection(
                name="ca/yes_or_no_count",
                params={},
                consumes={"count": "ca/t2017_reserve_partnership_year_began_before_june_25_2024"},
                produces={
                    "output": "ca/t2017_reserve_partnership_year_began_before_june_25_2024_checked"
                },
            ),
            # The reserve of the previous year in a later year, else 0, less the 2025 reserve.
            CapabilitySelection(
                name="core/times_count",
                params={},
                consumes={
                    "amount": "ca/t2017_reserve_previous_year_claim",
                    "count": "ca/t2017_reserve_later_year",
                },
                produces={"output": "ca/t2017_row_previous_reserve"},
            ),
            CapabilitySelection(
                name="core/subtract",
                params={},
                consumes={
                    "amount": "ca/t2017_row_previous_reserve",
                    "less": "ca/t2017_row_reserve",
                },
                produces={"output": "ca/t2017_row_change"},
            ),
        }
    return steps


def period_steps(line: int) -> set[CapabilitySelection]:
    """The selections that give the applicable percentage of a row, by the line's period."""
    four_year = CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/t2017_four_year_percentage"},
        consumes={"count": "ca/t2017_reserve_years_after_disposition"},
        produces={"output": "ca/t2017_reserve_four_year_percentage"},
    )
    nine_year = CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/t2017_nine_year_percentage"},
        consumes={"count": "ca/t2017_reserve_years_after_disposition"},
        produces={"output": "ca/t2017_reserve_nine_year_percentage"},
    )
    if line in CHOOSING_LINES:
        return {
            # "Family farm or fishing property and small business corporation shares disposed of to
            # your child, or disposition under a QBT or QCC": 1 for the nine-year kind, else 0.
            CapabilitySelection(
                name="ca/yes_or_no_count",
                params={},
                consumes={"count": "ca/t2017_reserve_nine_year"},
                produces={"output": "ca/t2017_reserve_nine_year_checked"},
            ),
            four_year,
            nine_year,
            CapabilitySelection(
                name="core/choose_by_count",
                params={},
                consumes={
                    "count": "ca/t2017_reserve_nine_year_checked",
                    "when_none": "ca/t2017_reserve_four_year_percentage",
                    "when_any": "ca/t2017_reserve_nine_year_percentage",
                },
                produces={"output": "ca/t2017_reserve_applicable_percentage"},
            ),
        }
    table = nine_year if line in NINE_YEAR_LINES else four_year
    return {
        CapabilitySelection(
            name=table.name,
            params=table.params,
            consumes=table.consumes,
            produces={"output": "ca/t2017_reserve_applicable_percentage"},
        )
    }


def summary_steps() -> set[CapabilitySelection]:
    """The summary's selections, one for each printed line that is computed."""
    totals = {line: f"ca/t2017_line_{line}" for line in ROW_LINES}
    return {
        # The record total of each row form's export, the line's total of the reserves.
        *(
            CapabilitySelection(
                name="core/record_total",
                params={},
                consumes={"records": f"{ROW_FORMS[line]}.t2017_row_reserve"},
                produces={"output": totals[line]},
            )
            for line in ROW_LINES
        ),
        # Lines 2 to 4 "Add lines 2 to 4." (5), line 1 minus line 5 (6).
        CapabilitySelection(
            name="core/sum",
            params={},
            consumes={"parts": ("ca/t2017_line_2", "ca/t2017_line_3", "ca/t2017_line_4")},
            produces={"output": "ca/t2017_line_5"},
        ),
        CapabilitySelection(
            name="core/subtract",
            params={},
            consumes={"amount": "ca/t2017_line_1", "less": "ca/t2017_line_5"},
            produces={"output": "ca/t2017_line_6"},
        ),
        # Lines 8 to 10 "Add lines 8 to 10." (11), line 7 minus line 11 (12).
        CapabilitySelection(
            name="core/sum",
            params={},
            consumes={"parts": ("ca/t2017_line_8", "ca/t2017_line_9", "ca/t2017_line_10")},
            produces={"output": "ca/t2017_line_11"},
        ),
        CapabilitySelection(
            name="core/subtract",
            params={},
            consumes={"amount": "ca/t2017_line_7", "less": "ca/t2017_line_11"},
            produces={"output": "ca/t2017_line_12"},
        ),
        # "Line 6 plus line 12" (13), which is line 15 of the next page.
        CapabilitySelection(
            name="core/sum",
            params={},
            consumes={"parts": ("ca/t2017_line_6", "ca/t2017_line_12")},
            produces={"output": "ca/t2017_line_13"},
        ),
        # Line 16 minus line 17 (18), then "Line 15 plus line 18" (19).
        CapabilitySelection(
            name="core/subtract",
            params={},
            consumes={"amount": "ca/t2017_line_16", "less": "ca/t2017_line_17"},
            produces={"output": "ca/t2017_line_18"},
        ),
        CapabilitySelection(
            name="core/sum",
            params={},
            consumes={"parts": ("ca/t2017_line_13", "ca/t2017_line_18")},
            produces={"output": "ca/t2017_line_19"},
        ),
        # Line 20 minus line 21 (22).
        CapabilitySelection(
            name="core/subtract",
            params={},
            consumes={"amount": "ca/t2017_line_20", "less": "ca/t2017_line_21"},
            produces={"output": "ca/t2017_line_22"},
        ),
        # Line 23 minus line 24 (25).
        CapabilitySelection(
            name="core/subtract",
            params={},
            consumes={"amount": "ca/t2017_line_23", "less": "ca/t2017_line_24"},
            produces={"output": "ca/t2017_line_25"},
        ),
        # The 2024 figure of line 26 less line 23 (26), signed: the form prints no bound.
        CapabilitySelection(
            name="core/subtract",
            params={},
            consumes={
                "amount": "ca/t2017_lines_66990_and_67058_for_2024",
                "less": "ca/t2017_line_23",
            },
            produces={"output": "ca/t2017_line_26"},
        ),
        # Line 26 minus line 27 (28).
        CapabilitySelection(
            name="core/subtract",
            params={},
            consumes={"amount": "ca/t2017_line_26", "less": "ca/t2017_line_27"},
            produces={"output": "ca/t2017_line_28"},
        ),
        # "Add lines 19, 22, 25, and 28" (29), and line 29 plus line 30 (31).
        CapabilitySelection(
            name="core/sum",
            params={},
            consumes={
                "parts": (
                    "ca/t2017_line_19",
                    "ca/t2017_line_22",
                    "ca/t2017_line_25",
                    "ca/t2017_line_28",
                )
            },
            produces={"output": "ca/t2017_line_29"},
        ),
        CapabilitySelection(
            name="core/sum",
            params={},
            consumes={"parts": ("ca/t2017_line_29", "ca/t2017_line_30")},
            produces={"output": "ca/t2017_line_31"},
        ),
    }


# The selections of each row form, and of the summary form, in the form they are declared.
ROW_STEPS = {line: row_steps(line) for line in ROW_LINES}
SUMMARY_STEPS = summary_steps()


# The wiring of each row form: the capability classes and the kinds each one reads and produces.
def row_wiring(line: int) -> set[tuple[object, frozenset[object], frozenset[object]]]:
    wiring: set[tuple[object, frozenset[object], frozenset[object]]] = {
        (
            AtMost,
            frozenset({T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END, T2017_RESERVE_PROCEEDS}),
            frozenset({T2017_RESERVE_PAYABLE_CHECKED}),
        ),
        (
            ApplyRatioOrZero,
            frozenset(
                {T2017_RESERVE_CAPITAL_GAIN, T2017_RESERVE_PAYABLE_CHECKED, T2017_RESERVE_PROCEEDS}
            ),
            frozenset({T2017_RESERVE_BY_PAYMENT}),
        ),
        (
            ApplyPercentage,
            frozenset({T2017_RESERVE_CAPITAL_GAIN, T2017_RESERVE_APPLICABLE_PERCENTAGE}),
            frozenset({T2017_RESERVE_BY_PERCENTAGE}),
        ),
        (
            LesserOf,
            frozenset({T2017_RESERVE_BY_PAYMENT, T2017_RESERVE_BY_PERCENTAGE}),
            frozenset({T2017_RESERVE_MAXIMUM}),
        ),
        (
            CountByConditions,
            frozenset({T2017_RESERVE_YEARS_AFTER_DISPOSITION}),
            frozenset({T2017_RESERVE_LATER_YEAR}),
        ),
        (
            LesserOf,
            frozenset({T2017_RESERVE_MAXIMUM, T2017_RESERVE_PREVIOUS_YEAR_CLAIM}),
            frozenset({T2017_RESERVE_LATER_YEAR_MAXIMUM}),
        ),
        (
            ChooseByCount,
            frozenset(
                {T2017_RESERVE_LATER_YEAR, T2017_RESERVE_MAXIMUM, T2017_RESERVE_LATER_YEAR_MAXIMUM}
            ),
            frozenset({T2017_RESERVE_CLAIM_LIMIT}),
        ),
        (
            AtMost,
            frozenset({T2017_RESERVE_CLAIMED, T2017_RESERVE_CLAIM_LIMIT}),
            frozenset({T2017_ROW_RESERVE}),
        ),
    }
    if line in CHOOSING_LINES:
        wiring |= {
            (
                YesOrNoCount,
                frozenset({T2017_RESERVE_NINE_YEAR}),
                frozenset({T2017_RESERVE_NINE_YEAR_CHECKED}),
            ),
            (
                AmountForCount,
                frozenset({T2017_RESERVE_YEARS_AFTER_DISPOSITION}),
                frozenset({T2017_RESERVE_FOUR_YEAR_PERCENTAGE}),
            ),
            (
                AmountForCount,
                frozenset({T2017_RESERVE_YEARS_AFTER_DISPOSITION}),
                frozenset({T2017_RESERVE_NINE_YEAR_PERCENTAGE}),
            ),
            (
                ChooseByCount,
                frozenset(
                    {
                        T2017_RESERVE_NINE_YEAR_CHECKED,
                        T2017_RESERVE_FOUR_YEAR_PERCENTAGE,
                        T2017_RESERVE_NINE_YEAR_PERCENTAGE,
                    }
                ),
                frozenset({T2017_RESERVE_APPLICABLE_PERCENTAGE}),
            ),
        }
    else:
        wiring.add(
            (
                AmountForCount,
                frozenset({T2017_RESERVE_YEARS_AFTER_DISPOSITION}),
                frozenset({T2017_RESERVE_APPLICABLE_PERCENTAGE}),
            )
        )
    if line in T657_LINES:
        wiring |= {
            (
                YesOrNoCount,
                frozenset({T2017_RESERVE_PERIOD_1_OF_2024}),
                frozenset({T2017_RESERVE_PERIOD_1_OF_2024_CHECKED}),
            ),
            (
                YesOrNoCount,
                frozenset({T2017_RESERVE_REPORTED_ON_SLIP}),
                frozenset({T2017_RESERVE_REPORTED_ON_SLIP_CHECKED}),
            ),
            (
                YesOrNoCount,
                frozenset({T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024}),
                frozenset({T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024_CHECKED}),
            ),
            (
                TimesCount,
                frozenset({T2017_RESERVE_PREVIOUS_YEAR_CLAIM, T2017_RESERVE_LATER_YEAR}),
                frozenset({T2017_ROW_PREVIOUS_RESERVE}),
            ),
            (
                Subtract,
                frozenset({T2017_ROW_PREVIOUS_RESERVE, T2017_ROW_RESERVE}),
                frozenset({T2017_ROW_CHANGE}),
            ),
        }
    return wiring


# The wiring of the row forms and of the summary form (the kinds of each step, by class).
ROW_WIRING = {line: row_wiring(line) for line in ROW_LINES}
SUMMARY_WIRING: set[tuple[object, frozenset[object], frozenset[object]]] = {
    (RecordTotal, frozenset({ROW_RESERVES[line]}), frozenset({kind}))
    for line, kind in (
        (2, T2017_LINE_2),
        (3, T2017_LINE_3),
        (4, T2017_LINE_4),
        (8, T2017_LINE_8),
        (9, T2017_LINE_9),
        (10, T2017_LINE_10),
        (17, T2017_LINE_17),
        (21, T2017_LINE_21),
        (24, T2017_LINE_24),
        (27, T2017_LINE_27),
    )
}
SUMMARY_WIRING |= {
    (Sum, frozenset({T2017_LINE_2, T2017_LINE_3, T2017_LINE_4}), frozenset({T2017_LINE_5})),
    (Subtract, frozenset({T2017_LINE_1, T2017_LINE_5}), frozenset({T2017_LINE_6})),
    (Sum, frozenset({T2017_LINE_8, T2017_LINE_9, T2017_LINE_10}), frozenset({T2017_LINE_11})),
    (Subtract, frozenset({T2017_LINE_7, T2017_LINE_11}), frozenset({T2017_LINE_12})),
    (Sum, frozenset({T2017_LINE_6, T2017_LINE_12}), frozenset({T2017_LINE_13})),
    (Subtract, frozenset({T2017_LINE_16, T2017_LINE_17}), frozenset({T2017_LINE_18})),
    (Sum, frozenset({T2017_LINE_13, T2017_LINE_18}), frozenset({T2017_LINE_19})),
    (Subtract, frozenset({T2017_LINE_20, T2017_LINE_21}), frozenset({T2017_LINE_22})),
    (Subtract, frozenset({T2017_LINE_23, T2017_LINE_24}), frozenset({T2017_LINE_25})),
    (
        Subtract,
        frozenset({T2017_LINES_66990_AND_67058_FOR_2024, T2017_LINE_23}),
        frozenset({T2017_LINE_26}),
    ),
    (Subtract, frozenset({T2017_LINE_26, T2017_LINE_27}), frozenset({T2017_LINE_28})),
    (
        Sum,
        frozenset({T2017_LINE_19, T2017_LINE_22, T2017_LINE_25, T2017_LINE_28}),
        frozenset({T2017_LINE_29}),
    ),
    (Sum, frozenset({T2017_LINE_29, T2017_LINE_30}), frozenset({T2017_LINE_31})),
}
