"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_engine.jurisdictions.ca.capabilities.divided_by_rate import DividedByRate
from tax_engine.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    DONATIONS_FIRST_TIER,
    DONATIONS_OVER_FIRST_TIER,
    EI_PREMIUMS,
    EI_PREMIUMS_ON_SELF_EMPLOYMENT,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    SPLIT_INCOME_LINE_18,
    SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED,
    STUDENT_LOAN_INTEREST,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
    TOTAL_SPLIT_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.catalog import (
    ONTARIO_BASIC_TAX,
    ONTARIO_SURTAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_AFTER_DIVIDEND_CREDIT,
    ONTARIO_TAX_BEFORE_DIVIDEND_CREDIT,
    ONTARIO_TAX_LESS_DIVIDEND_CREDIT,
    ONTARIO_TAX_WITH_SURTAX,
)

INPUTS = frozenset[str]()

OUTPUTS = frozenset(
    {
        "ca-on/ontario_tax_less_dividend_credit",
        "ca-on/tosi_adjusted_taxable_income",
    }
)

STEPS = {
    # ON428 line 33 and line 58560 "Your unused tuition and education amounts (attach Schedule
    # ON(S11))" and ON428 line 34 and line 58640 "Amounts transferred from your spouse or
    # common-law partner (attach Schedule ON(S2))", parts of line 35 "Add lines 31 to 34. =". Line
    # 44 (line 58800) "Line 35 plus line 43" adds the medical expenses after them, so the claims
    # sit between the disability amount transferred and the medical claim, in the form's order.
    # The adoption and pension amounts (lines 23 and 27) are in line 31, so they are in line 35 too.
    # The student loan interest (line 32, the amount from line 31900 of the federal return) sits
    # between lines 31 and 33, so it is a part here, after the disability amount transferred and
    # before the unused tuition claim. Line 31 (the sum Schedule ON(S11) line 3 reads) does not take
    # lines 32 to 34.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/basic_personal_amount",
                "ca-on/age_amount",
                "ca-on/spouse_amount",
                "ca-on/eligible_dependant_amount",
                "ca-on/caregiver_amount",
                "ca/cpp_base_contributions_on_return",
                "ca/cpp_base_contributions_on_self_employment_and_other_earnings",
                "ca/ei_premiums",
                "ca/ei_premiums_on_self_employment",
                "ca-on/adoption_credit",
                "ca-on/pension_income_credit",
                "ca-on/disability_amount_for_self",
                "ca-on/disability_transferred_amount",
                "ca/student_loan_interest",
                "ca-on/unused_tuition_claimed",
                "ca-on/amounts_transferred_from_spouse",
                "ca-on/medical_claim",
            )
        },
        produces={"output": "ca-on/non_refundable_credit_amounts"},
    ),
    # ON428 line 46 (line 58840) "Line 44 multiplied by the percentage from line 45": the
    # Ontario credit rate is applied once, to the total of credit amounts. It is the first of
    # the two lines that line 50 adds.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/credit_rate"},
        consumes={"base": "ca-on/non_refundable_credit_amounts"},
        produces={"output": "ca-on/credit_amounts_at_credit_rate"},
    ),
    # ON428 line 47 "Amount from line 13 of your federal Schedule 9" "multiplied by 5.05%":
    # 5.05% of the first $200 of the donations and gifts, the federal Schedule 9 line 13.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/donation_first_tier_rate"},
        consumes={"base": "ca/donations_first_tier"},
        produces={"output": "ca-on/donations_first_tier_credit"},
    ),
    # ON428 line 48 "Amount from line 14 of your federal Schedule 9" "multiplied by 11.16%":
    # 11.16% of the rest of the donations and gifts, the federal Schedule 9 line 14.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/donation_over_first_tier_rate"},
        consumes={"base": "ca/donations_over_first_tier"},
        produces={"output": "ca-on/donations_over_first_tier_credit"},
    ),
    # ON428 line 49 and line 58969 "Line 47 plus line 48".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/donations_first_tier_credit",
                "ca-on/donations_over_first_tier_credit",
            )
        },
        produces={"output": "ca-on/donations_and_gifts_credit"},
    ),
    # ON428 line 50 and line 61500 "Line 46 plus line 49 Enter this amount on line 52.
    # Ontario non-refundable tax credits": line 46 (line 58840) and line 49 (line 58969), in
    # line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca-on/credit_amounts_at_credit_rate", "ca-on/donations_and_gifts_credit")
        },
        produces={"output": "ca-on/non_refundable_tax_credits"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_basic_tax",
            "less": "ca-on/non_refundable_tax_credits",
        },
        produces={"output": "ca-on/ontario_tax_after_credits"},
    ),
    # Form T1206 Part 3 line 33 "The amount from line 31 multiplied by the tax rate you entered on
    # line 32. Enter this amount on the line of your Form 428 shown in column 4 in Chart C on page
    # 5.", line 31 being "Total split income from line 4" and the rate Chart C column 2 for Ontario,
    # 20.53%, column 4 being ON428 line 54 and line 61510 "Ontario tax on split income (complete
    # Form T1206)".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/split_income_rate"},
        consumes={"base": "ca/total_split_income"},
        produces={"output": "ca-on/ontario_tax_on_split_income"},
    ),
    # Form T1206 Part 3 line 33C "TOSI-adjusted taxable income: Amount from line 33A divided by
    # the tax rate you entered on line 33B", line 33A being the amount from line 33 and line 33B
    # the rate of Chart C column 3 for Ontario, 5.05%. Nothing on the Ontario return reads it, so
    # it is a declared output.
    CapabilitySelection(
        name="ca/divided_by_rate",
        params={"rate": "ca-on/tosi_taxable_income_rate"},
        consumes={"dividend": "ca-on/ontario_tax_on_split_income"},
        produces={"output": "ca-on/tosi_adjusted_taxable_income"},
    ),
    # "Provincial or territorial disability tax credit (DTC)": line 34 "DTC from line 58440 of your
    # provincial or territorial Form 428" (the Ontario amount for self, computed on the Ontario
    # personal amounts steps) and line 35 "DTC transferred from a dependant from line 58480 of your
    # provincial or territorial Form 428" (the Ontario disability amount transferred from a
    # dependant), line 36 "Line 34 plus line 35".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/disability_amount_for_self",
                "ca-on/disability_transferred_amount",
            )
        },
        produces={"output": "ca-on/split_income_line_36"},
    ),
    # Line 38, line 36 multiplied by "the tax rate you entered on line 37" (Chart C column 3 for
    # Ontario, 5.05%), and line 39 "Line 33 minus line 38", which prints no floor.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/split_income_disability_credit_rate"},
        consumes={"base": "ca-on/split_income_line_36"},
        produces={"output": "ca-on/split_income_line_38"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_on_split_income",
            "less": "ca-on/split_income_line_38",
        },
        produces={"output": "ca-on/split_income_line_39"},
    ),
    # "Provincial or territorial dividend tax credit on split income for eligible dividends and
    # dividends other than eligible dividends": line 40 "Amount from line 18" (the federal line 18)
    # times line 41, the eligible dividend tax credit rate (Chart C column 5 for Ontario, 10%), is
    # line 42; line 43 "Amount from line 17" (the federal line 17, the caller's line 2 of Part 1)
    # times line 44, the dividend other than eligible dividend tax credit rate (Chart C column 6 for
    # Ontario, 2.9863%), is line 45.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/split_income_dividend_credit_rate_eligible"},
        consumes={"base": "ca/split_income_line_18"},
        produces={"output": "ca-on/split_income_line_42"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/split_income_dividend_credit_rate_other_than_eligible"},
        consumes={"base": "ca/split_income_dividends_other_than_eligible_checked"},
        produces={"output": "ca-on/split_income_line_45"},
    ),
    # Line 46 "Line 42 plus line 45" and line 47 "Line 39 minus line 46", which prints no floor.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/split_income_line_42",
                "ca-on/split_income_line_45",
            )
        },
        produces={"output": "ca-on/split_income_line_46"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca-on/split_income_line_39", "less": "ca-on/split_income_line_46"},
        produces={"output": "ca-on/split_income_line_47"},
    ),
    # "Provincial or territorial foreign tax credit on split income": line 48 "Amount from line 47
    # on the previous page"; line 49 "Part of the amount from line 68370 on page 8 that is
    # non-business income" over "Part of the amount from line 68380 on page 8 that is non-business
    # income", "× Amount from line number of your Form 428 shown in column 7 in Chart C on page 5"
    # (ON428 line 82), rounded half-up to the cent once; 0 when there is no such income.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca-on/split_income_line_49_rounding"},
        consumes={
            "amount": "ca-on/provincial_foreign_tax_credit",
            "numerator": "ca/split_income_non_business_from_foreign_sources_checked",
            "denominator": "ca/total_non_business_income_from_foreign_sources_checked",
        },
        produces={"output": "ca-on/split_income_line_49"},
    ),
    # Line 50 "Line 48 minus line 49", which prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca-on/split_income_line_47", "less": "ca-on/split_income_line_49"},
        produces={"output": "ca-on/split_income_line_50"},
    ),
    # ON428 line 55 "Line 53 plus line 54 =", line 54 being the Ontario tax on split income of Form
    # T1206 line 33.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/ontario_tax_after_credits",
                "ca-on/ontario_tax_on_split_income",
            )
        },
        produces={"output": "ca-on/ontario_tax_with_split_income"},
    ),
    # ON428 lines 62 and 63 are the amount from line 61, the tax after the minimum tax carryover
    # (wired with lines 59 to 61 in the Ontario alternative minimum tax part). Line 64 "Ontario tax
    # on split income from line 54" and line 65 "Line 63 minus line 64 (if negative, enter "0")",
    # the base of the surtax.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/ontario_tax_on_split_income",)},
        produces={"output": "ca-on/ontario_tax_on_split_income_for_surtax"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_after_minimum_tax_carryover",
            "less": "ca-on/ontario_tax_on_split_income_for_surtax",
        },
        produces={"output": "ca-on/ontario_surtax_base"},
    ),
    # ON428 lines 66 to 68: the surtax on line 65, the Ontario tax with the tax on split income
    # taken out again (lines 63 and 64).
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca-on/surtax"},
        consumes={"base": "ca-on/ontario_surtax_base"},
        produces={"output": "ca-on/ontario_surtax"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca-on/ontario_tax_after_minimum_tax_carryover", "ca-on/ontario_surtax")
        },
        produces={"output": "ca-on/ontario_tax_with_surtax"},
    ),
    # ON428 line 56 "Enter the amount from line 53 above.", line 57 (printed "Line 57 and
    # line and line 61520") "Ontario dividend tax credit (use Worksheet ON428)" and line 58
    # "Line 56 minus line 57 (if negative, enter "0")". Worksheet ON428's "Line 61520 -
    # Ontario dividend tax credit": line A "Amount from line 12000 of your return" and line
    # 1 "Amount from line 12010 of your return Line B" "multiplied by 2.9863%", with no Note
    # 1, so A and B are the whole lines 12000 and 12010, each its own step; line 2 "Amount
    # A minus amount B Line C" "multiplied by 10%"; line 3 "Line 1 plus line 2 Enter this
    # amount on line 61520 of your Form ON428.", which is line 57.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/ontario_tax_after_credits",)},
        produces={"output": "ca-on/ontario_tax_before_dividend_credit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/taxable_dividends",)},
        produces={"output": "ca-on/dividends_amount_a"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/taxable_dividends_other_than_eligible",)},
        produces={"output": "ca-on/dividends_amount_b"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/dividend_credit_rate_other_than_eligible"},
        consumes={"base": "ca-on/dividends_amount_b"},
        produces={"output": "ca-on/other_dividends_credit"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca-on/dividends_amount_a", "less": "ca-on/dividends_amount_b"},
        produces={"output": "ca-on/dividends_amount_a_less_b"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/dividend_credit_rate_eligible"},
        consumes={"base": "ca-on/dividends_amount_a_less_b"},
        produces={"output": "ca-on/eligible_dividends_credit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/other_dividends_credit", "ca-on/eligible_dividends_credit")},
        produces={"output": "ca-on/dividend_tax_credit"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_before_dividend_credit",
            "less": "ca-on/dividend_tax_credit",
        },
        produces={"output": "ca-on/ontario_tax_less_dividend_credit"},
    ),
    # ON428 line 70 "Ontario dividend tax credit from line 57" and line 71 "Line 69 minus
    # line 70 (if negative, enter "0")": line 71, which line 73 then adds to line 72 (the
    # additional tax for minimum tax purposes, in 17_ontario_tax_reduction.yaml).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/dividend_tax_credit",)},
        produces={"output": "ca-on/dividend_credit_from_line_57"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_with_surtax",
            "less": "ca-on/dividend_credit_from_line_57",
        },
        produces={"output": "ca-on/ontario_tax_after_dividend_credit"},
    ),
}

