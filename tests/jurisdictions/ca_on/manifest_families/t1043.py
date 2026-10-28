"""The CA-ON manifest entries of Form T1043 "Deduction for Excess Registered Pension Plan Transfers
You Withdrew from an RRSP, a PRPP, an SPP, or a RRIF" (see `test_manifest_t1043.py`).

One form, `ca/t1043`, run once: line 1 (the lesser of the excess transfer on the T4A slips and the
excess amount on the receipt), line 4 (line 2 plus line 3, checked to be no more than line 1),
line 5, line 7 (checked to be no more than line 6), line 8 and line 9, the lesser of lines 5 and
8, which the two yes or no answers of the conditions ("you have to meet both") multiply into the
deduction for T1 line 23200. T1 reads line 9 as `ca/t1043.t1043_deduction` (see
`05_deductions.yaml` and `05m_t929_copies_2.yaml`).

The return selects none of the steps of the form and declares no output for it, as for Form T746.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca.catalog import (
    T1043_CLAIMED_AS_RRSP_DEDUCTION,
    T1043_DEDUCTED_USING_FORM,
    T1043_DEDUCTION,
    T1043_EXCESS_AMOUNT_ON_RECEIPT,
    T1043_EXCESS_TRANSFER_ON_T4A,
    T1043_EXCESS_TRANSFERRED,
    T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED,
    T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED_CHECKED,
    T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED,
    T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED_CHECKED,
    T1043_LINE_9,
    T1043_LINE_9_IF_EXCESS_INCLUDED,
    T1043_NOT_YET_CLAIMED,
    T1043_PART_DEDUCTIBLE_ELSEWHERE,
    T1043_PART_DEDUCTIBLE_ELSEWHERE_CHECKED,
    T1043_PLAN_AMOUNTS_IN_INCOME,
    T1043_PLAN_AMOUNTS_REMAINING,
    T1043_PREVIOUSLY_CLAIMED,
    T1043_PREVIOUSLY_CLAIMED_CHECKED,
)

FORM = "ca/t1043"

# The starting inputs of the form (lines 1, 2, 3, 6 and 7), in `01p_t1043_inputs.yaml`.
INPUTS = frozenset(
    {
        "ca/t1043_excess_transfer_on_t4a",
        "ca/t1043_excess_amount_on_receipt",
        "ca/t1043_claimed_as_rrsp_deduction",
        "ca/t1043_deducted_using_form",
        "ca/t1043_plan_amounts_in_income",
        "ca/t1043_part_deductible_elsewhere",
        # The two conditions "you have to meet both", yes or no answers (1 or 0).
        "ca/t1043_included_excess_in_income_for_year_transferred",
        "ca/t1043_including_plan_amounts_in_income_for_year_claimed",
    }
)

# The export of the form: line 9.
EXPORTS = frozenset({"ca/t1043_deduction"})

# The return selects no step of the form and reads no output of it in this family.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

FORM_STEPS = {
    # "To claim the deduction, you have to meet both of the following conditions".
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1043_included_excess_in_income_for_year_transferred"},
        produces={"output": "ca/t1043_included_excess_in_income_for_year_transferred_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1043_including_plan_amounts_in_income_for_year_claimed"},
        produces={"output": "ca/t1043_including_plan_amounts_in_income_for_year_claimed_checked"},
    ),
    # Line 1 "whichever is less".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/t1043_excess_transfer_on_t4a", "ca/t1043_excess_amount_on_receipt")
        },
        produces={"output": "ca/t1043_excess_transferred"},
    ),
    # Line 4 "Line 2 plus line 3".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1043_claimed_as_rrsp_deduction", "ca/t1043_deducted_using_form")},
        produces={"output": "ca/t1043_previously_claimed"},
    ),
    # Lines 2 and 3 are parts of line 1, so refused above it and never capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1043_previously_claimed",
            "bound": "ca/t1043_excess_transferred",
        },
        produces={"output": "ca/t1043_previously_claimed_checked"},
    ),
    # Line 5 "Line 1 minus line 4".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1043_excess_transferred",
            "less": "ca/t1043_previously_claimed_checked",
        },
        produces={"output": "ca/t1043_not_yet_claimed"},
    ),
    # Line 7 is a part of line 6, so refused above it and never capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1043_part_deductible_elsewhere",
            "bound": "ca/t1043_plan_amounts_in_income",
        },
        produces={"output": "ca/t1043_part_deductible_elsewhere_checked"},
    ),
    # Line 8 "Line 6 minus line 7".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1043_plan_amounts_in_income",
            "less": "ca/t1043_part_deductible_elsewhere_checked",
        },
        produces={"output": "ca/t1043_plan_amounts_remaining"},
    ),
    # Line 9 "Enter the amount from line 5 or line 8, whichever is less."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1043_not_yet_claimed", "ca/t1043_plan_amounts_remaining")},
        produces={"output": "ca/t1043_line_9"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1043_line_9",
            "count": "ca/t1043_included_excess_in_income_for_year_transferred_checked",
        },
        produces={"output": "ca/t1043_line_9_if_excess_included"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1043_line_9_if_excess_included",
            "count": "ca/t1043_including_plan_amounts_in_income_for_year_claimed_checked",
        },
        produces={"output": "ca/t1043_deduction"},
    ),
}

# The wiring of the steps, as `test_manifest_t1043.py` reads it from the composed form: the
# capability class, the kinds it consumes and the kinds it produces.
FORM_WIRING = {
    (
        LesserOf,
        frozenset({T1043_EXCESS_TRANSFER_ON_T4A, T1043_EXCESS_AMOUNT_ON_RECEIPT}),
        frozenset({T1043_EXCESS_TRANSFERRED}),
    ),
    (
        Sum,
        frozenset({T1043_CLAIMED_AS_RRSP_DEDUCTION, T1043_DEDUCTED_USING_FORM}),
        frozenset({T1043_PREVIOUSLY_CLAIMED}),
    ),
    (
        AtMost,
        frozenset({T1043_PREVIOUSLY_CLAIMED, T1043_EXCESS_TRANSFERRED}),
        frozenset({T1043_PREVIOUSLY_CLAIMED_CHECKED}),
    ),
    (
        Subtract,
        frozenset({T1043_EXCESS_TRANSFERRED, T1043_PREVIOUSLY_CLAIMED_CHECKED}),
        frozenset({T1043_NOT_YET_CLAIMED}),
    ),
    (
        AtMost,
        frozenset({T1043_PART_DEDUCTIBLE_ELSEWHERE, T1043_PLAN_AMOUNTS_IN_INCOME}),
        frozenset({T1043_PART_DEDUCTIBLE_ELSEWHERE_CHECKED}),
    ),
    (
        Subtract,
        frozenset({T1043_PLAN_AMOUNTS_IN_INCOME, T1043_PART_DEDUCTIBLE_ELSEWHERE_CHECKED}),
        frozenset({T1043_PLAN_AMOUNTS_REMAINING}),
    ),
    (
        LesserOf,
        frozenset({T1043_NOT_YET_CLAIMED, T1043_PLAN_AMOUNTS_REMAINING}),
        frozenset({T1043_LINE_9}),
    ),
    (
        YesOrNoCount,
        frozenset({T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED}),
        frozenset({T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED}),
        frozenset({T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED_CHECKED}),
    ),
    (
        TimesCount,
        frozenset({T1043_LINE_9, T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED_CHECKED}),
        frozenset({T1043_LINE_9_IF_EXCESS_INCLUDED}),
    ),
    (
        TimesCount,
        frozenset(
            {
                T1043_LINE_9_IF_EXCESS_INCLUDED,
                T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED_CHECKED,
            }
        ),
        frozenset({T1043_DEDUCTION}),
    ),
}
