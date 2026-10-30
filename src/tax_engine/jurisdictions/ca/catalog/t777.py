"""The federal catalog: Form T777, Statement of Employment Expenses, capital cost allowance schedule
for employees (Parts A and B, page 4 and page 5), the form `ca/t777`.

The row lists are built of the CCA table's own columns (`ca/cca_*`, declared in `personal_amounts`).
Part A has one list for Class 8 (line 13) and one for the vehicle classes 10, 54 and 55 (line 25),
Part B one list for Class 10.1 vehicles (line 25). The intermediate kinds are the steps between the
rows and the exports; the lines and the closing lists are the form's exports.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG
from tax_engine.jurisdictions.ca.catalog.income import CCA_SOLD_ZEPVS
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CHANGE_IN_USE,
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_DIEP_PROCEEDS,
    CCA_NO_PROPERTY_LEFT,
    CCA_PROCEEDS,
    CCA_RIIP_ADDITIONS,
    CCA_UCC_AT_END,
    CCA_UCC_AT_START,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_CHANGE_IN_USE,
    CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH,
    CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
    CCA_VEHICLE_SELLER_COST,
)

T777_VEHICLE_SALES_TAX_RATE = CATALOG.declare(
    "t777_vehicle_sales_tax_rate", Decimal, non_negative=True
)
"""GST plus PST, or HST, rate of the Class 54 sale, Form T777 Part A "Column 6: Proceeds of
dispositions in the year" for a zero-emission vehicle sold (Guide T4036 "Class 54 (30%)"): the rate
in percent, so 13 is 13%, a starting amount. Used when a Class 54 vehicle is sold from the vehicle
list, and the rate feeds the Class 10.1 limit with tax of Form T777 Part B (the prescribed amount
plus the same amount at this rate), which refuses a row above it. It is also the rate of Guide
T4044's "Eligible leasing costs" chart ("Use a GST rate of 5% or the HST rate applicable to your
province"), the one sales tax rate of the form."""

# The Part A columns of a row, in the order the table reads them: the columns the filer enters
# (class number, UCC at the start, additions, the AIIP and RIIP parts of the additions, proceeds,
# the DIEP part of the proceeds that `ca/cca_vehicle_proceeds` reads), then the claim (column 15,
# "CCA for the year") and the no-property-left tick the table reads.
T777_PART_A_COLUMNS = (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_START,
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_RIIP_ADDITIONS,
    CCA_PROCEEDS,
    CCA_DIEP_PROCEEDS,
    CCA_CLAIMED,
    CCA_NO_PROPERTY_LEFT,
)

# The Part A change in use answer and fair market value of a row (Guide T4044 2025, Part A column
# 3): the filer's yes or no answer and the figure the cost of additions must equal when it is yes.
T777_PART_A_CHANGE_IN_USE_COLUMNS = (
    CCA_CHANGE_IN_USE,
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE,
)

T777_CLASS_8_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_class_8_rows",
    fields=(*T777_PART_A_COLUMNS, *T777_PART_A_CHANGE_IN_USE_COLUMNS),
)
"""Part A rows of Class 8, Form T777 Part A "Class number" 8 (musical instruments, note (5)), which
feed line 13: one record for each row, holding columns 1 to 6 as the filer enters them (class
number, UCC at the start of the year (2), cost of additions (3), the AIIP or ZEV part of the
additions (4), the RIIP or ZEV part (5) and proceeds of dispositions (6)), the CCA for the year
(column 15, "column 13 multiplied by column 14 or lower amount"), and the no-property-left tick the
table reads. The form prints no DIEP or no-property-left column; those are 0 and the table reads
them as its own. The change in use answer and fair market value of column 3 are the filer's,
checked against the additions by `ca/cca_change_in_use_checks`."""

T777_VEHICLE_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_vehicle_rows",
    fields=(
        *T777_PART_A_COLUMNS,
        *T777_PART_A_CHANGE_IN_USE_COLUMNS,
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_SOLD_ZEPVS,
    ),
)
"""Part A rows of the vehicle classes 10, 54 and 55, Form T777 Part A "Class number" 10, 54 and 55,
which feed line 25: the same columns as the Class 8 rows, with the zero-emission passenger vehicles
of a Class 54 row sold in the year (Guide T4036 "Class 54 (30%)"), listed as vehicles, last. The
vehicle year, cost and government assistance are read by `ca/cca_vehicle_proceeds` for those
vehicles; the form prints none of them, so they are 0 for a row of the form."""

T777_CLASS_8_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_class_8_checked_rows",
    fields=T777_CLASS_8_ROWS.fields,
)
"""Class 8 rows that passed the checks of Form T777 Part A "Classes 8, 10, 54, and 55": one row for
each class, so a class number listed in an earlier row of the Class 8 list is refused. The rows are
passed on unchanged."""

T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_class_8_change_in_use_checked_rows",
    fields=T777_CLASS_8_ROWS.fields,
)
"""Class 8 rows checked for a change in use, Form T777 Part A column 3 "Cost of additions in the
year", Guide T4044 "Part A - Classes 8, 10, 54, and 55 property": the cost of additions of a Class 8
row answered as property that started being used for employment in the year must be its fair
market value at the time. The rows are passed on unchanged, with the same fields as the Class 8
rows, for the Class 8 claim and closing UCC to read."""

T777_VEHICLE_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_vehicle_checked_rows",
    fields=T777_VEHICLE_ROWS.fields,
)
"""Vehicle rows that passed the checks of Form T777 Part A "Classes 8, 10, 54, and 55": one row for
each class of 10, 54 and 55, so a "Class number" (column 1) listed in an earlier row of the vehicle
list is refused. The rows are passed on unchanged."""

T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_vehicle_change_in_use_checked_rows",
    fields=T777_VEHICLE_ROWS.fields,
)
"""Vehicle rows of Classes 10, 54 and 55 checked for a change in use, Form T777 Part A column 3
"Cost of additions in the year", Guide T4044 "Part A - Classes 8, 10, 54, and 55 property": the cost
of additions of a row answered as property that started being used for employment in the year must
be its fair market value at the time. The rows are passed on unchanged, with the same fields as the
vehicle rows, for the proceeds and the vehicle claim to read."""

T777_VEHICLE_ROWS_ADJUSTED = RecordListKind.declare(
    CATALOG,
    "t777_vehicle_rows_adjusted",
    fields=T777_PART_A_COLUMNS,
)
"""Part A rows of the vehicle classes with the proceeds of the sold zero-emission vehicles scaled
(Form T777 Part A columns 6 "Proceeds of dispositions in the year"): the vehicle list without the
year, cost, government assistance and sold vehicles, which `ca/cca_vehicle_proceeds` produces."""

T777_PART_B_COLUMNS = (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_START,
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_RIIP_ADDITIONS,
    CCA_PROCEEDS,
    CCA_CLAIMED,
    CCA_NO_PROPERTY_LEFT,
)

# The Part B columns of a row as the filer enters them: the form's first two columns, "Date acquired
# (yyyy-mm-dd)" (entered as its year) and "Cost of vehicle", then the columns of the table, then the
# Guide T4044 answers and figures for column 3: bought from a non-arm's-length person with its fair
# market value and the seller's cost, and the change in use with its fair market value.
T777_PART_B_ENTERED_COLUMNS = (
    *T777_PART_B_COLUMNS,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH,
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
    CCA_VEHICLE_SELLER_COST,
    CCA_VEHICLE_CHANGE_IN_USE,
    CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE,
)

T777_PART_B_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_part_b_rows",
    fields=T777_PART_B_ENTERED_COLUMNS,
)
"""Part B rows of Class 10.1 passenger vehicles, Form T777 Part B "List each passenger vehicle on a
separate line": one record for each vehicle, holding its class number (column 1), UCC at the start
of the year (column 2, note (11)), cost of additions in the year (column 3), the AIIP and RIIP
parts of the additions (notes (8) and (9)), proceeds of dispositions in the year (column 4), the
CCA for the year (column 7) and the tick "sold in the year" (no property left, the table's
no-property-left column), with the form's first two columns: the year of "Date acquired
(yyyy-mm-dd)" (required on every row, so never 0) and "Cost of vehicle" (0 when none is entered),
and the answers and figures the Guide asks of column 3: bought from a non-arm's-length person,
with the vehicle's fair market value and the seller's cost, and a change in use, with the fair
market value at the change, each answer 0 or 1 and each figure 0 when it does not apply. The Class
10.1 cost limit (Guide T4044) is checked on the additions (column 3) by
`ca/cca_vehicle_additions_checks`, whose passed rows (`t777_part_b_additions_checked_rows`) feed the
Part B claim. No line of the form reads the date acquired or the cost of vehicle (columns 5 to 8
read columns 2 and 3), so they are carried as entered. Feeds line 25."""

T777_PART_B_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_part_b_checked_rows",
    fields=T777_PART_B_ENTERED_COLUMNS,
)
"""Part B rows that passed the checks of Form T777 Part B: a vehicle is either owned from the
previous year (UCC at the start, note (11)) or bought in the year (additions), not both; proceeds
of dispositions are entered only with the "sold in the year" tick, note (11) and (12); and a tick
is entered only with proceeds. The rows are passed on unchanged."""

T777_PART_B_ADDITIONS_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_part_b_additions_checked_rows",
    fields=T777_PART_B_ENTERED_COLUMNS,
)
"""Part B rows checked for the Class 10.1 additions limit, Form T777 Part B "List each passenger
vehicle on a separate line": the cost of additions (column 3) of each Class 10.1 vehicle bought in
the year, checked to be not more than its limit with tax (Guide T4044 "$38,000 plus GST and PST, or
HST" for 2025). The rows are passed on unchanged, with the same fields as the Part B rows, for the
Part B claim to read."""

