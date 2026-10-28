"""The federal catalog: the refund or balance owing.

Total credits, the balance owing and the refund.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

TOTAL_CREDITS = CATALOG.declare("total_credits", Decimal)
"""Total credits, T1 line 166 (line 48200) "Add lines 150 to 165. Total credits": here line 150
(43700), line 152 (44800), line 153 (45000, the EI overpayment), line 154 (45200), line 155
(45300), line 156 (45350), line 157 (45355), line 158 (45400), line 159 (45600), line 160 (45700,
a caller input), line 161 (46900), line 162 (47555), line 47556, line 164 (47600) and line 165
(47900), in line order. Signed, as the line prints no floor.

Line 151 (44000, a Quebec abatement that does not apply to an Ontario return) is left out.
"""

FUEL_CHARGE_GROSS_FARMING_EXPENSES = CATALOG.declare("fuel_charge_gross_farming_expenses", Decimal)
"""Total gross farming expenses, Form T2043 Part 1 line 67061 "Total gross farming expenses for all
of your businesses: Add amount 6 of every Chart A.": the total of Chart A amount 6 over the
statements. Note 1 "If your total gross farming expenses for all businesses are $25,000 or more,
you are eligible to claim the credit." reads it."""

FUEL_CHARGE_EXPENSES_ON = CATALOG.declare("fuel_charge_expenses_on", Decimal)
"""Farming expenses in Ontario, Form T2043 Part 2 line 67063 "Add all farming expenses in ON from
amount 8 of Chart A.": the total of Chart A amount 8 over the statements in Ontario."""

FUEL_CHARGE_EXPENSES_MB = CATALOG.declare("fuel_charge_expenses_mb", Decimal)
"""Farming expenses in Manitoba, Form T2043 Part 2 line 67064 "Add all farming expenses in MB from
amount 8 of Chart A.": the total of Chart A amount 8 over the statements in Manitoba."""

FUEL_CHARGE_EXPENSES_SK = CATALOG.declare("fuel_charge_expenses_sk", Decimal)
"""Farming expenses in Saskatchewan, Form T2043 Part 2 line 67065 "Add all farming expenses in SK
from amount 8 of Chart A.": the total of Chart A amount 8 over the statements in Saskatchewan."""

FUEL_CHARGE_EXPENSES_AB = CATALOG.declare("fuel_charge_expenses_ab", Decimal)
"""Farming expenses in Alberta, Form T2043 Part 2 line 67066 "Add all farming expenses in AB from
amount 8 of Chart A.": the total of Chart A amount 8 over the statements in Alberta."""

FUEL_CHARGE_EXPENSES_NS = CATALOG.declare("fuel_charge_expenses_ns", Decimal)
"""Farming expenses in Nova Scotia, Form T2043 Part 2 line 67091 "Add all farming expenses in NS
from amount 8 of Chart A.": the total of Chart A amount 8 over the statements in Nova Scotia."""

FUEL_CHARGE_EXPENSES_PE = CATALOG.declare("fuel_charge_expenses_pe", Decimal)
"""Farming expenses in Prince Edward Island, Form T2043 Part 2 line 67092 "Add all farming expenses
in PE from amount 8 of Chart A.": the total of Chart A amount 8 over the statements in Prince Edward
Island."""

FUEL_CHARGE_EXPENSES_NL = CATALOG.declare("fuel_charge_expenses_nl", Decimal)
"""Farming expenses in Newfoundland and Labrador, Form T2043 Part 2 line 67093 "Add all farming
expenses in NL from amount 8 of Chart A.": the total of Chart A amount 8 over the statements in
Newfoundland and Labrador."""

FUEL_CHARGE_EXPENSES_NB = CATALOG.declare("fuel_charge_expenses_nb", Decimal)
"""Farming expenses in New Brunswick, Form T2043 Part 2 line 67094 "Add all farming expenses in NB
from amount 8 of Chart A.": the total of Chart A amount 8 over the statements in New Brunswick."""

