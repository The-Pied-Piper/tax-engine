"""The CA-ON manifest entries of Form T746 "Calculating Your Deduction for Refund of Unused RRSP,
PRPP, and SPP Contributions" (see `test_manifest_t746.py`).

Two forms. The row form `ca/t746_year` is lines 1 to 4 for one year of unused contributions, run
once for each record of its list `ca/t746_years`: the check that line 3 is no more than line 2 and
line 4, line 2 minus line 3. The summary form `ca/t746` runs once: line 4 as the total over the
years, line 12 (lines 6 to 10; line 11, the amount from Form T2205, is not built yet) and line 13,
the lesser of lines 4 and 12, the deduction for T1 line 23200. T1 reads line 13 as
`ca/t746.t746_deduction` (see `05_deductions.yaml` and `05m_t929_copies_2.yaml`).

The return selects none of the steps of the forms and declares no output for them, as for Form T90.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    T746_CONDITIONS_MET,
    T746_CONTRIBUTIONS,
    T746_CONTRIBUTIONS_DEDUCTED,
    T746_CONTRIBUTIONS_DEDUCTED_CHECKED,
    T746_DEDUCTION,
    T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW,
    T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW_CHECKED,
    T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS,
    T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS_CHECKED,
    T746_LINE_13,
    T746_T4A_BOX_18_SPP,
    T746_T4A_BOX_194,
    T746_T4RIF_BOX_24,
    T746_T4RSP_BOX_20,
    T746_T4RSP_BOX_22,
    T746_UNUSED_CONTRIBUTIONS,
    T746_UNUSED_CONTRIBUTIONS_OF_YEAR,
    T746_WITHDRAWALS,
)

YEAR_FORM = "ca/t746_year"
SUMMARY_FORM = "ca/t746"
YEARS_LIST = "ca/t746_years"

# The starting inputs of the summary form (lines 5 to 10), in `01o_t746_inputs.yaml`, with the list
# of the years the row form runs over.
SUMMARY_INPUTS = frozenset(
    {
        "ca/t746_withdrawal_year",
        "ca/t746_t4rsp_box_20",
        "ca/t746_t4rsp_box_22",
        "ca/t746_t4rif_box_24",
        "ca/t746_t4a_box_194",
        "ca/t746_t4a_box_18_spp",
        # The two eligibility conditions printed above line 1: the filer's yes or no answers.
        "ca/t746_expected_to_fully_deduct_contributions",
        "ca/t746_did_not_make_contributions_intending_to_withdraw",
    }
)
INPUTS = SUMMARY_INPUTS | {YEARS_LIST}

# The exports of the forms. Line 1 and line 5 are exported as entered: no step reads them.
YEAR_EXPORTS = frozenset({"ca/t746_unused_contributions_of_year", "ca/t746_contribution_year"})
SUMMARY_EXPORTS = frozenset({"ca/t746_deduction", "ca/t746_withdrawal_year"})

# The return selects no step of the forms and reads no output of them in this family.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

YEAR_STEPS = {
    # Line 3: a part of line 2, so refused above it and never capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t746_contributions_deducted",
            "bound": "ca/t746_contributions",
        },
        produces={"output": "ca/t746_contributions_deducted_checked"},
    ),
    # Line 4 "Line 2 minus line 3".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t746_contributions",
            "less": "ca/t746_contributions_deducted_checked",
        },
        produces={"output": "ca/t746_unused_contributions_of_year"},
    ),
}

SUMMARY_STEPS = {
    # "one or both of the following conditions apply": each answer a count of 1 or 0.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t746_expected_to_fully_deduct_contributions"},
        produces={"output": "ca/t746_expected_to_fully_deduct_contributions_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t746_did_not_make_contributions_intending_to_withdraw"},
        produces={"output": "ca/t746_did_not_make_contributions_intending_to_withdraw_checked"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t746_conditions"},
        consumes={
            "counts": (
                "ca/t746_expected_to_fully_deduct_contributions_checked",
                "ca/t746_did_not_make_contributions_intending_to_withdraw_checked",
            ),
            "amounts": (),
        },
        produces={"output": "ca/t746_conditions_met"},
    ),
    # Line 4 on the most recent form: the total of the line 4 amounts of all years.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t746_year.t746_unused_contributions_of_year"},
        produces={"output": "ca/t746_unused_contributions"},
    ),
    # Line 12 "Add lines 6 to 11": lines 6 to 10 (line 11 is not built yet).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t746_t4rsp_box_20",
                "ca/t746_t4rsp_box_22",
                "ca/t746_t4rif_box_24",
                "ca/t746_t4a_box_194",
                "ca/t746_t4a_box_18_spp",
            )
        },
        produces={"output": "ca/t746_withdrawals"},
    ),
    # Line 13 "the amount from line 4 or the amount from line 12, whichever is less".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t746_unused_contributions", "ca/t746_withdrawals")},
        produces={"output": "ca/t746_line_13"},
    ),
    # "For you to claim the deduction": line 13 when one or both conditions are met, else 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t746_line_13", "count": "ca/t746_conditions_met"},
        produces={"output": "ca/t746_deduction"},
    ),
}

# The wiring of the steps, as `test_manifest_t746.py` reads it from the composed forms: the
# capability class, the kinds it consumes and the kinds it produces.
YEAR_WIRING = {
    (
        AtMost,
        frozenset({T746_CONTRIBUTIONS_DEDUCTED, T746_CONTRIBUTIONS}),
        frozenset({T746_CONTRIBUTIONS_DEDUCTED_CHECKED}),
    ),
    (
        Subtract,
        frozenset({T746_CONTRIBUTIONS, T746_CONTRIBUTIONS_DEDUCTED_CHECKED}),
        frozenset({T746_UNUSED_CONTRIBUTIONS_OF_YEAR}),
    ),
}
SUMMARY_WIRING = {
    (
        YesOrNoCount,
        frozenset({T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS}),
        frozenset({T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW}),
        frozenset({T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS_CHECKED,
                T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW_CHECKED,
            }
        ),
        frozenset({T746_CONDITIONS_MET}),
    ),
    (
        Sum,
        frozenset(
            {
                T746_T4RSP_BOX_20,
                T746_T4RSP_BOX_22,
                T746_T4RIF_BOX_24,
                T746_T4A_BOX_194,
                T746_T4A_BOX_18_SPP,
            }
        ),
        frozenset({T746_WITHDRAWALS}),
    ),
    (
        LesserOf,
        frozenset({T746_UNUSED_CONTRIBUTIONS, T746_WITHDRAWALS}),
        frozenset({T746_LINE_13}),
    ),
    (
        TimesCount,
        frozenset({T746_LINE_13, T746_CONDITIONS_MET}),
        frozenset({T746_DEDUCTION}),
    ),
}
