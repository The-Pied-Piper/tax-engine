"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.greater_of import GreaterOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.apply_chosen_rate import ApplyChosenRate
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.catalog import (
    CHILD_CARE_EXPENSES,
    DONATIONS_AND_GIFTS_TOTAL,
    REFUND,
    SOCIAL_BENEFITS_REPAYMENT,
    SPOUSE_NET_INCOME,
    TAXABLE_INCOME,
    TOSI_ADJUSTED_NET_INCOME,
    TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO,
    TOTAL_SPLIT_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.capabilities.choose_by_range import ChooseByRange
from tax_engine.jurisdictions.ca_on.capabilities.coop_education_credit import (
    CoopEducationCredit,
)
from tax_engine.jurisdictions.ca_on.capabilities.flow_through_share_expenses import (
    FlowThroughShareExpenses,
)
from tax_engine.jurisdictions.ca_on.capabilities.quotient import Quotient
from tax_engine.jurisdictions.ca_on.capabilities.rate_by_income_band import RateByIncomeBand
from tax_engine.jurisdictions.ca_on.capabilities.record_count import RecordCount
from tax_engine.jurisdictions.ca_on.catalog import (
    CARE_ADJUSTED_INCOME,
    CARE_CREDIT,
    CARE_CREDIT_PERCENTAGE,
    CARE_FAMILY_ADJUSTED_INCOME,
    CARE_SUPPORTING_PERSONS_ADJUSTED_INCOME,
    CLAIMS_SENIORS_CARE_CREDIT_CHECKED,
    COMMUNITY_FOOD_PROGRAM_CREDIT,
    COMMUNITY_FOOD_PROGRAM_DONATIONS,
    COMMUNITY_FOOD_PROGRAM_DONATIONS_APPLIED,
    COOP_EDUCATION_CREDIT,
    COOP_EDUCATION_FULL_SHARE,
    COOP_EDUCATION_PAYROLL,
    COOP_EDUCATION_PAYROLL_OVER_THRESHOLD,
    COOP_EDUCATION_PAYROLL_RANGE,
    COOP_EDUCATION_PAYROLL_THRESHOLD,
    COOP_EDUCATION_PHASE_OUT_SHARE,
    COOP_EDUCATION_PLACEMENT_COUNT,
    COOP_EDUCATION_PLACEMENTS,
    COOP_EDUCATION_REMAINING_SHARE,
    FERTILITY_CREDIT,
    FERTILITY_CREDIT_BEFORE_MAXIMUM,
    FERTILITY_EXPENSES,
    FLOW_THROUGH_SHARE_CLAIMABLE,
    FLOW_THROUGH_SHARE_CREDIT,
    FLOW_THROUGH_SHARE_EXPENSES,
    FLOW_THROUGH_SHARE_EXPENSES_CLAIMED,
    FLOW_THROUGH_SHARE_SLIPS,
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_FOOD_CREDIT,
    ONTARIO_TAX_AFTER_LIFT_CREDIT,
    SENIORS_CARE_AMOUNT,
    SENIORS_CARE_BASE_AMOUNT,
    SENIORS_CARE_BEFORE_CLAIM,
    SENIORS_CARE_BEFORE_MAXIMUM,
    SENIORS_CARE_CREDIT,
    SENIORS_CARE_FAMILY_NET_INCOME,
    SENIORS_CARE_INCOME_OVER_BASE,
    SENIORS_CARE_REDUCTION,
    SENIORS_TRANSIT_AMOUNT_PAID_CHECKED,
    SENIORS_TRANSIT_CREDIT,
    SENIORS_TRANSIT_MAXIMUM,
    SENIORS_TRANSIT_PAID,
)

INPUTS = frozenset(
    {
        "ca-on/opportunities_fund_donation",
        "ca-on/fertility_expenses",
        "ca-on/claims_seniors_care_credit",
        "ca-on/seniors_transit_paid",
        "ca-on/flow_through_share_slips",
        "ca-on/coop_education_payroll",
        "ca-on/coop_education_placements",
        # ON479 line 63265 "Are you claiming this credit as a member of a partnership? 1 Yes or
        # 2 No" and line 63270 "If yes, enter your nine-digit business number. (enter 9
        # digits)": the form computes nothing from them, so each is also an output.
        "ca-on/coop_claimed_as_partnership_member",
        "ca-on/coop_partnership_business_number",
        "ca-on/community_food_program_donations",
        "ca-on/political_contributions",
        "ca-on/care_supporting_persons_adjusted_income",
    }
)

OUTPUTS = frozenset(
    {
        "ca-on/net_refund",
        "ca-on/coop_education_placement_count",
        "ca-on/coop_claimed_as_partnership_member",
        "ca-on/coop_partnership_business_number",
    }
)

STEPS = {
    # ON428 line 87 and line 62150 "Enter the amount of qualifying donations that have also
    # been claimed as a charitable donation.": the donations are a caller input, refused when
    # above the charitable donations claimed (Schedule 9 line 12, "Line 10 plus line 11"), not
    # capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/community_food_program_donations",
            "bound": "ca/donations_and_gifts_total",
        },
        produces={"output": "ca-on/community_food_program_donations_applied"},
    ),
    # ON428 line 87 and line 62150 "multiplied by 25%", under "Community food program donation
    # tax credit for farmers:", on the donations checked above.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/community_food_program_rate"},
        consumes={"base": "ca-on/community_food_program_donations_applied"},
        produces={"output": "ca-on/community_food_program_credit"},
    ),
    # ON428 line 88 "Line 86 minus line 87 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_after_lift_credit",
            "less": "ca-on/community_food_program_credit",
        },
        produces={"output": "ca-on/ontario_tax_after_food_credit"},
    ),
    # Form T1206 Part 3 line 51 "Amount from the line number of your Form 428 shown in column 8 of
    # Chart C on page 5" (ON428 line 88, above) and line 52 "Enter whichever is more: the amount
    # from line 50 or line 51. Enter the amount from line 52 on line 42800 of your return. (2) If
    # you were a resident of Ontario, enter this amount on line 88 of Form ON428 and complete the
    # remaining lines of that form.": the Ontario tax on split income never takes line 88 below line
    # 50 (line 50 being line 47, the foreign tax credit of line 49 not being wired), and line 52 is
    # the part ON428 line 90 adds the health premium to.
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={"amounts": ("ca-on/split_income_line_50", "ca-on/ontario_tax_after_food_credit")},
        produces={"output": "ca-on/split_income_line_52"},
    ),
    # T1206 "Also, add the amount from line 4 of this form to your taxable income when calculating
    # your Ontario health premium on Form ON428": ON428 line 89 chart line 1 "Enter your taxable
    # income from line 26000 of your return" plus the total split income.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/taxable_income",
                "ca/total_split_income",
            )
        },
        produces={"output": "ca-on/health_premium_income"},
    ),
    # ON428 line 89 "Ontario health premium (complete the chart below)": the chart's tiers on line
    # 1, the taxable income with the total split income added, each the previous plateau plus a rate
    # on the income over its threshold, at most the next plateau.
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca-on/health_premium"},
        consumes={"base": "ca-on/health_premium_income"},
        produces={"output": "ca-on/ontario_health_premium"},
    ),
    # ON428 line 90 "Line 88 plus line 89 Enter this amount on line 42800 of your return. Ontario
    # tax", line 88 being line 52 of Form T1206 (the more of T1206 line 50 and line 88).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/split_income_line_52", "ca-on/ontario_health_premium")},
        produces={"output": "ca-on/ontario_tax"},
    ),
    # Form ON479 line 1 and line 61268 "Eligible medical expenses for fertility treatment
    # multiplied by 25% (maximum $5,000) =": the rate on the expenses, before its maximum.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/fertility_credit_rate"},
        consumes={"base": "ca-on/fertility_expenses"},
        produces={"output": "ca-on/fertility_credit_before_maximum"},
    ),
    # Line 1's "(maximum $5,000)", printed after the percentage, so it caps the credit.
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/fertility_credit_maximum"},
        consumes={"base": "ca-on/fertility_credit_before_maximum"},
        produces={"output": "ca-on/fertility_credit"},
    ),
    # Schedule ON479-A "Family adjusted income calculation for the tax credit", column 1 "You".
    # Line 1 "Net income from line 23600 of the return (or the amount you would have entered if
    # the instructions on line 23600 said "if negative, show in brackets")" is the TOSI-adjusted net
    # income of Form T1206 Part 1 line 6, signed ("use line 6 of this form at column 1 of line 1 of
    # Schedule ON479-A"), the split income plus line 23600 before the floor at 0. Line 2 "Child
    # care expenses deduction from line 21400 of the return". Line 3 "Social benefits repayment
    # from line 23500 of the return" is added, in line order. Line 4 "Add lines 1 to 3 (if
    # negative, enter "0"). Adjusted income".
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/tosi_adjusted_net_income",
                "ca/child_care_expenses",
                "ca/social_benefits_repayment",
            )
        },
        produces={"output": "ca-on/care_adjusted_income"},
    ),
    # Column 2 "Supporting person(s)", line 4 (line 63047) is the supporting persons' adjusted
    # income, a caller input, ca-on/care_supporting_persons_adjusted_income, as it comes from
    # other people's returns; line 5 "Add the amounts from line 4 of columns 1 and 2. Family
    # adjusted income".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/care_adjusted_income",
                "ca-on/care_supporting_persons_adjusted_income",
            )
        },
        produces={"output": "ca-on/care_family_adjusted_income"},
    ),
    # Line 7 "If your family adjusted income on line 5 is "0", enter 75%. If not, enter the tax
    # credit rate that applies to your family adjusted income from the table below.": the table
    # "Family adjusted income and Tax credit rate", as printed.
    CapabilitySelection(
        name="ca-on/rate_by_income_band",
        params={"table": "ca-on/care_credit_rate"},
        consumes={"income": "ca-on/care_family_adjusted_income"},
        produces={"output": "ca-on/care_credit_percentage"},
    ),
    # Line 6 "Enter your child care expenses deduction from line 21400 of your return." and
    # line 8 "Line 6 multiplied by the percentage from line 7 Enter this amount on line 63050
    # of your Form ON479.": line 6 reads the child care expenses deduction, as line 2 does.
    CapabilitySelection(
        name="ca/apply_chosen_rate",
        params={"rounding": "ca-on/care_credit_rounding"},
        consumes={"base": "ca/child_care_expenses", "rate": "ca-on/care_credit_percentage"},
        produces={"output": "ca-on/care_credit"},
    ),
    # Form ON479 line 3 "Medical expenses from line 58769 of your Form ON428" is the artifact
    # ca-on/medical_claim (ON428 line 43), read directly. Line 4 "Allowable percentage 25%" and
    # line 5 "Line 3 multiplied by the percentage from line 4 (maximum $1,500) =": the
    # percentage on line 3, before the maximum.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/seniors_care_rate"},
        consumes={"base": "ca-on/medical_claim"},
        produces={"output": "ca-on/seniors_care_before_maximum"},
    ),
    # Line 5's "(maximum $1,500)", printed after the percentage, so it caps the result.
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/seniors_care_maximum"},
        consumes={"base": "ca-on/seniors_care_before_maximum"},
        produces={"output": "ca-on/seniors_care_amount"},
    ),
    # Line 8 "Line 6 plus line 7 Family net income =", line 6 being "Your net income from line 23600
    # of your return", the TOSI-adjusted net income of Form T1206 Part 1 line 6 in its place, not
    # below zero ("the Ontario seniors care at home tax credit (line 6 of Form ON479)"), and
    # line 7 "Your spouse's or common-law partner's net income from line 23600 of their return (if
    # applicable)", the caller input shared with T1 line 30300 and ON428 line 58120 (0 with no
    # spouse).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/tosi_adjusted_net_income_not_below_zero", "ca/spouse_net_income")},
        produces={"output": "ca-on/seniors_care_family_net_income"},
    ),
    # Line 9 "Base amount 35,000.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/seniors_care_base_amount"},
        consumes={},
        produces={"output": "ca-on/seniors_care_base_amount"},
    ),
    # Line 10 "Line 8 minus line 9 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/seniors_care_family_net_income",
            "less": "ca-on/seniors_care_base_amount",
        },
        produces={"output": "ca-on/seniors_care_income_over_base"},
    ),
    # Line 11 "Applicable rate 5%" and line 12 "Line 10 multiplied by the percentage from
    # line 11 =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/seniors_care_reduction_rate"},
        consumes={"base": "ca-on/seniors_care_income_over_base"},
        produces={"output": "ca-on/seniors_care_reduction"},
    ),
    # Line 13 and line 63095 "Line 5 minus line 12 (if negative, enter "0") =". The form's
    # rules for a family net income of $35,000 or less (line 5 on line 13) and of more than
    # $65,000 ("0" on line 13) follow from lines 9 to 12: line 10 is 0 up to $35,000, and at
    # $65,000 line 12 is $1,500.00, the most line 5 can be.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/seniors_care_amount",
            "less": "ca-on/seniors_care_reduction",
        },
        produces={"output": "ca-on/seniors_care_before_claim"},
    ),
    # The caller's 0/1 count "claims the Ontario seniors care at home tax credit": line 13
    # once if the filer claims it, else 0. ON479 prints no eligibility text for the credit, so
    # the caller claims it only for a filer who qualifies.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/seniors_care_before_claim",
            "count": "ca-on/claims_seniors_care_credit_checked",
        },
        produces={"output": "ca-on/seniors_care_credit"},
    ),
    # Line 14 "Amount paid in the year for eligible seniors' use of Ontario public transit
    # services (maximum $3,000) Line 63100 multiplied by 15% =": the "(maximum $3,000)" is
    # printed before the percentage, so it bounds the amount paid: above it the amount is an input
    # error, not capped.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/seniors_transit_maximum"},
        consumes={},
        produces={"output": "ca-on/seniors_transit_maximum"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/seniors_transit_paid",
            "bound": "ca-on/seniors_transit_maximum",
        },
        produces={"output": "ca-on/seniors_transit_amount_paid_checked"},
    ),
    # Line 14's "multiplied by 15% =", on the checked amount.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/seniors_transit_rate"},
        consumes={"base": "ca-on/seniors_transit_amount_paid_checked"},
        produces={"output": "ca-on/seniors_transit_credit"},
    ),
    # Form ON479 line 15 and line 63100 "Ontario political contributions made in 2025" is a
    # caller input, ca-on/political_contributions, taken as the form takes it; Worksheet ON479
    # "Line 16 - Ontario political contribution tax credit" reads it as line 63110 and builds
    # each of its three columns as printed, then the one that applies is picked.
    # Worksheet ON479 "Column 1: Line 63110 is $500.05 or less".
    # Line 2: 0.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/political_credit_column_1_line_2"},
        consumes={},
        produces={"output": "ca-on/political_credit_column_1_line_2"},
    ),
    # Column 1 line 3 "Line 1 minus line 2 (cannot be negative)", line 1 being the
    # contributions.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/political_contributions",
            "less": "ca-on/political_credit_column_1_line_2",
        },
        produces={"output": "ca-on/political_credit_column_1_line_3"},
    ),
    # Column 1 line 4 "Rate 75%" and line 5 "Line 3 multiplied by the percentage from line 4".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/political_credit_column_1_line_4"},
        consumes={"base": "ca-on/political_credit_column_1_line_3"},
        produces={"output": "ca-on/political_credit_column_1_line_5"},
    ),
    # Column 1 line 6: 0.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/political_credit_column_1_line_6"},
        consumes={},
        produces={"output": "ca-on/political_credit_column_1_line_6"},
    ),
    # Column 1 line 7 "Line 5 plus line 6 Enter this amount on line 16 of your Form ON479.".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/political_credit_column_1_line_5",
                "ca-on/political_credit_column_1_line_6",
            )
        },
        produces={"output": "ca-on/political_credit_column_1_line_7"},
    ),
    # Worksheet ON479 "Column 2: Line 63110 is more than $500.05 but not more than $1,666.82".
    # Line 2: 500.05, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/political_credit_column_2_line_2"},
        consumes={},
        produces={"output": "ca-on/political_credit_column_2_line_2"},
    ),
    # Column 2 line 3 "Line 1 minus line 2 (cannot be negative)", line 1 being the
    # contributions.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/political_contributions",
            "less": "ca-on/political_credit_column_2_line_2",
        },
        produces={"output": "ca-on/political_credit_column_2_line_3"},
    ),
    # Column 2 line 4 "Rate 50%" and line 5 "Line 3 multiplied by the percentage from line 4".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/political_credit_column_2_line_4"},
        consumes={"base": "ca-on/political_credit_column_2_line_3"},
        produces={"output": "ca-on/political_credit_column_2_line_5"},
    ),
    # Column 2 line 6: 375.03, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/political_credit_column_2_line_6"},
        consumes={},
        produces={"output": "ca-on/political_credit_column_2_line_6"},
    ),
    # Column 2 line 7 "Line 5 plus line 6 Enter this amount on line 16 of your Form ON479.".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/political_credit_column_2_line_5",
                "ca-on/political_credit_column_2_line_6",
            )
        },
        produces={"output": "ca-on/political_credit_column_2_line_7"},
    ),
    # Worksheet ON479 "Column 3: Line 63110 is more than $1,666.82".
    # Line 2: 1,666.82, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/political_credit_column_3_line_2"},
        consumes={},
        produces={"output": "ca-on/political_credit_column_3_line_2"},
    ),
    # Column 3 line 3 "Line 1 minus line 2 (cannot be negative)", line 1 being the
    # contributions.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/political_contributions",
            "less": "ca-on/political_credit_column_3_line_2",
        },
        produces={"output": "ca-on/political_credit_column_3_line_3"},
    ),
    # Column 3 line 4 "Rate 33.33%" and line 5 "Line 3 multiplied by the percentage from line
    # 4".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/political_credit_column_3_line_4"},
        consumes={"base": "ca-on/political_credit_column_3_line_3"},
        produces={"output": "ca-on/political_credit_column_3_line_5"},
    ),
    # Column 3 line 6: 958.41, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/political_credit_column_3_line_6"},
        consumes={},
        produces={"output": "ca-on/political_credit_column_3_line_6"},
    ),
    # Column 3 line 7 "Line 5 plus line 6 Enter this amount on line 16 of your Form ON479.".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/political_credit_column_3_line_5",
                "ca-on/political_credit_column_3_line_6",
            )
        },
        produces={"output": "ca-on/political_credit_column_3_line_7"},
    ),
    # The column that applies: column 1 if line 63110 is $500.05 or less, column 2 if it is more
    # than $500.05 but not more than $1,666.82, column 3 if it is more than $1,666.82. The
    # limits are the columns' own line 2 constants, which their headings print again.
    CapabilitySelection(
        name="ca-on/choose_by_range",
        params={},
        consumes={
            "amount": "ca-on/political_contributions",
            "first_limit": "ca-on/political_credit_column_2_line_2",
            "second_limit": "ca-on/political_credit_column_3_line_2",
            "first": "ca-on/political_credit_column_1_line_7",
            "second": "ca-on/political_credit_column_2_line_7",
            "third": "ca-on/political_credit_column_3_line_7",
        },
        produces={"output": "ca-on/political_credit_before_maximum"},
    ),
    # ON479 line 16 "(maximum $1,666.82)", after the chosen column's line 7.
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/political_credit_maximum"},
        consumes={"base": "ca-on/political_credit_before_maximum"},
        produces={"output": "ca-on/political_credit"},
    ),
    # Form T1221 lines 1 to 3 "Enter the amount of qualifying expenses." (one line for each
    # corporation or slip) and line 4 "Add lines 1 to 3. Enter this amount on line 63220 of
    # your Form ON479.": the expenses of every slip in the list, added.
    CapabilitySelection(
        name="ca-on/flow_through_share_expenses",
        params={},
        consumes={"slips": "ca-on/flow_through_share_slips"},
        produces={"output": "ca-on/flow_through_share_expenses"},
    ),
    # Form T1221 "You must be a resident of Ontario on the last day of the tax year to claim this
    # credit.": 0 when the filer was not a resident of Ontario on the last day of the tax year
    # (the count ON428 reads for "You were not a resident of Ontario on December 31, 2025"), else
    # 1.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca-on/flow_through_share_conditions"},
        consumes={
            "counts": ("ca-on/not_resident_of_ontario_at_year_end_checked",),
            "amounts": (),
        },
        produces={"output": "ca-on/flow_through_share_claimable"},
    ),
    # Form T1221 line 4, entered on ON479 line 17 and line 63220 only by a filer who may claim the
    # credit, so line 4 once, else "0".
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/flow_through_share_expenses",
            "count": "ca-on/flow_through_share_claimable",
        },
        produces={"output": "ca-on/flow_through_share_expenses_claimed"},
    ),
    # Form ON479 line 17 and line 63220 "Enter your total expenses from your Form T1221.
    # multiplied by 5% =": the 5% on T1221 line 4.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/flow_through_share_rate"},
        consumes={"base": "ca-on/flow_through_share_expenses_claimed"},
        produces={"output": "ca-on/flow_through_share_credit"},
    ),
    # Line 18 "Add lines 1, 2, 13, 14, 16, and 17. =": lines 1, 2 (line 63050, Schedule
    # ON479-A's line 8), 13, 14, 16 and 17, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/fertility_credit",
                "ca-on/care_credit",
                "ca-on/seniors_care_credit",
                "ca-on/seniors_transit_credit",
                "ca-on/political_credit",
                "ca-on/flow_through_share_credit",
            )
        },
        produces={"output": "ca-on/ontario_credits_subtotal"},
    ),
    # Worksheet ON479, "Line 20 - Ontario co-operative education tax credit", line 5
    # "400,000.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/coop_education_payroll_threshold"},
        consumes={},
        produces={"output": "ca-on/coop_education_payroll_threshold"},
    ),
    # Line 6 "Line 4 minus line 5 (if negative, enter "0")": line 4 "Total salaries and wages
    # paid in the 2024 taxation year" less the threshold.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/coop_education_payroll",
            "less": "ca-on/coop_education_payroll_threshold",
        },
        produces={"output": "ca-on/coop_education_payroll_over_threshold"},
    ),
    # Line 7 "200,000.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/coop_education_payroll_range"},
        consumes={},
        produces={"output": "ca-on/coop_education_payroll_range"},
    ),
    # Line 8 "Line 6 divided by line 7".
    CapabilitySelection(
        name="ca-on/quotient",
        params={},
        consumes={
            "dividend": "ca-on/coop_education_payroll_over_threshold",
            "divisor": "ca-on/coop_education_payroll_range",
        },
        produces={"output": "ca-on/coop_education_phase_out_share"},
    ),
    # Line 9 "1.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/coop_education_full_share"},
        consumes={},
        produces={"output": "ca-on/coop_education_full_share"},
    ),
    # Line 11 "Line 9 minus line 10 (if negative, enter "0")": line 10 is "Amount from line 8
    # above", so line 8 itself is taken off line 9.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/coop_education_full_share",
            "less": "ca-on/coop_education_phase_out_share",
        },
        produces={"output": "ca-on/coop_education_remaining_share"},
    ),
    # Lines 1, 3, 12 and 13 for each qualifying work placement, and ON479 line 20 and line
    # 63300 "Enter the total amount claimed for all qualifying work placements. (maximum
    # $3,000 per student)": the total of the placements' line 13.
    CapabilitySelection(
        name="ca-on/coop_education_credit",
        params={
            "expenditure_rate": "ca-on/coop_education_expenditure_rate",
            "supplement_rate": "ca-on/coop_education_supplement_rate",
            "maximum": "ca-on/coop_education_maximum",
        },
        consumes={
            "placements": "ca-on/coop_education_placements",
            "remaining_share": "ca-on/coop_education_remaining_share",
        },
        produces={"output": "ca-on/coop_education_credit"},
    ),
    # ON479 line 63260 "Number of eligible work placements your business or partnership is
    # claiming under the Ontario co-operative education tax credit program": the number of
    # placements in the list.
    CapabilitySelection(
        name="ca-on/record_count",
        params={},
        consumes={"records": "ca-on/coop_education_placements"},
        produces={"output": "ca-on/coop_education_placement_count"},
    ),
    # Line 21 "Line 19 plus line 20 Enter this amount online 47900 of your return. Ontario
    # credits =": line 19 "Amount from line 18 of the previous page" carries line 18, and
    # line 20 is the co-operative education credit.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/ontario_credits_subtotal", "ca-on/coop_education_credit")},
        produces={"output": "ca-on/ontario_credits"},
    ),
    # The Ontario opportunities fund, on the T1 provincial pages, line 1 "Amount from line 48400
    # above": the refund.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/refund",)},
        produces={"output": "ca-on/refund_before_donation"},
    ),
    # Line 2 and line 46500 "Your donation to the Ontario opportunities fund", at most line 1
    # "Amount from line 48400 above" (the refund, from which the form takes "some or all"): an
    # amount above it is an input error, not a cap, so the subtract below reads the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/opportunities_fund_donation",
            "bound": "ca-on/refund_before_donation",
        },
        produces={"output": "ca-on/opportunities_fund_donation_checked"},
    ),
    # Line 3 and line 46600 "Net refund (line 1 minus line 2) =": line 1 less line 2 and line
    # 46500 "Your donation to the Ontario opportunities fund", as checked.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca-on/refund_before_donation",
            "less": "ca-on/opportunities_fund_donation_checked",
        },
        produces={"output": "ca-on/net_refund"},
    ),
}

