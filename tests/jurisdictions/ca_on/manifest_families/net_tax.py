"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.greater_of import GreaterOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_calculator.jurisdictions.ca.catalog import (
    ADVANCED_CANADA_WORKERS_BENEFIT,
    CPP_PART_4_COMPLETED_CHECKED,
    CPP_PART_5_COMPLETED_CHECKED,
    CPP_PART_5_LINE_49,
    CPP_PART_5_LINE_49_IF_POSITIVE,
    CPP_PART_5_PAYABLE_ON_SELF_EMPLOYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ZERO,
    DISABILITY_AMOUNT_FOR_SELF,
    DISABILITY_TRANSFERRED_AMOUNT,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_LINE_41700,
    FEDERAL_TAX_ON_SPLIT_INCOME,
    NET_FEDERAL_TAX,
    RC359_TAX_TOTAL,
    RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    RESP_AIPS_ADDITIONAL_TAX,
    RL_10_LABOUR_SPONSORED_FUND_AMOUNT,
    SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE,
    SELF_EMPLOYED_EI_PREMIUMS,
    SOCIAL_BENEFITS_REPAYMENT,
    SOCIAL_BENEFITS_REPAYMENT_PAYABLE,
    SPECIAL_TAXES,
    SPLIT_INCOME_DIVIDENDS_CHECKED,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
    SPLIT_INCOME_LINE_10,
    SPLIT_INCOME_LINE_13,
    SPLIT_INCOME_LINE_14,
    SPLIT_INCOME_LINE_15,
    SPLIT_INCOME_LINE_18,
    SPLIT_INCOME_LINE_19,
    SPLIT_INCOME_LINE_20,
    SPLIT_INCOME_LINE_21,
    SPLIT_INCOME_LINE_22,
    SPLIT_INCOME_LINE_23,
    SPLIT_INCOME_LINE_24,
    SPLIT_INCOME_LINE_29,
    SPLIT_INCOME_LINE_30,
    TOTAL_INCOME_FROM_FOREIGN_SOURCES,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_TAX

INPUTS = frozenset(
    {
        "ca/income_tax_deducted",
    }
)

OUTPUTS = frozenset[str]()

