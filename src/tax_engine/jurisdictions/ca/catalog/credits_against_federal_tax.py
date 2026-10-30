"""The federal catalog: credits against federal tax.

The political contribution credit, the labour-sponsored funds credit, the countries and sheets of
the foreign tax credit with the lines of its business part, and the federal tax less credits.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

POLITICAL_CREDIT_COLUMN_1_LINE_2 = CATALOG.declare(
    "political_credit_column_1_line_2", Decimal, non_negative=True
)
"""Federal political contribution credit column 1 line 2, Federal Worksheet "Column 1: Line 40900 is
$400 or less", line 2 "0.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_1_LINE_3 = CATALOG.declare(
    "political_credit_column_1_line_3", Decimal, non_negative=True
)
"""Federal political contribution credit column 1 line 3, Federal Worksheet "Column 1: Line 40900 is
$400 or less", line 3 "Line 1 minus line 2 (if negative, enter "0") =": the contributions less line
2, not below zero."""

POLITICAL_CREDIT_COLUMN_1_LINE_5 = CATALOG.declare(
    "political_credit_column_1_line_5", Decimal, non_negative=True
)
"""Federal political contribution credit column 1 line 5, Federal Worksheet "Column 1: Line 40900 is
$400 or less", line 5 "Line 3 multiplied by the percentage from line 4 =": line 3 at the line 4 rate
of 75%."""

POLITICAL_CREDIT_COLUMN_1_LINE_6 = CATALOG.declare(
    "political_credit_column_1_line_6", Decimal, non_negative=True
)
"""Federal political contribution credit column 1 line 6, Federal Worksheet "Column 1: Line 40900 is
$400 or less", line 6 "0.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_1_LINE_7 = CATALOG.declare(
    "political_credit_column_1_line_7", Decimal, non_negative=True
)
"""Federal political contribution credit column 1 line 7, Federal Worksheet "Column 1: Line 40900 is
$400 or less", line 7 "Line 5 plus line 6 Enter this amount on line 41000 of your return. =": line 5
plus line 6."""

POLITICAL_CREDIT_COLUMN_2_LINE_2 = CATALOG.declare(
    "political_credit_column_2_line_2", Decimal, non_negative=True
)
"""Federal political contribution credit column 2 line 2, Federal Worksheet "Column 2: Line 40900 is
more than $400 but not more than $750", line 2 "400.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_2_LINE_3 = CATALOG.declare(
    "political_credit_column_2_line_3", Decimal, non_negative=True
)
"""Federal political contribution credit column 2 line 3, Federal Worksheet "Column 2: Line 40900 is
more than $400 but not more than $750", line 3 "Line 1 minus line 2 (if negative, enter "0") =": the
contributions less line 2, not below zero."""

POLITICAL_CREDIT_COLUMN_2_LINE_5 = CATALOG.declare(
    "political_credit_column_2_line_5", Decimal, non_negative=True
)
"""Federal political contribution credit column 2 line 5, Federal Worksheet "Column 2: Line 40900 is
more than $400 but not more than $750", line 5 "Line 3 multiplied by the percentage from line 4 =":
line 3 at the line 4 rate of 50%."""

POLITICAL_CREDIT_COLUMN_2_LINE_6 = CATALOG.declare(
    "political_credit_column_2_line_6", Decimal, non_negative=True
)
"""Federal political contribution credit column 2 line 6, Federal Worksheet "Column 2: Line 40900 is
more than $400 but not more than $750", line 6 "300.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_2_LINE_7 = CATALOG.declare(
    "political_credit_column_2_line_7", Decimal, non_negative=True
)
"""Federal political contribution credit column 2 line 7, Federal Worksheet "Column 2: Line 40900 is
more than $400 but not more than $750", line 7 "Line 5 plus line 6 Enter this amount on line 41000
of your return. =": line 5 plus line 6."""

