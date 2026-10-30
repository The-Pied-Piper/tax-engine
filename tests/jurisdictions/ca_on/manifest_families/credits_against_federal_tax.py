"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.logging_tax_credit import LoggingTaxCredit
from tax_engine.jurisdictions.ca.catalog import (
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX,
    AMT_PART_5_LINE_11_IS_POSITIVE,
    CHILD_CARE_EXPENSES,
    CREDITS_AGAINST_FEDERAL_TAX,
    DISABILITY_SUPPORTS_DEDUCTION,
    ELECTED_SPLIT_PENSION_DEDUCTION,
    FEDERAL_LOGGING_TAX_CREDIT,
    FEDERAL_TAX,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_LINE_41700,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    FHSA_DEDUCTION,
    INVESTMENT_TAX_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM,
    LABOUR_SPONSORED_FUNDS_NET_COST,
    LOGGING_CREDIT_BASE,
    LOGGING_CREDIT_CAP,
    LOGGING_OPERATIONS,
    MOVING_EXPENSES_DEDUCTION,
    POLITICAL_CONTRIBUTIONS,
    POLITICAL_CREDIT,
    POLITICAL_CREDIT_BEFORE_MAXIMUM,
    POLITICAL_CREDIT_CHOSEN_COLUMN,
    POLITICAL_CREDIT_COLUMN_1_LINE_2,
    POLITICAL_CREDIT_COLUMN_1_LINE_3,
    POLITICAL_CREDIT_COLUMN_1_LINE_5,
    POLITICAL_CREDIT_COLUMN_1_LINE_6,
    POLITICAL_CREDIT_COLUMN_1_LINE_7,
    POLITICAL_CREDIT_COLUMN_2_LINE_2,
    POLITICAL_CREDIT_COLUMN_2_LINE_3,
    POLITICAL_CREDIT_COLUMN_2_LINE_5,
    POLITICAL_CREDIT_COLUMN_2_LINE_6,
    POLITICAL_CREDIT_COLUMN_2_LINE_7,
    POLITICAL_CREDIT_COLUMN_3_LINE_2,
    POLITICAL_CREDIT_COLUMN_3_LINE_3,
    POLITICAL_CREDIT_COLUMN_3_LINE_5,
    POLITICAL_CREDIT_COLUMN_3_LINE_6,
    POLITICAL_CREDIT_COLUMN_3_LINE_7,
    POLITICAL_CREDIT_SHORTCUT_AMOUNT,
    POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
    PROVINCES_LOGGING_TAX_CREDIT,
    RRSP_DEDUCTION,
    SUPPORT_PAYMENTS_DEDUCTION_CHECKED,
    TAXABLE_INCOME,
)
from tax_engine.jurisdictions.ca_on.capabilities.choose_by_range import ChooseByRange

INPUTS = frozenset(
    {
        "ca/labour_sponsored_funds_net_cost",
        "ca/logging_operations",
    }
)

OUTPUTS = frozenset[str]()

