"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.contribution_tier import TieredContribution
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.greater_of import GreaterOf
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    BUSINESS_INCOME_NOT_BELOW_ZERO,
    CANADA_TRAINING_CREDIT,
    CANADA_WORKERS_BENEFIT,
    COMMISSION_INCOME,
    COMMISSION_INCOME_NOT_BELOW_ZERO,
    CPP_OR_QPP_BENEFITS,
    CPP_OVERPAYMENT,
    EDUCATOR_SCHOOL_SUPPLY_CREDIT,
    EI_AND_OTHER_BENEFITS,
    EI_OVERPAYMENT,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    EI_PREMIUMS,
    ELECTED_SPLIT_PENSION_AMOUNT,
    EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
    EMPLOYMENT_INCOME,
    FARMING_INCOME,
    FARMING_INCOME_NOT_BELOW_ZERO,
    FHSA_INCOME,
    FISHING_INCOME,
    FISHING_INCOME_NOT_BELOW_ZERO,
    FUEL_CHARGE_CREDIT_FARMERS_TOTAL,
    INCOME_BEFORE_LOSSES,
    INCOME_SUPPORT_BENEFITS,
    INCOME_TAX_DEDUCTED_AFTER_ELECTION,
    INTEREST_AND_OTHER_INVESTMENT_INCOME,
    INVESTMENT_TAX_CREDIT_REFUND,
    JOURNALISM_LABOUR_TAX_CREDIT,
    MULTIGENERATIONAL_HOME_RENOVATION_CREDIT,
    NET_PARTNERSHIP_INCOME,
    NET_RENTAL_INCOME,
    NET_RENTAL_INCOME_NOT_BELOW_ZERO,
    OLD_AGE_SECURITY,
    OTHER_EMPLOYMENT_INCOME,
    OTHER_FHSA_INCOME,
    OTHER_INCOME,
    OTHER_PENSIONS_AND_SUPERANNUATION,
    PART_XII_2_TAX_CREDIT,
    PROFESSIONAL_INCOME,
    PROFESSIONAL_INCOME_NOT_BELOW_ZERO,
    PROVINCIAL_CREDITS,
    RDSP_INCOME,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    RRSP_INCOME,
    T2204_EXEMPTION,
    T2204_INSURABLE_EARNINGS,
    T2204_LINE_1,
    T2204_LINE_1_COUNT,
    T2204_LINE_1_PLUS_2,
    T2204_LINE_3,
    T2204_LINE_6,
    T2204_LINE_7,
    T2204_LINE_8,
    T2204_LINE_9,
    T2204_LINE_10,
    T2204_LINE_12,
    T2204_LINE_13,
    T2204_LINE_14,
    T2204_LINE_15,
    T2204_LINE_15_COUNT,
    T2204_LINE_16,
    T2204_PPIP_PREMIUMS,
    T2204_PPIP_PREMIUMS_CHECKED,
    T2204_PREMIUMS_DEDUCTED,
    T2204_SELF_EMPLOYMENT_EARNINGS,
    T2205_ON_LINE_11500,
    T2205_ON_LINE_12900,
    T2205_ON_LINE_13000,
    TAX_PAID_BY_INSTALMENTS,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_DIVIDENDS,
    TAXABLE_SCHOLARSHIPS,
    TAXABLE_SUPPORT_PAYMENTS,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
    UNIVERSAL_CHILD_CARE_BENEFIT,
)

INPUTS = frozenset(
    {
        "ca/t2204_insurable_earnings",
        "ca/t2204_self_employment_earnings",
        "ca/t2204_premiums_deducted",
        "ca/t2204_ppip_premiums",
    }
)

# The box 55 check is read by nothing on the return: it is run and its amount refused above line 4,
# so the checked kind is a declared output.
OUTPUTS = frozenset(
    {
        "ca/refund_or_balance_owing",
        "ca/t2204_ppip_premiums_checked",
    }
)

