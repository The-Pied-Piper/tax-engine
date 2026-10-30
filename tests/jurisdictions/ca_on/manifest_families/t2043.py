"""The CA-ON manifest entries of Form T2043 (see `test_manifest.py` and `test_manifest_t2043.py`).

T2043 is a form of the manifest of its own: its selections belong to the form `ca/t2043`
(`FORM_STEPS`), which has no instances list, so it runs once. Its Part 1 total and its Part 2
provinces read the Chart A amounts of each Form T2042 statement (`ca/t2042.<export>`, one record for
each statement, in `t2042.py`), its Part 5 reads its own eight partnership credits (the manifest
inputs `INPUTS`), and it exports line 5D, "Total credit for all businesses", which the return adds
into line 48200 (`ca/t2043.fuel_charge_credit_farmers`, in `14_refund.yaml`). The return selects no
step of the form (`STEPS` and `OUTPUTS` are empty), and the form's Chart A steps are selections of
`ca/t2042`, listed in `t2042.py`.

Parts 3 and 4 total the Chart B and Chart C records of each statement (`ca/t2042.<export>`): Part 3
lines 67067 to 67076 and Part 4 amounts 4A to 4H (the Chart C amounts 7 of the eight provinces) and
amount 4I, which line 5B takes. Box 67062 (`BOX_67062_STEPS`) totals the statements present in each
of the nine places and counts the statements, then counts the pairs of places that a statement
count above 1 and two present places make. The partnership credit tie
(`PARTNERSHIP_CREDIT_TIE_STEPS`) totals line 9951 of Form T2042 over the statements and checks it
against amount 5C. So `FORM_STEPS` holds the 62 selections of the form, and
the form exports line 5D, "Total credit for all businesses", and the box, which nothing on the
return reads. The return totals the line 5D export into one kind
(`ca/fuel_charge_credit_farmers_total`, line 47556) in `STEPS`, because a form with no instances
exports its Decimal as a one-field record list that a return-level sum cannot take directly.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.threshold_gate import ThresholdGate
from tax_engine.jurisdictions.ca.catalog import (
    FARM_FUEL_CHARGE_CREDIT_TOTAL,
    FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_AB,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_MB,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_NB,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_NL,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_NS,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_ON,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_PE,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_SK,
    FUEL_CHARGE_CHART_B_SALARIES_AB,
    FUEL_CHARGE_CHART_B_SALARIES_MB,
    FUEL_CHARGE_CHART_B_SALARIES_NB,
    FUEL_CHARGE_CHART_B_SALARIES_NL,
    FUEL_CHARGE_CHART_B_SALARIES_NS,
    FUEL_CHARGE_CHART_B_SALARIES_ON,
    FUEL_CHARGE_CHART_B_SALARIES_PE,
    FUEL_CHARGE_CHART_B_SALARIES_SK,
    FUEL_CHARGE_CHART_B_TOTAL_GROSS_INCOME,
    FUEL_CHARGE_CHART_B_TOTAL_SALARIES,
    FUEL_CHARGE_CHART_C_TOTAL_AB,
    FUEL_CHARGE_CHART_C_TOTAL_MB,
    FUEL_CHARGE_CHART_C_TOTAL_NB,
    FUEL_CHARGE_CHART_C_TOTAL_NL,
    FUEL_CHARGE_CHART_C_TOTAL_NS,
    FUEL_CHARGE_CHART_C_TOTAL_ON,
    FUEL_CHARGE_CHART_C_TOTAL_PE,
    FUEL_CHARGE_CHART_C_TOTAL_SK,
    FUEL_CHARGE_CREDIT_AB,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_CREDIT_FARMERS_TOTAL,
    FUEL_CHARGE_CREDIT_MB,
    FUEL_CHARGE_CREDIT_NB,
    FUEL_CHARGE_CREDIT_NL,
    FUEL_CHARGE_CREDIT_NS,
    FUEL_CHARGE_CREDIT_ON,
    FUEL_CHARGE_CREDIT_PE,
    FUEL_CHARGE_CREDIT_SK,
    FUEL_CHARGE_EXPENSES_AB,
    FUEL_CHARGE_EXPENSES_MB,
    FUEL_CHARGE_EXPENSES_NB,
    FUEL_CHARGE_EXPENSES_NL,
    FUEL_CHARGE_EXPENSES_NS,
    FUEL_CHARGE_EXPENSES_ON,
    FUEL_CHARGE_EXPENSES_PE,
    FUEL_CHARGE_EXPENSES_SK,
    FUEL_CHARGE_FARM_STATEMENT_COUNT,
    FUEL_CHARGE_FARMS_IN_PROVINCE_AB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NL,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NS,
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_IN_PROVINCE_PE,
    FUEL_CHARGE_FARMS_IN_PROVINCE_SK,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_MULTIPLE_PROVINCES_BOX,
    FUEL_CHARGE_PART_2_TOTAL,
    FUEL_CHARGE_PART_4_TOTAL,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PART_5B_CREDIT,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_AB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_MB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NL,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NS,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_ON,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_PE,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_SK,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL,
)
from tax_engine.jurisdictions.ca_on.capabilities.record_count import RecordCount
from tests.jurisdictions.ca_on.manifest_families.t2042 import (
    FARM_AMOUNT_8_AB_PER_STATEMENT,
    FARM_AMOUNT_8_MB_PER_STATEMENT,
    FARM_AMOUNT_8_NB_PER_STATEMENT,
    FARM_AMOUNT_8_NL_PER_STATEMENT,
    FARM_AMOUNT_8_NS_PER_STATEMENT,
    FARM_AMOUNT_8_ON_PER_STATEMENT,
    FARM_AMOUNT_8_PE_PER_STATEMENT,
    FARM_AMOUNT_8_SK_PER_STATEMENT,
    FARM_CHART_A_GROSS_EXPENSES_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_AB_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_MB_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_NB_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_NL_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_NS_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_ON_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_PE_PER_STATEMENT,
    FARM_CHART_B_GROSS_INCOME_SK_PER_STATEMENT,
    FARM_CHART_B_ROW_2_WHEN_IN_USE_PER_STATEMENT,
    FARM_CHART_B_ROW_5_WHEN_IN_USE_PER_STATEMENT,
    FARM_CHART_B_SALARIES_AB_PER_STATEMENT,
    FARM_CHART_B_SALARIES_MB_PER_STATEMENT,
    FARM_CHART_B_SALARIES_NB_PER_STATEMENT,
    FARM_CHART_B_SALARIES_NL_PER_STATEMENT,
    FARM_CHART_B_SALARIES_NS_PER_STATEMENT,
    FARM_CHART_B_SALARIES_ON_PER_STATEMENT,
    FARM_CHART_B_SALARIES_PE_PER_STATEMENT,
    FARM_CHART_B_SALARIES_SK_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_AB_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_MB_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_NB_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_NL_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_NS_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_ON_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_PE_PER_STATEMENT,
    FARM_CHART_C_AMOUNT_SK_PER_STATEMENT,
    FARM_FUEL_CHARGE_CREDIT_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_AB_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_MB_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_NB_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_NL_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_NS_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_ON_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_PE_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_SK_PER_STATEMENT,
)

# The eight provinces in the form's order (ON, MB, SK, AB, NS, PE, NL, NB): the Part 2 line of each
# province's farming expenses (67063 to 67066 and 67091 to 67094), its credit (2A to 2H) and the
# partnership credit of Part 5 (67079 to 67082 and 67103 to 67106).
PROVINCE_EXPENSE_RECORDS = (
    FARM_AMOUNT_8_ON_PER_STATEMENT,
    FARM_AMOUNT_8_MB_PER_STATEMENT,
    FARM_AMOUNT_8_SK_PER_STATEMENT,
    FARM_AMOUNT_8_AB_PER_STATEMENT,
    FARM_AMOUNT_8_NS_PER_STATEMENT,
    FARM_AMOUNT_8_PE_PER_STATEMENT,
    FARM_AMOUNT_8_NL_PER_STATEMENT,
    FARM_AMOUNT_8_NB_PER_STATEMENT,
)
PROVINCE_EXPENSES = (
    FUEL_CHARGE_EXPENSES_ON,
    FUEL_CHARGE_EXPENSES_MB,
    FUEL_CHARGE_EXPENSES_SK,
    FUEL_CHARGE_EXPENSES_AB,
    FUEL_CHARGE_EXPENSES_NS,
    FUEL_CHARGE_EXPENSES_PE,
    FUEL_CHARGE_EXPENSES_NL,
    FUEL_CHARGE_EXPENSES_NB,
)
PROVINCE_CREDITS = (
    FUEL_CHARGE_CREDIT_ON,
    FUEL_CHARGE_CREDIT_MB,
    FUEL_CHARGE_CREDIT_SK,
    FUEL_CHARGE_CREDIT_AB,
    FUEL_CHARGE_CREDIT_NS,
    FUEL_CHARGE_CREDIT_PE,
    FUEL_CHARGE_CREDIT_NL,
    FUEL_CHARGE_CREDIT_NB,
)
PARTNERSHIP_CREDITS = (
    FUEL_CHARGE_PARTNERSHIP_CREDIT_ON,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_MB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_SK,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_AB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NS,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_PE,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NL,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NB,
)

# The eight partnership credits are manifest inputs: the form has no instances, so they are the
# Form's own inputs in the manifest, read by Part 5 line 5C only.
INPUTS = frozenset(identifier.identifier for identifier in PARTNERSHIP_CREDITS)

# The form's selections, one for each line that computes; line 5B has no selection yet.
FORM_STEPS = {
    # Form T2043 Part 1 line 67061 "Total gross farming expenses for all of your businesses: Add
    # amount 6 of every Chart A": the total of amount 6 over the statements.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_a_gross_expenses"},
        produces={"output": "ca/fuel_charge_gross_farming_expenses"},
    ),
    # Form T2043 Part 2 lines 67063 to 67066 and 67091 to 67094: "Add all farming expenses in ON
    # from amount 8 of Chart A" and the same for each province, the total of amount 8 over the
    # statements of the province (the others give 0 for it).
    *(
        CapabilitySelection(
            name="core/record_total",
            params={},
            consumes={"records": record.identifier},
            produces={"output": expense.identifier},
        )
        for record, expense in zip(PROVINCE_EXPENSE_RECORDS, PROVINCE_EXPENSES, strict=True)
    ),
    # Form T2043 Part 2 lines 2A to 2H "ON payment rate 0.229%" and the same for each province: the
    # province's expenses at the payment rate, rounded half-up to the cent.
    *(
        CapabilitySelection(
            name="core/apply_rate",
            params={"rate": "ca/fuel_charge_payment_rate"},
            consumes={"base": expense.identifier},
            produces={"output": credit.identifier},
        )
        for expense, credit in zip(PROVINCE_EXPENSES, PROVINCE_CREDITS, strict=True)
    ),
    # Form T2043 Part 2 line 2I "Total: Add amounts 2A to 2H": the sum of the eight credits.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": tuple(credit.identifier for credit in PROVINCE_CREDITS)},
        produces={"output": "ca/fuel_charge_part_2_total"},
    ),
    # Form T2043 Part 5 line 5A "Enter amount 2I", for a total gross farming expenses of at least
    # $25,000 (Part 1 Note 1 "If your total gross farming expenses for all businesses are $25,000
    # or more, you are eligible to claim the credit."): 2I when line 67061 reaches the threshold,
    # else 0.
    CapabilitySelection(
        name="ca/threshold_gate",
        params={"threshold": "ca/fuel_charge_expense_threshold"},
        consumes={
            "amount": "ca/fuel_charge_part_2_total",
            "gate": "ca/fuel_charge_gross_farming_expenses",
        },
        produces={"output": "ca/fuel_charge_part_5a_credit"},
    ),
    # Form T2043 Part 5 line 5C "Total credit allocated from partnerships: Add lines 67079 to 67082
    # and lines 67103 to 67106": the eight partnership credits, not gated.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": tuple(credit.identifier for credit in PARTNERSHIP_CREDITS)},
        produces={"output": FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL.identifier},
    ),
    # Form T2043 Part 5 line 5B "Enter amount 4I" (the total of Part 4 amounts 4A to 4H), gated like
    # 5A by the same threshold on line 67061.
    CapabilitySelection(
        name="ca/threshold_gate",
        params={"threshold": "ca/fuel_charge_expense_threshold"},
        consumes={
            "amount": "ca/fuel_charge_part_4_total",
            "gate": "ca/fuel_charge_gross_farming_expenses",
        },
        produces={"output": "ca/fuel_charge_part_5b_credit"},
    ),
    # Form T2043 Part 5 line 5D "Total credit for all businesses: Amount 5A plus amount 5B plus
    # amount 5C (enter this amount on line 47556 of your income tax and benefit return)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fuel_charge_part_5a_credit",
                "ca/fuel_charge_part_5b_credit",
                "ca/fuel_charge_partnership_credit_total",
            )
        },
        produces={"output": "ca/fuel_charge_credit_farmers"},
    ),
}

# Form T2043 exports line 5D, which the return reads as `ca/t2043.fuel_charge_credit_farmers` in its
# line 48200 sum. No other line is read by the return.
FORM_EXPORTS = (
    FUEL_CHARGE_CREDIT_FARMERS.identifier,
    "ca/fuel_charge_chart_b_gross_income_on",
    "ca/fuel_charge_chart_b_gross_income_mb",
    "ca/fuel_charge_chart_b_gross_income_sk",
    "ca/fuel_charge_chart_b_gross_income_ab",
    "ca/fuel_charge_chart_b_gross_income_ns",
    "ca/fuel_charge_chart_b_gross_income_pe",
    "ca/fuel_charge_chart_b_gross_income_nl",
    "ca/fuel_charge_chart_b_gross_income_nb",
    "ca/fuel_charge_chart_b_salaries_on",
    "ca/fuel_charge_chart_b_salaries_mb",
    "ca/fuel_charge_chart_b_salaries_sk",
    "ca/fuel_charge_chart_b_salaries_ab",
    "ca/fuel_charge_chart_b_salaries_ns",
    "ca/fuel_charge_chart_b_salaries_pe",
    "ca/fuel_charge_chart_b_salaries_nl",
    "ca/fuel_charge_chart_b_salaries_nb",
    "ca/fuel_charge_chart_b_total_gross_income",
    "ca/fuel_charge_chart_b_total_salaries",
    "ca/fuel_charge_multiple_provinces_box",
    "ca/farm_fuel_charge_credit_total_checked",
)

# The return declares no output for the form: its line 47556 is part of the sum of line 48200, and
# box 67062 is an export nothing on the return reads.
OUTPUTS: frozenset[str] = frozenset()

# The return's own step for the form: line 47556 totals the form's export, one record of
# `ca/t2043.fuel_charge_credit_farmers`, into `ca/fuel_charge_credit_farmers_total`, which the line
# 48200 sum takes (in `14_refund.yaml`). The form itself selects none of these.
FUEL_CHARGE_CREDIT_FARMERS_PER_FORM = RecordListKind(
    "ca/t2043.fuel_charge_credit_farmers", fields=(FUEL_CHARGE_CREDIT_FARMERS,)
)

# Form T2043 Parts 3 and 4: the record totals of the statements' Chart B and Chart C.
PART_3_AND_4_STEPS = {
    # Form T2043 Part 3 line 67067 "Add all ON amounts from row 1 of every Chart B" (Ontario).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_on"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_on"},
    ),
    # Form T2043 Part 3 line 67068 "Add all MB amounts from row 1 of every Chart B" (Manitoba).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_mb"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_mb"},
    ),
    # Form T2043 Part 3 line 67069 "Add all SK amounts from row 1 of every Chart B"
    # (Saskatchewan).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_sk"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_sk"},
    ),
    # Form T2043 Part 3 line 67070 "Add all AB amounts from row 1 of every Chart B" (Alberta).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_ab"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_ab"},
    ),
    # Form T2043 Part 3 line 67095 "Add all NS amounts from row 1 of every Chart B" (Nova Scotia).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_ns"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_ns"},
    ),
    # Form T2043 Part 3 line 67096 "Add all PE amounts from row 1 of every Chart B" (Prince Edward
    # Island).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_pe"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_pe"},
    ),
    # Form T2043 Part 3 line 67097 "Add all NL amounts from row 1 of every Chart B" (Newfoundland
    # and Labrador).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_nl"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_nl"},
    ),
    # Form T2043 Part 3 line 67098 "Add all NB amounts from row 1 of every Chart B" (New
    # Brunswick).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_gross_income_nb"},
        produces={"output": "ca/fuel_charge_chart_b_gross_income_nb"},
    ),
    # Form T2043 Part 3 line 67071 "Add all ON amounts from row 4 of every Chart B" (Ontario).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_on"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_on"},
    ),
    # Form T2043 Part 3 line 67072 "Add all MB amounts from row 4 of every Chart B" (Manitoba).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_mb"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_mb"},
    ),
    # Form T2043 Part 3 line 67073 "Add all SK amounts from row 4 of every Chart B"
    # (Saskatchewan).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_sk"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_sk"},
    ),
    # Form T2043 Part 3 line 67074 "Add all AB amounts from row 4 of every Chart B" (Alberta).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_ab"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_ab"},
    ),
    # Form T2043 Part 3 line 67099 "Add all NS amounts from row 4 of every Chart B" (Nova Scotia).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_ns"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_ns"},
    ),
    # Form T2043 Part 3 line 67100 "Add all PE amounts from row 4 of every Chart B" (Prince Edward
    # Island).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_pe"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_pe"},
    ),
    # Form T2043 Part 3 line 67101 "Add all NL amounts from row 4 of every Chart B" (Newfoundland
    # and Labrador).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_nl"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_nl"},
    ),
    # Form T2043 Part 3 line 67102 "Add all NB amounts from row 4 of every Chart B" (New
    # Brunswick).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_salaries_nb"},
        produces={"output": "ca/fuel_charge_chart_b_salaries_nb"},
    ),
    # Form T2043 Part 3 line 67075 "Total gross income in all provinces and territories from all
    # farming businesses: Add the amount from row 2 of every Chart B you fill in".
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_row_2_when_in_use"},
        produces={"output": "ca/fuel_charge_chart_b_total_gross_income"},
    ),
    # Form T2043 Part 3 line 67076 "Total salaries and wages paid to employees in all provinces
    # and territories from all farming businesses: Add the amount from row 5 of every Chart B you
    # fill in".
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_b_row_5_when_in_use"},
        produces={"output": "ca/fuel_charge_chart_b_total_salaries"},
    ),
    # Form T2043 Part 4 amount 4A "Total credit in ON for all businesses: Add amount 7 of every
    # Chart C" (Ontario).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_on"},
        produces={"output": "ca/fuel_charge_chart_c_total_on"},
    ),
    # Form T2043 Part 4 amount 4B "Total credit in MB for all businesses: Add amount 8 of every
    # Chart C" (Manitoba).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_mb"},
        produces={"output": "ca/fuel_charge_chart_c_total_mb"},
    ),
    # Form T2043 Part 4 amount 4C "Total credit in SK for all businesses: Add amount 9 of every
    # Chart C" (Saskatchewan).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_sk"},
        produces={"output": "ca/fuel_charge_chart_c_total_sk"},
    ),
    # Form T2043 Part 4 amount 4D "Total credit in AB for all businesses: Add amount 10 of every
    # Chart C" (Alberta).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_ab"},
        produces={"output": "ca/fuel_charge_chart_c_total_ab"},
    ),
    # Form T2043 Part 4 amount 4E "Total credit in NS for all businesses: Add amount 11 of every
    # Chart C" (Nova Scotia).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_ns"},
        produces={"output": "ca/fuel_charge_chart_c_total_ns"},
    ),
    # Form T2043 Part 4 amount 4F "Total credit in PE for all businesses: Add amount 12 of every
    # Chart C" (Prince Edward Island).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_pe"},
        produces={"output": "ca/fuel_charge_chart_c_total_pe"},
    ),
    # Form T2043 Part 4 amount 4G "Total credit in NL for all businesses: Add amount 13 of every
    # Chart C" (Newfoundland and Labrador).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_nl"},
        produces={"output": "ca/fuel_charge_chart_c_total_nl"},
    ),
    # Form T2043 Part 4 amount 4H "Total credit in NB for all businesses: Add amount 14 of every
    # Chart C" (New Brunswick).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_chart_c_amount_nb"},
        produces={"output": "ca/fuel_charge_chart_c_total_nb"},
    ),
    # Form T2043 Part 4 amount 4I "Total: Add amounts 4A to 4H (enter this total at amount 5B)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fuel_charge_chart_c_total_on",
                "ca/fuel_charge_chart_c_total_mb",
                "ca/fuel_charge_chart_c_total_sk",
                "ca/fuel_charge_chart_c_total_ab",
                "ca/fuel_charge_chart_c_total_ns",
                "ca/fuel_charge_chart_c_total_pe",
                "ca/fuel_charge_chart_c_total_nl",
                "ca/fuel_charge_chart_c_total_nb",
            )
        },
        produces={"output": "ca/fuel_charge_part_4_total"},
    ),
}

FORM_STEPS |= PART_3_AND_4_STEPS

# Form T2043 box 67062 "Tick this box if you have multiple farming businesses with one or more
# permanent establishments in multiple provinces or territories": the statements present in each of
# the nine places (`ca/t2042.farm_present_amount_<place>`, one record for each statement) totalled
# over the statements, the count of the statements (one record for each, the ON record list), and
# the box, which is 1 when there are more than one statement and two places each have a statement
# (`ca/fuel_charge_multiple_provinces_box_conditions`, 36 pairs of places). The box is a count, not
# a dollars-and-cents figure.
BOX_67062_PLACE_RECORDS = (
    FARM_PRESENT_AMOUNT_ON_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_MB_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_SK_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_AB_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_NS_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_PE_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_NL_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_NB_PER_STATEMENT,
    FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT_PER_STATEMENT,
)
BOX_67062_PLACE_TOTALS = (
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_SK,
    FUEL_CHARGE_FARMS_IN_PROVINCE_AB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NS,
    FUEL_CHARGE_FARMS_IN_PROVINCE_PE,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NL,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NB,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
)
BOX_67062_STEPS = {
    *(
        CapabilitySelection(
            name="core/record_total",
            params={},
            consumes={"records": record.identifier},
            produces={"output": total.identifier},
        )
        for record, total in zip(BOX_67062_PLACE_RECORDS, BOX_67062_PLACE_TOTALS, strict=True)
    ),
    # The count of the statements: one record for each statement, read through its ON record list.
    CapabilitySelection(
        name="ca-on/record_count",
        params={},
        consumes={"records": FARM_PRESENT_AMOUNT_ON_PER_STATEMENT.identifier},
        produces={"output": FUEL_CHARGE_FARM_STATEMENT_COUNT.identifier},
    ),
    # The box: 1 when the statement count is more than 1 and two of the nine places each total more
    # than 0 (one condition for each pair of places, in the form's order), else 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/fuel_charge_multiple_provinces_box_conditions"},
        consumes={
            "counts": (FUEL_CHARGE_FARM_STATEMENT_COUNT.identifier,),
            "amounts": tuple(total.identifier for total in BOX_67062_PLACE_TOTALS),
        },
        produces={"output": FUEL_CHARGE_MULTIPLE_PROVINCES_BOX.identifier},
    ),
}

FORM_STEPS |= BOX_67062_STEPS

# Form T2043 note 2 and Form T2042 line 9951: the credit the partnerships allocated is on both
# forms, so line 9951 totalled over the statements may not be above amount 5C (the part
# `03v_t2043_partnership_credit_check.yaml`): a total above it is refused. Amount 5C may be more
# (AgriStability and AgriInvest filers put the credit on other forms' line 9951). The checked total
# is a form export.
PARTNERSHIP_CREDIT_TIE_STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": FARM_FUEL_CHARGE_CREDIT_PER_STATEMENT.identifier},
        produces={"output": FARM_FUEL_CHARGE_CREDIT_TOTAL.identifier},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": FARM_FUEL_CHARGE_CREDIT_TOTAL.identifier,
            "bound": FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL.identifier,
        },
        produces={"output": FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED.identifier},
    ),
}

FORM_STEPS |= PARTNERSHIP_CREDIT_TIE_STEPS

STEPS: set[CapabilitySelection] = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2043.fuel_charge_credit_farmers"},
        produces={"output": "ca/fuel_charge_credit_farmers_total"},
    ),
}

FORM_WIRING = {
    (
        RecordTotal,
        frozenset({FARM_CHART_A_GROSS_EXPENSES_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_GROSS_FARMING_EXPENSES}),
    ),
    *(
        (
            RecordTotal,
            frozenset({record}),
            frozenset({expense}),
        )
        for record, expense in zip(PROVINCE_EXPENSE_RECORDS, PROVINCE_EXPENSES, strict=True)
    ),
    *(
        (ApplyRate, frozenset({expense}), frozenset({credit}))
        for expense, credit in zip(PROVINCE_EXPENSES, PROVINCE_CREDITS, strict=True)
    ),
    (
        Sum,
        frozenset(PROVINCE_CREDITS),
        frozenset({FUEL_CHARGE_PART_2_TOTAL}),
    ),
    (
        ThresholdGate,
        frozenset({FUEL_CHARGE_PART_2_TOTAL, FUEL_CHARGE_GROSS_FARMING_EXPENSES}),
        frozenset({FUEL_CHARGE_PART_5A_CREDIT}),
    ),
    (
        Sum,
        frozenset(PARTNERSHIP_CREDITS),
        frozenset({FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL}),
    ),
    (
        ThresholdGate,
        frozenset({FUEL_CHARGE_PART_4_TOTAL, FUEL_CHARGE_GROSS_FARMING_EXPENSES}),
        frozenset({FUEL_CHARGE_PART_5B_CREDIT}),
    ),
    (
        Sum,
        frozenset(
            {
                FUEL_CHARGE_PART_5A_CREDIT,
                FUEL_CHARGE_PART_5B_CREDIT,
                FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL,
            }
        ),
        frozenset({FUEL_CHARGE_CREDIT_FARMERS}),
    ),
}

PART_3_AND_4_WIRING: set[Any] = {
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_ON_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_ON}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_MB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_MB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_SK_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_SK}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_AB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_AB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_NS_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_NS}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_PE_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_PE}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_NL_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_NL}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_GROSS_INCOME_NB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_GROSS_INCOME_NB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_ON_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_ON}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_MB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_MB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_SK_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_SK}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_AB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_AB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_NS_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_NS}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_PE_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_PE}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_NL_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_NL}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_SALARIES_NB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_SALARIES_NB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_ROW_2_WHEN_IN_USE_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_TOTAL_GROSS_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_B_ROW_5_WHEN_IN_USE_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_B_TOTAL_SALARIES}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_ON_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_ON}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_MB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_MB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_SK_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_SK}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_AB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_AB}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_NS_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_NS}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_PE_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_PE}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_NL_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_NL}),
    ),
    (
        RecordTotal,
        frozenset({FARM_CHART_C_AMOUNT_NB_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_CHART_C_TOTAL_NB}),
    ),
    (
        Sum,
        frozenset(
            {
                FUEL_CHARGE_CHART_C_TOTAL_ON,
                FUEL_CHARGE_CHART_C_TOTAL_MB,
                FUEL_CHARGE_CHART_C_TOTAL_SK,
                FUEL_CHARGE_CHART_C_TOTAL_AB,
                FUEL_CHARGE_CHART_C_TOTAL_NS,
                FUEL_CHARGE_CHART_C_TOTAL_PE,
                FUEL_CHARGE_CHART_C_TOTAL_NL,
                FUEL_CHARGE_CHART_C_TOTAL_NB,
            }
        ),
        frozenset({FUEL_CHARGE_PART_4_TOTAL}),
    ),
}

FORM_WIRING |= PART_3_AND_4_WIRING

BOX_67062_WIRING: set[Any] = {
    *(
        (RecordTotal, frozenset({record}), frozenset({total}))
        for record, total in zip(BOX_67062_PLACE_RECORDS, BOX_67062_PLACE_TOTALS, strict=True)
    ),
    (
        RecordCount,
        frozenset({FARM_PRESENT_AMOUNT_ON_PER_STATEMENT}),
        frozenset({FUEL_CHARGE_FARM_STATEMENT_COUNT}),
    ),
    (
        CountByConditions,
        frozenset({FUEL_CHARGE_FARM_STATEMENT_COUNT, *BOX_67062_PLACE_TOTALS}),
        frozenset({FUEL_CHARGE_MULTIPLE_PROVINCES_BOX}),
    ),
}

FORM_WIRING |= BOX_67062_WIRING

PARTNERSHIP_CREDIT_TIE_WIRING: set[Any] = {
    (
        RecordTotal,
        frozenset({FARM_FUEL_CHARGE_CREDIT_PER_STATEMENT}),
        frozenset({FARM_FUEL_CHARGE_CREDIT_TOTAL}),
    ),
    (
        AtMost,
        frozenset({FARM_FUEL_CHARGE_CREDIT_TOTAL, FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL}),
        frozenset({FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED}),
    ),
}

FORM_WIRING |= PARTNERSHIP_CREDIT_TIE_WIRING

WIRING: set[object] = {
    (
        RecordTotal,
        frozenset({FUEL_CHARGE_CREDIT_FARMERS_PER_FORM}),
        frozenset({FUEL_CHARGE_CREDIT_FARMERS_TOTAL}),
    ),
}
