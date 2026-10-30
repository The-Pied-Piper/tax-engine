"""The CA-ON manifest entries of Form T776 (see `test_manifest.py` and `test_manifest_t776.py`).

T776 is a form of the manifest: its selections belong to the form `ca/t776` (`FORM_STEPS`), run
once for each statement of `ca/t776_statements`, whose fields are the T776 inputs (`FORM_INPUTS`).
The form exports artifacts, each readable by the other forms as `ca/t776.<export>`
(`FORM_EXPORTS`); the return reads some and declares no output for the ones nothing reads
(`OUTPUTS` is the total of the gross rental income, which no step reads). The return's own entries
are the instances input, the total of the net income over the statements that is T1 line 12600 and
the total of the gross rental income that is T1 line 12599 (`STEPS` and `WIRING`).
"""

from __future__ import annotations

from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities import (
    short_term_rental_non_compliant_cca_by_class as rental_cca,
)
from tax_engine.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_engine.jurisdictions.ca.capabilities.cca_additions_total import CcaAdditionsTotal
from tax_engine.jurisdictions.ca.capabilities.cca_claim_after_column_22_prorated import (
    CcaClaimAfterColumn22Prorated,
)
from tax_engine.jurisdictions.ca.capabilities.cca_opening_ucc_total import CcaOpeningUccTotal
from tax_engine.jurisdictions.ca.capabilities.cca_personal_part_remaining_total import (
    CcaPersonalPartRemainingTotal,
)
from tax_engine.jurisdictions.ca.capabilities.cca_vehicle_additions_checks import (
    CcaVehicleAdditionsChecks,
)
from tax_engine.jurisdictions.ca.capabilities.cca_vehicle_proceeds import CcaVehicleProceeds
from tax_engine.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_after_column_22_prorated import (
    ClosingUccAfterColumn22Prorated,
)
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.capabilities.fiscal_period_days import FiscalPeriodDays
from tax_engine.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_engine.jurisdictions.ca.capabilities.positive_part_of_negation import (
    PositivePartOfNegation,
)
from tax_engine.jurisdictions.ca.capabilities.prorated_by_fiscal_period_days import (
    ProratedByFiscalPeriodDays,
)
from tax_engine.jurisdictions.ca.capabilities.recaptured_cca import RecapturedCca
from tax_engine.jurisdictions.ca.capabilities.rental_additions_total import RentalAdditionsTotal
from tax_engine.jurisdictions.ca.capabilities.rental_gross_rents import RentalGrossRents
from tax_engine.jurisdictions.ca.capabilities.short_term_rental_gross_rents import (
    ShortTermRentalGrossRents,
)
from tax_engine.jurisdictions.ca.capabilities.short_term_rental_non_compliant_cca import (
    ShortTermRentalNonCompliantCca,
)
from tax_engine.jurisdictions.ca.capabilities.short_term_rental_non_compliant_expenses import (
    ShortTermRentalNonCompliantExpenses,
)
from tax_engine.jurisdictions.ca.capabilities.short_term_rental_related_expenses import (
    ShortTermRentalRelatedExpenses,
)
from tax_engine.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    GROSS_RENTAL_INCOME,
    IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
    NET_RENTAL_INCOME,
    RENTAL_ADVERTISING,
    RENTAL_ADVERTISING_PERSONAL_PORTION,
    RENTAL_ADVERTISING_SHORT_TERM_PORTION,
    RENTAL_BUILDING_ADDITIONS,
    RENTAL_BUILDING_ADDITIONS_TOTAL,
    RENTAL_CCA_ADDITIONS_TOTAL,
    RENTAL_CCA_BUSINESS_USE_OF_HOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLAIM_LESS_PERSONAL_PART,
    RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES,
    RENTAL_CCA_CLAIM_SHARE,
    RENTAL_CCA_CLASSES,
    RENTAL_CCA_CLASSES_ADJUSTED,
    RENTAL_CCA_CLASSES_CHECKED,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_OPENING_UCC_TOTAL,
    RENTAL_CCA_PERSONAL_PART,
    RENTAL_CCA_PERSONAL_PART_REMAINING_TOTAL,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CCA_TABLE_RECAPTURE,
    RENTAL_CCA_TABLE_TERMINAL_LOSS,
    RENTAL_CLOSING_UCC,
    RENTAL_COOWNER,
    RENTAL_COOWNER_CCA_CLAIM,
    RENTAL_COOWNER_CCA_CLAIM_CHECKED,
    RENTAL_COOWNER_CHECKED,
    RENTAL_COOWNER_OTHER_EXPENSES,
    RENTAL_COOWNER_RECAPTURED_CCA,
    RENTAL_COOWNER_RECAPTURED_CCA_CHECKED,
    RENTAL_COOWNER_SHARE,
    RENTAL_COOWNER_SHARE_CHECKED,
    RENTAL_COOWNER_SHARE_LOWER_CHECKED,
    RENTAL_COOWNER_TERMINAL_LOSS,
    RENTAL_COOWNER_TERMINAL_LOSS_CHECKED,
    RENTAL_DEDUCTIBLE_EXPENSES,
    RENTAL_EPOP_AGREEMENT_FILED,
    RENTAL_EPOP_AGREEMENT_FILED_CHECKED,
    RENTAL_EPOP_ASSOCIATED,
    RENTAL_EPOP_ASSOCIATED_CHECKED,
    RENTAL_EPOP_PERCENTAGE,
    RENTAL_EPOP_PERCENTAGE_MAXIMUM,
    RENTAL_EPOP_PERCENTAGE_ROOM,
    RENTAL_EPOP_PERCENTAGE_TOTAL,
    RENTAL_EQUIPMENT_ADDITIONS,
    RENTAL_EQUIPMENT_ADDITIONS_TOTAL,
    RENTAL_EXPENSES_LESS_PERSONAL_PORTION,
    RENTAL_FISCAL_PERIOD_DAYS,
    RENTAL_FISCAL_PERIOD_DAYS_ENTERED,
    RENTAL_GROSS_RENTS,
    RENTAL_IMMEDIATE_EXPENSING_ALLOCATED,
    RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    RENTAL_IMMEDIATE_EXPENSING_CAP,
    RENTAL_IMMEDIATE_EXPENSING_CLAIM,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    RENTAL_IMMEDIATE_EXPENSING_SHARE,
    RENTAL_INCOME_BEFORE_CCA,
    RENTAL_INSURANCE,
    RENTAL_INSURANCE_PERSONAL_PORTION,
    RENTAL_INSURANCE_SHORT_TERM_PORTION,
    RENTAL_INTEREST_AND_BANK_CHARGES,
    RENTAL_INTEREST_AND_BANK_CHARGES_PERSONAL_PORTION,
    RENTAL_INTEREST_AND_BANK_CHARGES_SHORT_TERM_PORTION,
    RENTAL_LAND_ADDITIONS,
    RENTAL_LAND_DISPOSITIONS,
    RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES,
    RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_PERSONAL_PORTION,
    RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_SHORT_TERM_PORTION,
    RENTAL_MINISTER_ALLOCATION,
    RENTAL_MINISTER_ALLOCATION_GIVEN,
    RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED,
    RENTAL_MOTOR_VEHICLE_EXPENSES,
    RENTAL_MOTOR_VEHICLE_EXPENSES_PERSONAL_PORTION,
    RENTAL_MOTOR_VEHICLE_EXPENSES_SHORT_TERM_PORTION,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    RENTAL_NET_INCOME_LOSS_SIZE,
    RENTAL_NET_INCOME_LOWER_BOUND,
    RENTAL_NET_INCOME_SHARE,
    RENTAL_NET_INCOME_UPPER_BOUND,
    RENTAL_NET_INCOME_WITH_RECAPTURE,
    RENTAL_NO_CCA_CLAIM,
    RENTAL_NON_COMPLIANT_CCA,
    RENTAL_NON_COMPLIANT_EXPENSES,
    RENTAL_NON_COMPLIANT_EXPENSES_CHECKED,
    RENTAL_OFFICE_EXPENSES,
    RENTAL_OFFICE_EXPENSES_PERSONAL_PORTION,
    RENTAL_OFFICE_EXPENSES_SHORT_TERM_PORTION,
    RENTAL_OTHER_EXPENSES,
    RENTAL_OTHER_EXPENSES_PERSONAL_PORTION,
    RENTAL_OTHER_EXPENSES_SHORT_TERM_PORTION,
    RENTAL_OTHER_INCOME,
    RENTAL_PARTNER,
    RENTAL_PARTNER_AMOUNT_7,
    RENTAL_PARTNER_AMOUNT_7_CONFLICT,
    RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED,
    RENTAL_PARTNER_CHECKED,
    RENTAL_PARTNER_GST_HST_REBATE,
    RENTAL_PARTNER_OTHER_EXPENSES,
    RENTAL_PARTNER_PERCENTAGE,
    RENTAL_PARTNER_PERCENTAGE_CHECKED,
    RENTAL_PARTNER_SHARE,
    RENTAL_PARTNER_SHARE_OF_AMOUNT_6,
    RENTAL_PARTNER_SHARE_WITH_REBATE,
    RENTAL_PARTNER_T5013_SLIP,
    RENTAL_PARTNER_T5013_SLIP_CHECKED,
    RENTAL_PARTNERSHIP_NET_INCOME,
    RENTAL_PERSONAL_PORTION,
    RENTAL_PROFESSIONAL_FEES,
    RENTAL_PROFESSIONAL_FEES_PERSONAL_PORTION,
    RENTAL_PROFESSIONAL_FEES_SHORT_TERM_PORTION,
    RENTAL_PROPERTIES,
    RENTAL_PROPERTY_TAXES,
    RENTAL_PROPERTY_TAXES_PERSONAL_PORTION,
    RENTAL_PROPERTY_TAXES_SHORT_TERM_PORTION,
    RENTAL_RECAPTURED_CCA,
    RENTAL_REPAIRS_AND_MAINTENANCE,
    RENTAL_REPAIRS_AND_MAINTENANCE_PERSONAL_PORTION,
    RENTAL_REPAIRS_AND_MAINTENANCE_SHORT_TERM_PORTION,
    RENTAL_SALARIES_WAGES_AND_BENEFITS,
    RENTAL_SALARIES_WAGES_AND_BENEFITS_PERSONAL_PORTION,
    RENTAL_SALARIES_WAGES_AND_BENEFITS_SHORT_TERM_PORTION,
    RENTAL_SHORT_TERM_PORTION,
    RENTAL_T5013_SLIP_CONFLICT,
    RENTAL_T5013_SLIP_CONFLICT_CHECKED,
    RENTAL_TERMINAL_LOSS,
    RENTAL_TOTAL_EXPENSES,
    RENTAL_TRAVEL,
    RENTAL_TRAVEL_PERSONAL_PORTION,
    RENTAL_TRAVEL_SHORT_TERM_PORTION,
    RENTAL_UTILITIES,
    RENTAL_UTILITIES_PERSONAL_PORTION,
    RENTAL_UTILITIES_SHORT_TERM_PORTION,
    RENTAL_VEHICLE_SALES_TAX_RATE,
    SHORT_TERM_RENTAL_CCA_UNITS,
    SHORT_TERM_RENTAL_GROSS_RENTS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,
    SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL,
    SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL_CHECKED,
    SHORT_TERM_RENTAL_UNITS,
)

