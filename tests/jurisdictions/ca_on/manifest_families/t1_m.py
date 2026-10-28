"""The CA-ON manifest entries of Form T1-M, Moving Expenses Deduction (see `test_manifest.py` and
`test_manifest_t1_m.py`).

T1-M is a form of the manifest: its 21 selections belong to the form `ca/t1_m` (`FORM_STEPS`), run
once for each move of `ca/t1_m_moves`, whose 19 fields are the caller's inputs of one move
(`FORM_INPUTS`). Line 28 is checked against the income lines it is taken from before lines 29 and
30 read it. The form exports line 29 and line 30 of each move, readable by the other forms as
`ca/t1_m.<export>` (`FORM_EXPORTS`). The return's own entries are the instances input and the T1
line 21900 total over the moves (`STEPS` and `WIRING`): the return reads the exported line 29 of
every move and declares no output for the line 30 that nothing reads (`OUTPUTS` is empty).
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.threshold_gate import ThresholdGate
from tax_calculator.jurisdictions.ca.catalog import (
    EMPLOYMENT_INCOME,
    MOVING_ACCOMMODATION_EXPENSES,
    MOVING_BUSINESS_INCOME,
    MOVING_BUYING_LEGAL_FEES,
    MOVING_BUYING_SUBTOTAL,
    MOVING_BUYING_TAXES,
    MOVING_COMMISSION_INCOME,
    MOVING_DISTANCE_DIFFERENCE,
    MOVING_ELIGIBLE_INCOME_LINES,
    MOVING_EXPENSES_CLAIM,
    MOVING_EXPENSES_DEDUCTION,
    MOVING_FARMING_INCOME,
    MOVING_FISHING_INCOME,
    MOVING_INCIDENTAL_COSTS,
    MOVING_LEASE_AND_INCIDENTAL_SUBTOTAL,
    MOVING_LEASE_CANCELLATION,
    MOVING_LESSER_OF_EXPENSES_AND_INCOME,
    MOVING_MEAL_EXPENSES,
    MOVING_NET_ELIGIBLE_INCOME,
    MOVING_NET_ELIGIBLE_INCOME_CHECKED,
    MOVING_NET_EXPENSES,
    MOVING_NET_EXPENSES_CARRIED,
    MOVING_NEW_HOME_DISTANCE,
    MOVING_OLD_HOME_DISTANCE,
    MOVING_OLD_HOME_MAINTENANCE,
    MOVING_OLD_HOME_MAINTENANCE_CAP,
    MOVING_OLD_HOME_MAINTENANCE_CHECKED,
    MOVING_PROFESSIONAL_INCOME,
    MOVING_REIMBURSEMENT,
    MOVING_SELLING_ADVERTISING,
    MOVING_SELLING_COMMISSION,
    MOVING_SELLING_LEGAL_FEES,
    MOVING_SELLING_OTHER_COSTS,
    MOVING_SELLING_SUBTOTAL,
    MOVING_TEMPORARY_LIVING_SUBTOTAL,
    MOVING_TEMPORARY_LODGING,
    MOVING_TEMPORARY_MEALS,
    MOVING_TOTAL_EXPENSES,
    MOVING_TRANSPORTATION_AND_STORAGE,
    MOVING_TRAVEL_EXPENSES,
    MOVING_TRAVEL_EXPENSES_SUBTOTAL,
    MOVING_UNUSED_EXPENSES,
    MOVING_UNUSED_EXPENSES_BEFORE_TEST,
    OTHER_EMPLOYMENT_INCOME,
    TAXABLE_SCHOLARSHIPS,
)
from tests.jurisdictions.ca_on.manifest_families.t1139 import (
    BUSINESS_PROFIT_ON_RETURN_LINES,
    COMMISSION_PROFIT_ON_RETURN_LINES,
    FARMING_PROFIT_ON_RETURN_LINES,
    FISHING_PROFIT_ON_RETURN_LINES,
    PROFESSIONAL_PROFIT_ON_RETURN_LINES,
)

# The caller's inputs of one move, the fields of `ca/t1_m_moves` (the form's lines 1, 2, 4, 5, 6, 7,
# 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 25 and 28).
FORM_INPUTS = frozenset(
    {
        "ca/moving_old_home_distance",
        "ca/moving_new_home_distance",
        "ca/moving_transportation_and_storage",
        "ca/moving_travel_expenses",
        "ca/moving_accommodation_expenses",
        "ca/moving_meal_expenses",
        "ca/moving_temporary_lodging",
        "ca/moving_temporary_meals",
        "ca/moving_lease_cancellation",
        "ca/moving_incidental_costs",
        "ca/moving_old_home_maintenance",
        "ca/moving_selling_commission",
        "ca/moving_selling_legal_fees",
        "ca/moving_selling_advertising",
        "ca/moving_selling_other_costs",
        "ca/moving_buying_legal_fees",
        "ca/moving_buying_taxes",
        "ca/moving_reimbursement",
        "ca/moving_net_eligible_income",
    }
)

FORM_EXPORTS = (
    "ca/moving_expenses_claim",
    "ca/moving_unused_expenses",
)

FORM_STEPS = {
    # T1-M Part 2 "Line 1 minus line 2" (line 3): the old home distance less the new one. The form
    # prints no floor, so the difference is signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/moving_old_home_distance",
            "less": "ca/moving_new_home_distance",
        },
        produces={"output": "ca/moving_distance_difference"},
    ),
    # T1-M Part 4 "Add lines 5 to 7." (line 8): the travel, accommodation and meal expenses.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/moving_travel_expenses",
                "ca/moving_accommodation_expenses",
                "ca/moving_meal_expenses",
            )
        },
        produces={"output": "ca/moving_travel_expenses_subtotal"},
    ),
    # T1-M Part 4 "Line 9 plus line 10" (line 11): the temporary lodging and meals.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/moving_temporary_lodging", "ca/moving_temporary_meals")},
        produces={"output": "ca/moving_temporary_living_subtotal"},
    ),
    # T1-M Part 4 "Costs to maintain your old home when vacant (maximum $5,000)" (line 14): the
    # caller's costs; above the $5,000 maximum they are an input error, not capped.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/moving_old_home_maintenance_cap"},
        consumes={},
        produces={"output": "ca/moving_old_home_maintenance_cap"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/moving_old_home_maintenance",
            "bound": "ca/moving_old_home_maintenance_cap",
        },
        produces={"output": "ca/moving_old_home_maintenance_checked"},
    ),
    # T1-M Part 4 "Add lines 12 to 14." (line 15): the lease, the incidental costs and line 14.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/moving_lease_cancellation",
                "ca/moving_incidental_costs",
                "ca/moving_old_home_maintenance_checked",
            )
        },
        produces={"output": "ca/moving_lease_and_incidental_subtotal"},
    ),
    # T1-M Part 4 "Add lines 16 to 19." (line 20): the costs of selling the old home.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/moving_selling_commission",
                "ca/moving_selling_legal_fees",
                "ca/moving_selling_advertising",
                "ca/moving_selling_other_costs",
            )
        },
        produces={"output": "ca/moving_selling_subtotal"},
    ),
    # T1-M Part 4 "Line 21 plus line 22" (line 23): the costs of buying the new home.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/moving_buying_legal_fees", "ca/moving_buying_taxes")},
        produces={"output": "ca/moving_buying_subtotal"},
    ),
    # T1-M Part 4 "Add lines 4, 8, 11, 15, 20 and 23." (line 24) "Total moving expenses".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/moving_transportation_and_storage",
                "ca/moving_travel_expenses_subtotal",
                "ca/moving_temporary_living_subtotal",
                "ca/moving_lease_and_incidental_subtotal",
                "ca/moving_selling_subtotal",
                "ca/moving_buying_subtotal",
            )
        },
        produces={"output": "ca/moving_total_expenses"},
    ),
    # T1-M Part 4 "Line 24 minus line 25 (if negative, enter "0")" (line 26) "Net moving expenses".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/moving_total_expenses",
            "less": "ca/moving_reimbursement",
        },
        produces={"output": "ca/moving_net_expenses"},
    ),
    # T1-M Part 4 "Amount from line 26 of the previous page" (line 27).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/moving_net_expenses",)},
        produces={"output": "ca/moving_net_expenses_carried"},
    ),
    # Each self-employment line is the profit of its businesses on the return (Form T1139's summary
    # form): a loss counts 0, and amount G or L of a Form T1139 takes the place of its statements.
    # T1-M Part 4 line 28 "Net eligible income": "If you are an employee ... the amounts reported
    # on your T4 or T4A slips ... included on lines 10100 or 10400 ..." and "If you are
    # self-employed ... the net amounts earned at the new work location that are included on lines
    # 13500, 13700, 13900, 14100, and 14300" (Form T1-M, "Net eligible income"): the positive net
    # of each self-employment line over its statements, a loss counting 0 (not below zero).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_business_profit_on_return"},
        produces={"output": "ca/moving_business_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_professional_profit_on_return"},
        produces={"output": "ca/moving_professional_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_commission_profit_on_return"},
        produces={"output": "ca/moving_commission_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_farming_profit_on_return"},
        produces={"output": "ca/moving_farming_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_fishing_profit_on_return"},
        produces={"output": "ca/moving_fishing_income"},
    ),
    # T1-M Part 4 line 28 "Net eligible income": the income lines it is taken from, the employment
    # income (line 10100), the other employment income (line 10400), the taxable scholarships of a
    # student and the five self-employment amounts above, added in that order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/employment_income",
                "ca/other_employment_income",
                "ca/taxable_scholarships",
                "ca/moving_business_income",
                "ca/moving_professional_income",
                "ca/moving_commission_income",
                "ca/moving_farming_income",
                "ca/moving_fishing_income",
            )
        },
        produces={"output": "ca/moving_eligible_income_lines"},
    ),
    # T1-M Part 4 line 28 is at most those income lines: an amount above them is an input error, not
    # capped (`core/at_most`), and the checked amount is the one that lines 29 and 30 read.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/moving_net_eligible_income",
            "bound": "ca/moving_eligible_income_lines",
        },
        produces={"output": "ca/moving_net_eligible_income_checked"},
    ),
    # T1-M Part 4 "Enter whichever is less: amount from line 27 or line 28." (before line 29).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/moving_net_expenses_carried",
                "ca/moving_net_eligible_income_checked",
            )
        },
        produces={"output": "ca/moving_lesser_of_expenses_and_income"},
    ),
    # T1-M Part 2 "If the amount on line 3 is less than 40 kilometres, you cannot deduct your moving
    # expenses." The line 29 amount is claimed only when line 3 is at least the 40 kilometres of the
    # `ca/moving_distance_threshold` dataset, otherwise 0.
    CapabilitySelection(
        name="ca/threshold_gate",
        params={"threshold": "ca/moving_distance_threshold"},
        consumes={
            "amount": "ca/moving_lesser_of_expenses_and_income",
            "gate": "ca/moving_distance_difference",
        },
        produces={"output": "ca/moving_expenses_claim"},
    ),
    # T1-M Part 4 "Line 27 minus line 28 (if negative, enter "0")" (line 30) "Your unused moving
    # expenses available to carry forward to a future year".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/moving_net_expenses_carried",
            "less": "ca/moving_net_eligible_income_checked",
        },
        produces={"output": "ca/moving_unused_expenses_before_test"},
    ),
    # T1-M Part 2 "If the amount on line 3 is less than 40 kilometres, you cannot deduct your
    # moving expenses. If this is the case, do not complete the rest of this form." The line 30
    # amount "Your unused moving expenses available to carry forward to a future year" is kept only
    # when line 3 is at least the 40 kilometres of the `ca/moving_distance_threshold` dataset,
    # otherwise 0.
    CapabilitySelection(
        name="ca/threshold_gate",
        params={"threshold": "ca/moving_distance_threshold"},
        consumes={
            "amount": "ca/moving_unused_expenses_before_test",
            "gate": "ca/moving_distance_difference",
        },
        produces={"output": "ca/moving_unused_expenses"},
    ),
}

FORM_WIRING = {
    (
        Subtract,
        frozenset({MOVING_OLD_HOME_DISTANCE, MOVING_NEW_HOME_DISTANCE}),
        frozenset({MOVING_DISTANCE_DIFFERENCE}),
    ),
    (
        Sum,
        frozenset({MOVING_TRAVEL_EXPENSES, MOVING_ACCOMMODATION_EXPENSES, MOVING_MEAL_EXPENSES}),
        frozenset({MOVING_TRAVEL_EXPENSES_SUBTOTAL}),
    ),
    (
        Sum,
        frozenset({MOVING_TEMPORARY_LODGING, MOVING_TEMPORARY_MEALS}),
        frozenset({MOVING_TEMPORARY_LIVING_SUBTOTAL}),
    ),
    (CreditAmount, frozenset(), frozenset({MOVING_OLD_HOME_MAINTENANCE_CAP})),
    (
        AtMost,
        frozenset({MOVING_OLD_HOME_MAINTENANCE, MOVING_OLD_HOME_MAINTENANCE_CAP}),
        frozenset({MOVING_OLD_HOME_MAINTENANCE_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                MOVING_LEASE_CANCELLATION,
                MOVING_INCIDENTAL_COSTS,
                MOVING_OLD_HOME_MAINTENANCE_CHECKED,
            }
        ),
        frozenset({MOVING_LEASE_AND_INCIDENTAL_SUBTOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                MOVING_SELLING_COMMISSION,
                MOVING_SELLING_LEGAL_FEES,
                MOVING_SELLING_ADVERTISING,
                MOVING_SELLING_OTHER_COSTS,
            }
        ),
        frozenset({MOVING_SELLING_SUBTOTAL}),
    ),
    (
        Sum,
        frozenset({MOVING_BUYING_LEGAL_FEES, MOVING_BUYING_TAXES}),
        frozenset({MOVING_BUYING_SUBTOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                MOVING_TRANSPORTATION_AND_STORAGE,
                MOVING_TRAVEL_EXPENSES_SUBTOTAL,
                MOVING_TEMPORARY_LIVING_SUBTOTAL,
                MOVING_LEASE_AND_INCIDENTAL_SUBTOTAL,
                MOVING_SELLING_SUBTOTAL,
                MOVING_BUYING_SUBTOTAL,
            }
        ),
        frozenset({MOVING_TOTAL_EXPENSES}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({MOVING_TOTAL_EXPENSES, MOVING_REIMBURSEMENT}),
        frozenset({MOVING_NET_EXPENSES}),
    ),
    (
        Sum,
        frozenset({MOVING_NET_EXPENSES}),
        frozenset({MOVING_NET_EXPENSES_CARRIED}),
    ),
    (
        RecordTotal,
        frozenset({BUSINESS_PROFIT_ON_RETURN_LINES}),
        frozenset({MOVING_BUSINESS_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({PROFESSIONAL_PROFIT_ON_RETURN_LINES}),
        frozenset({MOVING_PROFESSIONAL_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({COMMISSION_PROFIT_ON_RETURN_LINES}),
        frozenset({MOVING_COMMISSION_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({FARMING_PROFIT_ON_RETURN_LINES}),
        frozenset({MOVING_FARMING_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({FISHING_PROFIT_ON_RETURN_LINES}),
        frozenset({MOVING_FISHING_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                EMPLOYMENT_INCOME,
                OTHER_EMPLOYMENT_INCOME,
                TAXABLE_SCHOLARSHIPS,
                MOVING_BUSINESS_INCOME,
                MOVING_PROFESSIONAL_INCOME,
                MOVING_COMMISSION_INCOME,
                MOVING_FARMING_INCOME,
                MOVING_FISHING_INCOME,
            }
        ),
        frozenset({MOVING_ELIGIBLE_INCOME_LINES}),
    ),
    (
        AtMost,
        frozenset({MOVING_NET_ELIGIBLE_INCOME, MOVING_ELIGIBLE_INCOME_LINES}),
        frozenset({MOVING_NET_ELIGIBLE_INCOME_CHECKED}),
    ),
    (
        LesserOf,
        frozenset({MOVING_NET_EXPENSES_CARRIED, MOVING_NET_ELIGIBLE_INCOME_CHECKED}),
        frozenset({MOVING_LESSER_OF_EXPENSES_AND_INCOME}),
    ),
    (
        ThresholdGate,
        frozenset({MOVING_LESSER_OF_EXPENSES_AND_INCOME, MOVING_DISTANCE_DIFFERENCE}),
        frozenset({MOVING_EXPENSES_CLAIM}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({MOVING_NET_EXPENSES_CARRIED, MOVING_NET_ELIGIBLE_INCOME_CHECKED}),
        frozenset({MOVING_UNUSED_EXPENSES_BEFORE_TEST}),
    ),
    (
        ThresholdGate,
        frozenset({MOVING_UNUSED_EXPENSES_BEFORE_TEST, MOVING_DISTANCE_DIFFERENCE}),
        frozenset({MOVING_UNUSED_EXPENSES}),
    ),
}

# The instances input: the moves of the return, one record for each (any number, none included).
INPUTS = frozenset({"ca/t1_m_moves"})

# The return declares no output: line 30 is an export that nothing on the return reads.
OUTPUTS: frozenset[str] = frozenset()

# Each move's line 29, "Enter this amount on line 21900 of your return", as the record list
# `ca/t1_m.moving_expenses_claim`, one record for each move.
MOVING_EXPENSES_CLAIM_PER_MOVE = RecordListKind(
    "ca/t1_m.moving_expenses_claim", fields=(MOVING_EXPENSES_CLAIM,)
)
MOVING_UNUSED_EXPENSES_PER_MOVE = RecordListKind(
    "ca/t1_m.moving_unused_expenses", fields=(MOVING_UNUSED_EXPENSES,)
)

# T1 line 21900 "Moving expenses (complete Form T1-M)": the line 29 amounts of all the moves added.
STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1_m.moving_expenses_claim"},
        produces={"output": "ca/moving_expenses_deduction"},
    ),
}

WIRING = {
    (
        RecordTotal,
        frozenset({MOVING_EXPENSES_CLAIM_PER_MOVE}),
        frozenset({MOVING_EXPENSES_DEDUCTION}),
    ),
}
