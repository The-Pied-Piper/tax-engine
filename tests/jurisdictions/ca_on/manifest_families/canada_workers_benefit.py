"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.capped_amount import CappedAmount
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_calculator.jurisdictions.ca.capabilities.count_at_least import CountAtLeast
from tax_calculator.jurisdictions.ca.capabilities.count_at_most import CountAtMost
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca.catalog import (
    ACWB_BASIC_PAID,
    ACWB_DISABILITY_SUPPLEMENT_PAID,
    ACWB_LINE_46_APPLIES,
    ACWB_LINES_44_AND_45,
    ACWB_PAID,
    ACWB_PAID_TO_SPOUSE,
    ACWB_PAID_TO_YOU,
    ADJUSTED_FAMILY_NET_INCOME,
    ADVANCED_CANADA_WORKERS_BENEFIT,
    AGED_19_OR_OLDER_AT_END_OF_2025,
    AGED_19_OR_OLDER_AT_END_OF_2025_CHECKED,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_BEFORE_CONDITIONS,
    CANADA_WORKERS_BENEFIT_LINE_28,
    CANADA_WORKERS_BENEFIT_LINE_41,
    CANADA_WORKERS_BENEFIT_LINE_42,
    CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
    CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT,
    CONFINED_TO_PRISON_FOR_90_DAYS,
    CONFINED_TO_PRISON_FOR_90_DAYS_CHECKED,
    CWB_BEFORE_REDUCTION_WITH_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT,
    CWB_CLAIMED,
    CWB_CLAIMING_BASIC,
    CWB_CLAIMING_BASIC_CHECKED,
    CWB_DISABILITY_REDUCTION,
    CWB_DISABILITY_REDUCTION_BY_SPOUSE,
    CWB_DISABILITY_REDUCTION_BY_STATUS,
    CWB_DISABILITY_REDUCTION_WITH_DEPENDANT,
    CWB_DISABILITY_REDUCTION_WITH_DTC_SPOUSE,
    CWB_DISABILITY_REDUCTION_WITHOUT_DEPENDANT,
    CWB_DISABILITY_SUPPLEMENT,
    CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION,
    CWB_DTC_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED,
    CWB_ELIGIBLE,
    CWB_ELIGIBLE_DEPENDANTS,
    CWB_ELIGIBLE_DEPENDANTS_CHECKED,
    CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC,
    CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC_CHECKED,
    CWB_ELIGIBLE_SPOUSES,
    CWB_ELIGIBLE_SPOUSES_CHECKED,
    CWB_EMPLOYMENT_INCOME,
    CWB_FAMILY_NET_INCOME_LINE_10,
    CWB_FAMILY_NET_INCOME_LINE_12,
    CWB_FAMILY_NET_INCOME_LINE_13,
    CWB_FAMILY_WORKING_INCOME,
    CWB_INCLUDE_TAX_EXEMPT_INCOME,
    CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED,
    CWB_LINE_28_BY_SPOUSE,
    CWB_REDUCTION_WITH_DEPENDANT,
    CWB_REDUCTION_WITHOUT_DEPENDANT,
    CWB_SECONDARY_EARNER_EXEMPTION,
    CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM,
    CWB_SECONDARY_EARNER_SPOUSES,
    CWB_SECONDARY_EARNER_YOURS,
    CWB_SPOUSE_CLAIMING_BASIC,
    CWB_SPOUSE_CLAIMING_BASIC_CHECKED,
    CWB_SPOUSE_CLAIMING_BASIC_WITH_SPOUSE_CHECKED,
    CWB_SPOUSE_EMPLOYMENT_INCOME,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_10,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12_BEFORE_ELIGIBILITY,
    CWB_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED,
    CWB_SPOUSE_NET_EXEMPT_INCOME,
    CWB_SPOUSE_SELF_EMPLOYMENT_INCOME,
    CWB_SPOUSE_TAX_EXEMPT_NET_INCOME_ELECTED,
    CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME,
    CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED,
    CWB_SPOUSE_TAXABLE_SCHOLARSHIPS,
    CWB_SPOUSE_UCCB_AND_RDSP_INCOME,
    CWB_SPOUSE_WORKING_INCOME,
    CWB_SPOUSE_WORKING_INCOME_BEFORE_ELIGIBILITY,
    CWB_T90_EXEMPT_WORKING_INCOME_TOTAL,
    CWB_T90_NET_EXEMPT_INCOME_TOTAL,
    CWB_TAX_EXEMPT_NET_INCOME,
    CWB_TAX_EXEMPT_NET_INCOME_BEFORE_ELECTION,
    CWB_TAX_EXEMPT_WORKING_INCOME,
    CWB_TAX_EXEMPT_WORKING_INCOME_BEFORE_ELECTION,
    CWB_WORKING_INCOME_LESS_SPOUSE,
    ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED,
    EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME,
    EMPLOYMENT_INCOME,
    EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY,
    EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY_CHECKED,
    FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS,
    FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS_CHECKED,
    MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME,
    RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025,
    RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025_CHECKED,
    RESIDENT_IN_CANADA_THROUGHOUT_2025_CHECKED,
    SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
    SPOUSE_RDSP_INCOME,
    SPOUSE_RDSP_INCOME_REPAYMENT,
    SPOUSE_UCCB_REPAYMENT,
    SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT,
    T90_EXEMPT_WORKING_INCOME,
    T90_NET_EXEMPT_INCOME,
    TAXABLE_SCHOLARSHIPS,
    TOSI_ADJUSTED_NET_INCOME,
    UCCB_AND_RDSP_INCOME,
    UCCB_AND_RDSP_INCOME_REPAYMENTS,
    WORKING_INCOME,
)