WIRING = {
    (
        AtMost,
        frozenset({COMMUNITY_FOOD_PROGRAM_DONATIONS, DONATIONS_AND_GIFTS_TOTAL}),
        frozenset({COMMUNITY_FOOD_PROGRAM_DONATIONS_APPLIED}),
    ),
    (
        ApplyRate,
        frozenset({COMMUNITY_FOOD_PROGRAM_DONATIONS_APPLIED}),
        frozenset({COMMUNITY_FOOD_PROGRAM_CREDIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_TAX_AFTER_LIFT_CREDIT, COMMUNITY_FOOD_PROGRAM_CREDIT}),
        frozenset({ONTARIO_TAX_AFTER_FOOD_CREDIT}),
    ),
    (
        GreaterOf,
        frozenset({ontario.SPLIT_INCOME_LINE_50, ONTARIO_TAX_AFTER_FOOD_CREDIT}),
        frozenset({ontario.SPLIT_INCOME_LINE_52}),
    ),
    (
        Sum,
        frozenset({TAXABLE_INCOME, TOTAL_SPLIT_INCOME}),
        frozenset({ontario.HEALTH_PREMIUM_INCOME}),
    ),
    (
        TieredSurcharge,
        frozenset({ontario.HEALTH_PREMIUM_INCOME}),
        frozenset({ONTARIO_HEALTH_PREMIUM}),
    ),
    (
        Sum,
        frozenset({ontario.SPLIT_INCOME_LINE_52, ONTARIO_HEALTH_PREMIUM}),
        frozenset({ONTARIO_TAX}),
    ),
    (ApplyRate, frozenset({FERTILITY_EXPENSES}), frozenset({FERTILITY_CREDIT_BEFORE_MAXIMUM})),
    (CappedAmount, frozenset({FERTILITY_CREDIT_BEFORE_MAXIMUM}), frozenset({FERTILITY_CREDIT})),
    (
        SumNotBelowZero,
        frozenset({TOSI_ADJUSTED_NET_INCOME, CHILD_CARE_EXPENSES, SOCIAL_BENEFITS_REPAYMENT}),
        frozenset({CARE_ADJUSTED_INCOME}),
    ),
    (
        Sum,
        frozenset({CARE_ADJUSTED_INCOME, CARE_SUPPORTING_PERSONS_ADJUSTED_INCOME}),
        frozenset({CARE_FAMILY_ADJUSTED_INCOME}),
    ),
    (
        RateByIncomeBand,
        frozenset({CARE_FAMILY_ADJUSTED_INCOME}),
        frozenset({CARE_CREDIT_PERCENTAGE}),
    ),
    (
        ApplyChosenRate,
        frozenset({CHILD_CARE_EXPENSES, CARE_CREDIT_PERCENTAGE}),
        frozenset({CARE_CREDIT}),
    ),
    (ApplyRate, frozenset({ontario.MEDICAL_CLAIM}), frozenset({SENIORS_CARE_BEFORE_MAXIMUM})),
    (CappedAmount, frozenset({SENIORS_CARE_BEFORE_MAXIMUM}), frozenset({SENIORS_CARE_AMOUNT})),
    (
        Sum,
        frozenset({TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO, SPOUSE_NET_INCOME}),
        frozenset({SENIORS_CARE_FAMILY_NET_INCOME}),
    ),
    (CreditAmount, frozenset(), frozenset({SENIORS_CARE_BASE_AMOUNT})),
    (
        SubtractNotBelowZero,
        frozenset({SENIORS_CARE_FAMILY_NET_INCOME, SENIORS_CARE_BASE_AMOUNT}),
        frozenset({SENIORS_CARE_INCOME_OVER_BASE}),
    ),
    (
        ApplyRate,
        frozenset({SENIORS_CARE_INCOME_OVER_BASE}),
        frozenset({SENIORS_CARE_REDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({SENIORS_CARE_AMOUNT, SENIORS_CARE_REDUCTION}),
        frozenset({SENIORS_CARE_BEFORE_CLAIM}),
    ),
    (
        TimesCount,
        frozenset({SENIORS_CARE_BEFORE_CLAIM, CLAIMS_SENIORS_CARE_CREDIT_CHECKED}),
        frozenset({SENIORS_CARE_CREDIT}),
    ),
    (CreditAmount, frozenset(), frozenset({SENIORS_TRANSIT_MAXIMUM})),
    (
        AtMost,
        frozenset({SENIORS_TRANSIT_PAID, SENIORS_TRANSIT_MAXIMUM}),
        frozenset({SENIORS_TRANSIT_AMOUNT_PAID_CHECKED}),
    ),
    (
        ApplyRate,
        frozenset({SENIORS_TRANSIT_AMOUNT_PAID_CHECKED}),
        frozenset({SENIORS_TRANSIT_CREDIT}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.POLITICAL_CREDIT_COLUMN_1_LINE_2})),
    (
        SubtractNotBelowZero,
        frozenset({ontario.POLITICAL_CONTRIBUTIONS, ontario.POLITICAL_CREDIT_COLUMN_1_LINE_2}),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_1_LINE_3}),
    ),
    (
        ApplyRate,
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_1_LINE_3}),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_1_LINE_5}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.POLITICAL_CREDIT_COLUMN_1_LINE_6})),
    (
        FlowThroughShareExpenses,
        frozenset({FLOW_THROUGH_SHARE_SLIPS}),
        frozenset({FLOW_THROUGH_SHARE_EXPENSES}),
    ),
    (
        CountByConditions,
        frozenset({ontario.NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED}),
        frozenset({FLOW_THROUGH_SHARE_CLAIMABLE}),
    ),
    (
        TimesCount,
        frozenset({FLOW_THROUGH_SHARE_EXPENSES, FLOW_THROUGH_SHARE_CLAIMABLE}),
        frozenset({FLOW_THROUGH_SHARE_EXPENSES_CLAIMED}),
    ),
    (
        ApplyRate,
        frozenset({FLOW_THROUGH_SHARE_EXPENSES_CLAIMED}),
        frozenset({FLOW_THROUGH_SHARE_CREDIT}),
    ),
    (
        Sum,
        frozenset(
            {ontario.POLITICAL_CREDIT_COLUMN_1_LINE_5, ontario.POLITICAL_CREDIT_COLUMN_1_LINE_6}
        ),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_1_LINE_7}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.POLITICAL_CREDIT_COLUMN_2_LINE_2})),
    (
        SubtractNotBelowZero,
        frozenset({ontario.POLITICAL_CONTRIBUTIONS, ontario.POLITICAL_CREDIT_COLUMN_2_LINE_2}),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_2_LINE_3}),
    ),
    (
        ApplyRate,
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_2_LINE_3}),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_2_LINE_5}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.POLITICAL_CREDIT_COLUMN_2_LINE_6})),
    (
        Sum,
        frozenset(
            {ontario.POLITICAL_CREDIT_COLUMN_2_LINE_5, ontario.POLITICAL_CREDIT_COLUMN_2_LINE_6}
        ),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_2_LINE_7}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.POLITICAL_CREDIT_COLUMN_3_LINE_2})),
    (
        SubtractNotBelowZero,
        frozenset({ontario.POLITICAL_CONTRIBUTIONS, ontario.POLITICAL_CREDIT_COLUMN_3_LINE_2}),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_3_LINE_3}),
    ),
    (
        ApplyRate,
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_3_LINE_3}),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_3_LINE_5}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.POLITICAL_CREDIT_COLUMN_3_LINE_6})),
    (
        Sum,
        frozenset(
            {ontario.POLITICAL_CREDIT_COLUMN_3_LINE_5, ontario.POLITICAL_CREDIT_COLUMN_3_LINE_6}
        ),
        frozenset({ontario.POLITICAL_CREDIT_COLUMN_3_LINE_7}),
    ),
    (
        ChooseByRange,
        frozenset(
            {
                ontario.POLITICAL_CONTRIBUTIONS,
                ontario.POLITICAL_CREDIT_COLUMN_2_LINE_2,
                ontario.POLITICAL_CREDIT_COLUMN_3_LINE_2,
                ontario.POLITICAL_CREDIT_COLUMN_1_LINE_7,
                ontario.POLITICAL_CREDIT_COLUMN_2_LINE_7,
                ontario.POLITICAL_CREDIT_COLUMN_3_LINE_7,
            }
        ),
        frozenset({ontario.POLITICAL_CREDIT_BEFORE_MAXIMUM}),
    ),
    (
        CappedAmount,
        frozenset({ontario.POLITICAL_CREDIT_BEFORE_MAXIMUM}),
        frozenset({ontario.POLITICAL_CREDIT}),
    ),
    (
        Sum,
        frozenset(
            {
                FERTILITY_CREDIT,
                CARE_CREDIT,
                SENIORS_CARE_CREDIT,
                SENIORS_TRANSIT_CREDIT,
                ontario.POLITICAL_CREDIT,
                FLOW_THROUGH_SHARE_CREDIT,
            }
        ),
        frozenset({ONTARIO_CREDITS_SUBTOTAL}),
    ),
    (CreditAmount, frozenset(), frozenset({COOP_EDUCATION_PAYROLL_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({COOP_EDUCATION_PAYROLL, COOP_EDUCATION_PAYROLL_THRESHOLD}),
        frozenset({COOP_EDUCATION_PAYROLL_OVER_THRESHOLD}),
    ),
    (CreditAmount, frozenset(), frozenset({COOP_EDUCATION_PAYROLL_RANGE})),
    (
        Quotient,
        frozenset({COOP_EDUCATION_PAYROLL_OVER_THRESHOLD, COOP_EDUCATION_PAYROLL_RANGE}),
        frozenset({COOP_EDUCATION_PHASE_OUT_SHARE}),
    ),
    (CreditAmount, frozenset(), frozenset({COOP_EDUCATION_FULL_SHARE})),
    (
        SubtractNotBelowZero,
        frozenset({COOP_EDUCATION_FULL_SHARE, COOP_EDUCATION_PHASE_OUT_SHARE}),
        frozenset({COOP_EDUCATION_REMAINING_SHARE}),
    ),
    (
        CoopEducationCredit,
        frozenset({COOP_EDUCATION_PLACEMENTS, COOP_EDUCATION_REMAINING_SHARE}),
        frozenset({COOP_EDUCATION_CREDIT}),
    ),
    (
        RecordCount,
        frozenset({COOP_EDUCATION_PLACEMENTS}),
        frozenset({COOP_EDUCATION_PLACEMENT_COUNT}),
    ),
    (
        Sum,
        frozenset({ONTARIO_CREDITS_SUBTOTAL, COOP_EDUCATION_CREDIT}),
        frozenset({ONTARIO_CREDITS}),
    ),
    (Sum, frozenset({REFUND}), frozenset({ontario.REFUND_BEFORE_DONATION})),
    (
        AtMost,
        frozenset({ontario.OPPORTUNITIES_FUND_DONATION, ontario.REFUND_BEFORE_DONATION}),
        frozenset({ontario.OPPORTUNITIES_FUND_DONATION_CHECKED}),
    ),
    (
        Subtract,
        frozenset({ontario.REFUND_BEFORE_DONATION, ontario.OPPORTUNITIES_FUND_DONATION_CHECKED}),
        frozenset({ontario.NET_REFUND}),
    ),
}
