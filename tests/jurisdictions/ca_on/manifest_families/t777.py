"""The CA-ON manifest entries of Form T777 (see `test_manifest_t777.py`).

T777, the Statement of Employment Expenses, is the form `ca/t777`, which has no instances list, so
it runs once. Its inputs are the manifest's inputs of `01c_t777_inputs.yaml`: the Part A row lists
of Class 8 and of the vehicle classes 10, 54 and 55, the Part B row list of Class 10.1 vehicles,
the GST/HST rate of the Class 54 sold-vehicle step, the page 1 expenses (lines 1, 2, 4 to 10, 12
and 14), the line 3 chart's figures, the line 16 chart's figures and the list of labour mobility
relocations of line 11.

Its CCA selections (the Part A checks, the proceeds, the claims and the closing UCC) are in
`03k_t777.yaml`, as before. Its lines of page 1 to 3 and the line 11 total (`LINE_STEPS`, in
`03q_t777_lines.yaml`): the line 4 and line 9 steps, the line 3 chart and line 16 chart steps, and
the line 11 total over the relocation form's copies. The relocation form `ca/t777_relocation`
(`RELOCATION_STEPS`, in `03r_t777_relocation.yaml`) runs once for each relocation of
`ca/t777_relocations` and exports its line 39 and line 40 amounts.

The form exports the printed lines the form computes (`FORM_EXPORTS`); the return reads line 17
(T1 line 22900, in `05s_other_employment_expenses.yaml`) and no other export yet.

The entries of the return are listed in `manifest_families/other_employment_expenses.py`.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    NET_INCOME_SIGNED,
    T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT,
    T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_ALLOWED,
    T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION,
    T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION_TOTAL,
    T777_APPRENTICE_MECHANIC_TOOLS_NET_INCOME_LIMIT,
    T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS,
    T777_CLASS_8_CHECKED_ROWS,
    T777_CLASS_8_CLOSING_UCC,
    T777_LINE_10,
    T777_LINE_10_CHECKED,
    T777_LINE_10_TOTAL,
    T777_LINE_13,
    T777_LINE_25,
    T777_PART_B_ADDITIONS_CHECKED_ROWS,
    T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS,
    T777_PART_B_CLASS_CHECKED_ROWS,
    T777_PART_B_CLOSING_UCC,
    T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS,
    T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS,
    T777_VEHICLE_CHECKED_ROWS,
    T777_VEHICLE_CLOSING_UCC,
)

# The inputs of the form, in `01c_t777_inputs.yaml`. The page 1 expenses, the line 3 chart and the
# line 16 chart are scalar inputs; the labour mobility relocations are a record list (one record for
# each eligible temporary relocation), an input of the form's instances `ca/t777_relocations`.
INPUTS = frozenset(
    {
        # The Part A and Part B row lists and the Class 54 sold-vehicle rate (the CCA table).
        "ca/t777_class_8_rows",
        "ca/t777_vehicle_rows",
        "ca/t777_part_b_rows",
        "ca/t777_vehicle_sales_tax_rate",
        # Page 1, lines 1, 2, 4 (the amount before its 50%), 5 to 8, 9 (the amount before the
        # $1,000 maximum), 10, 12 and 14.
        "ca/t777_accounting_and_legal_fees",
        "ca/t777_advertising_and_promotion",
        "ca/t777_food_beverages_entertainment",
        "ca/t777_lodging",
        "ca/t777_parking",
        "ca/t777_office_supplies",
        "ca/t777_other_expenses",
        "ca/t777_tradespersons_tools",
        "ca/t777_apprentice_mechanic_tools",
        "ca/t777_musical_instrument_expenses",
        "ca/t777_artists_employment_expenses",
        # Guide T4044 "Deduction for tools": the tools cost, the tradesperson's employment income
        # and the two apprenticeship grant figures of the maximum deduction.
        "ca/t777_eligible_tools_cost",
        "ca/t777_were_a_tradesperson_in_2025",
        "ca/t777_tradesperson_tools_certified_on_t2200_question_12",
        "ca/t777_tradesperson_employment_income",
        "ca/t777_apprenticeship_grants_received",
        "ca/t777_apprenticeship_grant_overpayments",
        # Guide T4044 "Deduction for tools for an eligible apprentice mechanic": the first-time
        # answer, the tools cost of the last three months of 2024, the apprentice mechanic income
        # and the carry forward of 2024.
        "ca/t777_first_employed_as_apprentice_mechanic_in_2025",
        "ca/t777_registered_in_a_mechanic_designation_program",
        "ca/t777_employed_as_an_apprentice_mechanic",
        "ca/t777_apprentice_mechanic_tools_certified_on_t2200_question_13",
        "ca/t777_apprentice_tools_cost_last_three_months_of_2024",
        "ca/t777_apprentice_mechanic_employment_income",
        "ca/t777_apprentice_mechanic_tools_carry_forward",
        # Guide T4044 "Part 2 - Musical instrument expenses": the income as a musician.
        "ca/t777_musician_employment_income",
        # Guide T4044 "Part 1 - Artists' employment expenses": the expenses paid and carried
        # forward, the artistic employment income and the motor vehicle interest and capital cost
        # allowance deducted from artistic income.
        "ca/t777_artists_expenses_paid",
        "ca/t777_artists_expenses_carry_forward",
        "ca/t777_artists_employment_income",
        "ca/t777_artists_vehicle_interest_deducted",
        "ca/t777_artists_vehicle_cca_deducted",
        # Line 3 chart: lines 18 and 19 (kilometres), 21 to 24, 26 to 28 (the expenses) and 31 (the
        # allowances, rebates and reimbursements).
        "ca/t777_employment_kilometres",
        "ca/t777_total_kilometres",
        "ca/t777_vehicle_fuel",
        "ca/t777_vehicle_maintenance",
        "ca/t777_vehicle_insurance",
        "ca/t777_vehicle_licence_and_registration",
        "ca/t777_vehicle_interest",
        "ca/t777_interest_days",
        "ca/t777_vehicle_other_expenses",
        "ca/t777_vehicle_allowances",
        # Guide T4044 "Eligible leasing costs" chart: lines 1 to 4 and the year of the lease.
        "ca/t777_lease_charges",
        "ca/t777_lease_payments_before",
        "ca/t777_lease_days",
        "ca/t777_lease_list_price",
        "ca/t777_lease_year",
        "ca/t777_passenger_vehicle",
        # Guide T4044 "Repayments and imputed interest": a repayment owing and the three conditions
        # of imputed interest.
        "ca/t777_lease_repayment_owing",
        "ca/t777_lease_deposits_made",
        "ca/t777_lease_deposits_refundable",
        "ca/t777_lease_deposits_total",
        # Line 16 chart: lines 42 to 46 (the expenses), 48 (the employment-use amount the filer
        # calculates) and 49 (the amount carried forward from the previous year).
        "ca/t777_work_space_electricity_heat_water_internet",
        "ca/t777_work_space_maintenance",
        "ca/t777_work_space_home_insurance",
        "ca/t777_work_space_property_taxes",
        "ca/t777_work_space_other_expenses",
        "ca/t777_work_space_employment_use_amount",
        "ca/t777_work_space_carried_forward",
        # Line 11 chart: one record for each eligible temporary relocation (the instances).
        "ca/t777_relocations",
    }
)

# The exports of the form, in the order the form prints them: lines 3, 4, 9, 11, 13, 15, 16, 17 and
# 25, the leasing chart conflict check and the musical instrument expenses check (which the form
# reads nowhere), then the closing UCC of
# Parts A and B, then the work-space amount carried forward (line 55).
FORM_EXPORTS = (
    "ca/t777_line_3",
    "ca/t777_line_4",
    "ca/t777_tools_formula_b",
    "ca/t777_tradespersons_tools_maximum_deduction",
    "ca/t777_line_9",
    "ca/t777_apprentice_mechanic_tools_maximum_deduction",
    "ca/t777_line_10",
    "ca/t777_artists_employment_expenses_maximum_deduction",
    "ca/t777_artists_expenses_carried_forward_out",
    "ca/t777_line_14",
    "ca/t777_line_11",
    T777_LINE_13.identifier,
    "ca/t777_musical_instrument_expenses_maximum_deduction",
    "ca/t777_musical_instrument_expenses_checked",
    "ca/t777_line_15",
    "ca/t777_line_16",
    "ca/t777_work_space_expenses",
    "ca/t777_line_17",
    T777_LINE_25.identifier,
    "ca/t777_lease_chart_conflict_checked",
    T777_CLASS_8_CLOSING_UCC.identifier,
    T777_VEHICLE_CLOSING_UCC.identifier,
    T777_PART_B_CLOSING_UCC.identifier,
    "ca/t777_work_space_carried_forward_out",
)

# The class rates datasets of the CCA table, one for each list: Class 8, Classes 10, 54 and 55,
# Class 10.1.
FORM_DATASETS = frozenset(
    {
        "ca/t777_class_8_rates",
        "ca/t777_vehicle_class_rates",
        "ca/t777_part_b_class_rates",
    }
)

# The datasets of the lines of page 1 to 3 and of the line 11 total: the 50% of line 4, the $1,000
# of line 9, the rounding of the line 30 product, and the $4,000 of line 41.
LINE_DATASETS = frozenset(
    {
        "ca/t777_meals_rate",
        "ca/t777_tradespersons_tools_maximum",
        "ca/t777_tradespersons_tools_threshold",
        "ca/t777_apprentice_mechanic_tools_base",
        "ca/t777_apprentice_mechanic_tools_rate",
        "ca/t777_artists_employment_expenses_maximum",
        "ca/t777_artists_employment_expenses_rate",
        "ca/canada_employment_amount",
        "ca/t777_vehicle_rounding",
        "ca/t777_line_11_maximum",
    }
)

# The CCA table capabilities the form's selections are of.
FORM_TABLE_CAPABILITIES = frozenset({"ca/cca_vehicle_proceeds", "ca/cca_claim", "ca/closing_ucc"})

# The Part A check capability, one selection for each of the two Part A lists.
FORM_CHECK_CAPABILITIES = frozenset({"ca/cca_part_a_checks"})

# The Part A rows that passed the checks: the Class 8 rows and the vehicle rows.
FORM_CHECKED_LISTS = frozenset(
    {T777_CLASS_8_CHECKED_ROWS.identifier, T777_VEHICLE_CHECKED_ROWS.identifier}
)

# The Part A change in use check (`03y_t777_change_in_use_check.yaml`): one selection of
# `ca/cca_change_in_use_checks` for each of the two Part A checked lists, which it reads, and the
# change in use checked rows it produces: the Class 8 claim and closing UCC read the Class 8 rows,
# and the vehicle proceeds read the vehicle rows.
FORM_CHANGE_IN_USE_CAPABILITIES = frozenset({"ca/cca_change_in_use_checks"})
FORM_CHANGE_IN_USE_READS = frozenset(
    {T777_CLASS_8_CHECKED_ROWS.identifier, T777_VEHICLE_CHECKED_ROWS.identifier}
)
FORM_CHANGE_IN_USE_CHECKED_LISTS = frozenset(
    {
        T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS.identifier,
        T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS.identifier,
    }
)

# The Class 10.1 additions check of Part B (`03u_t777_vehicle_additions_check.yaml`): the Part B
# rows the Part B checks passed, its one check capability, the prescribed amounts it reads, and the
# checked rows it produces, which the Part B claim reads.
PART_B_ADDITIONS_CHECK_DATASETS = frozenset({"ca/cca_vehicle_prescribed_amounts"})
PART_B_ADDITIONS_CHECKED_LISTS = frozenset({T777_PART_B_ADDITIONS_CHECKED_ROWS.identifier})

# The Class 10.1 class condition check of Part B (`03v_t777_vehicle_class_check.yaml`): the
# additions checked rows it reads, the class conditions dataset, and the class checked rows it
# produces, which the Part B claim reads.
PART_B_CLASS_CHECK_DATASETS = frozenset({"ca/cca_class_10_1_conditions"})
PART_B_CLASS_CHECKED_LISTS = frozenset({T777_PART_B_CLASS_CHECKED_ROWS.identifier})

# The non-arm's-length purchase check of Part B (`03w_t777_vehicle_non_arms_length_check.yaml`): the
# class checked rows it reads, the prescribed amounts it reads, and the checked rows it produces,
# which the change in use check reads. The change in use check
# (`03x_t777_vehicle_change_in_use_check.yaml`) produces the rows the Part B claim reads.
PART_B_NON_ARMS_LENGTH_CHECK_DATASETS = frozenset({"ca/cca_vehicle_prescribed_amounts"})
PART_B_NON_ARMS_LENGTH_CHECKED_LISTS = frozenset(
    {T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS.identifier}
)
PART_B_CHANGE_IN_USE_CHECKED_LISTS = frozenset({T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS.identifier})
# The selections of Guide T4044's "Eligible leasing costs" chart (lines 1 to 8), in
# `03q_t777_leasing_chart.yaml`: the printed amounts of lines 5, 7 and 8 for the year of the lease
# (`ca/year_amount`) with the tax on each, line 6, line 7 less line 2 (line 2 refused above the
# "divided by 30" figure), line 8, and the lower of lines 7 and 8, which is line 27; and, before
# them, the guide's "Repayments and imputed interest" check (three yes or no answers, the conflict
# of a passenger vehicle with a repayment owing or imputed interest, and its refusal).
LEASING_STEPS = {
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_passenger_vehicle"},
        produces={"output": "ca/t777_passenger_vehicle_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_lease_repayment_owing"},
        produces={"output": "ca/t777_lease_repayment_owing_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_lease_deposits_made"},
        produces={"output": "ca/t777_lease_deposits_made_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_lease_deposits_refundable"},
        produces={"output": "ca/t777_lease_deposits_refundable_checked"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t777_lease_chart_conflicts"},
        consumes={
            "counts": (
                "ca/t777_passenger_vehicle_checked",
                "ca/t777_lease_repayment_owing_checked",
                "ca/t777_lease_deposits_made_checked",
                "ca/t777_lease_deposits_refundable_checked",
            ),
            "amounts": ("ca/t777_lease_deposits_total",),
        },
        produces={"output": "ca/t777_lease_chart_conflict"},
    ),
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/t777_lease_chart_conflict_refused"},
        consumes={"count": "ca/t777_lease_chart_conflict"},
        produces={"output": "ca/t777_lease_chart_conflict_checked"},
    ),
    CapabilitySelection(
        name="ca/year_amount",
        params={"amounts": "ca/t777_lease_list_price_limit"},
        consumes={"year": "ca/t777_lease_year"},
        produces={"output": "ca/t777_lease_list_price_limit"},
    ),
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/t777_vehicle_rounding"},
        consumes={
            "amount": "ca/t777_lease_list_price_limit",
            "percentage": "ca/t777_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/t777_lease_list_price_tax"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t777_lease_list_price_limit", "ca/t777_lease_list_price_tax")},
        produces={"output": "ca/t777_lease_line_5"},
    ),
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={"amounts": ("ca/t777_lease_list_price", "ca/t777_lease_line_5")},
        produces={"output": "ca/t777_lease_line_6_amount"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t777_lease_price_rate"},
        consumes={"base": "ca/t777_lease_line_6_amount"},
        produces={"output": "ca/t777_lease_line_6"},
    ),
    CapabilitySelection(
        name="ca/year_amount",
        params={"amounts": "ca/t777_lease_charge_limit"},
        consumes={"year": "ca/t777_lease_year"},
        produces={"output": "ca/t777_lease_charge_limit"},
    ),
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/t777_vehicle_rounding"},
        consumes={
            "amount": "ca/t777_lease_charge_limit",
            "percentage": "ca/t777_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/t777_lease_charge_tax"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t777_lease_charge_limit", "ca/t777_lease_charge_tax")},
        produces={"output": "ca/t777_lease_charge_with_tax"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t777_lease_charge_with_tax", "count": "ca/t777_lease_days"},
        produces={"output": "ca/t777_lease_line_7_times_days"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t777_lease_days_fraction"},
        consumes={"base": "ca/t777_lease_line_7_times_days"},
        produces={"output": "ca/t777_lease_line_7_divided"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_lease_payments_before",
            "bound": "ca/t777_lease_line_7_divided",
        },
        produces={"output": "ca/t777_lease_payments_before_checked"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t777_lease_line_7_divided",
            "less": "ca/t777_lease_payments_before_checked",
        },
        produces={"output": "ca/t777_lease_line_7"},
    ),
    CapabilitySelection(
        name="ca/year_amount",
        params={"amounts": "ca/t777_lease_cost_limit"},
        consumes={"year": "ca/t777_lease_year"},
        produces={"output": "ca/t777_lease_cost_limit"},
    ),
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/t777_vehicle_rounding"},
        consumes={
            "amount": "ca/t777_lease_cost_limit",
            "percentage": "ca/t777_vehicle_sales_tax_rate",
        },
        produces={"output": "ca/t777_lease_cost_tax"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t777_lease_cost_limit", "ca/t777_lease_cost_tax")},
        produces={"output": "ca/t777_lease_cost_with_tax"},
    ),
    CapabilitySelection(
        name="core/apply_ratio",
        params={"rounding": "ca/t777_vehicle_rounding"},
        consumes={
            "amount": "ca/t777_lease_cost_with_tax",
            "numerator": "ca/t777_lease_charges",
            "denominator": "ca/t777_lease_line_6",
        },
        produces={"output": "ca/t777_lease_line_8"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t777_lease_line_7", "ca/t777_lease_line_8")},
        produces={"output": "ca/t777_lease_eligible_cost"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t777_passenger_vehicle_checked",
            "when_none": "ca/t777_lease_charges",
            "when_any": "ca/t777_lease_eligible_cost",
        },
        produces={"output": "ca/t777_vehicle_leasing_costs"},
    ),
}


# The selections of line 26 "Interest expense", in `03q_t777_interest_chart.yaml` (Guide T4044
# "Available interest expense for passenger vehicles or zero-emission passenger vehicles chart").
INTEREST_STEPS = {
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/t777_interest_daily_limit"},
        consumes={"count": "ca/t777_interest_days"},
        produces={"output": "ca/t777_interest_limit"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t777_vehicle_interest", "ca/t777_interest_limit")},
        produces={"output": "ca/t777_interest_available"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t777_passenger_vehicle_checked",
            "when_none": "ca/t777_vehicle_interest",
            "when_any": "ca/t777_interest_available",
        },
        produces={"output": "ca/t777_line_26"},
    ),
}


# The selections of the tradesperson's tools maximum and line 9, in
# `03q_t777_tradespersons_tools_maximum.yaml` (Guide T4044 "Deduction for tools").
TOOLS_STEPS = {
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_tradesperson_employment_income",
            "bound": "ca/t777_work_space_employment_income",
        },
        produces={"output": "ca/t777_tradesperson_employment_income_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_were_a_tradesperson_in_2025"},
        produces={"output": "ca/t777_were_a_tradesperson_in_2025_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_tradesperson_tools_certified_on_t2200_question_12"},
        produces={"output": "ca/t777_tradesperson_tools_certified_on_t2200_question_12_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_tradesperson_employment_income_checked",
                "ca/t777_apprenticeship_grants_received",
            )
        },
        produces={"output": "ca/t777_tradesperson_income_with_grants"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t777_tradesperson_income_with_grants",
            "less": "ca/t777_apprenticeship_grant_overpayments",
        },
        produces={"output": "ca/t777_tradesperson_income_for_tools"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/t777_eligible_tools_cost", "ca/t777_tradesperson_income_for_tools")
        },
        produces={"output": "ca/t777_tools_formula_a"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t777_tradespersons_tools_threshold"},
        consumes={},
        produces={"output": "ca/t777_tradespersons_tools_threshold"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t777_tools_formula_a",
            "less": "ca/t777_tradespersons_tools_threshold",
        },
        produces={"output": "ca/t777_tools_formula_b"},
    ),
    CapabilitySelection(
        name="ca/lesser_of_with_maximum",
        params={"maximum": "ca/t777_tradespersons_tools_maximum"},
        consumes={"amounts": ("ca/t777_tools_formula_b",)},
        produces={"output": "ca/t777_tradespersons_tools_formula_maximum"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t777_tradespersons_tools_formula_maximum",
            "count": "ca/t777_were_a_tradesperson_in_2025_checked",
        },
        produces={"output": "ca/t777_tradespersons_tools_maximum_for_a_tradesperson"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t777_tradespersons_tools_maximum_for_a_tradesperson",
            "count": "ca/t777_tradesperson_tools_certified_on_t2200_question_12_checked",
        },
        produces={"output": "ca/t777_tradespersons_tools_maximum_deduction"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_tradespersons_tools",
            "bound": "ca/t777_tradespersons_tools_maximum_deduction",
        },
        produces={"output": "ca/t777_line_9"},
    ),
}


# The selections of the apprentice mechanic tools maximum and line 10, in
# `03q_t777_apprentice_mechanic_tools_maximum.yaml` (Guide T4044 "Deduction for tools for an
# eligible apprentice mechanic").
APPRENTICE_STEPS = {
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_mechanic_employment_income",
            "bound": "ca/t777_work_space_employment_income",
        },
        produces={"output": "ca/t777_apprentice_mechanic_employment_income_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_registered_in_a_mechanic_designation_program"},
        produces={"output": "ca/t777_registered_in_a_mechanic_designation_program_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_employed_as_an_apprentice_mechanic"},
        produces={"output": "ca/t777_employed_as_an_apprentice_mechanic_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_apprentice_mechanic_tools_certified_on_t2200_question_13"},
        produces={
            "output": "ca/t777_apprentice_mechanic_tools_certified_on_t2200_question_13_checked"
        },
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t777_first_employed_as_apprentice_mechanic_in_2025"},
        produces={"output": "ca/t777_first_employed_as_apprentice_mechanic_in_2025_checked"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_tools_cost_last_three_months_of_2024",
            "count": "ca/t777_first_employed_as_apprentice_mechanic_in_2025_checked",
        },
        produces={"output": "ca/t777_apprentice_tools_cost_added"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t777_eligible_tools_cost", "ca/t777_apprentice_tools_cost_added")},
        produces={"output": "ca/t777_apprentice_tools_formula_a"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/employment_income", "ca/other_employment_income")},
        produces={"output": "ca/t777_canada_employment_amount_income"},
    ),
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/canada_employment_amount"},
        consumes={"base": "ca/t777_canada_employment_amount_income"},
        produces={"output": "ca/t777_canada_employment_amount"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t777_apprentice_mechanic_tools_base"},
        consumes={},
        produces={"output": "ca/t777_apprentice_mechanic_tools_base"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/t777_apprentice_mechanic_tools_base", "ca/t777_canada_employment_amount")
        },
        produces={"output": "ca/t777_apprentice_tools_base_with_employment_amount"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_apprentice_mechanic_employment_income_checked",
                "ca/t777_apprenticeship_grants_received",
            )
        },
        produces={"output": "ca/t777_apprentice_income_with_grants"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_income_with_grants",
            "less": "ca/t777_line_9",
        },
        produces={"output": "ca/t777_apprentice_income_less_tools_claim"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_income_less_tools_claim",
            "less": "ca/t777_apprenticeship_grant_overpayments",
        },
        produces={"output": "ca/t777_apprentice_income_for_tools"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t777_apprentice_mechanic_tools_rate"},
        consumes={"base": "ca/t777_apprentice_income_for_tools"},
        produces={"output": "ca/t777_apprentice_tools_five_percent"},
    ),
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={
            "amounts": (
                "ca/t777_apprentice_tools_base_with_employment_amount",
                "ca/t777_apprentice_tools_five_percent",
            )
        },
        produces={"output": "ca/t777_apprentice_tools_formula_b2"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/t777_apprentice_tools_formula_a", "ca/t777_apprentice_tools_formula_b2")
        },
        produces={"output": "ca/t777_apprentice_tools_formula_b"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_tools_formula_a",
            "less": "ca/t777_apprentice_tools_formula_b",
        },
        produces={"output": "ca/t777_apprentice_tools_formula_a_less_b"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_tools_formula_a_less_b",
            "count": "ca/t777_registered_in_a_mechanic_designation_program_checked",
        },
        produces={"output": "ca/t777_apprentice_tools_formula_a_less_b_if_registered"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_tools_formula_a_less_b_if_registered",
            "count": "ca/t777_employed_as_an_apprentice_mechanic_checked",
        },
        produces={"output": "ca/t777_apprentice_tools_formula_a_less_b_if_employed"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_tools_formula_a_less_b_if_employed",
            "count": "ca/t777_apprentice_mechanic_tools_certified_on_t2200_question_13_checked",
        },
        produces={"output": "ca/t777_apprentice_tools_formula_a_less_b_if_certified"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_apprentice_tools_formula_a_less_b_if_certified",
                "ca/t777_apprentice_mechanic_tools_carry_forward",
            )
        },
        produces={"output": "ca/t777_apprentice_mechanic_tools_maximum_deduction"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_mechanic_tools",
            "bound": "ca/t777_apprentice_mechanic_tools_maximum_deduction",
        },
        produces={"output": "ca/t777_line_10"},
    ),
}


# The selections of the artists' employment expenses limit and line 14, in
# `03q_t777_artists_employment_expenses_maximum.yaml` (Guide T4044 "Part 1 - Artists' employment
# expenses").
ARTISTS_STEPS = {
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_artists_employment_income",
            "bound": "ca/t777_work_space_employment_income",
        },
        produces={"output": "ca/t777_artists_employment_income_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/t777_artists_expenses_paid", "ca/t777_artists_expenses_carry_forward")
        },
        produces={"output": "ca/t777_artists_expenses_available"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t777_artists_employment_expenses_rate"},
        consumes={"base": "ca/t777_artists_employment_income_checked"},
        produces={"output": "ca/t777_artists_income_twenty_percent"},
    ),
    CapabilitySelection(
        name="ca/lesser_of_with_maximum",
        params={"maximum": "ca/t777_artists_employment_expenses_maximum"},
        consumes={"amounts": ("ca/t777_artists_income_twenty_percent",)},
        produces={"output": "ca/t777_artists_limit_before_deductions"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_musical_instrument_expenses",
                "ca/t777_line_13",
                "ca/t777_artists_vehicle_interest_deducted",
                "ca/t777_artists_vehicle_cca_deducted",
            )
        },
        produces={"output": "ca/t777_artists_deductions_from_artistic_income"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t777_artists_limit_before_deductions",
            "less": "ca/t777_artists_deductions_from_artistic_income",
        },
        produces={"output": "ca/t777_artists_limit"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t777_artists_expenses_available", "ca/t777_artists_limit")},
        produces={"output": "ca/t777_artists_employment_expenses_maximum_deduction"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t777_artists_expenses_available",
            "less": "ca/t777_artists_employment_expenses_maximum_deduction",
        },
        produces={"output": "ca/t777_artists_expenses_carried_forward_out"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_artists_employment_expenses",
            "bound": "ca/t777_artists_employment_expenses_maximum_deduction",
        },
        produces={"output": "ca/t777_line_14"},
    ),
}


# The selections of the musical instrument expenses limit, in
# `03q_t777_musical_instrument_expenses_limit.yaml` (Guide T4044 "Part 2 - Musical instrument
# expenses").
MUSICAL_INSTRUMENT_STEPS = {
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_musician_employment_income",
            "bound": "ca/t777_work_space_employment_income",
        },
        produces={"output": "ca/t777_musician_employment_income_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t777_musical_instrument_expenses", "ca/t777_line_13")},
        produces={"output": "ca/t777_musical_instrument_expenses_deducted"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_accounting_and_legal_fees",
                "ca/t777_advertising_and_promotion",
                "ca/t777_line_3",
                "ca/t777_line_4",
                "ca/t777_lodging",
                "ca/t777_parking",
                "ca/t777_office_supplies",
                "ca/t777_other_expenses",
                "ca/t777_line_9",
                "ca/t777_line_10",
                "ca/t777_line_11",
                "ca/t777_artists_employment_expenses",
                "ca/rpp_deduction",
                "ca/union_dues",
            )
        },
        produces={"output": "ca/t777_employment_expenses_other_than_musical_instrument"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t777_musician_employment_income_checked",
            "less": "ca/t777_employment_expenses_other_than_musical_instrument",
        },
        produces={"output": "ca/t777_musical_instrument_expenses_maximum_deduction"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_musical_instrument_expenses_deducted",
            "bound": "ca/t777_musical_instrument_expenses_maximum_deduction",
        },
        produces={"output": "ca/t777_musical_instrument_expenses_checked"},
    ),
}


# The selections of the form's lines of page 1 to 3 and the line 11 total, in
# `03q_t777_lines.yaml` (the CCA steps of lines 13 and 25 stay in `03k_t777.yaml`). The line 3
# chart: line 20 is not a step of its own (line 30 is `ca/apply_ratio_or_zero` over the
# kilometres, rounded once). The line 16 chart: the employment income of line 51 is the return's own
# employment income (lines 10100 and 10400).
LINE_STEPS = {
    # Line 4 "Food, beverages, and entertainment expenses × 50%": the amount entered times the
    # printed 50% (the dataset's rate; the dataset's rounding rule rounds the product once).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t777_meals_rate"},
        consumes={"base": "ca/t777_food_beverages_entertainment"},
        produces={"output": "ca/t777_line_4"},
    ),
    # Line 29 "Add lines 21 to 28.": the chart's expenses, the CCA of line 25 among them.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_vehicle_fuel",
                "ca/t777_vehicle_maintenance",
                "ca/t777_vehicle_insurance",
                "ca/t777_vehicle_licence_and_registration",
                "ca/t777_line_25",
                "ca/t777_line_26",
                "ca/t777_vehicle_leasing_costs",
                "ca/t777_vehicle_other_expenses",
            )
        },
        produces={"output": "ca/t777_vehicle_total_expenses"},
    ),
    # Line 30 "Line 20 multiplied by line 29. Employment-use portion": line 29 times the quotient of
    # line 18 over line 19 (zero when no kilometres are entered), rounded once.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t777_vehicle_rounding"},
        consumes={
            "amount": "ca/t777_vehicle_total_expenses",
            "numerator": "ca/t777_employment_kilometres",
            "denominator": "ca/t777_total_kilometres",
        },
        produces={"output": "ca/t777_vehicle_employment_use"},
    ),
    # Line 31: the filer's amount is refused above line 30 (the T4044 guide: expenses must exceed
    # the allowance).
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_vehicle_allowances",
            "bound": "ca/t777_vehicle_employment_use",
        },
        produces={"output": "ca/t777_vehicle_allowances_checked"},
    ),
    # Line 32 "Line 30 minus line 31. Enter this amount on line 3 of page 1.": the form prints no
    # floor; line 31 is checked above, so the figure is never negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t777_vehicle_employment_use",
            "less": "ca/t777_vehicle_allowances_checked",
        },
        produces={"output": "ca/t777_line_3"},
    ),
    # Line 47 "Add lines 42 to 46.": the work-space expenses.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_work_space_electricity_heat_water_internet",
                "ca/t777_work_space_maintenance",
                "ca/t777_work_space_home_insurance",
                "ca/t777_work_space_property_taxes",
                "ca/t777_work_space_other_expenses",
            )
        },
        produces={"output": "ca/t777_work_space_expenses"},
    ),
    # Line 50 "Line 48 plus line 49 =": the employment-use amount and the amount carried forward.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_work_space_employment_use_amount",
                "ca/t777_work_space_carried_forward",
            )
        },
        produces={"output": "ca/t777_work_space_total_amount"},
    ),
    # Line 51 "Enter your employment income.": lines 10100 and 10400 of the return (the same reading
    # as #443, see the ticket's checks).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/employment_income", "ca/other_employment_income")},
        produces={"output": "ca/t777_work_space_employment_income"},
    ),
    # Line 52 "Enter any amounts from line 15 of page 1 and lines 20700 and 21200 of your return
    # that relate to your employment income.": all three in full (the return's only employment).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_line_15",
                "ca/rpp_deduction",
                "ca/union_dues",
            )
        },
        produces={"output": "ca/t777_work_space_employment_offsets"},
    ),
    # Line 53 "Line 51 minus line 52 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t777_work_space_employment_income",
            "less": "ca/t777_work_space_employment_offsets",
        },
        produces={"output": "ca/t777_work_space_income_limit"},
    ),
    # Line 54 "Enter whichever is less: Amount from line 50 or line 53.": the work-space expenses,
    # on line 16 of page 1.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/t777_work_space_total_amount",
                "ca/t777_work_space_income_limit",
            )
        },
        produces={"output": "ca/t777_line_16"},
    ),
    # Line 55 "Line 50 minus line 53 (if negative, enter "0")": the work-space expenses available to
    # use in future years (the line 49 of next year).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t777_work_space_total_amount",
            "less": "ca/t777_work_space_income_limit",
        },
        produces={"output": "ca/t777_work_space_carried_forward_out"},
    ),
    # Line 41 "Total labour mobility deduction for the year (maximum $4,000)": the line 39
    # amounts of the relocation copies, totalled, at most the maximum.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t777_relocation.t777_relocation_deduction"},
        produces={"output": "ca/t777_relocation_deduction_total"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/t777_line_11_maximum"},
        consumes={},
        produces={"output": "ca/t777_line_11_maximum"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_relocation_deduction_total",
            "bound": "ca/t777_line_11_maximum",
        },
        produces={"output": "ca/t777_line_11"},
    ),
    # Line 15 "Add lines 1 to 14.": the page 1 expenses and lines 3, 4, 9, 11 and 13.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_accounting_and_legal_fees",
                "ca/t777_advertising_and_promotion",
                "ca/t777_line_3",
                "ca/t777_line_4",
                "ca/t777_lodging",
                "ca/t777_parking",
                "ca/t777_office_supplies",
                "ca/t777_other_expenses",
                "ca/t777_line_9",
                "ca/t777_line_10",
                "ca/t777_line_11",
                "ca/t777_musical_instrument_expenses",
                "ca/t777_line_13",
                "ca/t777_line_14",
            )
        },
        produces={"output": "ca/t777_line_15"},
    ),
    # Line 17 "Line 15 plus line 16. Enter this amount on line 22900 of your return. Total
    # expenses": the total the return reads as T1 line 22900.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t777_line_15", "ca/t777_line_16")},
        produces={"output": "ca/t777_line_17"},
    ),
}

# The selections of the relocation form `ca/t777_relocation`, one copy for each relocation of
# `ca/t777_relocations`, in `03r_t777_relocation.yaml`. Line 37 "Add lines 33 to 36", line 38 the
# employment income of the relocation times 50%, line 39 the least of lines 37 and 38 and the claim
# (at most $4,000) and line 40 "Line 37 minus line 39".
RELOCATION_STEPS = {
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t777_relocation_carried_forward",
                "ca/t777_relocation_transportation",
                "ca/t777_relocation_meals",
                "ca/t777_relocation_lodging",
            )
        },
        produces={"output": "ca/t777_relocation_total"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t777_relocation_income_rate"},
        consumes={"base": "ca/t777_relocation_tradesperson_income"},
        produces={"output": "ca/t777_relocation_income_limit"},
    ),
    CapabilitySelection(
        name="ca/lesser_of_with_maximum",
        params={"maximum": "ca/t777_relocation_maximum"},
        consumes={
            "amounts": (
                "ca/t777_relocation_total",
                "ca/t777_relocation_income_limit",
                "ca/t777_relocation_claim",
            )
        },
        produces={"output": "ca/t777_relocation_deduction"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t777_relocation_total",
            "less": "ca/t777_relocation_deduction",
        },
        produces={"output": "ca/t777_relocation_carried_forward_out"},
    ),
}

# The form `ca/t777_relocation`: its instances, its exports (line 39 and line 40, read by the form
# `ca/t777` as `ca/t777_relocation.<export>`), and the fields of its record list (its inputs).
RELOCATION_FORM = "ca/t777_relocation"
RELOCATION_INSTANCES = "ca/t777_relocations"
RELOCATION_EXPORTS = (
    "ca/t777_relocation_deduction",
    "ca/t777_relocation_carried_forward_out",
)
RELOCATION_FIELDS = frozenset(
    {
        "ca/t777_relocation_carried_forward",
        "ca/t777_relocation_transportation",
        "ca/t777_relocation_meals",
        "ca/t777_relocation_lodging",
        "ca/t777_relocation_tradesperson_income",
        "ca/t777_relocation_claim",
    }
)
RELOCATION_DATASETS = frozenset({"ca/t777_relocation_income_rate", "ca/t777_relocation_maximum"})

# The entries of the return: the limit of the apprentice mechanic tools claim to the net income
# (`05x_t777_apprentice_mechanic_tools_net_income_check.yaml`); the return's line 22900 steps are in
# `manifest_families/other_employment_expenses.py`. The checked claim is a declared output, as no
# other step reads it.
OUTPUTS: frozenset[str] = frozenset(
    {"ca/t777_line_10_checked", "ca/t777_apprentice_mechanic_tools_carried_forward_out"}
)
STEPS: set[CapabilitySelection] = {
    # Form T777 line 10, the export of the form ca/t777 (one record), read as its total.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t777.t777_line_10"},
        produces={"output": "ca/t777_line_10_total"},
    ),
    # The net income plus the claim, never below zero.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/net_income_signed", "ca/t777_line_10_total")},
        produces={"output": "ca/t777_apprentice_mechanic_tools_net_income_limit"},
    ),
    # The claim is refused above it, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t777_line_10_total",
            "bound": "ca/t777_apprentice_mechanic_tools_net_income_limit",
        },
        produces={"output": "ca/t777_line_10_checked"},
    ),
    # The form's maximum deduction, read as its total.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t777.t777_apprentice_mechanic_tools_maximum_deduction"},
        produces={"output": "ca/t777_apprentice_mechanic_tools_maximum_deduction_total"},
    ),
    # The maximum allowed: the lesser of it and the net income limit.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/t777_apprentice_mechanic_tools_maximum_deduction_total",
                "ca/t777_apprentice_mechanic_tools_net_income_limit",
            )
        },
        produces={"output": "ca/t777_apprentice_mechanic_tools_maximum_allowed"},
    ),
    # The unused amount carried to 2026.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/t777_apprentice_mechanic_tools_maximum_allowed",
            "less": "ca/t777_line_10_checked",
        },
        produces={"output": "ca/t777_apprentice_mechanic_tools_carried_forward_out"},
    ),
}
T777_LINE_10_PER_FORM = RecordListKind("ca/t777.t777_line_10", fields=(T777_LINE_10,))
T777_MAXIMUM_PER_FORM = RecordListKind(
    "ca/t777.t777_apprentice_mechanic_tools_maximum_deduction",
    fields=(T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION,),
)
WIRING: set[object] = {
    (RecordTotal, frozenset({T777_LINE_10_PER_FORM}), frozenset({T777_LINE_10_TOTAL})),
    (
        SumNotBelowZero,
        frozenset({NET_INCOME_SIGNED, T777_LINE_10_TOTAL}),
        frozenset({T777_APPRENTICE_MECHANIC_TOOLS_NET_INCOME_LIMIT}),
    ),
    (
        AtMost,
        frozenset({T777_LINE_10_TOTAL, T777_APPRENTICE_MECHANIC_TOOLS_NET_INCOME_LIMIT}),
        frozenset({T777_LINE_10_CHECKED}),
    ),
    (
        RecordTotal,
        frozenset({T777_MAXIMUM_PER_FORM}),
        frozenset({T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION_TOTAL}),
    ),
    (
        LesserOf,
        frozenset(
            {
                T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION_TOTAL,
                T777_APPRENTICE_MECHANIC_TOOLS_NET_INCOME_LIMIT,
            }
        ),
        frozenset({T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_ALLOWED}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_ALLOWED, T777_LINE_10_CHECKED}),
        frozenset({T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT}),
    ),
}
