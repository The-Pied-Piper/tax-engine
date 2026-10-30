"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.threshold_gate import ThresholdGate
from tax_engine.jurisdictions.ca.catalog import (
    AGED_18_OR_OLDER_AT_END_OF_2025_CHECKED,
    CLERGY_RESIDENCE_DEDUCTION,
    DISABILITY_SUPPORTS_DEDUCTION,
    EDUCATOR_SCHOOL_SUPPLY_CREDIT,
    EDUCATOR_SUPPLIES_EXPENSES,
    EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM,
    EMPLOYMENT_INCOME,
    MEDICAL_CLAIM,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME,
    MEDICAL_SUPPLEMENT_IF_RESIDENT,
    MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET,
    MEDICAL_SUPPLEMENT_INCOME_THRESHOLD,
    MEDICAL_SUPPLEMENT_LINE_6,
    MEDICAL_SUPPLEMENT_LINE_8,
    MEDICAL_SUPPLEMENT_LINE_11,
    MEDICAL_SUPPLEMENT_LINE_13,
    MEDICAL_SUPPLEMENT_LINE_14,
    MEDICAL_SUPPLEMENT_LINE_15,
    MEDICAL_SUPPLEMENT_LINE_16,
    MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_WORKING_INCOME,
    NET_BUSINESS_INCOME,
    NET_COMMISSION_INCOME,
    NET_FARMING_INCOME,
    NET_FISHING_INCOME,
    NET_PROFESSIONAL_INCOME,
    OTHER_EMPLOYMENT_EXPENSES,
    OTHER_EMPLOYMENT_INCOME,
    PROVINCIAL_CREDITS,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    RESIDENT_IN_CANADA_THROUGHOUT_2025_CHECKED,
    RPP_DEDUCTION,
    SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
    SPOUSE_RDSP_INCOME,
    SPOUSE_RDSP_INCOME_REPAYMENT,
    SPOUSE_UCCB_REPAYMENT,
    SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT,
    TOSI_ADJUSTED_NET_INCOME,
    UCCB_AND_RDSP_INCOME,
    UCCB_AND_RDSP_INCOME_REPAYMENTS,
    UNION_DUES,
    WAGE_LOSS_REPLACEMENT_PLAN_INCOME,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_CREDITS
from tests.jurisdictions.ca_on.manifest_families.t1139 import (
    BUSINESS_PROFIT_ON_RETURN_LINES,
    COMMISSION_PROFIT_ON_RETURN_LINES,
    FARMING_PROFIT_ON_RETURN_LINES,
    FISHING_PROFIT_ON_RETURN_LINES,
    PROFESSIONAL_PROFIT_ON_RETURN_LINES,
)

INPUTS = frozenset(
    {
        "ca/part_xii_2_tax_credit",
        "ca/employee_and_partner_gst_hst_rebate",
        "ca/educator_supplies_expenses",
        "ca/tax_paid_by_instalments",
    }
)

OUTPUTS = frozenset[str]()

STEPS = {
    # T1 line 165 and line 47900 "Provincial or territorial credits (complete Form 479, if it
    # applies)": ON479 line 21, the Ontario credits.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/ontario_credits",)},
        produces={"output": "ca/provincial_credits"},
    ),
    # T1 "Eligible educator school supply tax credit" line 161 and line 46900: "Supplies
    # expenses (maximum $1,000) Line 46800 multiplied by 25% =": the "(maximum $1,000)" is
    # printed before the percentage, so it caps the supplies expenses (line 46800).
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/educator_supplies_maximum"},
        consumes={"base": "ca/educator_supplies_expenses"},
        produces={"output": "ca/educator_supplies_expenses_at_most_maximum"},
    ),
    # Line 161's "multiplied by 25% =", on the capped supplies expenses.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/educator_supplies_rate"},
        consumes={"base": "ca/educator_supplies_expenses_at_most_maximum"},
        produces={"output": "ca/educator_school_supply_credit"},
    ),
    # T1 line 154 and line 45200 "Refundable medical expense supplement (use Federal
    # Worksheet)"; Federal Worksheet "Line 45200 - Refundable medical expense supplement", one
    # step per printed line, then the conditions it states. The T1 lines it reads that are not
    # yet computed are caller inputs under their line names: 22900, 23100, and the professional
    # and commission income of lines 13700 and 13900. The self-employment lines 13500, 13700,
    # 13900, 14100 and 14300 are the profits only, as the worksheet's note asks, computed from the
    # T2125, T2042 and T2121 statements and those two inputs. "In addition, the total of the
    # following two amounts must be $4,390 or more:" "your employment income from lines 10100 and
    # 10400 of your return (other than
    # amounts received from a wage-loss replacement plan) minus the amounts from lines 20700,
    # 21200, 22900, and 23100 of your return (if the result is negative, consider it as "0")":
    # lines 10100 and 10400.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/employment_income", "ca/other_employment_income")},
        produces={"output": "ca/medical_supplement_employment_income"},
    ),
    # "(other than amounts received from a wage-loss replacement plan)": a caller input, which
    # lines 10100 and 10400 include.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/medical_supplement_employment_income",
            "less": "ca/wage_loss_replacement_plan_income",
        },
        produces={"output": "ca/medical_supplement_employment_income_less_wage_loss"},
    ),
    # "minus the amounts from lines 20700, 21200, 22900, and 23100 of your return", in line
    # order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rpp_deduction",
                "ca/union_dues",
                "ca/other_employment_expenses",
                "ca/clergy_residence_deduction",
            ),
        },
        produces={"output": "ca/medical_supplement_employment_deductions"},
    ),
    # "(if the result is negative, consider it as "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/medical_supplement_employment_income_less_wage_loss",
            "less": "ca/medical_supplement_employment_deductions",
        },
        produces={"output": "ca/medical_supplement_employment_working_income"},
    ),
    # "your net self-employment income (not including losses) from lines 13500, 13700, 13900,
    # 14100, and 14300 of your return": the positive net income of each Form T2125 statement,
    # added, so a loss counts 0 (line 13500). The note's "use only the profit amounts" and "If you
    # are reporting a loss from only one business on one of these lines, do not include that loss"
    # is that rule.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_business_profit_on_return"},
        produces={"output": "ca/net_business_income"},
    ),
    # The same rule for professional income (line 13700), not below zero, so a loss counts 0.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_professional_profit_on_return"},
        produces={"output": "ca/net_professional_income"},
    ),
    # The same rule for commission income (line 13900), not below zero, so a loss counts 0.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_commission_profit_on_return"},
        produces={"output": "ca/net_commission_income"},
    ),
    # The same rule for the statements of Form T2042 (farming, line 14100): a loss counts 0.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_farming_profit_on_return"},
        produces={"output": "ca/net_farming_income"},
    ),
    # The same rule for the statements of Form T2121 (fishing, line 14300): a loss counts 0.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_fishing_profit_on_return"},
        produces={"output": "ca/net_fishing_income"},
    ),
    # "your net self-employment income (not including losses) from lines 13500, 13700, 13900,
    # 14100, and 14300 of your return", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/net_business_income",
                "ca/net_professional_income",
                "ca/net_commission_income",
                "ca/net_farming_income",
                "ca/net_fishing_income",
            ),
        },
        produces={"output": "ca/medical_supplement_self_employment_income"},
    ),
    # "the total of the following two amounts".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/medical_supplement_employment_working_income",
                "ca/medical_supplement_self_employment_income",
            ),
        },
        produces={"output": "ca/medical_supplement_working_income"},
    ),
    # Column 1 "You" line 1 "Net income amount from line 23600 of the return (or the amount you
    # would have entered if the instructions on line 23600 said "if negative, show in brackets")" is
    # the TOSI-adjusted net income of Form T1206 Part 1 line 6, signed ("use line 6 of this form at
    # line 1 of column 1 of your Federal Worksheet for line 45200"), whose line 5 is line 23400
    # less line 23500, signed (`ca/net_income_signed`); line 2 "Total of the universal
    # child care benefit (UCCB) repayment (line 21300 of the return) and the registered disability
    # savings plan (RDSP) income repayment (included in the amount on line 23200 of the return)" is
    # the UCCB and RDSP income repayments of the other payments worksheet; line 3 "Line 1 plus line
    # 2".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/tosi_adjusted_net_income",
                "ca/uccb_and_rdsp_income_repayments",
            ),
        },
        produces={"output": "ca/medical_supplement_column_1_line_3"},
    ),
    # Column 1 line 4 "Total of the UCCB income (line 11700 of the return) and the RDSP income
    # (line 12500 of the return)" is the UCCB and RDSP income of the other payments worksheet;
    # line 5 "Line 3 minus line 4 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/medical_supplement_column_1_line_3",
            "less": "ca/uccb_and_rdsp_income",
        },
        produces={"output": "ca/medical_supplement_column_1_line_5"},
    ),
    # Column 2 "Your spouse or common-law partner" line 2, line 3 "Line 1 plus line 2", line 4
    # and line 5, the same lines for the spouse's caller inputs: 0 when there is no spouse or
    # common-law partner, and when "you were separated because of a breakdown in your
    # relationship for a period of 90 days or more that included December 31, 2025" or "your
    # spouse or common-law partner died on or before December 31, 2025", as the worksheet says
    # "do not include their income".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/spouse_uccb_repayment", "ca/spouse_rdsp_income_repayment")},
        produces={"output": "ca/medical_supplement_column_2_line_2"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/spouse_net_income_before_adjustments",
                "ca/medical_supplement_column_2_line_2",
            ),
        },
        produces={"output": "ca/medical_supplement_column_2_line_3"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/spouse_universal_child_care_benefit", "ca/spouse_rdsp_income")},
        produces={"output": "ca/medical_supplement_column_2_line_4"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/medical_supplement_column_2_line_3",
            "less": "ca/medical_supplement_column_2_line_4",
        },
        produces={"output": "ca/medical_supplement_column_2_line_5"},
    ),
    # Line 6 "Add the amounts from line 5 of columns 1 and 2. Adjusted family net income".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/medical_supplement_column_1_line_5",
                "ca/medical_supplement_column_2_line_5",
            ),
        },
        produces={"output": "ca/medical_supplement_line_6"},
    ),
    # Line 7 "Income threshold 33,294.00", a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/medical_supplement_income_threshold"},
        consumes={},
        produces={"output": "ca/medical_supplement_income_threshold"},
    ),
    # Line 8 "Line 6 minus line 7 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/medical_supplement_line_6",
            "less": "ca/medical_supplement_income_threshold",
        },
        produces={"output": "ca/medical_supplement_line_8"},
    ),
    # Line 9 "Amount from line 21500 of your return" (the amount computed on Form T929 line 12)
    # and line 10 "Amount from line 33200 of your return" (the medical claim); line 11 "Line 9
    # plus line 10".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/disability_supports_deduction", "ca/medical_claim")},
        produces={"output": "ca/medical_supplement_line_11"},
    ),
    # Line 12 "Applicable rate 25%" and line 13 "Line 11 multiplied by the percentage from line
    # 12 =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/medical_supplement_rate"},
        consumes={"base": "ca/medical_supplement_line_11"},
        produces={"output": "ca/medical_supplement_line_13"},
    ),
    # Line 14 "Enter whichever is less: amount from line 13 or $1,504".
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/medical_supplement_maximum"},
        consumes={"base": "ca/medical_supplement_line_13"},
        produces={"output": "ca/medical_supplement_line_14"},
    ),
    # Line 15 "Amount from line 8" "multiplied by 5% =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/medical_supplement_reduction_rate"},
        consumes={"base": "ca/medical_supplement_line_8"},
        produces={"output": "ca/medical_supplement_line_15"},
    ),
    # Line 16 "Line 14 minus line 15 (if negative, enter "0") Enter this amount on line 45200 of
    # your return. =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/medical_supplement_line_14",
            "less": "ca/medical_supplement_line_15",
        },
        produces={"output": "ca/medical_supplement_line_16"},
    ),
    # "In addition, the total of the following two amounts must be $4,390 or more:": line 16
    # when the working income is at least the threshold, else 0.
    CapabilitySelection(
        name="ca/threshold_gate",
        params={"threshold": "ca/medical_supplement_working_income_threshold"},
        consumes={
            "amount": "ca/medical_supplement_line_16",
            "gate": "ca/medical_supplement_working_income",
        },
        produces={"output": "ca/medical_supplement_if_working_income_met"},
    ),
    # "You were resident in Canada throughout 2025", a count of 0 or 1.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/medical_supplement_if_working_income_met",
            "count": "ca/resident_in_canada_throughout_2025_checked",
        },
        produces={"output": "ca/medical_supplement_if_resident"},
    ),
    # "You were 18 years of age or older at the end of 2025", a count of 0 or 1: T1 line 154 and
    # line 45200.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/medical_supplement_if_resident",
            "count": "ca/aged_18_or_older_at_end_of_2025_checked",
        },
        produces={"output": "ca/refundable_medical_expense_supplement"},
    ),
}