POLITICAL_CREDIT_COLUMN_3_LINE_2 = CATALOG.declare(
    "political_credit_column_3_line_2", Decimal, non_negative=True
)
"""Federal political contribution credit column 3 line 2, Federal Worksheet "Column 3: Line 40900 is
more than more than $750", line 2 "750.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_3_LINE_3 = CATALOG.declare(
    "political_credit_column_3_line_3", Decimal, non_negative=True
)
"""Federal political contribution credit column 3 line 3, Federal Worksheet "Column 3: Line 40900 is
more than more than $750", line 3 "Line 1 minus line 2 (if negative, enter "0") =": the
contributions less line 2, not below zero."""

POLITICAL_CREDIT_COLUMN_3_LINE_5 = CATALOG.declare(
    "political_credit_column_3_line_5", Decimal, non_negative=True
)
"""Federal political contribution credit column 3 line 5, Federal Worksheet "Column 3: Line 40900 is
more than more than $750", line 5 "Line 3 multiplied by the percentage from line 4 =": line 3 at the
line 4 rate of 33.33%."""

POLITICAL_CREDIT_COLUMN_3_LINE_6 = CATALOG.declare(
    "political_credit_column_3_line_6", Decimal, non_negative=True
)
"""Federal political contribution credit column 3 line 6, Federal Worksheet "Column 3: Line 40900 is
more than more than $750", line 6 "475.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_3_LINE_7 = CATALOG.declare(
    "political_credit_column_3_line_7", Decimal, non_negative=True
)
"""Federal political contribution credit column 3 line 7, Federal Worksheet "Column 3: Line 40900 is
more than more than $750", line 7 "Line 5 plus line 6 Enter this amount on line 41000 of your
return. =": line 5 plus line 6."""

POLITICAL_CREDIT_CHOSEN_COLUMN = CATALOG.declare(
    "political_credit_chosen_column", Decimal, non_negative=True
)
"""Federal political contribution credit, the column that applies, Federal Worksheet "Line 41000 -
Federal political contribution tax credit": the line 7 of column 1 if line 40900 is $400 or less,
of column 2 if it is more than $400 but not more than $750, of column 3 if it is more than $750."""

POLITICAL_CREDIT_SHORTCUT_THRESHOLD = CATALOG.declare(
    "political_credit_shortcut_threshold", Decimal, non_negative=True
)
"""Federal political contribution credit shortcut threshold, Federal Worksheet "Line 41000 -
Federal political contribution tax credit": "If your total federal political contributions from
line 40900 of your return were" "$1,275 or more, enter $650 on line 41000 of your return.": the
printed $1,275, a constant."""

POLITICAL_CREDIT_SHORTCUT_AMOUNT = CATALOG.declare(
    "political_credit_shortcut_amount", Decimal, non_negative=True
)
"""Federal political contribution credit shortcut amount, Federal Worksheet "Line 41000 - Federal
political contribution tax credit": "$1,275 or more, enter $650 on line 41000 of your return.": the
printed $650, a constant."""

POLITICAL_CREDIT_BEFORE_MAXIMUM = CATALOG.declare(
    "political_credit_before_maximum", Decimal, non_negative=True
)
"""Federal political contribution credit before its maximum, Federal Worksheet "Line 41000 -
Federal political contribution tax credit": the printed $650 when line 40900 is $1,275 or more,
otherwise the line 7 of the column that applies."""

POLITICAL_CREDIT = CATALOG.declare("political_credit", Decimal, non_negative=True)
"""Federal political contribution tax credit, T1 line 135 and line 41000 "Total federal political
contributions (attach receipts) Line 40900 (maximum $650)": the worksheet's result, at most
$650."""

LABOUR_SPONSORED_FUNDS_NET_COST = CATALOG.declare(
    "labour_sponsored_funds_net_cost", Decimal, non_negative=True
)
"""Net cost of shares of a provincially registered fund, T1 line 137, line 41300 "Net cost of shares
of a provincially registered fund": the caller's net cost, as entered."""

LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM = CATALOG.declare(
    "labour_sponsored_funds_credit_before_maximum", Decimal, non_negative=True
)
"""Labour-sponsored funds credit before the maximum, T1 line 137 (line 41400): the guide's "equal to
15% of the net cost reported on line 41300 of your return", before its "to a maximum of $750"."""

