"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.greater_of import GreaterOf
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.amount_or_divided_by_rate import (
    AmountOrDividedByRate,
)
from tax_engine.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.divided_by_rate import DividedByRate
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_4 import (
    ForeignBusinessTaxCreditLine4,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_5 import (
    ForeignBusinessTaxCreditLine5,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_7 import (
    ForeignBusinessTaxCreditLine7,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_8 import (
    ForeignBusinessTaxCreditLine8,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_10 import (
    ForeignBusinessTaxCreditLine10,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_11 import (
    ForeignBusinessTaxCreditLine11,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_non_business_tax_credit import (
    ForeignNonBusinessTaxCredit,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_property_tax_over_limit import (
    ForeignPropertyTaxOverLimit,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_surtax_allocated_total import (
    ForeignSurtaxAllocatedTotal,
)
from tax_engine.jurisdictions.ca.capabilities.lesser_of_when_positive import (
    LesserOfWhenPositive,
)
from tax_engine.jurisdictions.ca.capabilities.more_than_per_unit import MoreThanPerUnit
from tax_engine.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS_TOTAL,
    ADOPTION_CREDIT,
    ADOPTION_EXPENSE_CHILDREN,
    AGE_AMOUNT,
    AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    AMT_FEDERAL_SURTAX,
    AMT_SUBJECT_TO_MINIMUM_TAX,
    AMT_T2203_COLUMN_5_PERCENTAGE,
    AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED,
    AMT_T2203_COLUMN_5_PERCENTAGE_MAXIMUM,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX,
    BASIC_PERSONAL_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT_INCOME,
    CANADA_TRAINING_CREDIT,
    CANADA_TRAINING_CREDIT_BASIS,
    CANADA_TRAINING_CREDIT_CLAIMED,
    CANADA_TRAINING_CREDIT_LIMIT,
    CANADA_TRAINING_CREDIT_MAXIMUM,
    CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION,
    CANADIAN_TUITION_AVAILABLE,
    CANADIAN_TUITION_FEES,
    CANADIAN_TUITION_FEES_CHECKED,
    CANADIAN_TUITION_INSTITUTIONS,
    CAPITAL_GAINS_DEDUCTION,
    CAPITAL_GIFT_GAINS_DEDUCTION,
    CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED,
    CAPITAL_GIFT_TAXABLE_GAINS,
    CAPITAL_GIFTS_LIMIT_ADDITION,
    CAPITAL_GIFTS_TOTAL,
    CAPITAL_PROPERTY_GIFTS,
    CAREGIVER_AMOUNT,
    CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT,
    CHARITABLE_DONATIONS,
    CHARITABLE_DONATIONS_CLAIMED,
    CHARITABLE_DONATIONS_LIMIT,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_PART_4_COMPLETED_CHECKED,
    CPP_PART_5_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
    CPP_PART_5_COMPLETED_CHECKED,
    CPP_PART_5_LINE_70,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    CREDIT_AMOUNTS_SUBTOTAL,
    CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    CURRENT_YEAR_TUITION_AVAILABLE,
    CURRENT_YEAR_TUITION_CLAIMED,
    DEPRECIABLE_GIFT_CAPITAL_COST,
    DEPRECIABLE_GIFT_NET_PROCEEDS,
    DEPRECIABLE_GIFT_PROCEEDS_OR_COST,
    DEPRECIABLE_GIFT_RECAPTURED_DEPRECIATION,
    DEPRECIABLE_GIFTS,
    DISABILITY_AMOUNT_FOR_SELF,
    DISABILITY_TRANSFERRED_AMOUNT,
    DIVIDEND_TAX_CREDIT,
    DONATION_FIRST_TIER_MAXIMUM,
    DONATION_HIGH_INCOME_THRESHOLD,
    DONATION_LIMIT_ON_NET_INCOME,
    DONATION_LIMIT_WITH_CAPITAL_GIFTS,
    DONATIONS_AND_GIFTS_CREDIT,
    DONATIONS_AND_GIFTS_TOTAL,
    DONATIONS_FIRST_TIER,
    DONATIONS_OVER_FIRST_TIER,
    DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS,
    ECOLOGICAL_AND_CULTURAL_GIFTS,
    ECOLOGICAL_GIFTS_BEFORE_2016,
    EI_PREMIUMS,
    EI_PREMIUMS_ON_SELF_EMPLOYMENT,
    EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED,
    ELIGIBLE_DEPENDANT_AMOUNT,
    EMPLOYMENT_INCOME,
    EXEMPT_INCOME_DEDUCTIONS,
    EXEMPT_INCOME_DEDUCTIONS_CHECKED,
    FEDERAL_BASIC_TAX,
    FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
    FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_SURTAX_OUTSIDE_CANADA,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_ON_SPLIT_INCOME,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    FEDERAL_TAX_WITH_SPLIT_INCOME,
    FEDERAL_TAX_WITH_SURTAX,
    FEDERAL_TUITION_AMOUNT,
    FIRST_NATIONS_ABATEMENT,
    FIRST_TIER_DONATION_CREDIT,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_4,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_5,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_7,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_8,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_10,
    FOREIGN_CHARITY_DONATIONS,
    FOREIGN_PROPERTY_TAX_OVER_LIMIT,
    FOREIGN_SURTAX_ALLOCATED_TOTAL,
    FOREIGN_SURTAX_ALLOCATED_TOTAL_CHECKED,
    FOREIGN_SURTAX_LIMIT,
    FOREIGN_TAX_COUNTRIES,
    FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
    FOREIGN_TAX_CREDIT_NET_INCOME,
    FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME,
    FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS,
    FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME,
    FOREIGN_TAX_CREDIT_SHEETS,
    FOREIGN_TUITION_FEES,
    GOVERNMENT_DONATIONS,
    HIGH_INCOME_DONATION_CREDIT,
    HIGH_INCOME_DONATIONS,
    HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS,
    HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED,
    HOME_ACCESSIBILITY_CREDIT,
    HOME_ACCESSIBILITY_EXPENSES,
    HOME_ACCESSIBILITY_LINE_2,
    HOME_BUYERS_CLAIM,
    HOME_BUYERS_CREDIT,
    HOME_BUYERS_MAXIMUM,
    INFIRM_CHILDREN_AMOUNT,
    ITC_RECAPTURE,
    ITC_RECAPTURE_AT_15_PERCENT,
    ITC_RECAPTURE_AT_20_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT,
    MEDICAL_CLAIM,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    OTHER_EMPLOYMENT_INCOME,
    OTHER_PAYMENTS_DEDUCTION,
    OTHER_PENSIONS_AND_SUPERANNUATION,
    PENSION_ANNUITY_CONDITIONS_MET_CHECKED,
    PENSION_ANNUITY_PAYMENTS,
    PENSION_CHART_LINE_1,
    PENSION_CHART_LINE_5,
    PENSION_CHART_LINE_5_CHECKED,
    PENSION_CHART_LINE_6,
    PENSION_CHART_LINE_7,
    PENSION_CHART_LINE_8,
    PENSION_FOREIGN_INCOME,
    PENSION_FOREIGN_INCOME_CHECKED,
    PENSION_INCOME_CREDIT,
    PENSION_RRIF_TRANSFERRED,
    PENSION_US_IRA_INCOME,
    PENSION_WORKSHEET_AMOUNT,
    QBT_CAPITAL_GAINS_DEDUCTION,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    REGULAR_RATE_DONATION_CREDIT,
    REGULAR_RATE_DONATIONS,
    SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED,
    SEARCH_AND_RESCUE_CREDIT,
    SECURITY_OPTIONS_DEDUCTIONS,
    SELF_EMPLOYED_CPP_BASE_CREDIT,
    SELF_EMPLOYED_EI_PREMIUMS,
    SOCIAL_BENEFITS_REPAYMENT,
    SPLIT_INCOME_LINE_22,
    SPOUSE_ADJUSTED_TAXABLE_INCOME,
    SPOUSE_AMOUNT,
    SPOUSE_CREDITS_USED,
    SPOUSE_DESIGNATED_TUITION,
    SPOUSE_DESIGNATED_TUITION_CHECKED,
    SPOUSE_DESIGNATED_TUITION_MAXIMUM,
    SPOUSE_INCOME_FOR_TRANSFER,
    SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED,
    SPOUSE_RETURN_AGE_AMOUNT,
    SPOUSE_RETURN_AGE_AMOUNT_CHECKED,
    SPOUSE_RETURN_AGE_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT,
    SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED,
    SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_DISABILITY_AMOUNT,
    SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED,
    SPOUSE_RETURN_DISABILITY_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_FEDERAL_BASIC_TAX,
    SPOUSE_RETURN_FEDERAL_TUITION_AMOUNT,
    SPOUSE_RETURN_INFIRM_CHILDREN_AMOUNT,
    SPOUSE_RETURN_LINE_96,
    SPOUSE_RETURN_PENSION_INCOME_AMOUNT,
    SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED,
    SPOUSE_RETURN_PENSION_INCOME_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_TAXABLE_INCOME,
    SPOUSE_TRANSFERABLE_AMOUNTS,
    SPOUSE_UNUSED_AMOUNTS,
    STUDENT_LOAN_INTEREST,
    T2203_FEDERAL_SURTAX_OUTSIDE_CANADA,
    T2203_HAS_TAX_ON_SPLIT_INCOME,
    T2203_LINE_5,
    T2203_LINE_6,
    T2203_LINE_8,
    T2205_ON_LINE_11500,
    TAXABLE_INCOME,
    TAXABLE_INCOME_OVER_DONATION_THRESHOLD,
    TOP_UP_CREDITS_BASE,
    TOP_UP_EXCESS,
    TOP_UP_TAX_CREDIT,
    TOP_UP_THRESHOLD,
    TOSI_ADJUSTED_TAXABLE_INCOME,
    TOTAL_CHARITABLE_DONATIONS,
    TOTAL_SPLIT_INCOME,
    TOTAL_TUITION_AVAILABLE,
    TUITION_AVAILABLE_TO_TRANSFER,
    TUITION_CARRIED_FORWARD,
    TUITION_INCOME_BASE,
    TUITION_INCOME_LESS_CREDITS,
    TUITION_INCOME_REMAINING,
    TUITION_INCOME_WITH_TOSI,
    TUITION_TRANSFER_ELECTED,
    TUITION_TRANSFER_LIMIT,
    TUITION_TRANSFER_STUDENTS,
    TUITION_TRANSFERRED,
    TUITION_TRANSFERRED_FROM_CHILD,
    TUITION_TRANSFERRED_FROM_CHILD_CHECKED,
    TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM,
    UNIVERSITY_DONATIONS_OUTSIDE_CANADA,
    UNUSED_FEDERAL_TUITION,
    UNUSED_TUITION_CLAIMED,
    UNUSED_TUITION_FROM_2024,
    VOLUNTEER_AMOUNT_MAXIMUM,
    VOLUNTEER_CREDITS_CHECKED,
    VOLUNTEER_CREDITS_CLAIMED,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED,
    VOLUNTEER_FIREFIGHTERS_CREDIT,
)

INPUTS = frozenset(
    {
        # Form T2209, "the federal refundable First Nations abatement (line 44100 of your return)"
        # of note (4), and the countries of lines 1 and 2, each with lines 43100 and 43300.
        "ca/first_nations_abatement",
        "ca/foreign_tax_countries",
        # Form T2203 Part 1 line 52220 column 5, the percentage of Part 2 line 7 (and Form T691
        # Part 3 line 3), read by `core/at_most` against its maximum before the readers use it.
        "ca/amt_t2203_column_5_percentage",
        "ca/itc_recapture_expenditure_at_15_percent",
        "ca/itc_recapture_expenditure_at_20_percent",
        "ca/charitable_donations",
        "ca/government_donations",
        "ca/university_donations_outside_canada",
        "ca/foreign_charity_donations",
        "ca/ecological_and_cultural_gifts",
        "ca/ecological_gifts_before_2016",
        "ca/depreciable_gift_recaptured_depreciation",
        "ca/depreciable_gift_net_proceeds",
        "ca/depreciable_gift_capital_cost",
        "ca/capital_gift_taxable_gains",
        "ca/capital_gift_gains_deduction",
        "ca/ei_special_benefits_agreement",
        # Schedule 11 line 1 and line 32000 "(fees for each institution must be more than
        # $100)": the number of institutions the fees were paid to, read by `ca/more_than_per_unit`
        # (times $100).
        "ca/canadian_tuition_institutions",
        "ca/canadian_tuition_fees",
        "ca/canada_training_credit_limit",
        "ca/canada_training_credit_claimed",
        "ca/foreign_tuition_fees",
        "ca/unused_tuition_from_2024",
        "ca/tuition_transfer_elected",
        "ca/tuition_transferred_from_child",
        # 5000-G line 32400: the number of students the transfer comes from, read by the bound of
        # `core/per_unit_amount` (times $5,000) before `core/at_most` checks the transfer.
        "ca/tuition_transfer_students",
        "ca/spouse_return_age_amount",
        "ca/spouse_return_infirm_children_amount",
        "ca/spouse_return_pension_income_amount",
        "ca/spouse_return_disability_amount",
        "ca/spouse_designated_tuition",
        "ca/spouse_return_taxable_income",
        "ca/spouse_return_federal_basic_tax",
        "ca/spouse_return_basic_personal_amount",
        "ca/spouse_return_line_96",
        "ca/spouse_return_federal_tuition_amount",
        "ca/spouse_not_separated_90_days",
        # T1 lines 31220 and 31240, the caller's counts (1 when the conditions are met).
        "ca/volunteer_firefighters_conditions_met",
        "ca/search_and_rescue_conditions_met",
        # T1 line 31270 "Home buyers' amount", the claim, at most $10,000.
        "ca/home_buyers_claim",
        # Worksheet for line 31285, line 1 and line 3.
        "ca/home_accessibility_expenses",
        "ca/home_accessibility_claimed_by_others",
        # T1 line 31300, one record per eligible child.
        "ca/adoption_expense_children",
        # Worksheet for line 31400, lines 2 to 4 and line 7, and the 65-or-older gate.
        "ca/pension_foreign_income",
        "ca/pension_us_ira_income",
        "ca/pension_rrif_transferred",
        "ca/pension_annuity_payments",
        "ca/pension_annuity_conditions_met",
        # Worksheet for line 31400, last paragraph: the Form T1032 amount and the election.
        # T1 line 31900 "Interest paid on your student loans".
        "ca/student_loan_interest",
        # Schedule 11 line 32005 "Line 32005: Tick this box if you were eligible for the disability
        # tax credit in 2025 or had a mental or physical impairment in 2025 and a medical
        # practitioner has certified that you cannot reasonably be expected to be enrolled as a
        # full-time student because of the effects of your impairment.", line 32010 "Line 32010:
        # Number of months you were enrolled as a part-time student(box 24 of your Form T2202 and
        # column B of your forms TL11A and TL11C) (maximum 12)" and line 32020 "Line 32020: Number
        # of months you were enrolled as a full-time student (box 25 of your Form T2202 and column C
        # of your forms TL11A and TL11C) (maximum 12)": the form computes nothing from them, so each
        # is also an output.
        "ca/tuition_cannot_be_full_time_student",
        "ca/tuition_part_time_months",
        "ca/tuition_full_time_months",
    }
)

OUTPUTS = frozenset(
    {
        "ca/tuition_carried_forward",
        "ca/volunteer_credits_checked",
        "ca/foreign_property_tax_over_limit",
        "ca/foreign_surtax_allocated_total_checked",
        "ca/foreign_tax_credit_sheets",
        "ca/foreign_business_tax_credit_line_4",
        "ca/foreign_business_tax_credit_line_5",
        "ca/foreign_business_tax_credit_line_7",
        "ca/foreign_business_tax_credit_line_8",
        "ca/foreign_business_tax_credit_line_10",
        "ca/tuition_cannot_be_full_time_student",
        "ca/tuition_part_time_months",
        "ca/tuition_full_time_months",
    }
)

STEPS = {
    # T1 line 92 (line 31260) "Canada employment amount: Enter whichever is less: $1,471 or line 1
    # plus line 2.": line 1 "Employment income (box 14 of all T4 slips)" (line 10100) and line 2
    # "Other employment income" (line 10400), in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/employment_income", "ca/other_employment_income")},
        produces={"output": "ca/canada_employment_amount_income"},
    ),
    # The Canada employment amount: the lesser of the T1's cap and line 1 plus line 2.
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/canada_employment_amount"},
        consumes={"base": "ca/canada_employment_amount_income"},
        produces={"output": "ca/canada_employment_amount"},
    ),
    # T1 line 87 and line 31000, entered from Schedule 8 Part 4 line 15: Part 4 is completed only
    # when the filer reports self-employment income alone, so the amount is counted once for
    # each Part 4 completed, 1 or 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/self_employed_cpp_base_credit",
            "count": "ca/cpp_part_4_completed_checked",
        },
        produces={"output": "ca/cpp_base_contributions_on_self_employment"},
    ),
    # T1 line 87 and line 31000, entered from Schedule 8 Part 5 line 70: counted once for each
    # Part 5 completed, 1 or 0. The form prints line 70 as the amount for line 31000.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cpp_part_5_line_70",
            "count": "ca/cpp_part_5_completed_checked",
        },
        produces={"output": "ca/cpp_part_5_base_contributions_on_self_employment"},
    ),
    # T1 line 87 and line 31000: the Part 4 amount plus the Part 5 amount; both are added when
    # both parts are marked completed, as the form leaves the choice to the filer. Plus Form RC381
    # Part 4 line 111 (the form's total, 0 with no copy; the return carries Schedule 8 or Form
    # RC381, never both).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_base_contributions_on_self_employment",
                "ca/cpp_part_5_base_contributions_on_self_employment",
                "ca/rc381_cpp_base_contributions_on_self_employment_and_other_earnings",
            ),
        },
        produces={"output": "ca/cpp_base_contributions_on_self_employment_and_other_earnings"},
    ),
    # "Enter the amount from line 9 or line 10, whichever applies, on line 31217 and line 42120
    # of your return.": Schedule 13 is completed only with an agreement with the Canada
    # Employment Insurance Commission, so line 9 is counted once for each agreement, 1 or 0, on
    # each of the two lines.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/self_employed_ei_premiums",
            "count": "ca/ei_special_benefits_agreement_checked",
        },
        produces={"output": "ca/ei_premiums_on_self_employment"},
    ),
    # Schedule 11 line 1 and line 32000 "Eligible tuition fees paid to Canadian educational
    # institutions for 2025 (fees for each institution must be more than $100)": the form takes
    # one total, a caller input, and the institutions' count; the total must be more than the
    # count times $100 (the owner's decision), and the checked total is the one lines 2 to 8 read.
    CapabilitySelection(
        name="ca/more_than_per_unit",
        params={"amount": "ca/canadian_tuition_fee_minimum_per_institution"},
        consumes={
            "total": "ca/canadian_tuition_fees",
            "count": "ca/canadian_tuition_institutions",
        },
        produces={"output": "ca/canadian_tuition_fees_checked"},
    ),
    # Schedule 11 line 2 "Amount from line 1" "multiplied by 50% =": line 1 and line 32000 "Eligible
    # tuition fees paid to Canadian educational institutions for 2025" is a caller input.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/canada_training_credit_rate"},
        consumes={"base": "ca/canadian_tuition_fees_checked"},
        produces={"output": "ca/canada_training_credit_basis"},
    ),
    # Schedule 11 line 3 "Your Canada training credit limit from your latest notice of assessment
    # or reassessment", a caller input, and line 4 "Enter whichever is less: amount from line 2
    # or line 3."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/canada_training_credit_basis", "ca/canada_training_credit_limit")
        },
        produces={"output": "ca/canada_training_credit_maximum"},
    ),
    # Schedule 11 "Enter the Canada training credit amount that you are claiming for 2025 (cannot
    # be more than the amount on line 4)." and line 5 "Enter this amount on line 45350 of your
    # return. Your Canada training credit": the amount claimed is the filer's election, a caller
    # input, at most line 4; T1 line 156 and line 45350 "Canada training credit (CTC) (complete
    # Schedule 11)".
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/canada_training_credit_claimed",
            "bound": "ca/canada_training_credit_maximum",
        },
        produces={"output": "ca/canada_training_credit"},
    ),
    # Schedule 11 line 6 "Line 1 minus line 5 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/canadian_tuition_fees_checked",
            "less": "ca/canada_training_credit",
        },
        produces={"output": "ca/canadian_tuition_available"},
    ),
    # Schedule 11 line 7 and line 32001 "Eligible tuition fees paid to foreign educational
    # institutions for 2025", a caller input, and line 8 "Line 6 plus line 7 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/canadian_tuition_available", "ca/foreign_tuition_fees")},
        produces={"output": "ca/current_year_tuition_available"},
    ),
    # Schedule 11 line 9 "Unused federal tuition from your 2024 notice of assessment or
    # reassessment (note 1)", a caller input, and line 10 "Line 8 plus line 9 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/current_year_tuition_available", "ca/unused_tuition_from_2024")},
        produces={"output": "ca/total_tuition_available"},
    ),
    # Schedule 11 "Enter the amount from line 26000 of your return on line 11 if it is $57,375 or
    # less. If it is more than $57,375, enter the result of the following calculation:" and line
    # 11 "Amount from line 76 of your return divided by 14.5% =".
    CapabilitySelection(
        name="ca/amount_or_divided_by_rate",
        params={"limit": "ca/tuition_income_limit"},
        consumes={"amount": "ca/taxable_income", "dividend": "ca/federal_basic_tax"},
        produces={"output": "ca/tuition_income_base"},
    ),
    # T1 line 101 "Add lines 98 to 100. =": the credit amounts of the lines wired up to line 100
    # (line 31800), in the forms' line order, before line 102; Schedule 11 line 12 "Enter the
    # amount from line 101 of your return" reads it.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/basic_personal_amount",
                "ca/age_amount",
                "ca/spouse_amount",
                "ca/eligible_dependant_amount",
                "ca/caregiver_amount_for_spouse_or_dependant",
                "ca/caregiver_amount",
                "ca/infirm_children_amount",
                "ca/cpp_base_contributions_on_return",
                "ca/cpp_base_contributions_on_self_employment_and_other_earnings",
                "ca/ei_premiums",
                "ca/ei_premiums_on_self_employment",
                "ca/volunteer_firefighters_credit",
                "ca/search_and_rescue_credit",
                "ca/canada_employment_amount",
                "ca/home_buyers_credit",
                "ca/home_accessibility_credit",
                "ca/adoption_credit",
                "ca/pension_income_credit",
                "ca/disability_amount_for_self",
                "ca/disability_transferred_amount",
            )
        },
        produces={"output": "ca/credit_amounts_subtotal"},
    ),
    # Schedule 11 line 13 "Line 11 minus line 12 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/tuition_income_with_tosi", "less": "ca/credit_amounts_subtotal"},
        produces={"output": "ca/tuition_income_less_credits"},
    ),
    # Schedule 11 line 14 "Enter whichever is less amount from line 9 or line 13."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/unused_tuition_from_2024", "ca/tuition_income_less_credits")},
        produces={"output": "ca/unused_tuition_claimed"},
    ),
    # Schedule 11 line 15 "Line 13 minus line 14 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/tuition_income_less_credits", "less": "ca/unused_tuition_claimed"},
        produces={"output": "ca/tuition_income_remaining"},
    ),
    # Schedule 11 line 16 "Enter whichever is less amount from line 8 or line 15."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/current_year_tuition_available", "ca/tuition_income_remaining")},
        produces={"output": "ca/current_year_tuition_claimed"},
    ),
    # Schedule 11 line 17 "Line 14 plus line 16 Enter this amount on line 32300 of your return.
    # Your federal tuition amount =", T1 line 103 and line 32300 "Your federal tuition amount
    # (complete Schedule 11)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/unused_tuition_claimed", "ca/current_year_tuition_claimed")},
        produces={"output": "ca/federal_tuition_amount"},
    ),
    # Schedule 11 line 18 "Amount from line 10 of the previous page", line 19 "Amount from line
    # 17 of the previous page" and line 20 "Line 18 minus line 19 Total unused federal tuition
    # amount =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/total_tuition_available", "less": "ca/federal_tuition_amount"},
        produces={"output": "ca/unused_federal_tuition"},
    ),
    # Schedule 11 line 21 "Amount from line 8 of the previous page (maximum $5,000)".
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/tuition_transfer_maximum"},
        consumes={"base": "ca/current_year_tuition_available"},
        produces={"output": "ca/tuition_transfer_limit"},
    ),
    # Schedule 11 line 22 "Amount from line 16 of the previous page" and line 23 "minus line 22
    # (if negative, enter "0") Unused federal tuition amount available to transfer =", line 21
    # less line 22.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/tuition_transfer_limit",
            "less": "ca/current_year_tuition_claimed",
        },
        produces={"output": "ca/tuition_available_to_transfer"},
    ),
    # Schedule 11 line 24 and line 32700 "Enter the amount you are transferring to a designated
    # individual as shown on your Tuition and Enrolment Certificate (cannot be more than the
    # amount on line 23). Federal tuition amount transferred": the filer's election, a caller
    # input, at most line 23.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/tuition_transfer_elected",
            "bound": "ca/tuition_available_to_transfer",
        },
        produces={"output": "ca/tuition_transferred"},
    ),
    # 5000-G line 32400 "The maximum amount each student can transfer to you is $5,000 minus the
    # amount that they used to reduce their own tax payable": the bound is the printed $5,000 times
    # the caller's count of students (the owner's decision; the student's own use is not an input),
    # and the transfer is refused above it.
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/tuition_transfer_maximum_per_student"},
        consumes={"count": "ca/tuition_transfer_students"},
        produces={"output": "ca/tuition_transferred_from_child_maximum"},
    ),
    # Line 32400 "Tuition amount transferred from a child or grandchild": the amount the student
    # designates, a caller input, refused above the bound (not capped). The checked amount is the
    # one the line 33500 sum adds.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/tuition_transferred_from_child",
            "bound": "ca/tuition_transferred_from_child_maximum",
        },
        produces={"output": "ca/tuition_transferred_from_child_checked"},
    ),
    # Schedule 11 line 25 "Line 20 minus line 24 Unused federal tuition amount available to carry
    # forward to a future year =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/unused_federal_tuition", "less": "ca/tuition_transferred"},
        produces={"output": "ca/tuition_carried_forward"},
    ),
    # Schedule 2 line 1 and line 35200 "Enter the amount from line 30100 of their return.", the
    # age amount on T1 line 78 and line 30100 "Age amount (if you were born in 1960 or earlier)
    # (use Federal Worksheet) (maximum $9,028)": the maximum is a dataset of 9028 as printed, and
    # an amount above it is an input error (`InputAboveBoundError`), not capped.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/spouse_return_age_amount_maximum"},
        consumes={},
        produces={"output": "ca/spouse_return_age_amount_maximum"},
    ),
    # Schedule 2 line 1 against that maximum. The checked amount is the one line 6 adds.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/spouse_return_age_amount",
            "bound": "ca/spouse_return_age_amount_maximum",
        },
        produces={"output": "ca/spouse_return_age_amount_checked"},
    ),
    # Schedule 2 line 3 and line 35500 "Enter the amount from line 31400 of their return.
    # (maximum $2,000)", the pension income amount on T1 line 97 and line 31400 "Pension income
    # amount (use Federal Worksheet) (maximum $2,000)": the maximum is a dataset of 2000 as
    # printed, and an amount above it is an input error, not capped.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/spouse_return_pension_income_amount_maximum"},
        consumes={},
        produces={"output": "ca/spouse_return_pension_income_amount_maximum"},
    ),
    # Schedule 2 line 3 against that maximum. The checked amount is the one line 6 adds.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/spouse_return_pension_income_amount",
            "bound": "ca/spouse_return_pension_income_amount_maximum",
        },
        produces={"output": "ca/spouse_return_pension_income_amount_checked"},
    ),
    # Schedule 2 Note 2 "The maximum tuition amount your spouse or common-law partner can transfer
    # to you is $5,000 minus the current year amounts they use": line 5 and line 36000 "Enter the
    # federal amount designated to you from their forms T2202, TL11A, or TL11C. (Note 2)" is
    # refused above $5,000 as printed, not capped. The maximum is a dataset; the checked amount is
    # the output of `core/at_most`.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/spouse_designated_tuition_maximum"},
        consumes={},
        produces={"output": "ca/spouse_designated_tuition_maximum"},
    ),
    # Schedule 2 line 5 against that maximum. The checked amount is the one line 6 adds.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/spouse_designated_tuition",
            "bound": "ca/spouse_designated_tuition_maximum",
        },
        produces={"output": "ca/spouse_designated_tuition_checked"},
    ),
    # Schedule 2 line 4 and line 31600 "Enter this amount on line 31600 of your return. (maximum
    # $16,052)" (Federal Worksheet 5000-D1 line 7): line 4 and line 35700 are refused above
    # $16,052 as printed, not capped. The maximum is a dataset; the checked amount is the output
    # of `core/at_most`.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/spouse_return_disability_amount_maximum"},
        consumes={},
        produces={"output": "ca/spouse_return_disability_amount_maximum"},
    ),
    # Schedule 2 line 4 against that maximum. The checked amount is the one line 6 adds.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/spouse_return_disability_amount",
            "bound": "ca/spouse_return_disability_amount_maximum",
        },
        produces={"output": "ca/spouse_return_disability_amount_checked"},
    ),
    # Schedule 2 line 6 "Add lines 1 to 5. =": line 1 and line 35200 "Enter the amount from line
    # 30100 of their return.", line 2 and line 35300 "Enter the amount from line 30500 of their
    # return.", line 3 and line 35500 "Enter the amount from line 31400 of their return.
    # (maximum $2,000)", line 4 and line 35700 "Enter the amount from line 31600 of their return.
    # (Note 1)" and line 5 and line 36000 "Enter the federal amount designated to you from their
    # forms T2202, TL11A, or TL11C. (Note 2)", all of them figures from another person's return,
    # caller inputs; lines 1, 3, 4 and 5 are the checked amounts above.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/spouse_return_age_amount_checked",
                "ca/spouse_return_infirm_children_amount",
                "ca/spouse_return_pension_income_amount_checked",
                "ca/spouse_return_disability_amount_checked",
                "ca/spouse_designated_tuition_checked",
            )
        },
        produces={"output": "ca/spouse_transferable_amounts"},
    ),
    # Schedule 2 line 7 "Enter the amount from line 26000 of their return on line 7 if it is
    # $57,375 or less. If it is more than $57,375, enter the result of the following calculation:
    # amount from line 76 of their return divided by 14.5% =": their line 26000 and their line 76
    # are caller inputs.
    CapabilitySelection(
        name="ca/amount_or_divided_by_rate",
        params={"limit": "ca/spouse_transfer_income_limit"},
        consumes={
            "amount": "ca/spouse_return_taxable_income",
            "dividend": "ca/spouse_return_federal_basic_tax",
        },
        produces={"output": "ca/spouse_income_for_transfer"},
    ),
    # Schedule 2 line 8 and T1 line 30000 "(maximum $16,129)": the maximum is a dataset of 16129 as
    # printed, and an amount above it is an input error (`InputAboveBoundError`), not capped.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/spouse_return_basic_personal_amount_maximum"},
        consumes={},
        produces={"output": "ca/spouse_return_basic_personal_amount_maximum"},
    ),
    # Schedule 2 line 8 against that maximum. The checked amount is the one line 11 adds.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/spouse_return_basic_personal_amount",
            "bound": "ca/spouse_return_basic_personal_amount_maximum",
        },
        produces={"output": "ca/spouse_return_basic_personal_amount_checked"},
    ),
    # Schedule 2 line 8 "Amount from line 30000 of their return", line 9 "Amount from line 96 of
    # their return" and line 10 "Amount from line 32300 of their return", caller inputs, and line
    # 11 "Add lines 8 to 10. =", line 8 being the checked amount above.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/spouse_return_basic_personal_amount_checked",
                "ca/spouse_return_line_96",
                "ca/spouse_return_federal_tuition_amount",
            )
        },
        produces={"output": "ca/spouse_credits_used"},
    ),
    # Schedule 2 line 12 and line 36100 "Line 7 minus line 11 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/spouse_income_for_transfer", "less": "ca/spouse_credits_used"},
        produces={"output": "ca/spouse_adjusted_taxable_income"},
    ),
    # Schedule 2 line 13 "Line 6 minus line 12 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/spouse_transferable_amounts",
            "less": "ca/spouse_adjusted_taxable_income",
        },
        produces={"output": "ca/spouse_unused_amounts"},
    ),
    # Schedule 2 "If you were separated because of a breakdown in your relationship for a period
    # of 90 days or more including December 31, 2025, your spouse or common-law partner cannot
    # transfer any unused amounts to you." and line 13 "Enter this amount on line 32600 of your
    # return. Federal amounts transferred from your spouse or common-law partner", T1 line 105
    # and line 32600 "Amounts transferred from your spouse or common-law partner (complete
    # Schedule 2)": line 13 is counted once when not separated and not at all when separated, a
    # caller's 1 or 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/spouse_unused_amounts",
            "count": "ca/spouse_not_separated_90_days_checked",
        },
        produces={"output": "ca/amounts_transferred_from_spouse"},
    ),
    # T1 line 33500 (lines 30000, 30100, 30300, 30400, 30425, 30450, 30500, 30800, 31000, 31200,
    # 31217, 31260, 31800, 32300, 32400, 32600, 33200) and ON428 line 58800 (lines 58040, 58080,
    # 58120, 58160, 58185, 58240, 58280, 58300, 58305, 58769), in the forms' line order. T1 line
    # 113 and line 33500 is "Line 106 plus line 112", and line 112 (line 33200) follows the lines
    # that line 106 adds; ON428 line 44 and line 58800 is "Line 35 plus line 43", and line 43
    # (line 58769) follows the lines that line 35 adds. ON428 lines 58240, 58280, 58300 and 58305
    # are "Amount from line 30800 / 31000 / 31200 / 31217 of your return", so the Ontario sum
    # reads the federal kinds; it has no Canada employment amount. Lines 31000 "on self-employment
    # income and other earnings" and 31217 "on self-employment and other eligible earnings
    # (complete Schedule 13)" follow lines 30800 and 31200, as ON428's lines 58280 and 58305
    # follow its lines 58240 and 58300.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/basic_personal_amount",
                "ca/age_amount",
                "ca/spouse_amount",
                "ca/eligible_dependant_amount",
                "ca/caregiver_amount_for_spouse_or_dependant",
                "ca/caregiver_amount",
                "ca/infirm_children_amount",
                "ca/cpp_base_contributions_on_return",
                "ca/cpp_base_contributions_on_self_employment_and_other_earnings",
                "ca/ei_premiums",
                "ca/ei_premiums_on_self_employment",
                "ca/volunteer_firefighters_credit",
                "ca/search_and_rescue_credit",
                "ca/canada_employment_amount",
                "ca/home_buyers_credit",
                "ca/home_accessibility_credit",
                "ca/adoption_credit",
                "ca/pension_income_credit",
                "ca/disability_amount_for_self",
                "ca/disability_transferred_amount",
                "ca/student_loan_interest",
                "ca/federal_tuition_amount",
                "ca/tuition_transferred_from_child_checked",
                "ca/amounts_transferred_from_spouse",
                "ca/medical_claim",
            )
        },
        produces={"output": "ca/non_refundable_credit_amounts"},
    ),
    # Schedule 9 chart for line 33700 "Gifts of capital property that is depreciable property",
    # line 4 "Enter whichever is less: amount from line 2 or line 3.": the net proceeds of
    # disposition of the property donated in 2025 (line 2) and its capital cost (line 3), caller
    # inputs for the one class and property the return claims.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/depreciable_gift_net_proceeds", "ca/depreciable_gift_capital_cost")
        },
        produces={"output": "ca/depreciable_gift_proceeds_or_cost"},
    ),
    # Schedule 9 chart for line 33700, line 5 "Enter whichever is less: amount from line 1 or
    # line 4. Enter this amount on line 33700 of the previous page.": line 1 "Amount of
    # recaptured depreciation included on your 2025 return" is a caller input. This is the
    # previous page's line B, "Gifts of capital property that are depreciable property".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/depreciable_gift_recaptured_depreciation",
                "ca/depreciable_gift_proceeds_or_cost",
            )
        },
        produces={"output": "ca/depreciable_gifts"},
    ),
    # Schedule 9 chart for line 33900 "Gifts of capital property", line 2 "Amount of current-year
    # capital gains deduction from capital property donated in 2025" at most line 1 "Amount of
    # current-year taxable capital gains from capital property donated in 2025" (the bound; the
    # form prints no maximum for line 2), checked against line 1.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/capital_gift_gains_deduction",
            "bound": "ca/capital_gift_taxable_gains",
        },
        produces={"output": "ca/capital_gift_gains_deduction_checked"},
    ),
    # Schedule 9 chart for line 33900 line 3 "Line 1 minus Line 2 Enter this amount on line 33900
    # on the previous page.": line 1 is the caller's input and line 2 is the checked amount above.
    # This is the previous page's line C, "Gifts of capital property".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gift_taxable_gains",
            "less": "ca/capital_gift_gains_deduction_checked",
        },
        produces={"output": "ca/capital_property_gifts"},
    ),
    # Schedule 9 line 5 "Add lines 1 to 4. Total eligible amount of charitable donations": line
    # 1 donations to registered charities and similar organizations, line 2 (line 32900)
    # donations to the Government of Canada, a province or territory and similar bodies, line 3
    # (line 33300) donations to registered universities outside Canada and line 4 (line 33400)
    # donations to the United Nations and its agencies and registered foreign charities, caller
    # inputs taken as the receipts state them, with any unused donations of the previous five
    # years that the filer chooses to claim.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/charitable_donations",
                "ca/government_donations",
                "ca/university_donations_outside_canada",
                "ca/foreign_charity_donations",
            )
        },
        produces={"output": "ca/total_charitable_donations"},
    ),
    # Schedule 9 line 6 "Enter your net income from line 23600 of your return. Line A"
    # "multiplied by 75%": 75% of the net income.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/donation_net_income_rate"},
        consumes={"base": "ca/net_income"},
        produces={"output": "ca/donation_limit_on_net_income"},
    ),
    # Schedule 9 line 7 "Amount B plus amount C Line D" "multiplied by 25%": line D is the gifts
    # of capital property that are depreciable property (line B, line 33700) plus the gifts of
    # capital property (line C, line 33900), and line 7 is 25% of it.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/depreciable_gifts", "ca/capital_property_gifts")},
        produces={"output": "ca/capital_gifts_total"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/capital_gifts_limit_rate"},
        consumes={"base": "ca/capital_gifts_total"},
        produces={"output": "ca/capital_gifts_limit_addition"},
    ),
    # Schedule 9 line 8 "Line 6 plus line 7".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/donation_limit_on_net_income", "ca/capital_gifts_limit_addition")},
        produces={"output": "ca/donation_limit_with_capital_gifts"},
    ),
    # Schedule 9 line 9 "Enter whichever is less: amount A or line 8. Total charitable donations
    # limit": amount A is the net income of line 6, so the 25% of the gifts of capital property
    # can raise the limit above 75% of the net income, but not above the net income itself.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/net_income", "ca/donation_limit_with_capital_gifts")},
        produces={"output": "ca/charitable_donations_limit"},
    ),
    # Schedule 9 line 10 and line 34000 "Enter whichever is less: amount from line 5 or line 9."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/total_charitable_donations", "ca/charitable_donations_limit")},
        produces={"output": "ca/charitable_donations_claimed"},
    ),
    # Schedule 9 line 11 and line 34200 "Eligible amount of ecological gifts and cultural gifts
    # (see Guide P113)", a caller input, and line 12 "Line 10 plus line 11".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/charitable_donations_claimed", "ca/ecological_and_cultural_gifts")},
        produces={"output": "ca/donations_and_gifts_total"},
    ),
    # Schedule 9 line 13 "Enter whichever is less: amount from line 12 or $200.": the $200 is a
    # dataset, claimed whole.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/donation_first_tier_maximum"},
        consumes={},
        produces={"output": "ca/donation_first_tier_maximum"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/donations_and_gifts_total", "ca/donation_first_tier_maximum")},
        produces={"output": "ca/donations_first_tier"},
    ),
    # Schedule 9 line 14 "Line 12 minus line 13".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/donations_and_gifts_total", "less": "ca/donations_first_tier"},
        produces={"output": "ca/donations_over_first_tier"},
    ),
    # Schedule 9 line 15 and line 34210 "Total ecological gifts made after February 10, 2014,
    # and before 2016 included in the amount on line 11", a caller input, and line 16 "Line 14
    # minus line 15 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/donations_over_first_tier",
            "less": "ca/ecological_gifts_before_2016",
        },
        produces={"output": "ca/donations_over_first_tier_after_2016_gifts"},
    ),
    # Schedule 9 line 18 "Income threshold 253,414.00": the dataset becomes an artifact of the
    # same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/donation_high_income_threshold"},
        consumes={},
        produces={"output": "ca/donation_high_income_threshold"},
    ),
    # Schedule 9 line 17 "Enter your taxable income from line 26000 of your return." and line 19
    # "Line 17 minus line 18 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/taxable_income", "less": "ca/donation_high_income_threshold"},
        produces={"output": "ca/taxable_income_over_donation_threshold"},
    ),
    # Schedule 9 line 20 "Enter whichever is less: amount from line 16 or line 19. Line F"
    # "multiplied by 33%": line F, then 33% of it.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/donations_over_first_tier_after_2016_gifts",
                "ca/taxable_income_over_donation_threshold",
            )
        },
        produces={"output": "ca/high_income_donations"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/donation_high_income_rate"},
        consumes={"base": "ca/high_income_donations"},
        produces={"output": "ca/high_income_donation_credit"},
    ),
    # Schedule 9 line 21 "Amount E minus amount F Line G" "multiplied by 29%": amount E is the
    # amount from line 14 of the previous page and amount F is line F; line G, then 29% of it.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/donations_over_first_tier", "less": "ca/high_income_donations"},
        produces={"output": "ca/regular_rate_donations"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/donation_regular_rate"},
        consumes={"base": "ca/regular_rate_donations"},
        produces={"output": "ca/regular_rate_donation_credit"},
    ),
    # Schedule 9 line 22 "Amount from line 13 of the previous page Line H" "multiplied by
    # 14.5%".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/donation_first_tier_rate"},
        consumes={"base": "ca/donations_first_tier"},
        produces={"output": "ca/first_tier_donation_credit"},
    ),
    # Schedule 9 line 23 "Add lines 20 to 22. Enter this amount on line 34900 of your return.
    # Allowable donations for 2025", T1 line 116 (line 34900) "Donations and gifts (complete
    # Schedule 9)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/high_income_donation_credit",
                "ca/regular_rate_donation_credit",
                "ca/first_tier_donation_credit",
            )
        },
        produces={"output": "ca/donations_and_gifts_credit"},
    ),
    # T1 line 115 (line 33800) "Line 113 multiplied by the percentage from line 114": the
    # federal credit rate is applied once, to the total of credit amounts. It is the first of
    # the three lines that line 35000 adds, and the base of the top-up tax credit.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/credit_rate"},
        consumes={"base": "ca/non_refundable_credit_amounts"},
        produces={"output": "ca/credit_amounts_at_credit_rate"},
    ),
    # Federal Worksheet 5000-D1, "Line 34990 - Top-up tax credit": line 1 "Amount from line
    # 33800 of your return", line 2 "Amount from line 22 of your Schedule 9" and line 3 "Line 1
    # plus line 2".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/credit_amounts_at_credit_rate", "ca/first_tier_donation_credit")},
        produces={"output": "ca/top_up_credits_base"},
    ),
    # Federal Worksheet 5000-D1, "Line 34990 - Top-up tax credit", line 4 "8,319.38": the
    # dataset becomes an artifact of the same name; line 5 "Line 3 minus line 4 (if negative,
    # enter "0")".
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/top_up_threshold"},
        consumes={},
        produces={"output": "ca/top_up_threshold"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/top_up_credits_base", "less": "ca/top_up_threshold"},
        produces={"output": "ca/top_up_excess"},
    ),
    # Federal Worksheet 5000-D1, "Line 34990 - Top-up tax credit", line 6 "Applicable rate
    # 3.45%" and line 7 "Line 5 multiplied by the percentage from line 6 Enter this amount on
    # line 34990 of your return.", T1 line 117 (line 34990) "Top-up tax credit (use Federal
    # Worksheet)".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/top_up_rate"},
        consumes={"base": "ca/top_up_excess"},
        produces={"output": "ca/top_up_tax_credit"},
    ),
    # T1 line 118 (line 35000) "Add lines 115 to 117. Total federal non-refundable tax credits":
    # line 115 (line 33800), line 116 (line 34900) and line 117 (line 34990), in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/credit_amounts_at_credit_rate",
                "ca/donations_and_gifts_credit",
                "ca/top_up_tax_credit",
            )
        },
        produces={"output": "ca/non_refundable_tax_credits"},
    ),
    # Form T1206 Part 2 line 8 "Amount from line 7 multiplied by 33% Enter this amount on line 40424
    # of your return. Federal tax on split income", line 7 being "Total split income from line 4",
    # which is line 4 itself: T1 line 120 and line 40424 "Federal tax on split income (TOSI)
    # (complete Form T1206)".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/split_income_rate"},
        consumes={"base": "ca/total_split_income"},
        produces={"output": "ca/federal_tax_on_split_income"},
    ),
    # Form T1206 Part 2 line 8A "TOSI-adjusted taxable income: Amount from line 8 ÷ 14.5% =", line 8
    # being the federal tax on split income.
    CapabilitySelection(
        name="ca/divided_by_rate",
        params={"rate": "ca/tosi_taxable_income_rate"},
        consumes={"dividend": "ca/federal_tax_on_split_income"},
        produces={"output": "ca/tosi_adjusted_taxable_income"},
    ),
    # Form T1206 "If you are completing a federal Schedule 11, calculate line 8A and add it to the
    # amount on line 11 of Schedule 11": the amount on line 11 (the taxable income, or the tax
    # divided by 14.5%) plus line 8A.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/tuition_income_base", "ca/tosi_adjusted_taxable_income")},
        produces={"output": "ca/tuition_income_with_tosi"},
    ),
    # T1 line 121 and line 40400 "Line 119 plus line 120 =": line 119 "Enter the amount from line
    # 76." is the federal basic tax and line 120 is the federal tax on split income, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_basic_tax",
                "ca/federal_tax_on_split_income",
            )
        },
        produces={"output": "ca/federal_tax_with_split_income"},
    ),
    # Each form's credits come off its tax, not below zero: the unused part is lost. Federally the
    # tax is line 121 (line 119, the basic tax, plus line 120, the tax on split income) and the
    # credits are line 125 (T1 line 126 "Line 121 minus line 125 (if negative, enter "0")").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/federal_tax_with_split_income",
            "less": "ca/credits_against_basic_federal_tax",
        },
        produces={"output": "ca/federal_tax_after_credits"},
    ),
    # T2038(IND) Part C "Recapture", "Amount of expenditure on which ITC earned at 15% (after
    # 2013) is recaptured. Do not enter more than the amount of the original expenditure" (line
    # 67193), times 0.15, amount 1: the caller's line 67193 at 15%.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_recapture_rate_after_2013"},
        consumes={"base": "ca/itc_recapture_expenditure_at_15_percent"},
        produces={"output": "ca/itc_recapture_at_15_percent"},
    ),
    # Line 67195 "Amount of expenditure on which ITC earned at 20% (before 2014) is recaptured.
    # Do not enter more than the amount of the original expenditure", times 0.20, amount 2: the
    # caller's line 67195 at 20%.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_recapture_rate_before_2014"},
        consumes={"base": "ca/itc_recapture_expenditure_at_20_percent"},
        produces={"output": "ca/itc_recapture_at_20_percent"},
    ),
    # "Total recapture of investment tax credit on SR&ED expenditures (add amounts 1 and 2)
    # Enter this amount on the Recapture of investment tax credit line of your income tax and
    # benefit return" (amount 3), T1 line 131 "Recapture of investment tax credit (complete Form
    # T2038(IND))": amounts 1 and 2 added.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/itc_recapture_at_15_percent", "ca/itc_recapture_at_20_percent")},
        produces={"output": "ca/itc_recapture"},
    ),
    # Form T2209 note (3), "amounts deductible as ... foreign income exempt under a tax treaty ...
    # (included on line 25600 of your return)": the part of line 25600 that is exempt income is at
    # most the whole, line 25600 "Additional deductions" (`ca/additional_deductions_total`). An
    # amount
    # above it is refused, not capped; the sum below reads the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/exempt_income_deductions",
            "bound": "ca/additional_deductions_total",
        },
        produces={"output": "ca/exempt_income_deductions_checked"},
    ),
    # Form T2209 note (3), net income: "Amount from line 23600 of your return (or the amount you
    # would have entered if the instructions said "if negative, show in brackets") plus the amount
    # on line 68360 of Form T1206, Total split income, minus any:" "amount deductible as a
    # Canadian Forces personnel and police deduction (line 24400 of your return)", "amount
    # deductible as security options deductions (line 24900 of your return)", "amount deductible
    # as an other payments deduction (line 25000 of your return)", "net capital losses of other
    # years you claimed (line 25300 of your return)", "capital gains deduction for qualifying
    # business transfer or qualifying cooperative conversion you claimed (line 25395 of your
    # return)", "capital gains deduction you claimed (line 25400 of your return)" and "amounts
    # deductible as net employment income from a prescribed international organization, as foreign
    # income exempt under a tax treaty, or as adult basic education tuition assistance (included
    # on line 25600 of your return)", in the note's order, added.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/canadian_armed_forces_and_police_deduction",
                "ca/security_options_deductions",
                "ca/other_payments_deduction",
                "ca/net_capital_losses_of_other_years",
                "ca/qbt_capital_gains_deduction",
                "ca/capital_gains_deduction",
                "ca/exempt_income_deductions_checked",
            )
        },
        produces={"output": "ca/foreign_tax_credit_net_income_deductions"},
    ),
    # The net income of note (3), "Amount from line 23600 of your return (or the amount you would
    # have entered if the instructions said "if negative, show in brackets")": line 23400 less line
    # 23500, not floored, so signed. It is not the line 23600 kind, which is floored at 0.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/net_income_before_adjustments",
            "less": "ca/social_benefits_repayment",
        },
        produces={"output": "ca/foreign_tax_credit_net_income_before_split_income"},
    ),
    # Note (3), "plus the amount on line 68360 of Form T1206, Total split income": that amount
    # added. It is the same figure as the TOSI-adjusted net income, which adds line 68360 to line
    # 23400 less line 23500.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/foreign_tax_credit_net_income_before_split_income",
                "ca/total_split_income",
            )
        },
        produces={"output": "ca/foreign_tax_credit_net_income_with_split_income"},
    ),
    # Note (3), "minus any:" the deductions above. The note prints no "(if negative, enter "0")",
    # so the result is signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/foreign_tax_credit_net_income_with_split_income",
            "less": "ca/foreign_tax_credit_net_income_deductions",
        },
        produces={"output": "ca/foreign_tax_credit_net_income"},
    ),
    # Form T2209 note (4), basic federal tax: "Line 42900 of your return plus any:" "federal
    # dividend tax credit (line 40425 of your return)" (note (8) is this sum alone, for the
    # business lines).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/federal_tax_after_credits", "ca/dividend_tax_credit")},
        produces={"output": "ca/basic_federal_tax_with_dividend_credit"},
    ),
    # Note (4), "plus any: federal surtax on income allocated to "Other (Outside Canada)" (line 10
    # of Part 2 of Form T2203, or 48% of the amount from line 42900)": the surtax on income earned
    # outside Canada, T1 line 127 (`ca/federal_surtax_outside_canada`). The surtax prints no floor,
    # so the sum is not floored.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/basic_federal_tax_with_dividend_credit",
                "ca/federal_surtax_outside_canada",
            )
        },
        produces={"output": "ca/basic_federal_tax_with_dividend_credit_and_surtax"},
    ),
    # Note (4), "minus any:" "federal refundable First Nations abatement (line 44100 of your
    # return)" (and the refundable Quebec abatement, line 44000, which does not apply to an
    # Ontario return). The result is not below zero: the abatement is not allowed to take the basic
    # federal tax below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/basic_federal_tax_with_dividend_credit_and_surtax",
            "less": "ca/first_nations_abatement",
        },
        produces={"output": "ca/foreign_tax_credit_basic_federal_tax"},
    ),
    # Form T2209 page 1 note: the foreign tax paid on income from property over 15% of that income,
    # for line 23200, taken off line 1 of the credit below.
    CapabilitySelection(
        name="ca/foreign_property_tax_over_limit",
        params={"limit_rate": "ca/foreign_property_income_credit_limit_rate"},
        consumes={"countries": "ca/foreign_tax_countries"},
        produces={"output": "ca/foreign_property_tax_over_limit"},
    ),
    # Form T2209 line 6 "Federal surtax on income allocated to "Other (Outside Canada)":"
    # "Amount from line 10 of Part 2 of Form T2203 ... or 48% of the amount from line 42900 of your
    # return. Enter the amount that applies to the country or countries you identified at the top
    # of this page.": the amount that applies to the countries of a sheet is the filer's, each
    # country's record holding its part of the one surtax of T1 line 127
    # (`ca/federal_surtax_outside_canada`; T2203 Part 2 note (1): "enter this amount on line 127 of
    # your return"). The parts are added and may not be more than that surtax; no positive part is
    # allocated of a surtax of 0 or less.
    CapabilitySelection(
        name="ca/foreign_surtax_allocated_total",
        params={},
        consumes={"countries": "ca/foreign_tax_countries"},
        produces={"output": "ca/foreign_surtax_allocated_total"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/federal_surtax_outside_canada",)},
        produces={"output": "ca/foreign_surtax_limit"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/foreign_surtax_allocated_total",
            "bound": "ca/foreign_surtax_limit",
        },
        produces={"output": "ca/foreign_surtax_allocated_total_checked"},
    ),
    # Form T2209, federal non-business foreign tax credit: line 1 "Non-business income tax paid to
    # a foreign country (1) 43100", line 2 "Net foreign non-business income (2) 43300" "× Basic
    # federal tax (4) =" over "Net income (3)", line 3 "Enter whichever is less: the amount from
    # line 1 or line 2. Federal non-business foreign tax credit", for each country on its own
    # when "you paid tax to more than one foreign country, and the total foreign taxes paid to all
    # foreign countries was more than $200", otherwise once on the totals; the total of line 3.
    CapabilitySelection(
        name="ca/foreign_non_business_tax_credit",
        params={
            "rounding": "ca/foreign_non_business_tax_credit_rounding",
            "pooling_threshold": "ca/foreign_tax_pooling_threshold",
            "limit_rate": "ca/foreign_property_income_credit_limit_rate",
        },
        consumes={
            "countries": "ca/foreign_tax_countries",
            "net_income": "ca/foreign_tax_credit_net_income",
            "basic_federal_tax": "ca/foreign_tax_credit_basic_federal_tax",
        },
        produces={
            "total": "ca/federal_non_business_foreign_tax_credit",
            "sheets": "ca/foreign_tax_credit_sheets",
        },
    ),
    # Form T2209, federal business foreign tax credit, on the same sheets: line 4 "Business income
    # tax paid to a foreign country (5) for the year, plus any unused foreign tax credits for that
    # country for the 10 years (6) before, and the 3 years after this year" (43400); the total of
    # line 4.
    CapabilitySelection(
        name="ca/foreign_business_tax_credit_line_4",
        params={"rounding": "ca/foreign_business_tax_credit_rounding"},
        consumes={
            "sheets": "ca/foreign_tax_credit_sheets",
            "net_income": "ca/foreign_tax_credit_net_income",
            "basic_federal_tax": "ca/basic_federal_tax_with_dividend_credit",
        },
        produces={"output": "ca/foreign_business_tax_credit_line_4"},
    ),
    # Line 5 "Net foreign business income (7)" (43900) "× Basic federal tax (8)" over "Net income
    # (3)", where note (8) is "Line 42900 of your return plus any federal dividend tax credit (line
    # 40425 of your return)." and note (7) says "If your net foreign business income is more than
    # your net income, use your net income in the calculation."; the total of line 5, each sheet
    # rounded half-up to the cent.
    CapabilitySelection(
        name="ca/foreign_business_tax_credit_line_5",
        params={"rounding": "ca/foreign_business_tax_credit_rounding"},
        consumes={
            "sheets": "ca/foreign_tax_credit_sheets",
            "net_income": "ca/foreign_tax_credit_net_income",
            "basic_federal_tax": "ca/basic_federal_tax_with_dividend_credit",
        },
        produces={"output": "ca/foreign_business_tax_credit_line_5"},
    ),
    # Line 7 "Add lines 5 and 6.", line 6 being "Federal surtax on income allocated to "Other
    # (Outside Canada)":" "Amount from line 10 of Part 2 of Form T2203, Provincial and Territorial
    # Taxes for Multiple Jurisdictions, or 48% of the amount from line 42900 of your return. Enter
    # the amount that applies to the country or countries you identified at the top of this
    # page."; the total of line 7.
    CapabilitySelection(
        name="ca/foreign_business_tax_credit_line_7",
        params={"rounding": "ca/foreign_business_tax_credit_rounding"},
        consumes={
            "sheets": "ca/foreign_tax_credit_sheets",
            "net_income": "ca/foreign_tax_credit_net_income",
            "basic_federal_tax": "ca/basic_federal_tax_with_dividend_credit",
        },
        produces={"output": "ca/foreign_business_tax_credit_line_7"},
    ),
    # Line 8 "Add basic federal tax (8) and the amount from line 6."; the total of line 8.
    CapabilitySelection(
        name="ca/foreign_business_tax_credit_line_8",
        params={"rounding": "ca/foreign_business_tax_credit_rounding"},
        consumes={
            "sheets": "ca/foreign_tax_credit_sheets",
            "net_income": "ca/foreign_tax_credit_net_income",
            "basic_federal_tax": "ca/basic_federal_tax_with_dividend_credit",
        },
        produces={"output": "ca/foreign_business_tax_credit_line_8"},
    ),
    # Line 9 "Enter the amount from line 3, if any." and line 10 "Line 8 minus line 9", which prints
    # no "(if negative, enter "0")"; the total of line 10.
    CapabilitySelection(
        name="ca/foreign_business_tax_credit_line_10",
        params={"rounding": "ca/foreign_business_tax_credit_rounding"},
        consumes={
            "sheets": "ca/foreign_tax_credit_sheets",
            "net_income": "ca/foreign_tax_credit_net_income",
            "basic_federal_tax": "ca/basic_federal_tax_with_dividend_credit",
        },
        produces={"output": "ca/foreign_business_tax_credit_line_10"},
    ),
    # Line 11 "Enter whichever is less: the amount from line 4, 7 or 10." "Federal business foreign
    # tax credit"; the total of line 11.
    CapabilitySelection(
        name="ca/foreign_business_tax_credit_line_11",
        params={"rounding": "ca/foreign_business_tax_credit_rounding"},
        consumes={
            "sheets": "ca/foreign_tax_credit_sheets",
            "net_income": "ca/foreign_tax_credit_net_income",
            "basic_federal_tax": "ca/basic_federal_tax_with_dividend_credit",
        },
        produces={"output": "ca/federal_business_foreign_tax_credit"},
    ),
    # T2209 line 12 "Enter the amount from line 3, if any." and line 13 "Add lines 11 and 12."
    # "Federal foreign tax credit": line 11 and line 12, the total of line 3.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_business_foreign_tax_credit",
                "ca/federal_non_business_foreign_tax_credit",
            )
        },
        produces={"output": "ca/federal_foreign_tax_credit_before_limit"},
    ),
    # Form T2203 Part 1 line 52220 column 5 "percentage" above 100 is an input error, not capped (a
    # choice: the form prints no maximum). The maximum is a credit dataset of 100, taken whole, and
    # the checked percentage is the one the readers of the percentage apply.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/amt_t2203_column_5_percentage_maximum"},
        consumes={},
        produces={"output": "ca/amt_t2203_column_5_percentage_maximum"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_t2203_column_5_percentage",
            "bound": "ca/amt_t2203_column_5_percentage_maximum",
        },
        produces={"output": "ca/amt_t2203_column_5_percentage_checked"},
    ),
    # T2203 Part 2 line 4 "Enter your basic federal tax from line 42900 of your return." is
    # `ca/federal_tax_after_credits`, read directly. Line 5 "If you have to pay tax on split income,
    # enter the amount from line 22 of your Form T1206. If not, enter "0"": the condition "you have
    # to pay tax on split income" counts 1 when the federal tax on split income is more than 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t2203_tax_on_split_income_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/federal_tax_on_split_income",),
        },
        produces={"output": "ca/t2203_has_tax_on_split_income"},
    ),
    # T2203 Part 2 line 5, the second branch: line 22 of Form T1206 when there is tax on split
    # income (the count above), and "0" otherwise.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/split_income_line_22",
            "count": "ca/t2203_has_tax_on_split_income",
        },
        produces={"output": "ca/t2203_line_5"},
    ),
    # T2203 Part 2 line 6 "Enter whichever is more: amount from line 4 or line 5.": the greater of
    # line 4 (`ca/federal_tax_after_credits`) and line 5.
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={
            "amounts": (
                "ca/federal_tax_after_credits",
                "ca/t2203_line_5",
            )
        },
        produces={"output": "ca/t2203_line_6"},
    ),
    # T2203 Part 2 line 8 "Line 6 multiplied by the percentage from line 7": line 7 is the caller's
    # percentage of Part 1 line 52220 column 5, as printed (25 for 25%), rounded once by its
    # dataset.
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/t2203_line_8_rounding"},
        consumes={
            "amount": "ca/t2203_line_6",
            "percentage": "ca/amt_t2203_column_5_percentage_checked",
        },
        produces={"output": "ca/t2203_line_8"},
    ),
    # T2203 Part 2 line 10 "Line 8 multiplied by the percentage from line 9": line 9 "Federal
    # surtax rate", 48%, from its rate dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t2203_federal_surtax_rate"},
        consumes={"base": "ca/t2203_line_8"},
        produces={"output": "ca/t2203_federal_surtax_outside_canada"},
    ),
    # T1 line 127 "Federal surtax on income earned outside Canada (complete Form T2203)": line 10 of
    # Part 2 of Form T2203, or, when you are subject to minimum tax (the caller's count, 1 for yes),
    # line 4 of Part 3 of Form T691 ("If you are subject to minimum tax, do not complete lines 4 to
    # 10" on Form T2203). Part 3 line 4 has no floor, so the surtax may be negative.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/amt_subject_to_minimum_tax",
            "when_none": "ca/t2203_federal_surtax_outside_canada",
            "when_any": "ca/amt_federal_surtax",
        },
        produces={"output": "ca/federal_surtax_outside_canada"},
    ),
    # T1 line 128 "Line 126 plus line 127 =": line 126 (`ca/federal_tax_after_credits`) and line
    # 127.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_tax_after_credits",
                "ca/federal_surtax_outside_canada",
            )
        },
        produces={"output": "ca/federal_tax_with_surtax"},
    ),
    # T2209 line 13 "Add lines 11 and 12." "Federal foreign tax credit", limited by "The amount on
    # line 13 should not be more than the total of the amount on line 42900 of your return, plus
    # any federal surtax on income earned outside of Canada." The limit is line 42900 plus line
    # 127, that is line 128 (`ca/federal_tax_with_surtax`), and it is 0 when line 128 is not
    # positive. T1 line 129 (line 40500) "Federal foreign tax credit (complete Form T2209)".
    CapabilitySelection(
        name="ca/lesser_of_when_positive",
        params={},
        consumes={
            "amounts": (
                "ca/federal_foreign_tax_credit_before_limit",
                "ca/federal_tax_with_surtax",
            )
        },
        produces={"output": "ca/federal_foreign_tax_credit"},
    ),
    # T1 line 130 "Line 128 minus line 129 =": line 128 (`ca/federal_tax_with_surtax`) less line 129
    # (40500). The line prints no "(if negative, enter "0")", so the result is signed: line 128 is
    # negative only when line 127 is, and the credit is then 0.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/federal_tax_with_surtax",
            "less": "ca/federal_foreign_tax_credit",
        },
        produces={"output": "ca/federal_tax_less_foreign_tax_credit"},
    ),
    # T1 line 132 "Line 130 plus line 131 =": line 130 and line 131 "Recapture of investment tax
    # credit (complete Form T2038(IND))".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/federal_tax_less_foreign_tax_credit", "ca/itc_recapture")},
        produces={"output": "ca/federal_tax_with_itc_recapture"},
    ),
    # T1 line 31220 "Volunteer firefighters' amount (VFA)" (line 90): "You can claim $6,000 for the
    # volunteer firefighters' amount (VFA) or search and rescue volunteers' amount (SRVA), but not
    # both, if you meet all of the following conditions:" (T1 guide 5000-G, 2025). The amount is
    # $6,000 times the conditions met (a caller's count, 1 or 0).
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/volunteer_firefighters_amount"},
        consumes={"count": "ca/volunteer_firefighters_conditions_met_checked"},
        produces={"output": "ca/volunteer_firefighters_credit"},
    ),
    # T1 line 31240 "Search and rescue volunteers' amount (SRVA)" (line 91): the same $6,000
    # amount times the conditions met for search and rescue (a caller's count, 1 or 0).
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/search_and_rescue_volunteers_amount"},
        consumes={"count": "ca/search_and_rescue_conditions_met_checked"},
        produces={"output": "ca/search_and_rescue_credit"},
    ),
    # The VFA and the SRVA together, before the "but not both" maximum (line 31220 and line 31240).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/volunteer_firefighters_credit",
                "ca/search_and_rescue_credit",
            )
        },
        produces={"output": "ca/volunteer_credits_claimed"},
    ),
    # "but not both": the maximum of $6,000 for the VFA or the SRVA (T1 guide 5000-G, 2025).
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/volunteer_amount_maximum"},
        consumes={},
        produces={"output": "ca/volunteer_amount_maximum"},
    ),
    # "but not both": the VFA and the SRVA together at most the maximum. Above it the claim is an
    # input error (`InputAboveBoundError`), not capped. The result is a checked side artifact,
    # not summed (line 31220 and line 31240 are summed on line 33500 above).
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/volunteer_credits_claimed",
            "bound": "ca/volunteer_amount_maximum",
        },
        produces={"output": "ca/volunteer_credits_checked"},
    ),
    # T1 line 31270 "Home buyers' amount (maximum $10,000)" (line 93): "Enter $10,000 on line 31270
    # of your return if you are not splitting the amount with your spouse or common-law partner."
    # The maximum is $10,000 (T1 guide 5000-G, 2025).
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/home_buyers_maximum"},
        consumes={},
        produces={"output": "ca/home_buyers_maximum"},
    ),
    # T1 line 31270: the filer's claim, at most the maximum ("You and your spouse or common-law
    # partner can split the claim but the combined total cannot be more than $10,000." The split
    # is an election, so the filer enters their share). Above it is an input error.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/home_buyers_claim",
            "bound": "ca/home_buyers_maximum",
        },
        produces={"output": "ca/home_buyers_credit"},
    ),
    # Worksheet for line 31285 "Home accessibility expenses (use Federal Worksheet) (maximum
    # $20,000)", line 2: "Enter whichever is less: amount from line 1 or $20,000." (line 1, the
    # total eligible expenses, is the caller's input).
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/home_accessibility_maximum"},
        consumes={"base": "ca/home_accessibility_expenses"},
        produces={"output": "ca/home_accessibility_line_2"},
    ),
    # Worksheet for line 31285, line 3, checked against line 2: line 4 is "Line 2 minus line 3" and
    # the form prints no "if negative, enter 0", so an amount claimed by others above line 2 would
    # be a negative claim. It is refused as an input error, not floored (negatives rule).
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/home_accessibility_claimed_by_others",
            "bound": "ca/home_accessibility_line_2",
        },
        produces={"output": "ca/home_accessibility_claimed_by_others_checked"},
    ),
    # Worksheet for line 31285, line 4: "Line 2 minus line 3 Enter this amount on line 31285 of
    # your return." Line 3 is the amount claimed by other qualifying individuals in the same
    # dwelling, read as checked above.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/home_accessibility_line_2",
            "less": "ca/home_accessibility_claimed_by_others_checked",
        },
        produces={"output": "ca/home_accessibility_credit"},
    ),
    # T1 line 31300 "Adoption expenses" (line 95): "Enter on line 31300 of your return the amount of
    # eligible adoption expenses that you can claim for all eligible children." The list holds one
    # record for each child, the filer's eligible expenses for that child; the form has no federal
    # maximum for line 31300 (the guide and the T1 are silent), so the total is taken as entered.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/adoption_expense_children"},
        produces={"output": "ca/adoption_credit"},
    ),
    # Worksheet for line 31400, line 2 "Foreign pension income included in the amount on line 11500
    # of your return and deducted on line 25600 of your return": the foreign pension income is at
    # most line 25600 "Additional deductions" (`ca/additional_deductions_total`), which it is
    # deducted in.
    # An amount above it is refused, not capped. Line 5 reads the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/pension_foreign_income",
            "bound": "ca/additional_deductions_total",
        },
        produces={"output": "ca/pension_foreign_income_checked"},
    ),
    # Worksheet for line 31400 "Pension income amount" (line 97), line 5: "Add lines 2 to 4." (the
    # foreign pension income, the U.S. IRA income and the RRIF or PRPP amounts transferred).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/pension_foreign_income_checked",
                "ca/pension_us_ira_income",
                "ca/pension_rrif_transferred",
            )
        },
        produces={"output": "ca/pension_chart_line_5"},
    ),
    # Worksheet for line 31400, line 1 "Amount from line 11500 of your return": the other pensions
    # and the Form T2205 amount on line 11500, not below zero.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/other_pensions_and_superannuation", "ca/t2205_on_line_11500")},
        produces={"output": "ca/pension_chart_line_1"},
    ),
    # Worksheet for line 31400, line 1 "Amount from line 11500 of your return" bounds line 5: each
    # of lines 2 to 4 is "included in the amount on line 11500", so their total is at most line 1.
    # An amount above it is an input error, not capped. The checked amount is the one line 6 reads.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/pension_chart_line_5",
            "bound": "ca/pension_chart_line_1",
        },
        produces={"output": "ca/pension_chart_line_5_checked"},
    ),
    # Worksheet for line 31400, line 6: "Line 1 minus line 5", line 1 being the amount from line
    # 11500 of the return (`ca/pension_chart_line_1`). The form prints "minus" without
    # "(if negative, enter "0")"; the result is taken as not below zero. Line 5 is at most line 1,
    # a total above line 11500 being refused by the check above.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/pension_chart_line_1",
            "less": "ca/pension_chart_line_5_checked",
        },
        produces={"output": "ca/pension_chart_line_6"},
    ),
    # Worksheet for line 31400, line 7: "Annuity payments from line 12900 of your return (box 16 of
    # all your T4RSP slips) only if you were 65 years of age or older on December 31, 2025, or you
    # received the payments because of the death of your spouse or common-law partner". The gate is
    # the caller's 0 or 1 count, and the payments count once when it is 1.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/pension_annuity_payments",
            "count": "ca/pension_annuity_conditions_met_checked",
        },
        produces={"output": "ca/pension_chart_line_7"},
    ),
    # Worksheet for line 31400, line 8: "Line 6 plus line 7".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/pension_chart_line_6",
                "ca/pension_chart_line_7",
            )
        },
        produces={"output": "ca/pension_chart_line_8"},
    ),
    # Worksheet for line 31400, the last line: "Enter on line 31400 of your return whichever amount
    # is less: line 8 or $2,000." (maximum $2,000, T1 guide 5000-G and the T1 line 97).
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/pension_income_maximum"},
        consumes={"base": "ca/pension_chart_line_8"},
        produces={"output": "ca/pension_worksheet_amount"},
    ),
}