T777_PART_B_CLASS_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_part_b_class_checked_rows",
    fields=T777_PART_B_ENTERED_COLUMNS,
)
"""Part B rows checked for the Class 10.1 class condition, Form T777 Part B "List each passenger
vehicle on a separate line": the "Date acquired (yyyy-mm-dd)" (its year) and "Cost of vehicle" of
each Class 10.1 row (the date is required on every row), checked to meet one of the conditions of
Guide T4044 "Class 10.1" (acquired in 2025, it cost more than $38,000 before tax), else the vehicle
belongs in Class 10 and Part A. The rows are passed on unchanged, with the same fields as the Part B
rows, for the Part B claim to read."""

T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_part_b_non_arms_length_checked_rows",
    fields=T777_PART_B_ENTERED_COLUMNS,
)
"""Part B rows checked for the cost of a vehicle bought from a non-arm's-length person, Form T777
Part B column 3 "Cost of additions in the year", Guide T4044 "Part B - Class 10.1 property": the
capital cost of a Class 10.1 vehicle answered as bought from such a person must be the least of its
fair market value when acquired, $38,000 plus the GST and PST or HST on $38,000, and the seller's
cost. The rows are passed on unchanged, with the same fields as the Part B rows, for the Part B
claim to read."""

T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS = RecordListKind.declare(
    CATALOG,
    "t777_part_b_change_in_use_checked_rows",
    fields=T777_PART_B_ENTERED_COLUMNS,
)
"""Part B rows checked for a change in use, Form T777 Part B column 3 "Cost of additions in the
year", Guide T4044 "Part B - Class 10.1 property": the cost of additions of a Class 10.1 vehicle
answered as a personal vehicle that started being used for employment in the year must be its fair
market value at the time. The rows are passed on unchanged, with the same fields as the Part B
rows, for the Part B claim to read."""

T777_PART_B_CLOSING_UCC = RecordListKind.declare(
    CATALOG,
    "t777_part_b_closing_ucc",
    fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_END),
)
"""Closing UCC of Part B, Form T777 Part B "Column 8: UCC at the end of the year (column 2 or column
3 minus column 7)" (note (12): 0 for the year a Class 10.1 vehicle was sold): one record for each
Part B row, holding its class number and column 8."""

T777_CLASS_8_CLOSING_UCC = RecordListKind.declare(
    CATALOG,
    "t777_class_8_closing_ucc",
    fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_END),
)
"""Closing UCC of the Class 8 rows of Part A, Form T777 Part A "Column 16: UCC at the end of the
year (column 7 minus column 15)": one record for each Class 8 row, holding its class number and
column 16."""

T777_VEHICLE_CLOSING_UCC = RecordListKind.declare(
    CATALOG,
    "t777_vehicle_closing_ucc",
    fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_END),
)
"""Closing UCC of the vehicle rows of Part A, Form T777 Part A "Column 16: UCC at the end of the
year (column 7 minus column 15)": one record for each row of Classes 10, 54 and 55, holding its
class number and column 16."""

T777_VEHICLE_CLAIM = CATALOG.declare("t777_vehicle_claim", Decimal, non_negative=True)
"""CCA of the vehicle rows, Form T777 Part A "Column 15: Capital cost allowance (CCA) for the year
(column 13 multiplied by column 14 or lower amount)" summed over the Classes 10, 54 and 55 rows: the
part of line 25 that the Part A vehicle classes give, before the Part B total is added."""

T777_PART_B_CLAIM = CATALOG.declare("t777_part_b_claim", Decimal, non_negative=True)
"""CCA of the Class 10.1 vehicles, Form T777 Part B "Column 7: CCA for the year (column 5 multiplied
by column 6 or lower amount)" totalled over the rows: the Part B total that line 25 adds to the
vehicle classes of Part A."""

T777_LINE_13 = CATALOG.declare("t777_line_13", Decimal, non_negative=True)
"""Capital cost allowance for musical instruments, Form T777 line 13 "Capital cost allowance for
musical instruments (see Part A on page 4)": the CCA of the Class 8 rows of Part A, column 15 (Class
8 includes musical instruments, note (5))."""

T777_LINE_25 = CATALOG.declare("t777_line_25", Decimal, non_negative=True)
"""Capital cost allowance, Form T777 line 25 "Capital cost allowance (see Part A and Part B on pages
4 and 5)": the CCA of the Part A vehicle classes 10, 54 and 55 (column 15) plus the Part B total
(column 7)."""


# Form T777 page 1 to page 3: the expenses the filer enters, the line 3 and line 16 charts, the
# labour mobility relocations of the line 11 chart, and the lines the form computes (lines 3 to 17).

T777_ACCOUNTING_AND_LEGAL_FEES = CATALOG.declare(
    "t777_accounting_and_legal_fees", Decimal, non_negative=True
)
"""Accounting and legal fees, Form T777 line 1 "Accounting and legal fees" (8862): the amount the
filer enters, a starting amount."""

T777_ADVERTISING_AND_PROMOTION = CATALOG.declare(
    "t777_advertising_and_promotion", Decimal, non_negative=True
)
"""Advertising and promotion, Form T777 line 2 "Advertising and promotion" (8520): the amount the
filer enters, a starting amount."""

T777_FOOD_BEVERAGES_ENTERTAINMENT = CATALOG.declare(
    "t777_food_beverages_entertainment", Decimal, non_negative=True
)
"""Food, beverages, and entertainment expenses before the 50% limit, Form T777 line 4 "Food,
beverages, and entertainment expenses × 50% =" (8523): the amount the filer enters, a starting
amount; line 4 is 50% of it."""

T777_LODGING = CATALOG.declare("t777_lodging", Decimal, non_negative=True)
"""Lodging, Form T777 line 5 "Lodging" (9200): the amount the filer enters, a starting amount."""

T777_PARKING = CATALOG.declare("t777_parking", Decimal, non_negative=True)
"""Parking, Form T777 line 6 "Parking" (8910): the amount the filer enters, a starting amount."""

T777_OFFICE_SUPPLIES = CATALOG.declare("t777_office_supplies", Decimal, non_negative=True)
"""Office supplies, Form T777 line 7 "Office supplies (postage, stationery, ink cartridge, etc.)"
(8810): the amount the filer enters, a starting amount."""

T777_OTHER_EXPENSES = CATALOG.declare("t777_other_expenses", Decimal, non_negative=True)
"""Other expenses, Form T777 line 8 "Other expenses (employment use of a cell phone, long distance
calls for employment purposes, etc.) (specify)" (9270): the amount the filer enters, a starting
amount."""

T777_TRADESPERSONS_TOOLS = CATALOG.declare("t777_tradespersons_tools", Decimal, non_negative=True)
"""Tradesperson's tools claim, Form T777 line 9 "Tradesperson's tools expenses (maximum $1,000)"
(1770): the claim the filer enters, a starting amount; Guide T4044 "Deduction for tools": "Enter
your claim on the "Tradesperson's tools expenses" line of Form T777". A claim above the maximum
deduction (`ca/t777_tradespersons_tools_maximum_deduction`) is refused, not capped."""

T777_APPRENTICE_MECHANIC_TOOLS = CATALOG.declare(
    "t777_apprentice_mechanic_tools", Decimal, non_negative=True
)
"""Apprentice mechanic tools claim, Form T777 line 10 "Apprentice mechanic tools expenses" (9131):
the claim the filer enters, a starting amount; Guide T4044: "Enter your claim on the "Apprentice
mechanic tools expenses" line of Form T777". A claim above the maximum deduction
(`ca/t777_apprentice_mechanic_tools_maximum_deduction`) is refused, not capped."""

T777_MUSICAL_INSTRUMENT_EXPENSES = CATALOG.declare(
    "t777_musical_instrument_expenses", Decimal, non_negative=True
)
"""Musical instrument expenses, Form T777 line 12 "Musical instrument expenses" (1776): the amount
the filer enters, a starting amount."""

T777_ARTISTS_EMPLOYMENT_EXPENSES = CATALOG.declare(
    "t777_artists_employment_expenses", Decimal, non_negative=True
)
"""Artists' employment expenses claim, Form T777 line 14 "Artists' employment expenses" (9973) the
claim the filer enters, a starting amount; Guide T4044: "Enter the amount you can deduct on the
"Artists' employment expenses" line of Form T777". A claim above the maximum
(`ca/t777_artists_employment_expenses_maximum_deduction`) is refused, not capped."""

T777_MUSICIAN_EMPLOYMENT_INCOME = CATALOG.declare(
    "t777_musician_employment_income", Decimal, non_negative=True
)
"""Employment income as a musician, Guide T4044 "Part 2 - Musical instrument expenses": "the amount
of musical instrument expenses you can deduct cannot be more than your income for the year from your
employment as a musician after deducting all other employment expenses": the income before those
expenses, a starting amount."""

T777_ELIGIBLE_TOOLS_COST = CATALOG.declare("t777_eligible_tools_cost", Decimal, non_negative=True)
"""Cost of eligible tools bought in 2025, Guide T4044 "Deduction for tools": "the total cost of
eligible tools that you bought in 2025": a starting amount, A1 of the tradesperson's tools formula
and A of the apprentice mechanic formula."""

T777_TRADESPERSON_EMPLOYMENT_INCOME = CATALOG.declare(
    "t777_tradesperson_employment_income", Decimal, non_negative=True
)
"""Employment income as a tradesperson, Guide T4044 "Deduction for tools": "your income from
employment as a tradesperson for the year": a starting amount."""

T777_APPRENTICESHIP_GRANTS_RECEIVED = CATALOG.declare(
    "t777_apprenticeship_grants_received", Decimal, non_negative=True
)
"""Apprenticeship grants received, Guide T4044 "Deduction for tools": "the amount you received in
2025 under the Apprenticeship Incentive Grant and the Apprenticeship Completion Grant programs": a
starting amount."""