FUEL_CHARGE_CREDIT_ON = CATALOG.declare("fuel_charge_credit_on", Decimal)
"""Credit for Ontario, Form T2043 Part 2 amount 2A "ON payment rate 0.229%": line 67063 times the
payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_CREDIT_MB = CATALOG.declare("fuel_charge_credit_mb", Decimal)
"""Credit for Manitoba, Form T2043 Part 2 amount 2B "MB payment rate 0.229%": line 67064 times the
payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_CREDIT_SK = CATALOG.declare("fuel_charge_credit_sk", Decimal)
"""Credit for Saskatchewan, Form T2043 Part 2 amount 2C "SK payment rate 0.229%": line 67065 times
the payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_CREDIT_AB = CATALOG.declare("fuel_charge_credit_ab", Decimal)
"""Credit for Alberta, Form T2043 Part 2 amount 2D "AB payment rate 0.229%": line 67066 times the
payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_CREDIT_NS = CATALOG.declare("fuel_charge_credit_ns", Decimal)
"""Credit for Nova Scotia, Form T2043 Part 2 amount 2E "NS payment rate 0.229%": line 67091 times
the payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_CREDIT_PE = CATALOG.declare("fuel_charge_credit_pe", Decimal)
"""Credit for Prince Edward Island, Form T2043 Part 2 amount 2F "PE payment rate 0.229%": line 67092
times the payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_CREDIT_NL = CATALOG.declare("fuel_charge_credit_nl", Decimal)
"""Credit for Newfoundland and Labrador, Form T2043 Part 2 amount 2G "NL payment rate 0.229%": line
67093 times the payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_CREDIT_NB = CATALOG.declare("fuel_charge_credit_nb", Decimal)
"""Credit for New Brunswick, Form T2043 Part 2 amount 2H "NB payment rate 0.229%": line 67094 times
the payment rate 0.229%, rounded half-up to the cent."""

FUEL_CHARGE_PART_2_TOTAL = CATALOG.declare("fuel_charge_part_2_total", Decimal)
"""Total of Part 2, Form T2043 Part 2 amount 2I "Total: Add amounts 2A to 2H": the credits of the
eight designated provinces added."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_ON = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_on", Decimal, non_negative=True
)
"""Gross income in Ontario, Form T2043 Part 3 line 67067 "Add all ON amounts from row 1 of every
Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_MB = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_mb", Decimal, non_negative=True
)
"""Gross income in Manitoba, Form T2043 Part 3 line 67068 "Add all MB amounts from row 1 of every
Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_SK = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_sk", Decimal, non_negative=True
)
"""Gross income in Saskatchewan, Form T2043 Part 3 line 67069 "Add all SK amounts from row 1 of
every Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_AB = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_ab", Decimal, non_negative=True
)
"""Gross income in Alberta, Form T2043 Part 3 line 67070 "Add all AB amounts from row 1 of every
Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_NS = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_ns", Decimal, non_negative=True
)
"""Gross income in Nova Scotia, Form T2043 Part 3 line 67095 "Add all NS amounts from row 1 of every
Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_PE = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_pe", Decimal, non_negative=True
)
"""Gross income in Prince Edward Island, Form T2043 Part 3 line 67096 "Add all PE amounts from row 1
of every Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_NL = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_nl", Decimal, non_negative=True
)
"""Gross income in Newfoundland and Labrador, Form T2043 Part 3 line 67097 "Add all NL amounts from
row 1 of every Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_GROSS_INCOME_NB = CATALOG.declare(
    "fuel_charge_chart_b_gross_income_nb", Decimal, non_negative=True
)
"""Gross income in New Brunswick, Form T2043 Part 3 line 67098 "Add all NB amounts from row 1 of
every Chart B": the total of Chart B row 1 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_ON = CATALOG.declare(
    "fuel_charge_chart_b_salaries_on", Decimal, non_negative=True
)
"""Salaries and wages in Ontario, Form T2043 Part 3 line 67071 "Add all ON amounts from row 4 of
every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_MB = CATALOG.declare(
    "fuel_charge_chart_b_salaries_mb", Decimal, non_negative=True
)
"""Salaries and wages in Manitoba, Form T2043 Part 3 line 67072 "Add all MB amounts from row 4 of
every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_SK = CATALOG.declare(
    "fuel_charge_chart_b_salaries_sk", Decimal, non_negative=True
)
"""Salaries and wages in Saskatchewan, Form T2043 Part 3 line 67073 "Add all SK amounts from row 4
of every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_AB = CATALOG.declare(
    "fuel_charge_chart_b_salaries_ab", Decimal, non_negative=True
)
"""Salaries and wages in Alberta, Form T2043 Part 3 line 67074 "Add all AB amounts from row 4 of
every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_NS = CATALOG.declare(
    "fuel_charge_chart_b_salaries_ns", Decimal, non_negative=True
)
"""Salaries and wages in Nova Scotia, Form T2043 Part 3 line 67099 "Add all NS amounts from row 4 of
every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_PE = CATALOG.declare(
    "fuel_charge_chart_b_salaries_pe", Decimal, non_negative=True
)
"""Salaries and wages in Prince Edward Island, Form T2043 Part 3 line 67100 "Add all PE amounts from
row 4 of every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_NL = CATALOG.declare(
    "fuel_charge_chart_b_salaries_nl", Decimal, non_negative=True
)
"""Salaries and wages in Newfoundland and Labrador, Form T2043 Part 3 line 67101 "Add all NL amounts
from row 4 of every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_SALARIES_NB = CATALOG.declare(
    "fuel_charge_chart_b_salaries_nb", Decimal, non_negative=True
)
"""Salaries and wages in New Brunswick, Form T2043 Part 3 line 67102 "Add all NB amounts from row 4
of every Chart B": the total of Chart B row 4 over the statements."""