# The record kinds read by the two record totals: the one record of each export of Form T90.
T90_EXEMPT_WORKING_INCOME_PER_FORM = RecordListKind(
    "ca/t90.t90_exempt_working_income", fields=(T90_EXEMPT_WORKING_INCOME,)
)
T90_NET_EXEMPT_INCOME_PER_FORM = RecordListKind(
    "ca/t90.t90_net_exempt_income", fields=(T90_NET_EXEMPT_INCOME,)
)

INPUTS = frozenset(
    {
        "ca/cwb_eligible_dependants",
        "ca/cwb_eligible_spouses",
        "ca/cwb_spouse_employment_income",
        "ca/cwb_spouse_taxable_scholarships",
        "ca/cwb_spouse_self_employment_income",
        "ca/acwb_paid_to_you",
        "ca/acwb_paid_to_spouse",
        "ca/acwb_disability_supplement_paid",
        "ca/aged_19_or_older_at_end_of_2025",
        "ca/resided_with_spouse_or_child_at_end_of_2025",
        "ca/full_time_student_for_more_than_13_weeks",
        "ca/confined_to_prison_for_90_days",
        "ca/exempt_as_foreign_officer_or_family",
        # Schedule 6 line 38105 "Are you choosing to include tax-exempt income to calculate the
        # CWB?"
        "ca/cwb_include_tax_exempt_income",
        # Schedule 6 line 38104 "Is your eligible spouse eligible for the DTC for themselves?"
        "ca/cwb_eligible_spouse_eligible_for_dtc",
        # Schedule 6 line 38102 "Are you claiming the basic CWB?"
        "ca/cwb_claiming_basic",
        # Schedule 6 Step 4: an eligible spouse claiming the basic CWB for the filer.
        "ca/cwb_spouse_claiming_basic",
        # Column 2 line 4 (form number 38107) and line 8 (form number 38109) of the spouse.
        "ca/cwb_spouse_tax_exempt_working_income",
        "ca/cwb_spouse_net_exempt_income",
    }
)

OUTPUTS = frozenset({"ca/cwb_spouse_for_eligible_spouse_checked"})

ELIGIBILITY_ANSWERS = (
    "aged_19_or_older_at_end_of_2025",
    "resided_with_spouse_or_child_at_end_of_2025",
    "full_time_student_for_more_than_13_weeks",
    "confined_to_prison_for_90_days",
    "exempt_as_foreign_officer_or_family",
)