T777_APPRENTICESHIP_GRANT_OVERPAYMENTS = CATALOG.declare(
    "t777_apprenticeship_grant_overpayments", Decimal, non_negative=True
)
"""Apprenticeship grant overpayments repaid, Guide T4044 "Deduction for tools": "the amount of any
Apprenticeship Incentive Grant and Apprenticeship Completion Grant overpayments that you had to
repay in 2025": a starting amount."""

T777_FIRST_EMPLOYED_AS_APPRENTICE_MECHANIC_IN_2025 = CATALOG.declare(
    "t777_first_employed_as_apprentice_mechanic_in_2025", int, non_negative=True
)
"""First employed as an eligible apprentice mechanic during 2025, Guide T4044 "Deduction for tools
for an eligible apprentice mechanic" note ** of A: "If you become employed as an eligible
apprentice mechanic for the first time during 2025": the answer to a yes or no question, a count
of 1 or 0, checked before the step that reads it
(`ca/t777_first_employed_as_apprentice_mechanic_in_2025_checked`)."""

T777_WERE_A_TRADESPERSON_IN_2025 = CATALOG.declare(
    "t777_were_a_tradesperson_in_2025", int, non_negative=True
)
"""Were a tradesperson in 2025, Guide T4044 "Deduction for tools": "If you were a tradesperson in
2025, use the following formula to calculate your maximum tradesperson's tools deduction": the
answer to a yes or no question, a count of 1 or 0, checked before the step that reads it
(`ca/t777_were_a_tradesperson_in_2025_checked`)."""

T777_TRADESPERSON_TOOLS_CERTIFIED_ON_T2200_QUESTION_12 = CATALOG.declare(
    "t777_tradesperson_tools_certified_on_t2200_question_12", int, non_negative=True
)
"""Tradesperson's tools certified by the employer on Form T2200, Guide T4044 "Employed
tradespersons": "Have your employer complete question 12 of Part C of the form to certify that
the tools being claimed were bought and provided by you as a condition of your employment as a
tradesperson": the answer to a yes or no question, a count of 1 or 0, checked before the step
that reads it
(`ca/t777_tradesperson_tools_certified_on_t2200_question_12_checked`)."""

T777_REGISTERED_IN_A_MECHANIC_DESIGNATION_PROGRAM = CATALOG.declare(
    "t777_registered_in_a_mechanic_designation_program", int, non_negative=True
)
"""Registered in a program leading to a mechanic's designation, Guide T4044 "Employed apprentice
mechanics": "You are registered in a program established under the laws of Canada or of a
province or territory that leads to a designation under those laws as a mechanic licensed to
repair self-propelled motorized vehicles": the answer to a yes or no question, a count of 1 or
0, checked before the step that reads it
(`ca/t777_registered_in_a_mechanic_designation_program_checked`)."""

T777_EMPLOYED_AS_AN_APPRENTICE_MECHANIC = CATALOG.declare(
    "t777_employed_as_an_apprentice_mechanic", int, non_negative=True
)
"""Employed as an apprentice mechanic, Guide T4044 "Employed apprentice mechanics": "You are
employed as an apprentice mechanic": the answer to a yes or no question, a count of 1 or 0,
checked before the step that reads it
(`ca/t777_employed_as_an_apprentice_mechanic_checked`)."""

T777_APPRENTICE_MECHANIC_TOOLS_CERTIFIED_ON_T2200_QUESTION_13 = CATALOG.declare(
    "t777_apprentice_mechanic_tools_certified_on_t2200_question_13",
    int,
    non_negative=True,
)
"""Apprentice mechanic tools certified by the employer on Form T2200, Guide T4044 "Employed
apprentice mechanics": "Have your employer complete question 13 of Part C of the form to certify
that you bought and provided the tools you are claiming as a condition of your employment as an
eligible apprentice mechanic": the answer to a yes or no question, a count of 1 or 0, checked
before the step that reads it
(`ca/t777_apprentice_mechanic_tools_certified_on_t2200_question_13_checked`)."""

T777_APPRENTICE_TOOLS_COST_LAST_THREE_MONTHS_OF_2024 = CATALOG.declare(
    "t777_apprentice_tools_cost_last_three_months_of_2024", Decimal, non_negative=True
)
"""Cost of eligible tools bought in the last three months of 2024, Guide T4044 "Deduction for tools
for an eligible apprentice mechanic" note ** of A: "the cost of eligible tools you bought during the
last three months of 2024": a starting amount, added to A only for a first-time apprentice
mechanic."""

T777_APPRENTICE_MECHANIC_EMPLOYMENT_INCOME = CATALOG.declare(
    "t777_apprentice_mechanic_employment_income", Decimal, non_negative=True
)
"""Employment income as an eligible apprentice mechanic, Guide T4044 "Deduction for tools for an
eligible apprentice mechanic" B item 2: "your employment income as an eligible apprentice
mechanic": a starting amount."""

T777_APPRENTICE_MECHANIC_TOOLS_CARRY_FORWARD = CATALOG.declare(
    "t777_apprentice_mechanic_tools_carry_forward", Decimal, non_negative=True
)
"""Apprentice mechanic tools carry forward from 2024, Guide T4044 "Deduction for tools for an
eligible apprentice mechanic" C: "the amount, if any, of the maximum deduction for eligible tools
that you calculated for 2024 that you did not claim in 2024": a starting amount."""

T777_ARTISTS_EXPENSES_PAID = CATALOG.declare(
    "t777_artists_expenses_paid", Decimal, non_negative=True
)
"""Artists' employment expenses paid in 2025, Guide T4044 "Part 1 - Artists' employment expenses"
a): "the expenses you actually paid in 2025": a starting amount."""

T777_ARTISTS_EXPENSES_CARRY_FORWARD = CATALOG.declare(
    "t777_artists_expenses_carry_forward", Decimal, non_negative=True
)
"""Artists' employment expenses carried forward, Guide T4044 "Part 1 - Artists' employment expenses"
a): "any amounts you carried forward from previous years": a starting amount."""

T777_ARTISTS_EMPLOYMENT_INCOME = CATALOG.declare(
    "t777_artists_employment_income", Decimal, non_negative=True
)
"""Employment income from artistic activities, Guide T4044 "Part 1 - Artists' employment expenses"
b): "20% of your employment income from artistic activities", the total of all the employers: a
starting amount."""

T777_ARTISTS_VEHICLE_INTEREST_DEDUCTED = CATALOG.declare(
    "t777_artists_vehicle_interest_deducted", Decimal, non_negative=True
)
"""Motor vehicle interest deducted from artistic income, Guide T4044 "Part 1 - Artists' employment
expenses" b): "minus the following amounts you deducted from your income from an artistic activity:
[...] interest for your motor vehicle": a starting amount."""

T777_ARTISTS_VEHICLE_CCA_DEDUCTED = CATALOG.declare(
    "t777_artists_vehicle_cca_deducted", Decimal, non_negative=True
)
"""Motor vehicle capital cost allowance deducted from artistic income, Guide T4044 "Part 1 -
Artists' employment expenses" b): "minus the following amounts you deducted from your income from an
artistic activity: [...] capital cost allowance for your motor vehicle": a starting amount."""

T777_EMPLOYMENT_KILOMETRES = CATALOG.declare(
    "t777_employment_kilometres", Decimal, non_negative=True
)
"""Kilometres driven to earn employment income, Form T777 line 18 "Enter the number of kilometres
you drove in the tax year to earn employment income.": a starting amount, the numerator of the
employment-use share of the line 3 chart."""

T777_TOTAL_KILOMETRES = CATALOG.declare("t777_total_kilometres", Decimal, non_negative=True)
"""Total kilometres driven, Form T777 line 19 "Enter the total number of kilometres you drove in
the tax year.": a starting amount, the denominator of the employment-use share of the line 3
chart."""

T777_VEHICLE_FUEL = CATALOG.declare("t777_vehicle_fuel", Decimal, non_negative=True)
"""Motor vehicle fuel, Form T777 line 21 "Fuel (such as gasoline, propane, and oil) and
electricity": the amount the filer enters, a starting amount, part of line 29."""

T777_VEHICLE_MAINTENANCE = CATALOG.declare("t777_vehicle_maintenance", Decimal, non_negative=True)
"""Motor vehicle maintenance and repairs, Form T777 line 22 "Maintenance and repairs": the amount
the filer enters, a starting amount, part of line 29."""

T777_VEHICLE_INSURANCE = CATALOG.declare("t777_vehicle_insurance", Decimal, non_negative=True)
"""Motor vehicle insurance, Form T777 line 23 "Insurance": the amount the filer enters, a starting
amount, part of line 29."""

T777_VEHICLE_LICENCE_AND_REGISTRATION = CATALOG.declare(
    "t777_vehicle_licence_and_registration", Decimal, non_negative=True
)
"""Motor vehicle licence and registration, Form T777 line 24 "Licence and registration": the amount
the filer enters, a starting amount, part of line 29."""

T777_VEHICLE_INTEREST = CATALOG.declare("t777_vehicle_interest", Decimal, non_negative=True)
"""Total interest paid in the year, Guide T4044 "Available interest expense for passenger vehicles
or zero-emission passenger vehicles chart" line A "Total interest paid in the year": the amount the
filer enters, a starting amount. For a vehicle that is not a passenger vehicle it is Form T777 line
26 "Interest expense" whole; for a passenger vehicle line 26 is the chart's available interest
expense (`ca/t777_line_26`)."""

T777_INTEREST_DAYS = CATALOG.declare("t777_interest_days", int, non_negative=True)
"""Days for which interest was paid, Guide T4044 "Available interest expense for passenger vehicles
or zero-emission passenger vehicles chart" line B "$10 multiplied by the number of days for which
interest was paid": the number of days the filer enters, a starting count, used only for a
passenger vehicle and used as typed (the guide prints no maximum)."""