FUEL_CHARGE_CHART_B_TOTAL_GROSS_INCOME = CATALOG.declare(
    "fuel_charge_chart_b_total_gross_income", Decimal, non_negative=True
)
"""Total gross income in all provinces, Form T2043 Part 3 line 67075 "Total gross income in all
provinces and territories from all farming businesses: Add the amount from row 2 of every Chart B
you fill in": the total of Chart B row 2 over the statements."""

FUEL_CHARGE_CHART_B_TOTAL_SALARIES = CATALOG.declare(
    "fuel_charge_chart_b_total_salaries", Decimal, non_negative=True
)
"""Total salaries and wages in all provinces, Form T2043 Part 3 line 67076 "Total salaries and wages
paid to employees in all provinces and territories from all farming businesses: Add the amount from
row 5 of every Chart B you fill in": the total of Chart B row 5 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_ON = CATALOG.declare("fuel_charge_chart_c_total_on", Decimal)
"""Total credit in ON, Form T2043 Part 4 amount 4A "Total credit in ON for all businesses: Add
amount 7 of every Chart C": the total of Chart C amount 7 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_MB = CATALOG.declare("fuel_charge_chart_c_total_mb", Decimal)
"""Total credit in MB, Form T2043 Part 4 amount 4B "Total credit in MB for all businesses: Add
amount 8 of every Chart C": the total of Chart C amount 8 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_SK = CATALOG.declare("fuel_charge_chart_c_total_sk", Decimal)
"""Total credit in SK, Form T2043 Part 4 amount 4C "Total credit in SK for all businesses: Add
amount 9 of every Chart C": the total of Chart C amount 9 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_AB = CATALOG.declare("fuel_charge_chart_c_total_ab", Decimal)
"""Total credit in AB, Form T2043 Part 4 amount 4D "Total credit in AB for all businesses: Add
amount 10 of every Chart C": the total of Chart C amount 10 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_NS = CATALOG.declare("fuel_charge_chart_c_total_ns", Decimal)
"""Total credit in NS, Form T2043 Part 4 amount 4E "Total credit in NS for all businesses: Add
amount 11 of every Chart C": the total of Chart C amount 11 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_PE = CATALOG.declare("fuel_charge_chart_c_total_pe", Decimal)
"""Total credit in PE, Form T2043 Part 4 amount 4F "Total credit in PE for all businesses: Add
amount 12 of every Chart C": the total of Chart C amount 12 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_NL = CATALOG.declare("fuel_charge_chart_c_total_nl", Decimal)
"""Total credit in NL, Form T2043 Part 4 amount 4G "Total credit in NL for all businesses: Add
amount 13 of every Chart C": the total of Chart C amount 13 over the statements."""

