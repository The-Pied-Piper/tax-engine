"""The CA-ON manifest entries of Form T936 "Calculation of Cumulative Net Investment Loss (CNIL) to
December 31, 2025" (see `test_manifest_t936.py`).

The form `ca/t936` runs once (it has no instances). Its selections are `FORM_STEPS`: one step for
each printed line that computes (`OWN_STEPS`: Part 1, Part 2, Part 3 and Chart A), and the copies of
the return's steps that compute the figures the form reads from the return (`COPIED_STEPS`, a
subset of Form T2048's copies, verbatim, and the Schedule 3 line 19900 sum of Form T657 Step 1
line 8); the return keeps its originals. The five amounts the filer enters are `INPUTS`
(`01o_t936_inputs.yaml`). The form exports Chart A line 14 and Part 3 line C (`FORM_EXPORTS`), and
the return totals them, `core/record_total` over the form's derived kinds `ca/t936.<name>`, into
the two amounts Form T657 Step 1 line 15 and Step 2 line 16 read (see
`capital_gains_deduction_t657.py`).

The two sentences of Chart A, "If the amount is "0", do not complete lines 2 to 17, and enter "0"
on line 20" (line 1) and "If the total from line 14 is "0", do not complete lines 15 to 19, and
enter "0" on line 20" (line 14), are `choose_by_sign` gates: with line 1 at 0 both line 14 (the
export) and line 20 are 0, and with line 14 at 0 line 19 is 0. A `choose_by_sign` takes one
candidate for each sign branch, so the two gates on "not 0" (line 1 and line 19200, which print
"if negative, show in brackets") are two `choose_by_sign` steps, one for each of the two branches,
and a `core/sum` of the two. The form prints a floor ("if negative, enter "0"") on lines 11, 14, 20
and C only; every other difference is signed.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_calculator.jurisdictions.ca.catalog import (
    CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES,
    EXPLORATION_AND_DEVELOPMENT_EXPENSES,
    INTEREST_AND_OTHER_INVESTMENT_INCOME,
    LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_PARTNERSHIP_INCOME,
    NET_RENTAL_INCOME,
    OTHER_INCOME,
    QBT_EXPLORATION_RECOVERY_INCOME,
    QFFP_FORECLOSURE_GAIN_OR_LOSS,
    QFFP_GAIN_OR_LOSS,
    QSBCS_GAIN_OR_LOSS,
    SCHEDULE_3_LINE_19200,
    SCHEDULE_3_LINE_19900,
    T936_ADDITIONAL_INVESTMENT_EXPENSES,
    T936_ADDITIONAL_INVESTMENT_INCOME,
    T936_CHART_A_LINE_3,
    T936_CHART_A_LINE_7,
    T936_CHART_A_LINE_8,
    T936_CHART_A_LINE_8_WHEN_NEGATIVE,
    T936_CHART_A_LINE_8_WHEN_POSITIVE,
    T936_CHART_A_LINE_9,
    T936_CHART_A_LINE_9_AT_INCLUSION_RATE,
    T936_CHART_A_LINE_11,
    T936_CHART_A_LINE_13,
    T936_CHART_A_LINE_14,
    T936_CHART_A_LINE_14_BEFORE_GATE,
    T936_CHART_A_LINE_14_WHEN_LINE_1_NEGATIVE,
    T936_CHART_A_LINE_14_WHEN_LINE_1_POSITIVE,
    T936_CHART_A_LINE_17,
    T936_CHART_A_LINE_19,
    T936_CHART_A_LINE_19_BEFORE_GATE,
    T936_CNIL,
    T936_CUMULATIVE_INVESTMENT_EXPENSES,
    T936_CUMULATIVE_INVESTMENT_INCOME,
    T936_EXPLORATION_EXPENSES_AT_HALF,
    T936_EXPLORATION_RECOVERY_INCOME_CHECKED,
    T936_INVESTMENT_EXPENSES_PREVIOUS_YEARS,
    T936_INVESTMENT_INCOME,
    T936_INVESTMENT_INCOME_PREVIOUS_YEARS,
    T936_LINE_16,
    T936_NET_RENTAL_INCOME,
    T936_NET_RENTAL_LOSS,
    T936_OTHER_INVESTMENT_EXPENSES,
    T936_OTHER_PROPERTY_INCOME,
    T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
    T936_PARTNERSHIP_LOSSES,
    T936_PARTNERSHIP_TAXABLE_CAPITAL_GAINS,
    T936_RECOVERY_OF_EXPLORATION_EXPENSES,
    T936_T3_BOX_21_CAPITAL_GAINS,
    T936_T3_BOX_30_CAPITAL_GAINS,
    T936_T2017_LINE_13,
    T936_T2048_LINE_17215,
    T936_T2048_LINE_17216,
    T936_T2048_LINE_17218,
    T936_T2048_LINE_17218_FOR_2024,
    T936_T2048_LINE_17218_FOR_2025,
    T936_TOTAL_INVESTMENT_EXPENSES,
    T936_TOTAL_INVESTMENT_INCOME,
    TAXABLE_DIVIDENDS,
)
from tests.jurisdictions.ca_on.manifest_families.t2017_reserve import T2017_LINE_13_EXPORT
from tests.jurisdictions.ca_on.manifest_families.t2048 import (
    NET_INVESTMENT_LOSS_REDUCTION_PER_DISPOSITION,
    NON_ACTIVE_PARTNERSHIP_LOSSES_RECORD,
    OTHER_INVESTMENT_EXPENSES_RECORD,
    OTHER_PROPERTY_INCOME_RECORD,
    PARTNERSHIP_TAXABLE_CAPITAL_GAINS_RECORD,
    QSBCS_QFFP_GAINS_RELATED_PER_DISPOSITION,
    TAXABLE_GAINS_RELATED_PER_DISPOSITION,
)

FORM = "ca/t936"

# The five amounts of the form, as the filer enters them, in `01o_t936_inputs.yaml`: Part 3 lines
# 15 and 20, the 2024 part of line 17, and Chart A lines 15 and 16.
INPUTS = frozenset(
    {
        "ca/t936_investment_expenses_previous_years",
        "ca/t936_investment_income_previous_years",
        "ca/t936_t2048_line_17218_for_2024",
        "ca/t936_t3_box_21_capital_gains",
        "ca/t936_t3_box_30_capital_gains",
    }
)

# The exports of the form: Chart A line 14 (Form T657 Step 1 line 15) and Part 3 line C (Form T657
# Step 2 line 16).
FORM_EXPORTS = ("ca/t936_chart_a_line_14", "ca/t936_cnil")
EXPORTS = frozenset(FORM_EXPORTS)

# Each export is read by the return as the record list `ca/t936.<name>`, one record for the form run
# once.
CHART_A_LINE_14_EXPORT = RecordListKind(
    "ca/t936.t936_chart_a_line_14", fields=(T936_CHART_A_LINE_14,)
)
CNIL_EXPORT = RecordListKind("ca/t936.t936_cnil", fields=(T936_CNIL,))

# The other forms' exports the form reads (the form starts from them, as the other forms do).
IMPORTS = frozenset(
    {
        "ca/t776.net_rental_income",
        "ca/t1206_share_dispositions.t1206_under_18_dividend_amount",
        "ca/t2017.t2017_line_31",
        "ca/t2017.t2017_line_13",
        "ca/non_active_partnership_losses.non_active_partnership_losses",
        "ca/other_investment_expenses.other_investment_expenses",
        "ca/other_property_income.other_property_income",
        "ca/partnership_taxable_capital_gains.partnership_taxable_capital_gains",
        "ca/t2048.qbt_taxable_gains_related_to_deduction",
        "ca/t2048.qsbcs_qffp_taxable_gains_related_to_deduction",
        "ca/t2048.qbt_net_investment_loss_reduction",
    }
)

# The return selects none of the steps of the form and declares no output of it in this family.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

# The steps of the form, one for each printed line that computes, with its line in the comment.
OWN_STEPS = {
    # Part 1 line 2 and Part 2 line 9: "Net rental losses (line 12600)" is the negative part of the
    # signed net rental income, and "Net rental income, including recaptured capital cost allowance
    # (line 12600)" its positive part (as Form T2048 Chart A lines 2 and 12 do).
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/net_rental_income",)},
        produces={"output": "ca/t936_net_rental_income"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t936_net_rental_income", "less": "ca/net_rental_income"},
        produces={"output": "ca/t936_net_rental_loss"},
    ),
    # Part 1 line 3 "Limited or non-active partnership losses (line 12200) other than allowable
    # capital losses", part 1 line 6 (68080) "Any other investment expenses claimed in 2025 to earn
    # property income", Part 2 line 11 (68100) "Any other property income reported in 2025": the
    # total of the one record of each shared fact's form.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/non_active_partnership_losses.non_active_partnership_losses"},
        produces={"output": "ca/t936_partnership_losses"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/other_investment_expenses.other_investment_expenses"},
        produces={"output": "ca/t936_other_investment_expenses"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/other_property_income.other_property_income"},
        produces={"output": "ca/t936_other_property_income"},
    ),
    # Part 1 line 5 "50% of exploration and development expenses (line 22400)".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t936_exploration_expenses_rate"},
        consumes={"base": "ca/exploration_and_development_expenses"},
        produces={"output": "ca/t936_exploration_expenses_at_half"},
    ),
    # Part 1 line 7 "Additional investment expenses ... enter whichever is less: line 20 in Chart A
    # or line 25300 of your return". Chart A is always computed (a filer with no gains other than
    # QSBCS or QFFP gets 0 from its lines).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/t936_additional_investment_income",
                "ca/net_capital_losses_of_other_years",
            )
        },
        produces={"output": "ca/t936_additional_investment_expenses"},
    ),
    # Part 1 "Add lines 1 to 7." (Total investment expenses claimed in 2025) A: line 1 "Carrying
    # charges and interest expenses (line 22100)", line 2, line 3, line 4 "Limited partnership
    # losses of other years after 1985 (line 25100)", lines 5, 6 and 7.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/carrying_charges_interest_expenses_and_other_expenses",
                "ca/t936_net_rental_loss",
                "ca/t936_partnership_losses",
                "ca/limited_partnership_losses_of_other_years",
                "ca/t936_exploration_expenses_at_half",
                "ca/t936_other_investment_expenses",
                "ca/t936_additional_investment_expenses",
            )
        },
        produces={"output": "ca/t936_total_investment_expenses"},
    ),
    # Part 2 line 8 "Investment income (lines 12000 and 12100)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/taxable_dividends",
                "ca/interest_and_other_investment_income",
            )
        },
        produces={"output": "ca/t936_investment_income"},
    ),
    # Part 2 line 10 "Net income from limited or non-active partnership (line 12200) other than
    # taxable capital gains": line 12200 less the taxable capital gains in it, the form prints no
    # limit or floor, so the line is signed.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={
            "records": "ca/partnership_taxable_capital_gains.partnership_taxable_capital_gains"
        },
        produces={"output": "ca/t936_partnership_taxable_capital_gains"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/net_partnership_income",
            "less": "ca/t936_partnership_taxable_capital_gains",
        },
        produces={"output": "ca/t936_partnership_income_other_than_gains"},
    ),
    # Part 2 line 12 (68110) "50% of income from the recovery of exploration and development
    # expenses (line 13000)": the recovery part of line 13000, an input (the one of Form T2048 Chart
    # A line 15) that may not exceed line 13000 (refused, not capped), then 50% of it.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/qbt_exploration_recovery_income",
            "bound": "ca/other_income",
        },
        produces={"output": "ca/t936_exploration_recovery_income_checked"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t936_exploration_recovery_rate"},
        consumes={"base": "ca/t936_exploration_recovery_income_checked"},
        produces={"output": "ca/t936_recovery_of_exploration_expenses"},
    ),
    # Part 2 "Add lines 8 to 13." (Total investment income reported in 2025) B: line 13 is Chart A
    # line 20, "Additional investment income".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t936_investment_income",
                "ca/t936_net_rental_income",
                "ca/t936_partnership_income_other_than_gains",
                "ca/t936_other_property_income",
                "ca/t936_recovery_of_exploration_expenses",
                "ca/t936_additional_investment_income",
            )
        },
        produces={"output": "ca/t936_total_investment_income"},
    ),
    # Part 3 line 14 is line A. Line 16 "Line 14 plus line 15" (line 15, "Total investment expenses
    # claimed in previous years after 1987", is an input).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t936_total_investment_expenses",
                "ca/t936_investment_expenses_previous_years",
            )
        },
        produces={"output": "ca/t936_line_16"},
    ),
    # Part 3 line 17 "Amount from line 17218 of Form T2048 for 2024 to 2025": the 2024 amount (an
    # input) plus the total over this return's dispositions of line 17218 of Form T2048 for 2025.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2048.qbt_net_investment_loss_reduction"},
        produces={"output": "ca/t936_t2048_line_17218_for_2025"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t936_t2048_line_17218_for_2024",
                "ca/t936_t2048_line_17218_for_2025",
            )
        },
        produces={"output": "ca/t936_t2048_line_17218"},
    ),
    # Part 3 line 18 "Cumulative investment expenses (line 16 minus line 17)": no floor is printed,
    # so it is signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t936_line_16", "less": "ca/t936_t2048_line_17218"},
        produces={"output": "ca/t936_cumulative_investment_expenses"},
    ),
    # Part 3 line 19 is line B. Line 21 "Cumulative investment income (total of lines 19 and 20)"
    # (line 20, "Total investment income reported in previous years after 1987", is an input).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t936_total_investment_income",
                "ca/t936_investment_income_previous_years",
            )
        },
        produces={"output": "ca/t936_cumulative_investment_income"},
    ),
    # Part 3 line C "Line 18 minus line 21 (if negative, enter "0")" "CNIL to December 31, 2025".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t936_cumulative_investment_expenses",
            "less": "ca/t936_cumulative_investment_income",
        },
        produces={"output": "ca/t936_cnil"},
    ),
    # Chart A line 2 "Amount from line 17215 of Form T2048": the total over the dispositions.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2048.qbt_taxable_gains_related_to_deduction"},
        produces={"output": "ca/t936_t2048_line_17215"},
    ),
    # Chart A line 3 "Line 1 minus line 2" (line 1 is Schedule 3 line 19900, signed): no floor.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/schedule_3_line_19900", "less": "ca/t936_t2048_line_17215"},
        produces={"output": "ca/t936_chart_a_line_3"},
    ),
    # Chart A line 7 "Add lines 4 to 6 (if negative, show in brackets)": Schedule 3 lines 10700,
    # 11000 and 12400, signed.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/qsbcs_gain_or_loss",
                "ca/qffp_gain_or_loss",
                "ca/qffp_foreclosure_gain_or_loss",
            )
        },
        produces={"output": "ca/t936_chart_a_line_7"},
    ),
    # Chart A line 8 "If you reported an amount on line 19200 of Schedule 3, enter the amount from
    # line 13 of Form T2017 (if negative, show in brackets)": line 13 of Form T2017 (the one
    # record) whenever line 19200 is reported, that is more or less than 0 (the line being signed),
    # else 0. A sign gate takes one candidate for each branch, so the two branches are two gates
    # and line 8 is their sum (only one of the two is not 0).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2017.t2017_line_13"},
        produces={"output": "ca/t936_t2017_line_13"},
    ),
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/schedule_3_line_19200",
            "when_positive": ("ca/t936_t2017_line_13",),
            "when_zero": (),
            "when_negative": (),
            "when_non_positive": (),
            "when_non_negative": (),
        },
        produces={"output": "ca/t936_chart_a_line_8_when_positive"},
    ),
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/schedule_3_line_19200",
            "when_positive": (),
            "when_zero": (),
            "when_negative": ("ca/t936_t2017_line_13",),
            "when_non_positive": (),
            "when_non_negative": (),
        },
        produces={"output": "ca/t936_chart_a_line_8_when_negative"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t936_chart_a_line_8_when_positive",
                "ca/t936_chart_a_line_8_when_negative",
            )
        },
        produces={"output": "ca/t936_chart_a_line_8"},
    ),
    # Chart A line 9 "Line 7 plus line 8 (if negative, show in brackets)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t936_chart_a_line_7", "ca/t936_chart_a_line_8")},
        produces={"output": "ca/t936_chart_a_line_9"},
    ),
    # Chart A line 10 "Inclusion rate × 50%", then line 11 "Line 9 multiplied by the percentage on
    # line 10 (if negative, enter "0")": the product, signed, then its positive part.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t936_chart_a_inclusion_rate"},
        consumes={"base": "ca/t936_chart_a_line_9"},
        produces={"output": "ca/t936_chart_a_line_9_at_inclusion_rate"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/t936_chart_a_line_9_at_inclusion_rate",)},
        produces={"output": "ca/t936_chart_a_line_11"},
    ),
    # Chart A line 12 "Amount from line 17216 of Form T2048": the total over the dispositions.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2048.qsbcs_qffp_taxable_gains_related_to_deduction"},
        produces={"output": "ca/t936_t2048_line_17216"},
    ),
    # Chart A line 13 "Line 11 minus line 12": no floor is printed, so it is signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t936_chart_a_line_11", "less": "ca/t936_t2048_line_17216"},
        produces={"output": "ca/t936_chart_a_line_13"},
    ),
    # Chart A line 14 "Line 3 minus line 13 (if negative, enter "0")", before the gate of line 1.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/t936_chart_a_line_3", "less": "ca/t936_chart_a_line_13"},
        produces={"output": "ca/t936_chart_a_line_14_before_gate"},
    ),
    # Chart A line 1 "If the amount is "0", do not complete lines 2 to 17, and enter "0" on line
    # 20": line 14 is the computed amount whenever line 1 is more or less than 0 (the line being
    # signed), else 0. The two branches are two gates and line 14 is their sum (only one of the two
    # is not 0).
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/schedule_3_line_19900",
            "when_positive": ("ca/t936_chart_a_line_14_before_gate",),
            "when_zero": (),
            "when_negative": (),
            "when_non_positive": (),
            "when_non_negative": (),
        },
        produces={"output": "ca/t936_chart_a_line_14_when_line_1_positive"},
    ),
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/schedule_3_line_19900",
            "when_positive": (),
            "when_zero": (),
            "when_negative": ("ca/t936_chart_a_line_14_before_gate",),
            "when_non_positive": (),
            "when_non_negative": (),
        },
        produces={"output": "ca/t936_chart_a_line_14_when_line_1_negative"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t936_chart_a_line_14_when_line_1_positive",
                "ca/t936_chart_a_line_14_when_line_1_negative",
            )
        },
        produces={"output": "ca/t936_chart_a_line_14"},
    ),
    # Chart A line 17 "Line 15 minus line 16" (68150): box 21 less box 30 of the 2025 T3 slips, no
    # floor printed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t936_t3_box_21_capital_gains",
            "less": "ca/t936_t3_box_30_capital_gains",
        },
        produces={"output": "ca/t936_chart_a_line_17"},
    ),
    # Chart A line 18 "Inclusion rate × 50%", then line 19 "Line 17 multiplied by the percentage
    # on line 18": signed, no floor printed.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t936_t3_inclusion_rate"},
        consumes={"base": "ca/t936_chart_a_line_17"},
        produces={"output": "ca/t936_chart_a_line_19_before_gate"},
    ),
    # Chart A line 14 "If the total from line 14 is "0", do not complete lines 15 to 19, and enter
    # "0" on line 20": line 19 is the product only when line 14 is more than 0, else 0.
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/t936_chart_a_line_14",
            "when_positive": ("ca/t936_chart_a_line_19_before_gate",),
            "when_zero": (),
            "when_negative": (),
            "when_non_positive": (),
            "when_non_negative": (),
        },
        produces={"output": "ca/t936_chart_a_line_19"},
    ),
    # Chart A line 20 "Line 14 minus line 19 (if negative, enter "0")" "Additional investment
    # income".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/t936_chart_a_line_14", "less": "ca/t936_chart_a_line_19"},
        produces={"output": "ca/t936_additional_investment_income"},
    ),
}

# Copies of the return's steps that compute the figures the form reads from the return, a subset
# of Form T2048's copies verbatim (the return keeps its originals; a form reads the manifest's
# inputs and other forms' exports, never the return's artifacts): the taxable capital gains of
# Schedule 3 line 24 (`ca/included_capital_gain`) and the gains of lines 10700, 11000 and 12400,
# Schedule 3 line 19200, the net rental income of line 12600, the taxable dividends and the
# interest and other investment income of lines 12000 and 12100, the carrying charges and interest
# expenses of line 22100 and the net capital losses of other years of line 25300, with the steps
# each of those reads; and the sum of Schedule 3 line 19900 of Form T657 Step 1 line 8.
COPIED_STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1206_share_dispositions.t1206_under_18_dividend_amount"},
        produces={"output": "ca/t1206_under_18_dividend_amount"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/qsbcs_dispositions"},
        produces={"output": "ca/qsbcs_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/qffp_gains",
        params={},
        consumes={"dispositions": "ca/qffp_dispositions"},
        produces={"output": "ca/qffp_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/qffp_gains",
        params={},
        consumes={"dispositions": "ca/qffp_foreclosure_dispositions"},
        produces={"output": "ca/qffp_foreclosure_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/share_dispositions"},
        produces={"output": "ca/share_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/depreciable_property_gains",
        params={},
        consumes={"dispositions": "ca/real_estate_dispositions"},
        produces={"output": "ca/real_estate_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/bond_dispositions"},
        produces={"output": "ca/bond_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/crypto_asset_dispositions"},
        produces={"output": "ca/crypto_asset_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/qffp_gains",
        params={},
        consumes={"dispositions": "ca/other_foreclosure_dispositions"},
        produces={"output": "ca/other_foreclosure_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/personal_use_property_gains",
        params={"minimum": "ca/personal_use_property_minimum"},
        consumes={"dispositions": "ca/personal_use_property_dispositions"},
        produces={"output": "ca/personal_use_property_gain_rows"},
    ),
    CapabilitySelection(
        name="ca/principal_residence_line_57",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_57"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/personal_use_property_gain_rows",
                "ca/principal_residence_line_57",
            )
        },
        produces={"output": "ca/personal_use_property_gain"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/listed_personal_property_dispositions"},
        produces={"output": "ca/listed_personal_property_gain_or_loss"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/listed_personal_property_gain_or_loss",
            "less": "ca/unapplied_listed_personal_property_losses",
        },
        produces={"output": "ca/listed_personal_property_net_gain"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/qsbcs_gain_or_loss",
                "ca/qffp_gain_or_loss",
                "ca/qffp_foreclosure_gain_or_loss",
                "ca/share_gain_or_loss",
                "ca/real_estate_gain_or_loss",
                "ca/bond_gain_or_loss",
                "ca/crypto_asset_gain_or_loss",
                "ca/other_foreclosure_gain_or_loss",
                "ca/personal_use_property_gain",
                "ca/listed_personal_property_net_gain",
            )
        },
        produces={"output": "ca/capital_gains_of_qualified_and_other_properties"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_of_qualified_and_other_properties",
            "less": "ca/capital_gains_deferral_checked",
        },
        produces={"output": "ca/capital_gains_after_deferral"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/capital_gains_after_deferral",
                "ca/slip_capital_gains_or_losses",
                "ca/t3_capital_gains_or_losses",
            )
        },
        produces={"output": "ca/capital_gains_before_investment_loss_reduction"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_before_investment_loss_reduction",
            "less": "ca/business_investment_loss_reduction",
        },
        produces={"output": "ca/capital_gains_before_reserves"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2017.t2017_line_31"},
        produces={"output": "ca/schedule_3_line_19200"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/capital_gains_before_reserves",
                "ca/schedule_3_line_19200",
            )
        },
        produces={"output": "ca/capital_gain"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/capital_gains_inclusion_rate"},
        consumes={"base": "ca/capital_gain"},
        produces={"output": "ca/included_capital_gain"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/included_capital_gain",
                "ca/partnership_gains_at_full_inclusion",
            )
        },
        produces={"output": "ca/taxable_capital_gains"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t3_taxable_dividends",
                "ca/t4ps_taxable_dividends",
                "ca/t5_taxable_dividends",
                "ca/t5013_taxable_dividends",
            )
        },
        produces={"output": "ca/slip_taxable_dividends"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/eligible_dividend_gross_up"},
        consumes={"base": "ca/eligible_dividends_received_without_a_slip"},
        produces={"output": "ca/eligible_dividends_grossed_up"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/other_dividend_gross_up"},
        consumes={"base": "ca/other_dividends_received_without_a_slip"},
        produces={"output": "ca/other_dividends_grossed_up"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/eligible_dividends_grossed_up",
                "ca/other_dividends_grossed_up",
            )
        },
        produces={"output": "ca/dividends_without_a_slip_grossed_up"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/slip_taxable_dividends",
                "ca/dividends_without_a_slip_grossed_up",
                "ca/t1206_under_18_dividend_amount",
            )
        },
        produces={"output": "ca/taxable_dividends"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t3_investment_income",
                "ca/t5_investment_income",
                "ca/t5013_investment_income",
                "ca/investment_income_credited_not_received",
                "ca/tax_refund_interest",
                "ca/foreign_investment_income",
                "ca/investment_income_without_a_slip",
                "ca/investment_royalties",
            )
        },
        produces={"output": "ca/investment_income_before_prior_years"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/investment_income_reported_in_previous_years",
            "bound": "ca/investment_income_before_prior_years",
        },
        produces={"output": "ca/investment_income_reported_in_previous_years_applied"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/investment_income_before_prior_years",
            "less": "ca/investment_income_reported_in_previous_years_applied",
        },
        produces={"output": "ca/interest_and_other_investment_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t776.net_rental_income"},
        produces={"output": "ca/net_rental_income"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/total_carrying_charges",
                "ca/total_interest_expenses",
                "ca/total_other_expenses",
            )
        },
        produces={"output": "ca/carrying_charges_interest_expenses_and_other_expenses"},
    ),
    # Schedule 3 lines 543 and 544, summed (lines 2 and 3 of T1436).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/schedule_3_line_543", "ca/schedule_3_line_544")},
        produces={"output": "ca/schedule_3_lines_543_and_544_total"},
    ),
    # Line 2 (a): the amount entered less the Schedule 3 sum, not below 0.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": (
                "ca/capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property"
            ),
            "less": "ca/schedule_3_lines_543_and_544_total",
        },
        produces={"output": "ca/capital_gains_deductions_1988_and_1989_amount_a"},
    ),
    # Line 1, x 2.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_1_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1985_to_1987"},
        produces={"output": "ca/capital_gains_deductions_line_1"},
    ),
    # Line 2, x 1.5.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_2_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1988_and_1989_amount_a"},
        produces={"output": "ca/capital_gains_deductions_line_2"},
    ),
    # Line 3, the amount entered less amount (a), signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_deductions_1988_and_1989_eligible_capital_property",
            "less": "ca/capital_gains_deductions_1988_and_1989_amount_a",
        },
        produces={"output": "ca/capital_gains_deductions_1988_and_1989_after_amount_a"},
    ),
    # Line 3, the lesser of that difference and the Schedule 3 sum.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/capital_gains_deductions_1988_and_1989_after_amount_a",
                "ca/schedule_3_lines_543_and_544_total",
            )
        },
        produces={"output": "ca/capital_gains_deductions_1988_and_1989_limited"},
    ),
    # Line 3, x 1.3333.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_3_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1988_and_1989_limited"},
        produces={"output": "ca/capital_gains_deductions_line_3"},
    ),
    # Line 4, x 1.3333.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_4_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1990_to_1999"},
        produces={"output": "ca/capital_gains_deductions_line_4"},
    ),
    # Line 5, x 1/IR, rounded half-up to the cent; 0 when IR is 0.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1436_line_5_rounding"},
        consumes={
            "amount": "ca/capital_gains_deductions_2000",
            "numerator": "ca/net_capital_loss_numerator_one_2000",
            "denominator": "ca/t657_inclusion_rate_2000",
        },
        produces={"output": "ca/capital_gains_deductions_line_5"},
    ),
    # Line 6, x 2.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_6_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_2001_to_2024"},
        produces={"output": "ca/capital_gains_deductions_line_6"},
    ),
    # Line 7, "Add lines 1 to 6.": the six lines after their multipliers.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/capital_gains_deductions_line_1",
                "ca/capital_gains_deductions_line_2",
                "ca/capital_gains_deductions_line_3",
                "ca/capital_gains_deductions_line_4",
                "ca/capital_gains_deductions_line_5",
                "ca/capital_gains_deductions_line_6",
            )
        },
        produces={"output": "ca/capital_gains_deductions_claimed_1985_to_2024"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/other_business_investment_loss_reductions_1986_to_1994",
                "ca/other_business_investment_loss_reductions_1994_to_1996",
                "ca/other_business_investment_loss_reductions_1997_to_1999",
                "ca/other_business_investment_loss_reductions_2000",
                "ca/other_business_investment_loss_reductions_2001_to_2023",
                "ca/other_business_investment_loss_reductions_2024",
            )
        },
        produces={"output": "ca/other_business_investment_loss_reductions_1986_to_2024"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_deductions_claimed_1985_to_2024",
            "less": "ca/other_business_investment_loss_reductions_1986_to_2024",
        },
        produces={"output": "ca/business_investment_loss_reduction_available"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/business_investment_loss_reduction_available",
                "ca/business_investment_loss",
            )
        },
        produces={"output": "ca/business_investment_loss_reduction"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/pre_1986_deductions_factor_1988_and_1989"},
        consumes={"base": "ca/pre_1986_deductions_1988_and_1989"},
        produces={"output": "ca/pre_1986_deductions_adjusted_1988_and_1989"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/pre_1986_deductions_factor_1990_to_1999"},
        consumes={"base": "ca/pre_1986_deductions_1990_to_1999"},
        produces={"output": "ca/pre_1986_deductions_adjusted_1990_to_1999"},
    ),
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/pre_1986_deductions_adjusted_2000_rounding"},
        consumes={
            "amount": "ca/pre_1986_deductions_2000",
            "numerator": "ca/net_capital_loss_numerator_one_2000",
            "denominator": "ca/net_capital_loss_twice_ir_2000",
        },
        produces={"output": "ca/pre_1986_deductions_adjusted_2000"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/pre_1986_deductions_before_1988",
                "ca/pre_1986_deductions_adjusted_1988_and_1989",
                "ca/pre_1986_deductions_adjusted_1990_to_1999",
                "ca/pre_1986_deductions_adjusted_2000",
                "ca/pre_1986_deductions_2001_to_2024",
            )
        },
        produces={"output": "ca/pre_1986_deductions_total"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/net_capital_losses_before_may_23_1985",
            "less": "ca/pre_1986_deductions_total",
        },
        produces={"output": "ca/pre_1986_capital_loss_balance"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_before_may_23_1985"},
        consumes={"base": "ca/pre_1986_capital_loss_balance"},
        produces={"output": "ca/adjusted_gross_capital_losses_before_may_23_1985"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_1985_to_1987"},
        consumes={"base": "ca/unapplied_net_capital_losses_1985_to_1987"},
        produces={"output": "ca/adjusted_gross_capital_losses_1985_to_1987"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_1988_and_1989"},
        consumes={"base": "ca/unapplied_net_capital_losses_1988_and_1989"},
        produces={"output": "ca/adjusted_gross_capital_losses_1988_and_1989"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_1990_to_1999"},
        consumes={"base": "ca/unapplied_net_capital_losses_1990_to_1999"},
        produces={"output": "ca/adjusted_gross_capital_losses_1990_to_1999"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_inclusion_rate_factor_2001_to_2024"},
        consumes={"base": "ca/unapplied_net_capital_losses_2001_to_2024"},
        produces={"output": "ca/adjusted_gross_capital_losses_2001_to_2024"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/adjusted_gross_capital_losses_before_may_23_1985",
                "ca/adjusted_gross_capital_losses_1985_to_1987",
                "ca/adjusted_gross_capital_losses_1988_and_1989",
                "ca/adjusted_gross_capital_losses_1990_to_1999",
                "ca/adjusted_gross_capital_losses_2000",
                "ca/adjusted_gross_capital_losses_2001_to_2024",
            )
        },
        produces={"output": "ca/total_adjusted_net_capital_losses"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/total_adjusted_net_capital_losses",
                "ca/taxable_capital_gains",
            )
        },
        produces={"output": "ca/net_capital_losses_available_to_claim"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/net_capital_losses_claimed",
            "bound": "ca/net_capital_losses_available_to_claim",
        },
        produces={"output": "ca/adjusted_net_capital_losses_applied"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/total_adjusted_net_capital_losses",
            "less": "ca/adjusted_net_capital_losses_applied",
        },
        produces={"output": "ca/unapplied_adjusted_net_capital_losses"},
    ),
    CapabilitySelection(
        name="ca/lesser_of_with_maximum",
        params={"maximum": "ca/net_capital_losses_additional_deduction_maximum"},
        consumes={
            "amounts": (
                "ca/pre_1986_capital_loss_balance",
                "ca/unapplied_adjusted_net_capital_losses",
            )
        },
        produces={"output": "ca/net_capital_losses_additional_deduction"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/adjusted_net_capital_losses_applied",
                "ca/net_capital_losses_additional_deduction",
            )
        },
        produces={"output": "ca/net_capital_losses_of_other_years"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/net_capital_loss_twice_ir_fraction_2000"},
        consumes={"base": "ca/t657_inclusion_rate_2000"},
        produces={"output": "ca/net_capital_loss_twice_ir_2000"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/net_capital_loss_numerator_one_2000"},
        consumes={},
        produces={"output": "ca/net_capital_loss_numerator_one_2000"},
    ),
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/adjusted_gross_capital_losses_2000_rounding"},
        consumes={
            "amount": "ca/unapplied_net_capital_losses_2000",
            "numerator": "ca/net_capital_loss_numerator_one_2000",
            "denominator": "ca/net_capital_loss_twice_ir_2000",
        },
        produces={"output": "ca/adjusted_gross_capital_losses_2000"},
    ),
    # Schedule 3 line 4 and line 13200 "Total gain or loss (add all the amounts under column 5)",
    # floored at 0: a share loss leaves no share gain for the deferral, so the bound is 0 then.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/share_gain_or_loss",)},
        produces={"output": "ca/share_gain_not_below_zero"},
    ),
    # Schedule 3 line 13 and line 16100 "Capital gains deferral from qualifying dispositions of
    # eligible small business corporation shares included on line 4" is at most line 4, the share
    # gain floored at 0. It is refused above it, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/capital_gains_deferral",
            "bound": "ca/share_gain_not_below_zero",
        },
        produces={"output": "ca/capital_gains_deferral_checked"},
    ),
    # Form T657 Step 1 line 8 "Total taxable capital gains (or net capital losses) from line 19900
    # of Schedule 3 (if negative, show in brackets)": Schedule 3 line 24 plus line 25, signed (the
    # copy of the step of `06b_capital_gains_deduction_t657.yaml`); Chart A line 1 reads it.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/included_capital_gain",
                "ca/partnership_gains_at_full_inclusion",
            )
        },
        produces={"output": "ca/schedule_3_line_19900"},
    ),
}

FORM_STEPS = OWN_STEPS | COPIED_STEPS
FORM_STEPS_BY_OUTPUT = {step.produces["output"]: step for step in FORM_STEPS}

# The wiring of the form's own steps, as `test_manifest_t936.py` reads it from the composed form:
# the capability class, the kinds it consumes and the kinds it produces.
FORM_WIRING = {
    (
        SumNotBelowZero,
        frozenset({NET_RENTAL_INCOME}),
        frozenset({T936_NET_RENTAL_INCOME}),
    ),
    (
        Subtract,
        frozenset({T936_NET_RENTAL_INCOME, NET_RENTAL_INCOME}),
        frozenset({T936_NET_RENTAL_LOSS}),
    ),
    (
        RecordTotal,
        frozenset({NON_ACTIVE_PARTNERSHIP_LOSSES_RECORD}),
        frozenset({T936_PARTNERSHIP_LOSSES}),
    ),
    (
        RecordTotal,
        frozenset({OTHER_INVESTMENT_EXPENSES_RECORD}),
        frozenset({T936_OTHER_INVESTMENT_EXPENSES}),
    ),
    (
        RecordTotal,
        frozenset({OTHER_PROPERTY_INCOME_RECORD}),
        frozenset({T936_OTHER_PROPERTY_INCOME}),
    ),
    (
        ApplyRate,
        frozenset({EXPLORATION_AND_DEVELOPMENT_EXPENSES}),
        frozenset({T936_EXPLORATION_EXPENSES_AT_HALF}),
    ),
    (
        LesserOf,
        frozenset({T936_ADDITIONAL_INVESTMENT_INCOME, NET_CAPITAL_LOSSES_OF_OTHER_YEARS}),
        frozenset({T936_ADDITIONAL_INVESTMENT_EXPENSES}),
    ),
    (
        Sum,
        frozenset(
            {
                CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES,
                T936_NET_RENTAL_LOSS,
                T936_PARTNERSHIP_LOSSES,
                LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS,
                T936_EXPLORATION_EXPENSES_AT_HALF,
                T936_OTHER_INVESTMENT_EXPENSES,
                T936_ADDITIONAL_INVESTMENT_EXPENSES,
            }
        ),
        frozenset({T936_TOTAL_INVESTMENT_EXPENSES}),
    ),
    (
        Sum,
        frozenset({TAXABLE_DIVIDENDS, INTEREST_AND_OTHER_INVESTMENT_INCOME}),
        frozenset({T936_INVESTMENT_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({PARTNERSHIP_TAXABLE_CAPITAL_GAINS_RECORD}),
        frozenset({T936_PARTNERSHIP_TAXABLE_CAPITAL_GAINS}),
    ),
    (
        Subtract,
        frozenset({NET_PARTNERSHIP_INCOME, T936_PARTNERSHIP_TAXABLE_CAPITAL_GAINS}),
        frozenset({T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS}),
    ),
    (
        AtMost,
        frozenset({QBT_EXPLORATION_RECOVERY_INCOME, OTHER_INCOME}),
        frozenset({T936_EXPLORATION_RECOVERY_INCOME_CHECKED}),
    ),
    (
        ApplyRate,
        frozenset({T936_EXPLORATION_RECOVERY_INCOME_CHECKED}),
        frozenset({T936_RECOVERY_OF_EXPLORATION_EXPENSES}),
    ),
    (
        Sum,
        frozenset(
            {
                T936_INVESTMENT_INCOME,
                T936_NET_RENTAL_INCOME,
                T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
                T936_OTHER_PROPERTY_INCOME,
                T936_RECOVERY_OF_EXPLORATION_EXPENSES,
                T936_ADDITIONAL_INVESTMENT_INCOME,
            }
        ),
        frozenset({T936_TOTAL_INVESTMENT_INCOME}),
    ),
    (
        Sum,
        frozenset({T936_TOTAL_INVESTMENT_EXPENSES, T936_INVESTMENT_EXPENSES_PREVIOUS_YEARS}),
        frozenset({T936_LINE_16}),
    ),
    (
        RecordTotal,
        frozenset({NET_INVESTMENT_LOSS_REDUCTION_PER_DISPOSITION}),
        frozenset({T936_T2048_LINE_17218_FOR_2025}),
    ),
    (
        Sum,
        frozenset({T936_T2048_LINE_17218_FOR_2024, T936_T2048_LINE_17218_FOR_2025}),
        frozenset({T936_T2048_LINE_17218}),
    ),
    (
        Subtract,
        frozenset({T936_LINE_16, T936_T2048_LINE_17218}),
        frozenset({T936_CUMULATIVE_INVESTMENT_EXPENSES}),
    ),
    (
        Sum,
        frozenset({T936_TOTAL_INVESTMENT_INCOME, T936_INVESTMENT_INCOME_PREVIOUS_YEARS}),
        frozenset({T936_CUMULATIVE_INVESTMENT_INCOME}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({T936_CUMULATIVE_INVESTMENT_EXPENSES, T936_CUMULATIVE_INVESTMENT_INCOME}),
        frozenset({T936_CNIL}),
    ),
    (
        RecordTotal,
        frozenset({TAXABLE_GAINS_RELATED_PER_DISPOSITION}),
        frozenset({T936_T2048_LINE_17215}),
    ),
    (
        Subtract,
        frozenset({SCHEDULE_3_LINE_19900, T936_T2048_LINE_17215}),
        frozenset({T936_CHART_A_LINE_3}),
    ),
    (
        Sum,
        frozenset({QSBCS_GAIN_OR_LOSS, QFFP_GAIN_OR_LOSS, QFFP_FORECLOSURE_GAIN_OR_LOSS}),
        frozenset({T936_CHART_A_LINE_7}),
    ),
    (
        RecordTotal,
        frozenset({T2017_LINE_13_EXPORT}),
        frozenset({T936_T2017_LINE_13}),
    ),
    (
        ChooseBySign,
        frozenset({SCHEDULE_3_LINE_19200, T936_T2017_LINE_13}),
        frozenset({T936_CHART_A_LINE_8_WHEN_POSITIVE}),
    ),
    (
        ChooseBySign,
        frozenset({SCHEDULE_3_LINE_19200, T936_T2017_LINE_13}),
        frozenset({T936_CHART_A_LINE_8_WHEN_NEGATIVE}),
    ),
    (
        Sum,
        frozenset({T936_CHART_A_LINE_8_WHEN_POSITIVE, T936_CHART_A_LINE_8_WHEN_NEGATIVE}),
        frozenset({T936_CHART_A_LINE_8}),
    ),
    (
        Sum,
        frozenset({T936_CHART_A_LINE_7, T936_CHART_A_LINE_8}),
        frozenset({T936_CHART_A_LINE_9}),
    ),
    (
        ApplyRate,
        frozenset({T936_CHART_A_LINE_9}),
        frozenset({T936_CHART_A_LINE_9_AT_INCLUSION_RATE}),
    ),
    (
        SumNotBelowZero,
        frozenset({T936_CHART_A_LINE_9_AT_INCLUSION_RATE}),
        frozenset({T936_CHART_A_LINE_11}),
    ),
    (
        RecordTotal,
        frozenset({QSBCS_QFFP_GAINS_RELATED_PER_DISPOSITION}),
        frozenset({T936_T2048_LINE_17216}),
    ),
    (
        Subtract,
        frozenset({T936_CHART_A_LINE_11, T936_T2048_LINE_17216}),
        frozenset({T936_CHART_A_LINE_13}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({T936_CHART_A_LINE_3, T936_CHART_A_LINE_13}),
        frozenset({T936_CHART_A_LINE_14_BEFORE_GATE}),
    ),
    (
        ChooseBySign,
        frozenset({SCHEDULE_3_LINE_19900, T936_CHART_A_LINE_14_BEFORE_GATE}),
        frozenset({T936_CHART_A_LINE_14_WHEN_LINE_1_POSITIVE}),
    ),
    (
        ChooseBySign,
        frozenset({SCHEDULE_3_LINE_19900, T936_CHART_A_LINE_14_BEFORE_GATE}),
        frozenset({T936_CHART_A_LINE_14_WHEN_LINE_1_NEGATIVE}),
    ),
    (
        Sum,
        frozenset(
            {T936_CHART_A_LINE_14_WHEN_LINE_1_POSITIVE, T936_CHART_A_LINE_14_WHEN_LINE_1_NEGATIVE}
        ),
        frozenset({T936_CHART_A_LINE_14}),
    ),
    (
        Subtract,
        frozenset({T936_T3_BOX_21_CAPITAL_GAINS, T936_T3_BOX_30_CAPITAL_GAINS}),
        frozenset({T936_CHART_A_LINE_17}),
    ),
    (
        ApplyRate,
        frozenset({T936_CHART_A_LINE_17}),
        frozenset({T936_CHART_A_LINE_19_BEFORE_GATE}),
    ),
    (
        ChooseBySign,
        frozenset({T936_CHART_A_LINE_14, T936_CHART_A_LINE_19_BEFORE_GATE}),
        frozenset({T936_CHART_A_LINE_19}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({T936_CHART_A_LINE_14, T936_CHART_A_LINE_19}),
        frozenset({T936_ADDITIONAL_INVESTMENT_INCOME}),
    ),
}

# The kinds the copies produce which the form's own steps read (the rest of the copies' products
# are read by other copies): the form's whole use of the return's figures.
COPIED_PRODUCTS_READ = frozenset(
    {
        "ca/carrying_charges_interest_expenses_and_other_expenses",
        "ca/net_rental_income",
        "ca/taxable_dividends",
        "ca/interest_and_other_investment_income",
        "ca/net_capital_losses_of_other_years",
        "ca/qsbcs_gain_or_loss",
        "ca/qffp_gain_or_loss",
        "ca/qffp_foreclosure_gain_or_loss",
        "ca/schedule_3_line_19200",
        "ca/schedule_3_line_19900",
    }
)

# The record lists the return reads, `core/record_total` over each export of the form.
EXPORT_RECORDS = {
    "ca/t936_chart_a_line_14": CHART_A_LINE_14_EXPORT,
    "ca/t936_cnil": CNIL_EXPORT,
}