NET_RENTAL_INCOME_PER_STATEMENT = RecordListKind(
    "ca/t776.net_rental_income", fields=(NET_RENTAL_INCOME,)
)
GROSS_RENTAL_INCOME_PER_STATEMENT = RecordListKind(
    "ca/t776.gross_rental_income", fields=(GROSS_RENTAL_INCOME,)
)
SHORT_TERM_RENTAL_GROSS_RENTS_PER_STATEMENT = RecordListKind(
    "ca/t776.short_term_rental_gross_rents", fields=(SHORT_TERM_RENTAL_GROSS_RENTS,)
)
RENTAL_SHORT_TERM_PORTION_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_short_term_portion", fields=(RENTAL_SHORT_TERM_PORTION,)
)
RENTAL_CLOSING_UCC_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_closing_ucc", fields=(RENTAL_CLOSING_UCC,)
)
RENTAL_NON_COMPLIANT_CCA_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_non_compliant_cca", fields=(RENTAL_NON_COMPLIANT_CCA,)
)
SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS_PER_STATEMENT = RecordListKind(
    "ca/t776.short_term_rental_non_compliant_cca_by_class",
    fields=(SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,),
)
RENTAL_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_immediate_expensing_claim", fields=(RENTAL_IMMEDIATE_EXPENSING_CLAIM,)
)
RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_immediate_expensing_limit_unprorated",
    fields=(RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,),
)
RENTAL_EQUIPMENT_ADDITIONS_TOTAL_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_equipment_additions_total", fields=(RENTAL_EQUIPMENT_ADDITIONS_TOTAL,)
)
RENTAL_BUILDING_ADDITIONS_TOTAL_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_building_additions_total", fields=(RENTAL_BUILDING_ADDITIONS_TOTAL,)
)
RENTAL_LAND_ADDITIONS_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_land_additions", fields=(RENTAL_LAND_ADDITIONS,)
)
RENTAL_LAND_DISPOSITIONS_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_land_dispositions", fields=(RENTAL_LAND_DISPOSITIONS,)
)
RENTAL_COOWNER_SHARE_LOWER_CHECKED_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_coowner_share_lower_checked",
    fields=(RENTAL_COOWNER_SHARE_LOWER_CHECKED,),
)

RENTAL_T5013_SLIP_CONFLICT_CHECKED_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_t5013_slip_conflict_checked",
    fields=(RENTAL_T5013_SLIP_CONFLICT_CHECKED,),
)
RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_partner_amount_7_conflict_checked",
    fields=(RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED,),
)
RENTAL_INCOME_BEFORE_CCA_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_income_before_cca", fields=(RENTAL_INCOME_BEFORE_CCA,)
)
RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES_PER_STATEMENT = RecordListKind(
    "ca/t776.rental_cca_claim_on_own_properties", fields=(RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES,)
)

FORM_INPUTS = frozenset(
    {
        "ca/rental_properties",
        "ca/rental_other_income",
        "ca/rental_advertising",
        "ca/rental_advertising_personal_portion",
        "ca/rental_advertising_short_term_portion",
        "ca/rental_insurance",
        "ca/rental_insurance_personal_portion",
        "ca/rental_insurance_short_term_portion",
        "ca/rental_interest_and_bank_charges",
        "ca/rental_interest_and_bank_charges_personal_portion",
        "ca/rental_interest_and_bank_charges_short_term_portion",
        "ca/rental_office_expenses",
        "ca/rental_office_expenses_personal_portion",
        "ca/rental_office_expenses_short_term_portion",
        "ca/rental_professional_fees",
        "ca/rental_professional_fees_personal_portion",
        "ca/rental_professional_fees_short_term_portion",
        "ca/rental_management_and_administration_fees",
        "ca/rental_management_and_administration_fees_personal_portion",
        "ca/rental_management_and_administration_fees_short_term_portion",
        "ca/rental_repairs_and_maintenance",
        "ca/rental_repairs_and_maintenance_personal_portion",
        "ca/rental_repairs_and_maintenance_short_term_portion",
        "ca/rental_salaries_wages_and_benefits",
        "ca/rental_salaries_wages_and_benefits_personal_portion",
        "ca/rental_salaries_wages_and_benefits_short_term_portion",
        "ca/rental_property_taxes",
        "ca/rental_property_taxes_personal_portion",
        "ca/rental_property_taxes_short_term_portion",
        "ca/rental_travel",
        "ca/rental_travel_personal_portion",
        "ca/rental_travel_short_term_portion",
        "ca/rental_utilities",
        "ca/rental_utilities_personal_portion",
        "ca/rental_utilities_short_term_portion",
        "ca/rental_motor_vehicle_expenses",
        "ca/rental_motor_vehicle_expenses_personal_portion",
        "ca/rental_motor_vehicle_expenses_short_term_portion",
        "ca/rental_other_expenses",
        "ca/rental_other_expenses_personal_portion",
        "ca/rental_other_expenses_short_term_portion",
        "ca/short_term_rental_units",
        "ca/short_term_rental_cca_units",
        "ca/rental_coowner",
        "ca/rental_coowner_share",
        "ca/rental_coowner_other_expenses",
        "ca/rental_cca_classes",
        "ca/rental_equipment_additions",
        "ca/rental_building_additions",
        "ca/rental_vehicle_sales_tax_rate",
        "ca/rental_fiscal_period_days_entered",
        "ca/rental_land_additions",
        "ca/rental_land_dispositions",
        "ca/rental_coowner_recaptured_cca",
        "ca/rental_coowner_terminal_loss",
        "ca/rental_coowner_cca_claim",
        "ca/rental_cca_personal_part",
        "ca/rental_cca_business_use_of_home",
        "ca/rental_partner",
        "ca/rental_partner_t5013_slip",
        "ca/rental_partner_share",
        "ca/rental_partner_percentage",
        "ca/rental_partner_gst_hst_rebate",
        "ca/rental_partner_other_expenses",
        "ca/rental_epop_associated",
        "ca/rental_epop_agreement_filed",
        "ca/rental_epop_percentage",
        "ca/rental_epop_percentage_total",
        "ca/rental_minister_allocation_given",
        "ca/rental_minister_allocation",
    }
)