FUEL_CHARGE_CHART_C_TOTAL_NB = CATALOG.declare("fuel_charge_chart_c_total_nb", Decimal)
"""Total credit in NB, Form T2043 Part 4 amount 4H "Total credit in NB for all businesses: Add
amount 14 of every Chart C": the total of Chart C amount 14 over the statements."""

FUEL_CHARGE_PART_4_TOTAL = CATALOG.declare("fuel_charge_part_4_total", Decimal)
"""Total of Part 4, Form T2043 Part 4 amount 4I "Total: Add amounts 4A to 4H (enter this total at
amount 5B)": the eight totals added. Amount 5B takes it."""

FUEL_CHARGE_PART_5A_CREDIT = CATALOG.declare("fuel_charge_part_5a_credit", Decimal)
"""Credit of the businesses, Form T2043 Part 5 amount 5A "Enter amount 2I": amount 2I when the
total gross farming expenses (line 67061) reach $25,000 (Part 1 Note 1), else 0. Signed, as
Chart A amount 5 is no longer bounded."""

FUEL_CHARGE_PART_5B_CREDIT = CATALOG.declare("fuel_charge_part_5b_credit", Decimal)
"""Credit of the businesses in several provinces, Form T2043 Part 5 amount 5B "Enter amount 4I":
the total of Part 4 (amount 4I), the eight Chart C totals added. Signed, as
Part 4 prints no floor."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_ON = CATALOG.declare(
    "fuel_charge_partnership_credit_on", Decimal, non_negative=True
)
"""Credit allocated from a partnership for Ontario, Form T2043 Part 5 line 67079 "Credit allocated
from a partnership for ON (amount from box 237 of each T5013 slip or from each letter)": a starting
amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_MB = CATALOG.declare(
    "fuel_charge_partnership_credit_mb", Decimal, non_negative=True
)
"""Credit allocated from a partnership for Manitoba, Form T2043 Part 5 line 67080 "Credit allocated
from a partnership for MB (amount from box 237 of each T5013 slip or from each letter)": a starting
amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_SK = CATALOG.declare(
    "fuel_charge_partnership_credit_sk", Decimal, non_negative=True
)
"""Credit allocated from a partnership for Saskatchewan, Form T2043 Part 5 line 67081 "Credit
allocated from a partnership for SK (amount from box 237 of each T5013 slip or from each letter)": a
starting amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_AB = CATALOG.declare(
    "fuel_charge_partnership_credit_ab", Decimal, non_negative=True
)
"""Credit allocated from a partnership for Alberta, Form T2043 Part 5 line 67082 "Credit allocated
from a partnership for AB (amount from box 237 of each T5013 slip or from each letter)": a starting
amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_NS = CATALOG.declare(
    "fuel_charge_partnership_credit_ns", Decimal, non_negative=True
)
"""Credit allocated from a partnership for Nova Scotia, Form T2043 Part 5 line 67103 "Credit
allocated from a partnership for NS (amount from box 237 of each T5013 slip or from each letter)": a
starting amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_PE = CATALOG.declare(
    "fuel_charge_partnership_credit_pe", Decimal, non_negative=True
)
"""Credit allocated from a partnership for Prince Edward Island, Form T2043 Part 5 line 67104
"Credit allocated from a partnership for PE (amount from box 237 of each T5013 slip or from each
letter)": a starting amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_NL = CATALOG.declare(
    "fuel_charge_partnership_credit_nl", Decimal, non_negative=True
)
"""Credit allocated from a partnership for Newfoundland and Labrador, Form T2043 Part 5 line 67105
"Credit allocated from a partnership for NL (amount from box 237 of each T5013 slip or from each
letter)": a starting amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_NB = CATALOG.declare(
    "fuel_charge_partnership_credit_nb", Decimal, non_negative=True
)
"""Credit allocated from a partnership for New Brunswick, Form T2043 Part 5 line 67106 "Credit
allocated from a partnership for NB (amount from box 237 of each T5013 slip or from each letter)": a
starting amount."""

FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL = CATALOG.declare(
    "fuel_charge_partnership_credit_total", Decimal, non_negative=True
)
"""Total credit allocated from partnerships, Form T2043 Part 5 amount 5C "Total credit allocated
from partnerships: Add lines 67079 to 67082 and lines 67103 to 67106.": the eight lines added."""

FARM_FUEL_CHARGE_CREDIT_TOTAL = CATALOG.declare(
    "farm_fuel_charge_credit_total", Decimal, non_negative=True
)
"""Total of the credit allocated to the statements, Form T2042 line 9951 "Return of fuel charge
proceeds to farmers tax credit allocated to you in the year" added over the statements (Form T2043
note 2: "you must include the portion of the credit allocated to each business on line 9951 of
Form T2042 for that business"): the total of the exports of `ca/t2042` (`core/record_total`), which
amount 5C may not be below."""

FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED = CATALOG.declare(
    "farm_fuel_charge_credit_total_checked", Decimal, non_negative=True
)
"""Total of line 9951 over the statements after the check that it is not more than amount 5C
(`core/at_most`); a total above 5C is refused, not capped. Exported by Form T2043."""

FUEL_CHARGE_CREDIT_FARMERS = CATALOG.declare("fuel_charge_credit_farmers", Decimal)
"""Return of fuel charge proceeds to farmers tax credit, T1 line 47556 "Return of fuel charge
proceeds to farmers tax credit (complete Form T2043)" and Form T2043 Part 5 amount 5D "Total credit
for all businesses: Amount 5A plus amount 5B plus amount 5C (enter this amount on line 47556 of
your income tax and benefit return).": amounts 5A, 5B and 5C added, signed
as the form prints no floor."""

FUEL_CHARGE_CREDIT_FARMERS_TOTAL = CATALOG.declare("fuel_charge_credit_farmers_total", Decimal)
"""Return of fuel charge proceeds to farmers tax credit, T1 line 47556 "Return of fuel charge
proceeds to farmers tax credit (complete Form T2043)": amount 5D of Form T2043 (the form's export,
one record) totalled for the line 48200 sum, signed."""

FUEL_CHARGE_FARMS_IN_PROVINCE_ON = CATALOG.declare(
    "fuel_charge_farms_in_province_on", Decimal, non_negative=True
)
"""Statements present in Ontario, Form T2043 box 67062 "Tick this box if you have multiple farming
businesses with one or more permanent establishments in multiple provinces or territories.": the
total over the statements of the presence amount in Ontario (`ca/t2042.farm_present_amount_on`),
so the number of statements present in it."""

FUEL_CHARGE_FARMS_IN_PROVINCE_MB = CATALOG.declare(
    "fuel_charge_farms_in_province_mb", Decimal, non_negative=True
)
"""Statements present in Manitoba, Form T2043 box 67062 "Tick this box if you have multiple farming
businesses with one or more permanent establishments in multiple provinces or territories.": the
total over the statements of the presence amount in Manitoba
(`ca/t2042.farm_present_amount_mb`), so the number of statements present in it."""

FUEL_CHARGE_FARMS_IN_PROVINCE_SK = CATALOG.declare(
    "fuel_charge_farms_in_province_sk", Decimal, non_negative=True
)
"""Statements present in Saskatchewan, Form T2043 box 67062 "Tick this box if you have multiple
farming businesses with one or more permanent establishments in multiple provinces or
territories.": the total over the statements of the presence amount in Saskatchewan
(`ca/t2042.farm_present_amount_sk`), so the number of statements present in it."""