T777_INTEREST_LIMIT = CATALOG.declare("t777_interest_limit", Decimal, non_negative=True)
"""Guide T4044 interest chart line B "$10 multiplied by the number of days for which interest was
paid": the printed $10 times the checked days, rounded once."""

T777_INTEREST_AVAILABLE = CATALOG.declare("t777_interest_available", Decimal, non_negative=True)
"""Guide T4044 interest chart "The available interest expense is the lesser of amount A and amount
B.": the lesser of the total interest paid (`ca/t777_vehicle_interest`) and line B."""

T777_LINE_26 = CATALOG.declare("t777_line_26", Decimal, non_negative=True)
"""Form T777 line 26 "Interest expense", part of line 29: for a passenger vehicle or a zero-emission
passenger vehicle the guide's available interest expense ("Enter your available interest expense
amount on line 26 of Form T777"), for any other vehicle the interest paid whole ("You can deduct
interest you paid on money you borrowed to buy a motor vehicle")."""

T777_VEHICLE_LEASING_COSTS = CATALOG.declare(
    "t777_vehicle_leasing_costs", Decimal, non_negative=True
)
"""Motor vehicle leasing costs, Form T777 line 27 "Leasing costs": the eligible leasing cost of
Guide T4044's chart, the lower of its lines 7 and 8 (`core/lesser_of`), part of line 29. The guide
says "Enter your eligible leasing costs on line 27 of Form T777"."""

T777_LEASE_CHARGES = CATALOG.declare("t777_lease_charges", Decimal, non_negative=True)
"""Lease charges paid, Guide T4044 "Eligible leasing costs" line 1 "Enter the total lease charges
paid for the vehicle in 2025": the amount the filer enters, a starting amount."""

T777_LEASE_PAYMENTS_BEFORE = CATALOG.declare(
    "t777_lease_payments_before", Decimal, non_negative=True
)
"""Lease payments deducted before 2025, Guide T4044 "Eligible leasing costs" line 2 "Enter the total
lease payments deducted for the vehicle before 2025": the amount the filer enters, a starting
amount."""

T777_LEASE_DAYS = CATALOG.declare("t777_lease_days", int, non_negative=True)
"""Days leased, Guide T4044 "Eligible leasing costs" line 3 "Enter the total number of days the
vehicle was leased in 2025 and previous years": the number the filer enters, a starting count of
days."""

T777_LEASE_LIST_PRICE = CATALOG.declare("t777_lease_list_price", Decimal, non_negative=True)
"""Manufacturer's list price, Guide T4044 "Eligible leasing costs" line 4 "Enter the manufacturer's
list price": the amount the filer enters, a starting amount."""

T777_LEASE_YEAR = CATALOG.declare("t777_lease_year", int, non_negative=True)
"""Year the lease was entered into, Guide T4044 "Eligible leasing costs" footnotes * to **** (leases
entered into in 2024, 2023, 2022 and 2021 or before print other amounts): the year, a starting
count; 2021 or any earlier year uses the "2021 or before" amounts and a year after 2025 is
refused."""

T777_PASSENGER_VEHICLE = CATALOG.declare("t777_passenger_vehicle", int, non_negative=True)
"""Passenger vehicle, Guide T4044 "Interest expense" "If you use a passenger vehicle or a ZEPV to
earn employment income, there is a limit on the amount of interest you can deduct" and "Leasing
costs" "If you use a passenger vehicle to earn employment income, there is a limit on the amount
of leasing costs you can deduct. Use the chart ... to calculate your eligible leasing costs for a
passenger vehicle leased after December 31, 2000": 1 when the vehicle is a passenger vehicle (a
zero-emission passenger vehicle for the interest chart), 0 when it is not (the guide's definitions
and chart of vehicle types decide; a zero-emission vehicle that is not a zero-emission passenger
vehicle is not one), a starting count, read by the interest chart (line 26) and the leasing chart
(line 27). An answer above 1 is refused, not capped. For a vehicle that is not a passenger vehicle
neither chart applies: line 26 is the interest paid and line 27 the lease charges paid (chart line
1); the leasing chart lines 2 to 4 and the year of the lease are not used and are left at 0, since
the chart's refusals still read them."""

T777_PASSENGER_VEHICLE_CHECKED = CATALOG.declare(
    "t777_passenger_vehicle_checked", int, non_negative=True
)
"""The passenger vehicle answer, checked to be 0 or 1 (`ca/yes_or_no_count`)."""

T777_LEASE_REPAYMENT_OWING = CATALOG.declare("t777_lease_repayment_owing", int, non_negative=True)
"""Repayment owing on a leased passenger vehicle, Guide T4044 (2025) "Eligible leasing costs"
"Repayments and imputed interest": "When you lease a passenger vehicle, you may have either a
repayment owing to you, or you may have imputed interest. If this is your situation, you cannot use
the leasing chart below. Instead, contact the CRA.": 1 when the leased vehicle has a repayment owing
to the filer, 0 when it has none, a starting count. It is read only for a passenger vehicle, as the
chart is. An answer above 1 is refused, not capped."""

T777_LEASE_REPAYMENT_OWING_CHECKED = CATALOG.declare(
    "t777_lease_repayment_owing_checked", int, non_negative=True
)
"""The repayment owing answer, checked to be 0 or 1 (`ca/yes_or_no_count`)."""

T777_LEASE_DEPOSITS_MADE = CATALOG.declare("t777_lease_deposits_made", int, non_negative=True)
"""Deposits made for a leased passenger vehicle, Guide T4044 (2025) "Repayments and imputed
interest", first condition: "You made one or more deposits for the leased passenger vehicle": 1 when
one or more were, 0 when none were, a starting count. An answer above 1 is refused, not capped."""

T777_LEASE_DEPOSITS_MADE_CHECKED = CATALOG.declare(
    "t777_lease_deposits_made_checked", int, non_negative=True
)
"""The deposits made answer, checked to be 0 or 1 (`ca/yes_or_no_count`)."""

T777_LEASE_DEPOSITS_REFUNDABLE = CATALOG.declare(
    "t777_lease_deposits_refundable", int, non_negative=True
)
"""Whether all the deposits on a leased passenger vehicle are refundable, Guide T4044 (2025)
"Repayments and imputed interest", second condition: "All deposits are refundable": 1 when all are,
0 when any is not (or there are none), a starting count. An answer above 1 is refused, not
capped."""

T777_LEASE_DEPOSITS_REFUNDABLE_CHECKED = CATALOG.declare(
    "t777_lease_deposits_refundable_checked", int, non_negative=True
)
"""The all deposits refundable answer, checked to be 0 or 1 (`ca/yes_or_no_count`)."""

T777_LEASE_DEPOSITS_TOTAL = CATALOG.declare("t777_lease_deposits_total", Decimal, non_negative=True)
"""Total of the deposits on a leased passenger vehicle, Guide T4044 (2025) "Repayments and imputed
interest", third condition: "The deposits total is more than $1,000": a starting amount, 0 when
there are no deposits."""

T777_LEASE_CHART_CONFLICT = CATALOG.declare("t777_lease_chart_conflict", int, non_negative=True)
"""1 when the leasing chart cannot be used (`ca/count_by_conditions`): the vehicle is a passenger
vehicle and has a repayment owing, or has imputed interest (all three conditions of Guide T4044
"Repayments and imputed interest" apply); else 0."""

T777_LEASE_CHART_CONFLICT_CHECKED = CATALOG.declare(
    "t777_lease_chart_conflict_checked", int, non_negative=True
)
"""The leasing chart conflict, checked to be 0 (`ca/count_refused_by_conditions`): the guide says
"you cannot use the leasing chart below. Instead, contact the CRA.", so a conflict is an input
error, not a figure; the form reads it nowhere."""