FORM_STEPS = {
    # T776 Part 3, "Line 8140: Total of your gross rents for short-term rentals in the
    # year you receive them (add amounts under "Gross rents for short-term rentals")":
    # the total of that column of the rental properties, one row for each property; it
    # feeds no other line.
    CapabilitySelection(
        name="ca/short_term_rental_gross_rents",
        params={},
        consumes={"properties": "ca/rental_properties"},
        produces={"output": "ca/short_term_rental_gross_rents"},
    ),
    # T776 Part 3, "Line 8141: Total of all your gross rents in the year you receive
    # them (add lines under "Gross rents for all units")": the total of that column of
    # the rental properties.
    CapabilitySelection(
        name="ca/rental_gross_rents",
        params={},
        consumes={"properties": "ca/rental_properties"},
        produces={"output": "ca/rental_gross_rents"},
    ),
    # T776 "Line 8299: Total gross rental income: Enter this amount on your income tax
    # and benefit return on line 12599 (line 8141 plus line 8230)"; T1 "Line 12599:
    # Gross".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_gross_rents",
                "ca/rental_other_income",
            )
        },
        produces={"output": "ca/gross_rental_income"},
    ),
    # T776 Part 4, "Line A: Total expenses (add amounts listed under "Total expenses")":
    # the 13 expense lines (8521, 8690, 8710, 8810, 8860, 8871, 8960, 9060, 9180, 9200,
    # 9220, 9281 and 9270), in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_advertising",
                "ca/rental_insurance",
                "ca/rental_interest_and_bank_charges",
                "ca/rental_office_expenses",
                "ca/rental_professional_fees",
                "ca/rental_management_and_administration_fees",
                "ca/rental_repairs_and_maintenance",
                "ca/rental_salaries_wages_and_benefits",
                "ca/rental_property_taxes",
                "ca/rental_travel",
                "ca/rental_utilities",
                "ca/rental_motor_vehicle_expenses",
                "ca/rental_other_expenses",
            )
        },
        produces={"output": "ca/rental_total_expenses"},
    ),
    # T776 "Line 9949: Total for personal portion (add amounts listed under "Personal
    # portion of total expenses")": the same 13 expense lines, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_advertising_personal_portion",
                "ca/rental_insurance_personal_portion",
                "ca/rental_interest_and_bank_charges_personal_portion",
                "ca/rental_office_expenses_personal_portion",
                "ca/rental_professional_fees_personal_portion",
                "ca/rental_management_and_administration_fees_personal_portion",
                "ca/rental_repairs_and_maintenance_personal_portion",
                "ca/rental_salaries_wages_and_benefits_personal_portion",
                "ca/rental_property_taxes_personal_portion",
                "ca/rental_travel_personal_portion",
                "ca/rental_utilities_personal_portion",
                "ca/rental_motor_vehicle_expenses_personal_portion",
                "ca/rental_other_expenses_personal_portion",
            )
        },
        produces={"output": "ca/rental_personal_portion"},
    ),
    # T776 "Line 9365: Total for short-term rental portion (add amounts listed under
    # "Short-term rental portion of total expenses")": the same 13 expense lines, in
    # line order; it feeds no other line (Chart A's column 3 is a starting amount).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_advertising_short_term_portion",
                "ca/rental_insurance_short_term_portion",
                "ca/rental_interest_and_bank_charges_short_term_portion",
                "ca/rental_office_expenses_short_term_portion",
                "ca/rental_professional_fees_short_term_portion",
                "ca/rental_management_and_administration_fees_short_term_portion",
                "ca/rental_repairs_and_maintenance_short_term_portion",
                "ca/rental_salaries_wages_and_benefits_short_term_portion",
                "ca/rental_property_taxes_short_term_portion",
                "ca/rental_travel_short_term_portion",
                "ca/rental_utilities_short_term_portion",
                "ca/rental_motor_vehicle_expenses_short_term_portion",
                "ca/rental_other_expenses_short_term_portion",
            )
        },
        produces={"output": "ca/rental_short_term_portion"},
    ),
    # T776 "Line 9366: Non-compliant amount for short-term rentals (amount B from Chart
    # A)": Chart A's column 3 times column 4 divided by column 5 for each row of
    # short-term rental units, rounded to the cent, and "Line B" the total of column 6.
    CapabilitySelection(
        name="ca/short_term_rental_non_compliant_expenses",
        params={
            "rounding": "ca/short_term_rental_non_compliant_rounding",
        },
        consumes={"units": "ca/short_term_rental_units"},
        produces={"output": "ca/rental_non_compliant_expenses"},
    ),
    # T776 Chart B "Column 7 ***: Non-compliant amount (column 4 multiplied by column 5
    # divided by column 6)" for each row of short-term rental CCA units, rounded to the cent,
    # and "Line C: Total non-compliant amount of CCA for short-term rentals: Total of column 7
    # (enter on line 9367 of Part 4)".
    CapabilitySelection(
        name="ca/short_term_rental_non_compliant_cca",
        params={
            "rounding": "ca/short_term_rental_non_compliant_cca_rounding",
        },
        consumes={"units": "ca/short_term_rental_cca_units"},
        produces={"output": "ca/rental_non_compliant_cca"},
    ),
    # T776 Chart B "*** For each class, add the amounts from column 7 of Chart B and enter each
    # total in column 22 of Area A, in the respective row.": one record for each class, the
    # class number and column 22.
    CapabilitySelection(
        name="ca/short_term_rental_non_compliant_cca_by_class",
        params={
            "rounding": "ca/short_term_rental_non_compliant_cca_rounding",
        },
        consumes={"units": "ca/short_term_rental_cca_units"},
        produces={"output": "ca/short_term_rental_non_compliant_cca_by_class"},
    ),
    # T776 "Line 1: Deductible expenses (amount A minus line 9949 minus line 9366)",
    # first step: amount A minus line 9949.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/rental_total_expenses", "less": "ca/rental_personal_portion"},
        produces={"output": "ca/rental_expenses_less_personal_portion"},
    ),
    # T776 "Line 1: Deductible expenses (amount A minus line 9949 minus line 9366)",
    # second step: that result minus line 9366.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_expenses_less_personal_portion",
            "less": "ca/rental_non_compliant_expenses_checked",
        },
        produces={"output": "ca/rental_deductible_expenses"},
    ),
    # T776 "Line 9369: Net income (loss) before adjustments (total gross rental income
    # from line 8299 minus deductible expenses from amount 1)": signed, a loss is
    # negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/gross_rental_income", "less": "ca/rental_deductible_expenses"},
        produces={"output": "ca/rental_net_income_before_adjustments"},
    ),
    # T776 line 9369 "Net income (loss) before adjustments": the co-owner's share of it (amount 2)
    # is a part of the whole, the same sign and no larger in absolute value. The loss size is the
    # negation of a negative whole (else 0), the upper bound is the whole's positive part (the whole
    # plus the loss size) and the lower bound its negative part (the whole less the upper bound).
    CapabilitySelection(
        name="ca/positive_part_of_negation",
        params={},
        consumes={"amount": "ca/rental_net_income_before_adjustments"},
        produces={"output": "ca/rental_net_income_loss_size"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_net_income_before_adjustments",
                "ca/rental_net_income_loss_size",
            )
        },
        produces={"output": "ca/rental_net_income_upper_bound"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_net_income_before_adjustments",
            "less": "ca/rental_net_income_upper_bound",
        },
        produces={"output": "ca/rental_net_income_lower_bound"},
    ),
    # T776 "Line 2: Co-owners: calculate your share of net income from line 9369. Enter
    # your result on amount 2": the co-owner's share at most the upper bound, refused above it.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_coowner_share",
            "bound": "ca/rental_net_income_upper_bound",
        },
        produces={"output": "ca/rental_coowner_share_checked"},
    ),
    # T776 "Line 2: Co-owners: calculate your share of net income from line 9369. Enter
    # your result on amount 2": the co-owner's share at least the lower bound (a share of a loss
    # is a loss no larger than the whole), refused below it.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_net_income_lower_bound",
            "bound": "ca/rental_coowner_share_checked",
        },
        produces={"output": "ca/rental_coowner_share_lower_checked"},
    ),
    # T776 "Line 2: Co-owners: calculate your share of net income from line 9369. Enter
    # your result on amount 2": a count of 1 for a co-owner (a caller's 0 or 1) chooses
    # the co-owner's share (line 2, as entered); with a count of 0 amount 2 is line
    # 9369.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_coowner_checked",
            "when_none": "ca/rental_net_income_before_adjustments",
            "when_any": "ca/rental_coowner_share_checked",
        },
        produces={"output": "ca/rental_net_income_share"},
    ),
    # T776 "Line 3: Subtotal (amount 2 minus line 9945)": line 9945 is a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_net_income_share",
            "less": "ca/rental_coowner_other_expenses",
        },
        produces={"output": "ca/rental_net_income_after_coowner_expenses"},
    ),
    # T776 Area A, the Class 10.1 cost of additions: "Class 10.1 (30%)", Guide T4002 2025: "The
    # capital cost limits of a Class 10.1 passenger vehicle are the following prescribed amounts:
    # ... $38,000 for vehicles acquired in 2025, plus the GST/HST or PST." The cost of additions of
    # each Class 10.1 row is refused, not capped, when it is more than that amount plus the tax at
    # the sales tax rate the caller enters; the rows are passed on unchanged, before the proceeds
    # are adjusted.
    CapabilitySelection(
        name="ca/cca_vehicle_additions_checks",
        params={"prescribed_amounts": "ca/cca_vehicle_prescribed_amounts"},
        consumes={
            "classes": "ca/rental_cca_classes",
            "sales_tax_rate": "ca/rental_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/rental_cca_classes_checked"},
    ),
    # T776 Area B "Line 9925: Total equipment additions in the year: Total of column 5" (column 5
    # "Rental portion (column 3 minus column 4)") and Area C "Line 9927: Total building additions in
    # the year: Total of column 5": one step for each line, in `03e_t776_additions.yaml`.
    CapabilitySelection(
        name="ca/rental_additions_total",
        params={},
        consumes={"additions": "ca/rental_equipment_additions"},
        produces={"total": "ca/rental_equipment_additions_total"},
    ),
    CapabilitySelection(
        name="ca/rental_additions_total",
        params={},
        consumes={"additions": "ca/rental_building_additions"},
        produces={"total": "ca/rental_building_additions_total"},
    ),
    # T776 Area A Note 2 "The proceeds of disposition of a zero-emission passenger vehicle (ZEPV)
    # that has been included in Class 54, or a passenger vehicle bought after April 18, 2021, that
    # has been included in Class 10.1, and whose cost is more than the prescribed amount will be
    # adjusted based on a factor equal to its prescribed amount as a proportion of the actual cost
    # of the vehicle.": the Area A list with columns 5 and 6 of each such row scaled, which the
    # steps below read in place of the caller's list.
    # Guide T4036 2025, "Class 54 (30%)": "If a zero-emission passenger vehicle is disposed of to a
    # person or partnership with whom you deal at arm's length, and its cost exceeds the prescribed
    # amount ($55,000 for vehicles acquired after March 18, 2019, and before January 1, 2022;
    # $59,000 for vehicles acquired after December 31, 2021, and before January 1, 2023; or $61,000
    # for vehicles acquired after December 31, 2022), the proceeds of disposition will be adjusted
    # based on a factor equal to the prescribed amount as a proportion of the actual cost of the
    # vehicle.": each vehicle sold from a Class 54 row is scaled with the dataset of those amounts.
    CapabilitySelection(
        name="ca/cca_vehicle_proceeds",
        params={
            "prescribed_amounts": "ca/cca_vehicle_prescribed_amounts",
            "zepv_prescribed_amounts": "ca/cca_zepv_prescribed_amounts",
        },
        consumes={
            "classes": "ca/rental_cca_classes_checked",
            "sales_tax_rate": "ca/rental_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/rental_cca_classes_adjusted"},
    ),
    # T776 Area A "Line ii: Total CCA claim for the year *: Total of column 23" and Note 3 "If you
    # have a negative amount in column 7, add it to income as a recapture under "Recaptured
    # capital cost allowance" on line 9947": the recapture of each class of the Area A list
    # (column 7 made positive when negative), totalled.
    CapabilitySelection(
        name="ca/recaptured_cca",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"classes": "ca/rental_cca_classes_adjusted"},
        produces={"output": "ca/rental_cca_table_recapture"},
    ),
    # T776 "Line 9947: Recaptured capital cost allowance (co-owners: enter your share of the
    # amount)": the co-owner's share at most the recapture of Area A, refused above it.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_coowner_recaptured_cca",
            "bound": "ca/rental_cca_table_recapture",
        },
        produces={"output": "ca/rental_coowner_recaptured_cca_checked"},
    ),
    # T776 "Line 9947: Recaptured capital cost allowance (co-owners: enter your share of the
    # amount)": a count of 1 for a co-owner (a caller's 0 or 1) chooses the co-owner's share, as
    # entered; with a count of 0 line 9947 is the recapture of Area A.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_coowner_checked",
            "when_none": "ca/rental_cca_table_recapture",
            "when_any": "ca/rental_coowner_recaptured_cca_checked",
        },
        produces={"output": "ca/rental_recaptured_cca"},
    ),
    # T776 "Line 4: Subtotal (amount 3 plus line 9947)": line 9947 is computed from Area A.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_net_income_after_coowner_expenses",
                "ca/rental_recaptured_cca",
            )
        },
        produces={"output": "ca/rental_net_income_with_recapture"},
    ),
    # T776 Area A Note 3 "If no property is left in the class and there is a positive amount in
    # this column, deduct the amount from your income as a terminal loss under "Terminal loss" on
    # line 9948. Recapture and terminal loss do not apply to a Class 10.1 property unless it is a
    # DIEP": the terminal loss of each class of the Area A list, totalled.
    CapabilitySelection(
        name="ca/terminal_loss",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"classes": "ca/rental_cca_classes_adjusted"},
        produces={"output": "ca/rental_cca_table_terminal_loss"},
    ),
    # T776 "Line 9948: Terminal loss (co-owners: enter your share of the amount)": the co-owner's
    # share at most the terminal loss of Area A, refused above it.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_coowner_terminal_loss",
            "bound": "ca/rental_cca_table_terminal_loss",
        },
        produces={"output": "ca/rental_coowner_terminal_loss_checked"},
    ),
    # T776 "Line 9948: Terminal loss (co-owners: enter your share of the amount)": a count of 1
    # for a co-owner chooses the co-owner's share, as entered; with a count of 0 line 9948 is the
    # terminal loss of Area A.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_coowner_checked",
            "when_none": "ca/rental_cca_table_terminal_loss",
            "when_any": "ca/rental_coowner_terminal_loss_checked",
        },
        produces={"output": "ca/rental_terminal_loss"},
    ),
    # T776 "Line 5: Subtotal (amount 4 minus line 9948)": line 9948 is computed from Area A.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_net_income_with_recapture",
            "less": "ca/rental_terminal_loss",
        },
        produces={"output": "ca/rental_net_income_after_terminal_loss"},
    ),
    # T776 Part 1 "Fiscal period from Date (Year/Month/Day) to (Year/12/31)", the days of the
    # rental's fiscal period (Guide T4036, Area A "Column 23 – CCA claim for the year": "In your
    # first year of rental activities, you may have to prorate your CCA claim."; Guide T4002 "You
    # were asking?": "base your CCA claim on the number of days in your fiscal period compared to
    # 365 days."): the days the caller enters, or the 365 of a full year when none are.
    CapabilitySelection(
        name="ca/fiscal_period_days",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={"entered": "ca/rental_fiscal_period_days_entered"},
        produces={"output": "ca/rental_fiscal_period_days"},
    ),
    # T776 Area A "Line ii: Total CCA claim for the year *: Total of column 23": the CCA claimed
    # on each class of the Area A list, at most its maximum (column 19 multiplied by column 20)
    # less its column 22 (the Chart B total of the class), totalled, each maximum prorated by the
    # days of the fiscal period.
    CapabilitySelection(
        name="ca/cca_claim_after_column_22_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/rental_cca_classes_adjusted",
            "non_compliant": "ca/short_term_rental_non_compliant_cca_by_class",
            "fiscal_period_days": "ca/rental_fiscal_period_days",
        },
        produces={"output": "ca/rental_cca_table_claim"},
    ),
    # T776 Area A "* Sole proprietors and partnerships: Enter the total CCA claim for the year
    # from amount ii on line 9936. Co-owners: Enter only your share of the total CCA claim for
    # the year from amount ii on line 9936": the co-owner's share at most amount ii, refused above.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_coowner_cca_claim",
            "bound": "ca/rental_cca_table_claim",
        },
        produces={"output": "ca/rental_coowner_cca_claim_checked"},
    ),
    # T776 Area A "* Sole proprietors and partnerships: Enter the total CCA claim for the year
    # from amount ii on line 9936. Co-owners: Enter only your share of the total CCA claim for
    # the year from amount ii on line 9936": a count of 1 for a co-owner chooses the co-owner's
    # share, as entered; with a count of 0 it is amount ii.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_coowner_checked",
            "when_none": "ca/rental_cca_table_claim",
            "when_any": "ca/rental_coowner_cca_claim_checked",
        },
        produces={"output": "ca/rental_cca_claim_share"},
    ),
    # T776 "Line 9936: Total CCA claim for the year (amount ii from Area A minus any personal
    # part of CCA, and any CCA for business-use-of home expenses)", first step: amount ii minus
    # the checked personal part of CCA.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_cca_claim_share",
            "less": "ca/rental_cca_personal_part",
        },
        produces={"output": "ca/rental_cca_claim_less_personal_part"},
    ),
    # T776 "Line 9936: Total CCA claim for the year (amount ii from Area A minus any personal
    # part of CCA, and any CCA for business-use-of home expenses)", second step: that result
    # minus the CCA for business-use-of-home expenses, a caller input checked to be at most that
    # result.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_cca_claim_less_personal_part",
            "less": "ca/rental_cca_business_use_of_home",
        },
        produces={"output": "ca/rental_cca_claim"},
    ),
    # Guide T4036: "You cannot use CCA to create or increase a rental loss": amount 5 ("Line 5:
    # Subtotal (amount 4 minus line 9948)"), or 0 when amount 5 is negative, is the income of this
    # property before CCA that immediate expensing tests against. Owners: see
    # 03z_t776_cca_limit_all_statements.yaml.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/rental_net_income_after_terminal_loss",)},
        produces={"output": "ca/rental_cca_limit"},
    ),
    # T776 Area A "Column 24: UCC at the end of the year (column 7 minus column 23)": the class
    # number and column 24 of each class of the Area A list, a product of the return for next
    # year's column 2.
    CapabilitySelection(
        name="ca/closing_ucc_after_column_22_prorated",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/rental_cca_classes_adjusted",
            "non_compliant": "ca/short_term_rental_non_compliant_cca_by_class",
            "fiscal_period_days": "ca/rental_fiscal_period_days",
        },
        produces={"output": "ca/rental_closing_ucc"},
    ),
    # T776 Note 5 "the immediate expensing limit, which is equal to one of the following, whichever
    # is applicable: $1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year" and Area G "Line iii: Immediate expensing limit allocated
    # to you: Multiply $1.5 million by the percentage assigned to you in column 3 (see note 11)":
    # the printed $1.5 million, a dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/rental_immediate_expensing_cap"},
        consumes={},
        produces={"output": "ca/rental_immediate_expensing_cap"},
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
    # T776 Area G "The total of all percentages assigned under the agreement should not be more than
    # 100%. If the total is more than 100%, then the associated group has an immediate expensing
    # limit of zero." and Note 11 "If the total of column 3 is more than 100%, enter "0."": the
    # printed 100%, a dataset, as the form prints a percentage (100 for 100%).
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/rental_epop_percentage_maximum"},
        consumes={},
        produces={"output": "ca/rental_epop_percentage_maximum"},
    ),
    # T776 Area G "Line iii: Immediate expensing limit allocated to you: Multiply $1.5 million by
    # the percentage assigned to you in column 3 (see note 11)", first step: $1.5 million times the
    # percentage assigned to you in column 3, a caller input as the form prints it (40 for 40%).
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/rental_immediate_expensing_rounding"},
        consumes={
            "amount": "ca/rental_immediate_expensing_cap",
            "percentage": "ca/rental_epop_percentage",
        },
        produces={"output": "ca/rental_immediate_expensing_share"},
    ),
    # T776 Area G Note 11 "If the total of column 3 is more than 100%, enter "0."", first step: 100%
    # less "Total of percentage assigned: Total of column 3", a caller input; negative when the
    # total is more than 100%.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_epop_percentage_maximum",
            "less": "ca/rental_epop_percentage_total",
        },
        produces={"output": "ca/rental_epop_percentage_room"},
    ),
    # T776 Area G "Line iii: Immediate expensing limit allocated to you: Multiply $1.5 million by
    # the percentage assigned to you in column 3 (see note 11)" and Note 11 "If the total of column
    # 3 is more than 100%, enter "0."": the multiple above when 100% less the total of column 3 is
    # zero or positive, else 0.
    CapabilitySelection(
        name="ca/choose_by_sign",
        params={},
        consumes={
            "sign": "ca/rental_epop_percentage_room",
            "when_positive": (),
            "when_zero": (),
            "when_negative": (),
            "when_non_positive": (),
            "when_non_negative": ("ca/rental_immediate_expensing_share",),
        },
        produces={"output": "ca/rental_immediate_expensing_allocated"},
    ),
    # T776 Note 5 "amount iii of Area G, if you are associated with one or more EPOPs in the tax
    # year" and "zero, if you are associated with one or more EPOPs and an agreement that assigns a
    # percentage to one or more of the associated EPOPs was not filed with the minister in a
    # prescribed form": line iii times the count of agreements filed (a caller's 0 or 1), so 0 when
    # none was filed.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/rental_immediate_expensing_allocated",
            "count": "ca/rental_epop_agreement_filed_checked",
        },
        produces={"output": "ca/rental_immediate_expensing_associated_limit"},
    ),
    # T776 Note 5 "the immediate expensing limit, which is equal to one of the following, whichever
    # is applicable": a count of 1 for associated with one or more EPOPs (a caller's 0 or 1) chooses
    # the limit above ("amount iii of Area G" or "zero"); with a count of 0 it is the $1.5 million
    # ("if you are not associated with any other eligible person or partnership (EPOP) in the tax
    # year").
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_epop_associated_checked",
            "when_none": "ca/rental_immediate_expensing_cap",
            "when_any": "ca/rental_immediate_expensing_associated_limit",
        },
        produces={"output": "ca/rental_immediate_expensing_limit_before_minister"},
    ),
    # T776 Note 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": a count of 1 (a caller's 0 or 1) chooses the amount allocated by the minister,
    # as entered, in place of the limit before the days scaling; with a count of 0 the limit before
    # the minister's amount stands. The amount allocated is the amount for the year, and the days
    # scaling below applies to it as it does to the limit.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_minister_allocation_given_checked",
            "when_none": "ca/rental_immediate_expensing_limit_before_minister",
            "when_any": "ca/rental_minister_allocation",
        },
        produces={"output": "ca/rental_immediate_expensing_limit_before_proration"},
    ),
    # Income Tax Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation
    # year that is less than 51 weeks, its immediate expensing limit for the year is that proportion
    # of its immediate expensing limit for the year determined without reference to this paragraph
    # that the number of days in the year is of 365". The limit before the days scaling (the
    # minister's amount included) times the days of the fiscal period over the 365 of a full year,
    # rounded to the cent, for a fiscal period of fewer than 357 days (51 weeks of 7 days, the
    # shared figure `ca/immediate_expensing_short_year_days`); any other fiscal period keeps the
    # amount as it is. Guide T4036, "Immediate expensing incentive": "The limit is also prorated for
    # tax years shorter than 365 days" is the guide's wording of the same rule, which the
    # Regulations narrow to 51 weeks.
    CapabilitySelection(
        name="ca/prorated_by_fiscal_period_days",
        params={
            "rounding": "ca/rental_immediate_expensing_rounding",
            "class_rates": "ca/cca_class_rates",
        },
        consumes={
            "amount": "ca/rental_immediate_expensing_limit_before_proration",
            "fiscal_period_days": "ca/rental_fiscal_period_days",
            "short_year_days": "ca/immediate_expensing_short_year_days",
        },
        produces={"output": "ca/rental_immediate_expensing_limit"},
    ),
    # T776 Note 5 "the immediate expensing limit, which is equal to one of the following, whichever
    # is applicable", "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations", and Income Tax Regulations 1104(3.5)(b). The person's limit before the days
    # scaling, the one limit the statements of the four forms share: the limit before the minister's
    # amount, unscaled, or the amount allocated by the minister when there is one, which is also
    # unscaled. The statements are compared on it because each statement's own fiscal period scales
    # the limit above, and a person's statements may cover periods of different lengths.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_minister_allocation_given_checked",
            "when_none": "ca/rental_immediate_expensing_limit_before_minister",
            "when_any": "ca/rental_minister_allocation",
        },
        produces={"output": "ca/rental_immediate_expensing_limit_unprorated"},
    ),
    # T776 "Line i: Total immediate expensing claim for the year: Total of column 9" and Note 5 "The
    # total immediate expensing amount for the tax year (total of column 9) is limited to the lesser
    # of: the immediate expensing limit"; "the UCC of DIEPs in column 8"; "the amount of income, if
    # any, earned from the source of income that is a property (before any CCA deductions) in which
    # the relevant DIEP is used for the tax year": the total of column 9 of the Area A list, refused
    # when above the limit or above the income before CCA (amount 5 not below zero).
    CapabilitySelection(
        name="ca/immediate_expensing_claim",
        params={"class_rates": "ca/cca_class_rates"},
        consumes={
            "classes": "ca/rental_cca_classes_adjusted",
            "immediate_expensing_limit": "ca/rental_immediate_expensing_limit",
            "income_before_cca": "ca/rental_cca_limit",
        },
        produces={"output": "ca/rental_immediate_expensing_claim"},
    ),
    # T776 "Line 6: Net income (loss) (amount 5 minus line 9936)": line 9936 is computed above.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_net_income_after_terminal_loss",
            "less": "ca/rental_cca_claim",
        },
        produces={"output": "ca/rental_net_income_after_cca"},
    ),
    # T776 "Line 9946: ... For partnerships, enter the result from amount 7 plus line
    # 9974 minus line 9943", first step: amount 7 (line 7, "Partners: your share of
    # amount 6, or the amount from your T5013 slip, Statement of Partnership Income")
    # plus line 9974 ("Partners: GST/HST rebate for partners received in the year"),
    # (amount 7 is in 03z_t776_partner_amount_7.yaml and line 9974 is a caller input).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_partner_amount_7",
                "ca/rental_partner_gst_hst_rebate",
            )
        },
        produces={"output": "ca/rental_partner_share_with_rebate"},
    ),
    # T776 "Line 9946: ... For partnerships, enter the result from amount 7 plus line
    # 9974 minus line 9943", second step: that result minus line 9943 ("Partners: other
    # expenses of the partner"), a caller input.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rental_partner_share_with_rebate",
            "less": "ca/rental_partner_other_expenses",
        },
        produces={"output": "ca/rental_partnership_net_income"},
    ),
    # T776 "Line 9946: Your net income (loss): For sole proprietors or co-owners, enter
    # the result from amount 6. For partnerships, enter the result from amount 7 plus
    # line 9974 minus line 9943. Enter this amount on line 12600 of your income tax and
    # benefit return"; T1 "Line 12600: Net". A count of 1 for a partner (a caller's 0 or
    # 1) chooses the partnership figure, else amount 6.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_partner_checked",
            "when_none": "ca/rental_net_income_after_cca",
            "when_any": "ca/rental_partnership_net_income",
        },
        produces={"output": "ca/net_rental_income"},
    ),
    # Form T776 line 2 "Co-owners" and line 7 "Partners" are answers of 0 or 1: the co-owner
    # and partner answers are checked to be 0 or 1 before the steps that read them (in the part
    # `03e_t776_checks.yaml`). A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/rental_coowner"},
        produces={"output": "ca/rental_coowner_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/rental_partner"},
        produces={"output": "ca/rental_partner_checked"},
    ),
    # Guide T4036 "If you determine that you are a member of a partnership and you received a T5013
    # slip": the answer to a yes or no question, a count of 1 or 0, checked before the steps that
    # read it. A count of 2 or more is refused, not capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/rental_partner_t5013_slip"},
        produces={"output": "ca/rental_partner_t5013_slip_checked"},
    ),
    # The entries of the Area A rows that are not a claim, each totalled over the rows: the opening
    # UCC (column 2), the additions (column 3 and its parts in columns 4, 11 and 12, added) and the
    # remaining personal part (Note 9). A row with one of them is an entry of the form even when its
    # claim is 0. The totals are tests of any entry, not figures of the form.
    CapabilitySelection(
        name="ca/cca_opening_ucc_total",
        params={},
        consumes={"classes": "ca/rental_cca_classes_checked"},
        produces={"output": "ca/rental_cca_opening_ucc_total"},
    ),
    CapabilitySelection(
        name="ca/cca_additions_total",
        params={},
        consumes={"classes": "ca/rental_cca_classes_checked"},
        produces={"output": "ca/rental_cca_additions_total"},
    ),
    CapabilitySelection(
        name="ca/cca_personal_part_remaining_total",
        params={},
        consumes={"classes": "ca/rental_cca_classes_checked"},
        produces={"output": "ca/rental_cca_personal_part_remaining_total"},
    ),
    # The slip answer with the partner answer (line 7) and the other figures of the statement: the
    # count is 1 when the slip answer is 1 and the partner answer is 0, or when the slip answer is 1
    # and any of the amounts below is not 0 (the CCA claim of amount ii, the gross rents, the other
    # income, the expense lines, the recapture, the terminal loss, the land additions, the land
    # dispositions, the opening UCC total, the additions total and the remaining personal part total
    # of Area A, the total equipment additions of Area B and the total building additions of Area
    # C), else 0. The form prints no such rule; it is the guard of the form.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t776_t5013_slip_conflicts"},
        consumes={
            "counts": ("ca/rental_partner_checked", "ca/rental_partner_t5013_slip_checked"),
            "amounts": (
                "ca/rental_cca_table_claim",
                "ca/rental_gross_rents",
                "ca/rental_other_income",
                "ca/rental_advertising",
                "ca/rental_insurance",
                "ca/rental_interest_and_bank_charges",
                "ca/rental_office_expenses",
                "ca/rental_professional_fees",
                "ca/rental_management_and_administration_fees",
                "ca/rental_repairs_and_maintenance",
                "ca/rental_salaries_wages_and_benefits",
                "ca/rental_property_taxes",
                "ca/rental_travel",
                "ca/rental_utilities",
                "ca/rental_motor_vehicle_expenses",
                "ca/rental_other_expenses",
                "ca/rental_cca_table_recapture",
                "ca/rental_cca_table_terminal_loss",
                "ca/rental_land_additions",
                "ca/rental_land_dispositions",
                "ca/rental_cca_opening_ucc_total",
                "ca/rental_cca_additions_total",
                "ca/rental_cca_personal_part_remaining_total",
                "ca/rental_equipment_additions_total",
                "ca/rental_building_additions_total",
            ),
        },
        produces={"output": "ca/rental_t5013_slip_conflict"},
    ),
    # The count above is refused when it is 1: an input error naming the conflict (not capped, and
    # not a printed line). Its checked count is the form's export, read by nothing on the return.
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/t776_t5013_slip_conflict_refused"},
        consumes={"count": "ca/rental_t5013_slip_conflict"},
        produces={"output": "ca/rental_t5013_slip_conflict_checked"},
    ),
    # Area A endnote 5 answers, taken as a count of 0 or 1: each is checked to be 0 or 1 before
    # the step that reads it. A caller's 2 is refused, naming the kind.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/rental_epop_associated"},
        produces={"output": "ca/rental_epop_associated_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/rental_epop_agreement_filed"},
        produces={"output": "ca/rental_epop_agreement_filed_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/rental_minister_allocation_given"},
        produces={"output": "ca/rental_minister_allocation_given_checked"},
    ),
    # T776 Chart A "Column 3: Related portion of the total from line 9365 of Part 4": the total of
    # that column over the short-term rental units, one row for each property; the check below
    # refuses it above line 9365 (the short-term portion of the total expenses).
    CapabilitySelection(
        name="ca/short_term_rental_related_expenses",
        params={},
        consumes={"units": "ca/short_term_rental_units"},
        produces={"output": "ca/short_term_rental_related_expenses_total"},
    ),
    # T776 "Related portion of the total from line 9365 of Part 4", checked: the column 3 total at
    # most line 9365 ("Short-term rental portion of total expenses").
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/short_term_rental_related_expenses_total",
            "bound": "ca/rental_short_term_portion",
        },
        produces={"output": "ca/short_term_rental_related_expenses_total_checked"},
    ),
    # T776 "Line B: Total non-compliant amount of expenses for short-term rentals", checked against
    # the checked column 3 total: the order of the checks, since line B is never above that total.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_non_compliant_expenses",
            "bound": "ca/short_term_rental_related_expenses_total_checked",
        },
        produces={"output": "ca/rental_non_compliant_expenses_checked"},
    ),
    # The amount 7 typed, checked against the partner and slip answers: a typed amount 7 from a
    # partner with no slip is refused. The checked count is the form's export, read by nothing on
    # the return.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t776_partner_amount_7_conflicts"},
        consumes={
            "counts": ("ca/rental_partner_checked", "ca/rental_partner_t5013_slip_checked"),
            "amounts": ("ca/rental_partner_share",),
        },
        produces={"output": "ca/rental_partner_amount_7_conflict"},
    ),
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/t776_partner_amount_7_conflict_refused"},
        consumes={"count": "ca/rental_partner_amount_7_conflict"},
        produces={"output": "ca/rental_partner_amount_7_conflict_checked"},
    ),
    # T776 Part 1 "Your percentage of the partnership %" prints no bound; a share of the partnership
    # is at most the whole, 100, so the percentage is refused above it, not capped. The 100 is the
    # Area G figure (`ca/rental_epop_percentage_maximum`, produced in 03e_t776.yaml) reused for a
    # box that prints none: a sanity refusal, not a printed rule.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_partner_percentage",
            "bound": "ca/rental_epop_percentage_maximum",
        },
        produces={"output": "ca/rental_partner_percentage_checked"},
    ),
    # T776 "Line 7: Partners: your share of amount 6": amount 6 ("Line 6: Net income (loss)
    # (amount 5 minus line 9936)") times "Your percentage of the partnership %", for a partner who
    # received no T5013 slip.
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/rental_partner_share_rounding"},
        consumes={
            "amount": "ca/rental_net_income_after_cca",
            "percentage": "ca/rental_partner_percentage_checked",
        },
        produces={"output": "ca/rental_partner_share_of_amount_6"},
    ),
    # T776 "Line 7: Partners: your share of amount 6, or the amount from your T5013 slip": the
    # slip's amount (the typed figure) for a partner who received a slip (a count of 1), else the
    # share of amount 6.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_partner_t5013_slip_checked",
            "when_none": "ca/rental_partner_share_of_amount_6",
            "when_any": "ca/rental_partner_share",
        },
        produces={"output": "ca/rental_partner_amount_7"},
    ),
    # Guide T4036 "Limits on CCA", the statement's net rental income or loss before CCA: amount 5
    # ("Line 5: Subtotal (amount 4 minus line 9948)") for an owner or co-owner (a partner answer of
    # 0), or for a partner (a count of 1) amount 7 alone (IT-195R4, docs/cra-forms-2025/web/
    # it195r4-rental-property-cca-restrictions.txt, web page, para 10).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_partner_checked",
            "when_none": "ca/rental_net_income_after_terminal_loss",
            "when_any": "ca/rental_partner_amount_7",
        },
        produces={"output": "ca/rental_income_before_cca"},
    ),
    # Zero. No dataset or other artifact of the form is a zero (the form prints none; the zero of
    # Schedule 8, `ca/schedule_8_zero`, is that form's printed "0"), so this one is made from the
    # amount ii of Area A: its negation is never above zero, since amount ii is never below zero,
    # and the positive part of a figure not above zero is exactly 0
    # (`ca/positive_part_of_negation`). It is the claim on the own properties of a partner
    # statement.
    CapabilitySelection(
        name="ca/positive_part_of_negation",
        params={},
        consumes={"amount": "ca/rental_cca_table_claim"},
        produces={"output": "ca/rental_no_cca_claim"},
    ),
    # IT-195R4 (docs/cra-forms-2025/web/it195r4-rental-property-cca-restrictions.txt, web page) para
    # 2: the CCA claim of the person's own properties, line 9936 for an owner or co-owner (a partner
    # answer of 0), or 0 for a partner (a count of 1), whose line 9936 is the partnership's
    # depreciation, already inside amount 7 (para 10 of the same bulletin).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/rental_partner_checked",
            "when_none": "ca/rental_cca_claim",
            "when_any": "ca/rental_no_cca_claim",
        },
        produces={"output": "ca/rental_cca_claim_on_own_properties"},
    ),
}

