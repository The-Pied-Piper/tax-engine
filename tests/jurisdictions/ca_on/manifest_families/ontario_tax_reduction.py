"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.first_record_count import FirstRecordCount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.multiple_over import MultipleOver
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    AMT_FOREIGN_BUSINESS_TAX_PAID,
    AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS,
    AMT_PART_5_LINE_11_IS_POSITIVE,
    AMT_SPECIAL_FOREIGN_TAX_CREDIT,
    FOREIGN_TAX_CREDIT_NET_INCOME,
    FOREIGN_TAX_CREDIT_SHEETS,
    NET_INCOME,
    SPOUSE_NET_INCOME,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
)
from tax_engine.jurisdictions.ca_on.capabilities.provincial_foreign_tax_credit import (
    ProvincialForeignTaxCredit,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    BANKRUPT_IN_YEAR,
    BANKRUPT_IN_YEAR_CHECKED,
    CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME,
    CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME_CHECKED,
    DEPENDANTS,
    DEPENDENT_CHILDREN,
    NOT_CLAIMING_ONTARIO_TAX_REDUCTION,
    NOT_CLAIMING_ONTARIO_TAX_REDUCTION_CHECKED,
    NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR,
    NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR_CHECKED,
    NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END,
    NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED,
    ONTARIO_MINIMUM_TAX,
    ONTARIO_TAX_AFTER_DIVIDEND_CREDIT,
    ONTARIO_TAX_AFTER_FOREIGN_TAX_CREDIT,
    ONTARIO_TAX_AFTER_REDUCTION,
    ONTARIO_TAX_BEFORE_REDUCTION,
    ONTARIO_TAX_REDUCTION,
    ONTARIO_TAX_REDUCTION_BEFORE_CONDITIONS,
    ONTARIO_TAX_WITH_SURTAX,
    PROVINCIAL_FOREIGN_TAX_CREDIT,
    PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
    RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY,
    RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY_CHECKED,
    TAX_OTHERWISE_PAYABLE,
    TAX_OTHERWISE_PAYABLE_LINE_71,
    TAX_OTHERWISE_PAYABLE_LINE_73,
    TAX_OTHERWISE_PAYABLE_REDUCTION,
    TAX_OTHERWISE_PAYABLE_REDUCTION_BEFORE_CONDITIONS,
    TAX_OTHERWISE_PAYABLE_REDUCTION_CLAIMABLE,
    TAX_REDUCTION_AMOUNTS,
    TAX_REDUCTION_AMOUNTS_CLAIMABLE,
    TAX_REDUCTION_BASIC,
    TAX_REDUCTION_CLAIMABLE,
    TAX_REDUCTION_FOR_CHILDREN,
    TAX_REDUCTION_FOR_CHILDREN_BEFORE_SPOUSE_RULE,
    TAX_REDUCTION_FOR_DEPENDANTS,
    TAX_REDUCTION_FOR_DEPENDANTS_BEFORE_SPOUSE_RULE,
)

# The shared fact of the form `ca/spouse_on_december_31`, exported as the checked kind: the
# kind `<form>.<export>` that the return reads, a record list of the one checked count.
SPOUSE_ON_DECEMBER_31_EXPORT = RecordListKind(
    "ca/spouse_on_december_31.spouse_or_common_law_partner_on_december_31_checked",
    fields=(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED,),
)

INPUTS = frozenset(
    {
        "ca-on/dependent_children",
        "ca-on/dependants",
        "ca-on/not_resident_of_canada_at_start_of_year",
        "ca-on/not_resident_of_ontario_at_year_end",
        "ca-on/bankrupt_in_year",
        "ca-on/return_filed_by_trustee_in_bankruptcy",
        "ca-on/not_claiming_ontario_tax_reduction",
        "ca-on/claims_tax_reduction_amounts_at_equal_net_income",
    }
)

OUTPUTS = frozenset[str]()