LABOUR_SPONSORED_FUNDS_CREDIT = CATALOG.declare(
    "labour_sponsored_funds_credit", Decimal, non_negative=True
)
"""Labour-sponsored funds tax credit, T1 line 137 and line 41400 "Labour-sponsored funds tax credit
Line 41300: Net cost of shares of a provincially registered fund Line 41300: Allowable credit": the
guide's "allowable credit on line 41400 of your return that is equal to 15% of the net cost
reported on line 41300 of your return, to a maximum of $750."."""

LOGGING_TAX_PAID = CATALOG.declare("logging_tax_paid", Decimal, non_negative=True)
"""Logging tax paid to a province, 5000-G "Federal logging tax credit": "66.6667% of the logging tax
that you paid to that province for the year": the caller's figure for that province; a field of
each record of the logging operations, not an artifact of its own."""

NET_LOGGING_INCOME = CATALOG.declare("net_logging_income", Decimal, non_negative=True)
"""Net logging income in a province, 5000-G "Federal logging tax credit": "6.6667% of your net
logging income in that province for the year": the caller's figure for that province; a field of
each record of the logging operations, not an artifact of its own."""

LOGGING_OPERATIONS = RecordListKind.declare(
    CATALOG, "logging_operations", fields=(LOGGING_TAX_PAID, NET_LOGGING_INCOME)
)
"""Provinces with a logging operation, 5000-G "Federal logging tax credit": "for each province you
had a logging operation in": a starting list with one record for each such province, holding the
logging tax paid to it and the net logging income in it. The list may be empty."""

PROVINCES_LOGGING_TAX_CREDIT = CATALOG.declare(
    "provinces_logging_tax_credit", Decimal, non_negative=True
)
"""Federal logging tax credit over the provinces, 5000-G "To calculate your credit for each
province where you operated, use the lower of the following amounts for each province": the sum
over the provinces of the lesser of 66.6667% of the logging tax paid and 6.6667% of the net
logging income, before the cap of line 133."""

LOGGING_CREDIT_BASE = CATALOG.declare("logging_credit_base", Decimal, non_negative=True)
"""Base of the federal logging tax credit cap, 5000-G "up to 6.6667% of your taxable income from
line 26000 of your return, not including any amounts on lines 20800, 20805, 21000, 21400, 21500,
21900, and 22000": line 26000 with those seven lines added back, the sum of its parts."""

LOGGING_CREDIT_CAP = CATALOG.declare("logging_credit_cap", Decimal, non_negative=True)
"""Cap of the federal logging tax credit, 5000-G "up to 6.6667% of your taxable income from line
26000 of your return": 6.6667% of the base."""

FEDERAL_LOGGING_TAX_CREDIT = CATALOG.declare(
    "federal_logging_tax_credit", Decimal, non_negative=True
)
"""Federal logging tax credit, T1 line 133 "Line 133: Federal logging tax credit", the lesser of
the provinces' total and the cap."""

FEDERAL_TAX = CATALOG.declare("federal_tax", Decimal, non_negative=True)
"""Federal tax, T1 line 134 and line 40600 "Line 134 and line 40600: Line 132 minus line 133 (if
negative, enter "0") Federal tax =": line 132 less line 133, not below zero."""

CREDITS_AGAINST_FEDERAL_TAX = CATALOG.declare(
    "credits_against_federal_tax", Decimal, non_negative=True
)
"""Credits against federal tax, T1 line 138 (line 41600) "Add lines 135 to 137.": line 135
(`political_credit`, 41000), line 136 (`investment_tax_credit`, 41200) and line 137
(`labour_sponsored_funds_credit`), in line order."""

FEDERAL_TAX_LESS_CREDITS = CATALOG.declare("federal_tax_less_credits", Decimal, non_negative=True)
"""Federal tax less credits, T1 line 139 (line 41700) "Line 134 minus line 138 (if negative, enter
"0")": line 134 (`federal_tax`, 40600) less line 138, not below zero."""

FEDERAL_TAX_LINE_41700 = CATALOG.declare("federal_tax_line_41700", Decimal, non_negative=True)
"""Federal tax, T1 line 139 and line 41700 "Line 134 minus line 138 (if negative, enter "0")", or,
when Part 5 line 11 of Form T691 is positive, Part 6 line 14 "Enter this amount on line 41700 of
your return.": the figure entered on line 41700, the federal tax less credits when the count of
"line 11 is positive" is 0, else the Part 6 line 14 amount, never below zero."""

