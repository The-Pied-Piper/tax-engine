"""The CA-ON manifest entries of Form T2042 (see `test_manifest.py` and `test_manifest_t2042.py`).

T2042 is a form of the manifest: its 171 selections belong to the form `ca/t2042` (`FORM_STEPS`),
run once for each statement of `ca/t2042_statements`, whose fields are the T2042 inputs
(`FORM_INPUTS`). The form exports the artifacts listed in `FORM_EXPORTS`, each readable by the
other forms as `ca/t2042.<export>`; the return reads one and declares no output for the four
nothing reads (`OUTPUTS` is empty). The return's own entries are the instances input and the total
of the net income over the statements that is T1 line 14100 (`STEPS` and `WIRING`); the form selects
one step over the statement's vehicles, whose printed constants of Charts B and C are datasets.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.capabilities.amount_by_count import AmountForCount
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.capability import CapabilityRegistry
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
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_ab_total import (
    ChartBGrossIncomeAbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_mb_total import (
    ChartBGrossIncomeMbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_nb_total import (
    ChartBGrossIncomeNbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_nl_total import (
    ChartBGrossIncomeNlTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_ns_total import (
    ChartBGrossIncomeNsTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_on_total import (
    ChartBGrossIncomeOnTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_pe_total import (
    ChartBGrossIncomePeTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_sk_total import (
    ChartBGrossIncomeSkTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_ab_total import (
    ChartBSalariesAbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_mb_total import (
    ChartBSalariesMbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_nb_total import (
    ChartBSalariesNbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_nl_total import (
    ChartBSalariesNlTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_ns_total import (
    ChartBSalariesNsTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_on_total import (
    ChartBSalariesOnTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_pe_total import (
    ChartBSalariesPeTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_sk_total import (
    ChartBSalariesSkTotal,
)
from tax_engine.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_prorated import ClosingUccProrated
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.capabilities.fiscal_period_days import FiscalPeriodDays
from tax_engine.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_engine.jurisdictions.ca.capabilities.prorated_by_days_in_period import (
    ProratedByDaysInPeriod,
)
from tax_engine.jurisdictions.ca.capabilities.prorated_by_fiscal_period_days import (
    ProratedByFiscalPeriodDays,
)
from tax_engine.jurisdictions.ca.capabilities.recaptured_cca import RecapturedCca
from tax_engine.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_VEHICLES,
    FARM_ALSO_OUTSIDE_EIGHT,
    FARM_ALSO_OUTSIDE_EIGHT_CHECKED,
    FARM_AMOUNT_8_AB,
    FARM_AMOUNT_8_MB,
    FARM_AMOUNT_8_NB,
    FARM_AMOUNT_8_NL,
    FARM_AMOUNT_8_NS,
    FARM_AMOUNT_8_ON,
    FARM_AMOUNT_8_PE,
    FARM_AMOUNT_8_SK,
    FARM_BARLEY,
    FARM_BUILDING_REPAIRS_AND_MAINTENANCE,
    FARM_CANOLA,
    FARM_CAPITAL_CONTRIBUTIONS,
    FARM_CATTLE,
    FARM_CCA_CLAIM,
    FARM_CCA_CLAIM_LESS_PERSONAL_PART,
    FARM_CCA_CLASSES,
    FARM_CCA_CLASSES_ADJUSTED,
    FARM_CCA_CLASSES_CHECKED,
    FARM_CCA_PERSONAL_PART,
    FARM_CCA_TABLE_CLAIM,
    FARM_CHART_A_AMOUNT_8,
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CHART_A_SUBTOTAL,
    FARM_CHART_B_GROSS_INCOME_AB,
    FARM_CHART_B_GROSS_INCOME_MB,
    FARM_CHART_B_GROSS_INCOME_NB,
    FARM_CHART_B_GROSS_INCOME_NL,
    FARM_CHART_B_GROSS_INCOME_NS,
    FARM_CHART_B_GROSS_INCOME_ON,
    FARM_CHART_B_GROSS_INCOME_PE,
    FARM_CHART_B_GROSS_INCOME_SK,
    FARM_CHART_B_IN_USE,
    FARM_CHART_B_NOTE_9_APPLIES,
    FARM_CHART_B_PROVINCES,
    FARM_CHART_B_ROW_2_WHEN_IN_USE,
    FARM_CHART_B_ROW_3_AB,
    FARM_CHART_B_ROW_3_MB,
    FARM_CHART_B_ROW_3_NB,
    FARM_CHART_B_ROW_3_NL,
    FARM_CHART_B_ROW_3_NS,
    FARM_CHART_B_ROW_3_ON,
    FARM_CHART_B_ROW_3_PE,
    FARM_CHART_B_ROW_3_SK,
    FARM_CHART_B_ROW_5_WHEN_IN_USE,
    FARM_CHART_B_ROW_6_AB,
    FARM_CHART_B_ROW_6_MB,
    FARM_CHART_B_ROW_6_NB,
    FARM_CHART_B_ROW_6_NL,
    FARM_CHART_B_ROW_6_NS,
    FARM_CHART_B_ROW_6_ON,
    FARM_CHART_B_ROW_6_PE,
    FARM_CHART_B_ROW_6_SK,
    FARM_CHART_B_ROW_7_AB,
    FARM_CHART_B_ROW_7_MB,
    FARM_CHART_B_ROW_7_NB,
    FARM_CHART_B_ROW_7_NL,
    FARM_CHART_B_ROW_7_NS,
    FARM_CHART_B_ROW_7_ON,
    FARM_CHART_B_ROW_7_PE,
    FARM_CHART_B_ROW_7_SK,
    FARM_CHART_B_ROW_8_AB,
    FARM_CHART_B_ROW_8_MB,
    FARM_CHART_B_ROW_8_NB,
    FARM_CHART_B_ROW_8_NL,
    FARM_CHART_B_ROW_8_NS,
    FARM_CHART_B_ROW_8_ON,
    FARM_CHART_B_ROW_8_PE,
    FARM_CHART_B_ROW_8_PERCENTAGE,
    FARM_CHART_B_ROW_8_SK,
    FARM_CHART_B_ROW_9_AB,
    FARM_CHART_B_ROW_9_MB,
    FARM_CHART_B_ROW_9_NB,
    FARM_CHART_B_ROW_9_NL,
    FARM_CHART_B_ROW_9_NS,
    FARM_CHART_B_ROW_9_ON,
    FARM_CHART_B_ROW_9_PE,
    FARM_CHART_B_ROW_9_SK,
    FARM_CHART_B_ROW_11_AB,
    FARM_CHART_B_ROW_11_MB,
    FARM_CHART_B_ROW_11_NB,
    FARM_CHART_B_ROW_11_NL,
    FARM_CHART_B_ROW_11_NS,
    FARM_CHART_B_ROW_11_ON,
    FARM_CHART_B_ROW_11_PE,
    FARM_CHART_B_ROW_11_SK,
    FARM_CHART_B_SALARIES_AB,
    FARM_CHART_B_SALARIES_MB,
    FARM_CHART_B_SALARIES_NB,
    FARM_CHART_B_SALARIES_NL,
    FARM_CHART_B_SALARIES_NS,
    FARM_CHART_B_SALARIES_ON,
    FARM_CHART_B_SALARIES_PE,
    FARM_CHART_B_SALARIES_SK,
    FARM_CHART_B_TOTAL_GROSS_INCOME,
    FARM_CHART_B_TOTAL_SALARIES,
    FARM_CHART_C_AMOUNT_AB,
    FARM_CHART_C_AMOUNT_MB,
    FARM_CHART_C_AMOUNT_NB,
    FARM_CHART_C_AMOUNT_NL,
    FARM_CHART_C_AMOUNT_NS,
    FARM_CHART_C_AMOUNT_ON,
    FARM_CHART_C_AMOUNT_PE,
    FARM_CHART_C_AMOUNT_SK,
    FARM_CLEARING_LEVELLING_AND_DRAINING,
    FARM_CLOSING_UCC,
    FARM_CONTAINERS_AND_TWINE,
    FARM_CORN,
    FARM_CROP_INSURANCE,
    FARM_CROP_INSURANCE_PREMIUMS,
    FARM_CUSTOM_WORK,
    FARM_CUSTOM_WORK_EXPENSES,
    FARM_DAIRY_SUBSIDIES,
    FARM_DAYS_IN_2024,
    FARM_DESIGNATED_PROVINCE,
    FARM_DESIGNATED_PROVINCE_CHECKED,
    FARM_DRAWINGS,
    FARM_EGGS,
    FARM_ELECTRICITY,
    FARM_EPOP_AGREEMENT_FILED,
    FARM_EPOP_AGREEMENT_FILED_CHECKED,
    FARM_EPOP_ASSOCIATED,
    FARM_EPOP_ASSOCIATED_CHECKED,
    FARM_EPOP_PERCENTAGE,
    FARM_EPOP_PERCENTAGE_MAXIMUM,
    FARM_EPOP_PERCENTAGE_ROOM,
    FARM_EPOP_PERCENTAGE_TOTAL,
    FARM_EXPENSES_SUBTOTAL,
    FARM_FEED_SUPPLEMENTS_STRAW_AND_BEDDING,
    FARM_FERTILIZERS_AND_LIME,
    FARM_FISCAL_PERIOD_DAYS,
    FARM_FISCAL_PERIOD_DAYS_ENTERED,
    FARM_FLAXSEED,
    FARM_FORAGE_CROPS_OR_SEEDS,
    FARM_FRUIT,
    FARM_FUEL_CHARGE_CREDIT,
    FARM_GASOLINE_DIESEL_AND_OIL,
    FARM_GRAINS_AND_OILSEEDS,
    FARM_GREENHOUSE_AND_NURSERY,
    FARM_GROSS_INCOME,
    FARM_GROSS_INCOME_BEFORE_EXPENSES,
    FARM_HEATING_AND_CURING_FUEL,
    FARM_HOME_ALLOWABLE_CLAIM,
    FARM_HOME_CARRIED_FORWARD,
    FARM_HOME_CARRY_FORWARD,
    FARM_HOME_CCA,
    FARM_HOME_ELECTRICITY,
    FARM_HOME_EXPENSES,
    FARM_HOME_EXPENSES_AVAILABLE,
    FARM_HOME_EXPENSES_BUSINESS_PART,
    FARM_HOME_EXPENSES_SUBTOTAL,
    FARM_HOME_HEAT,
    FARM_HOME_INCOME_LIMIT,
    FARM_HOME_INSURANCE,
    FARM_HOME_MAINTENANCE,
    FARM_HOME_MORTGAGE_INTEREST,
    FARM_HOME_OTHER_EXPENSES,
    FARM_HOME_PERSONAL_USE_PART,
    FARM_HOME_PROPERTY_TAXES,
    FARM_IMMEDIATE_EXPENSING_ALLOCATED,
    FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    FARM_IMMEDIATE_EXPENSING_CAP,
    FARM_IMMEDIATE_EXPENSING_CLAIM,
    FARM_IMMEDIATE_EXPENSING_LIMIT,
    FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    FARM_IMMEDIATE_EXPENSING_SHARE,
    FARM_IN_PROVINCE_AB,
    FARM_IN_PROVINCE_MB,
    FARM_IN_PROVINCE_NB,
    FARM_IN_PROVINCE_NL,
    FARM_IN_PROVINCE_NS,
    FARM_IN_PROVINCE_ON,
    FARM_IN_PROVINCE_PE,
    FARM_IN_PROVINCE_SK,
    FARM_INCOME_BEFORE_CCA,
    FARM_INSURANCE,
    FARM_INSURANCE_PROCEEDS,
    FARM_INSURANCE_PROGRAM_OVERPAYMENT_RECAPTURE,
    FARM_INTEREST_AND_BANK_CHARGES,
    FARM_LAND_ADDITIONS,
    FARM_LAND_DISPOSITIONS,
    FARM_LIABILITIES,
    FARM_LIVESTOCK_AND_ANIMAL_PRODUCTS_REVENUE,
    FARM_LIVESTOCK_PURCHASED,
    FARM_MACHINERY_REPAIRS_LICENCES_AND_INSURANCE,
    FARM_MANDATORY_INVENTORY_ADJUSTMENT_CURRENT_YEAR,
    FARM_MANDATORY_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
    FARM_MILK_AND_CREAM,
    FARM_MINISTER_ALLOCATION,
    FARM_MINISTER_ALLOCATION_GIVEN,
    FARM_MINISTER_ALLOCATION_GIVEN_CHECKED,
    FARM_MIXED_GRAINS,
    FARM_MOTOR_VEHICLE_EXPENSES,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_NON_ARMS_LENGTH_EXPENSES,
    FARM_OATS,
    FARM_OFFICE_EXPENSES,
    FARM_OPTIONAL_INVENTORY_ADJUSTMENT_CURRENT_YEAR,
    FARM_OPTIONAL_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
    FARM_OTHER_COMMODITIES,
    FARM_OTHER_CROPS,
    FARM_OTHER_EXPENSES,
    FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    FARM_OTHER_INCOME,
    FARM_OTHER_INCOME_WITH_RECAPTURE,
    FARM_OTHER_PROGRAM_PAYMENTS,
    FARM_PARTNER,
    FARM_PARTNER_CHECKED,
    FARM_PARTNER_GST_HST_REBATE,
    FARM_PARTNER_OTHER_AMOUNT_A,
    FARM_PARTNER_OTHER_AMOUNT_B,
    FARM_PARTNER_OTHER_AMOUNT_C,
    FARM_PARTNER_OTHER_AMOUNT_D,
    FARM_PARTNER_OTHER_AMOUNT_E,
    FARM_PARTNER_OTHER_AMOUNTS,
    FARM_PARTNER_OTHER_AMOUNTS_TOTAL,
    FARM_PARTNER_SHARE,
    FARM_PARTNERSHIP_TOTAL,
    FARM_PATRONAGE_DIVIDENDS,
    FARM_PESTICIDES,
    FARM_POTATOES,
    FARM_POULTRY,
    FARM_PRESENT_AMOUNT_AB,
    FARM_PRESENT_AMOUNT_MB,
    FARM_PRESENT_AMOUNT_NB,
    FARM_PRESENT_AMOUNT_NL,
    FARM_PRESENT_AMOUNT_NS,
    FARM_PRESENT_AMOUNT_ON,
    FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT,
    FARM_PRESENT_AMOUNT_PE,
    FARM_PRESENT_AMOUNT_SK,
    FARM_PRESENT_IN_PROVINCE_AB,
    FARM_PRESENT_IN_PROVINCE_MB,
    FARM_PRESENT_IN_PROVINCE_NB,
    FARM_PRESENT_IN_PROVINCE_NL,
    FARM_PRESENT_IN_PROVINCE_NS,
    FARM_PRESENT_IN_PROVINCE_ON,
    FARM_PRESENT_IN_PROVINCE_PE,
    FARM_PRESENT_IN_PROVINCE_SK,
    FARM_PRESENT_OUTSIDE_EIGHT,
    FARM_PROFESSIONAL_FEES,
    FARM_PROPERTY_TAXES,
    FARM_QUOTA_ADDITIONS,
    FARM_QUOTA_DISPOSITIONS,
    FARM_REBATES,
    FARM_RECAPTURED_CCA,
    FARM_RENT,
    FARM_SALARIES_WAGES_AND_BENEFITS,
    FARM_SEEDS_AND_PLANTS,
    FARM_SHARE_OF_NET_INCOME,
    FARM_SHEEP_AND_LAMBS,
    FARM_SMALL_TOOLS,
    FARM_SOYBEANS,
    FARM_SWINE,
    FARM_TERMINAL_LOSS,
    FARM_TOBACCO,
    FARM_TOTAL_EXPENSES,
    FARM_VEGETABLES,
    FARM_VEHICLE_SALES_TAX_RATE,
    FARM_VETERINARY_FEES,
    FARM_WHEAT,
    FARMING_INCOME,
    IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
)
from tests.jurisdictions.ca_on.manifest_families.t1139 import FARMING_INCOME_ON_RETURN_LINES

NET_INCOME_PER_STATEMENT = RecordListKind("ca/t2042.farming_income", fields=(FARMING_INCOME,))
# The export of the form ca/farm_loss (the net of the statements, the restricted farm loss added
# back), which T1 line 14100 totals.
FARM_LOSS_INCOME = RecordListKind("ca/farm_loss.farming_income", fields=(FARMING_INCOME,))
FARM_CLOSING_UCC_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_closing_ucc", fields=(FARM_CLOSING_UCC,)
)
FARM_HOME_CARRY_FORWARD_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_home_carry_forward", fields=(FARM_HOME_CARRY_FORWARD,)
)

FARM_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_immediate_expensing_claim", fields=(FARM_IMMEDIATE_EXPENSING_CLAIM,)
)
FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_immediate_expensing_limit_unprorated",
    fields=(FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,),
)
FARM_CHART_A_GROSS_EXPENSES_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_a_gross_expenses", fields=(FARM_CHART_A_GROSS_EXPENSES,)
)
FARM_AMOUNT_8_ON_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_on", fields=(FARM_AMOUNT_8_ON,)
)
FARM_AMOUNT_8_MB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_mb", fields=(FARM_AMOUNT_8_MB,)
)
FARM_AMOUNT_8_SK_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_sk", fields=(FARM_AMOUNT_8_SK,)
)
FARM_AMOUNT_8_AB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_ab", fields=(FARM_AMOUNT_8_AB,)
)
FARM_AMOUNT_8_NS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_ns", fields=(FARM_AMOUNT_8_NS,)
)
FARM_AMOUNT_8_PE_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_pe", fields=(FARM_AMOUNT_8_PE,)
)
FARM_AMOUNT_8_NL_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_nl", fields=(FARM_AMOUNT_8_NL,)
)
FARM_AMOUNT_8_NB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_amount_8_nb", fields=(FARM_AMOUNT_8_NB,)
)

FORM_INPUTS = frozenset(
    {
        "ca/farm_wheat",
        "ca/farm_oats",
        "ca/farm_barley",
        "ca/farm_mixed_grains",
        "ca/farm_corn",
        "ca/farm_canola",
        "ca/farm_flaxseed",
        "ca/farm_soybeans",
        "ca/farm_grains_and_oilseeds",
        "ca/farm_fruit",
        "ca/farm_potatoes",
        "ca/farm_vegetables",
        "ca/farm_tobacco",
        "ca/farm_greenhouse_and_nursery",
        "ca/farm_forage_crops_or_seeds",
        "ca/farm_other_crops",
        "ca/farm_cattle",
        "ca/farm_swine",
        "ca/farm_poultry",
        "ca/farm_sheep_and_lambs",
        "ca/farm_livestock_and_animal_products_revenue",
        "ca/farm_milk_and_cream",
        "ca/farm_eggs",
        "ca/farm_other_commodities",
        "ca/farm_dairy_subsidies",
        "ca/farm_crop_insurance",
        "ca/farm_other_program_payments",
        "ca/farm_rebates",
        "ca/farm_custom_work",
        "ca/farm_insurance_proceeds",
        "ca/farm_patronage_dividends",
        "ca/farm_other_income",
        "ca/farm_containers_and_twine",
        "ca/farm_fertilizers_and_lime",
        "ca/farm_pesticides",
        "ca/farm_seeds_and_plants",
        "ca/farm_feed_supplements_straw_and_bedding",
        "ca/farm_livestock_purchased",
        "ca/farm_veterinary_fees",
        "ca/farm_machinery_repairs_licences_and_insurance",
        "ca/farm_gasoline_diesel_and_oil",
        "ca/farm_building_repairs_and_maintenance",
        "ca/farm_clearing_levelling_and_draining",
        "ca/farm_crop_insurance_premiums",
        "ca/farm_custom_work_expenses",
        "ca/farm_electricity",
        "ca/farm_heating_and_curing_fuel",
        "ca/farm_insurance_program_overpayment_recapture",
        "ca/farm_insurance",
        "ca/farm_interest_and_bank_charges",
        "ca/farm_office_expenses",
        "ca/farm_professional_fees",
        "ca/farm_property_taxes",
        "ca/farm_rent",
        "ca/farm_salaries_wages_and_benefits",
        "ca/business_vehicles",
        "ca/farm_vehicle_sales_tax_rate",
        "ca/farm_small_tools",
        "ca/farm_mandatory_inventory_adjustment_previous_year",
        "ca/farm_optional_inventory_adjustment_previous_year",
        "ca/farm_other_expenses",
        "ca/farm_optional_inventory_adjustment_current_year",
        "ca/farm_mandatory_inventory_adjustment_current_year",
        "ca/farm_cca_personal_part",
        "ca/farm_partner",
        "ca/farm_partner_share",
        "ca/farm_fuel_charge_credit",
        "ca/farm_partner_gst_hst_rebate",
        "ca/farm_partner_other_amount_a",
        "ca/farm_partner_other_amount_b",
        "ca/farm_partner_other_amount_c",
        "ca/farm_partner_other_amount_d",
        "ca/farm_partner_other_amount_e",
        "ca/farm_home_heat",
        "ca/farm_home_electricity",
        "ca/farm_home_insurance",
        "ca/farm_home_maintenance",
        "ca/farm_home_mortgage_interest",
        "ca/farm_home_property_taxes",
        "ca/farm_home_other_expenses",
        "ca/farm_home_personal_use_part",
        "ca/farm_home_cca",
        "ca/farm_home_carried_forward",
        "ca/farm_cca_classes",
        "ca/farm_epop_associated",
        "ca/farm_epop_agreement_filed",
        "ca/farm_epop_percentage",
        "ca/farm_epop_percentage_total",
        "ca/farm_minister_allocation_given",
        "ca/farm_minister_allocation",
        "ca/farm_fiscal_period_days_entered",
        "ca/farm_land_additions",
        "ca/farm_land_dispositions",
        "ca/farm_quota_additions",
        "ca/farm_quota_dispositions",
        "ca/farm_liabilities",
        "ca/farm_drawings",
        "ca/farm_capital_contributions",
        "ca/farm_designated_province",
        "ca/farm_non_arms_length_expenses",
        "ca/farm_days_in_2024",
    }
)

FORM_STEPS = {
    # T2042 Area A endnote 2 "The proceeds of disposition of a zero-emission passenger vehicle
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
            "classes": "ca/farm_cca_classes",
            "sales_tax_rate": "ca/farm_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/farm_cca_classes_checked"},
    ),
    CapabilitySelection(
        name="ca/cca_vehicle_proceeds",
        params={
            "prescribed_amounts": "ca/cca_vehicle_prescribed_amounts",
            "zepv_prescribed_amounts": "ca/cca_zepv_prescribed_amounts",
        },
        consumes={
            "classes": "ca/farm_cca_classes_checked",
            "sales_tax_rate": "ca/farm_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/farm_cca_classes_adjusted"},
    ),
    # T2042 Area A endnote 3 "If you have a negative amount in column 7, add it to income as a
    # recapture in Part 3 on line 9600. If no property is left in the class and there is a
    # positive amount in this column, deduct the amount from income as a terminal loss in Part 4
    # on line 9790.": the recapture of each class of the Area A list (column 7 made positive when
    # negative), totalled.
    CapabilitySelection(
        name="ca/recaptured_cca",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"classes": "ca/farm_cca_classes_adjusted"},
        produces={"output": "ca/farm_recaptured_cca"},
    ),
    # T2042 Part 3 line 9600 "Other income (specify):", which takes the recapture of Area A (the
    # Area A note "add it to income as a recapture in Part 3 on line 9600"): the other income the
    # caller specifies plus the recapture.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_other_income", "ca/farm_recaptured_cca")},
        produces={"output": "ca/farm_other_income_with_recapture"},
    ),
    # T2042 Part 3 "Gross income: Total of the income lines (enter this amount on line 14099 of
    # your income tax and benefit return)" (line 9659): the caller's income lines of Part 3, in
    # the form's order, including the subtotal lines 9370 ("Grains and oilseeds"), 9420 ("Other
    # crops") and 9470 ("Livestock and animal products revenue"), and line 9600 with its recapture.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_wheat",
                "ca/farm_oats",
                "ca/farm_barley",
                "ca/farm_mixed_grains",
                "ca/farm_corn",
                "ca/farm_canola",
                "ca/farm_flaxseed",
                "ca/farm_soybeans",
                "ca/farm_grains_and_oilseeds",
                "ca/farm_fruit",
                "ca/farm_potatoes",
                "ca/farm_vegetables",
                "ca/farm_tobacco",
                "ca/farm_greenhouse_and_nursery",
                "ca/farm_forage_crops_or_seeds",
                "ca/farm_other_crops",
                "ca/farm_cattle",
                "ca/farm_swine",
                "ca/farm_poultry",
                "ca/farm_sheep_and_lambs",
                "ca/farm_livestock_and_animal_products_revenue",
                "ca/farm_milk_and_cream",
                "ca/farm_eggs",
                "ca/farm_other_commodities",
                "ca/farm_dairy_subsidies",
                "ca/farm_crop_insurance",
                "ca/farm_other_program_payments",
                "ca/farm_rebates",
                "ca/farm_custom_work",
                "ca/farm_insurance_proceeds",
                "ca/farm_patronage_dividends",
                "ca/farm_other_income_with_recapture",
            )
        },
        produces={"output": "ca/farm_gross_income"},
    ),
    # T2042 Part 4 "Gross income (line 9659 of Part 3)" (4A): line 9659 alone, the gross income
    # that the expenses are taken from.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_gross_income",)},
        produces={"output": "ca/farm_gross_income_before_expenses"},
    ),
    # T2042 Area A endnote 3 "deduct the amount from income as a terminal loss in Part 4 on line
    # 9790": the terminal loss of each class of the Area A list, totalled.
    CapabilitySelection(
        name="ca/terminal_loss",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"classes": "ca/farm_cca_classes_adjusted"},
        produces={"output": "ca/farm_terminal_loss"},
    ),
    # T2042 Part 4 "Other expenses (specify):" and "Total other expenses (see column 7 of Area A on
    # page 5)" (line 9790): the other expenses the caller specifies plus the terminal loss.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_other_expenses", "ca/farm_terminal_loss")},
        produces={"output": "ca/farm_other_expenses_with_terminal_loss"},
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
            "sales_tax_rate": "ca/farm_vehicle_sales_tax_rate",
            "fiscal_period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_motor_vehicle_expenses"},
    ),
    # T2042 Part 4 "Subtotal of expenses" (4B), "Expenses (enter only the business part)": the
    # expense lines 9661 to 9820, the previous year's inventory adjustments 9937 and 9938, and
    # line 9790, in the form's order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_containers_and_twine",
                "ca/farm_fertilizers_and_lime",
                "ca/farm_pesticides",
                "ca/farm_seeds_and_plants",
                "ca/farm_feed_supplements_straw_and_bedding",
                "ca/farm_livestock_purchased",
                "ca/farm_veterinary_fees",
                "ca/farm_machinery_repairs_licences_and_insurance",
                "ca/farm_gasoline_diesel_and_oil",
                "ca/farm_building_repairs_and_maintenance",
                "ca/farm_clearing_levelling_and_draining",
                "ca/farm_crop_insurance_premiums",
                "ca/farm_custom_work_expenses",
                "ca/farm_electricity",
                "ca/farm_heating_and_curing_fuel",
                "ca/farm_insurance_program_overpayment_recapture",
                "ca/farm_insurance",
                "ca/farm_interest_and_bank_charges",
                "ca/farm_office_expenses",
                "ca/farm_professional_fees",
                "ca/farm_property_taxes",
                "ca/farm_rent",
                "ca/farm_salaries_wages_and_benefits",
                "ca/farm_motor_vehicle_expenses",
                "ca/farm_small_tools",
                "ca/farm_mandatory_inventory_adjustment_previous_year",
                "ca/farm_optional_inventory_adjustment_previous_year",
                "ca/farm_other_expenses_with_terminal_loss",
            )
        },
        produces={"output": "ca/farm_expenses_subtotal"},
    ),
    # T2042 Area A, the days of the fiscal period (Guide T4002 "You were asking?": "Since your
    # fiscal period is less than 365 days, you have to prorate your CCA claim. ... base your CCA
    # claim on the number of days in your fiscal period compared to 365 days. In this case, your
    # fiscal period is 214 days."): the days the caller enters, or the 365 of a full year when none
    # are.
    CapabilitySelection(
        name="ca/fiscal_period_days",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"entered": "ca/farm_fiscal_period_days_entered"},
        produces={"output": "ca/farm_fiscal_period_days"},
    ),
    # T2042 Area A "Total CCA claim for the year: Total of column 21 (enter on line 9936 of Part 4
    # amount ii minus any personal part and any CCA for business-use-of-home expenses)" (amount ii):
    # the CCA claimed on each class of the Area A list, at most its maximum (column 19 multiplied by
    # column 20), totalled.
    CapabilitySelection(
        name="ca/cca_claim_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/farm_cca_classes_adjusted",
            "fiscal_period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_cca_table_claim"},
    ),
    # T2042 Part 4 "Capital cost allowance (CCA). Enter amount ii of Area A minus any personal part
    # and any CCA for business-use-of-home expenses." (line 9936), first step: amount ii minus the
    # personal part of CCA, a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/farm_cca_table_claim", "less": "ca/farm_cca_personal_part"},
        produces={"output": "ca/farm_cca_claim_less_personal_part"},
    ),
    # T2042 Part 4 line 9936 (Capital cost allowance), second step: that result minus the CCA for
    # business-use-of-home expenses, amount 7K "Capital cost allowance (business part only), which
    # means amount ii of Area A minus any portion of capital cost allowance that is for personal use
    # or entered on line 9936 of Part 4", a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/farm_cca_claim_less_personal_part",
            "less": "ca/farm_home_cca",
        },
        produces={"output": "ca/farm_cca_claim"},
    ),
    # T2042 Part 4 "Total farm expenses: Amount 4B plus line 9936" (line 9898): the two added.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_expenses_subtotal", "ca/farm_cca_claim")},
        produces={"output": "ca/farm_total_expenses"},
    ),
    # T2042 Part 4 "Net income (loss) before inventory adjustments: Amount 4A minus line 9898"
    # (line 9899): signed, a loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/farm_gross_income_before_expenses",
            "less": "ca/farm_total_expenses",
        },
        produces={"output": "ca/farm_net_income_before_adjustments"},
    ),
    # T2042 Part 4 "Net income (loss) after inventory adjustments: Total of lines 9899, 9941, and
    # 9942" (4C), with line 9941 "Optional inventory adjustment included in the current year" and
    # line 9942 "Mandatory inventory adjustment included in the current year", both caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_net_income_before_adjustments",
                "ca/farm_optional_inventory_adjustment_current_year",
                "ca/farm_mandatory_inventory_adjustment_current_year",
            )
        },
        produces={"output": "ca/farm_net_income_after_inventory_adjustments"},
    ),
    # T2042 Part 5 "Your share of amount 4C or the amount from your T5013 slip, Statement of
    # Partnership Income" (5A): a count of 1 for a partner chooses the amount from the T5013 slip,
    # as entered; with a count of 0 it is amount 4C.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/farm_partner_checked",
            "when_none": "ca/farm_net_income_after_inventory_adjustments",
            "when_any": "ca/farm_partner_share",
        },
        produces={"output": "ca/farm_share_of_net_income"},
    ),
    # T2042 Part 5 "Total: Amount 5A plus line 9951 plus line 9974" (5B): line 9951 "Return of fuel
    # charge proceeds to farmers tax credit allocated to you in the year" and line 9974 "GST/HST
    # rebate for partners received in the year", both caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_share_of_net_income",
                "ca/farm_fuel_charge_credit",
                "ca/farm_partner_gst_hst_rebate",
            )
        },
        produces={"output": "ca/farm_partnership_total"},
    ),
    # T2042 Part 6 "Total other amounts deductible from your share of the net partnership income
    # (loss): Add amounts 6A to 6E (enter this amount on line 9943 of Part 5)." (6F): 6A to 6E,
    # caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_partner_other_amount_a",
                "ca/farm_partner_other_amount_b",
                "ca/farm_partner_other_amount_c",
                "ca/farm_partner_other_amount_d",
                "ca/farm_partner_other_amount_e",
            )
        },
        produces={"output": "ca/farm_partner_other_amounts_total"},
    ),
    # T2042 Part 5 "Other amounts deductible from your share of net partnership income (loss)
    # (amount 6F)" (line 9943).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_partner_other_amounts_total",)},
        produces={"output": "ca/farm_partner_other_amounts"},
    ),
    # T2042 Part 5 "Net income (loss) after adjustments: Amount 5B minus line 9943" (5C): signed, a
    # loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/farm_partnership_total", "less": "ca/farm_partner_other_amounts"},
        produces={"output": "ca/farm_net_income_after_adjustments"},
    ),
    # T2042 Part 7 "Subtotal: Add amounts 7A to 7G." (7H): 7A "Heat", 7B "Electricity", 7C
    # "Insurance", 7D "Maintenance", 7E "Mortgage interest", 7F "Property taxes" and 7G "Other
    # expenses (specify)", caller inputs.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_home_heat",
                "ca/farm_home_electricity",
                "ca/farm_home_insurance",
                "ca/farm_home_maintenance",
                "ca/farm_home_mortgage_interest",
                "ca/farm_home_property_taxes",
                "ca/farm_home_other_expenses",
            )
        },
        produces={"output": "ca/farm_home_expenses_subtotal"},
    ),
    # T2042 Part 7 "Subtotal: Amount 7H minus amount 7I" (7J): amount 7I "Personal-use part of the
    # business-use-of-home expenses", a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/farm_home_expenses_subtotal",
            "less": "ca/farm_home_personal_use_part",
        },
        produces={"output": "ca/farm_home_expenses_business_part"},
    ),
    # T2042 Part 7 "Subtotal: Add amounts 7J to 7L." (7M): amount 7K and 7L "Amount carried forward
    # from previous year", a caller input.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_home_expenses_business_part",
                "ca/farm_home_cca",
                "ca/farm_home_carried_forward",
            )
        },
        produces={"output": "ca/farm_home_expenses_available"},
    ),
    # T2042 Part 7 "Net income (loss) after adjustments (amount 5C) (if negative, enter "0")." (7N):
    # amount 5C, or 0 when it is negative.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/farm_net_income_after_adjustments",)},
        produces={"output": "ca/farm_home_income_limit"},
    ),
    # T2042 Part 7 "Business-use-of-home expenses available to carry forward: Amount 7M minus amount
    # 7N (if negative, enter "0")" (7O): the claim left over, 0 when amount 7N is the larger.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/farm_home_expenses_available", "less": "ca/farm_home_income_limit"},
        produces={"output": "ca/farm_home_carry_forward"},
    ),
    # T2042 Part 7 "Allowable claim: Amount 7M or 7N above, whichever is less (enter your share of
    # this amount on line 9945 of Part 5)" (7P).
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/farm_home_expenses_available", "ca/farm_home_income_limit")},
        produces={"output": "ca/farm_home_allowable_claim"},
    ),
    # T2042 Part 5 "Business-use-of-home expenses (amount 7P)" (line 9945).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_home_allowable_claim",)},
        produces={"output": "ca/farm_home_expenses"},
    ),
    # T2042 Part 5 "Your net income (loss): Amount 5C minus line 9945 (enter this amount on line
    # 14100 of your income tax and benefit return)" (line 9946): T1 "Line 25: Farming income" and
    # "Line 14100: Net" are the same artifact, signed: a loss is negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/farm_net_income_after_adjustments",
            "less": "ca/farm_home_expenses",
        },
        produces={"output": "ca/farming_income"},
    ),
    # T2042 Area A column 22 "UCC at the end of the year (col. 7 minus col. 21)": the class number
    # and column 22 of each class of the Area A list, a product of the return for next year's
    # column 1.
    CapabilitySelection(
        name="ca/closing_ucc_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/farm_cca_classes_adjusted",
            "fiscal_period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_closing_ucc"},
    ),
    # T2042 Area A endnote 5 "the immediate expensing limit, which is equal to one of the
    # following, whichever is applicable: $1.5 million, if you are not associated with any other
    # eligible person or partnership (EPOP) in the tax year" and Area G "Immediate expensing limit
    # allocated to your business: Multiply $1.5 million by the percentage assigned to your
    # business in column 3**" (amount iv): the printed $1.5 million, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/farm_immediate_expensing_cap"},
        consumes={},
        produces={"output": "ca/farm_immediate_expensing_cap"},
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
    # T2042 Area G "The total of all percentages assigned under the agreement should not be more
    # than 100%. If the total is more than 100%, then the associated group has an immediate
    # expensing limit of zero." and "** If the total of column 3 is more than 100%, enter "0."":
    # the printed 100%, a dataset, as the form prints a percentage (100 for 100%).
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/farm_epop_percentage_maximum"},
        consumes={},
        produces={"output": "ca/farm_epop_percentage_maximum"},
    ),
    # T2042 Area G "Immediate expensing limit allocated to your business: Multiply $1.5 million by
    # the percentage assigned to your business in column 3**" (amount iv), first step: $1.5
    # million times the percentage assigned to your business in column 3, a caller input as the
    # form prints it (40 for 40%).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_immediate_expensing_rounding"},
        consumes={
            "amount": "ca/farm_immediate_expensing_cap",
            "percentage": "ca/farm_epop_percentage",
        },
        produces={"output": "ca/farm_immediate_expensing_share"},
    ),
    # T2042 Area G "** If the total of column 3 is more than 100%, enter "0."", first step: 100%
    # less "Total of percentage assigned: Total of column 3", a caller input; negative when the
    # total is more than 100%.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/farm_epop_percentage_maximum",
            "less": "ca/farm_epop_percentage_total",
        },
        produces={"output": "ca/farm_epop_percentage_room"},
    ),
    # T2042 Area G "Immediate expensing limit allocated to your business: Multiply $1.5 million by
    # the percentage assigned to your business in column 3**" (amount iv) and "** If the total of
    # column 3 is more than 100%, enter "0."": the multiple above when 100% less the total of
    # column 3 is zero or positive, else 0.
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/farm_epop_percentage_room",
            "when_positive": (),
            "when_zero": (),
            "when_negative": (),
            "when_non_positive": (),
            "when_non_negative": ("ca/farm_immediate_expensing_share",),
        },
        produces={"output": "ca/farm_immediate_expensing_allocated"},
    ),
    # T2042 Area A endnote 5 "amount iv of Area G, if you are associated with one or more EPOPs
    # in the tax year" and "zero, if you are associated with one or more EPOPs and an agreement
    # that assigns a percentage to one or more of the associated EPOPs was not filed with the
    # minister in a prescribed form": amount iv times the count of agreements filed (a caller's 0
    # or 1), so 0 when none was filed.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/farm_immediate_expensing_allocated",
            "count": "ca/farm_epop_agreement_filed_checked",
        },
        produces={"output": "ca/farm_immediate_expensing_associated_limit"},
    ),
    # T2042 Area A endnote 5 "the immediate expensing limit, which is equal to one of the
    # following, whichever is applicable": a count of 1 for associated with one or more EPOPs (a
    # caller's 0 or 1) chooses the limit above ("amount iv of Area G" or "zero"); with a count of
    # 0 it is the $1.5 million ("if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year").
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/farm_epop_associated_checked",
            "when_none": "ca/farm_immediate_expensing_cap",
            "when_any": "ca/farm_immediate_expensing_associated_limit",
        },
        produces={"output": "ca/farm_immediate_expensing_limit_before_minister"},
    ),
    # T2042 Note 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": a count of 1 (a caller's 0 or 1) chooses the amount allocated by the minister,
    # as entered, in place of the limit before the days scaling; with a count of 0 the limit before
    # the minister's amount stands. The amount allocated is the amount for the year, and the days
    # scaling below applies to it as it does to the limit.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/farm_minister_allocation_given_checked",
            "when_none": "ca/farm_immediate_expensing_limit_before_minister",
            "when_any": "ca/farm_minister_allocation",
        },
        produces={"output": "ca/farm_immediate_expensing_limit_before_proration"},
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
            "rounding": "ca/farm_immediate_expensing_rounding",
            "class_rates": "ca/cca_class_rates",
        },
        consumes={
            "amount": "ca/farm_immediate_expensing_limit_before_proration",
            "fiscal_period_days": "ca/farm_fiscal_period_days",
            "short_year_days": "ca/immediate_expensing_short_year_days",
        },
        produces={"output": "ca/farm_immediate_expensing_limit"},
    ),
    # T2042 Area A endnote 5 "the immediate expensing limit, which is equal to one of the
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
            "count": "ca/farm_minister_allocation_given_checked",
            "when_none": "ca/farm_immediate_expensing_limit_before_minister",
            "when_any": "ca/farm_minister_allocation",
        },
        produces={"output": "ca/farm_immediate_expensing_limit_unprorated"},
    ),
    # T2042 Area A endnote 5 "the amount of income, if any, earned from the source of income that
    # is a business (before any CCA deductions) in which the relevant DIEP is used for the tax
    # year": line 9899 "Net income (loss) before inventory adjustments" plus line 9936, the CCA it
    # deducted (the recapture on line 9600 is already in gross income and the terminal loss on
    # line 9790 an expense), not below zero. Guide T4002 2025, "Line 9899 or 9369 - Net income
    # (loss) before adjustments": "For business and professional income, use line 9369 on Form
    # T2125. For farming income, use line 9899 on Form T2042. For fishing income, use line 9369 on
    # Form T2121." - the pairing of the figure T2125 and T2121 use for their income before CCA.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/farm_net_income_before_adjustments",
                "ca/farm_cca_claim",
            ),
        },
        produces={"output": "ca/farm_income_before_cca"},
    ),
    # T2042 Area A "Total immediate expensing claim for the year: Total of column 9" (line i) and
    # endnote 5 "The total immediate expensing amount for the tax year (total of column 9) is
    # limited to the lesser of: the immediate expensing limit"; "the UCC of DIEPs in column 8";
    # "the amount of income, if any, earned from the source of income that is a business (before
    # any CCA deductions) in which the relevant DIEP is used for the tax year": the total of
    # column 9 of the Area A list, refused when above the limit or above the income before CCA.
    CapabilitySelection(
        name="ca/immediate_expensing_claim",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/farm_cca_classes_adjusted",
            "immediate_expensing_limit": "ca/farm_immediate_expensing_limit",
            "income_before_cca": "ca/farm_income_before_cca",
        },
        produces={"output": "ca/farm_immediate_expensing_claim"},
    ),
    # Area A endnote 5 answers, taken as a count of 0 or 1: each is checked to be 0 or 1 before
    # the step that reads it. A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/farm_epop_associated"},
        produces={"output": "ca/farm_epop_associated_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/farm_epop_agreement_filed"},
        produces={"output": "ca/farm_epop_agreement_filed_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/farm_minister_allocation_given"},
        produces={"output": "ca/farm_minister_allocation_given_checked"},
    ),
    # Farm partner answer, checked to be 0 or 1 before the step that reads it (in the part
    # `03m_t2042_checks.yaml`). A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/farm_partner"},
        produces={"output": "ca/farm_partner_checked"},
    ),
    # Form T2043 Chart A amount 5 "Subtotal: Add amounts 2 to 4": the mandatory and optional
    # inventory adjustments of the previous year (lines 9937 and 9938 of this statement) and the
    # non-arm's length transactions of Part 4 of this statement.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/farm_mandatory_inventory_adjustment_previous_year",
                "ca/farm_optional_inventory_adjustment_previous_year",
                "ca/farm_non_arms_length_expenses",
            )
        },
        produces={"output": "ca/farm_chart_a_subtotal"},
    ),
    # Form T2043 Chart A amount 6 "Gross farming expenses: Amount 1 minus amount 5": the total
    # farming expenses of line 9898 less amount 5, signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/farm_total_expenses",
            "less": "ca/farm_chart_a_subtotal",
        },
        produces={"output": "ca/farm_chart_a_gross_expenses"},
    ),
    # Form T2043 Chart A amount 8 "Amount 6 multiplied by amount 7.", where amount 7 is "Total
    # number of days in the fiscal period that fall within the 2024 calendar year divided by the
    # total number of days in the fiscal period (if the fiscal period starts and ends in 2025,
    # enter "0")": the gross farming expenses (amount 6) times the days in 2024 over the fiscal
    # period days, one exact fraction rounded half-up to the cent.
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_a_amount_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_a_amount_8"},
    ),
    # The statement's designated province code is refused when it is above 8: a code that names
    # none of the eight provinces of Part 2 (0 is none, a farm elsewhere) is not a code.
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/farm_designated_province_refused"},
        consumes={"count": "ca/farm_designated_province"},
        produces={"output": "ca/farm_designated_province_checked"},
    ),
    # Form T2043 Part 2 lines 2A to 2H, one province each: a count of 1 when the statement's
    # designated province (its Form T2042 province code, 1 to 8) is this province, 0 otherwise.
    # Each province's conditions dataset holds the one condition, read from the count at position
    # 1 (the designated province) and position 2 (no Chart B in use, from the Chart B count of the
    # statement, so a statement that uses Chart B is not counted here); the amount of the province
    # is amount 8 times that count (the next step).
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_on_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_on"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_on"},
        produces={"output": "ca/farm_amount_8_on"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_mb_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_mb"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_mb"},
        produces={"output": "ca/farm_amount_8_mb"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_sk_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_sk"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_sk"},
        produces={"output": "ca/farm_amount_8_sk"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_ab_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_ab"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_ab"},
        produces={"output": "ca/farm_amount_8_ab"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_ns_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_ns"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_ns"},
        produces={"output": "ca/farm_amount_8_ns"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_pe_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_pe"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_pe"},
        produces={"output": "ca/farm_amount_8_pe"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_nl_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_nl"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_nl"},
        produces={"output": "ca/farm_amount_8_nl"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_province_nb_conditions"},
        consumes={
            "counts": ("ca/farm_designated_province_checked", "ca/farm_chart_b_in_use"),
            "amounts": (),
        },
        produces={"output": "ca/farm_in_province_nb"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_a_amount_8", "count": "ca/farm_in_province_nb"},
        produces={"output": "ca/farm_amount_8_nb"},
    ),
}

# The yes or no of the restricted farm loss is the return's, asked once (ca/farm_loss).
INPUTS = frozenset({"ca/t2042_statements", "ca/farm_not_main_source_of_income"})

FORM_EXPORTS = (
    "ca/farming_income",
    "ca/farm_closing_ucc",
    "ca/farm_home_carry_forward",
    "ca/farm_immediate_expensing_claim",
    "ca/farm_immediate_expensing_limit_unprorated",
    "ca/farm_chart_a_gross_expenses",
    "ca/farm_amount_8_on",
    "ca/farm_amount_8_mb",
    "ca/farm_amount_8_sk",
    "ca/farm_amount_8_ab",
    "ca/farm_amount_8_ns",
    "ca/farm_amount_8_pe",
    "ca/farm_amount_8_nl",
    "ca/farm_amount_8_nb",
    "ca/farm_chart_b_gross_income_on",
    "ca/farm_chart_b_gross_income_mb",
    "ca/farm_chart_b_gross_income_sk",
    "ca/farm_chart_b_gross_income_ab",
    "ca/farm_chart_b_gross_income_ns",
    "ca/farm_chart_b_gross_income_pe",
    "ca/farm_chart_b_gross_income_nl",
    "ca/farm_chart_b_gross_income_nb",
    "ca/farm_chart_b_salaries_on",
    "ca/farm_chart_b_salaries_mb",
    "ca/farm_chart_b_salaries_sk",
    "ca/farm_chart_b_salaries_ab",
    "ca/farm_chart_b_salaries_ns",
    "ca/farm_chart_b_salaries_pe",
    "ca/farm_chart_b_salaries_nl",
    "ca/farm_chart_b_salaries_nb",
    "ca/farm_chart_b_row_2_when_in_use",
    "ca/farm_chart_b_row_5_when_in_use",
    "ca/farm_chart_c_amount_on",
    "ca/farm_chart_c_amount_mb",
    "ca/farm_chart_c_amount_sk",
    "ca/farm_chart_c_amount_ab",
    "ca/farm_chart_c_amount_ns",
    "ca/farm_chart_c_amount_pe",
    "ca/farm_chart_c_amount_nl",
    "ca/farm_chart_c_amount_nb",
    "ca/farm_land_additions",
    "ca/farm_land_dispositions",
    "ca/farm_quota_additions",
    "ca/farm_quota_dispositions",
    "ca/farm_liabilities",
    "ca/farm_drawings",
    "ca/farm_capital_contributions",
    # The nine presence amounts of Form T2043 box 67062, one for each place (the eight designated
    # provinces, then outside eight), read by Form T2043 as one record for each statement.
    "ca/farm_present_amount_on",
    "ca/farm_present_amount_mb",
    "ca/farm_present_amount_sk",
    "ca/farm_present_amount_ab",
    "ca/farm_present_amount_ns",
    "ca/farm_present_amount_pe",
    "ca/farm_present_amount_nl",
    "ca/farm_present_amount_nb",
    "ca/farm_present_amount_outside_eight",
    # Line 9951, read by Form T2043 as one record for each statement, totalled and checked against
    # amount 5C.
    "ca/farm_fuel_charge_credit",
)

# The Chart A exports are Form T2043's: the gross farming expenses
# (amount 6) and the amount 8 of each designated province, read by Form T2043 as one record for each
# statement (`ca/t2042.<export>`), not by the return.
# The form exports Area A column 22 "UCC at the end of the year" (for next year), Part 7 line 7O
# "Business-use-of-home expenses available to carry forward", Area A line i "Total immediate
# expensing claim for the year", and Area F and H lines 9923 "Total cost of all land additions in
# the year", 9924 "Total proceeds from all land dispositions in the year", 9929 "Total cost of all
# quota additions in the year" and 9930 "Total proceeds from all quota dispositions in the year",
# which are taken as entered and printed: no line of the return reads them, so the return declares
# no output for them (an export nobody reads is fine). The Part 9 "Details of equity" lines 9931
# "Total business liabilities", 9932 "Drawings in the current year" and 9933 "Capital contributions
# in the current year" are taken as entered and printed, so the return declares no output for them.
OUTPUTS: frozenset[str] = frozenset()

# T1 line 14100 "Net": the total over the statements of the form ca/farm_loss's export.
STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_farming_income_on_return"},
        produces={"output": "ca/farming_income"},
    ),
}

FORM_WIRING = {
    (
        CcaVehicleAdditionsChecks,
        frozenset({FARM_CCA_CLASSES, FARM_VEHICLE_SALES_TAX_RATE}),
        frozenset({FARM_CCA_CLASSES_CHECKED}),
    ),
    (
        CcaVehicleProceeds,
        frozenset({FARM_CCA_CLASSES_CHECKED, FARM_VEHICLE_SALES_TAX_RATE}),
        frozenset({FARM_CCA_CLASSES_ADJUSTED}),
    ),
    (RecapturedCca, frozenset({FARM_CCA_CLASSES_ADJUSTED}), frozenset({FARM_RECAPTURED_CCA})),
    (
        Sum,
        frozenset({FARM_OTHER_INCOME, FARM_RECAPTURED_CCA}),
        frozenset({FARM_OTHER_INCOME_WITH_RECAPTURE}),
    ),
    (
        Sum,
        frozenset(
            {
                FARM_BARLEY,
                FARM_CANOLA,
                FARM_CATTLE,
                FARM_CORN,
                FARM_CROP_INSURANCE,
                FARM_CUSTOM_WORK,
                FARM_DAIRY_SUBSIDIES,
                FARM_EGGS,
                FARM_FLAXSEED,
                FARM_FORAGE_CROPS_OR_SEEDS,
                FARM_FRUIT,
                FARM_GRAINS_AND_OILSEEDS,
                FARM_GREENHOUSE_AND_NURSERY,
                FARM_INSURANCE_PROCEEDS,
                FARM_LIVESTOCK_AND_ANIMAL_PRODUCTS_REVENUE,
                FARM_MILK_AND_CREAM,
                FARM_MIXED_GRAINS,
                FARM_OATS,
                FARM_OTHER_COMMODITIES,
                FARM_OTHER_CROPS,
                FARM_OTHER_INCOME_WITH_RECAPTURE,
                FARM_OTHER_PROGRAM_PAYMENTS,
                FARM_PATRONAGE_DIVIDENDS,
                FARM_POTATOES,
                FARM_POULTRY,
                FARM_REBATES,
                FARM_SHEEP_AND_LAMBS,
                FARM_SOYBEANS,
                FARM_SWINE,
                FARM_TOBACCO,
                FARM_VEGETABLES,
                FARM_WHEAT,
            }
        ),
        frozenset({FARM_GROSS_INCOME}),
    ),
    (Sum, frozenset({FARM_GROSS_INCOME}), frozenset({FARM_GROSS_INCOME_BEFORE_EXPENSES})),
    (TerminalLoss, frozenset({FARM_CCA_CLASSES_ADJUSTED}), frozenset({FARM_TERMINAL_LOSS})),
    (
        Sum,
        frozenset({FARM_OTHER_EXPENSES, FARM_TERMINAL_LOSS}),
        frozenset({FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS}),
    ),
    (
        Sum,
        frozenset(
            {
                FARM_BUILDING_REPAIRS_AND_MAINTENANCE,
                FARM_CLEARING_LEVELLING_AND_DRAINING,
                FARM_CONTAINERS_AND_TWINE,
                FARM_CROP_INSURANCE_PREMIUMS,
                FARM_CUSTOM_WORK_EXPENSES,
                FARM_ELECTRICITY,
                FARM_FEED_SUPPLEMENTS_STRAW_AND_BEDDING,
                FARM_FERTILIZERS_AND_LIME,
                FARM_GASOLINE_DIESEL_AND_OIL,
                FARM_HEATING_AND_CURING_FUEL,
                FARM_INSURANCE,
                FARM_INSURANCE_PROGRAM_OVERPAYMENT_RECAPTURE,
                FARM_INTEREST_AND_BANK_CHARGES,
                FARM_LIVESTOCK_PURCHASED,
                FARM_MACHINERY_REPAIRS_LICENCES_AND_INSURANCE,
                FARM_MANDATORY_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
                FARM_MOTOR_VEHICLE_EXPENSES,
                FARM_OFFICE_EXPENSES,
                FARM_OPTIONAL_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
                FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
                FARM_PESTICIDES,
                FARM_PROFESSIONAL_FEES,
                FARM_PROPERTY_TAXES,
                FARM_RENT,
                FARM_SALARIES_WAGES_AND_BENEFITS,
                FARM_SEEDS_AND_PLANTS,
                FARM_SMALL_TOOLS,
                FARM_VETERINARY_FEES,
            }
        ),
        frozenset({FARM_EXPENSES_SUBTOTAL}),
    ),
    (
        FiscalPeriodDays,
        frozenset({FARM_FISCAL_PERIOD_DAYS_ENTERED}),
        frozenset({FARM_FISCAL_PERIOD_DAYS}),
    ),
    (
        CcaClaimProrated,
        frozenset({FARM_CCA_CLASSES_ADJUSTED, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CCA_TABLE_CLAIM}),
    ),
    (
        Subtract,
        frozenset({FARM_CCA_PERSONAL_PART, FARM_CCA_TABLE_CLAIM}),
        frozenset({FARM_CCA_CLAIM_LESS_PERSONAL_PART}),
    ),
    (
        Subtract,
        frozenset({FARM_CCA_CLAIM_LESS_PERSONAL_PART, FARM_HOME_CCA}),
        frozenset({FARM_CCA_CLAIM}),
    ),
    (Sum, frozenset({FARM_CCA_CLAIM, FARM_EXPENSES_SUBTOTAL}), frozenset({FARM_TOTAL_EXPENSES})),
    (
        Subtract,
        frozenset({FARM_GROSS_INCOME_BEFORE_EXPENSES, FARM_TOTAL_EXPENSES}),
        frozenset({FARM_NET_INCOME_BEFORE_ADJUSTMENTS}),
    ),
    (
        Sum,
        frozenset(
            {
                FARM_MANDATORY_INVENTORY_ADJUSTMENT_CURRENT_YEAR,
                FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
                FARM_OPTIONAL_INVENTORY_ADJUSTMENT_CURRENT_YEAR,
            }
        ),
        frozenset({FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS}),
    ),
    (
        ChooseByCount,
        frozenset(
            {FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS, FARM_PARTNER_CHECKED, FARM_PARTNER_SHARE}
        ),
        frozenset({FARM_SHARE_OF_NET_INCOME}),
    ),
    (
        Sum,
        frozenset({FARM_FUEL_CHARGE_CREDIT, FARM_PARTNER_GST_HST_REBATE, FARM_SHARE_OF_NET_INCOME}),
        frozenset({FARM_PARTNERSHIP_TOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                FARM_PARTNER_OTHER_AMOUNT_A,
                FARM_PARTNER_OTHER_AMOUNT_B,
                FARM_PARTNER_OTHER_AMOUNT_C,
                FARM_PARTNER_OTHER_AMOUNT_D,
                FARM_PARTNER_OTHER_AMOUNT_E,
            }
        ),
        frozenset({FARM_PARTNER_OTHER_AMOUNTS_TOTAL}),
    ),
    (Sum, frozenset({FARM_PARTNER_OTHER_AMOUNTS_TOTAL}), frozenset({FARM_PARTNER_OTHER_AMOUNTS})),
    (
        Subtract,
        frozenset({FARM_PARTNERSHIP_TOTAL, FARM_PARTNER_OTHER_AMOUNTS}),
        frozenset({FARM_NET_INCOME_AFTER_ADJUSTMENTS}),
    ),
    (
        Sum,
        frozenset(
            {
                FARM_HOME_ELECTRICITY,
                FARM_HOME_HEAT,
                FARM_HOME_INSURANCE,
                FARM_HOME_MAINTENANCE,
                FARM_HOME_MORTGAGE_INTEREST,
                FARM_HOME_OTHER_EXPENSES,
                FARM_HOME_PROPERTY_TAXES,
            }
        ),
        frozenset({FARM_HOME_EXPENSES_SUBTOTAL}),
    ),
    (
        Subtract,
        frozenset({FARM_HOME_EXPENSES_SUBTOTAL, FARM_HOME_PERSONAL_USE_PART}),
        frozenset({FARM_HOME_EXPENSES_BUSINESS_PART}),
    ),
    (
        Sum,
        frozenset({FARM_HOME_CARRIED_FORWARD, FARM_HOME_CCA, FARM_HOME_EXPENSES_BUSINESS_PART}),
        frozenset({FARM_HOME_EXPENSES_AVAILABLE}),
    ),
    (
        SumNotBelowZero,
        frozenset({FARM_NET_INCOME_AFTER_ADJUSTMENTS}),
        frozenset({FARM_HOME_INCOME_LIMIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FARM_HOME_EXPENSES_AVAILABLE, FARM_HOME_INCOME_LIMIT}),
        frozenset({FARM_HOME_CARRY_FORWARD}),
    ),
    (
        LesserOf,
        frozenset({FARM_HOME_EXPENSES_AVAILABLE, FARM_HOME_INCOME_LIMIT}),
        frozenset({FARM_HOME_ALLOWABLE_CLAIM}),
    ),
    (Sum, frozenset({FARM_HOME_ALLOWABLE_CLAIM}), frozenset({FARM_HOME_EXPENSES})),
    (
        Subtract,
        frozenset({FARM_HOME_EXPENSES, FARM_NET_INCOME_AFTER_ADJUSTMENTS}),
        frozenset({FARMING_INCOME}),
    ),
    (
        ClosingUccProrated,
        frozenset({FARM_CCA_CLASSES_ADJUSTED, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CLOSING_UCC}),
    ),
    (CreditAmount, frozenset(), frozenset({FARM_IMMEDIATE_EXPENSING_CAP})),
    (CreditAmount, frozenset(), frozenset({IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS})),
    (CreditAmount, frozenset(), frozenset({FARM_EPOP_PERCENTAGE_MAXIMUM})),
    (
        ApplyPercentage,
        frozenset({FARM_IMMEDIATE_EXPENSING_CAP, FARM_EPOP_PERCENTAGE}),
        frozenset({FARM_IMMEDIATE_EXPENSING_SHARE}),
    ),
    (
        Subtract,
        frozenset({FARM_EPOP_PERCENTAGE_MAXIMUM, FARM_EPOP_PERCENTAGE_TOTAL}),
        frozenset({FARM_EPOP_PERCENTAGE_ROOM}),
    ),
    (
        ChooseBySign,
        frozenset({FARM_EPOP_PERCENTAGE_ROOM, FARM_IMMEDIATE_EXPENSING_SHARE}),
        frozenset({FARM_IMMEDIATE_EXPENSING_ALLOCATED}),
    ),
    (
        TimesCount,
        frozenset({FARM_IMMEDIATE_EXPENSING_ALLOCATED, FARM_EPOP_AGREEMENT_FILED_CHECKED}),
        frozenset({FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FARM_EPOP_ASSOCIATED_CHECKED,
                FARM_IMMEDIATE_EXPENSING_CAP,
                FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
            }
        ),
        frozenset({FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FARM_MINISTER_ALLOCATION_GIVEN_CHECKED,
                FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                FARM_MINISTER_ALLOCATION,
            }
        ),
        frozenset({FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION}),
    ),
    (
        ProratedByFiscalPeriodDays,
        frozenset(
            {
                FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
                FARM_FISCAL_PERIOD_DAYS,
                IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
            }
        ),
        frozenset({FARM_IMMEDIATE_EXPENSING_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                FARM_MINISTER_ALLOCATION_GIVEN_CHECKED,
                FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                FARM_MINISTER_ALLOCATION,
            }
        ),
        frozenset({FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED}),
    ),
    (
        SumNotBelowZero,
        frozenset({FARM_NET_INCOME_BEFORE_ADJUSTMENTS, FARM_CCA_CLAIM}),
        frozenset({FARM_INCOME_BEFORE_CCA}),
    ),
    (
        ImmediateExpensingClaim,
        frozenset(
            {FARM_CCA_CLASSES_ADJUSTED, FARM_IMMEDIATE_EXPENSING_LIMIT, FARM_INCOME_BEFORE_CCA}
        ),
        frozenset({FARM_IMMEDIATE_EXPENSING_CLAIM}),
    ),
    (
        BusinessVehicleExpenses,
        frozenset({BUSINESS_VEHICLES, FARM_VEHICLE_SALES_TAX_RATE, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_MOTOR_VEHICLE_EXPENSES}),
    ),
    (
        YesOrNoCount,
        frozenset({FARM_EPOP_ASSOCIATED}),
        frozenset({FARM_EPOP_ASSOCIATED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FARM_EPOP_AGREEMENT_FILED}),
        frozenset({FARM_EPOP_AGREEMENT_FILED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FARM_MINISTER_ALLOCATION_GIVEN}),
        frozenset({FARM_MINISTER_ALLOCATION_GIVEN_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FARM_PARTNER}),
        frozenset({FARM_PARTNER_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                FARM_MANDATORY_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
                FARM_OPTIONAL_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
                FARM_NON_ARMS_LENGTH_EXPENSES,
            }
        ),
        frozenset({FARM_CHART_A_SUBTOTAL}),
    ),
    (
        Subtract,
        frozenset({FARM_TOTAL_EXPENSES, FARM_CHART_A_SUBTOTAL}),
        frozenset({FARM_CHART_A_GROSS_EXPENSES}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_A_AMOUNT_8}),
    ),
    (
        CountRefusedByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE}),
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_ON}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_ON}),
        frozenset({FARM_AMOUNT_8_ON}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_MB}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_MB}),
        frozenset({FARM_AMOUNT_8_MB}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_SK}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_SK}),
        frozenset({FARM_AMOUNT_8_SK}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_AB}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_AB}),
        frozenset({FARM_AMOUNT_8_AB}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_NS}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_NS}),
        frozenset({FARM_AMOUNT_8_NS}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_PE}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_PE}),
        frozenset({FARM_AMOUNT_8_PE}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_NL}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_NL}),
        frozenset({FARM_AMOUNT_8_NL}),
    ),
    (
        CountByConditions,
        frozenset({FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE}),
        frozenset({FARM_IN_PROVINCE_NB}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_A_AMOUNT_8, FARM_IN_PROVINCE_NB}),
        frozenset({FARM_AMOUNT_8_NB}),
    ),
}

WIRING = {
    (RecordTotal, frozenset({FARMING_INCOME_ON_RETURN_LINES}), frozenset({FARMING_INCOME})),
}

PERCENTAGE_OF = CapabilityRegistry.shared().get("ca/percentage_of")


# Form T2043 Chart B and Chart C, once for each statement (a business with permanent establishments
# in more than one province): the rows of Chart B in the form's order, and Chart C's amounts 7 to 14
# (one for each designated province). Row 2 and row 5 are the statement's own lines 9659 and 9814.
FARM_CHART_B_CHART_C_STEPS = {
    # Form T2043 Chart B row 1 "Gross income ($) of the farming business reasonably allocated to the
    # permanent establishment(s) in the designated province (applicable portion of line 9659 of Form
    # T2042, excluding the credit). See note 5.", for each province: the total of the statement's
    # province list (ca/farm_chart_b_provinces) for that province, 0 when it has no row.
    CapabilitySelection(
        name="ca/chart_b_gross_income_on_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_on"},
    ),
    CapabilitySelection(
        name="ca/chart_b_gross_income_mb_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_mb"},
    ),
    CapabilitySelection(
        name="ca/chart_b_gross_income_sk_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_sk"},
    ),
    CapabilitySelection(
        name="ca/chart_b_gross_income_ab_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_ab"},
    ),
    CapabilitySelection(
        name="ca/chart_b_gross_income_ns_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_ns"},
    ),
    CapabilitySelection(
        name="ca/chart_b_gross_income_pe_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_pe"},
    ),
    CapabilitySelection(
        name="ca/chart_b_gross_income_nl_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_nl"},
    ),
    CapabilitySelection(
        name="ca/chart_b_gross_income_nb_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_gross_income_nb"},
    ),
    # Form T2043 Chart B row 4 "Salaries and wages paid ($) to employees of the farming business
    # reasonably allocated to the permanent establishment(s) in the designated province (applicable
    # portion of line 9814 of Form T2042). See note 7.", for each province: the same total of row 4.
    CapabilitySelection(
        name="ca/chart_b_salaries_on_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_on"},
    ),
    CapabilitySelection(
        name="ca/chart_b_salaries_mb_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_mb"},
    ),
    CapabilitySelection(
        name="ca/chart_b_salaries_sk_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_sk"},
    ),
    CapabilitySelection(
        name="ca/chart_b_salaries_ab_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_ab"},
    ),
    CapabilitySelection(
        name="ca/chart_b_salaries_ns_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_ns"},
    ),
    CapabilitySelection(
        name="ca/chart_b_salaries_pe_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_pe"},
    ),
    CapabilitySelection(
        name="ca/chart_b_salaries_nl_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_nl"},
    ),
    CapabilitySelection(
        name="ca/chart_b_salaries_nb_total",
        params={},
        consumes={"provinces": "ca/farm_chart_b_provinces"},
        produces={"output": "ca/farm_chart_b_salaries_nb"},
    ),
    # Form T2043 Chart B row 2 "Total gross income ($) of the farming business in all provinces
    # and territories (line 9659 of Form T2042, excluding the credit)": the line 9659 of the
    # statement.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_gross_income",)},
        produces={"output": "ca/farm_chart_b_total_gross_income"},
    ),
    # Form T2043 Chart B row 5 "Total salaries and wages paid ($) to employees of the farming
    # business in all provinces and territories (line 9814 of Form T2042). See note 8.": line 9814
    # of the statement.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_salaries_wages_and_benefits",)},
        produces={"output": "ca/farm_chart_b_total_salaries"},
    ),
    # Form T2043 Part 3 line 67075 "Total gross income in all provinces and territories from all
    # farming businesses: Add the amount from row 2 of every Chart B you fill in", and line 67076
    # "Total salaries and wages paid to employees in all provinces and territories from all farming
    # businesses: Add the amount from row 5 of every Chart B you fill in": the statement uses Chart
    # B when one of its sixteen totals (rows 1 and 4 of each designated province) is more than 0, 1
    # when one is.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_chart_b_in_use_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/farm_chart_b_gross_income_on",
                "ca/farm_chart_b_gross_income_mb",
                "ca/farm_chart_b_gross_income_sk",
                "ca/farm_chart_b_gross_income_ab",
                "ca/farm_chart_b_gross_income_ns",
                "ca/farm_chart_b_gross_income_pe",
                "ca/farm_chart_b_gross_income_nl",
                "ca/farm_chart_b_gross_income_nb",
                "ca/farm_chart_b_salaries_on",
                "ca/farm_chart_b_salaries_mb",
                "ca/farm_chart_b_salaries_sk",
                "ca/farm_chart_b_salaries_ab",
                "ca/farm_chart_b_salaries_ns",
                "ca/farm_chart_b_salaries_pe",
                "ca/farm_chart_b_salaries_nl",
                "ca/farm_chart_b_salaries_nb",
            ),
        },
        produces={"output": "ca/farm_chart_b_in_use"},
    ),
    # Row 2 and row 5 are counted only when the statement uses Chart B: row 2 times that count.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/farm_chart_b_total_gross_income",
            "count": "ca/farm_chart_b_in_use",
        },
        produces={"output": "ca/farm_chart_b_row_2_when_in_use"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/farm_chart_b_total_salaries", "count": "ca/farm_chart_b_in_use"},
        produces={"output": "ca/farm_chart_b_row_5_when_in_use"},
    ),
    # Form T2043 Chart B note 9 "If either the total gross income from row 2 or the total salaries
    # and wages from row 5 is zero, do not multiply row 7 by 50%.": 1 when either is zero.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_chart_b_note_9_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/farm_chart_b_total_gross_income", "ca/farm_chart_b_total_salaries"),
        },
        produces={"output": "ca/farm_chart_b_note_9_applies"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%.": 50 when note 9 does not apply, 100 when it does.
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/farm_chart_b_row_8_percentage_table"},
        consumes={"count": "ca/farm_chart_b_note_9_applies"},
        produces={"output": "ca/farm_chart_b_row_8_percentage"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (Ontario).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_on",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_on"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (Ontario).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_on",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_on"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6" (Ontario).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_on", "ca/farm_chart_b_row_6_on")},
        produces={"output": "ca/farm_chart_b_row_7_on"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (Ontario).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_on",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_on"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business"
    # (Ontario).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_on",
        },
        produces={"output": "ca/farm_chart_b_row_9_on"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (Ontario).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_on",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_on"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in ON from row 11 of Chart B" times the
    # payment rate (Ontario).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_on"},
        produces={"output": "ca/farm_chart_c_amount_on"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (Manitoba).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_mb",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_mb"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (Manitoba).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_mb",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_mb"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6" (Manitoba).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_mb", "ca/farm_chart_b_row_6_mb")},
        produces={"output": "ca/farm_chart_b_row_7_mb"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (Manitoba).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_mb",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_mb"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business"
    # (Manitoba).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_mb",
        },
        produces={"output": "ca/farm_chart_b_row_9_mb"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (Manitoba).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_mb",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_mb"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in MB from row 11 of Chart B" times the
    # payment rate (Manitoba).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_mb"},
        produces={"output": "ca/farm_chart_c_amount_mb"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (Saskatchewan).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_sk",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_sk"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (Saskatchewan).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_sk",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_sk"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6"
    # (Saskatchewan).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_sk", "ca/farm_chart_b_row_6_sk")},
        produces={"output": "ca/farm_chart_b_row_7_sk"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (Saskatchewan).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_sk",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_sk"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business"
    # (Saskatchewan).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_sk",
        },
        produces={"output": "ca/farm_chart_b_row_9_sk"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (Saskatchewan).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_sk",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_sk"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in SK from row 11 of Chart B" times the
    # payment rate (Saskatchewan).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_sk"},
        produces={"output": "ca/farm_chart_c_amount_sk"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (Alberta).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_ab",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_ab"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (Alberta).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_ab",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_ab"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6" (Alberta).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_ab", "ca/farm_chart_b_row_6_ab")},
        produces={"output": "ca/farm_chart_b_row_7_ab"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (Alberta).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_ab",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_ab"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business"
    # (Alberta).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_ab",
        },
        produces={"output": "ca/farm_chart_b_row_9_ab"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (Alberta).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_ab",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_ab"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in AB from row 11 of Chart B" times the
    # payment rate (Alberta).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_ab"},
        produces={"output": "ca/farm_chart_c_amount_ab"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (Nova Scotia).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_ns",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_ns"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (Nova Scotia).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_ns",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_ns"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6" (Nova Scotia).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_ns", "ca/farm_chart_b_row_6_ns")},
        produces={"output": "ca/farm_chart_b_row_7_ns"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (Nova Scotia).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_ns",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_ns"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business" (Nova
    # Scotia).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_ns",
        },
        produces={"output": "ca/farm_chart_b_row_9_ns"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (Nova Scotia).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_ns",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_ns"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in NS from row 11 of Chart B" times the
    # payment rate (Nova Scotia).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_ns"},
        produces={"output": "ca/farm_chart_c_amount_ns"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (Prince Edward Island).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_pe",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_pe"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (Prince Edward Island).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_pe",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_pe"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6" (Prince Edward
    # Island).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_pe", "ca/farm_chart_b_row_6_pe")},
        produces={"output": "ca/farm_chart_b_row_7_pe"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (Prince Edward Island).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_pe",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_pe"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business" (Prince
    # Edward Island).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_pe",
        },
        produces={"output": "ca/farm_chart_b_row_9_pe"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (Prince Edward Island).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_pe",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_pe"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in PE from row 11 of Chart B" times the
    # payment rate (Prince Edward Island).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_pe"},
        produces={"output": "ca/farm_chart_c_amount_pe"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (Newfoundland and Labrador).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_nl",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_nl"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (Newfoundland and Labrador).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_nl",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_nl"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6" (Newfoundland
    # and Labrador).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_nl", "ca/farm_chart_b_row_6_nl")},
        produces={"output": "ca/farm_chart_b_row_7_nl"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (Newfoundland and Labrador).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_nl",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_nl"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business"
    # (Newfoundland and Labrador).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_nl",
        },
        produces={"output": "ca/farm_chart_b_row_9_nl"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (Newfoundland and Labrador).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_nl",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_nl"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in NL from row 11 of Chart B" times the
    # payment rate (Newfoundland and Labrador).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_nl"},
        produces={"output": "ca/farm_chart_c_amount_nl"},
    ),
    # Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
    # province. Row 1 divided by row 2" (New Brunswick).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_gross_income_nb",
            "divisor": "ca/farm_chart_b_total_gross_income",
        },
        produces={"output": "ca/farm_chart_b_row_3_nb"},
    ),
    # Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the designated
    # province. Row 4 divided by row 5" (New Brunswick).
    CapabilitySelection(
        name="ca/percentage_of",
        params={"rounding": "ca/farm_chart_b_percentage_rounding"},
        consumes={
            "dividend": "ca/farm_chart_b_salaries_nb",
            "divisor": "ca/farm_chart_b_total_salaries",
        },
        produces={"output": "ca/farm_chart_b_row_6_nb"},
    ),
    # Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6" (New
    # Brunswick).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/farm_chart_b_row_3_nb", "ca/farm_chart_b_row_6_nb")},
        produces={"output": "ca/farm_chart_b_row_7_nb"},
    ),
    # Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated province.
    # Row 7 multiplied by 50%. See note 9." (New Brunswick).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_8_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_7_nb",
            "percentage": "ca/farm_chart_b_row_8_percentage",
        },
        produces={"output": "ca/farm_chart_b_row_8_nb"},
    ),
    # Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business allocated to
    # the designated province. Row 8 multiplied by amount 6 of Chart A for this business" (New
    # Brunswick).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/farm_chart_b_row_9_rounding"},
        consumes={
            "amount": "ca/farm_chart_a_gross_expenses",
            "percentage": "ca/farm_chart_b_row_8_nb",
        },
        produces={"output": "ca/farm_chart_b_row_9_nb"},
    ),
    # Form T2043 Chart B rows 10 and 11 "Portion of eligible farming expenses of the farming
    # business allocated to the designated province attributed to the 2024 calendar year. Row 9
    # multiplied by row 10" (New Brunswick).
    CapabilitySelection(
        name="ca/prorated_by_days_in_period",
        params={"rounding": "ca/farm_chart_b_row_11_rounding"},
        consumes={
            "amount": "ca/farm_chart_b_row_9_nb",
            "days": "ca/farm_days_in_2024",
            "period_days": "ca/farm_fiscal_period_days",
        },
        produces={"output": "ca/farm_chart_b_row_11_nb"},
    ),
    # Form T2043 Chart C "Eligible farming expenses in NB from row 11 of Chart B" times the
    # payment rate (New Brunswick).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/fuel_charge_payment_rate"},
        consumes={"base": "ca/farm_chart_b_row_11_nb"},
        produces={"output": "ca/farm_chart_c_amount_nb"},
    ),
}

FARM_CHART_B_CHART_C_WIRING: set[Any] = {
    (
        ChartBGrossIncomeOnTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_ON}),
    ),
    (
        ChartBGrossIncomeMbTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_MB}),
    ),
    (
        ChartBGrossIncomeSkTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_SK}),
    ),
    (
        ChartBGrossIncomeAbTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_AB}),
    ),
    (
        ChartBGrossIncomeNsTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_NS}),
    ),
    (
        ChartBGrossIncomePeTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_PE}),
    ),
    (
        ChartBGrossIncomeNlTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_NL}),
    ),
    (
        ChartBGrossIncomeNbTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_GROSS_INCOME_NB}),
    ),
    (
        ChartBSalariesOnTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_ON}),
    ),
    (
        ChartBSalariesMbTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_MB}),
    ),
    (
        ChartBSalariesSkTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_SK}),
    ),
    (
        ChartBSalariesAbTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_AB}),
    ),
    (
        ChartBSalariesNsTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_NS}),
    ),
    (
        ChartBSalariesPeTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_PE}),
    ),
    (
        ChartBSalariesNlTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_NL}),
    ),
    (
        ChartBSalariesNbTotal,
        frozenset({FARM_CHART_B_PROVINCES}),
        frozenset({FARM_CHART_B_SALARIES_NB}),
    ),
    (Sum, frozenset({FARM_GROSS_INCOME}), frozenset({FARM_CHART_B_TOTAL_GROSS_INCOME})),
    (Sum, frozenset({FARM_SALARIES_WAGES_AND_BENEFITS}), frozenset({FARM_CHART_B_TOTAL_SALARIES})),
    (
        CountByConditions,
        frozenset(
            {
                FARM_CHART_B_GROSS_INCOME_ON,
                FARM_CHART_B_GROSS_INCOME_MB,
                FARM_CHART_B_GROSS_INCOME_SK,
                FARM_CHART_B_GROSS_INCOME_AB,
                FARM_CHART_B_GROSS_INCOME_NS,
                FARM_CHART_B_GROSS_INCOME_PE,
                FARM_CHART_B_GROSS_INCOME_NL,
                FARM_CHART_B_GROSS_INCOME_NB,
                FARM_CHART_B_SALARIES_ON,
                FARM_CHART_B_SALARIES_MB,
                FARM_CHART_B_SALARIES_SK,
                FARM_CHART_B_SALARIES_AB,
                FARM_CHART_B_SALARIES_NS,
                FARM_CHART_B_SALARIES_PE,
                FARM_CHART_B_SALARIES_NL,
                FARM_CHART_B_SALARIES_NB,
            }
        ),
        frozenset({FARM_CHART_B_IN_USE}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_B_TOTAL_GROSS_INCOME, FARM_CHART_B_IN_USE}),
        frozenset({FARM_CHART_B_ROW_2_WHEN_IN_USE}),
    ),
    (
        TimesCount,
        frozenset({FARM_CHART_B_TOTAL_SALARIES, FARM_CHART_B_IN_USE}),
        frozenset({FARM_CHART_B_ROW_5_WHEN_IN_USE}),
    ),
    (
        CountByConditions,
        frozenset({FARM_CHART_B_TOTAL_GROSS_INCOME, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_NOTE_9_APPLIES}),
    ),
    (
        AmountForCount,
        frozenset({FARM_CHART_B_NOTE_9_APPLIES}),
        frozenset({FARM_CHART_B_ROW_8_PERCENTAGE}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_ON, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_ON}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_ON, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_ON}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_ON, FARM_CHART_B_ROW_6_ON}),
        frozenset({FARM_CHART_B_ROW_7_ON}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_ON, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_ON}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_ON}),
        frozenset({FARM_CHART_B_ROW_9_ON}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_ON, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_ON}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_ON}), frozenset({FARM_CHART_C_AMOUNT_ON})),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_MB, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_MB}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_MB, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_MB}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_MB, FARM_CHART_B_ROW_6_MB}),
        frozenset({FARM_CHART_B_ROW_7_MB}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_MB, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_MB}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_MB}),
        frozenset({FARM_CHART_B_ROW_9_MB}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_MB, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_MB}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_MB}), frozenset({FARM_CHART_C_AMOUNT_MB})),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_SK, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_SK}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_SK, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_SK}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_SK, FARM_CHART_B_ROW_6_SK}),
        frozenset({FARM_CHART_B_ROW_7_SK}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_SK, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_SK}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_SK}),
        frozenset({FARM_CHART_B_ROW_9_SK}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_SK, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_SK}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_SK}), frozenset({FARM_CHART_C_AMOUNT_SK})),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_AB, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_AB}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_AB, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_AB}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_AB, FARM_CHART_B_ROW_6_AB}),
        frozenset({FARM_CHART_B_ROW_7_AB}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_AB, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_AB}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_AB}),
        frozenset({FARM_CHART_B_ROW_9_AB}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_AB, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_AB}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_AB}), frozenset({FARM_CHART_C_AMOUNT_AB})),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_NS, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_NS}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_NS, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_NS}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_NS, FARM_CHART_B_ROW_6_NS}),
        frozenset({FARM_CHART_B_ROW_7_NS}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_NS, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_NS}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_NS}),
        frozenset({FARM_CHART_B_ROW_9_NS}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_NS, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_NS}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_NS}), frozenset({FARM_CHART_C_AMOUNT_NS})),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_PE, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_PE}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_PE, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_PE}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_PE, FARM_CHART_B_ROW_6_PE}),
        frozenset({FARM_CHART_B_ROW_7_PE}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_PE, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_PE}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_PE}),
        frozenset({FARM_CHART_B_ROW_9_PE}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_PE, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_PE}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_PE}), frozenset({FARM_CHART_C_AMOUNT_PE})),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_NL, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_NL}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_NL, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_NL}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_NL, FARM_CHART_B_ROW_6_NL}),
        frozenset({FARM_CHART_B_ROW_7_NL}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_NL, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_NL}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_NL}),
        frozenset({FARM_CHART_B_ROW_9_NL}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_NL, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_NL}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_NL}), frozenset({FARM_CHART_C_AMOUNT_NL})),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_GROSS_INCOME_NB, FARM_CHART_B_TOTAL_GROSS_INCOME}),
        frozenset({FARM_CHART_B_ROW_3_NB}),
    ),
    (
        PERCENTAGE_OF,
        frozenset({FARM_CHART_B_SALARIES_NB, FARM_CHART_B_TOTAL_SALARIES}),
        frozenset({FARM_CHART_B_ROW_6_NB}),
    ),
    (
        Sum,
        frozenset({FARM_CHART_B_ROW_3_NB, FARM_CHART_B_ROW_6_NB}),
        frozenset({FARM_CHART_B_ROW_7_NB}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_B_ROW_7_NB, FARM_CHART_B_ROW_8_PERCENTAGE}),
        frozenset({FARM_CHART_B_ROW_8_NB}),
    ),
    (
        ApplyPercentage,
        frozenset({FARM_CHART_A_GROSS_EXPENSES, FARM_CHART_B_ROW_8_NB}),
        frozenset({FARM_CHART_B_ROW_9_NB}),
    ),
    (
        ProratedByDaysInPeriod,
        frozenset({FARM_CHART_B_ROW_9_NB, FARM_DAYS_IN_2024, FARM_FISCAL_PERIOD_DAYS}),
        frozenset({FARM_CHART_B_ROW_11_NB}),
    ),
    (ApplyRate, frozenset({FARM_CHART_B_ROW_11_NB}), frozenset({FARM_CHART_C_AMOUNT_NB})),
}

FARM_CHART_B_GROSS_INCOME_ON_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_on", fields=(FARM_CHART_B_GROSS_INCOME_ON,)
)
FARM_CHART_B_GROSS_INCOME_MB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_mb", fields=(FARM_CHART_B_GROSS_INCOME_MB,)
)
FARM_CHART_B_GROSS_INCOME_SK_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_sk", fields=(FARM_CHART_B_GROSS_INCOME_SK,)
)
FARM_CHART_B_GROSS_INCOME_AB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_ab", fields=(FARM_CHART_B_GROSS_INCOME_AB,)
)
FARM_CHART_B_GROSS_INCOME_NS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_ns", fields=(FARM_CHART_B_GROSS_INCOME_NS,)
)
FARM_CHART_B_GROSS_INCOME_PE_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_pe", fields=(FARM_CHART_B_GROSS_INCOME_PE,)
)
FARM_CHART_B_GROSS_INCOME_NL_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_nl", fields=(FARM_CHART_B_GROSS_INCOME_NL,)
)
FARM_CHART_B_GROSS_INCOME_NB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_gross_income_nb", fields=(FARM_CHART_B_GROSS_INCOME_NB,)
)
FARM_CHART_B_SALARIES_ON_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_on", fields=(FARM_CHART_B_SALARIES_ON,)
)
FARM_CHART_B_SALARIES_MB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_mb", fields=(FARM_CHART_B_SALARIES_MB,)
)
FARM_CHART_B_SALARIES_SK_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_sk", fields=(FARM_CHART_B_SALARIES_SK,)
)
FARM_CHART_B_SALARIES_AB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_ab", fields=(FARM_CHART_B_SALARIES_AB,)
)
FARM_CHART_B_SALARIES_NS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_ns", fields=(FARM_CHART_B_SALARIES_NS,)
)
FARM_CHART_B_SALARIES_PE_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_pe", fields=(FARM_CHART_B_SALARIES_PE,)
)
FARM_CHART_B_SALARIES_NL_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_nl", fields=(FARM_CHART_B_SALARIES_NL,)
)
FARM_CHART_B_SALARIES_NB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_salaries_nb", fields=(FARM_CHART_B_SALARIES_NB,)
)
FARM_CHART_B_ROW_2_WHEN_IN_USE_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_row_2_when_in_use", fields=(FARM_CHART_B_ROW_2_WHEN_IN_USE,)
)
FARM_CHART_B_ROW_5_WHEN_IN_USE_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_b_row_5_when_in_use", fields=(FARM_CHART_B_ROW_5_WHEN_IN_USE,)
)
FARM_CHART_C_AMOUNT_ON_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_on", fields=(FARM_CHART_C_AMOUNT_ON,)
)
FARM_CHART_C_AMOUNT_MB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_mb", fields=(FARM_CHART_C_AMOUNT_MB,)
)
FARM_CHART_C_AMOUNT_SK_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_sk", fields=(FARM_CHART_C_AMOUNT_SK,)
)
FARM_CHART_C_AMOUNT_AB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_ab", fields=(FARM_CHART_C_AMOUNT_AB,)
)
FARM_CHART_C_AMOUNT_NS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_ns", fields=(FARM_CHART_C_AMOUNT_NS,)
)
FARM_CHART_C_AMOUNT_PE_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_pe", fields=(FARM_CHART_C_AMOUNT_PE,)
)
FARM_CHART_C_AMOUNT_NL_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_nl", fields=(FARM_CHART_C_AMOUNT_NL,)
)
FARM_CHART_C_AMOUNT_NB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_chart_c_amount_nb", fields=(FARM_CHART_C_AMOUNT_NB,)
)
FARM_LAND_ADDITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_land_additions", fields=(FARM_LAND_ADDITIONS,)
)
FARM_LAND_DISPOSITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_land_dispositions", fields=(FARM_LAND_DISPOSITIONS,)
)
FARM_QUOTA_ADDITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_quota_additions", fields=(FARM_QUOTA_ADDITIONS,)
)
FARM_QUOTA_DISPOSITIONS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_quota_dispositions", fields=(FARM_QUOTA_DISPOSITIONS,)
)
FARM_LIABILITIES_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_liabilities", fields=(FARM_LIABILITIES,)
)
FARM_DRAWINGS_PER_STATEMENT = RecordListKind("ca/t2042.farm_drawings", fields=(FARM_DRAWINGS,))
FARM_CAPITAL_CONTRIBUTIONS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_capital_contributions", fields=(FARM_CAPITAL_CONTRIBUTIONS,)
)

FORM_STEPS |= FARM_CHART_B_CHART_C_STEPS
FORM_WIRING |= FARM_CHART_B_CHART_C_WIRING

# Form T2043 box 67062 "Tick this box if you have multiple farming businesses with one or more
# permanent establishments in multiple provinces or territories": a statement is present in a place
# when its designated province is that place and no Chart B is in use (the Chart A count of the
# place), or when its Chart B has a row 1 or row 4 amount for that place (the Chart B "in use"
# amounts). The nine places are the eight designated provinces, then outside eight (designated
# province code 0 with no Chart B in use). Each place's count is 1 when the statement is present
# there and 0 otherwise, and its presence amount is the statement counted, "1" (a dataset), once for
# each count of 1: the statement's presence in that place, totalled over the statements by T2043.
PRESENT_IN_PROVINCE_INPUTS = (
    (FARM_IN_PROVINCE_ON, FARM_CHART_B_GROSS_INCOME_ON, FARM_CHART_B_SALARIES_ON),
    (FARM_IN_PROVINCE_MB, FARM_CHART_B_GROSS_INCOME_MB, FARM_CHART_B_SALARIES_MB),
    (FARM_IN_PROVINCE_SK, FARM_CHART_B_GROSS_INCOME_SK, FARM_CHART_B_SALARIES_SK),
    (FARM_IN_PROVINCE_AB, FARM_CHART_B_GROSS_INCOME_AB, FARM_CHART_B_SALARIES_AB),
    (FARM_IN_PROVINCE_NS, FARM_CHART_B_GROSS_INCOME_NS, FARM_CHART_B_SALARIES_NS),
    (FARM_IN_PROVINCE_PE, FARM_CHART_B_GROSS_INCOME_PE, FARM_CHART_B_SALARIES_PE),
    (FARM_IN_PROVINCE_NL, FARM_CHART_B_GROSS_INCOME_NL, FARM_CHART_B_SALARIES_NL),
    (FARM_IN_PROVINCE_NB, FARM_CHART_B_GROSS_INCOME_NB, FARM_CHART_B_SALARIES_NB),
)
PRESENT_IN_PROVINCE_KINDS = (
    FARM_PRESENT_IN_PROVINCE_ON,
    FARM_PRESENT_IN_PROVINCE_MB,
    FARM_PRESENT_IN_PROVINCE_SK,
    FARM_PRESENT_IN_PROVINCE_AB,
    FARM_PRESENT_IN_PROVINCE_NS,
    FARM_PRESENT_IN_PROVINCE_PE,
    FARM_PRESENT_IN_PROVINCE_NL,
    FARM_PRESENT_IN_PROVINCE_NB,
)
PRESENT_AMOUNT_KINDS = (
    FARM_PRESENT_AMOUNT_ON,
    FARM_PRESENT_AMOUNT_MB,
    FARM_PRESENT_AMOUNT_SK,
    FARM_PRESENT_AMOUNT_AB,
    FARM_PRESENT_AMOUNT_NS,
    FARM_PRESENT_AMOUNT_PE,
    FARM_PRESENT_AMOUNT_NL,
    FARM_PRESENT_AMOUNT_NB,
)
# The nine presence amounts of each statement, one record for each statement, read by Form T2043.
FARM_PRESENT_AMOUNT_ON_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_on", fields=(FARM_PRESENT_AMOUNT_ON,)
)
FARM_PRESENT_AMOUNT_MB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_mb", fields=(FARM_PRESENT_AMOUNT_MB,)
)
FARM_PRESENT_AMOUNT_SK_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_sk", fields=(FARM_PRESENT_AMOUNT_SK,)
)
FARM_PRESENT_AMOUNT_AB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_ab", fields=(FARM_PRESENT_AMOUNT_AB,)
)
FARM_PRESENT_AMOUNT_NS_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_ns", fields=(FARM_PRESENT_AMOUNT_NS,)
)
FARM_PRESENT_AMOUNT_PE_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_pe", fields=(FARM_PRESENT_AMOUNT_PE,)
)
FARM_PRESENT_AMOUNT_NL_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_nl", fields=(FARM_PRESENT_AMOUNT_NL,)
)
FARM_PRESENT_AMOUNT_NB_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_nb", fields=(FARM_PRESENT_AMOUNT_NB,)
)
FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_present_amount_outside_eight", fields=(FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT,)
)
# Line 9951 of each statement, one record for each statement, read by Form T2043.
FARM_FUEL_CHARGE_CREDIT_PER_STATEMENT = RecordListKind(
    "ca/t2042.farm_fuel_charge_credit", fields=(FARM_FUEL_CHARGE_CREDIT,)
)

PRESENT_STEPS = {
    # Each province: the count of the statement's conditions (the designated province is the place,
    # with no Chart B in use, or a Chart B row 1 or row 4 amount for it), 1 when any applies.
    *(
        CapabilitySelection(
            name="ca/count_by_conditions",
            params={"conditions": "ca/farm_present_in_province_conditions"},
            consumes={
                "counts": (count.identifier,),
                "amounts": (gross.identifier, salaries.identifier),
            },
            produces={"output": present.identifier},
        )
        for (count, gross, salaries), present in zip(
            PRESENT_IN_PROVINCE_INPUTS, PRESENT_IN_PROVINCE_KINDS, strict=True
        )
    ),
    # Each province: the statement counted, "1", once for each count of 1 (the presence in it).
    *(
        CapabilitySelection(
            name="core/per_unit_amount",
            params={"amount": "ca/farm_statement_counted"},
            consumes={"count": present.identifier},
            produces={"output": amount.identifier},
        )
        for present, amount in zip(PRESENT_IN_PROVINCE_KINDS, PRESENT_AMOUNT_KINDS, strict=True)
    ),
    # The filer's answer that the business also has a permanent establishment outside the eight,
    # checked to be 0 or 1.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": FARM_ALSO_OUTSIDE_EIGHT.identifier},
        produces={"output": FARM_ALSO_OUTSIDE_EIGHT_CHECKED.identifier},
    ),
    # Outside eight: the designated province is code 0 and no Chart B is in use, or the business
    # also has a permanent establishment outside the eight, 1 when either holds.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/farm_present_outside_eight_conditions"},
        consumes={
            "counts": (
                FARM_DESIGNATED_PROVINCE_CHECKED.identifier,
                FARM_CHART_B_IN_USE.identifier,
                FARM_ALSO_OUTSIDE_EIGHT_CHECKED.identifier,
            ),
            "amounts": (),
        },
        produces={"output": FARM_PRESENT_OUTSIDE_EIGHT.identifier},
    ),
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/farm_statement_counted"},
        consumes={"count": FARM_PRESENT_OUTSIDE_EIGHT.identifier},
        produces={"output": FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT.identifier},
    ),
}

PRESENT_WIRING = {
    *(
        (
            CountByConditions,
            frozenset({count, gross, salaries}),
            frozenset({present}),
        )
        for (count, gross, salaries), present in zip(
            PRESENT_IN_PROVINCE_INPUTS, PRESENT_IN_PROVINCE_KINDS, strict=True
        )
    ),
    *(
        (PerUnitAmount, frozenset({present}), frozenset({amount}))
        for present, amount in zip(PRESENT_IN_PROVINCE_KINDS, PRESENT_AMOUNT_KINDS, strict=True)
    ),
    (
        YesOrNoCount,
        frozenset({FARM_ALSO_OUTSIDE_EIGHT}),
        frozenset({FARM_ALSO_OUTSIDE_EIGHT_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset(
            {FARM_DESIGNATED_PROVINCE_CHECKED, FARM_CHART_B_IN_USE, FARM_ALSO_OUTSIDE_EIGHT_CHECKED}
        ),
        frozenset({FARM_PRESENT_OUTSIDE_EIGHT}),
    ),
    (
        PerUnitAmount,
        frozenset({FARM_PRESENT_OUTSIDE_EIGHT}),
        frozenset({FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT}),
    ),
}

FORM_STEPS |= PRESENT_STEPS
FORM_WIRING |= PRESENT_WIRING
FORM_INPUTS = FORM_INPUTS | frozenset(
    [
        # The Chart B province list of the statement, in place of its 16 starting amounts, which
        # the form now computes from it (they stay in FORM_EXPORTS).
        "ca/farm_chart_b_provinces",
        # Whether the business also has a permanent establishment outside the eight designated
        # provinces (Chart B lists only the eight), for box 67062.
        "ca/farm_also_outside_eight",
    ]
)