STEPS = {
    # ON428 line 74 "Basic reduction 294.00": the dataset becomes an artifact of the same
    # name, the first part of line 77.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/tax_reduction_basic"},
        consumes={},
        produces={"output": "ca-on/tax_reduction_basic"},
    ),
    # ON428 line 75 (line 60969) "Number of dependent children multiplied by $544" and line
    # 76 (line 60970) "Number of dependants multiplied by $544", before the rule that "only the
    # individual with the higher net income can claim the amounts on lines 75 and 76".
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca-on/tax_reduction_per_dependant"},
        consumes={"count": "ca-on/dependent_children"},
        produces={"output": "ca-on/tax_reduction_for_children_before_spouse_rule"},
    ),
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca-on/tax_reduction_per_dependant"},
        consumes={"count": "ca-on/dependants"},
        produces={"output": "ca-on/tax_reduction_for_dependants_before_spouse_rule"},
    ),
    # The answers to the yes or no questions of ON428 and of the spouse rule, a count of 1 or 0,
    # checked before the step that reads them. A count of 2 or more is refused, not capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/not_resident_of_canada_at_start_of_year"},
        produces={"output": "ca-on/not_resident_of_canada_at_start_of_year_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/not_resident_of_ontario_at_year_end"},
        produces={"output": "ca-on/not_resident_of_ontario_at_year_end_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/bankrupt_in_year"},
        produces={"output": "ca-on/bankrupt_in_year_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/return_filed_by_trustee_in_bankruptcy"},
        produces={"output": "ca-on/return_filed_by_trustee_in_bankruptcy_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/not_claiming_ontario_tax_reduction"},
        produces={"output": "ca-on/not_claiming_ontario_tax_reduction_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/claims_tax_reduction_amounts_at_equal_net_income"},
        produces={"output": "ca-on/claims_tax_reduction_amounts_at_equal_net_income_checked"},
    ),
    # The spouse or common-law partner on December 31 is entered once, in the form
    # `ca/spouse_on_december_31`, whose export is read here as a count.
    CapabilitySelection(
        name="core/first_record_count",
        params={},
        consumes={
            "records": (
                "ca/spouse_on_december_31.spouse_or_common_law_partner_on_december_31_checked"
            )
        },
        produces={"output": "ca/spouse_or_common_law_partner_on_december_31_total"},
    ),
    # ON428 "If you had a spouse or common-law partner on December 31, 2025, only the
    # individual with the higher net income can claim the amounts on lines 75 and 76.": 1 when
    # there was no spouse or common-law partner (the T1's "Marital status on December 31, 2025"
    # Box 1 Married and Box 2 Living common-law), when the net income (line 23600) is more than
    # the spouse's (ON428 line 12 "Your spouse's or common-law partner's net income from line
    # 23600 of their return"), or when the two are equal and the caller says this return claims.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca-on/tax_reduction_spouse_rule"},
        consumes={
            "counts": (
                "ca/spouse_or_common_law_partner_on_december_31_total",
                "ca-on/claims_tax_reduction_amounts_at_equal_net_income_checked",
            ),
            "amounts": ("ca/net_income", "ca/spouse_net_income"),
        },
        produces={"output": "ca-on/tax_reduction_amounts_claimable"},
    ),
    # ON428 line 75 and line 76, each once if this return claims them, else 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/tax_reduction_for_children_before_spouse_rule",
            "count": "ca-on/tax_reduction_amounts_claimable",
        },
        produces={"output": "ca-on/tax_reduction_for_children"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/tax_reduction_for_dependants_before_spouse_rule",
            "count": "ca-on/tax_reduction_amounts_claimable",
        },
        produces={"output": "ca-on/tax_reduction_for_dependants"},
    ),
    # ON428 line 77 "Add lines 74 to 76.", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/tax_reduction_basic",
                "ca-on/tax_reduction_for_children",
                "ca-on/tax_reduction_for_dependants",
            )
        },
        produces={"output": "ca-on/tax_reduction_amounts"},
    ),
    # ON428 line 73 "Line 71 plus line 72 =": line 71 is the Ontario tax after the dividend
    # credit and line 72 the additional tax for minimum tax purposes (Worksheet ON428).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/ontario_tax_after_dividend_credit",
                "ca-on/ontario_minimum_tax",
            )
        },
        produces={"output": "ca-on/ontario_tax_before_reduction"},
    ),
    # ON428 line 78 "Amount from line 77 above multiplied by 2", line 79 "Amount from line 73
    # above" and line 80 "Line 78 minus line 79 (if negative, enter "0") Ontario tax
    # reduction", before the conditions on which the form enters "0" on line 80.
    CapabilitySelection(
        name="core/multiple_over",
        params={"factor": "ca-on/tax_reduction_factor"},
        consumes={
            "amount": "ca-on/tax_reduction_amounts",
            "less": "ca-on/ontario_tax_before_reduction",
        },
        produces={"output": "ca-on/ontario_tax_reduction_before_conditions"},
    ),
    # ON428 "Enter "0" on line 80 if any of the following applies to you:" the six printed
    # conditions in the form's order: "You were not a resident of Canada at the beginning of the
    # year", "You were not a resident of Ontario on December 31, 2025", "There is an amount on
    # line 72", "You were bankrupt at any time in 2025", "Your return is filed for you by a
    # trustee in bankruptcy" and "You are choosing not to claim an Ontario tax reduction": 0 when
    # any applies, else 1.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca-on/tax_reduction_conditions"},
        consumes={
            "counts": (
                "ca-on/not_resident_of_canada_at_start_of_year_checked",
                "ca-on/not_resident_of_ontario_at_year_end_checked",
                "ca-on/bankrupt_in_year_checked",
                "ca-on/return_filed_by_trustee_in_bankruptcy_checked",
                "ca-on/not_claiming_ontario_tax_reduction_checked",
            ),
            "amounts": ("ca-on/ontario_minimum_tax",),
        },
        produces={"output": "ca-on/tax_reduction_claimable"},
    ),
    # ON428 line 80 "Ontario tax reduction": line 78 minus line 79 once if none of the six
    # conditions applies, else "0".
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_reduction_before_conditions",
            "count": "ca-on/tax_reduction_claimable",
        },
        produces={"output": "ca-on/ontario_tax_reduction"},
    ),
    # ON428 line 81 "Line 73 minus line 80 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_before_reduction",
            "less": "ca-on/ontario_tax_reduction",
        },
        produces={"output": "ca-on/ontario_tax_after_reduction"},
    ),
    # Form T2036 note (4): "If you were a resident of Ontario, calculate this amount by entering
    # "0" on lines 70 and 72 of Form ON428 and continue the calculation. The result from line 81 is
    # your provincial or territorial tax otherwise payable." ON428 line 71 "Line 69 minus line 70
    # (if negative, enter "0")" with "0" on line 70: line 69 over one part.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/ontario_tax_with_surtax",)},
        produces={"output": "ca-on/tax_otherwise_payable_line_71"},
    ),
    # ON428 line 73 "Line 71 plus line 72 =" with "0" on line 72: line 71 over one part, for the
    # tax otherwise payable.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/tax_otherwise_payable_line_71",)},
        produces={"output": "ca-on/tax_otherwise_payable_line_73"},
    ),
    # ON428 line 78 "Amount from line 77 above multiplied by 2", line 79 "Amount from line 73
    # above" and line 80 "Line 78 minus line 79 (if negative, enter "0") Ontario tax reduction",
    # for the tax otherwise payable: lines 74 to 77 are those above and line 79 is its line 73,
    # before the conditions on which the form enters "0" on line 80.
    CapabilitySelection(
        name="core/multiple_over",
        params={"factor": "ca-on/tax_reduction_factor"},
        consumes={
            "amount": "ca-on/tax_reduction_amounts",
            "less": "ca-on/tax_otherwise_payable_line_73",
        },
        produces={"output": "ca-on/tax_otherwise_payable_reduction_before_conditions"},
    ),
    # ON428 "Enter "0" on line 80 if any of the following applies to you:" for the tax otherwise
    # payable, whose line 72 is "0": the printed conditions other than "There is an amount on line
    # 72", in the form's order, "You were not a resident of Canada at the beginning of the year",
    # "You were not a resident of Ontario on December 31, 2025", "You were bankrupt at any time in
    # 2025", "Your return is filed for you by a trustee in bankruptcy" and "You are choosing not
    # to claim an Ontario tax reduction": 0 when any applies, else 1.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca-on/tax_reduction_conditions_without_line_72"},
        consumes={
            "counts": (
                "ca-on/not_resident_of_canada_at_start_of_year_checked",
                "ca-on/not_resident_of_ontario_at_year_end_checked",
                "ca-on/bankrupt_in_year_checked",
                "ca-on/return_filed_by_trustee_in_bankruptcy_checked",
                "ca-on/not_claiming_ontario_tax_reduction_checked",
            ),
            "amounts": (),
        },
        produces={"output": "ca-on/tax_otherwise_payable_reduction_claimable"},
    ),
    # ON428 line 80 "Ontario tax reduction" for the tax otherwise payable: line 78 minus line 79
    # once if none of the five conditions applies, else "0".
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/tax_otherwise_payable_reduction_before_conditions",
            "count": "ca-on/tax_otherwise_payable_reduction_claimable",
        },
        produces={"output": "ca-on/tax_otherwise_payable_reduction"},
    ),
    # ON428 line 81 "Line 73 minus line 80 (if negative, enter "0")" with "0" on lines 70 and 72:
    # the provincial tax otherwise payable of Form T2036 note (4).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/tax_otherwise_payable_line_73",
            "less": "ca-on/tax_otherwise_payable_reduction",
        },
        produces={"output": "ca-on/tax_otherwise_payable"},
    ),
    # Form T2036, Provincial or Territorial Foreign Tax Credit: line 1 "Enter the amount from line
    # 1 of Form T2209.", line 2 "Enter the amount from line 3 of Form T2209, unless you have to
    # pay minimum tax.(1)", line 3 "Line 1 minus line 2", line 4 "Net foreign non-business income
    # (2)" "× Provincial or territorial tax otherwise payable (4)" over "Net income (3)" and line 5
    # "Enter whichever amount is less: line 3 or line 4." "Provincial or territorial foreign tax
    # credit", for each sheet of Form T2209 (a separate form for each country when "the total of
    # the non-business income taxes that you paid to all foreign countries was more than $200"):
    # "Enter the total from line 5 (for each country if applicable)" on ON428 line 82, before the
    # limit below. Line 2 note (1), when "you have to pay minimum tax" (Form T691 Part 5 line 11
    # positive) and "you were a resident of Ontario at the end of the year": "If the total
    # non-business income taxes you paid to all foreign countries is $200 or less", line 1 of
    # this form divided by "the sum of line 1 of this form and the amount on line 8 of Part 4 of
    # Form T691", times "the special foreign tax credit on line 11 of Part 4 of Form T691"; "If
    # the total non-business income taxes you paid to all foreign countries is more than $200",
    # for each country line 1 of that country divided by "the total foreign taxes paid for 2025
    # (to get this total, add the amount on line 7 of Part 4 of Form T691, Alternative Minimum
    # Tax, divided by 66.6666% and the amount on line 8 of Part 4 of Form T691)", times the same
    # line 11.
    CapabilitySelection(
        name="ca-on/provincial_foreign_tax_credit",
        params={
            "rounding": "ca-on/provincial_foreign_tax_credit_rounding",
            "threshold": "ca-on/provincial_foreign_tax_credit_separate_sheet_threshold",
            "rate": "ca/amt_special_foreign_tax_credit_rate",
        },
        consumes={
            "minimum_tax_applies": "ca/amt_part_5_line_11_is_positive",
            "sheets": "ca/foreign_tax_credit_sheets",
            "net_income": "ca/foreign_tax_credit_net_income",
            "provincial_tax": "ca-on/tax_otherwise_payable",
            "non_business_tax_paid": "ca/amt_foreign_non_business_tax_two_thirds",
            "business_tax_paid": "ca/amt_foreign_business_tax_paid",
            "special_foreign_tax_credit": "ca/amt_special_foreign_tax_credit",
        },
        produces={"total": "ca-on/provincial_foreign_tax_credit_before_limit"},
    ),
    # ON428 line 82 "Provincial foreign tax credit (complete Form T2036)": Form T2036 line 5 "The
    # amount on line 5 should not be more than the amount entered on the line for provincial or
    # territorial tax otherwise payable." (note (4), ON428 line 81 with "0" on lines 70 and 72).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca-on/provincial_foreign_tax_credit_before_limit",
                "ca-on/tax_otherwise_payable",
            )
        },
        produces={"output": "ca-on/provincial_foreign_tax_credit"},
    ),
    # ON428 line 83 "Line 81 minus line 82 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_after_reduction",
            "less": "ca-on/provincial_foreign_tax_credit",
        },
        produces={"output": "ca-on/ontario_tax_after_foreign_tax_credit"},
    ),
}