WIRING = {
    (Sum, frozenset({ONTARIO_CREDITS}), frozenset({PROVINCIAL_CREDITS})),
    (
        CappedAmount,
        frozenset({EDUCATOR_SUPPLIES_EXPENSES}),
        frozenset({EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM}),
    ),
    (
        ApplyRate,
        frozenset({EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM}),
        frozenset({EDUCATOR_SCHOOL_SUPPLY_CREDIT}),
    ),
    (
        Sum,
        frozenset({EMPLOYMENT_INCOME, OTHER_EMPLOYMENT_INCOME}),
        frozenset({MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME}),
    ),
    (
        Subtract,
        frozenset({MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME, WAGE_LOSS_REPLACEMENT_PLAN_INCOME}),
        frozenset({MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS}),
    ),
    (
        Sum,
        frozenset(
            {
                RPP_DEDUCTION,
                UNION_DUES,
                OTHER_EMPLOYMENT_EXPENSES,
                CLERGY_RESIDENCE_DEDUCTION,
            }
        ),
        frozenset({MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS,
                MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
            }
        ),
        frozenset({MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({BUSINESS_PROFIT_ON_RETURN_LINES}),
        frozenset({NET_BUSINESS_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({PROFESSIONAL_PROFIT_ON_RETURN_LINES}),
        frozenset({NET_PROFESSIONAL_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({COMMISSION_PROFIT_ON_RETURN_LINES}),
        frozenset({NET_COMMISSION_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({FARMING_PROFIT_ON_RETURN_LINES}),
        frozenset({NET_FARMING_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({FISHING_PROFIT_ON_RETURN_LINES}),
        frozenset({NET_FISHING_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                NET_BUSINESS_INCOME,
                NET_PROFESSIONAL_INCOME,
                NET_COMMISSION_INCOME,
                NET_FARMING_INCOME,
                NET_FISHING_INCOME,
            }
        ),
        frozenset({MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME,
                MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
            }
        ),
        frozenset({MEDICAL_SUPPLEMENT_WORKING_INCOME}),
    ),
    (
        Sum,
        frozenset({TOSI_ADJUSTED_NET_INCOME, UCCB_AND_RDSP_INCOME_REPAYMENTS}),
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3, UCCB_AND_RDSP_INCOME}),
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5}),
    ),
    (
        Sum,
        frozenset({SPOUSE_UCCB_REPAYMENT, SPOUSE_RDSP_INCOME_REPAYMENT}),
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2}),
    ),
    (
        Sum,
        frozenset({SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS, MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2}),
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3}),
    ),
    (
        Sum,
        frozenset({SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT, SPOUSE_RDSP_INCOME}),
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3, MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4}),
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5}),
    ),
    (
        Sum,
        frozenset({MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5, MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5}),
        frozenset({MEDICAL_SUPPLEMENT_LINE_6}),
    ),
    (CreditAmount, frozenset(), frozenset({MEDICAL_SUPPLEMENT_INCOME_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({MEDICAL_SUPPLEMENT_LINE_6, MEDICAL_SUPPLEMENT_INCOME_THRESHOLD}),
        frozenset({MEDICAL_SUPPLEMENT_LINE_8}),
    ),
    (
        Sum,
        frozenset({DISABILITY_SUPPORTS_DEDUCTION, MEDICAL_CLAIM}),
        frozenset({MEDICAL_SUPPLEMENT_LINE_11}),
    ),
    (
        ApplyRate,
        frozenset({MEDICAL_SUPPLEMENT_LINE_11}),
        frozenset({MEDICAL_SUPPLEMENT_LINE_13}),
    ),
    (
        CappedAmount,
        frozenset({MEDICAL_SUPPLEMENT_LINE_13}),
        frozenset({MEDICAL_SUPPLEMENT_LINE_14}),
    ),
    (
        ApplyRate,
        frozenset({MEDICAL_SUPPLEMENT_LINE_8}),
        frozenset({MEDICAL_SUPPLEMENT_LINE_15}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({MEDICAL_SUPPLEMENT_LINE_14, MEDICAL_SUPPLEMENT_LINE_15}),
        frozenset({MEDICAL_SUPPLEMENT_LINE_16}),
    ),
    (
        ThresholdGate,
        frozenset({MEDICAL_SUPPLEMENT_LINE_16, MEDICAL_SUPPLEMENT_WORKING_INCOME}),
        frozenset({MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET}),
    ),
    (
        TimesCount,
        frozenset(
            {MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET, RESIDENT_IN_CANADA_THROUGHOUT_2025_CHECKED}
        ),
        frozenset({MEDICAL_SUPPLEMENT_IF_RESIDENT}),
    ),
    (
        TimesCount,
        frozenset({MEDICAL_SUPPLEMENT_IF_RESIDENT, AGED_18_OR_OLDER_AT_END_OF_2025_CHECKED}),
        frozenset({REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT}),
    ),
}
