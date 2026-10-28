"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.capped_amount import CappedAmount
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.greater_of import GreaterOf
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.catalog import (
    EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME,
    RDSP_INCOME,
    RDSP_INCOME_REPAYMENT_CHECKED,
    SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
    SPOUSE_RDSP_INCOME,
    SPOUSE_RDSP_INCOME_REPAYMENT,
    SPOUSE_UCCB_REPAYMENT,
    SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT,
    TOSI_ADJUSTED_NET_INCOME,
    UCCB_REPAYMENT,
    UNIVERSAL_CHILD_CARE_BENEFIT,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT,
    LIFT_CREDIT_BEFORE_MAXIMUM,
    LIFT_EMPLOYMENT_INCOME,
    LIFT_MAXIMUM_CREDIT,
    LIFT_REDUCTION,
    ONTARIO_TAX_AFTER_FOREIGN_TAX_CREDIT,
    ONTARIO_TAX_AFTER_LIFT_CREDIT,
)

# Schedule ON428-A asks no input of its own: the spouse or common-law partner on December 31 is the
# shared fact of the form `ca/spouse_on_december_31`, read as the total below.
INPUTS: frozenset[str] = frozenset()

OUTPUTS = frozenset[str]()

STEPS = {
    # Schedule ON428-A line 3 "Line 1 plus line 2" (line 1 "Amount from line 10100 of your return"
    # and line 2 "Amount from line 10400 of your return"), in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/employment_income", "ca/other_employment_income")},
        produces={"output": "ca-on/lift_employment_income"},
    ),
    # Schedule ON428-A line 5 "Line 3 multiplied by the percentage from line 4 (maximum $875)",
    # line 4 "Applicable rate 5.05%": the rate on line 3, before its maximum.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/lift_rate"},
        consumes={"base": "ca-on/lift_employment_income"},
        produces={"output": "ca-on/lift_credit_before_maximum"},
    ),
    # Line 5's "(maximum $875)" and Part A line 14 "Amount from line 5 above (maximum
    # $875)".
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/lift_maximum"},
        consumes={"base": "ca-on/lift_credit_before_maximum"},
        produces={"output": "ca-on/lift_maximum_credit"},
    ),
    # Lines 6 to 9: line 6 "Net income from line 23600 of your return (or the amount you would
    # have entered if the instructions on line 23600 said "if negative, show in brackets")",
    # the TOSI-adjusted net income of Form T1206 Part 1 line 6 in its place, which is not floored
    # at zero; line 7 "Amount from line
    # 21300 of your return", the UCCB repayment; line 8 "Amount of registered disability
    # savings plan (RDSP) income repayment included on line 23200 of your return"; and line 9
    # "Add lines 6 to 8.", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/tosi_adjusted_net_income",
                "ca/uccb_repayment",
                "ca/rdsp_income_repayment_checked",
            )
        },
        produces={"output": "ca-on/lift_net_income_and_repayments"},
    ),
    # Lines 10 to 12: line 10 "Amount from line 11700 of your return", the universal child care
    # benefit; line 11 "Amount of RDSP income included on line 12500 of your return"; and line
    # 12 "Line 10 plus line 11", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/universal_child_care_benefit", "ca/rdsp_income")},
        produces={"output": "ca-on/lift_uccb_and_rdsp_income"},
    ),
    # Line 13 "Line 9 minus line 12 (if negative, enter "0") Your adjusted net income".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/lift_net_income_and_repayments",
            "less": "ca-on/lift_uccb_and_rdsp_income",
        },
        produces={"output": "ca-on/lift_adjusted_net_income"},
    ),
    # Lines 15 to 19: line 15 "Amount from line 13 above", the adjusted net income; line 16
    # "Individual income threshold 32,500.00"; line 17 "Line 15 minus line 16 (if negative,
    # enter "0")"; line 18 "Applicable rate 5%"; line 19 "Line 17 multiplied by the
    # percentage from line 18".
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca-on/lift_reduction"},
        consumes={"base": "ca-on/lift_adjusted_net_income"},
        produces={"output": "ca-on/lift_reduction"},
    ),
    # Line 20 "Line 14 minus line 19 (if negative, enter "0") Enter this amount on line 62140
    # of your Form ON428.", the credit for a single individual (Part A).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca-on/lift_maximum_credit", "less": "ca-on/lift_reduction"},
        produces={"output": "ca-on/lift_credit_single"},
    ),
    # Part B, lines 21 to 24: line 21 "Net income from line 23600 of your spouse's or common-law
    # partner's return (or the amount they would have entered if the instructions on line
    # 23600 said "if negative, show in brackets")", a caller's figure that may be negative;
    # line 22 "Amount from line 21300 of your spouse's or common-law partner's return"; line 23
    # "Amount of RDSP income repayment included on line 23200 of your spouse's or common-law
    # partner's return"; and line 24 "Add lines 21 to 23.", in line order. Lines 21 to 23 are
    # the caller's existing spouse inputs, the same figures the Federal Worksheet for line
    # 45200 uses (one shared input, entered once).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/spouse_net_income_before_adjustments",
                "ca/spouse_uccb_repayment",
                "ca/spouse_rdsp_income_repayment",
            )
        },
        produces={"output": "ca-on/lift_spouse_net_income_and_repayments"},
    ),
    # Lines 25 to 27: line 25 "Amount from line 11700 of your spouse's or common-law partner's
    # return"; line 26 "Amount of RDSP income included on line 12500 of your spouse's or
    # common-law partner's return"; and line 27 "Line 25 plus line 26", in line order. Lines 25
    # and 26 are likewise the caller's existing spouse inputs, shared with the Federal Worksheet
    # for line 45200.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/spouse_universal_child_care_benefit",
                "ca/spouse_rdsp_income",
            )
        },
        produces={"output": "ca-on/lift_spouse_uccb_and_rdsp_income"},
    ),
    # Line 28 "Line 24 minus line 27 (if negative, enter "0") Your spouse's or common-law
    # partner's adjusted net income".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/lift_spouse_net_income_and_repayments",
            "less": "ca-on/lift_spouse_uccb_and_rdsp_income",
        },
        produces={"output": "ca-on/lift_spouse_adjusted_net_income"},
    ),
    # Line 31 "Individual income threshold 32,500.00", the dataset as an artifact of the same
    # name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/lift_individual_income_threshold"},
        consumes={},
        produces={"output": "ca-on/lift_individual_income_threshold"},
    ),
    # Lines 30 to 32: line 30 "Amount from line 13 of the previous page", the adjusted net
    # income, and line 32 "Line 30 minus line 31 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/lift_adjusted_net_income",
            "less": "ca-on/lift_individual_income_threshold",
        },
        produces={"output": "ca-on/lift_excess_over_individual_threshold"},
    ),
    # Lines 33 to 35: line 33 "Amount from line 30 above" and line 34 "Amount from line 28
    # above", and line 35 "Line 33 plus line 34 Adjusted family net income", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/lift_adjusted_net_income",
                "ca-on/lift_spouse_adjusted_net_income",
            )
        },
        produces={"output": "ca-on/lift_family_net_income"},
    ),
    # Line 36 "Family income threshold 65,0000.00", printed with a typo, which is 65,000.00: the
    # dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/lift_family_income_threshold"},
        consumes={},
        produces={"output": "ca-on/lift_family_income_threshold"},
    ),
    # Line 37 "Line 35 minus line 36 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/lift_family_net_income",
            "less": "ca-on/lift_family_income_threshold",
        },
        produces={"output": "ca-on/lift_excess_over_family_threshold"},
    ),
    # Line 38 "Enter whichever is more: amount from line 32 or line 37.", in line order.
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={
            "amounts": (
                "ca-on/lift_excess_over_individual_threshold",
                "ca-on/lift_excess_over_family_threshold",
            )
        },
        produces={"output": "ca-on/lift_greater_excess"},
    ),
    # Line 39 "Applicable rate 5%" and line 40 "Line 38 multiplied by the percentage from line
    # 39", applied once to the greater excess.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/lift_family_rate"},
        consumes={"base": "ca-on/lift_greater_excess"},
        produces={"output": "ca-on/lift_family_reduction"},
    ),
    # Line 41 "Line 29 minus line 40 (if negative, enter "0") Enter this amount on line 62140
    # of your Form ON428.", the credit for an individual with a spouse or common-law partner
    # (Part B), where line 29 "Amount from line 5 of the previous page (maximum $875)" is the
    # credit at most its maximum.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/lift_maximum_credit",
            "less": "ca-on/lift_family_reduction",
        },
        produces={"output": "ca-on/lift_credit_with_spouse"},
    ),
    # ON428 line 85 "Low-income individuals and families tax (LIFT) credit (complete Schedule
    # ON428-A)": "If you were single at the end of the year, complete Part A" and "If you had a
    # spouse or common-law partner at the end of the year, complete Part B", so a count of 1
    # (a caller's 0 or 1, entered as 0 when the spouse or common-law partner died during the
    # year, as "complete Part A as if you were single") chooses line 41 over line 20.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/spouse_or_common_law_partner_on_december_31_total",
            "when_none": "ca-on/lift_credit_single",
            "when_any": "ca-on/lift_credit_with_spouse",
        },
        produces={"output": "ca-on/lift_credit"},
    ),
    # ON428 line 86 "Line 84 minus line 85 (if negative, enter "0")": line 84 "Amount from line
    # 83 of the previous page" carries line 83 "Line 81 minus line 82 (if negative, enter "0")",
    # the Ontario tax after the provincial foreign tax credit.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_after_foreign_tax_credit",
            "less": "ca-on/lift_credit",
        },
        produces={"output": "ca-on/ontario_tax_after_lift_credit"},
    ),
}

