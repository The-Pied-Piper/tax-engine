"""The CA-ON manifest entries of Form T2125 (see `test_manifest.py` and `test_manifest_t2125.py`).

T2125 is a form of the manifest: its 68 selections belong to the form `ca/t2125` (`FORM_STEPS`),
run once for each statement of `ca/t2125_statements`, whose fields are the T2125 inputs
(`FORM_INPUTS`). Each statement's line 9946 is routed by its line code: three conditions flags
(`ca/business_line_is_*`) count the code, and six `core/times_count` selections send the net
(`ca/net_on_*_line`) and the gross (`ca/gross_on_*_line`) to the one line of that code. The form
exports sixteen artifacts (`FORM_EXPORTS`), each readable by the other forms as `ca/t2125.<export>`.
The return declares the three grosses as its outputs (`OUTPUTS`) and reads the nets through
`core/record_total` (`STEPS` and `WIRING`), with the instances input in place of the statements.
The form selects one `ca/business_vehicle_expenses` step for Charts A to C, over the statement's
list of vehicles, with the printed constants of Charts B and C as its datasets.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_engine.jurisdictions.ca.capabilities.business_vehicle_expenses import (
    BusinessVehicleExpenses,
)
from tax_engine.jurisdictions.ca.capabilities.cca_claim_prorated import CcaClaimProrated
from tax_engine.jurisdictions.ca.capabilities.cca_vehicle_additions_checks import (
    CcaVehicleAdditionsChecks,
)
from tax_engine.jurisdictions.ca.capabilities.cca_vehicle_proceeds import CcaVehicleProceeds
from tax_engine.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_prorated import ClosingUccProrated
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.capabilities.fiscal_period_days_from_dates import (
    FiscalPeriodDaysFromDates,
)
from tax_engine.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_engine.jurisdictions.ca.capabilities.prorated_by_fiscal_period_days import (
    ProratedByFiscalPeriodDays,
)
from tax_engine.jurisdictions.ca.capabilities.recaptured_cca import RecapturedCca
from tax_engine.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_ADJUSTED_GROSS_SALES,
    BUSINESS_ADVERTISING,
    BUSINESS_BAD_DEBTS,
    BUSINESS_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,
    BUSINESS_CAPITAL_CONTRIBUTIONS,
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART,
    BUSINESS_CCA_CLASSES,
    BUSINESS_CCA_CLASSES_ADJUSTED,
    BUSINESS_CCA_CLASSES_CHECKED,
    BUSINESS_CCA_PERSONAL_PART,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_INVENTORY,
    BUSINESS_CLOSING_UCC,
    BUSINESS_COST_OF_GOODS_SOLD,
    BUSINESS_COST_OF_GOODS_SUBTOTAL,
    BUSINESS_DELIVERY_FREIGHT_AND_EXPRESS,
    BUSINESS_DIRECT_WAGE_COSTS,
    BUSINESS_DRAWINGS,
    BUSINESS_EPOP_AGREEMENT_FILED,
    BUSINESS_EPOP_AGREEMENT_FILED_CHECKED,
    BUSINESS_EPOP_ASSOCIATED,
    BUSINESS_EPOP_ASSOCIATED_CHECKED,
    BUSINESS_EPOP_PERCENTAGE,
    BUSINESS_EPOP_PERCENTAGE_MAXIMUM,
    BUSINESS_EPOP_PERCENTAGE_ROOM,
    BUSINESS_EPOP_PERCENTAGE_TOTAL,
    BUSINESS_FISCAL_PERIOD_DAYS,
    BUSINESS_FISCAL_PERIOD_FROM,
    BUSINESS_FISCAL_PERIOD_TO,
    BUSINESS_FUEL_COSTS,
    BUSINESS_GROSS_INCOME,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT,
    BUSINESS_GROSS_PROFIT,
    BUSINESS_GROSS_SALES,
    BUSINESS_HOME_ALLOWABLE_CLAIM,
    BUSINESS_HOME_CARRIED_FORWARD,
    BUSINESS_HOME_CARRY_FORWARD,
    BUSINESS_HOME_CCA,
    BUSINESS_HOME_ELECTRICITY,
    BUSINESS_HOME_EXPENSES,
    BUSINESS_HOME_EXPENSES_AVAILABLE,
    BUSINESS_HOME_EXPENSES_BUSINESS_PART,
    BUSINESS_HOME_EXPENSES_SUBTOTAL,
    BUSINESS_HOME_HEAT,
    BUSINESS_HOME_INCOME_LIMIT,
    BUSINESS_HOME_INSURANCE,
    BUSINESS_HOME_MAINTENANCE,
    BUSINESS_HOME_MORTGAGE_INTEREST,
    BUSINESS_HOME_OTHER_EXPENSES,
    BUSINESS_HOME_PERSONAL_USE_PART,
    BUSINESS_HOME_PROPERTY_TAXES,
    BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED,
    BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_CAP,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIM,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    BUSINESS_IMMEDIATE_EXPENSING_SHARE,
    BUSINESS_INCOME,
    BUSINESS_INCOME_BEFORE_CCA,
    BUSINESS_INCOME_LINE,
    BUSINESS_INCOME_LINE_CHECKED,
    BUSINESS_INSURANCE,
    BUSINESS_INTEREST_AND_BANK_CHARGES,
    BUSINESS_JOURNALISM_LABOUR_TAX_CREDIT,
    BUSINESS_LAND_ADDITIONS,
    BUSINESS_LAND_DISPOSITIONS,
    BUSINESS_LIABILITIES,
    BUSINESS_LINE_IS_BUSINESS,
    BUSINESS_LINE_IS_COMMISSION,
    BUSINESS_LINE_IS_PROFESSIONAL,
    BUSINESS_MANAGEMENT_AND_ADMINISTRATION_FEES,
    BUSINESS_MEALS_AND_ENTERTAINMENT,
    BUSINESS_MINISTER_ALLOCATION,
    BUSINESS_MINISTER_ALLOCATION_GIVEN,
    BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED,
    BUSINESS_MOTOR_VEHICLE_EXPENSES,
    BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_OFFICE_EXPENSES,
    BUSINESS_OFFICE_STATIONERY_AND_SUPPLIES,
    BUSINESS_OPENING_INVENTORY,
    BUSINESS_OTHER_COSTS,
    BUSINESS_OTHER_EXPENSES,
    BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    BUSINESS_OTHER_INCOME,
    BUSINESS_OTHER_INCOME_WITH_RECAPTURE,
    BUSINESS_PARTNER,
    BUSINESS_PARTNER_CHECKED,
    BUSINESS_PARTNER_GST_HST_REBATE,
    BUSINESS_PARTNER_OTHER_AMOUNT_A,
    BUSINESS_PARTNER_OTHER_AMOUNT_B,
    BUSINESS_PARTNER_OTHER_AMOUNT_C,
    BUSINESS_PARTNER_OTHER_AMOUNT_D,
    BUSINESS_PARTNER_OTHER_AMOUNT_E,
    BUSINESS_PARTNER_OTHER_AMOUNTS,
    BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL,
    BUSINESS_PARTNER_SHARE,
    BUSINESS_PARTNERSHIP_TOTAL,
    BUSINESS_PROFESSIONAL_FEES,
    BUSINESS_PROPERTY_TAXES,
    BUSINESS_PURCHASES,
    BUSINESS_QUICK_METHOD_ASSISTANCE,
    BUSINESS_QUICK_METHOD_GST_HST,
    BUSINESS_QUICK_METHOD_REMITTED,
    BUSINESS_RECAPTURED_CCA,
    BUSINESS_RENT,
    BUSINESS_REPAIRS_AND_MAINTENANCE,
    BUSINESS_RESERVES_AND_OTHER_INCOME,
    BUSINESS_RESERVES_DEDUCTED_LAST_YEAR,
    BUSINESS_SALARIES_WAGES_AND_BENEFITS,
    BUSINESS_SALES_ADJUSTMENTS,
    BUSINESS_SALES_SUBTOTAL,
    BUSINESS_SHARE_OF_NET_INCOME,
    BUSINESS_SUBCONTRACTS,
    BUSINESS_TERMINAL_LOSS,
    BUSINESS_TOTAL_EXPENSES,
    BUSINESS_TRAVEL_EXPENSES,
    BUSINESS_UTILITIES,
    BUSINESS_VEHICLE_SALES_TAX_RATE,
    BUSINESS_VEHICLES,
    COMMISSION_INCOME,
    GROSS_BUSINESS_INCOME,
    GROSS_COMMISSION_INCOME,
    GROSS_ON_BUSINESS_LINE,
    GROSS_ON_COMMISSION_LINE,
    GROSS_ON_PROFESSIONAL_LINE,
    GROSS_PROFESSIONAL_INCOME,
    IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
    JOURNALISM_LABOUR_TAX_CREDIT,
    NET_ON_BUSINESS_LINE,
    NET_ON_COMMISSION_LINE,
    NET_ON_PROFESSIONAL_LINE,
    PROFESSIONAL_INCOME,
)
from tests.jurisdictions.ca_on.manifest_families.t1139 import (
    BUSINESS_INCOME_ON_RETURN_LINES,
    COMMISSION_INCOME_ON_RETURN_LINES,
    PROFESSIONAL_INCOME_ON_RETURN_LINES,
)

NET_INCOME_PER_STATEMENT = RecordListKind(
    "ca/t2125.net_on_business_line", fields=(NET_ON_BUSINESS_LINE,)
)
NET_ON_PROFESSIONAL_LINE_PER_STATEMENT = RecordListKind(
    "ca/t2125.net_on_professional_line", fields=(NET_ON_PROFESSIONAL_LINE,)
)
NET_ON_COMMISSION_LINE_PER_STATEMENT = RecordListKind(
    "ca/t2125.net_on_commission_line", fields=(NET_ON_COMMISSION_LINE,)
)
GROSS_ON_BUSINESS_LINE_PER_STATEMENT = RecordListKind(
    "ca/t2125.gross_on_business_line", fields=(GROSS_ON_BUSINESS_LINE,)
)
GROSS_ON_PROFESSIONAL_LINE_PER_STATEMENT = RecordListKind(
    "ca/t2125.gross_on_professional_line", fields=(GROSS_ON_PROFESSIONAL_LINE,)
)
GROSS_ON_COMMISSION_LINE_PER_STATEMENT = RecordListKind(
    "ca/t2125.gross_on_commission_line", fields=(GROSS_ON_COMMISSION_LINE,)
)
BUSINESS_CLOSING_UCC_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_closing_ucc", fields=(BUSINESS_CLOSING_UCC,)
)
BUSINESS_HOME_CARRY_FORWARD_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_home_carry_forward", fields=(BUSINESS_HOME_CARRY_FORWARD,)
)
BUSINESS_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_immediate_expensing_claim", fields=(BUSINESS_IMMEDIATE_EXPENSING_CLAIM,)
)
BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_immediate_expensing_limit_unprorated",
    fields=(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,),
)
BUSINESS_LAND_ADDITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_land_additions", fields=(BUSINESS_LAND_ADDITIONS,)
)
BUSINESS_LAND_DISPOSITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_land_dispositions", fields=(BUSINESS_LAND_DISPOSITIONS,)
)
BUSINESS_LIABILITIES_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_liabilities", fields=(BUSINESS_LIABILITIES,)
)
BUSINESS_DRAWINGS_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_drawings", fields=(BUSINESS_DRAWINGS,)
)
BUSINESS_JOURNALISM_LABOUR_TAX_CREDIT_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_journalism_labour_tax_credit",
    fields=(BUSINESS_JOURNALISM_LABOUR_TAX_CREDIT,),
)
BUSINESS_CAPITAL_CONTRIBUTIONS_PER_STATEMENT = RecordListKind(
    "ca/t2125.business_capital_contributions", fields=(BUSINESS_CAPITAL_CONTRIBUTIONS,)
)

FORM_INPUTS = frozenset(
    {
        "ca/business_income_line",
        "ca/business_gross_sales",
        "ca/business_sales_adjustments",
        "ca/business_quick_method_gst_hst",
        "ca/business_quick_method_remitted",
        "ca/business_reserves_deducted_last_year",
        "ca/business_other_income",
        "ca/business_opening_inventory",
        "ca/business_purchases",
        "ca/business_direct_wage_costs",
        "ca/business_subcontracts",
        "ca/business_other_costs",
        "ca/business_closing_inventory",
        "ca/business_advertising",
        "ca/business_meals_and_entertainment",
        "ca/business_bad_debts",
        "ca/business_insurance",
        "ca/business_interest_and_bank_charges",
        "ca/business_business_taxes_licences_and_memberships",
        "ca/business_office_expenses",
        "ca/business_office_stationery_and_supplies",
        "ca/business_professional_fees",
        "ca/business_management_and_administration_fees",
        "ca/business_rent",
        "ca/business_repairs_and_maintenance",
        "ca/business_salaries_wages_and_benefits",
        "ca/business_property_taxes",
        "ca/business_travel_expenses",
        "ca/business_utilities",
        "ca/business_fuel_costs",
        "ca/business_delivery_freight_and_express",
        "ca/business_vehicles",
        "ca/business_vehicle_sales_tax_rate",
        "ca/business_cca_personal_part",
        "ca/business_other_expenses",
        "ca/business_journalism_labour_tax_credit",
        "ca/business_partner_gst_hst_rebate",
        "ca/business_partner_other_amount_a",
        "ca/business_partner_other_amount_b",
        "ca/business_partner_other_amount_c",
        "ca/business_partner_other_amount_d",
        "ca/business_partner_other_amount_e",
        "ca/business_home_heat",
        "ca/business_home_electricity",
        "ca/business_home_insurance",
        "ca/business_home_maintenance",
        "ca/business_home_mortgage_interest",
        "ca/business_home_property_taxes",
        "ca/business_home_other_expenses",
        "ca/business_home_personal_use_part",
        "ca/business_home_cca",
        "ca/business_home_carried_forward",
        "ca/business_partner_share",
        "ca/business_partner",
        "ca/business_cca_classes",
        "ca/business_epop_associated",
        "ca/business_epop_agreement_filed",
        "ca/business_epop_percentage",
        "ca/business_epop_percentage_total",
        "ca/business_minister_allocation_given",
        "ca/business_minister_allocation",
        "ca/business_fiscal_period_from",
        "ca/business_fiscal_period_to",
        "ca/business_land_additions",
        "ca/business_land_dispositions",
        "ca/business_liabilities",
        "ca/business_drawings",
        "ca/business_capital_contributions",
    }
)

FORM_STEPS = {
    # T2125 Part 3A "Subtotal: Amount 3A minus amount 3B 3C": amount 3A "Gross sales,
    # commissions, or fees (include GST/HST collected or collectible)" less amount 3B
    # "GST/HST, provincial sales tax, returns, allowances, discounts, and GST/HST
    # adjustments (included in amount 3A)", both caller inputs.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_gross_sales",
            "less": "ca/business_sales_adjustments",
        },
        produces={"output": "ca/business_sales_subtotal"},
    ),
    # T2125 Part 3A "If you are using the quick method for GST/HST - Government assistance
    # calculated as follows:" "Subtotal: Amount 3D minus amount 3E 3F": amount 3D "GST/HST
    # collected or collectible on sales, commissions, and fees eligible for the quick
    # method" less amount 3E "GST/HST remitted: (sales, commissions, and fees eligible for
    # the quick method plus GST/HST collected or collectible) multiplied by the applicable
    # quick method remittance rate", both caller inputs (no capability multiplies by a rate
    # the caller enters). Signed: 3F may be below zero.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_quick_method_gst_hst",
            "less": "ca/business_quick_method_remitted",
        },
        produces={"output": "ca/business_quick_method_assistance"},
    ),
    # T2125 Part 3A "Adjusted gross sales: Amount 3C plus amount 3F (enter on line 8000 of
    # Part 3C)"; Part 3C line 8000 "Adjusted gross sales (amount 3G) or adjusted
    # professional fees (amount 3N)" is the same artifact, so it has no step of its own.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_sales_subtotal",
                "ca/business_quick_method_assistance",
            ),
        },
        produces={"output": "ca/business_adjusted_gross_sales"},
    ),
    # T2125 Area A endnote 2 "The proceeds of disposition of a zero-emission passenger vehicle
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
            "classes": "ca/business_cca_classes",
            "sales_tax_rate": "ca/business_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/business_cca_classes_checked"},
    ),
    CapabilitySelection(
        name="ca/cca_vehicle_proceeds",
        params={
            "prescribed_amounts": "ca/cca_vehicle_prescribed_amounts",
            "zepv_prescribed_amounts": "ca/cca_zepv_prescribed_amounts",
        },
        consumes={
            "classes": "ca/business_cca_classes_checked",
            "sales_tax_rate": "ca/business_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/business_cca_classes_adjusted"},
    ),
    # T2125 Area A endnote 3 "If you have a negative amount in column 7, add it to income as
    # a recapture in Part 3C on line 8230. ... Recapture and terminal loss do not apply to a
    # Class 10.1 property unless it is a DIEP.": the recapture of each class of the Area A
    # list (column 7 made positive when negative), totalled.
    CapabilitySelection(
        name="ca/recaptured_cca",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/business_cca_classes_adjusted",
        },
        produces={"output": "ca/business_recaptured_cca"},
    ),
    # T2125 Part 3C line 8230 "Other income (specify):", which takes the recapture of Area A
    # (endnote 3 "add it to income as a recapture in Part 3C on line 8230"): the other
    # income the caller specifies plus the recapture.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_other_income",
                "ca/business_recaptured_cca",
            ),
        },
        produces={"output": "ca/business_other_income_with_recapture"},
    ),
    # T2125 Part 3C "Subtotal: Line 8290 plus line 8230 3O": line 8290 "Reserves deducted
    # last year", a caller input, plus line 8230.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_reserves_deducted_last_year",
                "ca/business_other_income_with_recapture",
            ),
        },
        produces={"output": "ca/business_reserves_and_other_income"},
    ),
    # T2125 Part 3C "Gross business or professional income: Line 8000 plus amount 3O" (line
    # 8299), "Report the gross business or professional income from line 8299 on the
    # applicable line of your income tax and benefit return as indicated below: business
    # income on line 13499"; line 8000 is amount 3G above.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_adjusted_gross_sales",
                "ca/business_reserves_and_other_income",
            ),
        },
        produces={"output": "ca/business_gross_income"},
    ),
    # T2125 Part 3D "Gross business income (line 8299 of Part 3C). 3P".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/business_gross_income",),
        },
        produces={"output": "ca/business_gross_income_for_gross_profit"},
    ),
    # T2125 Part 3D "Subtotal: Add amounts 3Q to 3U. 3V": 3Q "Opening inventory (include raw
    # materials, goods in process, and finished goods)", 3R "Purchases during the year (net
    # of returns, allowances, and discounts)", 3S "Direct wage costs", 3T "Subcontracts" and
    # 3U "Other costs", all caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_opening_inventory",
                "ca/business_purchases",
                "ca/business_direct_wage_costs",
                "ca/business_subcontracts",
                "ca/business_other_costs",
            ),
        },
        produces={"output": "ca/business_cost_of_goods_subtotal"},
    ),
    # T2125 Part 3D "Cost of goods sold: Amount 3V minus line 8500 8518": line 8500 "Closing
    # inventory (include raw materials, goods in process, and finished goods)", a caller
    # input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_cost_of_goods_subtotal",
            "less": "ca/business_closing_inventory",
        },
        produces={"output": "ca/business_cost_of_goods_sold"},
    ),
    # T2125 Part 3D "Gross profit (or loss): Amount 3P minus line 8518." (line 8519):
    # signed, a loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_gross_income_for_gross_profit",
            "less": "ca/business_cost_of_goods_sold",
        },
        produces={"output": "ca/business_gross_profit"},
    ),
    # T2125 Part 4 "Gross business or professional income (line 8299 of Part 3C) or Gross
    # profit (line 8519 of Part 3D). 4A": for a business statement, which has a Part 3D, it
    # is line 8519.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/business_gross_profit",),
        },
        produces={"output": "ca/business_gross_income_before_expenses"},
    ),
    # T2125 page 1 "Fiscal period From / to, Date (YYYYMMDD)": the days of the fiscal period,
    # inclusive, from the two dates the caller enters, or the 365 of a full year when none are
    # entered (0 and 0). Guide T4002 "You were asking?": "Since your fiscal period is less than 365
    # days, you have to prorate your CCA claim. ... base your CCA claim on the number of days in
    # your fiscal period compared to 365 days. In this case, your fiscal period is 214 days."
    CapabilitySelection(
        name="ca/fiscal_period_days_from_dates",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "from_date": "ca/business_fiscal_period_from",
            "to_date": "ca/business_fiscal_period_to",
        },
        produces={"output": "ca/business_fiscal_period_days"},
    ),
    # T2125 Area A "Total CCA claim for the year: Total of column 21 (enter on line 9936 of Part 4
    # amount ii minus any personal part and any CCA for business-use-of-home expenses)" (amount ii):
    # the CCA claimed on each class of the Area A list, at most its maximum (column 19 multiplied by
    # column 20), totalled.
    CapabilitySelection(
        name="ca/cca_claim_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/business_cca_classes_adjusted",
            "fiscal_period_days": "ca/business_fiscal_period_days",
        },
        produces={"output": "ca/business_cca_table_claim"},
    ),
    # T2125 Part 4 "Capital cost allowance (CCA). Enter amount ii of Area A minus any
    # personal part and any CCA for business-use-of-home expenses 9936 4U", first step:
    # amount ii minus the personal part of CCA, a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_cca_table_claim",
            "less": "ca/business_cca_personal_part",
        },
        produces={"output": "ca/business_cca_claim_less_personal_part"},
    ),
    # T2125 Part 4 line 9936 (amount 4U) "Capital cost allowance (CCA). Enter amount ii of
    # Area A minus any personal part and any CCA for business-use-of-home expenses", second
    # step: that result minus the CCA for business-use-of-home expenses, amount 7K "Capital
    # cost allowance (business part only)", a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_cca_claim_less_personal_part",
            "less": "ca/business_home_cca",
        },
        produces={"output": "ca/business_cca_claim"},
    ),
    # T2125 Area A endnote 3 "If no property is left in the class and there is a positive
    # amount in this column, deduct the amount from income as a terminal loss in Part 4 on
    # line 9270. Recapture and terminal loss do not apply to a Class 10.1 property unless it
    # is a DIEP.": the terminal loss of each class of the Area A list, totalled.
    CapabilitySelection(
        name="ca/terminal_loss",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/business_cca_classes_adjusted",
        },
        produces={"output": "ca/business_terminal_loss"},
    ),
    # T2125 Part 4 "Other expenses (specify): 9270 4V", which takes the terminal loss of
    # Area A (endnote 3 "deduct the amount from income as a terminal loss in Part 4 on line
    # 9270"): the other expenses the caller specifies plus the terminal loss.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_other_expenses",
                "ca/business_terminal_loss",
            ),
        },
        produces={"output": "ca/business_other_expenses_with_terminal_loss"},
    ),
    # T2125 Area A column 22 "UCC at the end of the year (col. 7 minus col. 21)": the class
    # number and column 22 of each class of the Area A list, a product of the return for
    # next year's column 1.
    CapabilitySelection(
        name="ca/closing_ucc_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/business_cca_classes_adjusted",
            "fiscal_period_days": "ca/business_fiscal_period_days",
        },
        produces={"output": "ca/business_closing_ucc"},
    ),
    # T2125 Area A endnote 5 "the immediate expensing limit, which is equal to one of the
    # following, whichever is applicable: $1.5 million, if you are not associated with any other
    # eligible person or partnership (EPOP) in the tax year" and Area G "Immediate expensing limit
    # allocated to your business: Multiply $1.5 million by the percentage assigned to your
    # business in column 3**": the printed $1.5 million, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/business_immediate_expensing_cap"},
        consumes={},
        produces={"output": "ca/business_immediate_expensing_cap"},
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
    # T2125 Area G "The total of all percentages assigned under the agreement should not be more
    # than 100%. If the total is more than 100%, then the associated group has an immediate
    # expensing limit of zero." and "** If the total of column 3 is more than 100%, enter "0."":
    # the printed 100%, a dataset, as the form prints a percentage (100 for 100%).
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/business_epop_percentage_maximum"},
        consumes={},
        produces={"output": "ca/business_epop_percentage_maximum"},
    ),
    # T2125 Area G "Immediate expensing limit allocated to your business: Multiply $1.5 million by
    # the percentage assigned to your business in column 3**", first step: $1.5 million times the
    # percentage assigned to your business in column 3, a caller input as the form prints it (40
    # for 40%).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/business_immediate_expensing_rounding"},
        consumes={
            "amount": "ca/business_immediate_expensing_cap",
            "percentage": "ca/business_epop_percentage",
        },
        produces={"output": "ca/business_immediate_expensing_share"},
    ),
    # T2125 Area G "** If the total of column 3 is more than 100%, enter "0."", first step: 100%
    # less "Total of percentage assigned: Total of column 3", a caller input; negative when the
    # total is more than 100%.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_epop_percentage_maximum",
            "less": "ca/business_epop_percentage_total",
        },
        produces={"output": "ca/business_epop_percentage_room"},
    ),
    # T2125 Area G "Immediate expensing limit allocated to your business: Multiply $1.5 million by
    # the percentage assigned to your business in column 3**" and "** If the total of column 3 is
    # more than 100%, enter "0."": the multiple above when 100% less the total of column 3 is zero
    # or positive, else 0.
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/business_epop_percentage_room",
            "when_positive": (),
            "when_zero": (),
            "when_negative": (),
            "when_non_positive": (),
            "when_non_negative": ("ca/business_immediate_expensing_share",),
        },
        produces={"output": "ca/business_immediate_expensing_allocated"},
    ),
    # T2125 Area A endnote 5 "amount iii of Area G, if you are associated with one or more EPOPs
    # in the tax year" and "zero, if you are associated with one or more EPOPs and an agreement
    # that assigns a percentage to one or more of the associated EPOPs was not filed with the
    # minister in a prescribed form": amount iii times the count of agreements filed (a caller's 0
    # or 1), so 0 when none was filed.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/business_immediate_expensing_allocated",
            "count": "ca/business_epop_agreement_filed_checked",
        },
        produces={"output": "ca/business_immediate_expensing_associated_limit"},
    ),
    # T2125 Area A endnote 5 "the immediate expensing limit, which is equal to one of the
    # following, whichever is applicable": a count of 1 for associated with one or more EPOPs (a
    # caller's 0 or 1) chooses the limit above ("amount iii of Area G" or "zero"); with a count of
    # 0 it is the $1.5 million ("if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year").
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/business_epop_associated_checked",
            "when_none": "ca/business_immediate_expensing_cap",
            "when_any": "ca/business_immediate_expensing_associated_limit",
        },
        produces={"output": "ca/business_immediate_expensing_limit_before_minister"},
    ),
    # T2125 Note 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": a count of 1 (a caller's 0 or 1) chooses the amount allocated by the minister,
    # as entered, in place of the limit before the days scaling; with a count of 0 the limit before
    # the minister's amount stands. The amount allocated is the amount for the year, and the days
    # scaling below applies to it as it does to the limit.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/business_minister_allocation_given_checked",
            "when_none": "ca/business_immediate_expensing_limit_before_minister",
            "when_any": "ca/business_minister_allocation",
        },
        produces={"output": "ca/business_immediate_expensing_limit_before_proration"},
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
            "rounding": "ca/business_immediate_expensing_rounding",
            "class_rates": "ca/cca_class_rates",
        },
        consumes={
            "amount": "ca/business_immediate_expensing_limit_before_proration",
            "fiscal_period_days": "ca/business_fiscal_period_days",
            "short_year_days": "ca/immediate_expensing_short_year_days",
        },
        produces={"output": "ca/business_immediate_expensing_limit"},
    ),
    # T2125 Area A endnote 5 "the immediate expensing limit, which is equal to one of the
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
            "count": "ca/business_minister_allocation_given_checked",
            "when_none": "ca/business_immediate_expensing_limit_before_minister",
            "when_any": "ca/business_minister_allocation",
        },
        produces={"output": "ca/business_immediate_expensing_limit_unprorated"},
    ),
    # T2125 Area A endnote 5 "the amount of income, if any, earned from the source of income that
    # is a business (before any CCA deductions) in which the relevant DIEP is used for the tax
    # year": line 9369 "Net income (loss) before adjustments" plus line 9936, the CCA it deducted
    # (the recapture on line 8230 is already in gross income and the terminal loss on line 9270 an
    # expense), not below zero.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/business_net_income_before_adjustments",
                "ca/business_cca_claim",
            ),
        },
        produces={"output": "ca/business_income_before_cca"},
    ),
    # T2125 Area A "Total immediate expensing claim for the year: Total of column 9" (line i) and
    # endnote 5 "The total immediate expensing amount for the tax year (total of column 9) is
    # limited to the lesser of: the immediate expensing limit"; "the UCC of DIEPs in column 8";
    # "the amount of income, if any, earned from the source of income that is a business (before
    # any CCA deductions) in which the relevant DIEP is used for the tax year": the total of
    # column 9 of the Area A list, refused when above the limit or above the income before CCA.
    CapabilitySelection(
        name="ca/immediate_expensing_claim",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/business_cca_classes_adjusted",
            "immediate_expensing_limit": "ca/business_immediate_expensing_limit",
            "income_before_cca": "ca/business_income_before_cca",
        },
        produces={"output": "ca/business_immediate_expensing_claim"},
    ),
    # T2125 Charts A to C, "Total motor vehicle expenses" (line 12), "Business use part" (line 13),
    # Chart B "Available interest expense" (lines 17 to 19), Chart C "Eligible leasing cost" (lines
    # 20 to 28) and Chart A line 16 "Allowable motor vehicle expenses: Add amounts 13 to 15 (enter
    # this total on line 9281 of Part 4)": one step over the vehicles of the statement, one chart
    # for each, whose line 16 amounts it adds. The printed constants ("$350***", "÷ 30", "$44,706",
    # "$1,100", "$38,000" and the 85%) and the rounding are its datasets; the sales tax rate of the
    # province stays a statement input.
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
            "sales_tax_rate": "ca/business_vehicle_sales_tax_rate",
            "fiscal_period_days": "ca/business_fiscal_period_days",
        },
        produces={"output": "ca/business_motor_vehicle_expenses"},
    ),
    # T2125 Part 4 "Total expenses: Total of amounts 4B to 4V 9368": the 19 expense lines 4B
    # to 4T ("Advertising" to "Motor vehicle expenses (not including CCA) (amount 16 of
    # Chart A)", the caller's inputs except 4T, which is the Chart A steps above), then 4U
    # (line 9936) and 4V (line 9270), in the form's order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_advertising",
                "ca/business_meals_and_entertainment",
                "ca/business_bad_debts",
                "ca/business_insurance",
                "ca/business_interest_and_bank_charges",
                "ca/business_business_taxes_licences_and_memberships",
                "ca/business_office_expenses",
                "ca/business_office_stationery_and_supplies",
                "ca/business_professional_fees",
                "ca/business_management_and_administration_fees",
                "ca/business_rent",
                "ca/business_repairs_and_maintenance",
                "ca/business_salaries_wages_and_benefits",
                "ca/business_property_taxes",
                "ca/business_travel_expenses",
                "ca/business_utilities",
                "ca/business_fuel_costs",
                "ca/business_delivery_freight_and_express",
                "ca/business_motor_vehicle_expenses",
                "ca/business_cca_claim",
                "ca/business_other_expenses_with_terminal_loss",
            ),
        },
        produces={"output": "ca/business_total_expenses"},
    ),
    # T2125 Part 4 "Net income (loss) before adjustments: Amount 4A minus line 9368" (line
    # 9369): signed, a loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_gross_income_before_expenses",
            "less": "ca/business_total_expenses",
        },
        produces={"output": "ca/business_net_income_before_adjustments"},
    ),
    # T2125 Part 5 partner answer, checked to be 0 or 1 before the step that reads it (in the part
    # `03y_t2125_partner_checks.yaml`). A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/business_partner"},
        produces={"output": "ca/business_partner_checked"},
    ),
    # T2125 Part 5 "Your share of line 9369 or the amount from your T5013 slip, Statement of
    # Partnership Income. 5A": a count of 1 for a partner (a caller's 0 or 1) chooses the
    # amount from the T5013 slip, as entered; with a count of 0 it is line 9369.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/business_partner_checked",
            "when_none": "ca/business_net_income_before_adjustments",
            "when_any": "ca/business_partner_share",
        },
        produces={"output": "ca/business_share_of_net_income"},
    ),
    # T2125 Part 6 "Total other amounts deductible from your share of the net partnership
    # income (loss): Add amounts 6A to 6E (enter this on line 9943 of Part 5). 6F": 6A to 6E
    # "List details of expenses: Expense amounts", caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_partner_other_amount_a",
                "ca/business_partner_other_amount_b",
                "ca/business_partner_other_amount_c",
                "ca/business_partner_other_amount_d",
                "ca/business_partner_other_amount_e",
            ),
        },
        produces={"output": "ca/business_partner_other_amounts_total"},
    ),
    # T2125 Part 5 "Other amounts deductible from your share of net partnership income
    # (loss) (amount 6F)" (line 9943).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/business_partner_other_amounts_total",),
        },
        produces={"output": "ca/business_partner_other_amounts"},
    ),
    # T2125 Part 5 "Total: Amount 5A plus amount 5B plus line 9974 5C": amount 5B "Canadian
    # journalism labour tax credit allocated to you in the year (box 236 of your T5013
    # slip)" and line 9974 "GST/HST rebate for partners received in the year", caller
    # inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_share_of_net_income",
                "ca/business_journalism_labour_tax_credit",
                "ca/business_partner_gst_hst_rebate",
            ),
        },
        produces={"output": "ca/business_partnership_total"},
    ),
    # T2125 Part 5 "Net income (loss) after adjustments: Amount 5C minus line 9943 5D":
    # signed, a loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_partnership_total",
            "less": "ca/business_partner_other_amounts",
        },
        produces={"output": "ca/business_net_income_after_adjustments"},
    ),
    # T2125 Part 7 "Subtotal: Add amounts 7A to 7G. 7H": 7A "Heat", 7B "Electricity", 7C
    # "Insurance", 7D "Maintenance", 7E "Mortgage interest", 7F "Property taxes" and 7G
    # "Other expenses (specify)", caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_home_heat",
                "ca/business_home_electricity",
                "ca/business_home_insurance",
                "ca/business_home_maintenance",
                "ca/business_home_mortgage_interest",
                "ca/business_home_property_taxes",
                "ca/business_home_other_expenses",
            ),
        },
        produces={"output": "ca/business_home_expenses_subtotal"},
    ),
    # T2125 Part 7 "Subtotal: Amount 7H minus amount 7I 7J": amount 7I "Personal-use part of
    # the business-use-of-home expenses", a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_home_expenses_subtotal",
            "less": "ca/business_home_personal_use_part",
        },
        produces={"output": "ca/business_home_expenses_business_part"},
    ),
    # T2125 Part 7 "Subtotal: Add amounts 7J to 7L. 7M": 7K "Capital cost allowance
    # (business part only), which means amount ii of Area A minus any portion of capital
    # cost allowance that is for personal use or entered on line 9936 of Part 4" and 7L
    # "Amount carried forward from previous year", caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_home_expenses_business_part",
                "ca/business_home_cca",
                "ca/business_home_carried_forward",
            ),
        },
        produces={"output": "ca/business_home_expenses_available"},
    ),
    # T2125 Part 7 "Net income (loss) after adjustments (amount 5D) (if negative, enter
    # "0"). 7N": amount 5D, or 0 when it is negative.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": ("ca/business_net_income_after_adjustments",),
        },
        produces={"output": "ca/business_home_income_limit"},
    ),
    # T2125 Part 7 "Business-use-of-home expenses available to carry forward: Amount 7M
    # minus amount 7N (if negative, enter "0") 7O": the claim left over, 0 when amount 7N is
    # the larger.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/business_home_expenses_available",
            "less": "ca/business_home_income_limit",
        },
        produces={"output": "ca/business_home_carry_forward"},
    ),
    # T2125 Part 7 "Allowable claim: Amount 7M or 7N above, whichever is less (enter your
    # share of this amount on line 9945 of Part 5) 7P".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/business_home_expenses_available",
                "ca/business_home_income_limit",
            ),
        },
        produces={"output": "ca/business_home_allowable_claim"},
    ),
    # T2125 Part 5 "Business-use-of-home expenses (amount 7P)" (line 9945).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/business_home_allowable_claim",),
        },
        produces={"output": "ca/business_home_expenses"},
    ),
    # T2125 Part 5 "Your net income (loss): Amount 5D minus line 9945" (line 9946), "Report
    # the net income amount from line 9946 on the applicable line of your income tax and
    # benefit return as indicated below: business income on line 13500"; T1 "Line 22:
    # Business income" is the same artifact, signed: a loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_net_income_after_adjustments",
            "less": "ca/business_home_expenses",
        },
        produces={"output": "ca/business_income"},
    ),
    # The statement's line code is refused when it is not 1, 2 or 3: a code that names none of the
    # three lines would send the net and the gross of the statement to no line.
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/t2125_line_code_refused"},
        consumes={"count": "ca/business_income_line"},
        produces={"output": "ca/business_income_line_checked"},
    ),
    # Form T2125 "Report the net income amount from line 9946 on the applicable line of your income
    # tax and benefit return as indicated below: business income on line 13500, professional income
    # on line 13700, commission income on line 13900". The statement's code names one of those
    # lines (1 business, 2 professional, 3 commission): each flag is 1 when the code is that line's
    # number, and 0 otherwise.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t2125_line_is_business"},
        consumes={"counts": ("ca/business_income_line_checked",), "amounts": ()},
        produces={"output": "ca/business_line_is_business"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t2125_line_is_professional"},
        consumes={"counts": ("ca/business_income_line_checked",), "amounts": ()},
        produces={"output": "ca/business_line_is_professional"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t2125_line_is_commission"},
        consumes={"counts": ("ca/business_income_line_checked",), "amounts": ()},
        produces={"output": "ca/business_line_is_commission"},
    ),
    # The statement's line 9946 net and line 8299 gross, each times its flag: the amount on the
    # statement's line and 0 on the other two. Nothing is rounded.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/business_income", "count": "ca/business_line_is_business"},
        produces={"output": "ca/net_on_business_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/business_income", "count": "ca/business_line_is_professional"},
        produces={"output": "ca/net_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/business_income", "count": "ca/business_line_is_commission"},
        produces={"output": "ca/net_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/business_gross_income", "count": "ca/business_line_is_business"},
        produces={"output": "ca/gross_on_business_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/business_gross_income",
            "count": "ca/business_line_is_professional",
        },
        produces={"output": "ca/gross_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/business_gross_income", "count": "ca/business_line_is_commission"},
        produces={"output": "ca/gross_on_commission_line"},
    ),
    # Area A endnote 5 answers, taken as a count of 0 or 1: each is checked to be 0 or 1 before
    # the step that reads it. A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/business_epop_associated"},
        produces={"output": "ca/business_epop_associated_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/business_epop_agreement_filed"},
        produces={"output": "ca/business_epop_agreement_filed_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/business_minister_allocation_given"},
        produces={"output": "ca/business_minister_allocation_given_checked"},
    ),
}

INPUTS = frozenset({"ca/t2125_statements"})

FORM_EXPORTS = (
    "ca/net_on_business_line",
    "ca/net_on_professional_line",
    "ca/net_on_commission_line",
    "ca/gross_on_business_line",
    "ca/gross_on_professional_line",
    "ca/gross_on_commission_line",
    "ca/business_closing_ucc",
    "ca/business_home_carry_forward",
    "ca/business_immediate_expensing_claim",
    "ca/business_immediate_expensing_limit_unprorated",
    "ca/business_land_additions",
    "ca/business_land_dispositions",
    "ca/business_liabilities",
    "ca/business_drawings",
    "ca/business_capital_contributions",
    "ca/business_journalism_labour_tax_credit",
)

# T1 lines 13499, 13699 and 13899 "Gross": the gross of each statement on the line of its code,
# totalled over the statements; the return declares them as outputs.
# The form exports Area A column 22 "UCC at the end of the year" (for next year), Part 7 line 7O
# "Business-use-of-home expenses available to carry forward" and Area A line i "Total immediate
# expensing claim for the year", Area F lines 9923 "Total cost of all land additions in the
# year" and 9924 "Total proceeds from all land dispositions in the year", and Part 9 lines 9931
# "Total business liabilities", 9932 "Drawings in the current year" and 9933 "Capital
# contributions in the current year", which are taken as entered and printed: none of them is
# read by a line of the return, so the return declares no output for them (an export nobody
# reads is fine).
OUTPUTS: frozenset[str] = frozenset(
    {
        "ca/gross_business_income",
        "ca/gross_professional_income",
        "ca/gross_commission_income",
    }
)

# T1 line 13500 "Net": the total of the statements' line 9946 net sent to line 13500 by its code.
# T1 lines 13700 and 13900 "Net" are the same totals for the codes 2 and 3.
STEPS = {
    # T1 line 162 (47555) "Canadian journalism labour tax credit (box 236 of all T5013 slips)": the
    # amount 5B of each T2125 statement ("Canadian journalism labour tax credit allocated to you in
    # the year (box 236 of your T5013 slip)"), totalled over the statements. The T1 guide (Line
    # 47555, docs/cra-forms-2025/5000-g-25e.txt): "Include the amount allocated to you by the
    # partnership (box 236 of your T5013 slip) in your business income (line 13500 of the return)
    # in the same tax year." So the credit is the statements' amount 5B, not a caller input.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.business_journalism_labour_tax_credit"},
        produces={"output": "ca/journalism_labour_tax_credit"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_business_income_on_return"},
        produces={"output": "ca/business_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_professional_income_on_return"},
        produces={"output": "ca/professional_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_commission_income_on_return"},
        produces={"output": "ca/commission_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.gross_on_business_line"},
        produces={"output": "ca/gross_business_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.gross_on_professional_line"},
        produces={"output": "ca/gross_professional_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.gross_on_commission_line"},
        produces={"output": "ca/gross_commission_income"},
    ),
}

FORM_WIRING = {
    (
        Subtract,
        frozenset(
            {
                BUSINESS_GROSS_SALES,
                BUSINESS_SALES_ADJUSTMENTS,
            }
        ),
        frozenset({BUSINESS_SALES_SUBTOTAL}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_QUICK_METHOD_GST_HST,
                BUSINESS_QUICK_METHOD_REMITTED,
            }
        ),
        frozenset({BUSINESS_QUICK_METHOD_ASSISTANCE}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_SALES_SUBTOTAL,
                BUSINESS_QUICK_METHOD_ASSISTANCE,
            }
        ),
        frozenset({BUSINESS_ADJUSTED_GROSS_SALES}),
    ),
    (
        CcaVehicleAdditionsChecks,
        frozenset({BUSINESS_CCA_CLASSES, BUSINESS_VEHICLE_SALES_TAX_RATE}),
        frozenset({BUSINESS_CCA_CLASSES_CHECKED}),
    ),
    (
        CcaVehicleProceeds,
        frozenset({BUSINESS_CCA_CLASSES_CHECKED, BUSINESS_VEHICLE_SALES_TAX_RATE}),
        frozenset({BUSINESS_CCA_CLASSES_ADJUSTED}),
    ),
    (
        RecapturedCca,
        frozenset(
            {
                BUSINESS_CCA_CLASSES_ADJUSTED,
            }
        ),
        frozenset({BUSINESS_RECAPTURED_CCA}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_OTHER_INCOME,
                BUSINESS_RECAPTURED_CCA,
            }
        ),
        frozenset({BUSINESS_OTHER_INCOME_WITH_RECAPTURE}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_RESERVES_DEDUCTED_LAST_YEAR,
                BUSINESS_OTHER_INCOME_WITH_RECAPTURE,
            }
        ),
        frozenset({BUSINESS_RESERVES_AND_OTHER_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_ADJUSTED_GROSS_SALES,
                BUSINESS_RESERVES_AND_OTHER_INCOME,
            }
        ),
        frozenset({BUSINESS_GROSS_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_GROSS_INCOME,
            }
        ),
        frozenset({BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_OPENING_INVENTORY,
                BUSINESS_PURCHASES,
                BUSINESS_DIRECT_WAGE_COSTS,
                BUSINESS_SUBCONTRACTS,
                BUSINESS_OTHER_COSTS,
            }
        ),
        frozenset({BUSINESS_COST_OF_GOODS_SUBTOTAL}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_COST_OF_GOODS_SUBTOTAL,
                BUSINESS_CLOSING_INVENTORY,
            }
        ),
        frozenset({BUSINESS_COST_OF_GOODS_SOLD}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT,
                BUSINESS_COST_OF_GOODS_SOLD,
            }
        ),
        frozenset({BUSINESS_GROSS_PROFIT}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_GROSS_PROFIT,
            }
        ),
        frozenset({BUSINESS_GROSS_INCOME_BEFORE_EXPENSES}),
    ),
    (
        FiscalPeriodDaysFromDates,
        frozenset({BUSINESS_FISCAL_PERIOD_FROM, BUSINESS_FISCAL_PERIOD_TO}),
        frozenset({BUSINESS_FISCAL_PERIOD_DAYS}),
    ),
    (
        CcaClaimProrated,
        frozenset({BUSINESS_CCA_CLASSES_ADJUSTED, BUSINESS_FISCAL_PERIOD_DAYS}),
        frozenset({BUSINESS_CCA_TABLE_CLAIM}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_CCA_TABLE_CLAIM,
                BUSINESS_CCA_PERSONAL_PART,
            }
        ),
        frozenset({BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART,
                BUSINESS_HOME_CCA,
            }
        ),
        frozenset({BUSINESS_CCA_CLAIM}),
    ),
    (
        TerminalLoss,
        frozenset(
            {
                BUSINESS_CCA_CLASSES_ADJUSTED,
            }
        ),
        frozenset({BUSINESS_TERMINAL_LOSS}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_OTHER_EXPENSES,
                BUSINESS_TERMINAL_LOSS,
            }
        ),
        frozenset({BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS}),
    ),
    (
        ClosingUccProrated,
        frozenset({BUSINESS_CCA_CLASSES_ADJUSTED, BUSINESS_FISCAL_PERIOD_DAYS}),
        frozenset({BUSINESS_CLOSING_UCC}),
    ),
    (CreditAmount, frozenset(), frozenset({BUSINESS_IMMEDIATE_EXPENSING_CAP})),
    (CreditAmount, frozenset(), frozenset({IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS})),
    (CreditAmount, frozenset(), frozenset({BUSINESS_EPOP_PERCENTAGE_MAXIMUM})),
    (
        ApplyPercentage,
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_CAP, BUSINESS_EPOP_PERCENTAGE}),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_SHARE}),
    ),
    (
        Subtract,
        frozenset({BUSINESS_EPOP_PERCENTAGE_MAXIMUM, BUSINESS_EPOP_PERCENTAGE_TOTAL}),
        frozenset({BUSINESS_EPOP_PERCENTAGE_ROOM}),
    ),
    (
        ChooseBySign,
        frozenset({BUSINESS_EPOP_PERCENTAGE_ROOM, BUSINESS_IMMEDIATE_EXPENSING_SHARE}),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED}),
    ),
    (
        TimesCount,
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED, BUSINESS_EPOP_AGREEMENT_FILED_CHECKED}),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                BUSINESS_EPOP_ASSOCIATED_CHECKED,
                BUSINESS_IMMEDIATE_EXPENSING_CAP,
                BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
            }
        ),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED,
                BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                BUSINESS_MINISTER_ALLOCATION,
            }
        ),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION}),
    ),
    (
        ProratedByFiscalPeriodDays,
        frozenset(
            {
                BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
                BUSINESS_FISCAL_PERIOD_DAYS,
                IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
            }
        ),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED,
                BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                BUSINESS_MINISTER_ALLOCATION,
            }
        ),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED}),
    ),
    (
        SumNotBelowZero,
        frozenset({BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS, BUSINESS_CCA_CLAIM}),
        frozenset({BUSINESS_INCOME_BEFORE_CCA}),
    ),
    (
        ImmediateExpensingClaim,
        frozenset(
            {
                BUSINESS_CCA_CLASSES_ADJUSTED,
                BUSINESS_IMMEDIATE_EXPENSING_LIMIT,
                BUSINESS_INCOME_BEFORE_CCA,
            }
        ),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_CLAIM}),
    ),
    (
        BusinessVehicleExpenses,
        frozenset(
            {BUSINESS_VEHICLES, BUSINESS_VEHICLE_SALES_TAX_RATE, BUSINESS_FISCAL_PERIOD_DAYS}
        ),
        frozenset({BUSINESS_MOTOR_VEHICLE_EXPENSES}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_ADVERTISING,
                BUSINESS_MEALS_AND_ENTERTAINMENT,
                BUSINESS_BAD_DEBTS,
                BUSINESS_INSURANCE,
                BUSINESS_INTEREST_AND_BANK_CHARGES,
                BUSINESS_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,
                BUSINESS_OFFICE_EXPENSES,
                BUSINESS_OFFICE_STATIONERY_AND_SUPPLIES,
                BUSINESS_PROFESSIONAL_FEES,
                BUSINESS_MANAGEMENT_AND_ADMINISTRATION_FEES,
                BUSINESS_RENT,
                BUSINESS_REPAIRS_AND_MAINTENANCE,
                BUSINESS_SALARIES_WAGES_AND_BENEFITS,
                BUSINESS_PROPERTY_TAXES,
                BUSINESS_TRAVEL_EXPENSES,
                BUSINESS_UTILITIES,
                BUSINESS_FUEL_COSTS,
                BUSINESS_DELIVERY_FREIGHT_AND_EXPRESS,
                BUSINESS_MOTOR_VEHICLE_EXPENSES,
                BUSINESS_CCA_CLAIM,
                BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
            }
        ),
        frozenset({BUSINESS_TOTAL_EXPENSES}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
                BUSINESS_TOTAL_EXPENSES,
            }
        ),
        frozenset({BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                BUSINESS_PARTNER_CHECKED,
                BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
                BUSINESS_PARTNER_SHARE,
            }
        ),
        frozenset({BUSINESS_SHARE_OF_NET_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_PARTNER_OTHER_AMOUNT_A,
                BUSINESS_PARTNER_OTHER_AMOUNT_B,
                BUSINESS_PARTNER_OTHER_AMOUNT_C,
                BUSINESS_PARTNER_OTHER_AMOUNT_D,
                BUSINESS_PARTNER_OTHER_AMOUNT_E,
            }
        ),
        frozenset({BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL,
            }
        ),
        frozenset({BUSINESS_PARTNER_OTHER_AMOUNTS}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_SHARE_OF_NET_INCOME,
                BUSINESS_JOURNALISM_LABOUR_TAX_CREDIT,
                BUSINESS_PARTNER_GST_HST_REBATE,
            }
        ),
        frozenset({BUSINESS_PARTNERSHIP_TOTAL}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_PARTNERSHIP_TOTAL,
                BUSINESS_PARTNER_OTHER_AMOUNTS,
            }
        ),
        frozenset({BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_HOME_HEAT,
                BUSINESS_HOME_ELECTRICITY,
                BUSINESS_HOME_INSURANCE,
                BUSINESS_HOME_MAINTENANCE,
                BUSINESS_HOME_MORTGAGE_INTEREST,
                BUSINESS_HOME_PROPERTY_TAXES,
                BUSINESS_HOME_OTHER_EXPENSES,
            }
        ),
        frozenset({BUSINESS_HOME_EXPENSES_SUBTOTAL}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_HOME_EXPENSES_SUBTOTAL,
                BUSINESS_HOME_PERSONAL_USE_PART,
            }
        ),
        frozenset({BUSINESS_HOME_EXPENSES_BUSINESS_PART}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_HOME_EXPENSES_BUSINESS_PART,
                BUSINESS_HOME_CCA,
                BUSINESS_HOME_CARRIED_FORWARD,
            }
        ),
        frozenset({BUSINESS_HOME_EXPENSES_AVAILABLE}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
            }
        ),
        frozenset({BUSINESS_HOME_INCOME_LIMIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                BUSINESS_HOME_EXPENSES_AVAILABLE,
                BUSINESS_HOME_INCOME_LIMIT,
            }
        ),
        frozenset({BUSINESS_HOME_CARRY_FORWARD}),
    ),
    (
        LesserOf,
        frozenset(
            {
                BUSINESS_HOME_EXPENSES_AVAILABLE,
                BUSINESS_HOME_INCOME_LIMIT,
            }
        ),
        frozenset({BUSINESS_HOME_ALLOWABLE_CLAIM}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_HOME_ALLOWABLE_CLAIM,
            }
        ),
        frozenset({BUSINESS_HOME_EXPENSES}),
    ),
    (
        Subtract,
        frozenset(
            {
                BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
                BUSINESS_HOME_EXPENSES,
            }
        ),
        frozenset({BUSINESS_INCOME}),
    ),
    (
        YesOrNoCount,
        frozenset({BUSINESS_EPOP_ASSOCIATED}),
        frozenset({BUSINESS_EPOP_ASSOCIATED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({BUSINESS_EPOP_AGREEMENT_FILED}),
        frozenset({BUSINESS_EPOP_AGREEMENT_FILED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({BUSINESS_MINISTER_ALLOCATION_GIVEN}),
        frozenset({BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({BUSINESS_PARTNER}),
        frozenset({BUSINESS_PARTNER_CHECKED}),
    ),
    (
        CountRefusedByConditions,
        frozenset({BUSINESS_INCOME_LINE}),
        frozenset({BUSINESS_INCOME_LINE_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset({BUSINESS_INCOME_LINE_CHECKED}),
        frozenset({BUSINESS_LINE_IS_BUSINESS}),
    ),
    (
        CountByConditions,
        frozenset({BUSINESS_INCOME_LINE_CHECKED}),
        frozenset({BUSINESS_LINE_IS_PROFESSIONAL}),
    ),
    (
        CountByConditions,
        frozenset({BUSINESS_INCOME_LINE_CHECKED}),
        frozenset({BUSINESS_LINE_IS_COMMISSION}),
    ),
    (
        TimesCount,
        frozenset({BUSINESS_INCOME, BUSINESS_LINE_IS_BUSINESS}),
        frozenset({NET_ON_BUSINESS_LINE}),
    ),
    (
        TimesCount,
        frozenset({BUSINESS_INCOME, BUSINESS_LINE_IS_PROFESSIONAL}),
        frozenset({NET_ON_PROFESSIONAL_LINE}),
    ),
    (
        TimesCount,
        frozenset({BUSINESS_INCOME, BUSINESS_LINE_IS_COMMISSION}),
        frozenset({NET_ON_COMMISSION_LINE}),
    ),
    (
        TimesCount,
        frozenset({BUSINESS_GROSS_INCOME, BUSINESS_LINE_IS_BUSINESS}),
        frozenset({GROSS_ON_BUSINESS_LINE}),
    ),
    (
        TimesCount,
        frozenset({BUSINESS_GROSS_INCOME, BUSINESS_LINE_IS_PROFESSIONAL}),
        frozenset({GROSS_ON_PROFESSIONAL_LINE}),
    ),
    (
        TimesCount,
        frozenset({BUSINESS_GROSS_INCOME, BUSINESS_LINE_IS_COMMISSION}),
        frozenset({GROSS_ON_COMMISSION_LINE}),
    ),
}

WIRING = {
    (
        RecordTotal,
        frozenset({BUSINESS_JOURNALISM_LABOUR_TAX_CREDIT_PER_STATEMENT}),
        frozenset({JOURNALISM_LABOUR_TAX_CREDIT}),
    ),
    (RecordTotal, frozenset({BUSINESS_INCOME_ON_RETURN_LINES}), frozenset({BUSINESS_INCOME})),
    (
        RecordTotal,
        frozenset({PROFESSIONAL_INCOME_ON_RETURN_LINES}),
        frozenset({PROFESSIONAL_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({COMMISSION_INCOME_ON_RETURN_LINES}),
        frozenset({COMMISSION_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({GROSS_ON_BUSINESS_LINE_PER_STATEMENT}),
        frozenset({GROSS_BUSINESS_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({GROSS_ON_PROFESSIONAL_LINE_PER_STATEMENT}),
        frozenset({GROSS_PROFESSIONAL_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({GROSS_ON_COMMISSION_LINE_PER_STATEMENT}),
        frozenset({GROSS_COMMISSION_INCOME}),
    ),
}