STEPS = {
    # T2204 line 1 "Total EI insurable earnings (box 24 or, if blank, box 14 of your T4 slips) (1)",
    # with note (1) "If you have no self-employment earnings and your total EI insurable earnings
    # on your T4 slips are less than $2,000, enter "0"." The count is 0 when the note applies and
    # 1 otherwise, so line 1 is the insurable earnings times the count. The Quebec variant of
    # line 11 is not modelled.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t2204_line_1_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/t2204_self_employment_earnings",
                "ca/t2204_exemption",
                "ca/t2204_insurable_earnings",
            ),
        },
        produces={"output": "ca/t2204_line_1_count"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t2204_insurable_earnings",
            "count": "ca/t2204_line_1_count",
        },
        produces={"output": "ca/t2204_line_1"},
    ),
    # T2204 line 3 "Line 1 plus line 2 (maximum $65,700)": the sum, then the maximum insurable
    # earnings of the dataset.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t2204_line_1", "ca/t2204_self_employment_earnings")},
        produces={"output": "ca/t2204_line_1_plus_2"},
    ),
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/t2204_maximum_insurable_earnings"},
        consumes={"base": "ca/t2204_line_1_plus_2"},
        produces={"output": "ca/t2204_line_3"},
    ),
    # T2204 line 7 "Amount from line 3 – $2,000 = (if negative, enter "0")": the $2,000 is a
    # dataset, claimed whole, and the line is not below zero.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t2204_exemption"},
        consumes={},
        produces={"output": "ca/t2204_exemption"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/t2204_line_3", "less": "ca/t2204_exemption"},
        produces={"output": "ca/t2204_line_7"},
    ),
    # Form T2204 line 4 "Total premiums deducted" is taken as typed: the form prints no limit on it,
    # so it is not checked against the rate times the insurable earnings.
    # The box 55 premiums are a part of line 4, so they are at most line 4.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t2204_ppip_premiums",
            "bound": "ca/t2204_premiums_deducted",
        },
        produces={"output": "ca/t2204_ppip_premiums_checked"},
    ),
    # T2204 line 6 "Line 4 plus line 5", where line 4 is the premiums deducted, as typed, and line 5
    # is Schedule 13 line 9 for each agreement (`ca/ei_payable_on_self_employment`).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t2204_premiums_deducted", "ca/ei_payable_on_self_employment")},
        produces={"output": "ca/t2204_line_6"},
    ),
    # T2204 line 8 "Line 6 minus line 7 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/t2204_line_6", "less": "ca/t2204_line_7"},
        produces={"output": "ca/t2204_line_8"},
    ),
    # T2204 line 9 "Total premiums deducted from line 4 above": line 4, as typed, carried over one
    # part.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t2204_premiums_deducted",)},
        produces={"output": "ca/t2204_line_9"},
    ),
    # T2204 line 10 "Residents of other than Quebec Amount from line 1 × 1.64% = (maximum
    # $1,077.48)": the EI premium tier, on line 1 (not line 3).
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/ei_premium"},
        consumes={"earnings": "ca/t2204_line_1"},
        produces={"output": "ca/t2204_line_10"},
    ),
    # T2204 line 12 "Enter the amount from line 10 or line 11, whichever applies.": line 10, line
    # 11 being the Quebec variant.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t2204_line_10",)},
        produces={"output": "ca/t2204_line_12"},
    ),
    # T2204 line 13 "Line 9 minus line 12 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/t2204_line_9", "less": "ca/t2204_line_12"},
        produces={"output": "ca/t2204_line_13"},
    ),
    # T2204 line 14 "Enter whichever is more: amount from line 8 or line 13.", and line 15 "Enter
    # whichever is less: amount from line 9 or line 14."
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={"amounts": ("ca/t2204_line_8", "ca/t2204_line_13")},
        produces={"output": "ca/t2204_line_14"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t2204_line_9", "ca/t2204_line_14")},
        produces={"output": "ca/t2204_line_15"},
    ),
    # T1 line 153 and line 45000 "Employment insurance (EI) overpayment": T2204 line 15 "If this
    # amount is more than $1, enter it on line 45000 of your return." The count is 1 when line
    # 15 is more than $1 and 0 otherwise.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t2204_line_15_conditions"},
        consumes={"counts": (), "amounts": ("ca/t2204_line_15",)},
        produces={"output": "ca/t2204_line_15_count"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t2204_line_15", "count": "ca/t2204_line_15_count"},
        produces={"output": "ca/ei_overpayment"},
    ),
    # T2204 line 16 "Enter whichever amount is the least: line 7, line 9 or line 12."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t2204_line_7", "ca/t2204_line_9", "ca/t2204_line_12")},
        produces={"output": "ca/t2204_line_16"},
    ),
    # T2204 line 16 "Enter this amount on line 31200 of your return": T1 line 31200 "through
    # employment (boxes 18 and 55 of all T4 slips) (maximum $1,077.48)" is that amount, carried
    # over one part.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t2204_line_16",)},
        produces={"output": "ca/ei_premiums"},
    ),
    # The bound of Form T1206 line 3 is the income before losses (14a_income_before_losses.yaml):
    # the T1 income lines of Step 2 as in total income, each line that can be a loss counted as 0
    # when it is one. The form prints no limit on it, so the bound is a choice, not a form rule.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/net_rental_income",)},
        produces={"output": "ca/net_rental_income_not_below_zero"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/business_income",)},
        produces={"output": "ca/business_income_not_below_zero"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/professional_income",)},
        produces={"output": "ca/professional_income_not_below_zero"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/commission_income",)},
        produces={"output": "ca/commission_income_not_below_zero"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/farming_income",)},
        produces={"output": "ca/farming_income_not_below_zero"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/fishing_income",)},
        produces={"output": "ca/fishing_income_not_below_zero"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/employment_income",
                "ca/other_employment_income",
                "ca/old_age_security",
                "ca/cpp_or_qpp_benefits",
                "ca/other_pensions_and_superannuation",
                "ca/t2205_on_line_11500",
                "ca/elected_split_pension_amount",
                "ca/universal_child_care_benefit",
                "ca/ei_and_other_benefits",
                "ca/taxable_dividends",
                "ca/interest_and_other_investment_income",
                "ca/net_partnership_income",
                "ca/rdsp_income",
                "ca/net_rental_income_not_below_zero",
                "ca/taxable_capital_gains",
                "ca/taxable_support_payments",
                "ca/rrsp_income",
                "ca/t2205_on_line_12900",
                "ca/fhsa_income",
                "ca/other_fhsa_income",
                "ca/other_income",
                "ca/t2205_on_line_13000",
                "ca/taxable_scholarships",
                "ca/business_income_not_below_zero",
                "ca/professional_income_not_below_zero",
                "ca/commission_income_not_below_zero",
                "ca/farming_income_not_below_zero",
                "ca/fishing_income_not_below_zero",
                "ca/income_support_benefits",
            )
        },
        produces={"output": "ca/income_before_losses"},
    ),
    # T1 line 166 (line 48200) "Add lines 150 to 165. Total credits": line 150 (43700), line 152
    # (44800) "CPP or QPP overpayment" (Schedule 8 line 29, 0 when line 24 is not positive), line
    # 153 (45000) "Employment insurance (EI) overpayment" (T2204 line 15 when it is more than $1),
    # line 154 (45200) "Refundable medical expense supplement (use Federal Worksheet)", line 155
    # (45300) "Canada workers benefit (CWB) (complete Schedule 6)", line 156 (45350) "Canada
    # training credit (CTC) (complete Schedule 11)", line 157 (45355) "Multigenerational home
    # renovation tax credit (MHRTC) (complete Schedule 12)", line 158 (45400) "Refund of investment
    # tax credit (complete Form T2038(IND))", line 159 (45600) "Part XII.2 tax credit (box 38 of all
    # T3 slips and box 209 of all T5013 slips)", line 160 (45700) "Employee and partner GST/HST
    # rebate (complete Form GST370)", line 161 (46900), line 162 (47555) "Canadian journalism labour
    # tax credit (box 236 of all T5013 slips)", line 164 (47600) "Tax paid by instalments" and line
    # 165 (47900), in line order; line 151 (44000, a Quebec abatement that does not apply
    # to an Ontario return) is left out.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/income_tax_deducted_after_election",
                "ca/cpp_overpayment",
                "ca/ei_overpayment",
                "ca/refundable_medical_expense_supplement",
                "ca/canada_workers_benefit",
                "ca/canada_training_credit",
                "ca/multigenerational_home_renovation_credit",
                "ca/investment_tax_credit_refund",
                "ca/part_xii_2_tax_credit",
                "ca/employee_and_partner_gst_hst_rebate",
                "ca/educator_school_supply_credit",
                "ca/journalism_labour_tax_credit",
                "ca/fuel_charge_credit_farmers_total",
                "ca/tax_paid_by_instalments",
                "ca/provincial_credits",
            )
        },
        produces={"output": "ca/total_credits"},
    ),
    # T1 line 167 "Line 149 minus line 166 If the amount is negative, enter it on line
    # 48400 below. If the amount is positive, enter it on line 48500 below. Refund or
    # balance owing": not floored, so a negative result is a refund and a positive one a
    # balance owing.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/total_payable", "less": "ca/total_credits"},
        produces={"output": "ca/refund_or_balance_owing"},
    ),
    # T1 line 48400 "Refund": line 167 is entered on line 48400 "If the amount is negative", so
    # the total credits less the total payable, not below zero, a refund and never a negative.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/total_credits", "less": "ca/total_payable"},
        produces={"output": "ca/refund"},
    ),
}