STEPS = {
    # T1 line 141 and line 41800 "Special taxes": the amount of Form T1172 (line 10 or 13) and
    # the RL-10 amount, the guide's "Report, on line 41800 of your return, the result of the
    # following calculation using your RL-10 slip: Tax Credit for a Labour-Sponsored Fund" whose
    # list the guide's .txt cuts off after "75% of box", so the amount is the caller's until the
    # rest is quoted (to be confirmed). The tax on excess EPSP amounts, Form RC359 line 9 for each
    # employer, is the total of the copies' line 9 (`ca/rc359_tax_total`), its last part.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/resp_aips_additional_tax",
                "ca/rl_10_labour_sponsored_fund_amount",
                "ca/rc359_tax_total",
            )
        },
        produces={"output": "ca/special_taxes"},
    ),
    # Form T1206 Part 2 line 10 "Line 8 plus line 9", line 9 being "Amount from line 41500 of your
    # return" (the advanced Canada workers benefit).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_tax_on_split_income",
                "ca/advanced_canada_workers_benefit",
            )
        },
        produces={"output": "ca/split_income_line_10"},
    ),
    # "Federal disability tax credit": line 11 "Amount from line 31600 of your return" (the
    # disability amount for self, computed on the personal amounts steps) and line 12 "Amount from
    # line 31800 of your return" (the disability amount transferred from a dependant), line 13
    # "Line 11 plus line 12".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/disability_amount_for_self",
                "ca/disability_transferred_amount",
            )
        },
        produces={"output": "ca/split_income_line_13"},
    ),
    # Line 14, line 13 "× 14.5%".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/split_income_disability_credit_rate"},
        consumes={"base": "ca/split_income_line_13"},
        produces={"output": "ca/split_income_line_14"},
    ),
    # Line 15 "Line 10 minus line 14", which prints no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/split_income_line_10", "less": "ca/split_income_line_14"},
        produces={"output": "ca/split_income_line_15"},
    ),
    # "Federal dividend tax credit on split income": line 16 "Amount from line 1 of Part 1" and line
    # 17 "Amount from line 2 of Part 1" are the caller's lines 1 and 2, read as they are; line 18
    # "Line 16 minus line 17 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/split_income_dividends_checked",
            "less": "ca/split_income_dividends_other_than_eligible_checked",
        },
        produces={"output": "ca/split_income_line_18"},
    ),
    # Line 19, line 17 "× 9.0301%", and line 20, line 18 "× 15.0198%".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/split_income_dividend_credit_rate_other_than_eligible"},
        consumes={"base": "ca/split_income_dividends_other_than_eligible_checked"},
        produces={"output": "ca/split_income_line_19"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/split_income_dividend_credit_rate_eligible"},
        consumes={"base": "ca/split_income_line_18"},
        produces={"output": "ca/split_income_line_20"},
    ),
    # Line 21 "Line 19 plus line 20" and line 22 "Line 15 minus line 21", which prints no floor.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/split_income_line_19",
                "ca/split_income_line_20",
            )
        },
        produces={"output": "ca/split_income_line_21"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/split_income_line_15", "less": "ca/split_income_line_21"},
        produces={"output": "ca/split_income_line_22"},
    ),
    # Line 23 "Part of the amount on line 3 that is from foreign sources" (68370) over "Total income
    # from foreign sources" (68380), "× Amount from line 40500 of your return": the federal foreign
    # tax credit times the share of the split income from foreign sources, rounded half-up to the
    # cent once; 0 when there is no income from foreign sources.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/split_income_line_23_rounding"},
        consumes={
            "amount": "ca/federal_foreign_tax_credit",
            "numerator": "ca/split_income_from_foreign_sources_checked",
            "denominator": "ca/total_income_from_foreign_sources",
        },
        produces={"output": "ca/split_income_line_23"},
    ),
    # Line 24 "Line 22 minus line 23 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/split_income_line_22", "less": "ca/split_income_line_23"},
        produces={"output": "ca/split_income_line_24"},
    ),
    # Line 25 "Amount from line 40600 of your return", line 26 "Amount from line 41600 of your
    # return" and line 27 "Line 25 minus line 26 (if negative, enter "0")" are the T1's line 41700,
    # the federal tax of the return (line 139, or the Part 6 line 14 of Form T691 when Part 5 line
    # 11 is positive), and line 28 "Amount from line 41500 of your return" is line 140: line 29
    # "Line 27 plus line 28".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_tax_line_41700",
                "ca/advanced_canada_workers_benefit",
            )
        },
        produces={"output": "ca/split_income_line_29"},
    ),
    # Line 30 "Enter whichever is more: the amount from line 24 or line 29."
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={"amounts": ("ca/split_income_line_24", "ca/split_income_line_29")},
        produces={"output": "ca/split_income_line_30"},
    ),
    # T1 line 142 (line 42000) "Add lines 139 to 141. Net federal tax", here by Form T1206 Part 2
    # "Add the amount from line 30 to the amount from line 41800 of your return, and enter the
    # result on line 42000 of your return.": line 30 (the more of line 24 and line 29, line 29 being
    # lines 139 and 140) and line 141 (41800), in line order. Line 124 (minimum tax carryover) is
    # not modelled.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/split_income_line_30",
                "ca/special_taxes",
            )
        },
        produces={"output": "ca/net_federal_tax"},
    ),
    # T1 line 144 and line 42100, entered from Schedule 8 Part 4 line 14: Part 4 is completed
    # only when the filer reports self-employment income alone, so the amount is counted once
    # for each Part 4 completed, 1 or 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/self_employed_cpp_contributions_payable",
            "count": "ca/cpp_part_4_completed_checked",
        },
        produces={"output": "ca/cpp_payable_on_self_employment"},
    ),
    # Schedule 8 Part 5 line 49 "If positive, enter the amount (in dollars and cents) on line
    # 42100 of your return": line 49 less 0, not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_part_5_line_49",
            "less": "ca/cpp_zero",
        },
        produces={"output": "ca/cpp_part_5_line_49_if_positive"},
    ),
    # T1 line 144 and line 42100, entered from Part 5 line 49: counted once for each Part 5
    # completed, 1 or 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/cpp_part_5_line_49_if_positive",
            "count": "ca/cpp_part_5_completed_checked",
        },
        produces={"output": "ca/cpp_part_5_payable_on_self_employment"},
    ),
    # T1 line 144 and line 42100: the Part 4 amount plus the Part 5 amount; both are added
    # when both parts are marked completed, as the form leaves the choice to the filer. Plus Form
    # RC381 Part 4 line 90 (the form's total, 0 with no copy; the return carries Schedule 8 or
    # Form RC381, never both).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_payable_on_self_employment",
                "ca/cpp_part_5_payable_on_self_employment",
                "ca/rc381_cpp_payable_on_self_employment",
            ),
        },
        produces={"output": "ca/cpp_payable_on_self_employment_and_other_earnings"},
    ),
    # T1 line 145 and line 42120, entered from Schedule 13 line 9, counted once for each
    # agreement with the Canada Employment Insurance Commission, 1 or 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/self_employed_ei_premiums",
            "count": "ca/ei_special_benefits_agreement_checked",
        },
        produces={"output": "ca/ei_payable_on_self_employment"},
    ),
    # T1 line 146 and line 42200 "Social benefits repayment (amount from line 23500)": the amount
    # of line 23500, carried over one part.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/social_benefits_repayment",)},
        produces={"output": "ca/social_benefits_repayment_payable"},
    ),
    # T1 line 148 (line 43500) "Add lines 143 to 147. Total payable": line 143 "Amount from line
    # 42000", line 144 (42100) "CPP contributions payable on self-employment income and other
    # earnings", line 145 (42120) "Employment insurance premiums payable on self-employment and
    # other eligible earnings", line 146 (42200) "Social benefits repayment (amount from line
    # 23500)" and line 147 (42800), the Ontario tax, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/net_federal_tax",
                "ca/cpp_payable_on_self_employment_and_other_earnings",
                "ca/ei_payable_on_self_employment",
                "ca/social_benefits_repayment_payable",
                "ca-on/ontario_tax",
            )
        },
        produces={"output": "ca/total_payable"},
    ),
}