WIRING = {
    (
        Sum,
        frozenset({EMPLOYMENT_INCOME, OTHER_EMPLOYMENT_INCOME}),
        frozenset({CANADA_EMPLOYMENT_AMOUNT_INCOME}),
    ),
    (
        CappedAmount,
        frozenset({CANADA_EMPLOYMENT_AMOUNT_INCOME}),
        frozenset({CANADA_EMPLOYMENT_AMOUNT}),
    ),
    (
        TimesCount,
        frozenset({SELF_EMPLOYED_CPP_BASE_CREDIT, CPP_PART_4_COMPLETED_CHECKED}),
        frozenset({CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT}),
    ),
    (
        TimesCount,
        frozenset({CPP_PART_5_LINE_70, CPP_PART_5_COMPLETED_CHECKED}),
        frozenset({CPP_PART_5_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT}),
    ),
    (
        Sum,
        frozenset(
            {
                CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
                CPP_PART_5_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
                RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            }
        ),
        frozenset({CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS}),
    ),
    (
        TimesCount,
        frozenset({SELF_EMPLOYED_EI_PREMIUMS, EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED}),
        frozenset({EI_PREMIUMS_ON_SELF_EMPLOYMENT}),
    ),
    (
        MoreThanPerUnit,
        frozenset({CANADIAN_TUITION_FEES, CANADIAN_TUITION_INSTITUTIONS}),
        frozenset({CANADIAN_TUITION_FEES_CHECKED}),
    ),
    (
        ApplyRate,
        frozenset({CANADIAN_TUITION_FEES_CHECKED}),
        frozenset({CANADA_TRAINING_CREDIT_BASIS}),
    ),
    (
        LesserOf,
        frozenset({CANADA_TRAINING_CREDIT_BASIS, CANADA_TRAINING_CREDIT_LIMIT}),
        frozenset({CANADA_TRAINING_CREDIT_MAXIMUM}),
    ),
    (
        AtMost,
        frozenset({CANADA_TRAINING_CREDIT_CLAIMED, CANADA_TRAINING_CREDIT_MAXIMUM}),
        frozenset({CANADA_TRAINING_CREDIT}),
    ),
    (
        Subtract,
        frozenset({CANADIAN_TUITION_FEES_CHECKED, CANADA_TRAINING_CREDIT}),
        frozenset({CANADIAN_TUITION_AVAILABLE}),
    ),
    (
        Sum,
        frozenset({CANADIAN_TUITION_AVAILABLE, FOREIGN_TUITION_FEES}),
        frozenset({CURRENT_YEAR_TUITION_AVAILABLE}),
    ),
    (
        Sum,
        frozenset({CURRENT_YEAR_TUITION_AVAILABLE, UNUSED_TUITION_FROM_2024}),
        frozenset({TOTAL_TUITION_AVAILABLE}),
    ),
    (
        AmountOrDividedByRate,
        frozenset({TAXABLE_INCOME, FEDERAL_BASIC_TAX}),
        frozenset({TUITION_INCOME_BASE}),
    ),
    (
        Sum,
        frozenset(
            {
                BASIC_PERSONAL_AMOUNT,
                AGE_AMOUNT,
                SPOUSE_AMOUNT,
                ELIGIBLE_DEPENDANT_AMOUNT,
                CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT,
                CAREGIVER_AMOUNT,
                INFIRM_CHILDREN_AMOUNT,
                CPP_BASE_CONTRIBUTIONS_ON_RETURN,
                CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
                EI_PREMIUMS,
                EI_PREMIUMS_ON_SELF_EMPLOYMENT,
                VOLUNTEER_FIREFIGHTERS_CREDIT,
                SEARCH_AND_RESCUE_CREDIT,
                CANADA_EMPLOYMENT_AMOUNT,
                HOME_BUYERS_CREDIT,
                HOME_ACCESSIBILITY_CREDIT,
                ADOPTION_CREDIT,
                PENSION_INCOME_CREDIT,
                DISABILITY_AMOUNT_FOR_SELF,
                DISABILITY_TRANSFERRED_AMOUNT,
            }
        ),
        frozenset({CREDIT_AMOUNTS_SUBTOTAL}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({TUITION_INCOME_WITH_TOSI, CREDIT_AMOUNTS_SUBTOTAL}),
        frozenset({TUITION_INCOME_LESS_CREDITS}),
    ),
    (
        LesserOf,
        frozenset({UNUSED_TUITION_FROM_2024, TUITION_INCOME_LESS_CREDITS}),
        frozenset({UNUSED_TUITION_CLAIMED}),
    ),
    (
        Subtract,
        frozenset({TUITION_INCOME_LESS_CREDITS, UNUSED_TUITION_CLAIMED}),
        frozenset({TUITION_INCOME_REMAINING}),
    ),
    (
        LesserOf,
        frozenset({CURRENT_YEAR_TUITION_AVAILABLE, TUITION_INCOME_REMAINING}),
        frozenset({CURRENT_YEAR_TUITION_CLAIMED}),
    ),
    (
        Sum,
        frozenset({UNUSED_TUITION_CLAIMED, CURRENT_YEAR_TUITION_CLAIMED}),
        frozenset({FEDERAL_TUITION_AMOUNT}),
    ),
    (
        Subtract,
        frozenset({TOTAL_TUITION_AVAILABLE, FEDERAL_TUITION_AMOUNT}),
        frozenset({UNUSED_FEDERAL_TUITION}),
    ),
    (
        CappedAmount,
        frozenset({CURRENT_YEAR_TUITION_AVAILABLE}),
        frozenset({TUITION_TRANSFER_LIMIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({TUITION_TRANSFER_LIMIT, CURRENT_YEAR_TUITION_CLAIMED}),
        frozenset({TUITION_AVAILABLE_TO_TRANSFER}),
    ),
    (
        AtMost,
        frozenset({TUITION_TRANSFER_ELECTED, TUITION_AVAILABLE_TO_TRANSFER}),
        frozenset({TUITION_TRANSFERRED}),
    ),
    (
        PerUnitAmount,
        frozenset({TUITION_TRANSFER_STUDENTS}),
        frozenset({TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM}),
    ),
    (
        AtMost,
        frozenset({TUITION_TRANSFERRED_FROM_CHILD, TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM}),
        frozenset({TUITION_TRANSFERRED_FROM_CHILD_CHECKED}),
    ),
    (
        Subtract,
        frozenset({UNUSED_FEDERAL_TUITION, TUITION_TRANSFERRED}),
        frozenset({TUITION_CARRIED_FORWARD}),
    ),
    (CreditAmount, frozenset(), frozenset({SPOUSE_RETURN_AGE_AMOUNT_MAXIMUM})),
    (
        AtMost,
        frozenset({SPOUSE_RETURN_AGE_AMOUNT, SPOUSE_RETURN_AGE_AMOUNT_MAXIMUM}),
        frozenset({SPOUSE_RETURN_AGE_AMOUNT_CHECKED}),
    ),
    (CreditAmount, frozenset(), frozenset({SPOUSE_RETURN_PENSION_INCOME_AMOUNT_MAXIMUM})),
    (
        AtMost,
        frozenset(
            {SPOUSE_RETURN_PENSION_INCOME_AMOUNT, SPOUSE_RETURN_PENSION_INCOME_AMOUNT_MAXIMUM}
        ),
        frozenset({SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED}),
    ),
    (CreditAmount, frozenset(), frozenset({SPOUSE_DESIGNATED_TUITION_MAXIMUM})),
    (
        AtMost,
        frozenset({SPOUSE_DESIGNATED_TUITION, SPOUSE_DESIGNATED_TUITION_MAXIMUM}),
        frozenset({SPOUSE_DESIGNATED_TUITION_CHECKED}),
    ),
    (CreditAmount, frozenset(), frozenset({SPOUSE_RETURN_DISABILITY_AMOUNT_MAXIMUM})),
    (
        AtMost,
        frozenset({SPOUSE_RETURN_DISABILITY_AMOUNT, SPOUSE_RETURN_DISABILITY_AMOUNT_MAXIMUM}),
        frozenset({SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                SPOUSE_RETURN_AGE_AMOUNT_CHECKED,
                SPOUSE_RETURN_INFIRM_CHILDREN_AMOUNT,
                SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED,
                SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED,
                SPOUSE_DESIGNATED_TUITION_CHECKED,
            }
        ),
        frozenset({SPOUSE_TRANSFERABLE_AMOUNTS}),
    ),
    (
        AmountOrDividedByRate,
        frozenset({SPOUSE_RETURN_TAXABLE_INCOME, SPOUSE_RETURN_FEDERAL_BASIC_TAX}),
        frozenset({SPOUSE_INCOME_FOR_TRANSFER}),
    ),
    (CreditAmount, frozenset(), frozenset({SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_MAXIMUM})),
    (
        AtMost,
        frozenset(
            {SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT, SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_MAXIMUM}
        ),
        frozenset({SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED,
                SPOUSE_RETURN_LINE_96,
                SPOUSE_RETURN_FEDERAL_TUITION_AMOUNT,
            }
        ),
        frozenset({SPOUSE_CREDITS_USED}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({SPOUSE_INCOME_FOR_TRANSFER, SPOUSE_CREDITS_USED}),
        frozenset({SPOUSE_ADJUSTED_TAXABLE_INCOME}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({SPOUSE_TRANSFERABLE_AMOUNTS, SPOUSE_ADJUSTED_TAXABLE_INCOME}),
        frozenset({SPOUSE_UNUSED_AMOUNTS}),
    ),
    (
        TimesCount,
        frozenset({SPOUSE_UNUSED_AMOUNTS, SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED}),
        frozenset({AMOUNTS_TRANSFERRED_FROM_SPOUSE}),
    ),
    (
        Sum,
        frozenset(
            {
                BASIC_PERSONAL_AMOUNT,
                AGE_AMOUNT,
                SPOUSE_AMOUNT,
                ELIGIBLE_DEPENDANT_AMOUNT,
                CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT,
                CAREGIVER_AMOUNT,
                INFIRM_CHILDREN_AMOUNT,
                CPP_BASE_CONTRIBUTIONS_ON_RETURN,
                CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
                EI_PREMIUMS,
                EI_PREMIUMS_ON_SELF_EMPLOYMENT,
                VOLUNTEER_FIREFIGHTERS_CREDIT,
                SEARCH_AND_RESCUE_CREDIT,
                CANADA_EMPLOYMENT_AMOUNT,
                HOME_BUYERS_CREDIT,
                HOME_ACCESSIBILITY_CREDIT,
                ADOPTION_CREDIT,
                PENSION_INCOME_CREDIT,
                MEDICAL_CLAIM,
                DISABILITY_AMOUNT_FOR_SELF,
                DISABILITY_TRANSFERRED_AMOUNT,
                STUDENT_LOAN_INTEREST,
                FEDERAL_TUITION_AMOUNT,
                TUITION_TRANSFERRED_FROM_CHILD_CHECKED,
                AMOUNTS_TRANSFERRED_FROM_SPOUSE,
            }
        ),
        frozenset({NON_REFUNDABLE_CREDIT_AMOUNTS}),
    ),
    (
        ApplyRate,
        frozenset({NON_REFUNDABLE_CREDIT_AMOUNTS}),
        frozenset({CREDIT_AMOUNTS_AT_CREDIT_RATE}),
    ),
    (
        LesserOf,
        frozenset({DEPRECIABLE_GIFT_NET_PROCEEDS, DEPRECIABLE_GIFT_CAPITAL_COST}),
        frozenset({DEPRECIABLE_GIFT_PROCEEDS_OR_COST}),
    ),
    (
        LesserOf,
        frozenset({DEPRECIABLE_GIFT_RECAPTURED_DEPRECIATION, DEPRECIABLE_GIFT_PROCEEDS_OR_COST}),
        frozenset({DEPRECIABLE_GIFTS}),
    ),
    (
        AtMost,
        frozenset({CAPITAL_GIFT_GAINS_DEDUCTION, CAPITAL_GIFT_TAXABLE_GAINS}),
        frozenset({CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED}),
    ),
    (
        Subtract,
        frozenset({CAPITAL_GIFT_TAXABLE_GAINS, CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED}),
        frozenset({CAPITAL_PROPERTY_GIFTS}),
    ),
    (
        Sum,
        frozenset(
            {
                CHARITABLE_DONATIONS,
                GOVERNMENT_DONATIONS,
                UNIVERSITY_DONATIONS_OUTSIDE_CANADA,
                FOREIGN_CHARITY_DONATIONS,
            }
        ),
        frozenset({TOTAL_CHARITABLE_DONATIONS}),
    ),
    (ApplyRate, frozenset({NET_INCOME}), frozenset({DONATION_LIMIT_ON_NET_INCOME})),
    (
        Sum,
        frozenset({DEPRECIABLE_GIFTS, CAPITAL_PROPERTY_GIFTS}),
        frozenset({CAPITAL_GIFTS_TOTAL}),
    ),
    (ApplyRate, frozenset({CAPITAL_GIFTS_TOTAL}), frozenset({CAPITAL_GIFTS_LIMIT_ADDITION})),
    (
        Sum,
        frozenset({DONATION_LIMIT_ON_NET_INCOME, CAPITAL_GIFTS_LIMIT_ADDITION}),
        frozenset({DONATION_LIMIT_WITH_CAPITAL_GIFTS}),
    ),
    (
        LesserOf,
        frozenset({NET_INCOME, DONATION_LIMIT_WITH_CAPITAL_GIFTS}),
        frozenset({CHARITABLE_DONATIONS_LIMIT}),
    ),
    (
        LesserOf,
        frozenset({TOTAL_CHARITABLE_DONATIONS, CHARITABLE_DONATIONS_LIMIT}),
        frozenset({CHARITABLE_DONATIONS_CLAIMED}),
    ),
    (
        Sum,
        frozenset({CHARITABLE_DONATIONS_CLAIMED, ECOLOGICAL_AND_CULTURAL_GIFTS}),
        frozenset({DONATIONS_AND_GIFTS_TOTAL}),
    ),
    (CreditAmount, frozenset(), frozenset({DONATION_FIRST_TIER_MAXIMUM})),
    (
        LesserOf,
        frozenset({DONATIONS_AND_GIFTS_TOTAL, DONATION_FIRST_TIER_MAXIMUM}),
        frozenset({DONATIONS_FIRST_TIER}),
    ),
    (
        Subtract,
        frozenset({DONATIONS_AND_GIFTS_TOTAL, DONATIONS_FIRST_TIER}),
        frozenset({DONATIONS_OVER_FIRST_TIER}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({DONATIONS_OVER_FIRST_TIER, ECOLOGICAL_GIFTS_BEFORE_2016}),
        frozenset({DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS}),
    ),
    (CreditAmount, frozenset(), frozenset({DONATION_HIGH_INCOME_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({TAXABLE_INCOME, DONATION_HIGH_INCOME_THRESHOLD}),
        frozenset({TAXABLE_INCOME_OVER_DONATION_THRESHOLD}),
    ),
    (
        LesserOf,
        frozenset(
            {DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS, TAXABLE_INCOME_OVER_DONATION_THRESHOLD}
        ),
        frozenset({HIGH_INCOME_DONATIONS}),
    ),
    (ApplyRate, frozenset({HIGH_INCOME_DONATIONS}), frozenset({HIGH_INCOME_DONATION_CREDIT})),
    (
        Subtract,
        frozenset({DONATIONS_OVER_FIRST_TIER, HIGH_INCOME_DONATIONS}),
        frozenset({REGULAR_RATE_DONATIONS}),
    ),
    (ApplyRate, frozenset({REGULAR_RATE_DONATIONS}), frozenset({REGULAR_RATE_DONATION_CREDIT})),
    (ApplyRate, frozenset({DONATIONS_FIRST_TIER}), frozenset({FIRST_TIER_DONATION_CREDIT})),
    (
        Sum,
        frozenset(
            {
                HIGH_INCOME_DONATION_CREDIT,
                REGULAR_RATE_DONATION_CREDIT,
                FIRST_TIER_DONATION_CREDIT,
            }
        ),
        frozenset({DONATIONS_AND_GIFTS_CREDIT}),
    ),
    (
        Sum,
        frozenset({CREDIT_AMOUNTS_AT_CREDIT_RATE, FIRST_TIER_DONATION_CREDIT}),
        frozenset({TOP_UP_CREDITS_BASE}),
    ),
    (CreditAmount, frozenset(), frozenset({TOP_UP_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({TOP_UP_CREDITS_BASE, TOP_UP_THRESHOLD}),
        frozenset({TOP_UP_EXCESS}),
    ),
    (ApplyRate, frozenset({TOP_UP_EXCESS}), frozenset({TOP_UP_TAX_CREDIT})),
    (
        Sum,
        frozenset({CREDIT_AMOUNTS_AT_CREDIT_RATE, DONATIONS_AND_GIFTS_CREDIT, TOP_UP_TAX_CREDIT}),
        frozenset({NON_REFUNDABLE_TAX_CREDITS}),
    ),
    (ApplyRate, frozenset({TOTAL_SPLIT_INCOME}), frozenset({FEDERAL_TAX_ON_SPLIT_INCOME})),
    (
        DividedByRate,
        frozenset({FEDERAL_TAX_ON_SPLIT_INCOME}),
        frozenset({TOSI_ADJUSTED_TAXABLE_INCOME}),
    ),
    (
        Sum,
        frozenset({TUITION_INCOME_BASE, TOSI_ADJUSTED_TAXABLE_INCOME}),
        frozenset({TUITION_INCOME_WITH_TOSI}),
    ),
    (
        Sum,
        frozenset({FEDERAL_BASIC_TAX, FEDERAL_TAX_ON_SPLIT_INCOME}),
        frozenset({FEDERAL_TAX_WITH_SPLIT_INCOME}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FEDERAL_TAX_WITH_SPLIT_INCOME, CREDITS_AGAINST_BASIC_FEDERAL_TAX}),
        frozenset({FEDERAL_TAX_AFTER_CREDITS}),
    ),
    (
        ApplyRate,
        frozenset({ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT}),
        frozenset({ITC_RECAPTURE_AT_15_PERCENT}),
    ),
    (
        ApplyRate,
        frozenset({ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT}),
        frozenset({ITC_RECAPTURE_AT_20_PERCENT}),
    ),
    (
        Sum,
        frozenset({ITC_RECAPTURE_AT_15_PERCENT, ITC_RECAPTURE_AT_20_PERCENT}),
        frozenset({ITC_RECAPTURE}),
    ),
    (
        AtMost,
        frozenset({EXEMPT_INCOME_DEDUCTIONS, ADDITIONAL_DEDUCTIONS_TOTAL}),
        frozenset({EXEMPT_INCOME_DEDUCTIONS_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION,
                SECURITY_OPTIONS_DEDUCTIONS,
                OTHER_PAYMENTS_DEDUCTION,
                NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
                QBT_CAPITAL_GAINS_DEDUCTION,
                CAPITAL_GAINS_DEDUCTION,
                EXEMPT_INCOME_DEDUCTIONS_CHECKED,
            }
        ),
        frozenset({FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS}),
    ),
    (
        Subtract,
        frozenset({NET_INCOME_BEFORE_ADJUSTMENTS, SOCIAL_BENEFITS_REPAYMENT}),
        frozenset({FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME}),
    ),
    (
        Sum,
        frozenset({FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME, TOTAL_SPLIT_INCOME}),
        frozenset({FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME}),
    ),
    (
        Subtract,
        frozenset(
            {
                FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME,
                FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS,
            }
        ),
        frozenset({FOREIGN_TAX_CREDIT_NET_INCOME}),
    ),
    (
        Sum,
        frozenset({FEDERAL_TAX_AFTER_CREDITS, DIVIDEND_TAX_CREDIT}),
        frozenset({BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT}),
    ),
    (
        Sum,
        frozenset({BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT, FEDERAL_SURTAX_OUTSIDE_CANADA}),
        frozenset({BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX, FIRST_NATIONS_ABATEMENT}),
        frozenset({FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX}),
    ),
    (
        ForeignPropertyTaxOverLimit,
        frozenset({FOREIGN_TAX_COUNTRIES}),
        frozenset({FOREIGN_PROPERTY_TAX_OVER_LIMIT}),
    ),
    (
        ForeignSurtaxAllocatedTotal,
        frozenset({FOREIGN_TAX_COUNTRIES}),
        frozenset({FOREIGN_SURTAX_ALLOCATED_TOTAL}),
    ),
    (
        SumNotBelowZero,
        frozenset({FEDERAL_SURTAX_OUTSIDE_CANADA}),
        frozenset({FOREIGN_SURTAX_LIMIT}),
    ),
    (
        AtMost,
        frozenset({FOREIGN_SURTAX_ALLOCATED_TOTAL, FOREIGN_SURTAX_LIMIT}),
        frozenset({FOREIGN_SURTAX_ALLOCATED_TOTAL_CHECKED}),
    ),
    (
        ForeignNonBusinessTaxCredit,
        frozenset(
            {
                FOREIGN_TAX_COUNTRIES,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
            }
        ),
        frozenset({FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT, FOREIGN_TAX_CREDIT_SHEETS}),
    ),
    (
        ForeignBusinessTaxCreditLine4,
        frozenset(
            {
                FOREIGN_TAX_CREDIT_SHEETS,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
            }
        ),
        frozenset({FOREIGN_BUSINESS_TAX_CREDIT_LINE_4}),
    ),
    (
        ForeignBusinessTaxCreditLine5,
        frozenset(
            {
                FOREIGN_TAX_CREDIT_SHEETS,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
            }
        ),
        frozenset({FOREIGN_BUSINESS_TAX_CREDIT_LINE_5}),
    ),
    (
        ForeignBusinessTaxCreditLine7,
        frozenset(
            {
                FOREIGN_TAX_CREDIT_SHEETS,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
            }
        ),
        frozenset({FOREIGN_BUSINESS_TAX_CREDIT_LINE_7}),
    ),
    (
        ForeignBusinessTaxCreditLine8,
        frozenset(
            {
                FOREIGN_TAX_CREDIT_SHEETS,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
            }
        ),
        frozenset({FOREIGN_BUSINESS_TAX_CREDIT_LINE_8}),
    ),
    (
        ForeignBusinessTaxCreditLine10,
        frozenset(
            {
                FOREIGN_TAX_CREDIT_SHEETS,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
            }
        ),
        frozenset({FOREIGN_BUSINESS_TAX_CREDIT_LINE_10}),
    ),
    (
        ForeignBusinessTaxCreditLine11,
        frozenset(
            {
                FOREIGN_TAX_CREDIT_SHEETS,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
            }
        ),
        frozenset({FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT}),
    ),
    (
        Sum,
        frozenset({FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT, FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT}),
        frozenset({FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT}),
    ),
    (
        CountByConditions,
        frozenset({FEDERAL_TAX_ON_SPLIT_INCOME}),
        frozenset({T2203_HAS_TAX_ON_SPLIT_INCOME}),
    ),
    (
        TimesCount,
        frozenset({SPLIT_INCOME_LINE_22, T2203_HAS_TAX_ON_SPLIT_INCOME}),
        frozenset({T2203_LINE_5}),
    ),
    (GreaterOf, frozenset({FEDERAL_TAX_AFTER_CREDITS, T2203_LINE_5}), frozenset({T2203_LINE_6})),
    (CreditAmount, frozenset(), frozenset({AMT_T2203_COLUMN_5_PERCENTAGE_MAXIMUM})),
    (
        AtMost,
        frozenset({AMT_T2203_COLUMN_5_PERCENTAGE, AMT_T2203_COLUMN_5_PERCENTAGE_MAXIMUM}),
        frozenset({AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED}),
    ),
    (
        ApplyPercentage,
        frozenset({T2203_LINE_6, AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED}),
        frozenset({T2203_LINE_8}),
    ),
    (ApplyRate, frozenset({T2203_LINE_8}), frozenset({T2203_FEDERAL_SURTAX_OUTSIDE_CANADA})),
    (
        ChooseByCount,
        frozenset(
            {AMT_SUBJECT_TO_MINIMUM_TAX, T2203_FEDERAL_SURTAX_OUTSIDE_CANADA, AMT_FEDERAL_SURTAX}
        ),
        frozenset({FEDERAL_SURTAX_OUTSIDE_CANADA}),
    ),
    (
        Sum,
        frozenset({FEDERAL_TAX_AFTER_CREDITS, FEDERAL_SURTAX_OUTSIDE_CANADA}),
        frozenset({FEDERAL_TAX_WITH_SURTAX}),
    ),
    (
        LesserOfWhenPositive,
        frozenset({FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT, FEDERAL_TAX_WITH_SURTAX}),
        frozenset({FEDERAL_FOREIGN_TAX_CREDIT}),
    ),
    (
        Subtract,
        frozenset({FEDERAL_TAX_WITH_SURTAX, FEDERAL_FOREIGN_TAX_CREDIT}),
        frozenset({FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT}),
    ),
    (
        Sum,
        frozenset({FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT, ITC_RECAPTURE}),
        frozenset({FEDERAL_TAX_WITH_ITC_RECAPTURE}),
    ),
    (
        PerUnitAmount,
        frozenset({VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED}),
        frozenset({VOLUNTEER_FIREFIGHTERS_CREDIT}),
    ),
    (
        PerUnitAmount,
        frozenset({SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED}),
        frozenset({SEARCH_AND_RESCUE_CREDIT}),
    ),
    (
        Sum,
        frozenset({VOLUNTEER_FIREFIGHTERS_CREDIT, SEARCH_AND_RESCUE_CREDIT}),
        frozenset({VOLUNTEER_CREDITS_CLAIMED}),
    ),
    (CreditAmount, frozenset(), frozenset({VOLUNTEER_AMOUNT_MAXIMUM})),
    (
        AtMost,
        frozenset({VOLUNTEER_CREDITS_CLAIMED, VOLUNTEER_AMOUNT_MAXIMUM}),
        frozenset({VOLUNTEER_CREDITS_CHECKED}),
    ),
    (CreditAmount, frozenset(), frozenset({HOME_BUYERS_MAXIMUM})),
    (AtMost, frozenset({HOME_BUYERS_CLAIM, HOME_BUYERS_MAXIMUM}), frozenset({HOME_BUYERS_CREDIT})),
    (
        CappedAmount,
        frozenset({HOME_ACCESSIBILITY_EXPENSES}),
        frozenset({HOME_ACCESSIBILITY_LINE_2}),
    ),
    (
        AtMost,
        frozenset({HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS, HOME_ACCESSIBILITY_LINE_2}),
        frozenset({HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED}),
    ),
    (
        Subtract,
        frozenset({HOME_ACCESSIBILITY_LINE_2, HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED}),
        frozenset({HOME_ACCESSIBILITY_CREDIT}),
    ),
    (RecordTotal, frozenset({ADOPTION_EXPENSE_CHILDREN}), frozenset({ADOPTION_CREDIT})),
    (
        AtMost,
        frozenset({PENSION_FOREIGN_INCOME, ADDITIONAL_DEDUCTIONS_TOTAL}),
        frozenset({PENSION_FOREIGN_INCOME_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {PENSION_FOREIGN_INCOME_CHECKED, PENSION_US_IRA_INCOME, PENSION_RRIF_TRANSFERRED}
        ),
        frozenset({PENSION_CHART_LINE_5}),
    ),
    (
        SumNotBelowZero,
        frozenset({OTHER_PENSIONS_AND_SUPERANNUATION, T2205_ON_LINE_11500}),
        frozenset({PENSION_CHART_LINE_1}),
    ),
    (
        AtMost,
        frozenset({PENSION_CHART_LINE_5, PENSION_CHART_LINE_1}),
        frozenset({PENSION_CHART_LINE_5_CHECKED}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({PENSION_CHART_LINE_1, PENSION_CHART_LINE_5_CHECKED}),
        frozenset({PENSION_CHART_LINE_6}),
    ),
    (
        TimesCount,
        frozenset({PENSION_ANNUITY_PAYMENTS, PENSION_ANNUITY_CONDITIONS_MET_CHECKED}),
        frozenset({PENSION_CHART_LINE_7}),
    ),
    (
        Sum,
        frozenset({PENSION_CHART_LINE_6, PENSION_CHART_LINE_7}),
        frozenset({PENSION_CHART_LINE_8}),
    ),
    (CappedAmount, frozenset({PENSION_CHART_LINE_8}), frozenset({PENSION_WORKSHEET_AMOUNT})),
}