FOREIGN_NON_BUSINESS_TAX_PAID = CATALOG.declare(
    "foreign_non_business_tax_paid", Decimal, non_negative=True
)
"""Non-business income tax paid to a foreign country, Form T2209 line 1 "Non-business income tax
paid to a foreign country (1) 43100": the total of the non-business income or profits tax paid to
that country for the year, minus the part deductible under subsection 20(11) or deducted under
subsection 20(12) of the ITA, as the caller enters it, before the tax on income from property over
15% (`foreign_property_tax_paid`), which the engine takes off line 1 itself and deducts on line
23200, so the caller does not remove it; a field of each record of the foreign tax
countries, not an artifact of its own."""

NET_FOREIGN_NON_BUSINESS_INCOME = CATALOG.declare(
    "net_foreign_non_business_income", Decimal, non_negative=True
)
"""Net foreign non-business income, Form T2209 line 2 "Net foreign non-business income (2) 43300":
the net income from that country; a field of each record of the foreign tax countries, not an
artifact of its own."""

FOREIGN_BUSINESS_TAX_PAID = CATALOG.declare("foreign_business_tax_paid", Decimal, non_negative=True)
"""Business income tax paid to a foreign country for the year, Form T2209 line 4 (43400) "Business
income tax paid to a foreign country (5) for the year, plus any unused foreign tax credits for that
country for the 10 years (6) before, and the 3 years after this year", note (5) "Total of business
income or profits tax you paid to a country or a political subdivision of a country for the
year.": the first part of line 4; a field of each record of the foreign tax countries and of the
foreign tax credit sheets, not an artifact of its own."""

FOREIGN_BUSINESS_UNUSED_TAX_CREDITS = CATALOG.declare(
    "foreign_business_unused_tax_credits", Decimal, non_negative=True
)
"""Unused business foreign tax credits of that country, Form T2209 line 4 (43400) "plus any unused
foreign tax credits for that country for the 10 years (6) before, and the 3 years after this
year", note (6) "Unused business foreign tax credits can be carried forward 10 years and carried
back 3 years.": the second part of line 4, one figure for the country; a field of each record of
the foreign tax countries and of the foreign tax credit sheets, not an artifact of its own."""

NET_FOREIGN_BUSINESS_INCOME = CATALOG.declare(
    "net_foreign_business_income", Decimal, non_negative=True
)
"""Net foreign business income, Form T2209 line 5 "Net foreign business income (7) 43900", note (7)
"Net amount by which the business income you earned in a foreign country is more than the business
losses you incurred in that country.": a field of each record of the foreign tax countries and,
after the cap at net income of note (7), of the foreign tax credit sheets, not an artifact of its
own."""

FOREIGN_SURTAX_OUTSIDE_CANADA = CATALOG.declare(
    "foreign_surtax_outside_canada", Decimal, non_negative=True
)
"""Federal surtax on income allocated to "Other (Outside Canada)", Form T2209 line 6: "Amount from
line 10 of Part 2 of Form T2203, Provincial and Territorial Taxes for Multiple Jurisdictions, or 48%
of the amount from line 42900 of your return. Enter the amount that applies to the country or
countries you identified at the top of this page.", as the caller enters it for each country: the
part of the one surtax of T1 line 127 (`federal_surtax_outside_canada`) that applies to the
country, 0 when nothing is allocated; a field of each record of the foreign tax countries and of
the foreign tax credit sheets, not an artifact of its own."""

FOREIGN_SURTAX_ALLOCATED_TOTAL = CATALOG.declare(
    "foreign_surtax_allocated_total", Decimal, non_negative=True
)
"""The total of the allocated parts of the federal surtax on income allocated to "Other (Outside
Canada)" over the foreign tax countries, Form T2209 line 6 "Enter the amount that applies to the
country or countries you identified at the top of this page.": the parts of the one surtax of T1
line 127, so the total may not be more than it."""