STEPS = {
    # T1 line 135 and line 41000 "Total federal political contributions (attach receipts) Line
    # 40900" is a caller input, ca/political_contributions, taken as the T1 takes it; the
    # Federal Worksheet "Line 41000 - Federal political contribution tax credit" reads it as
    # line 40900 and builds each of its three columns as printed, then the one that applies is
    # picked.
    # Federal Worksheet "Column 1: Line 40900 is $400 or less".
    # Line 2: 0.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_column_1_line_2"},
        consumes={},
        produces={"output": "ca/political_credit_column_1_line_2"},
    ),
    # Column 1 line 3 "Line 1 minus line 2 (if negative, enter "0") =", line 1 being the
    # contributions.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/political_contributions",
            "less": "ca/political_credit_column_1_line_2",
        },
        produces={"output": "ca/political_credit_column_1_line_3"},
    ),
    # Column 1 line 4 "Rate 75%" and line 5 "Line 3 multiplied by the percentage from line 4 =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/political_credit_column_1_line_4"},
        consumes={"base": "ca/political_credit_column_1_line_3"},
        produces={"output": "ca/political_credit_column_1_line_5"},
    ),
    # Column 1 line 6: 0.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_column_1_line_6"},
        consumes={},
        produces={"output": "ca/political_credit_column_1_line_6"},
    ),
    # Column 1 line 7 "Line 5 plus line 6 Enter this amount on line 41000 of your return. =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/political_credit_column_1_line_5",
                "ca/political_credit_column_1_line_6",
            ),
        },
        produces={"output": "ca/political_credit_column_1_line_7"},
    ),
    # Federal Worksheet "Column 2: Line 40900 is more than $400 but not more than $750".
    # Line 2: 400.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_column_2_line_2"},
        consumes={},
        produces={"output": "ca/political_credit_column_2_line_2"},
    ),
    # Column 2 line 3 "Line 1 minus line 2 (if negative, enter "0") =", line 1 being the
    # contributions.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/political_contributions",
            "less": "ca/political_credit_column_2_line_2",
        },
        produces={"output": "ca/political_credit_column_2_line_3"},
    ),
    # Column 2 line 4 "Rate 50%" and line 5 "Line 3 multiplied by the percentage from line 4 =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/political_credit_column_2_line_4"},
        consumes={"base": "ca/political_credit_column_2_line_3"},
        produces={"output": "ca/political_credit_column_2_line_5"},
    ),
    # Column 2 line 6: 300.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_column_2_line_6"},
        consumes={},
        produces={"output": "ca/political_credit_column_2_line_6"},
    ),
    # Column 2 line 7 "Line 5 plus line 6 Enter this amount on line 41000 of your return. =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/political_credit_column_2_line_5",
                "ca/political_credit_column_2_line_6",
            ),
        },
        produces={"output": "ca/political_credit_column_2_line_7"},
    ),
    # Federal Worksheet "Column 3: Line 40900 is more than more than $750".
    # Line 2: 750.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_column_3_line_2"},
        consumes={},
        produces={"output": "ca/political_credit_column_3_line_2"},
    ),
    # Column 3 line 3 "Line 1 minus line 2 (if negative, enter "0") =", line 1 being the
    # contributions.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/political_contributions",
            "less": "ca/political_credit_column_3_line_2",
        },
        produces={"output": "ca/political_credit_column_3_line_3"},
    ),
    # Column 3 line 4 "Rate 33.33%" and line 5 "Line 3 multiplied by the percentage from line 4
    # =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/political_credit_column_3_line_4"},
        consumes={"base": "ca/political_credit_column_3_line_3"},
        produces={"output": "ca/political_credit_column_3_line_5"},
    ),
    # Column 3 line 6: 475.00, a printed constant.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_column_3_line_6"},
        consumes={},
        produces={"output": "ca/political_credit_column_3_line_6"},
    ),
    # Column 3 line 7 "Line 5 plus line 6 Enter this amount on line 41000 of your return. =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/political_credit_column_3_line_5",
                "ca/political_credit_column_3_line_6",
            ),
        },
        produces={"output": "ca/political_credit_column_3_line_7"},
    ),
    # The column that applies, "Use column 1 if the amount from line 40900 is $400 or less. Use
    # column 2 if the amount from line 40900 is more than $400 but not more than $750. Use
    # column 3 if the amount from line 40900 is more than $750.": the limits are the columns'
    # own line 2 constants, which their headings print again.
    CapabilitySelection(
        name="ca-on/choose_by_range",
        params={},
        consumes={
            "amount": "ca/political_contributions",
            "first_limit": "ca/political_credit_column_2_line_2",
            "second_limit": "ca/political_credit_column_3_line_2",
            "first": "ca/political_credit_column_1_line_7",
            "second": "ca/political_credit_column_2_line_7",
            "third": "ca/political_credit_column_3_line_7",
        },
        produces={"output": "ca/political_credit_chosen_column"},
    ),
    # The shortcut, "If your total federal political contributions from line 40900 of your
    # return were" "$1,275 or more, enter $650 on line 41000 of your return. If not, use the
    # amount from line 40900 of your return to decide which column to complete.": the printed
    # 1,275 and 650 are datasets. Nothing compares two amounts yet, so the same chooser tests
    # the 1,275 against the contributions: when it is at most the contributions it chooses the
    # 650, otherwise the chosen column's line 7. A chooser's six artifact slots must be six
    # different artifacts, so the middle range is given column 3's line 2 (750) as its limit
    # and column 3's line 7 as its value: 1,275 is never at most 750, so it is never chosen.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_shortcut_threshold"},
        consumes={},
        produces={"output": "ca/political_credit_shortcut_threshold"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/political_credit_shortcut_amount"},
        consumes={},
        produces={"output": "ca/political_credit_shortcut_amount"},
    ),
    CapabilitySelection(
        name="ca-on/choose_by_range",
        params={},
        consumes={
            "amount": "ca/political_credit_shortcut_threshold",
            "first_limit": "ca/political_contributions",
            "second_limit": "ca/political_credit_column_3_line_2",
            "first": "ca/political_credit_shortcut_amount",
            "second": "ca/political_credit_column_3_line_7",
            "third": "ca/political_credit_chosen_column",
        },
        produces={"output": "ca/political_credit_before_maximum"},
    ),
    # T1 line 135 and line 41000 "(maximum $650)", after the worksheet's line 7 or the
    # shortcut's $650.
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/political_credit_maximum"},
        consumes={"base": "ca/political_credit_before_maximum"},
        produces={"output": "ca/political_credit"},
    ),
    # T1 line 137 and line 41400 "Labour-sponsored funds tax credit Line 41300: Net cost of
    # shares of a provincially registered fund Line 41300: Allowable credit": the guide's "Claim
    # the amount of your allowable credit on line 41400 of your return that is equal to 15% of
    # the net cost reported on line 41300 of your return, to a maximum of $750." is 15% of line
    # 41300, the caller's net cost.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/labour_sponsored_funds_rate"},
        consumes={"base": "ca/labour_sponsored_funds_net_cost"},
        produces={"output": "ca/labour_sponsored_funds_credit_before_maximum"},
    ),
    # The guide's "to a maximum of $750" comes after the percentage, so it caps the credit.
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/labour_sponsored_funds_maximum"},
        consumes={"base": "ca/labour_sponsored_funds_credit_before_maximum"},
        produces={"output": "ca/labour_sponsored_funds_credit"},
    ),
    # T1 line 138 (line 41600) "Add lines 135 to 137.": line 135 (41000, the federal political
    # contribution tax credit), line 136 (41200, the investment tax credit of Form T2038(IND) Part D
    # amount 15) and line 137 (41400), in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/political_credit",
                "ca/investment_tax_credit",
                "ca/labour_sponsored_funds_credit",
            ),
        },
        produces={"output": "ca/credits_against_federal_tax"},
    ),
    # Federal logging tax credit, one item per province with a logging operation: "To calculate
    # your credit for each province where you operated, use the lower of the following amounts for
    # each province you had a logging operation in: 66.6667% of the logging tax that you paid to
    # that province for the year; 6.6667% of your net logging income in that province for the
    # year." The per-item capability does the lower of the two amounts for each province, one
    # trace line each, and gives their total.
    CapabilitySelection(
        name="ca/logging_tax_credit",
        params={
            "tax_rate": "ca/logging_tax_rate",
            "income_rate": "ca/logging_income_rate",
        },
        consumes={"provinces": "ca/logging_operations"},
        produces={"output": "ca/provinces_logging_tax_credit"},
    ),
    # Federal logging tax credit, the base and the cap: "up to 6.6667% of your taxable income from
    # line 26000 of your return, not including any amounts on lines 20800, 20805, 21000, 21400,
    # 21500, 21900, and 22000 of your return." The base is line 26000 with those seven lines added
    # back, and the cap is 6.6667% of it.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/taxable_income",
                "ca/rrsp_deduction",
                "ca/fhsa_deduction",
                "ca/elected_split_pension_deduction",
                "ca/child_care_expenses",
                "ca/disability_supports_deduction",
                "ca/moving_expenses_deduction",
                "ca/support_payments_deduction_checked",
            ),
        },
        produces={"output": "ca/logging_credit_base"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/logging_income_rate"},
        consumes={"base": "ca/logging_credit_base"},
        produces={"output": "ca/logging_credit_cap"},
    ),
    # T1 line 133 (5006-R Ontario edition): "Line 133: Federal logging tax credit", the lesser of
    # the provinces' total and the cap.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/provinces_logging_tax_credit",
                "ca/logging_credit_cap",
            ),
        },
        produces={"output": "ca/federal_logging_tax_credit"},
    ),
    # T1 line 134 and line 40600 (5006-R Ontario edition): "Line 134 and line 40600: Line 132 minus
    # line 133 (if negative, enter "0") Federal tax =", never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/federal_tax_with_itc_recapture",
            "less": "ca/federal_logging_tax_credit",
        },
        produces={"output": "ca/federal_tax"},
    ),
    # T1 line 139 (line 41700) "Line 134 minus line 138 (if negative, enter "0")": line 134
    # (40600) "Line 132 minus line 133 (if negative, enter "0") Federal tax", see above.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/federal_tax",
            "less": "ca/credits_against_federal_tax",
        },
        produces={"output": "ca/federal_tax_less_credits"},
    ),
    # T691 Part 5 "If line 11 is positive, complete parts 6 and 7." The condition "line 11 is
    # positive" counts 1 when line 11 (the alternative minimum tax payable) is more than 0, and 0
    # otherwise.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/amt_line_11_is_positive_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/amt_alternative_minimum_tax_payable",),
        },
        produces={"output": "ca/amt_part_5_line_11_is_positive"},
    ),
    # T1 line 139 and line 41700 "Line 134 minus line 138 (if negative, enter "0")", or, when Part 5
    # line 11 is positive, Form T691 Part 6 line 14 "Enter this amount on line 41700 of your
    # return.": the federal tax less credits when the count is 0, else the Part 6 line 14 amount.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/amt_part_5_line_11_is_positive",
            "when_none": "ca/federal_tax_less_credits",
            "when_any": "ca/amt_federal_tax_payable_under_minimum_tax",
        },
        produces={"output": "ca/federal_tax_line_41700"},
    ),
}

