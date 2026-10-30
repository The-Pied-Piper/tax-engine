"""The CA-ON manifest entries of Form T1032, "Joint Election to Split Pension Income" (see
`test_manifest_t1032.py`), with the steps of line 33 and Note 1 (`NOTE_1_STEPS`, in
`22d_t1032_line_33_note_1.yaml`) at the end and the steps of line 31 recalculated
(`LINE_31_STEPS`, in `22e_t1032_line_31_note_1.yaml`).

The form is `ca/t1032`: it runs once (no instances) and its steps are the lines of Step 2 to Step 5,
in the order the form prints them. Its starting inputs are in `01j_t1032_inputs.yaml`, and its steps
in `22a_t1032_pension_income_splitting.yaml`. Line 22 is the one input `ca/t1032_line_22`, entered
once with the filer's answer; `22c_t1032_income_tax_deducted.yaml` carries it to T1 line 21000
(`ca/elected_split_pension_deduction`, the transferring spouse's return) or line 11600
(`ca/elected_split_pension_amount`, the receiving spouse's), which are worked out, not entered. The
return also selects the line 1 check of `22b_t1032_line_1_check.yaml`, which compares line 1
with line 8 of the return's own Federal Worksheet for line 31400.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.apply_ratio import ApplyRatio
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.first_record_count import FirstRecordCount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    ELECTED_SPLIT_PENSION_AMOUNT,
    ELECTED_SPLIT_PENSION_DEDUCTION,
    INCOME_TAX_DEDUCTED,
    INCOME_TAX_DEDUCTED_AFTER_ELECTION,
    OTHER_INCOME,
    PENSION_CHART_LINE_8,
    PENSION_INCOME_CREDIT,
    PENSION_WORKSHEET_AMOUNT,
    T1032_ELECTION_APPLIES,
    T1032_ELIGIBLE_PENSION_INCOME,
    T1032_FILER_IS_TRANSFERRING_SPOUSE,
    T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED,
    T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL,
    T1032_INCOME_TAX_DEDUCTED_ON_PENSION,
    T1032_LINE_1_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_2_CHECKED,
    T1032_LINE_3,
    T1032_LINE_4_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_5,
    T1032_LINE_7,
    T1032_LINE_8,
    T1032_LINE_8_BEFORE_GATE,
    T1032_LINE_12,
    T1032_LINE_13,
    T1032_LINE_15,
    T1032_LINE_16,
    T1032_LINE_17,
    T1032_LINE_18,
    T1032_LINE_18_MONTHS_IN_TAX_YEAR,
    T1032_LINE_19,
    T1032_LINE_21,
    T1032_LINE_21_IF_CONDITIONS_MET,
    T1032_LINE_21_IF_NOT_SEPARATED,
    T1032_LINE_22,
    T1032_LINE_22_CHECKED,
    T1032_LINE_22_TOTAL,
    T1032_LINE_29,
    T1032_LINE_30,
    T1032_LINE_31,
    T1032_LINE_31_AFTER_NOTE_1,
    T1032_LINE_33,
    T1032_LINE_34,
    T1032_LINE_35_CHECKED,
    T1032_LINE_35_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_35_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_36,
    T1032_LINE_37_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_39,
    T1032_LINE_39_TOTAL,
    T1032_LINE_42,
    T1032_LINE_42_TOTAL,
    T1032_LINE_31400,
    T1032_LINE_31400_RECEIVING,
    T1032_LINE_31400_RECEIVING_TOTAL,
    T1032_LINE_31400_TRANSFERRING,
    T1032_LINE_31400_TRANSFERRING_TOTAL,
    T1032_LINE_43700,
    T1032_MARITAL_STATUS_CHANGED,
    T1032_MARITAL_STATUS_CHANGED_CHECKED,
    T1032_MONTHS_IN_TAX_YEAR,
    T1032_MONTHS_IN_TAX_YEAR_CEILING,
    T1032_MONTHS_IN_TAX_YEAR_CHECKED,
    T1032_MONTHS_MARRIED,
    T1032_MONTHS_MARRIED_CHECKED,
    T1032_NOT_SEPARATED_90_DAYS,
    T1032_NOT_SEPARATED_90_DAYS_CHECKED,
    T1032_NOTE_1_APPLIES,
    T1032_NOTE_1_LINE_8_BOUND,
    T1032_NOTE_1_LINE_8_CHECKED,
    T1032_NOTE_1_LINE_8_TO_CHECK,
    T1032_NOTE_1_LINE_17,
    T1032_NOTE_1_LINE_17_IS_ZERO,
    T1032_NOTE_1_LINE_22,
    T1032_NOTE_1_LINE_29,
    T1032_NOTE_1_LINE_29_APPLIES,
    T1032_NOTE_1_LINE_30,
    T1032_NOTE_1_LINE_31,
    T1032_NOTE_1_LINE_32_LIMIT,
    T1032_NOTE_1_LINE_33,
    T1032_NOTE_1_PAYMENTS_A_TO_D,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_CHECKED,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_IF_APPLIES,
    T1032_NOTE_1_PAYMENTS_TO_REMOVE,
    T1032_NOTE_1_PAYMENTS_TOTAL,
    T1032_NOTE_1_PAYMENTS_TOTAL_IF_APPLIES,
    T1032_NOTE_1_RECALCULATION,
    T1032_NOTE_1_RESULT,
    T1032_NOTE_1_RESULT_LIMIT,
    T1032_OTHER_INCOME_OF_TRANSFERRING_SPOUSE,
    T1032_RCA_PAYMENTS_QUALIFY,
    T1032_RCA_PAYMENTS_QUALIFY_CHECKED,
    T1032_RECEIVING_SPOUSE_PENSION_AMOUNT,
    T1032_RECEIVING_SPOUSE_UNDER_65,
    T1032_RECEIVING_SPOUSE_UNDER_65_CHECKED,
    T1032_RESIDENTS_OF_CANADA,
    T1032_RESIDENTS_OF_CANADA_CHECKED,
    T1032_T4A_BOX_128,
    T1032_T4A_RCA_BOX_17,
    T1032_TRANSFERRING_SPOUSE_65_OR_OLDER,
    T1032_TRANSFERRING_SPOUSE_65_OR_OLDER_CHECKED,
    T1032_TRANSFERRING_SPOUSE_DIED,
    T1032_TRANSFERRING_SPOUSE_DIED_CHECKED,
    T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE,
    T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED,
)

FORM = "ca/t1032"

# The form's checked answer, exported and read by the line 1 check as the kind `<form>.<export>`, a
# record list of the one checked count.
T1032_FILER_IS_TRANSFERRING_SPOUSE_EXPORT = RecordListKind(
    "ca/t1032.t1032_filer_is_transferring_spouse_checked",
    fields=(T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED,),
)

# The form's exports the return totals (22c_t1032_income_tax_deducted.yaml), each a record list of
# the one exported amount.
T1032_LINE_22_EXPORT = RecordListKind(
    "ca/t1032.t1032_line_22_checked", fields=(T1032_LINE_22_CHECKED,)
)
T1032_LINE_31400_TRANSFERRING_EXPORT = RecordListKind(
    "ca/t1032.t1032_line_31400_transferring", fields=(T1032_LINE_31400_TRANSFERRING,)
)
T1032_LINE_31400_RECEIVING_EXPORT = RecordListKind(
    "ca/t1032.t1032_line_31400_receiving", fields=(T1032_LINE_31400_RECEIVING,)
)
T1032_LINE_39_EXPORT = RecordListKind("ca/t1032.t1032_line_39", fields=(T1032_LINE_39,))
T1032_LINE_42_EXPORT = RecordListKind("ca/t1032.t1032_line_42", fields=(T1032_LINE_42,))

# The dataset the return step reads: the election applies when line 22 is above 0.
RETURN_DATASETS = frozenset({"ca/t1032_election_applies_conditions"})

# The starting inputs of the form, in `01j_t1032_inputs.yaml`: the figures and answers the
# transferring spouse and the receiving spouse enter on the form, and the answer naming the filer's
# own spouse.
INPUTS = frozenset(
    {
        "ca/t1032_eligible_pension_income",
        "ca/t1032_t4a_box_128",
        "ca/t1032_t4a_rca_box_17",
        "ca/t1032_rca_payments_qualify",
        "ca/t1032_marital_status_changed",
        "ca/t1032_filer_is_transferring_spouse",
        "ca/t1032_line_22",
        "ca/t1032_months_married",
        "ca/t1032_months_in_tax_year",
        "ca/t1032_transferring_spouse_died",
        "ca/t1032_not_separated_90_days",
        "ca/t1032_residents_of_canada",
        "ca/t1032_receiving_spouse_pension_amount",
        "ca/t1032_income_tax_deducted_on_pension",
        "ca/t1032_receiving_spouse_under_65",
        "ca/t1032_transferring_spouse_65_or_older",
        "ca/t1032_note_1_payments_a_to_d",
        "ca/t1032_note_1_payments_due_to_death",
    }
)

# The existing pension income maximum, $2,000, the cap of lines 31 and 34 ("whichever is less").
EXISTING_DATASETS = frozenset({"ca/pension_income_maximum"})

# The datasets the steps of the form read: the ceiling of lines 5 and 13, the 12 months of the tax
# year, the maximum rate of line 20, and the rounding rule of the ratios of lines 29 and 36.
DATASETS = (
    frozenset(
        {
            "ca/t1032_rca_and_veterans_ceiling",
            "ca/t1032_months_in_tax_year_maximum",
            "ca/t1032_maximum_split_rate",
            "ca/t1032_rounding",
        }
    )
    | EXISTING_DATASETS
)

# The exports of the form, in the order the form prints them: line 21, the elected amount checked
# (line 22), the two line 31400 amounts, line 39 and line 42.
EXPORTS = (
    "ca/t1032_line_21",
    "ca/t1032_filer_is_transferring_spouse_checked",
    "ca/t1032_line_22_checked",
    "ca/t1032_line_31400_transferring",
    "ca/t1032_line_31400_receiving",
    "ca/t1032_line_39",
    "ca/t1032_line_42",
)

# The selections of the form, one for each line that computes (the form has thirty-two).
# The return selects only the checks of `22b_t1032_line_1_check.yaml` (STEPS: line 1 against line 8
# of the Federal Worksheet, line 4 against other income), listing their three checked amounts as
# outputs (OUTPUTS): the check runs only because they are read.
OUTPUTS = frozenset(
    {
        "ca/t1032_line_1_of_transferring_spouse_checked",
        "ca/t1032_worksheet_line_8_of_transferring_spouse_checked",
        "ca/t1032_line_4_of_transferring_spouse_checked",
    }
)
STEPS = {
    # "Enter the amount ... calculated on line 8 of the transferring spouse's ... Federal
    # Worksheet for line 31400" is the transferring spouse's return only: the answer the form
    # checked, its first value.
    CapabilitySelection(
        name="core/first_record_count",
        params={},
        consumes={"records": "ca/t1032.t1032_filer_is_transferring_spouse_checked"},
        produces={"output": "ca/t1032_filer_is_transferring_spouse_total"},
    ),
    # Line 1 of this return when it is the transferring spouse's, otherwise 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_eligible_pension_income",
            "count": "ca/t1032_filer_is_transferring_spouse_total",
        },
        produces={"output": "ca/t1032_line_1_of_transferring_spouse"},
    ),
    # Line 8 of this return's Federal Worksheet for line 31400 when it is the transferring spouse's.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/pension_chart_line_8",
            "count": "ca/t1032_filer_is_transferring_spouse_total",
        },
        produces={"output": "ca/t1032_worksheet_line_8_of_transferring_spouse"},
    ),
    # Line 1 refused above the worksheet's line 8.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_line_1_of_transferring_spouse",
            "bound": "ca/t1032_worksheet_line_8_of_transferring_spouse",
        },
        produces={"output": "ca/t1032_line_1_of_transferring_spouse_checked"},
    ),
    # Line 1 refused below the worksheet's line 8.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_worksheet_line_8_of_transferring_spouse",
            "bound": "ca/t1032_line_1_of_transferring_spouse",
        },
        produces={"output": "ca/t1032_worksheet_line_8_of_transferring_spouse_checked"},
    ),
    # Line 4 (box 17 of the T4A-RCA slips) of this return when it is the transferring spouse's.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_t4a_rca_box_17",
            "count": "ca/t1032_filer_is_transferring_spouse_total",
        },
        produces={"output": "ca/t1032_line_4_of_transferring_spouse"},
    ),
    # Other income (T1 line 13000) of this return when it is the transferring spouse's.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/other_income",
            "count": "ca/t1032_filer_is_transferring_spouse_total",
        },
        produces={"output": "ca/t1032_other_income_of_transferring_spouse"},
    ),
    # Line 4 refused above the return's other income, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_line_4_of_transferring_spouse",
            "bound": "ca/t1032_other_income_of_transferring_spouse",
        },
        produces={"output": "ca/t1032_line_4_of_transferring_spouse_checked"},
    ),
    # 08m_other_federal_non_refundable_credits.yaml: T1 line 31400 from the form's two amounts, when
    # the election applies (the worksheet amount otherwise).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1032.t1032_line_31400_transferring"},
        produces={"output": "ca/t1032_line_31400_transferring_total"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1032.t1032_line_31400_receiving"},
        produces={"output": "ca/t1032_line_31400_receiving_total"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_filer_is_transferring_spouse_total",
            "when_none": "ca/t1032_line_31400_receiving_total",
            "when_any": "ca/t1032_line_31400_transferring_total",
        },
        produces={"output": "ca/t1032_line_31400"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_election_applies",
            "when_none": "ca/pension_worksheet_amount",
            "when_any": "ca/t1032_line_31400",
        },
        produces={"output": "ca/pension_income_credit"},
    ),
    # 22c_t1032_income_tax_deducted.yaml: T1 line 43700 from the form's line 22, 39 and 42.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1032.t1032_line_22_checked"},
        produces={"output": "ca/t1032_line_22_total"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1032_election_applies_conditions"},
        consumes={"counts": (), "amounts": ("ca/t1032_line_22_total",)},
        produces={"output": "ca/t1032_election_applies"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1032.t1032_line_39"},
        produces={"output": "ca/t1032_line_39_total"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1032.t1032_line_42"},
        produces={"output": "ca/t1032_line_42_total"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_filer_is_transferring_spouse_total",
            "when_none": "ca/t1032_line_42_total",
            "when_any": "ca/t1032_line_39_total",
        },
        produces={"output": "ca/t1032_line_43700"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_election_applies",
            "when_none": "ca/income_tax_deducted",
            "when_any": "ca/t1032_line_43700",
        },
        produces={"output": "ca/income_tax_deducted_after_election"},
    ),
    # Line 22 on T1 line 21000 (the transferring spouse's return) and on line 11600 (the receiving
    # spouse's): the one amount, by the answer.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_line_22_total",
            "count": "ca/t1032_filer_is_transferring_spouse_total",
        },
        produces={"output": "ca/elected_split_pension_deduction"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1032_line_22_total",
            "less": "ca/elected_split_pension_deduction",
        },
        produces={"output": "ca/elected_split_pension_amount"},
    ),
}
WIRING = {
    (
        TimesCount,
        frozenset({T1032_LINE_22_TOTAL, T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL}),
        frozenset({ELECTED_SPLIT_PENSION_DEDUCTION}),
    ),
    (
        Subtract,
        frozenset({T1032_LINE_22_TOTAL, ELECTED_SPLIT_PENSION_DEDUCTION}),
        frozenset({ELECTED_SPLIT_PENSION_AMOUNT}),
    ),
    (
        RecordTotal,
        frozenset({T1032_LINE_31400_TRANSFERRING_EXPORT}),
        frozenset({T1032_LINE_31400_TRANSFERRING_TOTAL}),
    ),
    (
        RecordTotal,
        frozenset({T1032_LINE_31400_RECEIVING_EXPORT}),
        frozenset({T1032_LINE_31400_RECEIVING_TOTAL}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL,
                T1032_LINE_31400_RECEIVING_TOTAL,
                T1032_LINE_31400_TRANSFERRING_TOTAL,
            }
        ),
        frozenset({T1032_LINE_31400}),
    ),
    (
        ChooseByCount,
        frozenset({T1032_ELECTION_APPLIES, PENSION_WORKSHEET_AMOUNT, T1032_LINE_31400}),
        frozenset({PENSION_INCOME_CREDIT}),
    ),
    (
        RecordTotal,
        frozenset({T1032_LINE_22_EXPORT}),
        frozenset({T1032_LINE_22_TOTAL}),
    ),
    (CountByConditions, frozenset({T1032_LINE_22_TOTAL}), frozenset({T1032_ELECTION_APPLIES})),
    (RecordTotal, frozenset({T1032_LINE_39_EXPORT}), frozenset({T1032_LINE_39_TOTAL})),
    (RecordTotal, frozenset({T1032_LINE_42_EXPORT}), frozenset({T1032_LINE_42_TOTAL})),
    (
        ChooseByCount,
        frozenset(
            {T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL, T1032_LINE_42_TOTAL, T1032_LINE_39_TOTAL}
        ),
        frozenset({T1032_LINE_43700}),
    ),
    (
        ChooseByCount,
        frozenset({T1032_ELECTION_APPLIES, INCOME_TAX_DEDUCTED, T1032_LINE_43700}),
        frozenset({INCOME_TAX_DEDUCTED_AFTER_ELECTION}),
    ),
    (
        FirstRecordCount,
        frozenset({T1032_FILER_IS_TRANSFERRING_SPOUSE_EXPORT}),
        frozenset({T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL}),
    ),
    (
        TimesCount,
        frozenset({T1032_ELIGIBLE_PENSION_INCOME, T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL}),
        frozenset({T1032_LINE_1_OF_TRANSFERRING_SPOUSE}),
    ),
    (
        TimesCount,
        frozenset({PENSION_CHART_LINE_8, T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL}),
        frozenset({T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE}),
    ),
    (
        AtMost,
        frozenset(
            {T1032_LINE_1_OF_TRANSFERRING_SPOUSE, T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE}
        ),
        frozenset({T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED}),
    ),
    (
        AtMost,
        frozenset(
            {T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE, T1032_LINE_1_OF_TRANSFERRING_SPOUSE}
        ),
        frozenset({T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED}),
    ),
    (
        TimesCount,
        frozenset({T1032_T4A_RCA_BOX_17, T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL}),
        frozenset({T1032_LINE_4_OF_TRANSFERRING_SPOUSE}),
    ),
    (
        TimesCount,
        frozenset({OTHER_INCOME, T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL}),
        frozenset({T1032_OTHER_INCOME_OF_TRANSFERRING_SPOUSE}),
    ),
    (
        AtMost,
        frozenset({T1032_LINE_4_OF_TRANSFERRING_SPOUSE, T1032_OTHER_INCOME_OF_TRANSFERRING_SPOUSE}),
        frozenset({T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED}),
    ),
}

FORM_STEPS = {
    # Lines 1 and 2 and the Step 2 answer: "Line 1 and line 68020" and "Line 2 and line 68025".
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1032_rca_payments_qualify"},
        produces={"output": "ca/t1032_rca_payments_qualify_checked"},
    ),
    # Line 18 intro: "If your marital status changed during the year".
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1032_marital_status_changed"},
        produces={"output": "ca/t1032_marital_status_changed_checked"},
    ),
    # Step 3 "Enter this amount on line 21000 of the transferring spouse's ... return and on line
    # 11600 of the receiving spouse's ... return": the answer naming which return this is.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1032_filer_is_transferring_spouse"},
        produces={"output": "ca/t1032_filer_is_transferring_spouse_checked"},
    ),
    # Line 2 "Enter the amount from box 128", included in line 1: refused above line 1, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/t1032_t4a_box_128", "bound": "ca/t1032_eligible_pension_income"},
        produces={"output": "ca/t1032_line_2_checked"},
    ),
    # Line 3 "Line 1 minus line 2 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1032_eligible_pension_income",
            "less": "ca/t1032_line_2_checked",
        },
        produces={"output": "ca/t1032_line_3"},
    ),
    # Line 5 "131,483.45", the ceiling of the RCA calculation.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t1032_rca_and_veterans_ceiling"},
        consumes={},
        produces={"output": "ca/t1032_line_5"},
    ),
    # Line 7 "Line 5 minus line 6 (if negative, enter "0")"; line 6 is line 3.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/t1032_line_5", "less": "ca/t1032_line_3"},
        produces={"output": "ca/t1032_line_7"},
    ),
    # Line 8 "Enter whichever is less: line 4 or line 7".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1032_t4a_rca_box_17", "ca/t1032_line_7")},
        produces={"output": "ca/t1032_line_8_before_gate"},
    ),
    # Line 8 "Otherwise, enter "0" on line 8": the amount times the RCA answer, 0 when it is 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_line_8_before_gate",
            "count": "ca/t1032_rca_payments_qualify_checked",
        },
        produces={"output": "ca/t1032_line_8"},
    ),
    # Line 12 "Line 10 plus line 11", where line 10 is line 3 and line 11 is line 8.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1032_line_3", "ca/t1032_line_8")},
        produces={"output": "ca/t1032_line_12"},
    ),
    # Line 13 "131,483.45", the ceiling of the veterans calculation.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t1032_rca_and_veterans_ceiling"},
        consumes={},
        produces={"output": "ca/t1032_line_13"},
    ),
    # Line 15 "Line 13 minus line 14 (if negative, enter "0")"; line 14 is line 12.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/t1032_line_13", "less": "ca/t1032_line_12"},
        produces={"output": "ca/t1032_line_15"},
    ),
    # Line 16 "Enter whichever is less: line 9 or line 15"; line 9 is line 2.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1032_line_2_checked", "ca/t1032_line_15")},
        produces={"output": "ca/t1032_line_16"},
    ),
    # Line 17 "Add lines 3, 8, and 16."
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1032_line_3", "ca/t1032_line_8", "ca/t1032_line_16")},
        produces={"output": "ca/t1032_line_17"},
    ),
    # Line 18 "Number of months married or living common-law", at most the months in the year.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_months_married",
            "bound": "ca/t1032_months_in_tax_year_checked",
        },
        produces={"output": "ca/t1032_months_married_checked"},
    ),
    # Line 18 "Number of months in the tax year (12)": the 12 months, the dataset's maximum.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t1032_months_in_tax_year_maximum"},
        consumes={},
        produces={"output": "ca/t1032_months_in_tax_year_ceiling"},
    ),
    # Line 18 denominator: the printed 12, or under Note 1 the typed months in the tax year when the
    # transferring spouse died.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_transferring_spouse_died_checked",
            "when_none": "ca/t1032_months_in_tax_year_ceiling",
            "when_any": "ca/t1032_months_in_tax_year",
        },
        produces={"output": "ca/t1032_line_18_months_in_tax_year"},
    ),
    # Line 18 denominator, at most 12 (or the months to the month of death, Note 1).
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_line_18_months_in_tax_year",
            "bound": "ca/t1032_months_in_tax_year_ceiling",
        },
        produces={"output": "ca/t1032_months_in_tax_year_checked"},
    ),
    # Line 18 "Divided by ... multiplied by Amount from line 17": line 17 times the months married
    # over the months in the tax year, rounded once; a zero denominator is refused.
    CapabilitySelection(
        name="core/apply_ratio",
        params={"rounding": "ca/t1032_rounding"},
        consumes={
            "amount": "ca/t1032_line_17",
            "numerator": "ca/t1032_months_married_checked",
            "denominator": "ca/t1032_months_in_tax_year_checked",
        },
        produces={"output": "ca/t1032_line_18"},
    ),
    # Line 19 "Enter the amount from line 18, if it applies. Otherwise, enter the amount from
    # line 17."
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_marital_status_changed_checked",
            "when_none": "ca/t1032_line_17",
            "when_any": "ca/t1032_line_18",
        },
        produces={"output": "ca/t1032_line_19"},
    ),
    # Line 21 "Line 19 multiplied by line 20 Maximum split-pension amount", line 20 being 50%.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t1032_maximum_split_rate"},
        consumes={"base": "ca/t1032_line_19"},
        produces={"output": "ca/t1032_line_21"},
    ),
    # Line 22 "The split-pension amount cannot be more than the amount from line 21": refused.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/t1032_line_22", "bound": "ca/t1032_line_21_if_conditions_met"},
        produces={"output": "ca/t1032_line_22_checked"},
    ),
    # Line 29 "Line 27 multiplied by line 28": line 22 times line 25 (line 8) over line 26
    # (line 17),
    # zero when line 26 is zero.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1032_rounding"},
        consumes={
            "amount": "ca/t1032_line_22_checked",
            "numerator": "ca/t1032_line_8",
            "denominator": "ca/t1032_line_17",
        },
        produces={"output": "ca/t1032_line_29"},
    ),
    # Line 30 "Line 24 minus line 29 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1032_line_22_checked", "less": "ca/t1032_line_29"},
        produces={"output": "ca/t1032_line_30"},
    ),
    # Line 31 "Line 23 minus line 30 =", where line 23 is line 1.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1032_eligible_pension_income", "less": "ca/t1032_line_30"},
        produces={"output": "ca/t1032_line_31"},
    ),
    # Line 31400 of the transferring spouse: "whichever is less: $2,000 or the amount from line 31".
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/pension_income_maximum"},
        consumes={"base": "ca/t1032_line_31_after_note_1"},
        produces={"output": "ca/t1032_line_31400_transferring"},
    ),
    # Line 34 "Line 32 plus line 33 =", line 33 being in `22d_t1032_line_33_note_1.yaml`.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/t1032_receiving_spouse_pension_amount", "ca/t1032_line_33"),
        },
        produces={"output": "ca/t1032_line_34"},
    ),
    # Line 31400 of the receiving spouse: "whichever is less: $2,000 or the amount from line 34".
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/pension_income_maximum"},
        consumes={"base": "ca/t1032_line_34"},
        produces={"output": "ca/t1032_line_31400_receiving"},
    ),
    # Line 35 "Enter the total tax deducted ... entered on line 17" and line 37 "Total tax deducted
    # from all of the transferring spouse's ... slips" (the return's own income tax deducted), each
    # only for the transferring spouse's return (times the checked answer).
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_income_tax_deducted_on_pension",
            "count": "ca/t1032_filer_is_transferring_spouse_checked",
        },
        produces={"output": "ca/t1032_line_35_of_transferring_spouse"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/income_tax_deducted",
            "count": "ca/t1032_filer_is_transferring_spouse_checked",
        },
        produces={"output": "ca/t1032_line_37_of_transferring_spouse"},
    ),
    # Line 35 refused above line 37 (the tax on all the transferring spouse's slips), not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_line_35_of_transferring_spouse",
            "bound": "ca/t1032_line_37_of_transferring_spouse",
        },
        produces={"output": "ca/t1032_line_35_of_transferring_spouse_checked"},
    ),
    # Line 35: the checked amount for the transferring spouse's return, as entered for the receiving
    # spouse's.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_filer_is_transferring_spouse_checked",
            "when_none": "ca/t1032_income_tax_deducted_on_pension",
            "when_any": "ca/t1032_line_35_of_transferring_spouse_checked",
        },
        produces={"output": "ca/t1032_line_35_checked"},
    ),
    # Line 36 "Amount from line 35 multiplied by Amount from line 22 divided by Amount from line
    # 17".
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1032_rounding"},
        consumes={
            "amount": "ca/t1032_line_35_checked",
            "numerator": "ca/t1032_line_22_checked",
            "denominator": "ca/t1032_line_17",
        },
        produces={"output": "ca/t1032_line_36"},
    ),
    # Line 39 "Line 37 minus line 38", entered on line 43700 of the transferring spouse's return.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/income_tax_deducted",
            "less": "ca/t1032_line_36",
        },
        produces={"output": "ca/t1032_line_39"},
    ),
    # Line 42 "Line 40 plus line 41", entered on line 43700 of the receiving spouse's return.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/income_tax_deducted", "ca/t1032_line_36"),
        },
        produces={"output": "ca/t1032_line_42"},
    ),
}

FORM_WIRING = {
    (
        YesOrNoCount,
        frozenset({T1032_RCA_PAYMENTS_QUALIFY}),
        frozenset({T1032_RCA_PAYMENTS_QUALIFY_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({T1032_MARITAL_STATUS_CHANGED}),
        frozenset({T1032_MARITAL_STATUS_CHANGED_CHECKED}),
    ),
    (
        AtMost,
        frozenset({T1032_T4A_BOX_128, T1032_ELIGIBLE_PENSION_INCOME}),
        frozenset({T1032_LINE_2_CHECKED}),
    ),
    (
        Subtract,
        frozenset({T1032_ELIGIBLE_PENSION_INCOME, T1032_LINE_2_CHECKED}),
        frozenset({T1032_LINE_3}),
    ),
    (CreditAmount, frozenset(), frozenset({T1032_LINE_5})),
    (SubtractNotBelowZero, frozenset({T1032_LINE_5, T1032_LINE_3}), frozenset({T1032_LINE_7})),
    (
        LesserOf,
        frozenset({T1032_T4A_RCA_BOX_17, T1032_LINE_7}),
        frozenset({T1032_LINE_8_BEFORE_GATE}),
    ),
    (
        TimesCount,
        frozenset({T1032_LINE_8_BEFORE_GATE, T1032_RCA_PAYMENTS_QUALIFY_CHECKED}),
        frozenset({T1032_LINE_8}),
    ),
    (Sum, frozenset({T1032_LINE_3, T1032_LINE_8}), frozenset({T1032_LINE_12})),
    (CreditAmount, frozenset(), frozenset({T1032_LINE_13})),
    (SubtractNotBelowZero, frozenset({T1032_LINE_13, T1032_LINE_12}), frozenset({T1032_LINE_15})),
    (LesserOf, frozenset({T1032_LINE_2_CHECKED, T1032_LINE_15}), frozenset({T1032_LINE_16})),
    (Sum, frozenset({T1032_LINE_3, T1032_LINE_8, T1032_LINE_16}), frozenset({T1032_LINE_17})),
    (
        AtMost,
        frozenset({T1032_MONTHS_MARRIED, T1032_MONTHS_IN_TAX_YEAR_CHECKED}),
        frozenset({T1032_MONTHS_MARRIED_CHECKED}),
    ),
    (CreditAmount, frozenset(), frozenset({T1032_MONTHS_IN_TAX_YEAR_CEILING})),
    (
        ChooseByCount,
        frozenset(
            {
                T1032_TRANSFERRING_SPOUSE_DIED_CHECKED,
                T1032_MONTHS_IN_TAX_YEAR_CEILING,
                T1032_MONTHS_IN_TAX_YEAR,
            }
        ),
        frozenset({T1032_LINE_18_MONTHS_IN_TAX_YEAR}),
    ),
    (
        AtMost,
        frozenset({T1032_LINE_18_MONTHS_IN_TAX_YEAR, T1032_MONTHS_IN_TAX_YEAR_CEILING}),
        frozenset({T1032_MONTHS_IN_TAX_YEAR_CHECKED}),
    ),
    (
        ApplyRatio,
        frozenset({T1032_LINE_17, T1032_MONTHS_MARRIED_CHECKED, T1032_MONTHS_IN_TAX_YEAR_CHECKED}),
        frozenset({T1032_LINE_18}),
    ),
    (
        ChooseByCount,
        frozenset({T1032_MARITAL_STATUS_CHANGED_CHECKED, T1032_LINE_17, T1032_LINE_18}),
        frozenset({T1032_LINE_19}),
    ),
    (ApplyRate, frozenset({T1032_LINE_19}), frozenset({T1032_LINE_21})),
    (
        YesOrNoCount,
        frozenset({T1032_FILER_IS_TRANSFERRING_SPOUSE}),
        frozenset({T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED}),
    ),
    (
        AtMost,
        frozenset({T1032_LINE_22, T1032_LINE_21_IF_CONDITIONS_MET}),
        frozenset({T1032_LINE_22_CHECKED}),
    ),
    (
        ApplyRatioOrZero,
        frozenset({T1032_LINE_22_CHECKED, T1032_LINE_8, T1032_LINE_17}),
        frozenset({T1032_LINE_29}),
    ),
    (Subtract, frozenset({T1032_LINE_22_CHECKED, T1032_LINE_29}), frozenset({T1032_LINE_30})),
    (
        Subtract,
        frozenset({T1032_ELIGIBLE_PENSION_INCOME, T1032_LINE_30}),
        frozenset({T1032_LINE_31}),
    ),
    (
        CappedAmount,
        frozenset({T1032_LINE_31_AFTER_NOTE_1}),
        frozenset({T1032_LINE_31400_TRANSFERRING}),
    ),
    (
        Sum,
        frozenset({T1032_RECEIVING_SPOUSE_PENSION_AMOUNT, T1032_LINE_33}),
        frozenset({T1032_LINE_34}),
    ),
    (CappedAmount, frozenset({T1032_LINE_34}), frozenset({T1032_LINE_31400_RECEIVING})),
    (
        TimesCount,
        frozenset(
            {T1032_INCOME_TAX_DEDUCTED_ON_PENSION, T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED}
        ),
        frozenset({T1032_LINE_35_OF_TRANSFERRING_SPOUSE}),
    ),
    (
        TimesCount,
        frozenset({INCOME_TAX_DEDUCTED, T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED}),
        frozenset({T1032_LINE_37_OF_TRANSFERRING_SPOUSE}),
    ),
    (
        AtMost,
        frozenset({T1032_LINE_35_OF_TRANSFERRING_SPOUSE, T1032_LINE_37_OF_TRANSFERRING_SPOUSE}),
        frozenset({T1032_LINE_35_OF_TRANSFERRING_SPOUSE_CHECKED}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED,
                T1032_INCOME_TAX_DEDUCTED_ON_PENSION,
                T1032_LINE_35_OF_TRANSFERRING_SPOUSE_CHECKED,
            }
        ),
        frozenset({T1032_LINE_35_CHECKED}),
    ),
    (
        ApplyRatioOrZero,
        frozenset({T1032_LINE_35_CHECKED, T1032_LINE_22_CHECKED, T1032_LINE_17}),
        frozenset({T1032_LINE_36}),
    ),
    (
        Subtract,
        frozenset({INCOME_TAX_DEDUCTED, T1032_LINE_36}),
        frozenset({T1032_LINE_39}),
    ),
    (
        Sum,
        frozenset({INCOME_TAX_DEDUCTED, T1032_LINE_36}),
        frozenset({T1032_LINE_42}),
    ),
}

# The datasets the steps of line 33 read: the $2,000 line 32 is compared with, the $4,000 the
# result is compared with, the two condition lists, the maximum rate of line 21 and the rounding
# rule of lines 18 and 29 (the form's own).
NOTE_1_DATASETS = frozenset(
    {
        "ca/t1032_line_32_figure",
        "ca/t1032_note_1_result_figure",
        "ca/t1032_note_1_applies_conditions",
        "ca/t1032_note_1_recalculation_conditions",
        "ca/t1032_note_1_line_29_applies_conditions",
        "ca/t1032_note_1_line_17_is_zero_conditions",
        "ca/t1032_maximum_split_rate",
        "ca/t1032_rounding",
    }
)

# The selections of line 33 and Note 1, in the order the part lists them.
_YES_NO = [
    ("ca/t1032_receiving_spouse_under_65", "ca/t1032_receiving_spouse_under_65_checked"),
    (
        "ca/t1032_transferring_spouse_65_or_older",
        "ca/t1032_transferring_spouse_65_or_older_checked",
    ),
]
# Part 22f: Note 1 on line 18, the answer whether the transferring spouse died.
DIED_STEPS = {
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1032_transferring_spouse_died"},
        produces={"output": "ca/t1032_transferring_spouse_died_checked"},
    ),
}

# Part 22g: the conditions of page 1.
ELIGIBILITY_STEPS = {
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1032_not_separated_90_days"},
        produces={"output": "ca/t1032_not_separated_90_days_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1032_residents_of_canada"},
        produces={"output": "ca/t1032_residents_of_canada_checked"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_line_21",
            "count": "ca/t1032_not_separated_90_days_checked",
        },
        produces={"output": "ca/t1032_line_21_if_not_separated"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_line_21_if_not_separated",
            "count": "ca/t1032_residents_of_canada_checked",
        },
        produces={"output": "ca/t1032_line_21_if_conditions_met"},
    ),
}

NOTE_1_STEPS = {
    CapabilitySelection(
        name="ca/yes_or_no_count", params={}, consumes={"count": source}, produces={"output": out}
    )
    for source, out in _YES_NO
} | {
    # "e) eligible veterans benefits" is the box 128 amount of line 2: added to a) to d).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1032_note_1_payments_a_to_d", "ca/t1032_t4a_box_128")},
        produces={"output": "ca/t1032_note_1_payments_total"},
    ),
    # "the amount on line 32 is less than $2,000": the $2,000.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t1032_line_32_figure"},
        consumes={},
        produces={"output": "ca/t1032_note_1_line_32_limit"},
    ),
    # "If all of the following conditions apply, calculate line 33 according to the instructions in
    # note 1".
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1032_note_1_applies_conditions"},
        consumes={
            "counts": (
                "ca/t1032_receiving_spouse_under_65_checked",
                "ca/t1032_transferring_spouse_65_or_older_checked",
            ),
            "amounts": (
                "ca/t1032_receiving_spouse_pension_amount",
                "ca/t1032_note_1_line_32_limit",
                "ca/t1032_note_1_payments_total",
            ),
        },
        produces={"output": "ca/t1032_note_1_applies"},
    ),
    # "does not need to remove those payments from line 1 if ... as a consequence of the death of a
    # spouse": the part received on a death, refused above the amounts a) to e).
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_note_1_payments_due_to_death_if_applies",
            "bound": "ca/t1032_note_1_payments_total_if_applies",
        },
        produces={"output": "ca/t1032_note_1_payments_due_to_death_checked"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1032_note_1_payments_total_if_applies",
            "less": "ca/t1032_note_1_payments_due_to_death_checked",
        },
        produces={"output": "ca/t1032_note_1_payments_to_remove"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1032_eligible_pension_income",
            "less": "ca/t1032_note_1_payments_to_remove",
        },
        produces={"output": "ca/t1032_note_1_result"},
    ),
    # "If the result is $4,000 or more ... If the result is less than $4,000": the $4,000.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t1032_note_1_result_figure"},
        consumes={},
        produces={"output": "ca/t1032_note_1_result_limit"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1032_note_1_recalculation_conditions"},
        consumes={
            "counts": ("ca/t1032_note_1_applies",),
            "amounts": ("ca/t1032_note_1_result_limit", "ca/t1032_note_1_result"),
        },
        produces={"output": "ca/t1032_note_1_recalculation"},
    ),
    # "use that result as the amount for line 17".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_note_1_recalculation",
            "when_none": "ca/t1032_line_17",
            "when_any": "ca/t1032_note_1_result",
        },
        produces={"output": "ca/t1032_note_1_line_17"},
    ),
    # Line 22 kept as entered.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/t1032_line_22_checked", "bound": "ca/t1032_line_21"},
        produces={"output": "ca/t1032_note_1_line_22"},
    ),
    # Lines 29 and 30 recalculated.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1032_rounding"},
        consumes={
            "amount": "ca/t1032_note_1_line_22",
            "numerator": "ca/t1032_note_1_line_8_checked",
            "denominator": "ca/t1032_note_1_line_17",
        },
        produces={"output": "ca/t1032_note_1_line_29"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1032_note_1_line_22", "less": "ca/t1032_note_1_line_29"},
        produces={"output": "ca/t1032_note_1_line_30"},
    ),
    # "Enter on line 33 whichever is less: the amount from line 22 or line 30".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1032_note_1_line_22", "ca/t1032_note_1_line_30")},
        produces={"output": "ca/t1032_note_1_line_33"},
    ),
    # "Line 33: Otherwise, enter the amount from line 30" / "If the result is $4,000 or more,
    # enter on line 33 the amount from line 30".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_note_1_recalculation",
            "when_none": "ca/t1032_line_30",
            "when_any": "ca/t1032_note_1_line_33",
        },
        produces={"output": "ca/t1032_line_33"},
    ),
}

# The checks that run only where Note 1 does something (`22h_t1032_note_1_checks.yaml`).
NOTE_1_CHECK_STEPS = {
    # Note 1 "Subtract from line 1 any of the above amounts": the amounts a) to e) if Note 1
    # applies.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_note_1_payments_total",
            "count": "ca/t1032_note_1_applies",
        },
        produces={"output": "ca/t1032_note_1_payments_total_if_applies"},
    ),
    # The part received on a death, when Note 1 applies.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_note_1_payments_due_to_death",
            "count": "ca/t1032_note_1_applies",
        },
        produces={"output": "ca/t1032_note_1_payments_due_to_death_if_applies"},
    ),
    # Line 29 has an amount to multiply when the recalculated line 22 is above 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1032_note_1_line_29_applies_conditions"},
        consumes={"counts": (), "amounts": ("ca/t1032_note_1_line_22",)},
        produces={"output": "ca/t1032_note_1_line_29_applies"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1032_line_8", "count": "ca/t1032_note_1_line_29_applies"},
        produces={"output": "ca/t1032_note_1_line_8_to_check"},
    ),
    # Line 26 is 0: line 27 would divide by 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1032_note_1_line_17_is_zero_conditions"},
        consumes={"counts": (), "amounts": ("ca/t1032_note_1_line_17",)},
        produces={"output": "ca/t1032_note_1_line_17_is_zero"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_note_1_line_17_is_zero",
            "when_none": "ca/t1032_note_1_line_8_to_check",
            "when_any": "ca/t1032_note_1_line_17",
        },
        produces={"output": "ca/t1032_note_1_line_8_bound"},
    ),
    # Line 8 (line 25) is refused where line 26 is 0 and line 8 is not.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t1032_note_1_line_8_to_check",
            "bound": "ca/t1032_note_1_line_8_bound",
        },
        produces={"output": "ca/t1032_note_1_line_8_checked"},
    ),
}

DIED_WIRING = {
    (
        YesOrNoCount,
        frozenset({T1032_TRANSFERRING_SPOUSE_DIED}),
        frozenset({T1032_TRANSFERRING_SPOUSE_DIED_CHECKED}),
    ),
}

ELIGIBILITY_WIRING = {
    (
        YesOrNoCount,
        frozenset({T1032_NOT_SEPARATED_90_DAYS}),
        frozenset({T1032_NOT_SEPARATED_90_DAYS_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({T1032_RESIDENTS_OF_CANADA}),
        frozenset({T1032_RESIDENTS_OF_CANADA_CHECKED}),
    ),
    (
        TimesCount,
        frozenset({T1032_LINE_21, T1032_NOT_SEPARATED_90_DAYS_CHECKED}),
        frozenset({T1032_LINE_21_IF_NOT_SEPARATED}),
    ),
    (
        TimesCount,
        frozenset({T1032_LINE_21_IF_NOT_SEPARATED, T1032_RESIDENTS_OF_CANADA_CHECKED}),
        frozenset({T1032_LINE_21_IF_CONDITIONS_MET}),
    ),
}

# Line 31 recalculated (`22e_t1032_line_31_note_1.yaml`).
LINE_31_STEPS = {
    # "Line 31: Line 23 minus line 30 =", line 23 being line 1, line 30 the recalculated one.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1032_eligible_pension_income", "less": "ca/t1032_note_1_line_30"},
        produces={"output": "ca/t1032_note_1_line_31"},
    ),
    # Note 1 "recalculate lines 18 to 31": the recalculated line 31 when Note 1 recalculates.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1032_note_1_recalculation",
            "when_none": "ca/t1032_line_31",
            "when_any": "ca/t1032_note_1_line_31",
        },
        produces={"output": "ca/t1032_line_31_after_note_1"},
    ),
}

NOTE_1_WIRING = {
    (
        YesOrNoCount,
        frozenset({T1032_RECEIVING_SPOUSE_UNDER_65}),
        frozenset({T1032_RECEIVING_SPOUSE_UNDER_65_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({T1032_TRANSFERRING_SPOUSE_65_OR_OLDER}),
        frozenset({T1032_TRANSFERRING_SPOUSE_65_OR_OLDER_CHECKED}),
    ),
    (
        Sum,
        frozenset({T1032_NOTE_1_PAYMENTS_A_TO_D, T1032_T4A_BOX_128}),
        frozenset({T1032_NOTE_1_PAYMENTS_TOTAL}),
    ),
    (CreditAmount, frozenset(), frozenset({T1032_NOTE_1_LINE_32_LIMIT})),
    (
        CountByConditions,
        frozenset(
            {
                T1032_RECEIVING_SPOUSE_UNDER_65_CHECKED,
                T1032_TRANSFERRING_SPOUSE_65_OR_OLDER_CHECKED,
                T1032_RECEIVING_SPOUSE_PENSION_AMOUNT,
                T1032_NOTE_1_LINE_32_LIMIT,
                T1032_NOTE_1_PAYMENTS_TOTAL,
            }
        ),
        frozenset({T1032_NOTE_1_APPLIES}),
    ),
    (
        AtMost,
        frozenset(
            {T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_IF_APPLIES, T1032_NOTE_1_PAYMENTS_TOTAL_IF_APPLIES}
        ),
        frozenset({T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_CHECKED}),
    ),
    (
        Subtract,
        frozenset(
            {T1032_NOTE_1_PAYMENTS_TOTAL_IF_APPLIES, T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_CHECKED}
        ),
        frozenset({T1032_NOTE_1_PAYMENTS_TO_REMOVE}),
    ),
    (
        Subtract,
        frozenset({T1032_ELIGIBLE_PENSION_INCOME, T1032_NOTE_1_PAYMENTS_TO_REMOVE}),
        frozenset({T1032_NOTE_1_RESULT}),
    ),
    (CreditAmount, frozenset(), frozenset({T1032_NOTE_1_RESULT_LIMIT})),
    (
        CountByConditions,
        frozenset({T1032_NOTE_1_APPLIES, T1032_NOTE_1_RESULT_LIMIT, T1032_NOTE_1_RESULT}),
        frozenset({T1032_NOTE_1_RECALCULATION}),
    ),
    (
        ChooseByCount,
        frozenset({T1032_NOTE_1_RECALCULATION, T1032_LINE_17, T1032_NOTE_1_RESULT}),
        frozenset({T1032_NOTE_1_LINE_17}),
    ),
    (
        AtMost,
        frozenset({T1032_LINE_22_CHECKED, T1032_LINE_21}),
        frozenset({T1032_NOTE_1_LINE_22}),
    ),
    (
        ApplyRatioOrZero,
        frozenset({T1032_NOTE_1_LINE_22, T1032_NOTE_1_LINE_8_CHECKED, T1032_NOTE_1_LINE_17}),
        frozenset({T1032_NOTE_1_LINE_29}),
    ),
    (
        Subtract,
        frozenset({T1032_NOTE_1_LINE_22, T1032_NOTE_1_LINE_29}),
        frozenset({T1032_NOTE_1_LINE_30}),
    ),
    (
        LesserOf,
        frozenset({T1032_NOTE_1_LINE_22, T1032_NOTE_1_LINE_30}),
        frozenset({T1032_NOTE_1_LINE_33}),
    ),
    (
        ChooseByCount,
        frozenset({T1032_NOTE_1_RECALCULATION, T1032_LINE_30, T1032_NOTE_1_LINE_33}),
        frozenset({T1032_LINE_33}),
    ),
}

NOTE_1_CHECK_WIRING = {
    (
        TimesCount,
        frozenset({T1032_NOTE_1_PAYMENTS_TOTAL, T1032_NOTE_1_APPLIES}),
        frozenset({T1032_NOTE_1_PAYMENTS_TOTAL_IF_APPLIES}),
    ),
    (
        TimesCount,
        frozenset({T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH, T1032_NOTE_1_APPLIES}),
        frozenset({T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_IF_APPLIES}),
    ),
    (
        CountByConditions,
        frozenset({T1032_NOTE_1_LINE_22}),
        frozenset({T1032_NOTE_1_LINE_29_APPLIES}),
    ),
    (
        TimesCount,
        frozenset({T1032_LINE_8, T1032_NOTE_1_LINE_29_APPLIES}),
        frozenset({T1032_NOTE_1_LINE_8_TO_CHECK}),
    ),
    (
        CountByConditions,
        frozenset({T1032_NOTE_1_LINE_17}),
        frozenset({T1032_NOTE_1_LINE_17_IS_ZERO}),
    ),
    (
        ChooseByCount,
        frozenset(
            {T1032_NOTE_1_LINE_17_IS_ZERO, T1032_NOTE_1_LINE_8_TO_CHECK, T1032_NOTE_1_LINE_17}
        ),
        frozenset({T1032_NOTE_1_LINE_8_BOUND}),
    ),
    (
        AtMost,
        frozenset({T1032_NOTE_1_LINE_8_TO_CHECK, T1032_NOTE_1_LINE_8_BOUND}),
        frozenset({T1032_NOTE_1_LINE_8_CHECKED}),
    ),
}

LINE_31_WIRING = {
    (
        Subtract,
        frozenset({T1032_ELIGIBLE_PENSION_INCOME, T1032_NOTE_1_LINE_30}),
        frozenset({T1032_NOTE_1_LINE_31}),
    ),
    (
        ChooseByCount,
        frozenset({T1032_NOTE_1_RECALCULATION, T1032_LINE_31, T1032_NOTE_1_LINE_31}),
        frozenset({T1032_LINE_31_AFTER_NOTE_1}),
    ),
}