WIRING = {
    (
        Sum,
        frozenset({EMPLOYMENT_INCOME, OTHER_EMPLOYMENT_INCOME}),
        frozenset({LIFT_EMPLOYMENT_INCOME}),
    ),
    (ApplyRate, frozenset({LIFT_EMPLOYMENT_INCOME}), frozenset({LIFT_CREDIT_BEFORE_MAXIMUM})),
    (CappedAmount, frozenset({LIFT_CREDIT_BEFORE_MAXIMUM}), frozenset({LIFT_MAXIMUM_CREDIT})),
    (
        Sum,
        frozenset({TOSI_ADJUSTED_NET_INCOME, UCCB_REPAYMENT, RDSP_INCOME_REPAYMENT_CHECKED}),
        frozenset({ontario.LIFT_NET_INCOME_AND_REPAYMENTS}),
    ),
    (
        Sum,
        frozenset({UNIVERSAL_CHILD_CARE_BENEFIT, RDSP_INCOME}),
        frozenset({ontario.LIFT_UCCB_AND_RDSP_INCOME}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ontario.LIFT_NET_INCOME_AND_REPAYMENTS, ontario.LIFT_UCCB_AND_RDSP_INCOME}),
        frozenset({ontario.LIFT_ADJUSTED_NET_INCOME}),
    ),
    (
        TieredSurcharge,
        frozenset({ontario.LIFT_ADJUSTED_NET_INCOME}),
        frozenset({LIFT_REDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({LIFT_MAXIMUM_CREDIT, LIFT_REDUCTION}),
        frozenset({ontario.LIFT_CREDIT_SINGLE}),
    ),
    (
        Sum,
        frozenset(
            {
                SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
                SPOUSE_UCCB_REPAYMENT,
                SPOUSE_RDSP_INCOME_REPAYMENT,
            }
        ),
        frozenset({ontario.LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS}),
    ),
    (
        Sum,
        frozenset(
            {
                SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT,
                SPOUSE_RDSP_INCOME,
            }
        ),
        frozenset({ontario.LIFT_SPOUSE_UCCB_AND_RDSP_INCOME}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                ontario.LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS,
                ontario.LIFT_SPOUSE_UCCB_AND_RDSP_INCOME,
            }
        ),
        frozenset({ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.LIFT_INDIVIDUAL_INCOME_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({ontario.LIFT_ADJUSTED_NET_INCOME, ontario.LIFT_INDIVIDUAL_INCOME_THRESHOLD}),
        frozenset({ontario.LIFT_EXCESS_OVER_INDIVIDUAL_THRESHOLD}),
    ),
    (
        Sum,
        frozenset({ontario.LIFT_ADJUSTED_NET_INCOME, ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME}),
        frozenset({ontario.LIFT_FAMILY_NET_INCOME}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.LIFT_FAMILY_INCOME_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({ontario.LIFT_FAMILY_NET_INCOME, ontario.LIFT_FAMILY_INCOME_THRESHOLD}),
        frozenset({ontario.LIFT_EXCESS_OVER_FAMILY_THRESHOLD}),
    ),
    (
        GreaterOf,
        frozenset(
            {
                ontario.LIFT_EXCESS_OVER_INDIVIDUAL_THRESHOLD,
                ontario.LIFT_EXCESS_OVER_FAMILY_THRESHOLD,
            }
        ),
        frozenset({ontario.LIFT_GREATER_EXCESS}),
    ),
    (
        ApplyRate,
        frozenset({ontario.LIFT_GREATER_EXCESS}),
        frozenset({ontario.LIFT_FAMILY_REDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({LIFT_MAXIMUM_CREDIT, ontario.LIFT_FAMILY_REDUCTION}),
        frozenset({ontario.LIFT_CREDIT_WITH_SPOUSE}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
                ontario.LIFT_CREDIT_SINGLE,
                ontario.LIFT_CREDIT_WITH_SPOUSE,
            }
        ),
        frozenset({LIFT_CREDIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_TAX_AFTER_FOREIGN_TAX_CREDIT, LIFT_CREDIT}),
        frozenset({ONTARIO_TAX_AFTER_LIFT_CREDIT}),
    ),
}