STEPS = {
    # Schedule 6 line 1 "Employment income and other employment income from line 10100 and line
    # 10400 of the return": the two amounts added, as line 1 of the medical supplement's
    # worksheet adds them.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/employment_income", "ca/other_employment_income")},
        produces={"output": "ca/cwb_employment_income"},
    ),
    # Schedule 6 line 5 "Add lines 1 to 4. Enter the result, even if it is "0". Working
    # income": line 1 (the step above), line 2 "Taxable scholarships, fellowships, bursaries, and
    # artists' project grants from line 13010 of the return" (ca/taxable_scholarships), line 3
    # "Total self-employment income from lines 13500, 13700, 13900, 14100, and 14300 of the
    # return (excluding losses) (Note 2)" (ca/medical_supplement_self_employment_income) and line 4
    # "Tax-exempt working income earned on a reserve" (ca/cwb_tax_exempt_working_income, zero unless
    # the election of line 38105 is yes): column 1 ("You") of Part A.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cwb_employment_income",
                "ca/taxable_scholarships",
                "ca/medical_supplement_self_employment_income",
                "ca/cwb_tax_exempt_working_income",
            )
        },
        produces={"output": "ca/working_income"},
    ),
    # Schedule 6 line 4 "Tax-exempt working income earned on a reserve (from line 10000 of Form T90,
    # Income Exempt from Tax under the Indian Act) (Note 1) and the tax-exempt portion of any
    # allowance received as an emergency volunteer (from line 10105 of the return)": the T90 line 4
    # export ("Total exempt working income 10000") and the T1 line 10105 amount, before the
    # election.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t90.t90_exempt_working_income"},
        produces={"output": "ca/cwb_t90_exempt_working_income_total"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cwb_t90_exempt_working_income_total",
                "ca/emergency_services_volunteer_exempt_income",
            )
        },
        produces={"output": "ca/cwb_tax_exempt_working_income_before_election"},
    ),
    # Schedule 6 line 38105 "Are you choosing to include tax-exempt income to calculate the CWB?
    # (Note 1) 1 Yes or 2 No", a count of 1 or 0, checked before the election reads it. A count of
    # 2 or more is refused, not capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/cwb_include_tax_exempt_income"},
        produces={"output": "ca/cwb_include_tax_exempt_income_checked"},
    ),
    # Schedule 6 line 4 counts only when the election is yes (line 38105, the checked answer, 1 or
    # 0): with no election the T90 figures are ignored and no refusal is made. Note 1 is met by the
    # one answer, which covers both columns and both parts.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cwb_tax_exempt_working_income_before_election",
            "count": "ca/cwb_include_tax_exempt_income_checked",
        },
        produces={"output": "ca/cwb_tax_exempt_working_income"},
    ),
    # Schedule 6 line 8 "Total of net exempt income earned on a reserve (line 10026 of Form T90) and
    # the tax-exempt portion of any allowance received as an emergency volunteer (line 10105 of the
    # return)": the T90 line 20 export ("Net exempt income 10026", signed) and the T1 line 10105
    # amount, before the election.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t90.t90_net_exempt_income"},
        produces={"output": "ca/cwb_t90_net_exempt_income_total"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cwb_t90_net_exempt_income_total",
                "ca/emergency_services_volunteer_exempt_income",
            )
        },
        produces={"output": "ca/cwb_tax_exempt_net_income_before_election"},
    ),
    # Schedule 6 line 8 counts only when the election is yes, as line 4 does (signed: a negative
    # net exempt income is shown in brackets on the form).
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cwb_tax_exempt_net_income_before_election",
            "count": "ca/cwb_include_tax_exempt_income_checked",
        },
        produces={"output": "ca/cwb_tax_exempt_net_income"},
    ),
    # Schedule 6 line 38101 "Do you have an eligible spouse? 1 Yes or 2 No", a count of 1 or 0,
    # checked before the spouse column reads it. A count of 2 or more is refused, not capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/cwb_eligible_spouses"},
        produces={"output": "ca/cwb_eligible_spouses_checked"},
    ),
    # An eligible spouse is a cohabiting spouse or common-law partner on December 31 (Schedule 6,
    # "An eligible spouse is a person who meets all of the following conditions"), so the
    # spouse count of the shared spouse fact must be at least the answer to line 38101: a yes
    # with no spouse on December 31 is an input error.
    CapabilitySelection(
        name="ca/count_at_least",
        params={},
        consumes={
            "count": "ca/spouse_or_common_law_partner_on_december_31_total",
            "minimum": "ca/cwb_eligible_spouses_checked",
        },
        produces={"output": "ca/cwb_spouse_for_eligible_spouse_checked"},
    ),
    # Schedule 6 column 2 line 4 "Tax-exempt working income earned on a reserve" (form number
    # 38107), the spouse's amount as entered, counted only when the election is yes (line 38105).
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cwb_spouse_tax_exempt_working_income",
            "count": "ca/cwb_include_tax_exempt_income_checked",
        },
        produces={"output": "ca/cwb_spouse_tax_exempt_working_income_elected"},
    ),
    # Schedule 6 column 2 ("Your eligible spouse") line 5: lines 1, 2 and 3 of column 2 added,
    # the spouse's employment income, taxable scholarships and self-employment income (Note 2:
    # profit only, losses excluded), and line 4 of column 2.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cwb_spouse_employment_income",
                "ca/cwb_spouse_taxable_scholarships",
                "ca/cwb_spouse_self_employment_income",
                "ca/cwb_spouse_tax_exempt_working_income_elected",
            )
        },
        produces={"output": "ca/cwb_spouse_working_income_before_eligibility"},
    ),
    # Column 2 line 5 counts only with an eligible spouse (line 38101): the amount above times
    # the checked answer, 1 or 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cwb_spouse_working_income_before_eligibility",
            "count": "ca/cwb_eligible_spouses_checked",
        },
        produces={"output": "ca/cwb_spouse_working_income"},
    ),
    # Schedule 6 line 6 "Add the amounts from line 5 in columns 1 and 2. Enter this amount on
    # line 16. Family working income": column 1 (ca/working_income) and column 2
    # (ca/cwb_spouse_working_income).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/working_income", "ca/cwb_spouse_working_income")},
        produces={"output": "ca/cwb_family_working_income"},
    ),
    # Schedule 6 column 2 line 8 "Total of net exempt income earned on a reserve" (form number
    # 38109), the spouse's signed amount as entered, counted only when the election is yes.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cwb_spouse_net_exempt_income",
            "count": "ca/cwb_include_tax_exempt_income_checked",
        },
        produces={"output": "ca/cwb_spouse_tax_exempt_net_income_elected"},
    ),
    # Schedule 6 column 2 line 10 "Add lines 7 to 9.": line 7 "Net income from line 23600 of the
    # return" of the spouse (ca/spouse_net_income_before_adjustments, signed), line 8 of column 2
    # and line 9, the spouse's UCCB repayment and RDSP income repayment.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/spouse_net_income_before_adjustments",
                "ca/spouse_uccb_repayment",
                "ca/spouse_rdsp_income_repayment",
                "ca/cwb_spouse_tax_exempt_net_income_elected",
            )
        },
        produces={"output": "ca/cwb_spouse_family_net_income_line_10"},
    ),
    # Schedule 6 column 2 line 11 "Total of UCCB (line 11700 of the return) and RDSP income (line
    # 12500 of the return)": the spouse's UCCB and RDSP income.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/spouse_universal_child_care_benefit",
                "ca/spouse_rdsp_income",
            )
        },
        produces={"output": "ca/cwb_spouse_uccb_and_rdsp_income"},
    ),
    # Schedule 6 column 2 line 12 "Line 10 minus line 11 (if negative, enter "0")", before the
    # eligible spouse count is applied.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cwb_spouse_family_net_income_line_10",
            "less": "ca/cwb_spouse_uccb_and_rdsp_income",
        },
        produces={"output": "ca/cwb_spouse_family_net_income_line_12_before_eligibility"},
    ),
    # Column 2 line 12 counts only with an eligible spouse (line 38101), as line 5 does.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cwb_spouse_family_net_income_line_12_before_eligibility",
            "count": "ca/cwb_eligible_spouses_checked",
        },
        produces={"output": "ca/cwb_spouse_family_net_income_line_12"},
    ),
    # Schedule 6 Part B, column 1 "You": line 7 (the TOSI-adjusted net income, signed), line 8
    # (the tax-exempt net income, signed, zero unless elected) and line 9 (the UCCB and RDSP income
    # repayments) added by line 10 "Add lines 7 to 9."
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/tosi_adjusted_net_income",
                "ca/uccb_and_rdsp_income_repayments",
                "ca/cwb_tax_exempt_net_income",
            )
        },
        produces={"output": "ca/cwb_family_net_income_line_10"},
    ),
    # Line 12 "Line 10 minus line 11 (if negative, enter "0")", line 11 being the UCCB and RDSP
    # income.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cwb_family_net_income_line_10", "less": "ca/uccb_and_rdsp_income"},
        produces={"output": "ca/cwb_family_net_income_line_12"},
    ),
    # Schedule 6 line 13 "Add the amounts from line 12 in columns 1 and 2. If you had an eligible
    # spouse, continue at line 14; if not, continue at line 15.": the two line 12 amounts added.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cwb_family_net_income_line_12",
                "ca/cwb_spouse_family_net_income_line_12",
            )
        },
        produces={"output": "ca/cwb_family_net_income_line_13"},
    ),
    # Schedule 6 line 14 "Secondary earner exemption": the first amount, "If your working income
    # (line 5) is less than your eligible spouse's working income", is column 1 less column 2's
    # working income, a signed amount; the sign picks the column below.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/working_income",
            "less": "ca/cwb_spouse_working_income",
        },
        produces={"output": "ca/cwb_working_income_less_spouse"},
    ),
    # Schedule 6 line 14, "enter whichever is less from column 1: amount from line 5 or line 12":
    # the less of the filer's working income (line 5) and the filer's line 12.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/working_income", "ca/cwb_family_net_income_line_12"),
        },
        produces={"output": "ca/cwb_secondary_earner_yours"},
    ),
    # Schedule 6 line 14, "...equal to or more than your eligible spouse's working income, enter
    # whichever is less from column 2: amount from line 5 or line 12": the less of the spouse's
    # working income and the spouse's line 12.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cwb_spouse_working_income",
                "ca/cwb_spouse_family_net_income_line_12",
            ),
        },
        produces={"output": "ca/cwb_secondary_earner_spouses"},
    ),
    # Schedule 6 line 14: the column 1 amount when the working income is less than the spouse's
    # (a negative difference), else the column 2 amount.
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/cwb_working_income_less_spouse",
            "when_positive": (),
            "when_zero": (),
            "when_negative": ("ca/cwb_secondary_earner_yours",),
            "when_non_positive": (),
            "when_non_negative": ("ca/cwb_secondary_earner_spouses",),
        },
        produces={"output": "ca/cwb_secondary_earner_exemption_before_maximum"},
    ),
    # Schedule 6 line 14 "(maximum $16,386)": the amount capped at the maximum dataset, the
    # secondary earner exemption, a line of the form. With no eligible spouse both spouse
    # figures are 0, so the line is 0.
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/cwb_secondary_earner_exemption_maximum"},
        consumes={"base": "ca/cwb_secondary_earner_exemption_before_maximum"},
        produces={"output": "ca/cwb_secondary_earner_exemption"},
    ),
    # Schedule 6 line 15 "Line 13 minus line 14 Enter this amount on line 23 and line 35. Adjusted
    # family net income": the line 13 amount less the line 14 exemption; the form prints no "if
    # negative, enter 0", so it is signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cwb_family_net_income_line_13",
            "less": "ca/cwb_secondary_earner_exemption",
        },
        produces={"output": "ca/adjusted_family_net_income"},
    ),
    # Schedule 6 lines 16 to 22: line 16 "Family working income from line 6"; line 17 "Base
    # amount 3,000.00"; line 18 "Line 16 minus line 17 (if negative, enter "0")"; line 19
    # "Rate 27%"; line 20 "Line 18 multiplied by the percentage from line 19"; line 21 "If
    # you had an eligible spouse or an eligible dependant, enter $2,813. If not, enter
    # $1,633."; line 22 "Enter whichever is less: amount from line 20 or line 21.": one tier
    # with a maximum, with no eligible spouse or dependant.
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_basic"},
        consumes={"base": "ca/cwb_family_working_income"},
        produces={"output": "ca/cwb_before_reduction_without_dependant"},
    ),
    # The same lines with an eligible dependant or spouse: line 21's $2,813 as the tier's maximum.
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_basic_with_dependant"},
        consumes={"base": "ca/cwb_family_working_income"},
        produces={"output": "ca/cwb_before_reduction_with_dependant"},
    ),
    # Schedule 6 lines 23 to 27: line 23 "Adjusted family net income from line 15"; line 24
    # "If you had an eligible spouse or an eligible dependant, enter $30,639. If not, enter
    # $26,855."; line 25 "Line 23 minus line 24 (if negative, enter "0")"; line 26 "Rate
    # 15%"; line 27 "Line 25 multiplied by the percentage from line 26": one tier, with no
    # eligible spouse or dependant.
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_reduction"},
        consumes={"base": "ca/adjusted_family_net_income"},
        produces={"output": "ca/cwb_reduction_without_dependant"},
    ),
    # The same lines with an eligible dependant or spouse: line 24's $30,639 as the tier's
    # threshold.
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_reduction_with_dependant"},
        consumes={"base": "ca/adjusted_family_net_income"},
        produces={"output": "ca/cwb_reduction_with_dependant"},
    ),
    # Schedule 6 line 28 "Line 22 minus line 27 (if negative, enter "0") If you are not
    # completing Step 3, enter this amount on line 45300 of your return.", with no eligible
    # spouse or dependant: Step 3 (the disability supplement) is not triggered.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cwb_before_reduction_without_dependant",
            "less": "ca/cwb_reduction_without_dependant",
        },
        produces={"output": "ca/canada_workers_benefit_without_dependant"},
    ),
    # Line 28 with an eligible dependant or spouse.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cwb_before_reduction_with_dependant",
            "less": "ca/cwb_reduction_with_dependant",
        },
        produces={"output": "ca/canada_workers_benefit_with_dependant"},
    ),
    # The answer to the eligible dependant question of Schedule 6 line 38100, a count of 1 or 0,
    # checked before line 28 reads it. A count of 2 or more is refused, not capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/cwb_eligible_dependants"},
        produces={"output": "ca/cwb_eligible_dependants_checked"},
    ),
    # Line 28 for the filer's spouse status, which lines 21 and 24 read ("If you had an eligible
    # spouse or an eligible dependant ... If not ..."): the line with no eligible spouse when the
    # count of Schedule 6 line 38101 is 0, else the line with one.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cwb_eligible_spouses_checked",
            "when_none": "ca/canada_workers_benefit_without_dependant",
            "when_any": "ca/canada_workers_benefit_with_dependant",
        },
        produces={"output": "ca/cwb_line_28_by_spouse"},
    ),
    # Line 28 for the filer's family status: the line by spouse when there is no eligible
    # dependant (Schedule 6 line 38100), else the line with an eligible dependant.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cwb_eligible_dependants_checked",
            "when_none": "ca/cwb_line_28_by_spouse",
            "when_any": "ca/canada_workers_benefit_with_dependant",
        },
        produces={"output": "ca/canada_workers_benefit_line_28"},
    ),
    # Schedule 6 line 38104 "Is your eligible spouse eligible for the DTC for themselves? ...
    # 1 Yes or 2 No", a count of 1 or 0, checked before line 38 reads it. A count of 2 or more is
    # refused, not capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/cwb_eligible_spouse_eligible_for_dtc"},
        produces={"output": "ca/cwb_eligible_spouse_eligible_for_dtc_checked"},
    ),
    # Line 38104 asks about "your eligible spouse": a 1 with no eligible spouse (line 38101) is an
    # input error.
    CapabilitySelection(
        name="ca/count_at_most",
        params={},
        consumes={
            "count": "ca/cwb_eligible_spouse_eligible_for_dtc_checked",
            "maximum": "ca/cwb_eligible_spouses_checked",
        },
        produces={"output": "ca/cwb_dtc_spouse_for_eligible_spouse_checked"},
    ),
    # Schedule 6 Step 3 lines 29 to 34: one tier over line 30's $1,150 with line 34's $843 as its
    # maximum, on the working income of column 1 (line 29).
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_disability_supplement"},
        consumes={"base": "ca/working_income"},
        produces={"output": "ca/cwb_disability_supplement_before_reduction"},
    ),
    # Lines 35 to 39: one tier over line 36 on the adjusted family net income (line 35), once for
    # each of line 36 and line 38's cases.
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_disability_reduction"},
        consumes={"base": "ca/adjusted_family_net_income"},
        produces={"output": "ca/cwb_disability_reduction_without_dependant"},
    ),
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_disability_reduction_with_dependant"},
        consumes={"base": "ca/adjusted_family_net_income"},
        produces={"output": "ca/cwb_disability_reduction_with_dependant"},
    ),
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca/cwb_disability_reduction_with_dtc_spouse"},
        consumes={"base": "ca/adjusted_family_net_income"},
        produces={"output": "ca/cwb_disability_reduction_with_dtc_spouse"},
    ),
    # Line 39 for the spouse status (line 38101), then the family status (line 38100), then line
    # 38's rate (line 38104).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cwb_eligible_spouses_checked",
            "when_none": "ca/cwb_disability_reduction_without_dependant",
            "when_any": "ca/cwb_disability_reduction_with_dependant",
        },
        produces={"output": "ca/cwb_disability_reduction_by_spouse"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cwb_eligible_dependants_checked",
            "when_none": "ca/cwb_disability_reduction_by_spouse",
            "when_any": "ca/cwb_disability_reduction_with_dependant",
        },
        produces={"output": "ca/cwb_disability_reduction_by_status"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cwb_dtc_spouse_for_eligible_spouse_checked",
            "when_none": "ca/cwb_disability_reduction_by_status",
            "when_any": "ca/cwb_disability_reduction_with_dtc_spouse",
        },
        produces={"output": "ca/cwb_disability_reduction"},
    ),
    # Line 40 "Line 34 minus line 39 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cwb_disability_supplement_before_reduction",
            "less": "ca/cwb_disability_reduction",
        },
        produces={"output": "ca/cwb_disability_supplement"},
    ),
    # Schedule 6 line 38102 "Are you claiming the basic CWB? ... 1 Yes or 2 No", a count of 1 or 0,
    # checked before line 41 reads it. A count of 2 or more is refused, not capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/cwb_claiming_basic"},
        produces={"output": "ca/cwb_claiming_basic_checked"},
    ),
    # Line 41 "If you completed Step 2, enter the amount from line 28. If not, enter "0"." is
    # line 28 when line 38102 is yes, else 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/canada_workers_benefit_line_28",
            "count": "ca/cwb_claiming_basic_checked",
        },
        produces={"output": "ca/canada_workers_benefit_line_41"},
    ),
    # Line 42 "Line 40 plus line 41".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/cwb_disability_supplement", "ca/canada_workers_benefit_line_41"),
        },
        produces={"output": "ca/canada_workers_benefit_line_42"},
    ),
    # Line 38103 "Are you eligible for the disability tax credit (DTC)?": line 42 when yes, else
    # line 28 as Step 2 completes it (line 41).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/eligible_for_disability_amount_checked",
            "when_none": "ca/canada_workers_benefit_line_41",
            "when_any": "ca/canada_workers_benefit_line_42",
        },
        produces={"output": "ca/canada_workers_benefit_before_conditions"},
    ),
    # Schedule 6's yes or no answers (age 19, resided with a spouse or child, full-time student,
    # prison, officer of another country), each checked to be 0 or 1.
    *(
        CapabilitySelection(
            name="ca/yes_or_no_count",
            params={},
            consumes={"count": f"ca/{answer}"},
            produces={"output": f"ca/{answer}_checked"},
        )
        for answer in ELIGIBILITY_ANSWERS
    ),
    # 0 when a condition under which the Canada workers benefit cannot be claimed applies.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cwb_eligibility_conditions"},
        consumes={
            "counts": (
                "ca/resident_in_canada_throughout_2025_checked",
                "ca/aged_19_or_older_at_end_of_2025_checked",
                "ca/resided_with_spouse_or_child_at_end_of_2025_checked",
                "ca/cwb_eligible_dependants_checked",
                "ca/full_time_student_for_more_than_13_weeks_checked",
                "ca/confined_to_prison_for_90_days_checked",
                "ca/exempt_as_foreign_officer_or_family_checked",
            ),
            "amounts": (),
        },
        produces={"output": "ca/cwb_eligible"},
    ),
    # Line 45300: line 28 for a filer who meets the conditions, else 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/canada_workers_benefit_before_conditions",
            "count": "ca/cwb_eligible",
        },
        produces={"output": "ca/canada_workers_benefit"},
    ),
    # Schedule 6 Step 4: line 43 is the benefit of the return, line 46 adds lines 44 and 45, line 48
    # adds line 47, and line 49 is the lesser of lines 43 and 48 (T1 line 41500).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/canada_workers_benefit",)},
        produces={"output": "ca/cwb_claimed"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/acwb_paid_to_you", "ca/acwb_paid_to_spouse")},
        produces={"output": "ca/acwb_lines_44_and_45"},
    ),
    # The answer for an eligible spouse claiming the basic CWB for the filer, a count of 1 or 0,
    # checked before line 46 reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/cwb_spouse_claiming_basic"},
        produces={"output": "ca/cwb_spouse_claiming_basic_checked"},
    ),
    # "an eligible spouse who is claiming the basic CWB for you": a 1 with no eligible spouse (line
    # 38101) is an input error.
    CapabilitySelection(
        name="ca/count_at_most",
        params={},
        consumes={
            "count": "ca/cwb_spouse_claiming_basic_checked",
            "maximum": "ca/cwb_eligible_spouses_checked",
        },
        produces={"output": "ca/cwb_spouse_claiming_basic_with_spouse_checked"},
    ),
    # Line 46: 0 when an eligible spouse is claiming the basic CWB for the filer who is claiming the
    # disability supplement, else 1.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/acwb_line_46_spouse_rule"},
        consumes={
            "counts": (
                "ca/cwb_eligible_spouses_checked",
                "ca/cwb_claiming_basic_checked",
                "ca/cwb_spouse_claiming_basic_with_spouse_checked",
                "ca/eligible_for_disability_amount_checked",
            ),
            "amounts": (),
        },
        produces={"output": "ca/acwb_line_46_applies"},
    ),
    # Line 46 "Line 44 plus line 45", or 0 under that rule.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/acwb_lines_44_and_45", "count": "ca/acwb_line_46_applies"},
        produces={"output": "ca/acwb_basic_paid"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/acwb_basic_paid", "ca/acwb_disability_supplement_paid")},
        produces={"output": "ca/acwb_paid"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cwb_claimed", "ca/acwb_paid")},
        produces={"output": "ca/advanced_canada_workers_benefit"},
    ),
}