WIRING = {
    (
        Sum,
        frozenset({RESP_AIPS_ADDITIONAL_TAX, RL_10_LABOUR_SPONSORED_FUND_AMOUNT, RC359_TAX_TOTAL}),
        frozenset({SPECIAL_TAXES}),
    ),
    (
        Sum,
        frozenset({FEDERAL_TAX_ON_SPLIT_INCOME, ADVANCED_CANADA_WORKERS_BENEFIT}),
        frozenset({SPLIT_INCOME_LINE_10}),
    ),
    (
        Sum,
        frozenset({DISABILITY_AMOUNT_FOR_SELF, DISABILITY_TRANSFERRED_AMOUNT}),
        frozenset({SPLIT_INCOME_LINE_13}),
    ),
    (ApplyRate, frozenset({SPLIT_INCOME_LINE_13}), frozenset({SPLIT_INCOME_LINE_14})),
    (
        Subtract,
        frozenset({SPLIT_INCOME_LINE_10, SPLIT_INCOME_LINE_14}),
        frozenset({SPLIT_INCOME_LINE_15}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {SPLIT_INCOME_DIVIDENDS_CHECKED, SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED}
        ),
        frozenset({SPLIT_INCOME_LINE_18}),
    ),
    (
        ApplyRate,
        frozenset({SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED}),
        frozenset({SPLIT_INCOME_LINE_19}),
    ),
    (ApplyRate, frozenset({SPLIT_INCOME_LINE_18}), frozenset({SPLIT_INCOME_LINE_20})),
    (
        Sum,
        frozenset({SPLIT_INCOME_LINE_19, SPLIT_INCOME_LINE_20}),
        frozenset({SPLIT_INCOME_LINE_21}),
    ),
    (
        Subtract,
        frozenset({SPLIT_INCOME_LINE_15, SPLIT_INCOME_LINE_21}),
        frozenset({SPLIT_INCOME_LINE_22}),
    ),
    (
        ApplyRatioOrZero,
        frozenset(
            {
                FEDERAL_FOREIGN_TAX_CREDIT,
                SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
                TOTAL_INCOME_FROM_FOREIGN_SOURCES,
            }
        ),
        frozenset({SPLIT_INCOME_LINE_23}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({SPLIT_INCOME_LINE_22, SPLIT_INCOME_LINE_23}),
        frozenset({SPLIT_INCOME_LINE_24}),
    ),
    (
        Sum,
        frozenset({FEDERAL_TAX_LINE_41700, ADVANCED_CANADA_WORKERS_BENEFIT}),
        frozenset({SPLIT_INCOME_LINE_29}),
    ),
    (
        GreaterOf,
        frozenset({SPLIT_INCOME_LINE_24, SPLIT_INCOME_LINE_29}),
        frozenset({SPLIT_INCOME_LINE_30}),
    ),
    (
        Sum,
        frozenset({SPLIT_INCOME_LINE_30, SPECIAL_TAXES}),
        frozenset({NET_FEDERAL_TAX}),
    ),
    (
        TimesCount,
        frozenset({SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE, CPP_PART_4_COMPLETED_CHECKED}),
        frozenset({CPP_PAYABLE_ON_SELF_EMPLOYMENT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_PART_5_LINE_49, CPP_ZERO}),
        frozenset({CPP_PART_5_LINE_49_IF_POSITIVE}),
    ),
    (
        TimesCount,
        frozenset({CPP_PART_5_LINE_49_IF_POSITIVE, CPP_PART_5_COMPLETED_CHECKED}),
        frozenset({CPP_PART_5_PAYABLE_ON_SELF_EMPLOYMENT}),
    ),
    (
        Sum,
        frozenset(
            {
                CPP_PAYABLE_ON_SELF_EMPLOYMENT,
                CPP_PART_5_PAYABLE_ON_SELF_EMPLOYMENT,
                RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
            }
        ),
        frozenset({CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS}),
    ),
    (
        TimesCount,
        frozenset({SELF_EMPLOYED_EI_PREMIUMS, EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED}),
        frozenset({EI_PAYABLE_ON_SELF_EMPLOYMENT}),
    ),
    (Sum, frozenset({SOCIAL_BENEFITS_REPAYMENT}), frozenset({SOCIAL_BENEFITS_REPAYMENT_PAYABLE})),
    (
        Sum,
        frozenset(
            {
                NET_FEDERAL_TAX,
                CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
                EI_PAYABLE_ON_SELF_EMPLOYMENT,
                SOCIAL_BENEFITS_REPAYMENT_PAYABLE,
                ONTARIO_TAX,
            }
        ),
        frozenset({TOTAL_PAYABLE}),
    ),
}