WIRING = {
    (
        YesOrNoCount,
        frozenset({NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR}),
        frozenset({NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END}),
        frozenset({NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({BANKRUPT_IN_YEAR}),
        frozenset({BANKRUPT_IN_YEAR_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY}),
        frozenset({RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({NOT_CLAIMING_ONTARIO_TAX_REDUCTION}),
        frozenset({NOT_CLAIMING_ONTARIO_TAX_REDUCTION_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME}),
        frozenset({CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME_CHECKED}),
    ),
    (
        FirstRecordCount,
        frozenset({SPOUSE_ON_DECEMBER_31_EXPORT}),
        frozenset({SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL}),
    ),
    (CreditAmount, frozenset(), frozenset({TAX_REDUCTION_BASIC})),
    (
        PerUnitAmount,
        frozenset({DEPENDENT_CHILDREN}),
        frozenset({TAX_REDUCTION_FOR_CHILDREN_BEFORE_SPOUSE_RULE}),
    ),
    (
        PerUnitAmount,
        frozenset({DEPENDANTS}),
        frozenset({TAX_REDUCTION_FOR_DEPENDANTS_BEFORE_SPOUSE_RULE}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
                CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME_CHECKED,
                NET_INCOME,
                SPOUSE_NET_INCOME,
            }
        ),
        frozenset({TAX_REDUCTION_AMOUNTS_CLAIMABLE}),
    ),
    (
        TimesCount,
        frozenset({TAX_REDUCTION_FOR_CHILDREN_BEFORE_SPOUSE_RULE, TAX_REDUCTION_AMOUNTS_CLAIMABLE}),
        frozenset({TAX_REDUCTION_FOR_CHILDREN}),
    ),
    (
        TimesCount,
        frozenset(
            {TAX_REDUCTION_FOR_DEPENDANTS_BEFORE_SPOUSE_RULE, TAX_REDUCTION_AMOUNTS_CLAIMABLE}
        ),
        frozenset({TAX_REDUCTION_FOR_DEPENDANTS}),
    ),
    (
        Sum,
        frozenset({TAX_REDUCTION_BASIC, TAX_REDUCTION_FOR_CHILDREN, TAX_REDUCTION_FOR_DEPENDANTS}),
        frozenset({TAX_REDUCTION_AMOUNTS}),
    ),
    (
        Sum,
        frozenset({ONTARIO_TAX_AFTER_DIVIDEND_CREDIT, ONTARIO_MINIMUM_TAX}),
        frozenset({ONTARIO_TAX_BEFORE_REDUCTION}),
    ),
    (
        MultipleOver,
        frozenset({TAX_REDUCTION_AMOUNTS, ONTARIO_TAX_BEFORE_REDUCTION}),
        frozenset({ONTARIO_TAX_REDUCTION_BEFORE_CONDITIONS}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR_CHECKED,
                NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED,
                BANKRUPT_IN_YEAR_CHECKED,
                RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY_CHECKED,
                NOT_CLAIMING_ONTARIO_TAX_REDUCTION_CHECKED,
                ONTARIO_MINIMUM_TAX,
            }
        ),
        frozenset({TAX_REDUCTION_CLAIMABLE}),
    ),
    (
        TimesCount,
        frozenset({ONTARIO_TAX_REDUCTION_BEFORE_CONDITIONS, TAX_REDUCTION_CLAIMABLE}),
        frozenset({ONTARIO_TAX_REDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_TAX_BEFORE_REDUCTION, ONTARIO_TAX_REDUCTION}),
        frozenset({ONTARIO_TAX_AFTER_REDUCTION}),
    ),
    (
        Sum,
        frozenset({ONTARIO_TAX_WITH_SURTAX}),
        frozenset({TAX_OTHERWISE_PAYABLE_LINE_71}),
    ),
    (
        Sum,
        frozenset({TAX_OTHERWISE_PAYABLE_LINE_71}),
        frozenset({TAX_OTHERWISE_PAYABLE_LINE_73}),
    ),
    (
        MultipleOver,
        frozenset({TAX_REDUCTION_AMOUNTS, TAX_OTHERWISE_PAYABLE_LINE_73}),
        frozenset({TAX_OTHERWISE_PAYABLE_REDUCTION_BEFORE_CONDITIONS}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR_CHECKED,
                NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED,
                BANKRUPT_IN_YEAR_CHECKED,
                RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY_CHECKED,
                NOT_CLAIMING_ONTARIO_TAX_REDUCTION_CHECKED,
            }
        ),
        frozenset({TAX_OTHERWISE_PAYABLE_REDUCTION_CLAIMABLE}),
    ),
    (
        TimesCount,
        frozenset(
            {
                TAX_OTHERWISE_PAYABLE_REDUCTION_BEFORE_CONDITIONS,
                TAX_OTHERWISE_PAYABLE_REDUCTION_CLAIMABLE,
            }
        ),
        frozenset({TAX_OTHERWISE_PAYABLE_REDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({TAX_OTHERWISE_PAYABLE_LINE_73, TAX_OTHERWISE_PAYABLE_REDUCTION}),
        frozenset({TAX_OTHERWISE_PAYABLE}),
    ),
    (
        ProvincialForeignTaxCredit,
        frozenset(
            {
                AMT_PART_5_LINE_11_IS_POSITIVE,
                FOREIGN_TAX_CREDIT_SHEETS,
                FOREIGN_TAX_CREDIT_NET_INCOME,
                TAX_OTHERWISE_PAYABLE,
                AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS,
                AMT_FOREIGN_BUSINESS_TAX_PAID,
                AMT_SPECIAL_FOREIGN_TAX_CREDIT,
            }
        ),
        frozenset({PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT}),
    ),
    (
        LesserOf,
        frozenset({PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT, TAX_OTHERWISE_PAYABLE}),
        frozenset({PROVINCIAL_FOREIGN_TAX_CREDIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_TAX_AFTER_REDUCTION, PROVINCIAL_FOREIGN_TAX_CREDIT}),
        frozenset({ONTARIO_TAX_AFTER_FOREIGN_TAX_CREDIT}),
    ),
}