WIRING = {
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_COLUMN_1_LINE_2})),
    (
        SubtractNotBelowZero,
        frozenset({POLITICAL_CONTRIBUTIONS, POLITICAL_CREDIT_COLUMN_1_LINE_2}),
        frozenset({POLITICAL_CREDIT_COLUMN_1_LINE_3}),
    ),
    (
        ApplyRate,
        frozenset({POLITICAL_CREDIT_COLUMN_1_LINE_3}),
        frozenset({POLITICAL_CREDIT_COLUMN_1_LINE_5}),
    ),
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_COLUMN_1_LINE_6})),
    (
        Sum,
        frozenset({POLITICAL_CREDIT_COLUMN_1_LINE_5, POLITICAL_CREDIT_COLUMN_1_LINE_6}),
        frozenset({POLITICAL_CREDIT_COLUMN_1_LINE_7}),
    ),
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_COLUMN_2_LINE_2})),
    (
        SubtractNotBelowZero,
        frozenset({POLITICAL_CONTRIBUTIONS, POLITICAL_CREDIT_COLUMN_2_LINE_2}),
        frozenset({POLITICAL_CREDIT_COLUMN_2_LINE_3}),
    ),
    (
        ApplyRate,
        frozenset({POLITICAL_CREDIT_COLUMN_2_LINE_3}),
        frozenset({POLITICAL_CREDIT_COLUMN_2_LINE_5}),
    ),
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_COLUMN_2_LINE_6})),
    (
        Sum,
        frozenset({POLITICAL_CREDIT_COLUMN_2_LINE_5, POLITICAL_CREDIT_COLUMN_2_LINE_6}),
        frozenset({POLITICAL_CREDIT_COLUMN_2_LINE_7}),
    ),
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_COLUMN_3_LINE_2})),
    (
        SubtractNotBelowZero,
        frozenset({POLITICAL_CONTRIBUTIONS, POLITICAL_CREDIT_COLUMN_3_LINE_2}),
        frozenset({POLITICAL_CREDIT_COLUMN_3_LINE_3}),
    ),
    (
        ApplyRate,
        frozenset({POLITICAL_CREDIT_COLUMN_3_LINE_3}),
        frozenset({POLITICAL_CREDIT_COLUMN_3_LINE_5}),
    ),
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_COLUMN_3_LINE_6})),
    (
        Sum,
        frozenset({POLITICAL_CREDIT_COLUMN_3_LINE_5, POLITICAL_CREDIT_COLUMN_3_LINE_6}),
        frozenset({POLITICAL_CREDIT_COLUMN_3_LINE_7}),
    ),
    (
        ChooseByRange,
        frozenset(
            {
                POLITICAL_CONTRIBUTIONS,
                POLITICAL_CREDIT_COLUMN_2_LINE_2,
                POLITICAL_CREDIT_COLUMN_3_LINE_2,
                POLITICAL_CREDIT_COLUMN_1_LINE_7,
                POLITICAL_CREDIT_COLUMN_2_LINE_7,
                POLITICAL_CREDIT_COLUMN_3_LINE_7,
            }
        ),
        frozenset({POLITICAL_CREDIT_CHOSEN_COLUMN}),
    ),
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_SHORTCUT_THRESHOLD})),
    (CreditAmount, frozenset(), frozenset({POLITICAL_CREDIT_SHORTCUT_AMOUNT})),
    (
        ChooseByRange,
        frozenset(
            {
                POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
                POLITICAL_CONTRIBUTIONS,
                POLITICAL_CREDIT_COLUMN_3_LINE_2,
                POLITICAL_CREDIT_SHORTCUT_AMOUNT,
                POLITICAL_CREDIT_COLUMN_3_LINE_7,
                POLITICAL_CREDIT_CHOSEN_COLUMN,
            }
        ),
        frozenset({POLITICAL_CREDIT_BEFORE_MAXIMUM}),
    ),
    (CappedAmount, frozenset({POLITICAL_CREDIT_BEFORE_MAXIMUM}), frozenset({POLITICAL_CREDIT})),
    (
        ApplyRate,
        frozenset({LABOUR_SPONSORED_FUNDS_NET_COST}),
        frozenset({LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM}),
    ),
    (
        CappedAmount,
        frozenset({LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM}),
        frozenset({LABOUR_SPONSORED_FUNDS_CREDIT}),
    ),
    (
        Sum,
        frozenset({POLITICAL_CREDIT, INVESTMENT_TAX_CREDIT, LABOUR_SPONSORED_FUNDS_CREDIT}),
        frozenset({CREDITS_AGAINST_FEDERAL_TAX}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FEDERAL_TAX, CREDITS_AGAINST_FEDERAL_TAX}),
        frozenset({FEDERAL_TAX_LESS_CREDITS}),
    ),
    (
        LoggingTaxCredit,
        frozenset({LOGGING_OPERATIONS}),
        frozenset({PROVINCES_LOGGING_TAX_CREDIT}),
    ),
    (
        Sum,
        frozenset(
            {
                TAXABLE_INCOME,
                RRSP_DEDUCTION,
                FHSA_DEDUCTION,
                ELECTED_SPLIT_PENSION_DEDUCTION,
                CHILD_CARE_EXPENSES,
                DISABILITY_SUPPORTS_DEDUCTION,
                MOVING_EXPENSES_DEDUCTION,
                SUPPORT_PAYMENTS_DEDUCTION_CHECKED,
            }
        ),
        frozenset({LOGGING_CREDIT_BASE}),
    ),
    (
        ApplyRate,
        frozenset({LOGGING_CREDIT_BASE}),
        frozenset({LOGGING_CREDIT_CAP}),
    ),
    (
        LesserOf,
        frozenset({PROVINCES_LOGGING_TAX_CREDIT, LOGGING_CREDIT_CAP}),
        frozenset({FEDERAL_LOGGING_TAX_CREDIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FEDERAL_TAX_WITH_ITC_RECAPTURE, FEDERAL_LOGGING_TAX_CREDIT}),
        frozenset({FEDERAL_TAX}),
    ),
    (
        CountByConditions,
        frozenset({AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE}),
        frozenset({AMT_PART_5_LINE_11_IS_POSITIVE}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                AMT_PART_5_LINE_11_IS_POSITIVE,
                FEDERAL_TAX_LESS_CREDITS,
                AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX,
            }
        ),
        frozenset({FEDERAL_TAX_LINE_41700}),
    ),
}