FOREIGN_SURTAX_ALLOCATED_TOTAL_CHECKED = CATALOG.declare(
    "foreign_surtax_allocated_total_checked", Decimal, non_negative=True
)
"""The total of the allocated parts of the surtax, checked to be at most the federal surtax on
income earned outside Canada of T1 line 127 (`federal_surtax_outside_canada`, held at 0 when it is
negative): above it the return is refused, not capped."""

FOREIGN_SURTAX_LIMIT = CATALOG.declare("foreign_surtax_limit", Decimal, non_negative=True)
"""The most the surtax allocated to the foreign countries can total, Form T2209 line 6: the one
surtax of T1 line 127 (`federal_surtax_outside_canada`), 0 when it is negative (under minimum tax,
Form T691 Part 3 line 4 prints no floor). No positive part can be allocated of a surtax that is not
positive; a negative part is refused by the input kind (#947)."""

FOREIGN_PROPERTY_TAX_PAID = CATALOG.declare("foreign_property_tax_paid", Decimal, non_negative=True)
"""Foreign tax paid on income from property, Form T2209 page 1 note: "If you paid tax on income from
property sourced outside of Canada (other than real or immovable property), your non-business
foreign tax credit for that income cannot be more than 15% of your net income from that property.
However, you may be able to deduct the part of the foreign taxes you paid over 15% on line 23200 of
your return.": the part of the non-business tax paid of line 1 (43100) that is on income from such
property, as the caller enters it; a field of each record of the foreign tax countries, not an
artifact of its own."""

NET_FOREIGN_PROPERTY_INCOME = CATALOG.declare(
    "net_foreign_property_income", Decimal, non_negative=True
)
"""Net foreign income from property, Form T2209 page 1 note: "your net income from that property"
(property sourced outside of Canada, other than real or immovable property): the part of the net
foreign non-business income of line 2 (43300) that is income from such property, as the caller
enters it; a field of each record of the foreign tax countries, not an artifact of its own."""

FOREIGN_TAX_COUNTRIES = RecordListKind.declare(
    CATALOG,
    "foreign_tax_countries",
    fields=(
        FOREIGN_NON_BUSINESS_TAX_PAID,
        NET_FOREIGN_NON_BUSINESS_INCOME,
        FOREIGN_BUSINESS_TAX_PAID,
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
        NET_FOREIGN_BUSINESS_INCOME,
        FOREIGN_SURTAX_OUTSIDE_CANADA,
        FOREIGN_PROPERTY_TAX_PAID,
        NET_FOREIGN_PROPERTY_INCOME,
    ),
)
"""Foreign tax countries, Form T2209 "do the applicable calculation shown on this form for
non-business and business taxes paid to each country on a separate sheet": a starting list with one
record for each country, holding line 1 (43100), line 2 (43300), the two parts of line 4 (43400),
line 5 (43900), line 6, and the foreign tax paid on income from property and that income, for the
15% limit of the page 1 note. The list may be empty."""

FOREIGN_PROPERTY_TAX_OVER_LIMIT = CATALOG.declare(
    "foreign_property_tax_over_limit", Decimal, non_negative=True
)
"""Foreign tax on income from property over the 15% limit, Form T2209 page 1 note: "you may be able
to deduct the part of the foreign taxes you paid over 15% on line 23200 of your return": for each
country the foreign tax paid on income from property less 15% of that income, not below zero,
added; the part of line 1 that is deducted on line 23200 and not credited."""

FOREIGN_TAX_CREDIT_SHEET_LINE_3 = CATALOG.declare(
    "foreign_tax_credit_sheet_line_3", Decimal, non_negative=True
)
"""Federal non-business foreign tax credit of a sheet, Form T2209 line 3 "Enter whichever is less:
the amount from line 1 or line 2.": the lesser of the tax paid and the rounded line 2 of that sheet;
a field of each record of the foreign tax credit sheets, not an artifact of its own."""

FOREIGN_TAX_CREDIT_SHEETS = RecordListKind.declare(
    CATALOG,
    "foreign_tax_credit_sheets",
    fields=(
        FOREIGN_NON_BUSINESS_TAX_PAID,
        NET_FOREIGN_NON_BUSINESS_INCOME,
        FOREIGN_TAX_CREDIT_SHEET_LINE_3,
        FOREIGN_BUSINESS_TAX_PAID,
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
        NET_FOREIGN_BUSINESS_INCOME,
        FOREIGN_SURTAX_OUTSIDE_CANADA,
    ),
)
"""Foreign tax credit sheets, Form T2209 "on a separate sheet": one record for each sheet worked, in
order, holding line 1 (43100), the net foreign income used on line 2 (43300, after the cap at net
income), line 3, the two parts of line 4 (43400), the net foreign business income used on line 5
(43900, after the cap at net income) and line 6. The list may be empty."""