WIRING = {
    (
        Sum,
        frozenset(
            {
                ontario.BASIC_PERSONAL_AMOUNT,
                ontario.AGE_AMOUNT,
                ontario.SPOUSE_AMOUNT,
                ontario.ELIGIBLE_DEPENDANT_AMOUNT,
                ontario.CAREGIVER_AMOUNT,
                CPP_BASE_CONTRIBUTIONS_ON_RETURN,
                CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
                EI_PREMIUMS,
                EI_PREMIUMS_ON_SELF_EMPLOYMENT,
                ontario.ADOPTION_CREDIT,
                ontario.PENSION_INCOME_CREDIT,
                ontario.DISABILITY_AMOUNT_FOR_SELF,
                ontario.DISABILITY_TRANSFERRED_AMOUNT,
                STUDENT_LOAN_INTEREST,
                ontario.UNUSED_TUITION_CLAIMED,
                ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE,
                ontario.MEDICAL_CLAIM,
            }
        ),
        frozenset({ontario.NON_REFUNDABLE_CREDIT_AMOUNTS}),
    ),
    (
        ApplyRate,
        frozenset({ontario.NON_REFUNDABLE_CREDIT_AMOUNTS}),
        frozenset({ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE}),
    ),
    (
        ApplyRate,
        frozenset({DONATIONS_FIRST_TIER}),
        frozenset({ontario.DONATIONS_FIRST_TIER_CREDIT}),
    ),
    (
        ApplyRate,
        frozenset({DONATIONS_OVER_FIRST_TIER}),
        frozenset({ontario.DONATIONS_OVER_FIRST_TIER_CREDIT}),
    ),
    (
        Sum,
        frozenset({ontario.DONATIONS_FIRST_TIER_CREDIT, ontario.DONATIONS_OVER_FIRST_TIER_CREDIT}),
        frozenset({ontario.DONATIONS_AND_GIFTS_CREDIT}),
    ),
    (
        Sum,
        frozenset({ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE, ontario.DONATIONS_AND_GIFTS_CREDIT}),
        frozenset({ontario.NON_REFUNDABLE_TAX_CREDITS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_BASIC_TAX, ontario.NON_REFUNDABLE_TAX_CREDITS}),
        frozenset({ONTARIO_TAX_AFTER_CREDITS}),
    ),
    (ApplyRate, frozenset({TOTAL_SPLIT_INCOME}), frozenset({ontario.ONTARIO_TAX_ON_SPLIT_INCOME})),
    (
        DividedByRate,
        frozenset({ontario.ONTARIO_TAX_ON_SPLIT_INCOME}),
        frozenset({ontario.TOSI_ADJUSTED_TAXABLE_INCOME}),
    ),
    (
        Sum,
        frozenset({ontario.DISABILITY_AMOUNT_FOR_SELF, ontario.DISABILITY_TRANSFERRED_AMOUNT}),
        frozenset({ontario.SPLIT_INCOME_LINE_36}),
    ),
    (
        ApplyRate,
        frozenset({ontario.SPLIT_INCOME_LINE_36}),
        frozenset({ontario.SPLIT_INCOME_LINE_38}),
    ),
    (
        Subtract,
        frozenset({ontario.ONTARIO_TAX_ON_SPLIT_INCOME, ontario.SPLIT_INCOME_LINE_38}),
        frozenset({ontario.SPLIT_INCOME_LINE_39}),
    ),
    (ApplyRate, frozenset({SPLIT_INCOME_LINE_18}), frozenset({ontario.SPLIT_INCOME_LINE_42})),
    (
        ApplyRate,
        frozenset({SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED}),
        frozenset({ontario.SPLIT_INCOME_LINE_45}),
    ),
    (
        Sum,
        frozenset({ontario.SPLIT_INCOME_LINE_42, ontario.SPLIT_INCOME_LINE_45}),
        frozenset({ontario.SPLIT_INCOME_LINE_46}),
    ),
    (
        Subtract,
        frozenset({ontario.SPLIT_INCOME_LINE_39, ontario.SPLIT_INCOME_LINE_46}),
        frozenset({ontario.SPLIT_INCOME_LINE_47}),
    ),
    (
        ApplyRatioOrZero,
        frozenset(
            {
                ontario.PROVINCIAL_FOREIGN_TAX_CREDIT,
                SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED,
                TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
            }
        ),
        frozenset({ontario.SPLIT_INCOME_LINE_49}),
    ),
    (
        Subtract,
        frozenset({ontario.SPLIT_INCOME_LINE_47, ontario.SPLIT_INCOME_LINE_49}),
        frozenset({ontario.SPLIT_INCOME_LINE_50}),
    ),
    (
        Sum,
        frozenset({ONTARIO_TAX_AFTER_CREDITS, ontario.ONTARIO_TAX_ON_SPLIT_INCOME}),
        frozenset({ontario.ONTARIO_TAX_WITH_SPLIT_INCOME}),
    ),
    (
        Sum,
        frozenset({ontario.ONTARIO_TAX_ON_SPLIT_INCOME}),
        frozenset({ontario.ONTARIO_TAX_ON_SPLIT_INCOME_FOR_SURTAX}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER,
                ontario.ONTARIO_TAX_ON_SPLIT_INCOME_FOR_SURTAX,
            }
        ),
        frozenset({ontario.ONTARIO_SURTAX_BASE}),
    ),
    (TieredSurcharge, frozenset({ontario.ONTARIO_SURTAX_BASE}), frozenset({ONTARIO_SURTAX})),
    (
        Sum,
        frozenset({ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER, ONTARIO_SURTAX}),
        frozenset({ONTARIO_TAX_WITH_SURTAX}),
    ),
    (
        Sum,
        frozenset({ONTARIO_TAX_AFTER_CREDITS}),
        frozenset({ONTARIO_TAX_BEFORE_DIVIDEND_CREDIT}),
    ),
    (Sum, frozenset({TAXABLE_DIVIDENDS}), frozenset({ontario.DIVIDENDS_AMOUNT_A})),
    (
        Sum,
        frozenset({TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE}),
        frozenset({ontario.DIVIDENDS_AMOUNT_B}),
    ),
    (
        ApplyRate,
        frozenset({ontario.DIVIDENDS_AMOUNT_B}),
        frozenset({ontario.OTHER_DIVIDENDS_CREDIT}),
    ),
    (
        Subtract,
        frozenset({ontario.DIVIDENDS_AMOUNT_A, ontario.DIVIDENDS_AMOUNT_B}),
        frozenset({ontario.DIVIDENDS_AMOUNT_A_LESS_B}),
    ),
    (
        ApplyRate,
        frozenset({ontario.DIVIDENDS_AMOUNT_A_LESS_B}),
        frozenset({ontario.ELIGIBLE_DIVIDENDS_CREDIT}),
    ),
    (
        Sum,
        frozenset({ontario.OTHER_DIVIDENDS_CREDIT, ontario.ELIGIBLE_DIVIDENDS_CREDIT}),
        frozenset({ontario.DIVIDEND_TAX_CREDIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_TAX_BEFORE_DIVIDEND_CREDIT, ontario.DIVIDEND_TAX_CREDIT}),
        frozenset({ONTARIO_TAX_LESS_DIVIDEND_CREDIT}),
    ),
    (
        Sum,
        frozenset({ontario.DIVIDEND_TAX_CREDIT}),
        frozenset({ontario.DIVIDEND_CREDIT_FROM_LINE_57}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_TAX_WITH_SURTAX, ontario.DIVIDEND_CREDIT_FROM_LINE_57}),
        frozenset({ONTARIO_TAX_AFTER_DIVIDEND_CREDIT}),
    ),
}