FUEL_CHARGE_FARMS_IN_PROVINCE_AB = CATALOG.declare(
    "fuel_charge_farms_in_province_ab", Decimal, non_negative=True
)
"""Statements present in Alberta, Form T2043 box 67062 "Tick this box if you have multiple farming
businesses with one or more permanent establishments in multiple provinces or territories.": the
total over the statements of the presence amount in Alberta (`ca/t2042.farm_present_amount_ab`),
so the number of statements present in it."""

FUEL_CHARGE_FARMS_IN_PROVINCE_NS = CATALOG.declare(
    "fuel_charge_farms_in_province_ns", Decimal, non_negative=True
)
"""Statements present in Nova Scotia, Form T2043 box 67062 "Tick this box if you have multiple
farming businesses with one or more permanent establishments in multiple provinces or
territories.": the total over the statements of the presence amount in Nova Scotia
(`ca/t2042.farm_present_amount_ns`), so the number of statements present in it."""

FUEL_CHARGE_FARMS_IN_PROVINCE_PE = CATALOG.declare(
    "fuel_charge_farms_in_province_pe", Decimal, non_negative=True
)
"""Statements present in Prince Edward Island, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the total over the statements of the presence amount in Prince Edward Island
(`ca/t2042.farm_present_amount_pe`), so the number of statements present in it."""

FUEL_CHARGE_FARMS_IN_PROVINCE_NL = CATALOG.declare(
    "fuel_charge_farms_in_province_nl", Decimal, non_negative=True
)
"""Statements present in Newfoundland and Labrador, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the total over the statements of the presence amount in Newfoundland and Labrador
(`ca/t2042.farm_present_amount_nl`), so the number of statements present in it."""

FUEL_CHARGE_FARMS_IN_PROVINCE_NB = CATALOG.declare(
    "fuel_charge_farms_in_province_nb", Decimal, non_negative=True
)
"""Statements present in New Brunswick, Form T2043 box 67062 "Tick this box if you have multiple
farming businesses with one or more permanent establishments in multiple provinces or
territories.": the total over the statements of the presence amount in New Brunswick
(`ca/t2042.farm_present_amount_nb`), so the number of statements present in it."""

FUEL_CHARGE_FARMS_OUTSIDE_EIGHT = CATALOG.declare(
    "fuel_charge_farms_outside_eight", Decimal, non_negative=True
)
"""Statements present outside the eight designated provinces, Form T2043 box 67062 "Tick this box
if you have multiple farming businesses with one or more permanent establishments in multiple
provinces or territories.": the total over the statements of the presence amount outside the
eight (`ca/t2042.farm_present_amount_outside_eight`), so the number of statements present there."""

FUEL_CHARGE_FARM_STATEMENT_COUNT = CATALOG.declare(
    "fuel_charge_farm_statement_count", int, non_negative=True
)
"""Number of farm statements, Form T2043 box 67062 "Tick this box if you have multiple farming
businesses with one or more permanent establishments in multiple provinces or territories.": one
for each Form T2042 statement entered, the count the box reads with the places."""

FUEL_CHARGE_MULTIPLE_PROVINCES_BOX = CATALOG.declare(
    "fuel_charge_multiple_provinces_box", int, non_negative=True
)
"""Multiple farming businesses in multiple provinces, Form T2043 box 67062 "Tick this box if you
have multiple farming businesses with one or more permanent establishments in multiple provinces
or territories.": 1 when there is more than one statement and two of the nine places (the eight
designated provinces, then outside the eight) each have a statement present in them, else 0, a
count."""