FOREIGN_BUSINESS_TAX_CREDIT_LINE_4 = CATALOG.declare(
    "foreign_business_tax_credit_line_4", Decimal, non_negative=True
)
"""Form T2209 line 4 (43400) "Business income tax paid to a foreign country (5) for the year, plus
any unused foreign tax credits for that country for the 10 years (6) before, and the 3 years after
this year": the total over the sheets."""

FOREIGN_BUSINESS_TAX_CREDIT_LINE_5 = CATALOG.declare(
    "foreign_business_tax_credit_line_5", Decimal, non_negative=True
)
"""Form T2209 line 5 "Net foreign business income (7) 43900" "× Basic federal tax (8)" over "Net
income (3)": the total over the sheets, each rounded."""

FOREIGN_BUSINESS_TAX_CREDIT_LINE_7 = CATALOG.declare(
    "foreign_business_tax_credit_line_7", Decimal, non_negative=True
)
"""Form T2209 line 7 "Add lines 5 and 6.": the total over the sheets."""

FOREIGN_BUSINESS_TAX_CREDIT_LINE_8 = CATALOG.declare(
    "foreign_business_tax_credit_line_8", Decimal, non_negative=True
)
"""Form T2209 line 8 "Add basic federal tax (8) and the amount from line 6.": the total over the
sheets."""

FOREIGN_BUSINESS_TAX_CREDIT_LINE_10 = CATALOG.declare(
    "foreign_business_tax_credit_line_10", Decimal
)
"""Form T2209 line 10 "Line 8 minus line 9": the total over the sheets; it prints no "(if
negative, enter "0")", so it can be below zero."""

FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT = CATALOG.declare(
    "federal_business_foreign_tax_credit", Decimal, non_negative=True
)
"""Federal business foreign tax credit, Form T2209 line 11 "Enter whichever is less: the amount
from line 4, 7 or 10. Federal business foreign tax credit": the total over the sheets of the
least of the sheet's lines 4, 7 and 10."""

FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT = CATALOG.declare(
    "federal_foreign_tax_credit_before_limit", Decimal, non_negative=True
)
"""Federal foreign tax credit before the limit, Form T2209 line 13 "Add lines 11 and 12." "Federal
foreign tax credit": line 11 plus line 12, before "The amount on line 13 should not be more than
the total of the amount on line 42900 of your return, plus any federal surtax on income earned
outside of Canada"."""

ITC_APPRENTICE_SALARY_AND_WAGES = CATALOG.declare(
    "itc_apprentice_salary_and_wages", Decimal, non_negative=True
)
"""Apprentice's eligible salary and wages, Form T2038(IND) Part B Table 1 "The lesser of eligible
salary and wages** payable in the year or $20,000.": each apprentice's eligible salary and wages
payable in the year, net of any assistance; a field of each record of the apprentices, not an
artifact of its own."""

ITC_APPRENTICES = RecordListKind.declare(
    CATALOG, "itc_apprentices", fields=(ITC_APPRENTICE_SALARY_AND_WAGES,)
)
"""Apprentices, Form T2038(IND) Part B Table 1 "Calculation of total Apprenticeship job creation tax
credit": a starting list with one record for each apprentice, holding the eligible salary and wages
(column 3). The list may be empty."""

ITC_APPRENTICESHIP_WAGES_TOTAL = CATALOG.declare(
    "itc_apprenticeship_wages_total", Decimal, non_negative=True
)
"""Apprenticeship wages total, Form T2038(IND) Part B Table 1 "Total apprenticeship job creation tax
credit (Total of amounts in column 3 plus applicable amount from box 40* of your T3 slip)": the
total of the column 3 amounts, before the 10% and before the box 40 amount, which are not part of
this figure."""