FORM_WIRING = {
    (
        ShortTermRentalGrossRents,
        frozenset({RENTAL_PROPERTIES}),
        frozenset({SHORT_TERM_RENTAL_GROSS_RENTS}),
    ),
    (RentalGrossRents, frozenset({RENTAL_PROPERTIES}), frozenset({RENTAL_GROSS_RENTS})),
    (
        Sum,
        frozenset({RENTAL_GROSS_RENTS, RENTAL_OTHER_INCOME}),
        frozenset({GROSS_RENTAL_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                RENTAL_ADVERTISING,
                RENTAL_INSURANCE,
                RENTAL_INTEREST_AND_BANK_CHARGES,
                RENTAL_OFFICE_EXPENSES,
                RENTAL_PROFESSIONAL_FEES,
                RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES,
                RENTAL_REPAIRS_AND_MAINTENANCE,
                RENTAL_SALARIES_WAGES_AND_BENEFITS,
                RENTAL_PROPERTY_TAXES,
                RENTAL_TRAVEL,
                RENTAL_UTILITIES,
                RENTAL_MOTOR_VEHICLE_EXPENSES,
                RENTAL_OTHER_EXPENSES,
            }
        ),
        frozenset({RENTAL_TOTAL_EXPENSES}),
    ),
    (
        Sum,
        frozenset(
            {
                RENTAL_ADVERTISING_PERSONAL_PORTION,
                RENTAL_INSURANCE_PERSONAL_PORTION,
                RENTAL_INTEREST_AND_BANK_CHARGES_PERSONAL_PORTION,
                RENTAL_OFFICE_EXPENSES_PERSONAL_PORTION,
                RENTAL_PROFESSIONAL_FEES_PERSONAL_PORTION,
                RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_PERSONAL_PORTION,
                RENTAL_REPAIRS_AND_MAINTENANCE_PERSONAL_PORTION,
                RENTAL_SALARIES_WAGES_AND_BENEFITS_PERSONAL_PORTION,
                RENTAL_PROPERTY_TAXES_PERSONAL_PORTION,
                RENTAL_TRAVEL_PERSONAL_PORTION,
                RENTAL_UTILITIES_PERSONAL_PORTION,
                RENTAL_MOTOR_VEHICLE_EXPENSES_PERSONAL_PORTION,
                RENTAL_OTHER_EXPENSES_PERSONAL_PORTION,
            }
        ),
        frozenset({RENTAL_PERSONAL_PORTION}),
    ),
    (
        Sum,
        frozenset(
            {
                RENTAL_ADVERTISING_SHORT_TERM_PORTION,
                RENTAL_INSURANCE_SHORT_TERM_PORTION,
                RENTAL_INTEREST_AND_BANK_CHARGES_SHORT_TERM_PORTION,
                RENTAL_OFFICE_EXPENSES_SHORT_TERM_PORTION,
                RENTAL_PROFESSIONAL_FEES_SHORT_TERM_PORTION,
                RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_SHORT_TERM_PORTION,
                RENTAL_REPAIRS_AND_MAINTENANCE_SHORT_TERM_PORTION,
                RENTAL_SALARIES_WAGES_AND_BENEFITS_SHORT_TERM_PORTION,
                RENTAL_PROPERTY_TAXES_SHORT_TERM_PORTION,
                RENTAL_TRAVEL_SHORT_TERM_PORTION,
                RENTAL_UTILITIES_SHORT_TERM_PORTION,
                RENTAL_MOTOR_VEHICLE_EXPENSES_SHORT_TERM_PORTION,
                RENTAL_OTHER_EXPENSES_SHORT_TERM_PORTION,
            }
        ),
        frozenset({RENTAL_SHORT_TERM_PORTION}),
    ),
    (
        ShortTermRentalNonCompliantExpenses,
        frozenset({SHORT_TERM_RENTAL_UNITS}),
        frozenset({RENTAL_NON_COMPLIANT_EXPENSES}),
    ),
    (
        ShortTermRentalNonCompliantCca,
        frozenset({SHORT_TERM_RENTAL_CCA_UNITS}),
        frozenset({RENTAL_NON_COMPLIANT_CCA}),
    ),
    (
        rental_cca.ShortTermRentalNonCompliantCcaByClass,
        frozenset({SHORT_TERM_RENTAL_CCA_UNITS}),
        frozenset({SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS}),
    ),
    (
        ShortTermRentalRelatedExpenses,
        frozenset({SHORT_TERM_RENTAL_UNITS}),
        frozenset({SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL}),
    ),
    (
        AtMost,
        frozenset({SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL, RENTAL_SHORT_TERM_PORTION}),
        frozenset({SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL_CHECKED}),
    ),
    (
        AtMost,
        frozenset(
            {RENTAL_NON_COMPLIANT_EXPENSES, SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL_CHECKED}
        ),
        frozenset({RENTAL_NON_COMPLIANT_EXPENSES_CHECKED}),
    ),
    (
        Subtract,
        frozenset({RENTAL_TOTAL_EXPENSES, RENTAL_PERSONAL_PORTION}),
        frozenset({RENTAL_EXPENSES_LESS_PERSONAL_PORTION}),
    ),
    (
        Subtract,
        frozenset({RENTAL_EXPENSES_LESS_PERSONAL_PORTION, RENTAL_NON_COMPLIANT_EXPENSES_CHECKED}),
        frozenset({RENTAL_DEDUCTIBLE_EXPENSES}),
    ),
    (
        Subtract,
        frozenset({GROSS_RENTAL_INCOME, RENTAL_DEDUCTIBLE_EXPENSES}),
        frozenset({RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS}),
    ),
    (
        PositivePartOfNegation,
        frozenset({RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS}),
        frozenset({RENTAL_NET_INCOME_LOSS_SIZE}),
    ),
    (
        Sum,
        frozenset({RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS, RENTAL_NET_INCOME_LOSS_SIZE}),
        frozenset({RENTAL_NET_INCOME_UPPER_BOUND}),
    ),
    (
        Subtract,
        frozenset({RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS, RENTAL_NET_INCOME_UPPER_BOUND}),
        frozenset({RENTAL_NET_INCOME_LOWER_BOUND}),
    ),
    (
        AtMost,
        frozenset({RENTAL_COOWNER_SHARE, RENTAL_NET_INCOME_UPPER_BOUND}),
        frozenset({RENTAL_COOWNER_SHARE_CHECKED}),
    ),
    (
        AtMost,
        frozenset({RENTAL_NET_INCOME_LOWER_BOUND, RENTAL_COOWNER_SHARE_CHECKED}),
        frozenset({RENTAL_COOWNER_SHARE_LOWER_CHECKED}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_COOWNER_CHECKED,
                RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
                RENTAL_COOWNER_SHARE_CHECKED,
            }
        ),
        frozenset({RENTAL_NET_INCOME_SHARE}),
    ),
    (
        Subtract,
        frozenset({RENTAL_NET_INCOME_SHARE, RENTAL_COOWNER_OTHER_EXPENSES}),
        frozenset({RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES}),
    ),
    (
        CcaVehicleAdditionsChecks,
        frozenset({RENTAL_CCA_CLASSES, RENTAL_VEHICLE_SALES_TAX_RATE}),
        frozenset({RENTAL_CCA_CLASSES_CHECKED}),
    ),
    (
        RentalAdditionsTotal,
        frozenset({RENTAL_EQUIPMENT_ADDITIONS}),
        frozenset({RENTAL_EQUIPMENT_ADDITIONS_TOTAL}),
    ),
    (
        RentalAdditionsTotal,
        frozenset({RENTAL_BUILDING_ADDITIONS}),
        frozenset({RENTAL_BUILDING_ADDITIONS_TOTAL}),
    ),
    (
        CcaVehicleProceeds,
        frozenset({RENTAL_CCA_CLASSES_CHECKED, RENTAL_VEHICLE_SALES_TAX_RATE}),
        frozenset({RENTAL_CCA_CLASSES_ADJUSTED}),
    ),
    (
        RecapturedCca,
        frozenset({RENTAL_CCA_CLASSES_ADJUSTED}),
        frozenset({RENTAL_CCA_TABLE_RECAPTURE}),
    ),
    (
        AtMost,
        frozenset({RENTAL_COOWNER_RECAPTURED_CCA, RENTAL_CCA_TABLE_RECAPTURE}),
        frozenset({RENTAL_COOWNER_RECAPTURED_CCA_CHECKED}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_COOWNER_CHECKED,
                RENTAL_CCA_TABLE_RECAPTURE,
                RENTAL_COOWNER_RECAPTURED_CCA_CHECKED,
            }
        ),
        frozenset({RENTAL_RECAPTURED_CCA}),
    ),
    (
        TerminalLoss,
        frozenset({RENTAL_CCA_CLASSES_ADJUSTED}),
        frozenset({RENTAL_CCA_TABLE_TERMINAL_LOSS}),
    ),
    (
        AtMost,
        frozenset({RENTAL_COOWNER_TERMINAL_LOSS, RENTAL_CCA_TABLE_TERMINAL_LOSS}),
        frozenset({RENTAL_COOWNER_TERMINAL_LOSS_CHECKED}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_COOWNER_CHECKED,
                RENTAL_CCA_TABLE_TERMINAL_LOSS,
                RENTAL_COOWNER_TERMINAL_LOSS_CHECKED,
            }
        ),
        frozenset({RENTAL_TERMINAL_LOSS}),
    ),
    (
        FiscalPeriodDays,
        frozenset({RENTAL_FISCAL_PERIOD_DAYS_ENTERED}),
        frozenset({RENTAL_FISCAL_PERIOD_DAYS}),
    ),
    (
        CcaClaimAfterColumn22Prorated,
        frozenset(
            {
                RENTAL_CCA_CLASSES_ADJUSTED,
                SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,
                RENTAL_FISCAL_PERIOD_DAYS,
            }
        ),
        frozenset({RENTAL_CCA_TABLE_CLAIM}),
    ),
    (
        AtMost,
        frozenset({RENTAL_COOWNER_CCA_CLAIM, RENTAL_CCA_TABLE_CLAIM}),
        frozenset({RENTAL_COOWNER_CCA_CLAIM_CHECKED}),
    ),
    (
        ChooseByCount,
        frozenset(
            {RENTAL_COOWNER_CHECKED, RENTAL_CCA_TABLE_CLAIM, RENTAL_COOWNER_CCA_CLAIM_CHECKED}
        ),
        frozenset({RENTAL_CCA_CLAIM_SHARE}),
    ),
    (
        Subtract,
        frozenset({RENTAL_CCA_CLAIM_SHARE, RENTAL_CCA_PERSONAL_PART}),
        frozenset({RENTAL_CCA_CLAIM_LESS_PERSONAL_PART}),
    ),
    (
        Subtract,
        frozenset({RENTAL_CCA_CLAIM_LESS_PERSONAL_PART, RENTAL_CCA_BUSINESS_USE_OF_HOME}),
        frozenset({RENTAL_CCA_CLAIM}),
    ),
    (
        SumNotBelowZero,
        frozenset({RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS}),
        frozenset({RENTAL_CCA_LIMIT}),
    ),
    (
        ClosingUccAfterColumn22Prorated,
        frozenset(
            {
                RENTAL_CCA_CLASSES_ADJUSTED,
                SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,
                RENTAL_FISCAL_PERIOD_DAYS,
            }
        ),
        frozenset({RENTAL_CLOSING_UCC}),
    ),
    (
        Sum,
        frozenset({RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES, RENTAL_RECAPTURED_CCA}),
        frozenset({RENTAL_NET_INCOME_WITH_RECAPTURE}),
    ),
    (
        Subtract,
        frozenset({RENTAL_NET_INCOME_WITH_RECAPTURE, RENTAL_TERMINAL_LOSS}),
        frozenset({RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS}),
    ),
    (CreditAmount, frozenset(), frozenset({RENTAL_IMMEDIATE_EXPENSING_CAP})),
    (CreditAmount, frozenset(), frozenset({IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS})),
    (CreditAmount, frozenset(), frozenset({RENTAL_EPOP_PERCENTAGE_MAXIMUM})),
    (
        ApplyPercentage,
        frozenset({RENTAL_IMMEDIATE_EXPENSING_CAP, RENTAL_EPOP_PERCENTAGE}),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_SHARE}),
    ),
    (
        Subtract,
        frozenset({RENTAL_EPOP_PERCENTAGE_MAXIMUM, RENTAL_EPOP_PERCENTAGE_TOTAL}),
        frozenset({RENTAL_EPOP_PERCENTAGE_ROOM}),
    ),
    (
        ChooseBySign,
        frozenset({RENTAL_EPOP_PERCENTAGE_ROOM, RENTAL_IMMEDIATE_EXPENSING_SHARE}),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_ALLOCATED}),
    ),
    (
        TimesCount,
        frozenset({RENTAL_IMMEDIATE_EXPENSING_ALLOCATED, RENTAL_EPOP_AGREEMENT_FILED_CHECKED}),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_EPOP_ASSOCIATED_CHECKED,
                RENTAL_IMMEDIATE_EXPENSING_CAP,
                RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
            }
        ),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED,
                RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                RENTAL_MINISTER_ALLOCATION,
            }
        ),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION}),
    ),
    (
        ProratedByFiscalPeriodDays,
        frozenset(
            {
                RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
                RENTAL_FISCAL_PERIOD_DAYS,
                IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
            }
        ),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_LIMIT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED,
                RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
                RENTAL_MINISTER_ALLOCATION,
            }
        ),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED}),
    ),
    (
        ImmediateExpensingClaim,
        frozenset(
            {RENTAL_CCA_CLASSES_ADJUSTED, RENTAL_IMMEDIATE_EXPENSING_LIMIT, RENTAL_CCA_LIMIT}
        ),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_CLAIM}),
    ),
    (
        Subtract,
        frozenset({RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS, RENTAL_CCA_CLAIM}),
        frozenset({RENTAL_NET_INCOME_AFTER_CCA}),
    ),
    (
        Sum,
        frozenset({RENTAL_PARTNER_AMOUNT_7, RENTAL_PARTNER_GST_HST_REBATE}),
        frozenset({RENTAL_PARTNER_SHARE_WITH_REBATE}),
    ),
    (
        Subtract,
        frozenset({RENTAL_PARTNER_SHARE_WITH_REBATE, RENTAL_PARTNER_OTHER_EXPENSES}),
        frozenset({RENTAL_PARTNERSHIP_NET_INCOME}),
    ),
    (
        ChooseByCount,
        frozenset(
            {RENTAL_PARTNER_CHECKED, RENTAL_NET_INCOME_AFTER_CCA, RENTAL_PARTNERSHIP_NET_INCOME}
        ),
        frozenset({NET_RENTAL_INCOME}),
    ),
    (
        YesOrNoCount,
        frozenset({RENTAL_COOWNER}),
        frozenset({RENTAL_COOWNER_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({RENTAL_PARTNER}),
        frozenset({RENTAL_PARTNER_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({RENTAL_PARTNER_T5013_SLIP}),
        frozenset({RENTAL_PARTNER_T5013_SLIP_CHECKED}),
    ),
    (
        CcaOpeningUccTotal,
        frozenset({RENTAL_CCA_CLASSES_CHECKED}),
        frozenset({RENTAL_CCA_OPENING_UCC_TOTAL}),
    ),
    (
        CcaAdditionsTotal,
        frozenset({RENTAL_CCA_CLASSES_CHECKED}),
        frozenset({RENTAL_CCA_ADDITIONS_TOTAL}),
    ),
    (
        CcaPersonalPartRemainingTotal,
        frozenset({RENTAL_CCA_CLASSES_CHECKED}),
        frozenset({RENTAL_CCA_PERSONAL_PART_REMAINING_TOTAL}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                RENTAL_PARTNER_CHECKED,
                RENTAL_PARTNER_T5013_SLIP_CHECKED,
                RENTAL_CCA_TABLE_CLAIM,
                RENTAL_GROSS_RENTS,
                RENTAL_OTHER_INCOME,
                RENTAL_ADVERTISING,
                RENTAL_INSURANCE,
                RENTAL_INTEREST_AND_BANK_CHARGES,
                RENTAL_OFFICE_EXPENSES,
                RENTAL_PROFESSIONAL_FEES,
                RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES,
                RENTAL_REPAIRS_AND_MAINTENANCE,
                RENTAL_SALARIES_WAGES_AND_BENEFITS,
                RENTAL_PROPERTY_TAXES,
                RENTAL_TRAVEL,
                RENTAL_UTILITIES,
                RENTAL_MOTOR_VEHICLE_EXPENSES,
                RENTAL_OTHER_EXPENSES,
                RENTAL_CCA_TABLE_RECAPTURE,
                RENTAL_CCA_TABLE_TERMINAL_LOSS,
                RENTAL_LAND_ADDITIONS,
                RENTAL_LAND_DISPOSITIONS,
                RENTAL_CCA_OPENING_UCC_TOTAL,
                RENTAL_CCA_ADDITIONS_TOTAL,
                RENTAL_CCA_PERSONAL_PART_REMAINING_TOTAL,
                RENTAL_EQUIPMENT_ADDITIONS_TOTAL,
                RENTAL_BUILDING_ADDITIONS_TOTAL,
            }
        ),
        frozenset({RENTAL_T5013_SLIP_CONFLICT}),
    ),
    (
        CountRefusedByConditions,
        frozenset({RENTAL_T5013_SLIP_CONFLICT}),
        frozenset({RENTAL_T5013_SLIP_CONFLICT_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({RENTAL_EPOP_ASSOCIATED}),
        frozenset({RENTAL_EPOP_ASSOCIATED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({RENTAL_EPOP_AGREEMENT_FILED}),
        frozenset({RENTAL_EPOP_AGREEMENT_FILED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({RENTAL_MINISTER_ALLOCATION_GIVEN}),
        frozenset({RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                RENTAL_PARTNER_CHECKED,
                RENTAL_PARTNER_T5013_SLIP_CHECKED,
                RENTAL_PARTNER_SHARE,
            }
        ),
        frozenset({RENTAL_PARTNER_AMOUNT_7_CONFLICT}),
    ),
    (
        CountRefusedByConditions,
        frozenset({RENTAL_PARTNER_AMOUNT_7_CONFLICT}),
        frozenset({RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED}),
    ),
    (
        AtMost,
        frozenset({RENTAL_PARTNER_PERCENTAGE, RENTAL_EPOP_PERCENTAGE_MAXIMUM}),
        frozenset({RENTAL_PARTNER_PERCENTAGE_CHECKED}),
    ),
    (
        ApplyPercentage,
        frozenset({RENTAL_NET_INCOME_AFTER_CCA, RENTAL_PARTNER_PERCENTAGE_CHECKED}),
        frozenset({RENTAL_PARTNER_SHARE_OF_AMOUNT_6}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_PARTNER_T5013_SLIP_CHECKED,
                RENTAL_PARTNER_SHARE_OF_AMOUNT_6,
                RENTAL_PARTNER_SHARE,
            }
        ),
        frozenset({RENTAL_PARTNER_AMOUNT_7}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                RENTAL_PARTNER_CHECKED,
                RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
                RENTAL_PARTNER_AMOUNT_7,
            }
        ),
        frozenset({RENTAL_INCOME_BEFORE_CCA}),
    ),
    (
        PositivePartOfNegation,
        frozenset({RENTAL_CCA_TABLE_CLAIM}),
        frozenset({RENTAL_NO_CCA_CLAIM}),
    ),
    (
        ChooseByCount,
        frozenset({RENTAL_PARTNER_CHECKED, RENTAL_CCA_CLAIM, RENTAL_NO_CCA_CLAIM}),
        frozenset({RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES}),
    ),
}

INPUTS = frozenset({"ca/t776_statements"})

FORM_EXPORTS = (
    "ca/net_rental_income",
    "ca/gross_rental_income",
    "ca/short_term_rental_gross_rents",
    "ca/rental_short_term_portion",
    "ca/rental_closing_ucc",
    "ca/rental_non_compliant_cca",
    "ca/short_term_rental_non_compliant_cca_by_class",
    "ca/rental_immediate_expensing_claim",
    "ca/rental_immediate_expensing_limit_unprorated",
    "ca/rental_equipment_additions_total",
    "ca/rental_building_additions_total",
    "ca/rental_land_additions",
    "ca/rental_land_dispositions",
    "ca/rental_coowner_share_lower_checked",
    "ca/rental_t5013_slip_conflict_checked",
    "ca/rental_partner_amount_7_conflict_checked",
    "ca/rental_income_before_cca",
    "ca/rental_cca_claim_on_own_properties",
)

# The form exports the net rental income before CCA (`ca/rental_income_before_cca`) and the CCA
# claim on the own properties (`ca/rental_cca_claim_on_own_properties`), which
# 03z_t776_cca_limit_all_statements.yaml reads, and the lines nothing on the return reads (line
# 8140, line 9365, Chart B's line C and total for each class, Area A column 24 and line i, Area B
# line 9925 and Area C line 9927, Area F
# lines 9923 "Total cost of all land additions in the year" and 9924 "Total proceeds from all land
# dispositions in the year", which are taken as entered and printed, the checked counts of the
# T5013 slip conflicts and of the amount 7 conflicts):
# an export nobody reads is fine, so the return
# declares no output for them. The gross rental income is the one the return declares (T1 line
# 12599, which no step reads).
OUTPUTS: frozenset[str] = frozenset({"ca/gross_rental_income"})

# T1 line 12600 "Net": the total of T776 line 9946 over the statements; T1 line 12599 "Gross": the
# total of T776 line 8299 over the statements.
STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t776.gross_rental_income"},
        produces={"output": "ca/gross_rental_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t776.net_rental_income"},
        produces={"output": "ca/net_rental_income"},
    ),
}

WIRING = {
    (
        RecordTotal,
        frozenset({NET_RENTAL_INCOME_PER_STATEMENT}),
        frozenset({NET_RENTAL_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({GROSS_RENTAL_INCOME_PER_STATEMENT}),
        frozenset({GROSS_RENTAL_INCOME}),
    ),
}