WIRING = {
    (
        SumNotBelowZero,
        frozenset({NET_RENTAL_INCOME}),
        frozenset({NET_RENTAL_INCOME_NOT_BELOW_ZERO}),
    ),
    (SumNotBelowZero, frozenset({BUSINESS_INCOME}), frozenset({BUSINESS_INCOME_NOT_BELOW_ZERO})),
    (
        SumNotBelowZero,
        frozenset({PROFESSIONAL_INCOME}),
        frozenset({PROFESSIONAL_INCOME_NOT_BELOW_ZERO}),
    ),
    (
        SumNotBelowZero,
        frozenset({COMMISSION_INCOME}),
        frozenset({COMMISSION_INCOME_NOT_BELOW_ZERO}),
    ),
    (SumNotBelowZero, frozenset({FARMING_INCOME}), frozenset({FARMING_INCOME_NOT_BELOW_ZERO})),
    (SumNotBelowZero, frozenset({FISHING_INCOME}), frozenset({FISHING_INCOME_NOT_BELOW_ZERO})),
    (
        Sum,
        frozenset(
            {
                EMPLOYMENT_INCOME,
                OTHER_EMPLOYMENT_INCOME,
                OLD_AGE_SECURITY,
                CPP_OR_QPP_BENEFITS,
                OTHER_PENSIONS_AND_SUPERANNUATION,
                T2205_ON_LINE_11500,
                ELECTED_SPLIT_PENSION_AMOUNT,
                UNIVERSAL_CHILD_CARE_BENEFIT,
                EI_AND_OTHER_BENEFITS,
                TAXABLE_DIVIDENDS,
                INTEREST_AND_OTHER_INVESTMENT_INCOME,
                NET_PARTNERSHIP_INCOME,
                RDSP_INCOME,
                NET_RENTAL_INCOME_NOT_BELOW_ZERO,
                TAXABLE_CAPITAL_GAINS,
                TAXABLE_SUPPORT_PAYMENTS,
                RRSP_INCOME,
                T2205_ON_LINE_12900,
                FHSA_INCOME,
                OTHER_FHSA_INCOME,
                OTHER_INCOME,
                T2205_ON_LINE_13000,
                TAXABLE_SCHOLARSHIPS,
                BUSINESS_INCOME_NOT_BELOW_ZERO,
                PROFESSIONAL_INCOME_NOT_BELOW_ZERO,
                COMMISSION_INCOME_NOT_BELOW_ZERO,
                FARMING_INCOME_NOT_BELOW_ZERO,
                FISHING_INCOME_NOT_BELOW_ZERO,
                INCOME_SUPPORT_BENEFITS,
            }
        ),
        frozenset({INCOME_BEFORE_LOSSES}),
    ),
    (
        Sum,
        frozenset(
            {
                INCOME_TAX_DEDUCTED_AFTER_ELECTION,
                CPP_OVERPAYMENT,
                EI_OVERPAYMENT,
                REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
                CANADA_WORKERS_BENEFIT,
                CANADA_TRAINING_CREDIT,
                MULTIGENERATIONAL_HOME_RENOVATION_CREDIT,
                INVESTMENT_TAX_CREDIT_REFUND,
                PART_XII_2_TAX_CREDIT,
                EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
                EDUCATOR_SCHOOL_SUPPLY_CREDIT,
                JOURNALISM_LABOUR_TAX_CREDIT,
                FUEL_CHARGE_CREDIT_FARMERS_TOTAL,
                TAX_PAID_BY_INSTALMENTS,
                PROVINCIAL_CREDITS,
            }
        ),
        frozenset({TOTAL_CREDITS}),
    ),
    (
        Subtract,
        frozenset({TOTAL_PAYABLE, TOTAL_CREDITS}),
        frozenset({REFUND_OR_BALANCE_OWING}),
    ),
    (SubtractNotBelowZero, frozenset({TOTAL_CREDITS, TOTAL_PAYABLE}), frozenset({REFUND})),
    (
        CountByConditions,
        frozenset({T2204_SELF_EMPLOYMENT_EARNINGS, T2204_EXEMPTION, T2204_INSURABLE_EARNINGS}),
        frozenset({T2204_LINE_1_COUNT}),
    ),
    (
        TimesCount,
        frozenset({T2204_INSURABLE_EARNINGS, T2204_LINE_1_COUNT}),
        frozenset({T2204_LINE_1}),
    ),
    (
        Sum,
        frozenset({T2204_LINE_1, T2204_SELF_EMPLOYMENT_EARNINGS}),
        frozenset({T2204_LINE_1_PLUS_2}),
    ),
    (CappedAmount, frozenset({T2204_LINE_1_PLUS_2}), frozenset({T2204_LINE_3})),
    (CreditAmount, frozenset(), frozenset({T2204_EXEMPTION})),
    (
        SubtractNotBelowZero,
        frozenset({T2204_LINE_3, T2204_EXEMPTION}),
        frozenset({T2204_LINE_7}),
    ),
    (
        AtMost,
        frozenset({T2204_PPIP_PREMIUMS, T2204_PREMIUMS_DEDUCTED}),
        frozenset({T2204_PPIP_PREMIUMS_CHECKED}),
    ),
    (
        Sum,
        frozenset({T2204_PREMIUMS_DEDUCTED, EI_PAYABLE_ON_SELF_EMPLOYMENT}),
        frozenset({T2204_LINE_6}),
    ),
    (SubtractNotBelowZero, frozenset({T2204_LINE_6, T2204_LINE_7}), frozenset({T2204_LINE_8})),
    (Sum, frozenset({T2204_PREMIUMS_DEDUCTED}), frozenset({T2204_LINE_9})),
    (TieredContribution, frozenset({T2204_LINE_1}), frozenset({T2204_LINE_10})),
    (Sum, frozenset({T2204_LINE_10}), frozenset({T2204_LINE_12})),
    (SubtractNotBelowZero, frozenset({T2204_LINE_9, T2204_LINE_12}), frozenset({T2204_LINE_13})),
    (GreaterOf, frozenset({T2204_LINE_8, T2204_LINE_13}), frozenset({T2204_LINE_14})),
    (LesserOf, frozenset({T2204_LINE_9, T2204_LINE_14}), frozenset({T2204_LINE_15})),
    (CountByConditions, frozenset({T2204_LINE_15}), frozenset({T2204_LINE_15_COUNT})),
    (
        TimesCount,
        frozenset({T2204_LINE_15, T2204_LINE_15_COUNT}),
        frozenset({EI_OVERPAYMENT}),
    ),
    (
        LesserOf,
        frozenset({T2204_LINE_7, T2204_LINE_9, T2204_LINE_12}),
        frozenset({T2204_LINE_16}),
    ),
    (Sum, frozenset({T2204_LINE_16}), frozenset({EI_PREMIUMS})),
}