ELIGIBILITY_ANSWER_KINDS = (
    AGED_19_OR_OLDER_AT_END_OF_2025,
    RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025,
    FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS,
    CONFINED_TO_PRISON_FOR_90_DAYS,
    EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY,
)
ELIGIBILITY_CHECKED_KINDS = (
    AGED_19_OR_OLDER_AT_END_OF_2025_CHECKED,
    RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025_CHECKED,
    FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS_CHECKED,
    CONFINED_TO_PRISON_FOR_90_DAYS_CHECKED,
    EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY_CHECKED,
)

WIRING = {
    (
        Sum,
        frozenset({EMPLOYMENT_INCOME, OTHER_EMPLOYMENT_INCOME}),
        frozenset({CWB_EMPLOYMENT_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                CWB_EMPLOYMENT_INCOME,
                TAXABLE_SCHOLARSHIPS,
                MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
                CWB_TAX_EXEMPT_WORKING_INCOME,
            }
        ),
        frozenset({WORKING_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({T90_EXEMPT_WORKING_INCOME_PER_FORM}),
        frozenset({CWB_T90_EXEMPT_WORKING_INCOME_TOTAL}),
    ),
    (
        Sum,
        frozenset(
            {CWB_T90_EXEMPT_WORKING_INCOME_TOTAL, EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME}
        ),
        frozenset({CWB_TAX_EXEMPT_WORKING_INCOME_BEFORE_ELECTION}),
    ),
    (
        YesOrNoCount,
        frozenset({CWB_INCLUDE_TAX_EXEMPT_INCOME}),
        frozenset({CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED}),
    ),
    (
        TimesCount,
        frozenset(
            {CWB_TAX_EXEMPT_WORKING_INCOME_BEFORE_ELECTION, CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED}
        ),
        frozenset({CWB_TAX_EXEMPT_WORKING_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({T90_NET_EXEMPT_INCOME_PER_FORM}),
        frozenset({CWB_T90_NET_EXEMPT_INCOME_TOTAL}),
    ),
    (
        Sum,
        frozenset({CWB_T90_NET_EXEMPT_INCOME_TOTAL, EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME}),
        frozenset({CWB_TAX_EXEMPT_NET_INCOME_BEFORE_ELECTION}),
    ),
    (
        TimesCount,
        frozenset(
            {CWB_TAX_EXEMPT_NET_INCOME_BEFORE_ELECTION, CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED}
        ),
        frozenset({CWB_TAX_EXEMPT_NET_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {TOSI_ADJUSTED_NET_INCOME, UCCB_AND_RDSP_INCOME_REPAYMENTS, CWB_TAX_EXEMPT_NET_INCOME}
        ),
        frozenset({CWB_FAMILY_NET_INCOME_LINE_10}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CWB_FAMILY_NET_INCOME_LINE_10, UCCB_AND_RDSP_INCOME}),
        frozenset({CWB_FAMILY_NET_INCOME_LINE_12}),
    ),
    (
        YesOrNoCount,
        frozenset({CWB_ELIGIBLE_SPOUSES}),
        frozenset({CWB_ELIGIBLE_SPOUSES_CHECKED}),
    ),
    (
        CountAtLeast,
        frozenset(
            {
                SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
                CWB_ELIGIBLE_SPOUSES_CHECKED,
            }
        ),
        frozenset({CWB_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED}),
    ),
    (
        TimesCount,
        frozenset({CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME, CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED}),
        frozenset({CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED}),
    ),
    (
        TimesCount,
        frozenset({CWB_SPOUSE_NET_EXEMPT_INCOME, CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED}),
        frozenset({CWB_SPOUSE_TAX_EXEMPT_NET_INCOME_ELECTED}),
    ),
    (
        Sum,
        frozenset(
            {
                CWB_SPOUSE_EMPLOYMENT_INCOME,
                CWB_SPOUSE_TAXABLE_SCHOLARSHIPS,
                CWB_SPOUSE_SELF_EMPLOYMENT_INCOME,
                CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED,
            }
        ),
        frozenset({CWB_SPOUSE_WORKING_INCOME_BEFORE_ELIGIBILITY}),
    ),
    (
        TimesCount,
        frozenset({CWB_SPOUSE_WORKING_INCOME_BEFORE_ELIGIBILITY, CWB_ELIGIBLE_SPOUSES_CHECKED}),
        frozenset({CWB_SPOUSE_WORKING_INCOME}),
    ),
    (
        Sum,
        frozenset({WORKING_INCOME, CWB_SPOUSE_WORKING_INCOME}),
        frozenset({CWB_FAMILY_WORKING_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
                SPOUSE_UCCB_REPAYMENT,
                SPOUSE_RDSP_INCOME_REPAYMENT,
                CWB_SPOUSE_TAX_EXEMPT_NET_INCOME_ELECTED,
            }
        ),
        frozenset({CWB_SPOUSE_FAMILY_NET_INCOME_LINE_10}),
    ),
    (
        Sum,
        frozenset({SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT, SPOUSE_RDSP_INCOME}),
        frozenset({CWB_SPOUSE_UCCB_AND_RDSP_INCOME}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CWB_SPOUSE_FAMILY_NET_INCOME_LINE_10, CWB_SPOUSE_UCCB_AND_RDSP_INCOME}),
        frozenset({CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12_BEFORE_ELIGIBILITY}),
    ),
    (
        TimesCount,
        frozenset(
            {
                CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12_BEFORE_ELIGIBILITY,
                CWB_ELIGIBLE_SPOUSES_CHECKED,
            }
        ),
        frozenset({CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12}),
    ),
    (
        Sum,
        frozenset({CWB_FAMILY_NET_INCOME_LINE_12, CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12}),
        frozenset({CWB_FAMILY_NET_INCOME_LINE_13}),
    ),
    (
        Subtract,
        frozenset({WORKING_INCOME, CWB_SPOUSE_WORKING_INCOME}),
        frozenset({CWB_WORKING_INCOME_LESS_SPOUSE}),
    ),
    (
        LesserOf,
        frozenset({WORKING_INCOME, CWB_FAMILY_NET_INCOME_LINE_12}),
        frozenset({CWB_SECONDARY_EARNER_YOURS}),
    ),
    (
        LesserOf,
        frozenset({CWB_SPOUSE_WORKING_INCOME, CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12}),
        frozenset({CWB_SECONDARY_EARNER_SPOUSES}),
    ),
    (
        ChooseBySign,
        frozenset(
            {
                CWB_WORKING_INCOME_LESS_SPOUSE,
                CWB_SECONDARY_EARNER_YOURS,
                CWB_SECONDARY_EARNER_SPOUSES,
            }
        ),
        frozenset({CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM}),
    ),
    (
        CappedAmount,
        frozenset({CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM}),
        frozenset({CWB_SECONDARY_EARNER_EXEMPTION}),
    ),
    (
        Subtract,
        frozenset({CWB_FAMILY_NET_INCOME_LINE_13, CWB_SECONDARY_EARNER_EXEMPTION}),
        frozenset({ADJUSTED_FAMILY_NET_INCOME}),
    ),
    (
        TieredSurcharge,
        frozenset({CWB_FAMILY_WORKING_INCOME}),
        frozenset({CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT}),
    ),
    (
        TieredSurcharge,
        frozenset({CWB_FAMILY_WORKING_INCOME}),
        frozenset({CWB_BEFORE_REDUCTION_WITH_DEPENDANT}),
    ),
    (
        TieredSurcharge,
        frozenset({ADJUSTED_FAMILY_NET_INCOME}),
        frozenset({CWB_REDUCTION_WITHOUT_DEPENDANT}),
    ),
    (
        TieredSurcharge,
        frozenset({ADJUSTED_FAMILY_NET_INCOME}),
        frozenset({CWB_REDUCTION_WITH_DEPENDANT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT, CWB_REDUCTION_WITHOUT_DEPENDANT}),
        frozenset({CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CWB_BEFORE_REDUCTION_WITH_DEPENDANT, CWB_REDUCTION_WITH_DEPENDANT}),
        frozenset({CANADA_WORKERS_BENEFIT_WITH_DEPENDANT}),
    ),
    (
        YesOrNoCount,
        frozenset({CWB_ELIGIBLE_DEPENDANTS}),
        frozenset({CWB_ELIGIBLE_DEPENDANTS_CHECKED}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CWB_ELIGIBLE_SPOUSES_CHECKED,
                CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT,
                CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
            }
        ),
        frozenset({CWB_LINE_28_BY_SPOUSE}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CWB_ELIGIBLE_DEPENDANTS_CHECKED,
                CWB_LINE_28_BY_SPOUSE,
                CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
            }
        ),
        frozenset({CANADA_WORKERS_BENEFIT_LINE_28}),
    ),
    (
        YesOrNoCount,
        frozenset({CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC}),
        frozenset({CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC_CHECKED}),
    ),
    (
        CountAtMost,
        frozenset({CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC_CHECKED, CWB_ELIGIBLE_SPOUSES_CHECKED}),
        frozenset({CWB_DTC_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED}),
    ),
    (
        TieredSurcharge,
        frozenset({WORKING_INCOME}),
        frozenset({CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION}),
    ),
    (
        TieredSurcharge,
        frozenset({ADJUSTED_FAMILY_NET_INCOME}),
        frozenset({CWB_DISABILITY_REDUCTION_WITHOUT_DEPENDANT}),
    ),
    (
        TieredSurcharge,
        frozenset({ADJUSTED_FAMILY_NET_INCOME}),
        frozenset({CWB_DISABILITY_REDUCTION_WITH_DEPENDANT}),
    ),
    (
        TieredSurcharge,
        frozenset({ADJUSTED_FAMILY_NET_INCOME}),
        frozenset({CWB_DISABILITY_REDUCTION_WITH_DTC_SPOUSE}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CWB_ELIGIBLE_SPOUSES_CHECKED,
                CWB_DISABILITY_REDUCTION_WITHOUT_DEPENDANT,
                CWB_DISABILITY_REDUCTION_WITH_DEPENDANT,
            }
        ),
        frozenset({CWB_DISABILITY_REDUCTION_BY_SPOUSE}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CWB_ELIGIBLE_DEPENDANTS_CHECKED,
                CWB_DISABILITY_REDUCTION_BY_SPOUSE,
                CWB_DISABILITY_REDUCTION_WITH_DEPENDANT,
            }
        ),
        frozenset({CWB_DISABILITY_REDUCTION_BY_STATUS}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CWB_DTC_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED,
                CWB_DISABILITY_REDUCTION_BY_STATUS,
                CWB_DISABILITY_REDUCTION_WITH_DTC_SPOUSE,
            }
        ),
        frozenset({CWB_DISABILITY_REDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION, CWB_DISABILITY_REDUCTION}),
        frozenset({CWB_DISABILITY_SUPPLEMENT}),
    ),
    (YesOrNoCount, frozenset({CWB_CLAIMING_BASIC}), frozenset({CWB_CLAIMING_BASIC_CHECKED})),
    (
        TimesCount,
        frozenset({CANADA_WORKERS_BENEFIT_LINE_28, CWB_CLAIMING_BASIC_CHECKED}),
        frozenset({CANADA_WORKERS_BENEFIT_LINE_41}),
    ),
    (
        Sum,
        frozenset({CWB_DISABILITY_SUPPLEMENT, CANADA_WORKERS_BENEFIT_LINE_41}),
        frozenset({CANADA_WORKERS_BENEFIT_LINE_42}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED,
                CANADA_WORKERS_BENEFIT_LINE_41,
                CANADA_WORKERS_BENEFIT_LINE_42,
            }
        ),
        frozenset({CANADA_WORKERS_BENEFIT_BEFORE_CONDITIONS}),
    ),
    *(
        (YesOrNoCount, frozenset({answer}), frozenset({checked}))
        for answer, checked in zip(ELIGIBILITY_ANSWER_KINDS, ELIGIBILITY_CHECKED_KINDS, strict=True)
    ),
    (
        CountByConditions,
        frozenset(
            {
                RESIDENT_IN_CANADA_THROUGHOUT_2025_CHECKED,
                *ELIGIBILITY_CHECKED_KINDS[:2],
                CWB_ELIGIBLE_DEPENDANTS_CHECKED,
                *ELIGIBILITY_CHECKED_KINDS[2:],
            }
        ),
        frozenset({CWB_ELIGIBLE}),
    ),
    (
        TimesCount,
        frozenset({CANADA_WORKERS_BENEFIT_BEFORE_CONDITIONS, CWB_ELIGIBLE}),
        frozenset({CANADA_WORKERS_BENEFIT}),
    ),
    (Sum, frozenset({CANADA_WORKERS_BENEFIT}), frozenset({CWB_CLAIMED})),
    (Sum, frozenset({ACWB_PAID_TO_YOU, ACWB_PAID_TO_SPOUSE}), frozenset({ACWB_LINES_44_AND_45})),
    (
        YesOrNoCount,
        frozenset({CWB_SPOUSE_CLAIMING_BASIC}),
        frozenset({CWB_SPOUSE_CLAIMING_BASIC_CHECKED}),
    ),
    (
        CountAtMost,
        frozenset({CWB_SPOUSE_CLAIMING_BASIC_CHECKED, CWB_ELIGIBLE_SPOUSES_CHECKED}),
        frozenset({CWB_SPOUSE_CLAIMING_BASIC_WITH_SPOUSE_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                CWB_ELIGIBLE_SPOUSES_CHECKED,
                CWB_CLAIMING_BASIC_CHECKED,
                CWB_SPOUSE_CLAIMING_BASIC_WITH_SPOUSE_CHECKED,
                ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED,
            }
        ),
        frozenset({ACWB_LINE_46_APPLIES}),
    ),
    (
        TimesCount,
        frozenset({ACWB_LINES_44_AND_45, ACWB_LINE_46_APPLIES}),
        frozenset({ACWB_BASIC_PAID}),
    ),
    (
        Sum,
        frozenset({ACWB_BASIC_PAID, ACWB_DISABILITY_SUPPLEMENT_PAID}),
        frozenset({ACWB_PAID}),
    ),
    (LesserOf, frozenset({CWB_CLAIMED, ACWB_PAID}), frozenset({ADVANCED_CANADA_WORKERS_BENEFIT})),
}
