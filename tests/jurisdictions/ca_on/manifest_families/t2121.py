"""The CA-ON manifest entries of Form T2121 (see `test_manifest.py` and `test_manifest_t2121.py`).

T2121 is a form of the manifest: its 60 selections belong to the form `ca/t2121` (`FORM_STEPS`),
run once for each statement of `ca/t2121_statements`, whose fields are the T2121 inputs
(`FORM_INPUTS`). The form exports eleven artifacts, each readable by the other forms as
`ca/t2121.<export>` (`FORM_EXPORTS`); the return reads one and declares no output for the four
nothing reads (`OUTPUTS` is empty). The return's own entries are the instances input and the total
of the net income over the statements that is T1 line 14300 (`STEPS` and `WIRING`); the form selects
one step over the statement's vehicles, whose printed constants of Charts B and C are datasets.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_calculator.jurisdictions.ca.capabilities.business_vehicle_expenses import (
    BusinessVehicleExpenses,
)
from tax_calculator.jurisdictions.ca.capabilities.cca_claim_prorated import CcaClaimProrated
from tax_calculator.jurisdictions.ca.capabilities.cca_vehicle_additions_checks import (
    CcaVehicleAdditionsChecks,
)
from tax_calculator.jurisdictions.ca.capabilities.cca_vehicle_proceeds import CcaVehicleProceeds
from tax_calculator.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_calculator.jurisdictions.ca.capabilities.closing_ucc_prorated import ClosingUccProrated
from tax_calculator.jurisdictions.ca.capabilities.fiscal_period_days import FiscalPeriodDays
from tax_calculator.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_calculator.jurisdictions.ca.capabilities.prorated_by_fiscal_period_days import (
    ProratedByFiscalPeriodDays,
)
from tax_calculator.jurisdictions.ca.capabilities.recaptured_cca import RecapturedCca
from tax_calculator.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_VEHICLES,
    FISH_BOAT_MAINLY_PERSONAL,
    FISH_BOAT_MAINLY_PERSONAL_CHECKED,
    FISH_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,
    FISH_CAPITAL_CONTRIBUTIONS,
    FISH_CCA_CLAIM,
    FISH_CCA_CLAIM_LESS_PERSONAL_PART,
    FISH_CCA_CLASSES,
    FISH_CCA_CLASSES_ADJUSTED,
    FISH_CCA_CLASSES_CHECKED,
    FISH_CCA_PERSONAL_PART,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_COMPENSATION_FOR_LOSS,
    FISH_CREW_SHARES,
    FISH_DRAWINGS,
    FISH_EPOP_AGREEMENT_FILED,
    FISH_EPOP_AGREEMENT_FILED_CHECKED,
    FISH_EPOP_ASSOCIATED,
    FISH_EPOP_ASSOCIATED_CHECKED,
    FISH_EPOP_PERCENTAGE,
    FISH_EPOP_PERCENTAGE_MAXIMUM,
    FISH_EPOP_PERCENTAGE_ROOM,
    FISH_EPOP_PERCENTAGE_TOTAL,
    FISH_EXPENSES_LIMITED_TO_CATCH_INCOME,
    FISH_EXPENSES_SUBTOTAL,
    FISH_FISCAL_PERIOD_DAYS,
    FISH_FISCAL_PERIOD_DAYS_ENTERED,
    FISH_FISH_PRODUCTS,
    FISH_FISHING_GEAR,
    FISH_FUEL_COSTS,
    FISH_GRANTS_CREDITS_AND_REBATES,
    FISH_GROSS_INCOME,
    FISH_GROSS_INCOME_BEFORE_EXPENSES,
    FISH_HOME_ALLOWABLE_CLAIM,
    FISH_HOME_CARRIED_FORWARD,
    FISH_HOME_CARRY_FORWARD,
    FISH_HOME_CCA,
    FISH_HOME_ELECTRICITY,
    FISH_HOME_EXPENSES,
    FISH_HOME_EXPENSES_AVAILABLE,
    FISH_HOME_EXPENSES_BUSINESS_PART,
    FISH_HOME_EXPENSES_SUBTOTAL,
    FISH_HOME_HEAT,
    FISH_HOME_INCOME_LIMIT,
    FISH_HOME_INSURANCE,
    FISH_HOME_MAINTENANCE,
    FISH_HOME_MORTGAGE_INTEREST,
    FISH_HOME_OTHER_EXPENSES,
    FISH_HOME_PERSONAL_USE_PART,
    FISH_HOME_PROPERTY_TAXES,
    FISH_IMMEDIATE_EXPENSING_ALLOCATED,
    FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    FISH_IMMEDIATE_EXPENSING_CAP,
    FISH_IMMEDIATE_EXPENSING_CLAIM,
    FISH_IMMEDIATE_EXPENSING_LIMIT,
    FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    FISH_IMMEDIATE_EXPENSING_SHARE,
    FISH_INCOME_BEFORE_CCA,
    FISH_INSURANCE,
    FISH_INSURANCE_RECOVERY,
    FISH_INTEREST_AND_BANK_CHARGES,
    FISH_LAND_ADDITIONS,
    FISH_LAND_DISPOSITIONS,
    FISH_LIABILITIES,
    FISH_MEALS_AND_ENTERTAINMENT,
    FISH_MINISTER_ALLOCATION,
    FISH_MINISTER_ALLOCATION_GIVEN,
    FISH_MINISTER_ALLOCATION_GIVEN_CHECKED,
    FISH_MOTOR_VEHICLE_EXPENSES,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_NET_INCOME_BEFORE_BOAT_LIMIT,
    FISH_NETS_AND_TRAPS,
    FISH_OFFICE_EXPENSES,
    FISH_OTHER_EXPENSES,
    FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    FISH_OTHER_INCOME,
    FISH_OTHER_INCOME_WITH_RECAPTURE,
    FISH_OTHER_MARINE_PRODUCTS,
    FISH_PARTNER,
    FISH_PARTNER_CHECKED,
    FISH_PARTNER_GST_HST_REBATE,
    FISH_PARTNER_OTHER_AMOUNT_A,
    FISH_PARTNER_OTHER_AMOUNT_B,
    FISH_PARTNER_OTHER_AMOUNT_C,
    FISH_PARTNER_OTHER_AMOUNT_D,
    FISH_PARTNER_OTHER_AMOUNT_E,
    FISH_PARTNER_OTHER_AMOUNTS,
    FISH_PARTNER_OTHER_AMOUNTS_TOTAL,
    FISH_PARTNER_SHARE,
    FISH_PARTNERSHIP_TOTAL,
    FISH_PROFESSIONAL_FEES,
    FISH_RECAPTURED_CCA,
    FISH_REPAIRS_ELECTRICAL_EQUIPMENT,
    FISH_REPAIRS_ENGINE,
    FISH_REPAIRS_FISHING_BOAT,
    FISH_REPAIRS_TOTAL,
    FISH_REPAIRS_YOUR_COST,
    FISH_SALARIES_WAGES_AND_BENEFITS,
    FISH_SALT_BAIT_AND_ICE,
    FISH_SHARE_OF_NET_INCOME,
    FISH_SHARESPERSON_INCOME,
    FISH_SUBSIDIES,
    FISH_TERMINAL_LOSS,
    FISH_TOTAL_EXPENSES,
    FISH_TOTAL_EXPENSES_DEDUCTIBLE,
    FISH_VEHICLE_SALES_TAX_RATE,
    FISHING_INCOME,
    IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
)
from tests.jurisdictions.ca_on.manifest_families.t1139 import FISHING_INCOME_ON_RETURN_LINES

NET_INCOME_PER_STATEMENT = RecordListKind("ca/t2121.fishing_income", fields=(FISHING_INCOME,))
FISH_CLOSING_UCC_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_closing_ucc", fields=(FISH_CLOSING_UCC,)
)
FISH_HOME_CARRY_FORWARD_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_home_carry_forward", fields=(FISH_HOME_CARRY_FORWARD,)
)
FISH_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_immediate_expensing_claim", fields=(FISH_IMMEDIATE_EXPENSING_CLAIM,)
)
FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_immediate_expensing_limit_unprorated",
    fields=(FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,),
)
FISH_LAND_ADDITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_land_additions", fields=(FISH_LAND_ADDITIONS,)
)
FISH_LAND_DISPOSITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_land_dispositions", fields=(FISH_LAND_DISPOSITIONS,)
)
FISH_LIABILITIES_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_liabilities", fields=(FISH_LIABILITIES,)
)
FISH_DRAWINGS_PER_STATEMENT = RecordListKind("ca/t2121.fish_drawings", fields=(FISH_DRAWINGS,))
FISH_CAPITAL_CONTRIBUTIONS_PER_STATEMENT = RecordListKind(
    "ca/t2121.fish_capital_contributions", fields=(FISH_CAPITAL_CONTRIBUTIONS,)
)

FORM_INPUTS = frozenset(
    {
        "ca/fish_fish_products",
        "ca/fish_other_marine_products",
        "ca/fish_grants_credits_and_rebates",
        "ca/fish_subsidies",
        "ca/fish_compensation_for_loss",
        "ca/fish_sharesperson_income",
        "ca/fish_other_income",
        "ca/fish_salt_bait_and_ice",
        "ca/fish_crew_shares",
        "ca/fish_fuel_costs",
        "ca/fish_fishing_gear",
        "ca/fish_insurance",
        "ca/fish_interest_and_bank_charges",
        "ca/fish_meals_and_entertainment",
        "ca/fish_business_taxes_licences_and_memberships",
        "ca/business_vehicles",
        "ca/fish_vehicle_sales_tax_rate",
        "ca/fish_office_expenses",
        "ca/fish_nets_and_traps",
        "ca/fish_professional_fees",
        "ca/fish_salaries_wages_and_benefits",
        "ca/fish_repairs_fishing_boat",
        "ca/fish_repairs_engine",
        "ca/fish_repairs_electrical_equipment",
        "ca/fish_insurance_recovery",
        "ca/fish_other_expenses",
        "ca/fish_cca_personal_part",
        "ca/fish_cca_classes",
        "ca/fish_partner",
        "ca/fish_partner_share",
        "ca/fish_partner_gst_hst_rebate",
        "ca/fish_partner_other_amount_a",
        "ca/fish_partner_other_amount_b",
        "ca/fish_partner_other_amount_c",
        "ca/fish_partner_other_amount_d",
        "ca/fish_partner_other_amount_e",
        "ca/fish_home_heat",
        "ca/fish_home_electricity",
        "ca/fish_home_insurance",
        "ca/fish_home_maintenance",
        "ca/fish_home_mortgage_interest",
        "ca/fish_home_property_taxes",
        "ca/fish_home_other_expenses",
        "ca/fish_home_personal_use_part",
        "ca/fish_home_cca",
        "ca/fish_home_carried_forward",
        "ca/fish_epop_associated",
        "ca/fish_epop_agreement_filed",
        "ca/fish_epop_percentage",
        "ca/fish_epop_percentage_total",
        "ca/fish_minister_allocation_given",
        "ca/fish_minister_allocation",
        "ca/fish_fiscal_period_days_entered",
        "ca/fish_land_additions",
        "ca/fish_land_dispositions",
        "ca/fish_liabilities",
        "ca/fish_drawings",
        "ca/fish_capital_contributions",
        "ca/fish_boat_mainly_personal",
    }
)

FORM_STEPS = {
    # T2121 Area A endnote 2 "The proceeds of disposition of a zero-emission passenger vehicle
    # (ZEPV) that has been included in Class 54, or a passenger vehicle bought after April 18, 2021,
    # that has been included in Class 10.1, and whose cost is more than the prescribed amount will
    # be adjusted based on a factor equal to its prescribed amount as a proportion of the actual
    # cost of the vehicle.": the Area A list with columns 5 and 6 of each such row scaled, which
    # the steps below read in place of the caller's list.
    # Guide T4036 2025, "Class 54 (30%)": "If a zero-emission passenger vehicle is disposed of to a
    # person or partnership with whom you deal at arm's length, and its cost exceeds the prescribed
    # amount ($55,000 for vehicles acquired after March 18, 2019, and before January 1, 2022;
    # $59,000 for vehicles acquired after December 31, 2021, and before January 1, 2023; or $61,000
    # for vehicles acquired after December 31, 2022), the proceeds of disposition will be adjusted
    # based on a factor equal to the prescribed amount as a proportion of the actual cost of the
    # vehicle.": each vehicle sold from a Class 54 row is scaled with the dataset of those amounts.
    CapabilitySelection(
        name="ca/cca_vehicle_additions_checks",
        params={"prescribed_amounts": "ca/cca_vehicle_prescribed_amounts"},
        consumes={
            "classes": "ca/fish_cca_classes",
            "sales_tax_rate": "ca/fish_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/fish_cca_classes_checked"},
    ),
    CapabilitySelection(
        name="ca/cca_vehicle_proceeds",
        params={
            "prescribed_amounts": "ca/cca_vehicle_prescribed_amounts",
            "zepv_prescribed_amounts": "ca/cca_zepv_prescribed_amounts",
        },
        consumes={
            "classes": "ca/fish_cca_classes_checked",
            "sales_tax_rate": "ca/fish_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/fish_cca_classes_adjusted"},
    ),
    # T2121 Area A endnote 3 "If you have a negative amount in column 7, add it to income as a
    # recapture in Part 3 on line 9600. If no property is left in the class and there is a positive
    # amount in this column, deduct the amount from income as a terminal loss in Part 4 on line
    # 9270.": the recapture of each class of the Area A list (column 7 made positive when negative),
    # totalled.
    CapabilitySelection(
        name="ca/recaptured_cca",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"classes": "ca/fish_cca_classes_adjusted"},
        produces={"output": "ca/fish_recaptured_cca"},
    ),
    # T2121 Part 3 line 9600 "Other income (specify):", which takes the recapture of Area A (the
    # Area A endnote "add it to income as a recapture in Part 3 on line 9600"): the other income
    # the caller specifies plus the recapture.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fish_other_income", "ca/fish_recaptured_cca")},
        produces={"output": "ca/fish_other_income_with_recapture"},
    ),
    # T2121 Part 3 "Gross income: Total of amounts 3A to 3F and line 9600 (enter this amount on line
    # 14299 of your income tax and benefit return)" (line 8299): the caller's amounts 3A to 3F in
    # the form's order, and line 9600 with its recapture.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fish_fish_products",
                "ca/fish_other_marine_products",
                "ca/fish_grants_credits_and_rebates",
                "ca/fish_subsidies",
                "ca/fish_compensation_for_loss",
                "ca/fish_sharesperson_income",
                "ca/fish_other_income_with_recapture",
            )
        },
        produces={"output": "ca/fish_gross_income"},
    ),
    # T2121 Part 4 "Gross income (line 8299 of Part 3)" (4A): line 8299 alone, the gross income that
    # the expenses are taken from.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fish_gross_income",)},
        produces={"output": "ca/fish_gross_income_before_expenses"},
    ),
    # T2121 Area A endnote 3 "deduct the amount from income as a terminal loss in Part 4 on line
    # 9270": the terminal loss of each class of the Area A list, totalled.
    CapabilitySelection(
        name="ca/terminal_loss",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"classes": "ca/fish_cca_classes_adjusted"},
        produces={"output": "ca/fish_terminal_loss"},
    ),
    # T2121 Part 4 "Other expenses (specify): 9270 4P": the other expenses the caller specifies plus
    # the terminal loss.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fish_other_expenses", "ca/fish_terminal_loss")},
        produces={"output": "ca/fish_other_expenses_with_terminal_loss"},
    ),
    # T2121 Part 4 "Repairs and maintenance: Fishing boat", "Engine", "Electrical equipment"
    # (amounts 1 to 3) and "Total of amounts 1 to 3" (amount 4): the three caller amounts added.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fish_repairs_fishing_boat",
                "ca/fish_repairs_engine",
                "ca/fish_repairs_electrical_equipment",
            )
        },
        produces={"output": "ca/fish_repairs_total"},
    ),
    # T2121 Part 4 "Your cost (amount 4 minus amount 5)" (line 8963, 4O): amount 4 less the
    # insurance recovery, amount 5.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_repairs_total",
            "less": "ca/fish_insurance_recovery",
        },
        produces={"output": "ca/fish_repairs_your_cost"},
    ),
    # T2042 Charts A to C, "Motor vehicle expenses", filled in for each vehicle of the statement's
    # list and added: Chart A line 16 "Allowable motor vehicle expenses: Add amounts 13 to 15 (enter
    # this total on line 9819 of Part 4)". The printed constants ("$350***", "÷ 30", "$44,706",
    # "$1,100", "$38,000" and the 85%) and the rounding are the datasets that T2125 uses, and the
    # sales tax rate of the province is the statement's one input.
    CapabilitySelection(
        name="ca/business_vehicle_expenses",
        params={
            "interest_limits": "ca/business_vehicle_interest_limits",
            "lease_limits": "ca/business_vehicle_lease_limits",
            "days_divisor": "ca/business_vehicle_days_divisor",
            "lease_price_rate": "ca/business_vehicle_lease_price_rate",
            "deposit_minimum": "ca/business_vehicle_deposit_minimum",
            "rounding": "ca/business_vehicle_rounding",
        },
        consumes={
            "vehicles": "ca/business_vehicles",
            "sales_tax_rate": "ca/fish_vehicle_sales_tax_rate",
            "fiscal_period_days": "ca/fish_fiscal_period_days",
        },
        produces={"output": "ca/fish_motor_vehicle_expenses"},
    ),
    # T2121 Part 4 "Subtotal: Add amounts 4B to 4P." (4Q): the expense lines 4B to 4N, amount 4O and
    # the other expenses of line 9270 with the terminal loss.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fish_salt_bait_and_ice",
                "ca/fish_crew_shares",
                "ca/fish_fuel_costs",
                "ca/fish_fishing_gear",
                "ca/fish_insurance",
                "ca/fish_interest_and_bank_charges",
                "ca/fish_meals_and_entertainment",
                "ca/fish_business_taxes_licences_and_memberships",
                "ca/fish_motor_vehicle_expenses",
                "ca/fish_office_expenses",
                "ca/fish_nets_and_traps",
                "ca/fish_professional_fees",
                "ca/fish_salaries_wages_and_benefits",
                "ca/fish_repairs_your_cost",
                "ca/fish_other_expenses_with_terminal_loss",
            )
        },
        produces={"output": "ca/fish_expenses_subtotal"},
    ),
    # T2121 Area A, the days of the fiscal period (Guide T4002 "You were asking?": "Since your
    # fiscal period is less than 365 days, you have to prorate your CCA claim. ... base your CCA
    # claim on the number of days in your fiscal period compared to 365 days. In this case, your
    # fiscal period is 214 days."): the days the caller enters, or the 365 of a full year when none
    # are.
    CapabilitySelection(
        name="ca/fiscal_period_days",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"entered": "ca/fish_fiscal_period_days_entered"},
        produces={"output": "ca/fish_fiscal_period_days"},
    ),
    # T2121 Area A "Total CCA claim for the year: Total of column 21 (enter on line 9936 of Part 4
    # amount ii minus any personal part and any CCA for business-use-of-home expenses)" (amount ii):
    # the CCA claimed on each class of the Area A list, at most its maximum, totalled.
    CapabilitySelection(
        name="ca/cca_claim_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/fish_cca_classes_adjusted",
            "fiscal_period_days": "ca/fish_fiscal_period_days",
        },
        produces={"output": "ca/fish_cca_table_claim"},
    ),
    # T2121 Part 4 "Capital cost allowance (CCA). Enter amount ii of Area A minus any personal part
    # and any CCA for business-use-of-home expenses." (line 9936), first step: amount ii minus the
    # personal part of CCA, a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/fish_cca_table_claim", "less": "ca/fish_cca_personal_part"},
        produces={"output": "ca/fish_cca_claim_less_personal_part"},
    ),
    # T2121 Part 4 line 9936, second step: that result minus the CCA for business-use-of-home
    # expenses, amount 7K "Capital cost allowance (business part only), which means amount ii of
    # Area A minus any portion of capital cost allowance that is for personal use or entered on
    # line 9936 of Part 4", a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_cca_claim_less_personal_part",
            "less": "ca/fish_home_cca",
        },
        produces={"output": "ca/fish_cca_claim"},
    ),
    # T2121 Part 4 "Total expenses: Amount 4Q plus line 9936" (line 9368): the two added.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fish_expenses_subtotal", "ca/fish_cca_claim")},
        produces={"output": "ca/fish_total_expenses"},
    ),
    # T2121 Part 4 "Net income (loss) before adjustments: Amount 4A minus line 9368" before the
    # limit of the boat mainly for personal use: signed; the immediate expensing check reads it, as
    # its income is "before any CCA deductions".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_gross_income_before_expenses",
            "less": "ca/fish_total_expenses",
        },
        produces={"output": "ca/fish_net_income_before_boat_limit"},
    ),
    # Guide T4002 2025 (page 51), "Use of a fishing boat mainly for personal use": "You may have
    # used a fishing boat mainly for personal use, but sometimes caught a small amount of fish to
    # sell. In this case, you can deduct expenses and CCA. However, the amount you deduct cannot be
    # more than your income from the catch." The answer (0 or 1) is checked as a yes or no.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/fish_boat_mainly_personal"},
        produces={"output": "ca/fish_boat_mainly_personal_checked"},
    ),
    # The amount deducted cannot be more than the income from the catch: the lesser of line 9368
    # (the expenses and the CCA) and the gross income of Part 3 (line 8299, amount 4A).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/fish_total_expenses", "ca/fish_gross_income_before_expenses")},
        produces={"output": "ca/fish_expenses_limited_to_catch_income"},
    ),
    # With an answer of 1 the deductible total is that lesser amount, otherwise line 9368.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/fish_boat_mainly_personal_checked",
            "when_none": "ca/fish_total_expenses",
            "when_any": "ca/fish_expenses_limited_to_catch_income",
        },
        produces={"output": "ca/fish_total_expenses_deductible"},
    ),
    # T2121 Part 4 "Net income (loss) before adjustments: Amount 4A minus line 9368" (line 9369):
    # signed, a loss is negative; line 9368 is the deductible total (the guide's limit above).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_gross_income_before_expenses",
            "less": "ca/fish_total_expenses_deductible",
        },
        produces={"output": "ca/fish_net_income_before_adjustments"},
    ),
    # T2121 Part 5 "Your share of line 9369 or the amount from your T5013 slip, Statement of
    # Partnership Income" (5A): a count of 1 for a partner chooses the amount from the T5013 slip,
    # as entered; with a count of 0 it is line 9369.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/fish_partner_checked",
            "when_none": "ca/fish_net_income_before_adjustments",
            "when_any": "ca/fish_partner_share",
        },
        produces={"output": "ca/fish_share_of_net_income"},
    ),
    # T2121 Part 5 "Total: Amount 5A plus line 9974" (5B): amount 5A and line 9974 "GST/HST rebate
    # for partners received in the year", a caller input.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fish_share_of_net_income",
                "ca/fish_partner_gst_hst_rebate",
            )
        },
        produces={"output": "ca/fish_partnership_total"},
    ),
    # T2121 Part 6 "Total other amounts deductible from your share of the net partnership income
    # (loss): Add amounts 6A to 6E (enter this amount on line 9943 of Part 5)." (6F): 6A to 6E,
    # caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fish_partner_other_amount_a",
                "ca/fish_partner_other_amount_b",
                "ca/fish_partner_other_amount_c",
                "ca/fish_partner_other_amount_d",
                "ca/fish_partner_other_amount_e",
            )
        },
        produces={"output": "ca/fish_partner_other_amounts_total"},
    ),
    # T2121 Part 5 "Other amounts deductible from your share of net partnership income (loss)
    # (amount 6F)" (line 9943).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fish_partner_other_amounts_total",)},
        produces={"output": "ca/fish_partner_other_amounts"},
    ),
    # T2121 Part 5 "Net income (loss) after adjustments: Amount 5B minus line 9943" (5C): signed, a
    # loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_partnership_total",
            "less": "ca/fish_partner_other_amounts",
        },
        produces={"output": "ca/fish_net_income_after_adjustments"},
    ),
    # T2121 Part 7 "Subtotal: Add amounts 7A to 7G." (7H): 7A "Heat", 7B "Electricity", 7C
    # "Insurance", 7D "Maintenance", 7E "Mortgage interest", 7F "Property taxes" and 7G "Other
    # expenses (specify)", caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fish_home_heat",
                "ca/fish_home_electricity",
                "ca/fish_home_insurance",
                "ca/fish_home_maintenance",
                "ca/fish_home_mortgage_interest",
                "ca/fish_home_property_taxes",
                "ca/fish_home_other_expenses",
            )
        },
        produces={"output": "ca/fish_home_expenses_subtotal"},
    ),
    # T2121 Part 7 "Subtotal: Amount 7H minus amount 7I" (7J): amount 7I "Personal-use part of the
    # business-use-of-home expenses", a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_home_expenses_subtotal",
            "less": "ca/fish_home_personal_use_part",
        },
        produces={"output": "ca/fish_home_expenses_business_part"},
    ),
    # T2121 Part 7 "Subtotal: Add amounts 7J to 7L." (7M): 7J, amount 7K (the CCA for the business
    # part, a caller input) and 7L "Amount carried forward from previous year", a caller input.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fish_home_expenses_business_part",
                "ca/fish_home_cca",
                "ca/fish_home_carried_forward",
            )
        },
        produces={"output": "ca/fish_home_expenses_available"},
    ),
    # T2121 Part 7 "Net income (loss) after adjustments (amount 5C) (if negative, enter "0")." (7N):
    # amount 5C, or 0 when it is negative.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/fish_net_income_after_adjustments",)},
        produces={"output": "ca/fish_home_income_limit"},
    ),
    # T2121 Part 7 "Business-use-of-home expenses available to carry forward: Amount 7M minus amount
    # 7N (if negative, enter "0")" (7O): the claim left over, 0 when amount 7N is the larger.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fish_home_expenses_available",
            "less": "ca/fish_home_income_limit",
        },
        produces={"output": "ca/fish_home_carry_forward"},
    ),
    # T2121 Part 7 "Allowable claim: Amount 7M or 7N above, whichever is less (enter your share of
    # this amount on line 9945 of Part 5)" (7P).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/fish_home_expenses_available", "ca/fish_home_income_limit"),
        },
        produces={"output": "ca/fish_home_allowable_claim"},
    ),
    # T2121 Part 5 "Business-use-of-home expenses (amount 7P)" (line 9945).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fish_home_allowable_claim",)},
        produces={"output": "ca/fish_home_expenses"},
    ),
    # T2121 Part 5 "Your net income (loss): Amount 5C minus line 9945 (enter this amount on line
    # 14300 of your income tax and benefit return)" (line 9946): T1 "Line 26: Fishing income" and
    # "Line 14300: Net" are the same artifact, signed: a loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_net_income_after_adjustments",
            "less": "ca/fish_home_expenses",
        },
        produces={"output": "ca/fishing_income"},
    ),
    # T2121 Area A column 22 "UCC at the end of the year (col. 7 minus col. 21)": the class number
    # and column 22 of each class of the Area A list, a product of the return for next year's column
    # 1.
    CapabilitySelection(
        name="ca/closing_ucc_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/fish_cca_classes_adjusted",
            "fiscal_period_days": "ca/fish_fiscal_period_days",
        },
        produces={"output": "ca/fish_closing_ucc"},
    ),
    # T2121 Area G (page 6) "Immediate expensing limit allocated to your business: Multiply $1.5
    # million by the percentage assigned to your business in column 3**" (amount iii) and Area A
    # endnote 5 (page 7) "$1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year": the printed $1.5 million, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fish_immediate_expensing_cap"},
        consumes={},
        produces={"output": "ca/fish_immediate_expensing_cap"},
    ),
    # Income Tax Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation
    # year that is less than 51 weeks": the 51 weeks, printed as 51 weeks of 7 days, 357 days, one
    # figure for each form, read by the prorating step.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/immediate_expensing_short_year_days"},
        consumes={},
        produces={"output": "ca/immediate_expensing_short_year_days"},
    ),
    # T2121 Area G (page 6) "The total of all percentages assigned under the agreement should not be
    # more than 100%. If the total is more than 100%, then the associated group has an immediate
    # expensing limit of zero." and "** If the total of column 3 is more than 100%, enter "0."": the
    # printed 100%, a dataset, as the form prints a percentage (100 for 100%).
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fish_epop_percentage_maximum"},
        consumes={},
        produces={"output": "ca/fish_epop_percentage_maximum"},
    ),
    # T2121 Area G (page 6) "Immediate expensing limit allocated to your business: Multiply $1.5
    # million by the percentage assigned to your business in column 3**" (amount iii), first step:
    # $1.5 million times the percentage assigned to your business in column 3, a caller input as the
    # form prints it (40 for 40%).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/fish_immediate_expensing_rounding"},
        consumes={
            "amount": "ca/fish_immediate_expensing_cap",
            "percentage": "ca/fish_epop_percentage",
        },
        produces={"output": "ca/fish_immediate_expensing_share"},
    ),
    # T2121 Area G (page 6) "** If the total of column 3 is more than 100%, enter "0."", first step:
    # 100% less "Total of percentage assigned: Total of column 3", a caller input; negative when the
    # total is more than 100%.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fish_epop_percentage_maximum",
            "less": "ca/fish_epop_percentage_total",
        },
        produces={"output": "ca/fish_epop_percentage_room"},
    ),
    # T2121 Area G (page 6) "Immediate expensing limit allocated to your business" (amount iii) and
    # "** If the total of column 3 is more than 100%, enter "0."": the multiple above when 100% less
    # the total of column 3 is zero or positive, else 0.
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/fish_epop_percentage_room",
            "when_positive": (),
            "when_zero": (),
            "when_negative": (),
            "when_non_positive": (),
            "when_non_negative": ("ca/fish_immediate_expensing_share",),
        },
        produces={"output": "ca/fish_immediate_expensing_allocated"},
    ),
    # T2121 Area A endnote 5 (page 7) "amount iii of Area G, if you are associated with one or more
    # EPOPs in the tax year" and "zero, if you are associated with one or more EPOPs and an
    # agreement that assigns a percentage to one or more of the associated EPOPs was not filed with
    # the minister in a prescribed form": amount iii times the count of agreements filed (a caller's
    # 0 or 1), so 0 when none was filed.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/fish_immediate_expensing_allocated",
            "count": "ca/fish_epop_agreement_filed_checked",
        },
        produces={"output": "ca/fish_immediate_expensing_associated_limit"},
    ),
    # T2121 Area A endnote 5 (page 7) "the immediate expensing limit, which is equal to one of the
    # following, whichever is applicable": a count of 1 for associated with one or more EPOPs (a
    # caller's 0 or 1) chooses the limit above ("amount iii of Area G" or "zero"); with a count of 0
    # it is the $1.5 million ("if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year").
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/fish_epop_associated_checked",
            "when_none": "ca/fish_immediate_expensing_cap",
            "when_any": "ca/fish_immediate_expensing_associated_limit",
        },
        produces={"output": "ca/fish_immediate_expensing_limit_before_minister"},
    ),
    # T2121 Note 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": a count of 1 (a caller's 0 or 1) chooses the amount allocated by the minister,
    # as entered, in place of the limit before the days scaling; with a count of 0 the limit before
    # the minister's amount stands. The amount allocated is the amount for the year, and the days
    # scaling below applies to it as it does to the limit.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/fish_minister_allocation_given_checked",
            "when_none": "ca/fish_immediate_expensing_limit_before_minister",
            "when_any": "ca/fish_minister_allocation",
        },
        produces={"output": "ca/fish_immediate_expensing_limit_before_proration"},
    ),
    # Income Tax Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation
    # year that is less than 51 weeks, its immediate expensing limit for the year is that proportion
    # of its immediate expensing limit for the year determined without reference to this paragraph
    # that the number of days in the year is of 365". The limit before the days scaling (the
    # minister's amount included) times the days of the fiscal period over the 365 of a full year,
    # rounded to the cent, for a fiscal period of fewer than 357 days (51 weeks of 7 days, the
    # shared figure `ca/immediate_expensing_short_year_days`); any other fiscal period keeps the
    # amount as it is. Guide T4002, "Immediate expensing incentive": "The limit is also prorated for
    # tax years shorter than 365 days" is the guide's wording of the same rule, which the
    # Regulations narrow to 51 weeks.
    CapabilitySelection(
        name="ca/prorated_by_fiscal_period_days",
        params={
            "rounding": "ca/fish_immediate_expensing_rounding",
            "class_rates": "ca/cca_class_rates",
        },
        consumes={
            "amount": "ca/fish_immediate_expensing_limit_before_proration",
            "fiscal_period_days": "ca/fish_fiscal_period_days",
            "short_year_days": "ca/immediate_expensing_short_year_days",
        },
        produces={"output": "ca/fish_immediate_expensing_limit"},
    ),
    # T2121 Area A endnote 5 "the immediate expensing limit, which is equal to one of the
    # following, whichever is applicable", "any amount allocated by the minister under subsection
    # 1104(3.4) of the Regulations", and Guide T4002: "The limit is also prorated for tax years
    # shorter than 365 days". The person's limit before the days scaling, the one limit the
    # statements of the four forms share: the limit before the minister's amount, unscaled, or the
    # amount allocated by the minister when there is one, which is already unscaled. The
    # statements are compared on it because each statement's own fiscal period scales the limit
    # above, and a person's statements may cover periods of different lengths.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/fish_minister_allocation_given_checked",
            "when_none": "ca/fish_immediate_expensing_limit_before_minister",
            "when_any": "ca/fish_minister_allocation",
        },
        produces={"output": "ca/fish_immediate_expensing_limit_unprorated"},
    ),
    # T2121 Area A endnote 5 (page 7) "the amount of income, if any, earned from the source of
    # income that is a business (before any CCA deductions) in which the relevant DIEP is used for
    # the tax year": line 9369 "Net income (loss) before adjustments" plus line 9936, the CCA it
    # deducted (page 2), not below zero. Guide T4002 (page 61) names line 9369 as "Net income (loss)
    # before adjustments" for this form. The recapture on line 9600 is already in gross income and
    # the terminal loss on line 9270 an expense.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/fish_net_income_before_boat_limit",
                "ca/fish_cca_claim",
            ),
        },
        produces={"output": "ca/fish_income_before_cca"},
    ),
    # T2121 Area A (page 4) "Total immediate expensing claim for the year: Total of column 9" (line
    # i) and endnote 5 (page 7) "The total immediate expensing amount for the tax year (total of
    # column 9) is limited to the lesser of: the immediate expensing limit"; "the UCC of DIEPs in
    # column 8"; "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": the total of
    # column 9 of the Area A list, refused when above the limit or above the income before CCA.
    CapabilitySelection(
        name="ca/immediate_expensing_claim",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/fish_cca_classes_adjusted",
            "immediate_expensing_limit": "ca/fish_immediate_expensing_limit",
            "income_before_cca": "ca/fish_income_before_cca",
        },
        produces={"output": "ca/fish_immediate_expensing_claim"},
    ),
    # Area A endnote 5 answers, taken as a count of 0 or 1: each is checked to be 0 or 1 before
    # the step that reads it. A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/fish_epop_associated"},
        produces={"output": "ca/fish_epop_associated_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/fish_epop_agreement_filed"},
        produces={"output": "ca/fish_epop_agreement_filed_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/fish_minister_allocation_given"},
        produces={"output": "ca/fish_minister_allocation_given_checked"},
    ),
    # Fish partner answer, checked to be 0 or 1 before the step that reads it (in the part
    # `03n_t2121_checks.yaml`). A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/fish_partner"},
        produces={"output": "ca/fish_partner_checked"},
    ),
}

INPUTS = frozenset({"ca/t2121_statements"})

FORM_EXPORTS = (
    "ca/fishing_income",
    "ca/fish_closing_ucc",
    "ca/fish_home_carry_forward",
    "ca/fish_immediate_expensing_claim",
    "ca/fish_immediate_expensing_limit_unprorated",
    "ca/fish_land_additions",
    "ca/fish_land_dispositions",
    "ca/fish_liabilities",
    "ca/fish_drawings",
    "ca/fish_capital_contributions",
)

# The form exports Area A column 22 "UCC at the end of the year" (for next year), Part 7 line 7O
# "Business-use-of-home expenses available to carry forward" and Area A line i "Total immediate
# expensing claim for the year", and Area F lines 9923 "Total cost of all land additions in the
# year" and 9924 "Total proceeds from all land dispositions in the year", which are taken as
# entered and printed: none of them is read by a line of the return, so the return declares no
# output for them (an export nobody reads is fine). The Part 9 "Details of equity" lines 9931
# "Total business liabilities", 9932 "Drawings in the current year" and 9933 "Capital contributions
# in the current year" are taken as entered and printed, so the return declares no output for them.
OUTPUTS: frozenset[str] = frozenset()

# T1 line 14300 "Net": the total of T2121 line 9946 over the statements.
STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_fishing_income_on_return"},
        produces={"output": "ca/fishing_income"},
    ),
}

FORM_WIRING = {
    (
        CcaVehicleAdditionsChecks,
        frozenset({FISH_CCA_CLASSES, FISH_VEHICLE_SALES_TAX_RATE}),
        frozenset({FISH_CCA_CLASSES_CHECKED}),
    ),
    (
        CcaVehicleProceeds,
        frozenset({FISH_CCA_CLASSES_CHECKED, FISH_VEHICLE_SALES_TAX_RATE}),
        frozenset({FISH_CCA_CLASSES_ADJUSTED}),
    ),
    (RecapturedCca, frozenset({FISH_CCA_CLASSES_ADJUSTED}), frozenset({FISH_RECAPTURED_CCA})),
    (
        Sum,
        frozenset({FISH_OTHER_INCOME, FISH_RECAPTURED_CCA}),
        frozenset({FISH_OTHER_INCOME_WITH_RECAPTURE}),
    ),
    (
        Sum,
        frozenset(
            {
                FISH_FISH_PRODUCTS,
                FISH_OTHER_MARINE_PRODUCTS,
                FISH_GRANTS_CREDITS_AND_REBATES,
                FISH_SUBSIDIES,
                FISH_COMPENSATION_FOR_LOSS,
                FISH_SHARESPERSON_INCOME,
                FISH_OTHER_INCOME_WITH_RECAPTURE,
            }
        ),
        frozenset({FISH_GROSS_INCOME}),
    ),
    (Sum, frozenset({FISH_GROSS_INCOME}), frozenset({FISH_GROSS_INCOME_BEFORE_EXPENSES})),
    (TerminalLoss, frozenset({FISH_CCA_CLASSES_ADJUSTED}), frozenset({FISH_TERMINAL_LOSS})),
    (
        Sum,
        frozenset({FISH_OTHER_EXPENSES, FISH_TERMINAL_LOSS}),
        frozenset({FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS}),
    ),
    (
        Sum,
        frozenset(
            {
                FISH_REPAIRS_FISHING_BOAT,
                FISH_REPAIRS_ENGINE,
                FISH_REPAIRS_ELECTRICAL_EQUIPMENT,
            }
        ),
        frozenset({FISH_REPAIRS_TOTAL}),
    ),
    (
        Subtract,
        frozenset({FISH_REPAIRS_TOTAL, FISH_INSURANCE_RECOVERY}),
        frozenset({FISH_REPAIRS_YOUR_COST}),
    ),
    (
        Sum,
        frozenset(
            {
                FISH_SALT_BAIT_AND_ICE,
                FISH_CREW_SHARES,
                FISH_FUEL_COSTS,
                FISH_FISHING_GEAR,
                FISH_INSURANCE,
                FISH_INTEREST_AND_BANK_CHARGES,
                FISH_MEALS_AND_ENTERTAINMENT,
                FISH_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,
                FISH_MOTOR_VEHICLE_EXPENSES,
                FISH_OFFICE_EXPENSES,
                FISH_NETS_AND_TRAPS,
                FISH_PROFESSIONAL_FEES,
                FISH_SALARIES_WAGES_AND_BENEFITS,
                FISH_REPAIRS_YOUR_COST,
                FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
            }
        ),
        frozenset({FISH_EXPENSES_SUBTOTAL}),
    ),
    (
        FiscalPeriodDays,
        frozenset({FISH_FISCAL_PERIOD_DAYS_ENTERED}),
        frozenset({FISH_FISCAL_PERIOD_DAYS}),
    ),
    (
        CcaClaimProrated,
        frozenset({FISH_CCA_CLASSES_ADJUSTED, FISH_FISCAL_PERIOD_DAYS}),
        frozenset({FISH_CCA_TABLE_CLAIM}),
    ),
    (
        Subtract,
        frozenset({FISH_CCA_PERSONAL_PART, FISH_CCA_TABLE_CLAIM}),
        frozenset({FISH_CCA_CLAIM_LESS_PERSONAL_PART}),
    ),
    (
        Subtract,
        frozenset({FISH_CCA_CLAIM_LESS_PERSONAL_PART, FISH_HOME_CCA}),
        frozenset({FISH_CCA_CLAIM}),
    ),
    (Sum, frozenset({FISH_CCA_CLAIM, FISH_EXPENSES_SUBTOTAL}), frozenset({FISH_TOTAL_EXPENSES})),
    (
        YesOrNoCount,
        frozenset({FISH_BOAT_MAINLY_PERSONAL}),
        frozenset({FISH_BOAT_MAINLY_PERSONAL_CHECKED}),
    ),
    (
        LesserOf,
        frozenset({FISH_TOTAL_EXPENSES, FISH_GROSS_INCOME_BEFORE_EXPENSES}),
        frozenset({FISH_EXPENSES_LIMITED_TO_CATCH_INCOME}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FISH_BOAT_MAINLY_PERSONAL_CHECKED,
                FISH_TOTAL_EXPENSES,
                FISH_EXPENSES_LIMITED_TO_CATCH_INCOME,
            }
        ),
        frozenset({FISH_TOTAL_EXPENSES_DEDUCTIBLE}),
    ),
    (
        Subtract,
        frozenset({FISH_GROSS_INCOME_BEFORE_EXPENSES, FISH_TOTAL_EXPENSES}),
        frozenset({FISH_NET_INCOME_BEFORE_BOAT_LIMIT}),
    ),
    (
        Subtract,
        frozenset({FISH_GROSS_INCOME_BEFORE_EXPENSES, FISH_TOTAL_EXPENSES_DEDUCTIBLE}),
        frozenset({FISH_NET_INCOME_BEFORE_ADJUSTMENTS}),
    ),
    (
        ChooseByCount,
        frozenset({FISH_NET_INCOME_BEFORE_ADJUSTMENTS, FISH_PARTNER_CHECKED, FISH_PARTNER_SHARE}),
        frozenset({FISH_SHARE_OF_NET_INCOME}),
    ),
    (
        Sum,
        frozenset({FISH_SHARE_OF_NET_INCOME, FISH_PARTNER_GST_HST_REBATE}),
        frozenset({FISH_PARTNERSHIP_TOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                FISH_PARTNER_OTHER_AMOUNT_A,
                FISH_PARTNER_OTHER_AMOUNT_B,
                FISH_PARTNER_OTHER_AMOUNT_C,
                FISH_PARTNER_OTHER_AMOUNT_D,
                FISH_PARTNER_OTHER_AMOUNT_E,
            }
        ),
        frozenset({FISH_PARTNER_OTHER_AMOUNTS_TOTAL}),
    ),
    (Sum, frozenset({FISH_PARTNER_OTHER_AMOUNTS_TOTAL}), frozenset({FISH_PARTNER_OTHER_AMOUNTS})),
    (
        Subtract,
        frozenset({FISH_PARTNERSHIP_TOTAL, FISH_PARTNER_OTHER_AMOUNTS}),
        frozenset({FISH_NET_INCOME_AFTER_ADJUSTMENTS}),
    ),
    (
        Sum,
        frozenset(
            {
                FISH_HOME_HEAT,
                FISH_HOME_ELECTRICITY,
                FISH_HOME_INSURANCE,
                FISH_HOME_MAINTENANCE,
                FISH_HOME_MORTGAGE_INTEREST,
                FISH_HOME_PROPERTY_TAXES,
                FISH_HOME_OTHER_EXPENSES,
            }
        ),
        frozenset({FISH_HOME_EXPENSES_SUBTOTAL}),
    ),
    (
        Subtract,
        frozenset({FISH_HOME_EXPENSES_SUBTOTAL, FISH_HOME_PERSONAL_USE_PART}),
        frozenset({FISH_HOME_EXPENSES_BUSINESS_PART}),
    ),
    (
        Sum,
        frozenset({FISH_HOME_CARRIED_FORWARD, FISH_HOME_CCA, FISH_HOME_EXPENSES_BUSINESS_PART}),
        frozenset({FISH_HOME_EXPENSES_AVAILABLE}),
    ),
    (
        SumNotBelowZero,
        frozenset({FISH_NET_INCOME_AFTER_ADJUSTMENTS}),
        frozenset({FISH_HOME_INCOME_LIMIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FISH_HOME_EXPENSES_AVAILABLE, FISH_HOME_INCOME_LIMIT}),
        frozenset({FISH_HOME_CARRY_FORWARD}),
    ),
    (
        LesserOf,
        frozenset({FISH_HOME_EXPENSES_AVAILABLE, FISH_HOME_INCOME_LIMIT}),
        frozenset({FISH_HOME_ALLOWABLE_CLAIM}),
    ),
    (Sum, frozenset({FISH_HOME_ALLOWABLE_CLAIM}), frozenset({FISH_HOME_EXPENSES})),
    (
        Subtract,
        frozenset({FISH_HOME_EXPENSES, FISH_NET_INCOME_AFTER_ADJUSTMENTS}),
        frozenset({FISHING_INCOME}),
    ),
    (
        ClosingUccProrated,
        frozenset({FISH_CCA_CLASSES_ADJUSTED, FISH_FISCAL_PERIOD_DAYS}),
        frozenset({FISH_CLOSING_UCC}),
    ),
    (CreditAmount, frozenset(), frozenset({FISH_IMMEDIATE_EXPENSING_CAP})),
    (CreditAmount, frozenset(), frozenset({IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS})),
    (CreditAmount, frozenset(), frozenset({FISH_EPOP_PERCENTAGE_MAXIMUM})),
    (
        ApplyPercentage,
        frozenset({FISH_IMMEDIATE_EXPENSING_CAP, FISH_EPOP_PERCENTAGE}),
        frozenset({FISH_IMMEDIATE_EXPENSING_SHARE}),
    ),
    (
        Subtract,
        frozenset({FISH_EPOP_PERCENTAGE_MAXIMUM, FISH_EPOP_PERCENTAGE_TOTAL}),
        frozenset({FISH_EPOP_PERCENTAGE_ROOM}),
    ),
    (
        ChooseBySign,
        frozenset({FISH_EPOP_PERCENTAGE_ROOM, FISH_IMMEDIATE_EXPENSING_SHARE}),
        frozenset({FISH_IMMEDIATE_EXPENSING_ALLOCATED}),
    ),
    (
        TimesCount,
        frozenset({FISH_IMMEDIATE_EXPENSING_ALLOCATED, FISH_EPOP_AGREEMENT_FILED_CHECKED}),
        frozenset({FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FISH_EPOP_ASSOCIATED_CHECKED,
                FISH_IMMEDIATE_EXPENSING_CAP,
                FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
            }
        ),
        frozenset({FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FISH_MINISTER_ALLOCATION_GIVEN_CHECKED,
                FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                FISH_MINISTER_ALLOCATION,
            }
        ),
        frozenset({FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION}),
    ),
    (
        ProratedByFiscalPeriodDays,
        frozenset(
            {
                FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
                FISH_FISCAL_PERIOD_DAYS,
                IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
            }
        ),
        frozenset({FISH_IMMEDIATE_EXPENSING_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FISH_MINISTER_ALLOCATION_GIVEN_CHECKED,
                FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                FISH_MINISTER_ALLOCATION,
            }
        ),
        frozenset({FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED}),
    ),
    (
        SumNotBelowZero,
        frozenset({FISH_NET_INCOME_BEFORE_BOAT_LIMIT, FISH_CCA_CLAIM}),
        frozenset({FISH_INCOME_BEFORE_CCA}),
    ),
    (
        ImmediateExpensingClaim,
        frozenset(
            {FISH_CCA_CLASSES_ADJUSTED, FISH_IMMEDIATE_EXPENSING_LIMIT, FISH_INCOME_BEFORE_CCA}
        ),
        frozenset({FISH_IMMEDIATE_EXPENSING_CLAIM}),
    ),
    (
        BusinessVehicleExpenses,
        frozenset({BUSINESS_VEHICLES, FISH_VEHICLE_SALES_TAX_RATE, FISH_FISCAL_PERIOD_DAYS}),
        frozenset({FISH_MOTOR_VEHICLE_EXPENSES}),
    ),
    (
        YesOrNoCount,
        frozenset({FISH_EPOP_ASSOCIATED}),
        frozenset({FISH_EPOP_ASSOCIATED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FISH_EPOP_AGREEMENT_FILED}),
        frozenset({FISH_EPOP_AGREEMENT_FILED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FISH_MINISTER_ALLOCATION_GIVEN}),
        frozenset({FISH_MINISTER_ALLOCATION_GIVEN_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FISH_PARTNER}),
        frozenset({FISH_PARTNER_CHECKED}),
    ),
}

WIRING = {
    (RecordTotal, frozenset({FISHING_INCOME_ON_RETURN_LINES}), frozenset({FISHING_INCOME})),
}