REFUND_OR_BALANCE_OWING = CATALOG.declare("refund_or_balance_owing", Decimal)
"""Refund or balance owing, T1 line 167 "Line 149 minus line 166 If the amount is negative, enter
it on line 48400 below. If the amount is positive, enter it on line 48500 below. Refund or balance
owing": the total payable less the total credits, both already in cents.

Line 149 is "Enter the amount from line 148 of the previous page.", the total payable. The one
kind not declared non-negative: a negative amount is a refund (line 48400 "Refund"), a positive
one a balance owing (line 48500 "Balance owing"). The line takes amounts already in cents, so it
is in cents without a rounding of its own.
"""

REFUND = CATALOG.declare("refund", Decimal, non_negative=True)
"""Refund, T1 line 48400 "Refund": line 167 "If the amount is negative, enter it on line 48400
below", so the total credits less the total payable, not below zero. A refund is never negative,
unlike line 167 (`refund_or_balance_owing`), which stays signed."""

T2204_INSURABLE_EARNINGS = CATALOG.declare("t2204_insurable_earnings", Decimal, non_negative=True)
"""Total EI insurable earnings, Form T2204 line 1 "Total EI insurable earnings (box 24 or, if
blank, box 14 of your T4 slips) (1)": a starting amount, before note (1) "If you have no
self-employment earnings and your total EI insurable earnings on your T4 slips are less than
$2,000, enter "0"."
"""

T2204_SELF_EMPLOYMENT_EARNINGS = CATALOG.declare(
    "t2204_self_employment_earnings", Decimal, non_negative=True
)
"""Self-employment and other earnings eligible under the EI agreement, Form T2204 line 2 "Total
self-employment and other earnings eligible for the EI program for access to EI special benefits":
a starting amount, nil when there is no agreement with the Canada Employment Insurance
Commission."""

T2204_PREMIUMS_DEDUCTED = CATALOG.declare("t2204_premiums_deducted", Decimal, non_negative=True)
"""Total premiums deducted, Form T2204 line 4 "Total premiums deducted: Residents of other than
Quebec (box 18 and box 55 of your T4 slips)": a starting amount, taken as typed. Lines 6 and 9 read
it as typed; the form prints no limit on line 4."""

T2204_PPIP_PREMIUMS = CATALOG.declare("t2204_ppip_premiums", Decimal, non_negative=True)
"""Quebec parental insurance plan (PPIP) premiums, the box 55 part of Form T2204 line 4 "Total
premiums deducted: Residents of other than Quebec (box 18 and box 55 of your T4 slips)": the total
of box 55 of the filer's T4 slips, a starting amount. Line 4 (`ca/t2204_premiums_deducted`) includes
it, so it is checked to be at most line 4 (`ca/t2204_ppip_premiums_checked`). Note (2)
(EI-exempt pay in box 28, and the controlling-shareholder agreement) is the filer's to apply: the
form gives no box to key it on."""

T2204_PPIP_PREMIUMS_CHECKED = CATALOG.declare(
    "t2204_ppip_premiums_checked", Decimal, non_negative=True
)
"""Quebec parental insurance plan (PPIP) premiums, the box 55 part of Form T2204 line 4, after the
check that they are not more than line 4 (`ca/t2204_premiums_deducted`), of which they are a part
(`core/at_most`), so a box 55 amount above line 4 is an input error, not capped."""

T2204_LINE_1_COUNT = CATALOG.declare("t2204_line_1_count", int, non_negative=True)
"""Count of the note (1) on Form T2204 line 1 "If you have no self-employment earnings and your
total EI insurable earnings on your T4 slips are less than $2,000, enter "0"": 0 when the note
applies and 1 otherwise, the factor of line 1."""

T2204_LINE_1 = CATALOG.declare("t2204_line_1", Decimal, non_negative=True)
"""Total EI insurable earnings, Form T2204 line 1 "Total EI insurable earnings (box 24 or, if
blank, box 14 of your T4 slips) (1)", after note (1): the insurable earnings, or "0" when the note
applies."""

T2204_LINE_1_PLUS_2 = CATALOG.declare("t2204_line_1_plus_2", Decimal, non_negative=True)
"""Line 1 plus line 2 of Form T2204 before the maximum of line 3: the insurable earnings after note
(1) plus the self-employment earnings eligible under the agreement, not yet capped."""