T777_LEASE_ELIGIBLE_COST = CATALOG.declare("t777_lease_eligible_cost", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" "Your eligible leasing cost is the lower of the amounts on
line 7 and line 8" (`core/lesser_of`), the amount entered on line 27 for a passenger vehicle."""

T777_LEASE_LIST_PRICE_LIMIT = CATALOG.declare(
    "t777_lease_list_price_limit", Decimal, non_negative=True
)
"""Line 5's printed amount, Guide T4044 "Eligible leasing costs" line 5 "44,706*", or the footnoted
amount for the year the lease was entered into (`ca/year_amount`)."""

T777_LEASE_LIST_PRICE_TAX = CATALOG.declare("t777_lease_list_price_tax", Decimal, non_negative=True)
"""The GST and PST, or HST, on line 5's printed amount, Guide T4044 line 5 "+ GST** and PST** or
HST**" (`ca/apply_percentage`, at the filer's rate in percent)."""

T777_LEASE_LINE_5 = CATALOG.declare("t777_lease_line_5", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" line 5 "44,706* + GST** and PST** or HST**": the printed
amount plus its tax (`core/sum`)."""

T777_LEASE_LINE_6_AMOUNT = CATALOG.declare("t777_lease_line_6_amount", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" line 6 "Enter the amount from line 4 or line 5, whichever is
more" (`core/greater_of`)."""

T777_LEASE_LINE_6 = CATALOG.declare("t777_lease_line_6", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" line 6 "multiplied by 85%": the larger of lines 4 and 5
times 85% (`core/apply_rate`)."""

T777_LEASE_CHARGE_LIMIT = CATALOG.declare("t777_lease_charge_limit", Decimal, non_negative=True)
"""Line 7's printed amount, Guide T4044 "Eligible leasing costs" line 7 "$1,100***", or the
footnoted amount for the year the lease was entered into (`ca/year_amount`)."""

T777_LEASE_CHARGE_TAX = CATALOG.declare("t777_lease_charge_tax", Decimal, non_negative=True)
"""The GST and PST, or HST, on line 7's printed amount, Guide T4044 line 7 "+ GST** and PST** or
HST**" (`ca/apply_percentage`)."""

T777_LEASE_CHARGE_WITH_TAX = CATALOG.declare(
    "t777_lease_charge_with_tax", Decimal, non_negative=True
)
"""Guide T4044 "Eligible leasing costs" line 7 "($1,100*** + GST** and PST** or HST**)": the printed
amount plus its tax (`core/sum`)."""

T777_LEASE_LINE_7_TIMES_DAYS = CATALOG.declare(
    "t777_lease_line_7_times_days", Decimal, non_negative=True
)
"""Guide T4044 "Eligible leasing costs" line 7 "multiplied by line 3 =" (`core/times_count`)."""

T777_LEASE_LINE_7_DIVIDED = CATALOG.declare("t777_lease_line_7_divided", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" line 7 "divided by 30 =" (`core/apply_fraction`)."""

T777_LEASE_PAYMENTS_BEFORE_CHECKED = CATALOG.declare(
    "t777_lease_payments_before_checked", Decimal, non_negative=True
)
"""Guide T4044 line 2 after the check that it is not more than line 7's "divided by 30" figure
(`core/at_most`): line 7 prints no floor after "minus line 2", and a negative line 7 would be a
negative leasing cost on line 27, so a larger line 2 is refused (the owner's rule of 2026-10-27:
a claim, deduction or credit line the form leaves unfloored, whose negative would change a later
figure, is refused)."""

T777_LEASE_LINE_7 = CATALOG.declare("t777_lease_line_7", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" line 7 "minus line 2" (`core/subtract`)."""

T777_LEASE_COST_LIMIT = CATALOG.declare("t777_lease_cost_limit", Decimal, non_negative=True)
"""Line 8's printed amount, Guide T4044 "Eligible leasing costs" line 8 "$38,000****", or the
footnoted amount for the year the lease was entered into (`ca/year_amount`)."""

T777_LEASE_COST_TAX = CATALOG.declare("t777_lease_cost_tax", Decimal, non_negative=True)
"""The GST and PST, or HST, on line 8's printed amount, Guide T4044 line 8 "+ GST** and PST** or
HST**" (`ca/apply_percentage`)."""

T777_LEASE_COST_WITH_TAX = CATALOG.declare("t777_lease_cost_with_tax", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" line 8 "($38,000**** + GST** and PST** or HST**)": the
printed amount plus its tax (`core/sum`)."""

T777_LEASE_LINE_8 = CATALOG.declare("t777_lease_line_8", Decimal, non_negative=True)
"""Guide T4044 "Eligible leasing costs" line 8 "multiplied by line 1 = divided by line 6": the
amount with tax times line 1 over line 6, one exact fraction rounded once (`core/apply_ratio`)."""

T777_VEHICLE_OTHER_EXPENSES = CATALOG.declare(
    "t777_vehicle_other_expenses", Decimal, non_negative=True
)
"""Other motor vehicle expenses, Form T777 line 28 "Other expenses (specify)": the amount the filer
enters, a starting amount, part of line 29."""

T777_VEHICLE_ALLOWANCES = CATALOG.declare("t777_vehicle_allowances", Decimal, non_negative=True)
"""Motor vehicle rebates, allowances and reimbursements, Form T777 line 31 "Enter the total of all
rebates, motor vehicle allowances, and reimbursements for motor vehicle expenses you received that
are not included in income": the amount the filer enters, a starting amount, deducted on line 32
after the check that it is not more than line 30 (`ca/t777_vehicle_allowances_checked`)."""

T777_VEHICLE_ALLOWANCES_CHECKED = CATALOG.declare(
    "t777_vehicle_allowances_checked", Decimal, non_negative=True
)
"""Motor vehicle rebates, allowances and reimbursements, Form T777 line 31, after the check that
`ca/t777_vehicle_allowances` is not more than line 30, `ca/t777_vehicle_employment_use`
(`core/at_most`): the amount line 32 deducts. Line 32 prints no floor, so a larger line 31 would
leave a negative figure that the engine's own total of line 3 cannot take. Neither T777 line 31 nor
line 32 prints a bound or a floor (t777-25e.pdf, t4044-25e.txt lines 4183-4189), but the T4044 guide
(t4044-25e.txt, about a non-taxable motor vehicle allowance) lets you deduct motor vehicle expenses
only if you can show they are in excess of the allowance, so the refusal follows the guide."""

T777_WORK_SPACE_ELECTRICITY_HEAT_WATER_INTERNET = CATALOG.declare(
    "t777_work_space_electricity_heat_water_internet", Decimal, non_negative=True
)
"""Work-space electricity, heat, water and home Internet access fees, Form T777 line 42
"Electricity, heat, water, home Internet access fees": the amount the filer enters, a starting
amount, part of line 47."""

T777_WORK_SPACE_MAINTENANCE = CATALOG.declare(
    "t777_work_space_maintenance", Decimal, non_negative=True
)
"""Work-space maintenance, Form T777 line 43 "Maintenance (cleaning supplies, light bulbs, etc.)":
the amount the filer enters, a starting amount, part of line 47."""

T777_WORK_SPACE_HOME_INSURANCE = CATALOG.declare(
    "t777_work_space_home_insurance", Decimal, non_negative=True
)
"""Work-space home insurance, Form T777 line 44 "Home insurance (commission employees only)": the
amount the filer enters, a starting amount, part of line 47."""

T777_WORK_SPACE_PROPERTY_TAXES = CATALOG.declare(
    "t777_work_space_property_taxes", Decimal, non_negative=True
)
"""Work-space property taxes, Form T777 line 45 "Property taxes (commission employees only)": the
amount the filer enters, a starting amount, part of line 47."""

T777_WORK_SPACE_OTHER_EXPENSES = CATALOG.declare(
    "t777_work_space_other_expenses", Decimal, non_negative=True
)
"""Other work-space expenses, Form T777 line 46 "Other expenses (rent, etc.) (specify)": the amount
the filer enters, a starting amount, part of line 47."""

T777_WORK_SPACE_EMPLOYMENT_USE_AMOUNT = CATALOG.declare(
    "t777_work_space_employment_use_amount", Decimal, non_negative=True
)
"""Total employment-use amount, Form T777 line 48 "Total employment-use amount (see example below)":
the amount the filer calculates (note (4), "You must calculate your employment-use amount"), a
starting amount, added to line 49 on line 50."""

T777_WORK_SPACE_CARRIED_FORWARD = CATALOG.declare(
    "t777_work_space_carried_forward", Decimal, non_negative=True
)
"""Work-space expenses carried forward from the previous year, Form T777 line 49 "Amount carried
forward from the previous year": a starting amount, the line 55 of the previous year's form."""

T777_RELOCATION_CARRIED_FORWARD = CATALOG.declare(
    "t777_relocation_carried_forward", Decimal, non_negative=True
)
"""Relocation expenses carried forward from the previous year, Form T777 line 11 chart line 33
"expenses carried forward from the previous year from the same eligible temporary relocation": a
starting amount, a field of each relocation record."""

T777_RELOCATION_TRANSPORTATION = CATALOG.declare(
    "t777_relocation_transportation", Decimal, non_negative=True
)
"""Relocation transportation expenses, Form T777 line 11 chart line 34 "transportation expenses (one
round trip per eligible temporary relocation by the taxpayer between the ordinary residence and the
temporary lodging)": a starting amount, a field of each relocation record."""

T777_RELOCATION_MEALS = CATALOG.declare("t777_relocation_meals", Decimal, non_negative=True)
"""Relocation meal expenses, Form T777 line 11 chart line 35 "meal expenses incurred during the
round trip": a starting amount, a field of each relocation record."""

T777_RELOCATION_LODGING = CATALOG.declare("t777_relocation_lodging", Decimal, non_negative=True)
"""Relocation temporary lodging expenses, Form T777 line 11 chart line 36 "temporary lodging
expenses": a starting amount, a field of each relocation record."""

T777_RELOCATION_TRADESPERSON_INCOME = CATALOG.declare(
    "t777_relocation_tradesperson_income", Decimal, non_negative=True
)
"""Employment income as an eligible tradesperson at the temporary work location, Form T777 line 11
chart line 38 "Employment income earned as an eligible tradesperson in the year at the temporary
work location × 50%": the amount the filer enters before the 50%, a field of each relocation
record."""

T777_RELOCATION_CLAIM = CATALOG.declare("t777_relocation_claim", Decimal, non_negative=True)
"""Amount claimed for the relocation, Form T777 line 11 chart line 39 "the amount you are claiming
for this eligible temporary relocation": the filer's election, a field of each relocation record."""

T777_RELOCATIONS = RecordListKind.declare(
    CATALOG,
    "t777_relocations",
    fields=(
        T777_RELOCATION_CARRIED_FORWARD,
        T777_RELOCATION_TRANSPORTATION,
        T777_RELOCATION_MEALS,
        T777_RELOCATION_LODGING,
        T777_RELOCATION_TRADESPERSON_INCOME,
        T777_RELOCATION_CLAIM,
    ),
)
"""Eligible temporary relocations, Form T777 line 11 chart "Complete lines 33 to 40 below for each
eligible temporary relocation": one record for each relocation, holding lines 33, 34, 35, 36 and 38
of its copy and the amount claimed for it (line 39). The form's copy runs once for each record."""

T777_LINE_3 = CATALOG.declare("t777_line_3", Decimal)
"""Allowable motor vehicle expenses, Form T777 line 3 "Allowable motor vehicle expenses (see chart
for line 3 below)": line 32 of the chart, "Line 30 minus line 31. Enter this amount on line 3 of
page 1." The form prints no floor, so the kind is signed; line 31 is refused above line 30
(`ca/t777_vehicle_allowances_checked`), so the figure is never below zero."""

T777_LINE_4 = CATALOG.declare("t777_line_4", Decimal, non_negative=True)
"""Food, beverages, and entertainment expenses allowed, Form T777 line 4 "Food, beverages, and
entertainment expenses × 50% =": the food, beverages and entertainment expenses entered before the
50% (`t777_food_beverages_entertainment`) times the printed 50%, rounded half-up to the cent."""

T777_LINE_9 = CATALOG.declare("t777_line_9", Decimal, non_negative=True)
"""Tradesperson's tools expenses allowed, Form T777 line 9 "Tradesperson's tools expenses (maximum
$1,000)": the claim entered, which is not more than the maximum deduction of Guide T4044 "Deduction
for tools" (`ca/t777_tradespersons_tools_maximum_deduction`)."""

T777_TRADESPERSON_INCOME_WITH_GRANTS = CATALOG.declare(
    "t777_tradesperson_income_with_grants", Decimal, non_negative=True
)
"""Tradesperson's employment income plus the grants received, Guide T4044 "Deduction for tools",
A item 2: "your income from employment as a tradesperson for the year plus the amount you
received in 2025 under the Apprenticeship Incentive Grant and the Apprenticeship Completion Grant
programs"."""

T777_TRADESPERSON_INCOME_FOR_TOOLS = CATALOG.declare("t777_tradesperson_income_for_tools", Decimal)
"""Tradesperson's income for the tools formula, Guide T4044 "Deduction for tools", A item 2, after
"minus the amount of any [...] overpayments that you had to repay in 2025". The guide prints no
floor, so the kind is signed."""

T777_TOOLS_FORMULA_A = CATALOG.declare("t777_tools_formula_a", Decimal)
"""A of the tradesperson's tools formula, Guide T4044 "Deduction for tools": "A = the lesser of the
following amounts: 1. the total cost of eligible tools that you bought in 2025 2. your income from
employment as a tradesperson for the year plus [...] minus [...]". Signed, as item 2 is."""

T777_TRADESPERSONS_TOOLS_THRESHOLD = CATALOG.declare(
    "t777_tradespersons_tools_threshold", Decimal, non_negative=True
)
"""The $1,471 of the tradesperson's tools formula, Guide T4044 "Deduction for tools": "A minus
$1,471", the dataset's figure as printed."""

T777_TOOLS_FORMULA_B = CATALOG.declare("t777_tools_formula_b", Decimal, non_negative=True)
"""The formula of the tradesperson's tools maximum, Guide T4044 "Deduction for tools": "b) the
amount, if any, determined by the formula A minus $1,471"; "if any" is no amount below zero."""

T777_TRADESPERSONS_TOOLS_MAXIMUM_DEDUCTION = CATALOG.declare(
    "t777_tradespersons_tools_maximum_deduction", Decimal, non_negative=True
)
"""Maximum tradesperson's tools deduction, Guide T4044 "Deduction for tools": "Maximum deduction for
eligible tools is the lesser of the following amounts: a) $1,000 b) the amount, if any, determined
by the formula A minus $1,471". The most Form T777 line 9 can claim."""

T777_LINE_10 = CATALOG.declare("t777_line_10", Decimal, non_negative=True)
"""Apprentice mechanic tools expenses allowed, Form T777 line 10 "Apprentice mechanic tools
expenses": the claim entered, which is not more than the maximum deduction of Guide T4044 "Deduction
for tools for an eligible apprentice mechanic"
(`ca/t777_apprentice_mechanic_tools_maximum_deduction`)."""

T777_FIRST_EMPLOYED_AS_APPRENTICE_MECHANIC_IN_2025_CHECKED = CATALOG.declare(
    "t777_first_employed_as_apprentice_mechanic_in_2025_checked", int, non_negative=True
)
"""First employed as an eligible apprentice mechanic during 2025, after the check that the count is
0 or 1 (`ca/yes_or_no_count`)."""

T777_WERE_A_TRADESPERSON_IN_2025_CHECKED = CATALOG.declare(
    "t777_were_a_tradesperson_in_2025_checked", int, non_negative=True
)
"""Were a tradesperson in 2025, after the check that the count is 0 or 1 (`ca/yes_or_no_count`)."""

T777_TRADESPERSON_TOOLS_CERTIFIED_ON_T2200_QUESTION_12_CHECKED = CATALOG.declare(
    "t777_tradesperson_tools_certified_on_t2200_question_12_checked",
    int,
    non_negative=True,
)
"""Tradesperson's tools certified by the employer on Form T2200, after the check that the count is
0 or 1 (`ca/yes_or_no_count`)."""

T777_REGISTERED_IN_A_MECHANIC_DESIGNATION_PROGRAM_CHECKED = CATALOG.declare(
    "t777_registered_in_a_mechanic_designation_program_checked", int, non_negative=True
)
"""Registered in a program leading to a mechanic's designation, after the check that the count is 0
or 1 (`ca/yes_or_no_count`)."""

T777_EMPLOYED_AS_AN_APPRENTICE_MECHANIC_CHECKED = CATALOG.declare(
    "t777_employed_as_an_apprentice_mechanic_checked", int, non_negative=True
)
"""Employed as an apprentice mechanic, after the check that the count is 0 or 1
(`ca/yes_or_no_count`)."""

T777_APPRENTICE_MECHANIC_TOOLS_CERTIFIED_ON_T2200_QUESTION_13_CHECKED = CATALOG.declare(
    "t777_apprentice_mechanic_tools_certified_on_t2200_question_13_checked",
    int,
    non_negative=True,
)
"""Apprentice mechanic tools certified by the employer on Form T2200, after the check that the
count is 0 or 1 (`ca/yes_or_no_count`)."""

T777_APPRENTICE_TOOLS_COST_ADDED = CATALOG.declare(
    "t777_apprentice_tools_cost_added", Decimal, non_negative=True
)
"""Cost added to A, Guide T4044 "Deduction for tools for an eligible apprentice mechanic" note ** of
A: the cost of eligible tools bought in the last three months of 2024 for a first-time apprentice
mechanic, else 0."""

T777_APPRENTICE_TOOLS_FORMULA_A = CATALOG.declare(
    "t777_apprentice_tools_formula_a", Decimal, non_negative=True
)
"""A of the apprentice mechanic formula, Guide T4044 "Deduction for tools for an eligible apprentice
mechanic": "A = the total cost of eligible tools that you bought in 2025", plus the cost added by
note **."""

T777_CANADA_EMPLOYMENT_AMOUNT_INCOME = CATALOG.declare(
    "t777_canada_employment_amount_income", Decimal, non_negative=True
)
"""Employment income of the Canada employment amount, T1 line 31260 (line 92 of the worksheet)
"Enter whichever is less: $1,471 or line 1 plus line 2.", the form's own copy for Guide T4044 "the
Canada employment amount claimed on line 31260": the employment income plus the other employment
income."""

T777_CANADA_EMPLOYMENT_AMOUNT = CATALOG.declare(
    "t777_canada_employment_amount", Decimal, non_negative=True
)
"""Canada employment amount, Guide T4044 "Deduction for tools for an eligible apprentice mechanic" B
item 2: "the Canada employment amount claimed on line 31260 of your income tax and benefit return
(maximum $1,471)", the form's own copy of the T1 steps."""

T777_APPRENTICE_MECHANIC_TOOLS_BASE = CATALOG.declare(
    "t777_apprentice_mechanic_tools_base", Decimal, non_negative=True
)
"""The $1,000 of the apprentice mechanic formula, Guide T4044 B item 2: "$1,000 + the Canada
employment amount claimed on line 31260", the dataset's figure as printed."""

T777_APPRENTICE_TOOLS_BASE_WITH_EMPLOYMENT_AMOUNT = CATALOG.declare(
    "t777_apprentice_tools_base_with_employment_amount", Decimal, non_negative=True
)
"""$1,000 plus the Canada employment amount, Guide T4044 "Deduction for tools for an eligible
apprentice mechanic" B item 2: "$1,000 + the Canada employment amount claimed on line 31260 of your
income tax and benefit return (maximum $1,471)"."""

T777_APPRENTICE_INCOME_WITH_GRANTS = CATALOG.declare(
    "t777_apprentice_income_with_grants", Decimal, non_negative=True
)
"""Apprentice mechanic employment income plus the grants received, Guide T4044 B item 2 "5% of: --
your employment income as an eligible apprentice mechanic -- plus the amount you received in 2025
under the Apprenticeship Incentive Grant and the Apprenticeship Completion Grant programs"."""

T777_APPRENTICE_INCOME_LESS_TOOLS_CLAIM = CATALOG.declare(
    "t777_apprentice_income_less_tools_claim", Decimal
)
"""Apprentice mechanic income with the grants less the tradesperson's tools claim, Guide T4044 B
item 2 "-- minus any claim you made for the tradesperson's deduction for tools": Form T777 line 9.
The guide prints no floor, so the kind is signed."""

T777_APPRENTICE_INCOME_FOR_TOOLS = CATALOG.declare("t777_apprentice_income_for_tools", Decimal)
"""The figure the 5% of the apprentice mechanic formula applies to, Guide T4044 B item 2 "[...] and
the amount of any Apprenticeship Incentive Grant and Apprenticeship Completion Grant overpayments
that you had to repay in 2025". The guide prints no floor, so the kind is signed."""

T777_APPRENTICE_TOOLS_FIVE_PERCENT = CATALOG.declare("t777_apprentice_tools_five_percent", Decimal)
"""5% of the apprentice mechanic's income, Guide T4044 B item 2 "5% of: [...]", rounded half-up to
the cent. Signed, as its base is."""

T777_APPRENTICE_TOOLS_FORMULA_B2 = CATALOG.declare(
    "t777_apprentice_tools_formula_b2", Decimal, non_negative=True
)
"""B item 2 of the apprentice mechanic formula, Guide T4044: "2. the greater of: - $1,000 + the
Canada employment amount [...] - 5% of: [...]"."""

T777_APPRENTICE_TOOLS_FORMULA_B = CATALOG.declare(
    "t777_apprentice_tools_formula_b", Decimal, non_negative=True
)
"""B of the apprentice mechanic formula, Guide T4044: "B = the lesser of: 1. the total cost of
eligible tools that you bought in 2025 as calculated in A 2. the greater of: [...]"."""

T777_APPRENTICE_TOOLS_FORMULA_A_LESS_B = CATALOG.declare(
    "t777_apprentice_tools_formula_a_less_b", Decimal, non_negative=True
)
"""A minus B of the apprentice mechanic formula, Guide T4044 "(A minus B) plus C"; B is at most A,
so it is never negative."""

T777_TRADESPERSONS_TOOLS_FORMULA_MAXIMUM = CATALOG.declare(
    "t777_tradespersons_tools_formula_maximum", Decimal, non_negative=True
)
"""Maximum tradesperson's tools deduction before the conditions, Guide T4044 "Deduction for tools":
"Maximum deduction for eligible tools is the lesser of the following amounts: a) $500 b) the
amount, if any, determined by the formula A minus $1,471" (the Guide prints $1,000 in its example
and on the form, the dataset's figure)."""

T777_TRADESPERSONS_TOOLS_MAXIMUM_FOR_A_TRADESPERSON = CATALOG.declare(
    "t777_tradespersons_tools_maximum_for_a_tradesperson", Decimal, non_negative=True
)
"""Maximum tradesperson's tools deduction for a tradesperson, Guide T4044 "Deduction for tools":
"If you were a tradesperson in 2025, use the following formula": the maximum before the
conditions for a tradesperson, else 0."""

T777_APPRENTICE_TOOLS_FORMULA_A_LESS_B_IF_REGISTERED = CATALOG.declare(
    "t777_apprentice_tools_formula_a_less_b_if_registered", Decimal, non_negative=True
)
"""(A minus B) for a registered apprentice mechanic, Guide T4044 "Employed apprentice mechanics":
"You are registered in a program [...]": (A minus B) when registered, else 0."""

T777_APPRENTICE_TOOLS_FORMULA_A_LESS_B_IF_EMPLOYED = CATALOG.declare(
    "t777_apprentice_tools_formula_a_less_b_if_employed", Decimal, non_negative=True
)
"""(A minus B) for an employed apprentice mechanic, Guide T4044 "Employed apprentice mechanics":
"You are employed as an apprentice mechanic": the amount above when employed, else 0."""

T777_APPRENTICE_TOOLS_FORMULA_A_LESS_B_IF_CERTIFIED = CATALOG.declare(
    "t777_apprentice_tools_formula_a_less_b_if_certified", Decimal, non_negative=True
)
"""(A minus B) with the tools certified by the employer, Guide T4044 "Employed apprentice
mechanics": "Have your employer complete question 13 of Part C of the form to certify [...]":
the amount above when certified, else 0."""

T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION = CATALOG.declare(
    "t777_apprentice_mechanic_tools_maximum_deduction", Decimal, non_negative=True
)
"""Maximum apprentice mechanic tools deduction, Guide T4044 "Deduction for tools for an eligible
apprentice mechanic": "Maximum deduction for eligible tools* = (A minus B) plus C". The most Form
T777 line 10 can claim before the limit to net income."""

T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT = CATALOG.declare(
    "t777_apprentice_mechanic_tools_carried_forward_out", Decimal, non_negative=True
)
"""Apprentice mechanic tools deduction carried forward to 2026, Guide T4044 "Deduction for tools for
an eligible apprentice mechanic": "If you do not want to claim the maximum deduction, you can carry
forward the unused amount for use against income earned in a future year": the maximum deduction
allowed (`ca/t777_apprentice_mechanic_tools_maximum_allowed`) less the claim of Form T777 line 10
after the check against the net income (`ca/t777_line_10_checked`)."""

T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION_TOTAL = CATALOG.declare(
    "t777_apprentice_mechanic_tools_maximum_deduction_total", Decimal, non_negative=True
)
"""Maximum apprentice mechanic tools deduction, Guide T4044 "(A minus B) plus C", the export of Form
T777 read as its total by the return, for the limit to the net income."""

T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_ALLOWED = CATALOG.declare(
    "t777_apprentice_mechanic_tools_maximum_allowed", Decimal, non_negative=True
)
"""Maximum apprentice mechanic tools deduction allowed, Guide T4044 Example 1: "your maximum
deduction in 2025 is $4,029 [...] since it is less than your net income": the lesser of the maximum
deduction and the net income limit of "* This claim cannot be more than your net income for 2025
from all sources"."""

T777_LINE_10_TOTAL = CATALOG.declare("t777_line_10_total", Decimal, non_negative=True)
"""Apprentice mechanic tools expenses allowed, Form T777 line 10, the export of the form read as its
total by the return, for the limit to the net income of Guide T4044 "Deduction for tools for an
eligible apprentice mechanic"."""

T777_APPRENTICE_MECHANIC_TOOLS_NET_INCOME_LIMIT = CATALOG.declare(
    "t777_apprentice_mechanic_tools_net_income_limit", Decimal, non_negative=True
)
"""Limit of the apprentice mechanic tools claim to the net income, Guide T4044 "* This claim cannot
be more than your net income for 2025 from all sources (the claim cannot create a non-capital
loss)": the net income of the return (T1 line 23600, signed) plus the claim, never below zero."""

T777_LINE_10_CHECKED = CATALOG.declare("t777_line_10_checked", Decimal, non_negative=True)
"""Apprentice mechanic tools expenses allowed, Form T777 line 10, after the check that the claim is
not more than the net income (`ca/t777_apprentice_mechanic_tools_net_income_limit`)."""

T777_ARTISTS_EXPENSES_AVAILABLE = CATALOG.declare(
    "t777_artists_expenses_available", Decimal, non_negative=True
)
"""Artists' expenses available to claim, Guide T4044 "Part 1 - Artists' employment expenses" a):
"the expenses you actually paid in 2025 plus any amounts you carried forward from previous
years"."""

T777_ARTISTS_INCOME_TWENTY_PERCENT = CATALOG.declare(
    "t777_artists_income_twenty_percent", Decimal, non_negative=True
)
"""20% of the artistic employment income, Guide T4044 "Part 1 - Artists' employment expenses" b):
"20% of your employment income from artistic activities", rounded half-up to the cent."""

T777_ARTISTS_LIMIT_BEFORE_DEDUCTIONS = CATALOG.declare(
    "t777_artists_limit_before_deductions", Decimal, non_negative=True
)
"""The lesser of $1,000 and 20% of the artistic employment income, Guide T4044 "Part 1 - Artists'
employment expenses" b): "the lesser of: -- $1000 -- 20% of your employment income from artistic
activities"."""

T777_ARTISTS_DEDUCTIONS_FROM_ARTISTIC_INCOME = CATALOG.declare(
    "t777_artists_deductions_from_artistic_income", Decimal, non_negative=True
)
"""The amounts already deducted from artistic income, Guide T4044 "Part 1 - Artists' employment
expenses" b): "minus the following amounts you deducted from your income from an artistic activity:
-- musical instrument expenses -- interest for your motor vehicle -- capital cost allowance for your
motor vehicle", the musical instrument expenses being lines 12 and 13 of the form (Part 2: the
"Musical instrument expenses" line and the "Capital cost allowance for musical instruments"
line)."""

T777_ARTISTS_LIMIT = CATALOG.declare("t777_artists_limit", Decimal, non_negative=True)
"""Item b) of the artists' employment expenses limit, Guide T4044 "Part 1 - Artists' employment
expenses": the lesser of $1,000 and 20% of the artistic income, minus the amounts deducted from
artistic income. The guide prints no floor; a result below zero allows no claim, so it is zero."""

T777_ARTISTS_EMPLOYMENT_EXPENSES_MAXIMUM_DEDUCTION = CATALOG.declare(
    "t777_artists_employment_expenses_maximum_deduction", Decimal, non_negative=True
)
"""The most that can be claimed as artists' employment expenses, Guide T4044 "Part 1 - Artists'
employment expenses": "The amount you can claim is limited to the lesser of: a) [the expenses paid
plus the carry forward] b) [the limit of item b)]"."""

T777_LINE_14 = CATALOG.declare("t777_line_14", Decimal, non_negative=True)
"""Artists' employment expenses allowed, Form T777 line 14 "Artists' employment expenses": the claim
entered, which is not more than the maximum of Guide T4044 "Part 1 - Artists' employment expenses"
(`ca/t777_artists_employment_expenses_maximum_deduction`)."""

T777_ARTISTS_EXPENSES_CARRIED_FORWARD_OUT = CATALOG.declare(
    "t777_artists_expenses_carried_forward_out", Decimal, non_negative=True
)
"""Artists' employment expenses carried forward to 2026, Guide T4044 "Part 1 - Artists' employment
expenses": "If you have expenses you cannot claim because of the 20% or $1,000 limit, you can deduct
them from artistic income you earn in a future year": the expenses available
(`ca/t777_artists_expenses_available`) less the most that can be claimed
(`ca/t777_artists_employment_expenses_maximum_deduction`)."""

T777_MUSICIAN_EMPLOYMENT_INCOME_CHECKED = CATALOG.declare(
    "t777_musician_employment_income_checked", Decimal, non_negative=True
)
"""The income as a musician, checked to be not more than the employment income of the return
(`ca/t777_work_space_employment_income`, T1 lines 10100 and 10400): Guide T4044 "Part 2 - Musical
instrument expenses" prints "your income for the year from your employment as a musician", a part
of the employment income; above it the figure is an input error, not capped."""

T777_TRADESPERSON_EMPLOYMENT_INCOME_CHECKED = CATALOG.declare(
    "t777_tradesperson_employment_income_checked", Decimal, non_negative=True
)
"""The income as a tradesperson, checked to be not more than the employment income of the return
(`ca/t777_work_space_employment_income`, T1 lines 10100 and 10400): Guide T4044 "Deduction for
tools" prints "your income from employment as a tradesperson for the year", a part of the
employment income; above it the figure is an input error, not capped."""

T777_APPRENTICE_MECHANIC_EMPLOYMENT_INCOME_CHECKED = CATALOG.declare(
    "t777_apprentice_mechanic_employment_income_checked", Decimal, non_negative=True
)
"""The income as an eligible apprentice mechanic, checked to be not more than the employment income
of the return (`ca/t777_work_space_employment_income`, T1 lines 10100 and 10400): Guide T4044
"Deduction for tools for an eligible apprentice mechanic" prints "your employment income as an
eligible apprentice mechanic", a part of the employment income; above it the figure is an input
error, not capped."""

T777_ARTISTS_EMPLOYMENT_INCOME_CHECKED = CATALOG.declare(
    "t777_artists_employment_income_checked", Decimal, non_negative=True
)
"""The income from artistic activities, checked to be not more than the employment income of the
return (`ca/t777_work_space_employment_income`, T1 lines 10100 and 10400): Guide T4044 "Part 1 -
Artists' employment expenses" prints "20% of your employment income from artistic activities", a
part of the employment income; above it the figure is an input error, not capped."""

T777_MUSICAL_INSTRUMENT_EXPENSES_DEDUCTED = CATALOG.declare(
    "t777_musical_instrument_expenses_deducted", Decimal, non_negative=True
)
"""The musical instrument expenses deducted, Guide T4044 "Part 2 - Musical instrument expenses":
"Enter the amount you can deduct on the "Musical instrument expenses" line and the "Capital cost
allowance for musical instruments" line of Form T777", lines 12 and 13 together."""

T777_EMPLOYMENT_EXPENSES_OTHER_THAN_MUSICAL_INSTRUMENT = CATALOG.declare(
    "t777_employment_expenses_other_than_musical_instrument", Decimal, non_negative=True
)
"""All the other employment expenses, Guide T4044 "Part 2 - Musical instrument expenses": "after
deducting all other employment expenses": lines 1 to 11 and 14 of Form T777 page 1 and lines 20700
and 21200 of the return, as line 52 of the line 16 chart adds them for the same phrase. Line 16 is
not among them: its chart reads line 15, which includes the musical instrument expenses."""

T777_MUSICAL_INSTRUMENT_EXPENSES_MAXIMUM_DEDUCTION = CATALOG.declare(
    "t777_musical_instrument_expenses_maximum_deduction", Decimal, non_negative=True
)
"""The most that can be deducted for the musical instrument, Guide T4044 "Part 2 - Musical
instrument expenses": the income as a musician minus all the other employment expenses. The guide
prints no floor; a result below zero allows no deduction, so it is zero."""

T777_MUSICAL_INSTRUMENT_EXPENSES_CHECKED = CATALOG.declare(
    "t777_musical_instrument_expenses_checked", Decimal, non_negative=True
)
"""The musical instrument expenses of lines 12 and 13, checked to be not more than the maximum
(`ca/t777_musical_instrument_expenses_maximum_deduction`): above it they are an input error, not
capped; the form reads it nowhere."""

T777_LINE_11 = CATALOG.declare("t777_line_11", Decimal, non_negative=True)
"""Labour mobility deduction, Form T777 line 11 "Labour mobility deduction (see chart for line 11 on
page 2) (maximum $4,000)": the chart's line 41 "Total labour mobility deduction for the year
(maximum $4,000)", the relocation deductions of all the copies, at most $4,000."""

T777_LINE_15 = CATALOG.declare("t777_line_15", Decimal, non_negative=True)
"""Total of the expenses of lines 1 to 14, Form T777 line 15 "Add lines 1 to 14.": the page 1
expenses with lines 3, 4, 9, 11 and 13 among them. The form prints no floor, so a negative line 3
(allowances above the employment-use portion) with nothing to offset it is refused here."""

T777_LINE_16 = CATALOG.declare("t777_line_16", Decimal, non_negative=True)
"""Work-space-in-the-home expenses, Form T777 line 16 "Work-space-in-the-home expenses (see chart
for line 16 on page 3)": line 54 of the chart, the lesser of the work-space total and the
employment income limit."""

T777_LINE_17 = CATALOG.declare("t777_line_17", Decimal, non_negative=True)
"""Total expenses, Form T777 line 17 "Line 15 plus line 16. Enter this amount on line 22900 of your
return. Total expenses": line 15 plus line 16, the total the return reads as T1 line 22900."""

T777_VEHICLE_TOTAL_EXPENSES = CATALOG.declare(
    "t777_vehicle_total_expenses", Decimal, non_negative=True
)
"""Total motor vehicle expenses, Form T777 line 3 chart line 29 "Add lines 21 to 28.": the vehicle
expenses of lines 21 to 28, the capital cost allowance of line 25 among them."""

T777_VEHICLE_EMPLOYMENT_USE = CATALOG.declare(
    "t777_vehicle_employment_use", Decimal, non_negative=True
)
"""Employment-use portion of motor vehicle expenses, Form T777 line 3 chart line 30 "Line 20
multiplied by line 29. Employment-use portion": line 29 times the employment-use share of line 20,
rounded half-up to the cent once."""

T777_WORK_SPACE_EXPENSES = CATALOG.declare("t777_work_space_expenses", Decimal, non_negative=True)
"""Work-space expenses of lines 42 to 46, Form T777 line 16 chart line 47 "Add lines 42 to 46.": the
total of the work-space expenses the filer enters."""

T777_WORK_SPACE_TOTAL_AMOUNT = CATALOG.declare(
    "t777_work_space_total_amount", Decimal, non_negative=True
)
"""Work-space total amount, Form T777 line 16 chart line 50 "Line 48 plus line 49": the
employment-use amount and the amount carried forward, the amount that lines 54 and 55 take."""

T777_WORK_SPACE_EMPLOYMENT_INCOME = CATALOG.declare(
    "t777_work_space_employment_income", Decimal, non_negative=True
)
"""Employment income for the work-space limit, Form T777 line 16 chart line 51 "Enter your
employment income.": the employment income lines of the return (lines 10100 and 10400)."""

T777_WORK_SPACE_EMPLOYMENT_OFFSETS = CATALOG.declare(
    "t777_work_space_employment_offsets", Decimal, non_negative=True
)
"""Amounts that relate to employment income, Form T777 line 16 chart line 52 "Enter any amounts from
line 15 of page 1 and lines 20700 and 21200 of your return that relate to your employment income.":
line 15 of page 1, line 20700 and line 21200, in full."""

T777_WORK_SPACE_INCOME_LIMIT = CATALOG.declare(
    "t777_work_space_income_limit", Decimal, non_negative=True
)
"""Employment income limit for the work space, Form T777 line 16 chart line 53 "Line 51 minus line
52 (if negative, enter "0")": the employment income less the offsets, not below zero."""

T777_WORK_SPACE_CARRIED_FORWARD_OUT = CATALOG.declare(
    "t777_work_space_carried_forward_out", Decimal, non_negative=True
)
"""Work-space expenses available to use in future years, Form T777 line 16 chart line 55 "Line 50
minus line 53 (if negative, enter "0") Work-space-in-the-home expenses available to use in future
years": carried to the next year's line 49."""

T777_RELOCATION_TOTAL = CATALOG.declare("t777_relocation_total", Decimal, non_negative=True)
"""Total eligible temporary relocation expenses of one relocation, Form T777 line 11 chart line 37
"Add lines 33 to 36. Total eligible temporary relocation expenses"."""

T777_RELOCATION_INCOME_LIMIT = CATALOG.declare(
    "t777_relocation_income_limit", Decimal, non_negative=True
)
"""Relocation income limit of one relocation, Form T777 line 11 chart line 38 "Employment income
earned as an eligible tradesperson in the year at the temporary work location × 50%": the
tradesperson's employment income at 50%, rounded half-up to the cent."""

T777_RELOCATION_DEDUCTION = CATALOG.declare("t777_relocation_deduction", Decimal, non_negative=True)
"""Temporary relocation expenses available for deduction in the year, Form T777 line 11 chart line
39: the least of line 37, line 38 and the amount claimed, at most $4,000, for one relocation (the
export that the form's total of line 41 reads)."""

T777_RELOCATION_CARRIED_FORWARD_OUT = CATALOG.declare(
    "t777_relocation_carried_forward_out", Decimal, non_negative=True
)
"""Unused temporary relocation expenses carried forward, Form T777 line 11 chart line 40 "Line 37
minus line 39. Unused temporary relocation expenses carried forward to the following year": for one
relocation, the export carried to the next year's record."""

T777_RELOCATION_DEDUCTION_TOTAL = CATALOG.declare(
    "t777_relocation_deduction_total", Decimal, non_negative=True
)
"""Total of the relocation deductions of all the copies, Form T777 line 11 chart line 41 "Enter the
amount from line 39. If you have multiple eligible temporary relocations in the year, add the amount
from line 39 for each eligible temporary relocation.": the line 39 amounts totalled, before the
$4,000 maximum of line 11."""

T777_LINE_11_MAXIMUM = CATALOG.declare("t777_line_11_maximum", Decimal, non_negative=True)
"""Maximum of the labour mobility deduction, Form T777 line 11 "Total labour mobility deduction for
the year (maximum $4,000)" and chart line 41: the $4,000, the most the total can be."""

T777_LINE_17_TOTAL = CATALOG.declare("t777_line_17_total", Decimal, non_negative=True)
"""Total expenses of the Form T777 copy, line 17 "Total expenses" (the form's one record of
`ca/t777.t777_line_17`), read as an amount: T1 line 22900 "Other employment expenses (see Guide
T4044)" adds it to the RC359 line 7 total."""