T2204_LINE_3 = CATALOG.declare("t2204_line_3", Decimal, non_negative=True)
"""Line 3 of Form T2204, "Line 1 plus line 2 (maximum $65,700)": the sum of lines 1 and 2, capped at
the maximum insurable earnings of $65,700."""

T2204_EXEMPTION = CATALOG.declare("t2204_exemption", Decimal, non_negative=True)
"""Exemption of Form T2204 line 7 "Amount from line 3 – $2,000 = (if negative, enter "0")": the
$2,000 taken from line 3, claimed whole, a dataset figure."""

T2204_LINE_6 = CATALOG.declare("t2204_line_6", Decimal, non_negative=True)
"""Line 6 of Form T2204, "Line 4 plus line 5": the premiums deducted (line 4) plus the Schedule 13
premiums payable on self-employment and other earnings (line 5), for each agreement."""

T2204_LINE_7 = CATALOG.declare("t2204_line_7", Decimal, non_negative=True)
"""Line 7 of Form T2204, "Amount from line 3 – $2,000 = (if negative, enter "0")": line 3 less the
$2,000 exemption, not below zero."""

T2204_LINE_8 = CATALOG.declare("t2204_line_8", Decimal, non_negative=True)
"""Line 8 of Form T2204, "Line 6 minus line 7 (if negative, enter "0")": line 6 less line 7, not
below zero."""

T2204_LINE_9 = CATALOG.declare("t2204_line_9", Decimal, non_negative=True)
"""Line 9 of Form T2204, "Total premiums deducted from line 4 above": line 4 carried over."""

T2204_LINE_10 = CATALOG.declare("t2204_line_10", Decimal, non_negative=True)
"""Line 10 of Form T2204, "Residents of other than Quebec Amount from line 1 × 1.64% = (maximum
$1,077.48)": line 1 times the EI premium rate, capped at the maximum premium. The Quebec variant
(line 11) is not modelled."""

T2204_LINE_12 = CATALOG.declare("t2204_line_12", Decimal, non_negative=True)
"""Line 12 of Form T2204, "Enter the amount from line 10 or line 11, whichever applies.": line 10,
as the Quebec variant of line 11 is not modelled."""

T2204_LINE_13 = CATALOG.declare("t2204_line_13", Decimal, non_negative=True)
"""Line 13 of Form T2204, "Line 9 minus line 12 (if negative, enter "0")": the premiums deducted
less the premiums payable, not below zero."""

T2204_LINE_14 = CATALOG.declare("t2204_line_14", Decimal, non_negative=True)
"""Line 14 of Form T2204, "Enter whichever is more: amount from line 8 or line 13.": the greater of
line 8 and line 13."""

T2204_LINE_15 = CATALOG.declare("t2204_line_15", Decimal, non_negative=True)
"""Line 15 of Form T2204, "Enter whichever is less: amount from line 9 or line 14.": the lesser of
line 9 and line 14."""

T2204_LINE_15_COUNT = CATALOG.declare("t2204_line_15_count", int, non_negative=True)
"""Count of Form T2204 line 15, "If this amount is more than $1, enter it on line 45000 of your
return.": 1 when line 15 is more than $1 and 0 otherwise, the factor of line 45000."""

T2204_LINE_16 = CATALOG.declare("t2204_line_16", Decimal, non_negative=True)
"""Line 16 of Form T2204, "Enter whichever amount is the least: line 7, line 9 or line 12.": the
least of lines 7, 9 and 12. It is entered on line 31200 of the return (`ca/ei_premiums`)."""

EI_OVERPAYMENT = CATALOG.declare("ei_overpayment", Decimal, non_negative=True)
"""Employment insurance (EI) overpayment, T1 line 45000 "Employment insurance (EI) overpayment":
line 15 of Form T2204 when it is more than $1 ("If this amount is more than $1, enter it on line
45000 of your return"), else 0. Total credits (line 48200) read it at line 153."""
