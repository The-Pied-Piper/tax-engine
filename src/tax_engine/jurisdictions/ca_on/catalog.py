"""The Ontario artifact catalog: Ontario's own kinds, named from the Ontario forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_on import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, ON428 line 9 (line 58040) "Basic personal amount Claim $12,747": the
amount claimed, the first part of the total of the Ontario credit amounts."""

ON428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "on428_taxable_income_line_1", non_negative=True
)
"""Taxable income, ON428 line 1 "Enter your taxable income from line 26000 of your return.": the
T1 taxable income, the base of the Part A bracket columns."""

ON428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "on428_bracket_lower_bound_line_3", non_negative=True
)
"""Bracket lower bound, ON428 line 3 (each column prints "Line 3:" with 0.00, 52,886.00, 105,775.00,
150,000.00 or 220,000.00): the printed lower bound of the column that line 1 falls in."""

ON428_TAX_AT_COLUMN_START_LINE_7 = AmountKind.declare(
    CATALOG, "on428_tax_at_column_start_line_7", non_negative=True
)
"""Tax at the column's start, ON428 line 7 (each column prints "Line 7:" with 0.00, 2,670.74,
7,510.09, 12,445.60 or 20,957.60): the printed tax at the start of the column that line 1 falls
in."""

ON428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "on428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, ON428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

ON428_BRACKET_COLUMN_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "on428_bracket_column_rate_line_5", non_negative=True
)
"""Bracket column rate, ON428 line 5 (each column prints "Line 5: Rate" with 5.05%, 9.15%, 11.16%,
12.16% or 13.16%): the printed rate of the column that line 1 falls in."""

ON428_EXCESS_TIMES_COLUMN_RATE_LINE_6 = AmountKind.declare(
    CATALOG, "on428_excess_times_column_rate_line_6", non_negative=True
)
"""Line 4 times the column rate, ON428 line 6 "Line 6: Line 4 multiplied by the percentage from
line 5 =": line 4 times line 5, a fraction, rounded half-up to the cent."""

ON428_PERSONAL_AMOUNTS_SUBTOTAL_LINE_18 = AmountKind.declare(
    CATALOG, "on428_personal_amounts_subtotal_line_18", non_negative=True
)
"""Personal amounts subtotal, ON428 line 18 "Add lines 9, 10, 13, 16, and 17.": the sum of lines
9, 10, 13, 16 and 17."""

ON428_CPP_EI_CREDIT_AMOUNTS_LINE_24 = AmountKind.declare(
    CATALOG, "on428_cpp_ei_credit_amounts_line_24", non_negative=True
)
"""CPP and EI credit amounts subtotal, ON428 line 24 "Add lines 19 to 23.": the sum of lines 19
to 23."""

ON428_CREDITS_SUBTOTAL_LINE_25 = AmountKind.declare(
    CATALOG, "on428_credits_subtotal_line_25", non_negative=True
)
"""Credits subtotal, ON428 line 25 "Line 18 plus line 24 =": line 18 plus line 24."""

ON428_CREDITS_WITH_TRANSFERS_LINE_35 = AmountKind.declare(
    CATALOG, "on428_credits_with_transfers_line_35", non_negative=True
)
"""Total of the credits with the student loan, tuition and transfer amounts, ON428 line 35 "Add
lines 31 to 34.": the sum of line 31 with lines 32 to 34."""

ON428_MEDICAL_EXPENSES_LINE_43 = AmountKind.declare(
    CATALOG, "on428_medical_expenses_line_43", non_negative=True
)
"""Medical expenses, ON428 line 43 and line 58769 "Line 41 plus line 42 =": line 41 "Line 36 minus
line 40 (if negative, enter "0")" plus line 42 "Allowable amount of medical expenses for other
dependants", a part of line 44."""

ON428_TOTAL_CREDIT_AMOUNTS_LINE_44 = AmountKind.declare(
    CATALOG, "on428_total_credit_amounts_line_44", non_negative=True
)
"""Total credit amounts, ON428 line 44 "Line 44 and line 58800: Line 35 plus line 43 =": line 35
plus line 43."""

ON428_CREDIT_AMOUNTS_AT_CREDIT_RATE_LINE_46 = AmountKind.declare(
    CATALOG, "on428_credit_amounts_at_credit_rate_line_46", non_negative=True
)
"""Credit amounts at the credit rate, ON428 line 46 "Line 46 and line 58840: Line 44 multiplied by
the percentage from line 45 =": line 44 times the 5.05% of line 45."""

ON428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "on428_tax_on_taxable_income_line_8", non_negative=True
)
"""Ontario tax on taxable income, ON428 line 8 "Line 6 plus line 7 Ontario tax on taxable income =":
line 6 plus line 7."""

ON428_SURTAX_36_PERCENT_TIER_LINE_67 = AmountKind.declare(
    CATALOG, "on428_surtax_36_percent_tier_line_67", non_negative=True
)
"""36% surtax tier, ON428 line 67 "(Line 65 minus $7,307) multiplied by 36% (if negative, enter
"0") =": 36% of line 65 above $7,307, never below 0."""

ON428_DONATIONS_CREDIT_LINE_49 = AmountKind.declare(
    CATALOG, "on428_donations_credit_line_49", non_negative=True
)
"""Donations and gifts credit, ON428 line 49 "Line 49 and line 58969: Line 47 plus line 48": a
caller input, read as 0 when the filer has no donations or gifts."""

ON428_NON_REFUNDABLE_CREDITS_LINE_50 = AmountKind.declare(
    CATALOG, "on428_non_refundable_credits_line_50", non_negative=True
)
"""Ontario non-refundable tax credits, ON428 line 50 "Line 50 and line 61500: Line 46 plus line 49":
line 46 (the credits at the rate) plus line 49 (the donations and gifts credit)."""

ON428_TAX_MINUS_CREDITS_LINE_53 = AmountKind.declare(
    CATALOG, "on428_tax_minus_credits_line_53", non_negative=True
)
"""Tax minus credits, ON428 line 53 "Line 51 minus line 52 (if negative, enter "0") =": line 8
(copied to line 51) minus line 50 (copied to line 52), not below 0."""

ON428_TAX_ON_SPLIT_INCOME_LINE_54 = AmountKind.declare(CATALOG, "on428_tax_on_split_income_line_54")
"""Ontario tax on split income, ON428 line 54 "Line 54 and line 61510: Ontario tax on split income
(complete Form T1206)": the tax from Form T1206."""

ON428_TAX_WITH_SPLIT_INCOME_LINE_55 = AmountKind.declare(
    CATALOG, "on428_tax_with_split_income_line_55"
)
"""Tax with split income, ON428 line 55 "Line 55: Line 53 plus line 54 =": line 53 plus line 54."""

ON428_MINIMUM_TAX_CARRYOVER_LINE_60 = AmountKind.declare(
    CATALOG, "on428_minimum_tax_carryover_line_60", non_negative=True
)
"""Minimum tax carryover applied, ON428 line 60 "Line 60 and line 61540: Enter whichever is less:
amount from line 58 or line 59.": the lesser of line 58 and line 59, an optional input that a
salary-only caller leaves out."""

ON428_TAX_AFTER_MINIMUM_TAX_CARRYOVER_LINE_61 = AmountKind.declare(
    CATALOG, "on428_tax_after_minimum_tax_carryover_line_61", non_negative=True
)
"""Ontario tax after the minimum tax carryover, ON428 line 61 "Line 61: Line 55 minus line 60 (if
negative, enter "0") =": line 55 minus line 60, not below zero."""

ON428_SURTAX_BASE_LINE_65 = AmountKind.declare(
    CATALOG, "on428_surtax_base_line_65", non_negative=True
)
"""Surtax base, ON428 line 65 "Line 65: Line 63 minus line 64 (if negative, enter "0") =": line 61
less line 54, never below zero."""

ON428_SURTAX_20_PERCENT_TIER_LINE_66 = AmountKind.declare(
    CATALOG, "on428_surtax_20_percent_tier_line_66", non_negative=True
)
"""Surtax 20% tier, ON428 line 66 "(Line 65 minus $5,710) multiplied by 20% (if negative, enter
"0") =": 20% of line 65 above $5,710, never below 0."""

ON428_SURTAX_TOTAL_LINE_68 = AmountKind.declare(
    CATALOG, "on428_surtax_total_line_68", non_negative=True
)
"""Ontario surtax, ON428 line 68 "Line 66 plus line 67 =": line 66 plus line 67."""

ON428_DIVIDEND_TAX_CREDIT_LINE_57 = AmountKind.declare(
    CATALOG, "on428_dividend_tax_credit_line_57", non_negative=True
)
"""Ontario dividend tax credit, ON428 line 57 "Line 57 and line and line 61520: Ontario dividend
tax credit (use Worksheet ON428)": an optional input that a salary-only caller leaves out."""

ON428_TAX_WITH_SURTAX_LINE_69 = AmountKind.declare(
    CATALOG, "on428_tax_with_surtax_line_69", non_negative=True
)
"""ON428 line 69 "Line 69: Line 62 plus line 68 =": line 61 plus line 68."""

ON428_BASIC_REDUCTION_LINE_74 = AmountKind.declare(
    CATALOG, "on428_basic_reduction_line_74", non_negative=True
)
"""Basic reduction, ON428 line 74 "Basic reduction 294.00": the amount claimed, the first part of
line 77."""

ON428_TAX_AFTER_DIVIDEND_CREDIT_LINE_71 = AmountKind.declare(
    CATALOG, "on428_tax_after_dividend_credit_line_71", non_negative=True
)
"""Ontario tax after the dividend tax credit, ON428 line 71 "Line 71: Line 69 minus line 70 (if
negative, enter "0") =": line 69 minus the dividend tax credit, not below zero."""

ON428_ADDITIONAL_TAX_FOR_MINIMUM_TAX_LINE_72 = AmountKind.declare(
    CATALOG, "on428_additional_tax_for_minimum_tax_line_72", non_negative=True
)
"""Additional tax for minimum tax purposes, ON428 line 72 "Line 72: If you entered an amount on line
11 of Part 5 of Form T691, use Worksheet ON428 to calculate your additional tax for minimum tax
purposes": an optional input that a salary-only caller leaves out."""

ON428_TAX_WITH_MINIMUM_TAX_ADDITION_LINE_73 = AmountKind.declare(
    CATALOG, "on428_tax_with_minimum_tax_addition_line_73", non_negative=True
)
"""Tax with the minimum tax addition, ON428 line 73 "Line 73: Line 71 plus line 72 =": line 71 plus
line 72."""

ON428_TAX_REDUCTION_LINE_77 = AmountKind.declare(
    CATALOG, "on428_tax_reduction_line_77", non_negative=True
)
"""Tax reduction, ON428 line 77 "Add lines 74 to 76": the sum of the reduction parts, which for a
single filer with no dependants is the basic reduction on line 74 alone."""

ON428_TAX_REDUCTION_DOUBLED_LINE_78 = AmountKind.declare(
    CATALOG, "on428_tax_reduction_doubled_line_78", non_negative=True
)
"""Doubled tax reduction, ON428 line 78 "Amount from line 77 above multiplied by 2 =": line 77
multiplied by 2."""

ON428_TAX_REDUCTION_BEFORE_CONDITIONS_LINE_80 = AmountKind.declare(
    CATALOG, "on428_tax_reduction_before_conditions_line_80", non_negative=True
)
"""Ontario tax reduction before the conditions, ON428 line 80 "Line 80: Line 78 minus line 79 (if
negative, enter "0") Ontario tax reduction =": line 78 minus line 79 (a copy of line 73), not below
zero, before the printed "Enter "0" on line 80 if any of the following applies to you" rule."""

ON428_TAX_REDUCTION_CONDITIONS_COUNT_LINE_80 = CountKind.declare(
    CATALOG, "on428_tax_reduction_conditions_count_line_80", non_negative=True
)
"""Conditions count for ON428 line 80, "Enter "0" on line 80 if any of the following applies to
you:" "There is an amount on line 72": 0 when there is an amount on line 72, else 1."""

ON428_ONTARIO_TAX_REDUCTION_LINE_80 = AmountKind.declare(
    CATALOG, "on428_ontario_tax_reduction_line_80", non_negative=True
)
"""Ontario tax reduction, ON428 line 80 "Line 80: Line 78 minus line 79 (if negative, enter "0")
Ontario tax reduction =": the line 78 minus line 79 box, not below zero, or "0" when the printed
"Enter "0" on line 80 if any of the following applies to you" rule applies (take-home: there is
an amount on line 72)."""

ON428_TAX_AFTER_TAX_REDUCTION_LINE_81 = AmountKind.declare(
    CATALOG, "on428_tax_after_tax_reduction_line_81", non_negative=True
)
"""Ontario tax after the tax reduction, ON428 line 81 "Line 81: Line 73 minus line 80 (if negative,
enter "0") =": line 73 minus the Ontario tax reduction, not below zero."""

ON428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_82 = AmountKind.declare(
    CATALOG, "on428_provincial_foreign_tax_credit_line_82", non_negative=True
)
"""Provincial foreign tax credit, ON428 line 82 "Line 82: Provincial foreign tax credit (complete
Form T2036)": an optional input that a salary-only caller leaves out."""

ON428_TAX_AFTER_FOREIGN_TAX_CREDIT_LINE_83 = AmountKind.declare(
    CATALOG, "on428_tax_after_foreign_tax_credit_line_83", non_negative=True
)
"""Ontario tax after the foreign tax credit, ON428 line 83 "Line 83: Line 81 minus line 82 (if
negative, enter "0") =": line 81 minus line 82, not below zero."""

ON428_LIFT_CREDIT_LINE_85 = AmountKind.declare(
    CATALOG, "on428_lift_credit_line_85", non_negative=True
)
"""Low-income individuals and families tax (LIFT) credit, ON428 line 85 "Line 85 and line 62140:
Low-income individuals and families tax (LIFT) credit (complete Schedule ON428-A)": the LIFT credit
for a single filer, Schedule ON428-A Part A line 20."""

ON428_TAX_AFTER_LIFT_CREDIT_LINE_86 = AmountKind.declare(
    CATALOG, "on428_tax_after_lift_credit_line_86", non_negative=True
)
"""Ontario tax after the LIFT credit, ON428 line 86 "Line 86: Line 84 minus line 85 (if negative,
enter "0") =": line 84 minus the LIFT credit, not below zero."""

ON428_QUALIFYING_FOOD_DONATIONS_LINE_87 = AmountKind.declare(
    CATALOG, "on428_qualifying_food_donations_line_87", non_negative=True
)
"""Qualifying food donations, ON428 line 87 "Line 87 and line 62150: Enter the amount of qualifying
donations that have also been claimed as a charitable donation": an optional input that a
salary-only caller leaves out, read as 0."""

ON428_FARMERS_FOOD_DONATION_CREDIT_LINE_87 = AmountKind.declare(
    CATALOG, "on428_farmers_food_donation_credit_line_87", non_negative=True
)
"""Farmers' food donation credit, ON428 line 87 "Line 87 and line 62150: Enter the amount of
qualifying donations that have also been claimed as a charitable donation. multiplied by 25% =":
calculated, the qualifying donations multiplied by 25%."""

ON428_TAX_AFTER_FARMERS_FOOD_DONATION_CREDIT_LINE_88 = AmountKind.declare(
    CATALOG, "on428_tax_after_farmers_food_donation_credit_line_88", non_negative=True
)
"""Ontario tax after the farmers' food donation credit, ON428 line 88 "Line 88: Line 86 minus line
87 (if negative, enter "0") =": line 86 minus line 87, never below zero."""

ON428_TAXABLE_INCOME_LINE_89 = AmountKind.declare(
    CATALOG, "on428_taxable_income_line_89", non_negative=True
)
"""Taxable income, ON428 line 89 chart line 1 "Enter your taxable income from line 26000 of your
return": the T1 taxable income, read from its record list."""

ON428_ONTARIO_HEALTH_PREMIUM_LINE_89 = AmountKind.declare(
    CATALOG, "on428_ontario_health_premium_line_89", non_negative=True
)
"""Ontario health premium, ON428 line 89 "Ontario health premium (complete the chart below)": the
row of the chart that line 1 falls in, its figure rounded half-up to the cent."""

ON428_ONTARIO_TAX_LINE_90 = AmountKind.declare(
    CATALOG, "on428_ontario_tax_line_90", non_negative=True
)
"""Ontario tax, ON428 line 90 "Line 90: Line 88 plus line 89 Enter this amount on line 42800 of your
return. Ontario tax =": line 88 plus line 89, entered on T1 line 42800."""

ON428_CPP_BASE_CREDIT_AMOUNT_LINE_19 = AmountKind.declare(
    CATALOG, "on428_cpp_base_credit_amount_line_19", non_negative=True
)
"""CPP base contributions credit amount, ON428 line 19 and line 58240 "Amount from line 30800 of
your return": a copy of Schedule 8 line 25, the CPP base contributions on the return."""

ON428_EI_CREDIT_AMOUNT_LINE_21 = AmountKind.declare(
    CATALOG, "on428_ei_credit_amount_line_21", non_negative=True
)
"""EI premiums credit amount, ON428 line 21 and line 58300: a copy of T2204 line 16, the EI
premiums credit amount."""

ON428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "on428_pension_income_amount", non_negative=True
)
"""Pension income amount, ON428 line 27 "Line 27 and line 58360: Pension income amount (maximum
$1,762)": the amount the filer claims, a caller input that is read as 0 when it is left out."""

ON428_CREDITS_WITH_PENSION_LINE_28 = AmountKind.declare(
    CATALOG, "on428_credits_with_pension_line_28", non_negative=True
)
"""Ontario credits with the pension income amount, ON428 line 28 "Line 28: Line 26 plus line 27 =":
line 26 "Amount from line 25 of the previous page" (a copy of line 25) plus line 27 (the pension
income amount)."""

ON428_CREDITS_WITH_DISABILITY_LINE_31 = AmountKind.declare(
    CATALOG, "on428_credits_with_disability_line_31", non_negative=True
)
"""Total of the credits with the disability amounts, ON428 line 31 "Add lines 28 to 30.": the sum
of line 28 with the disability amounts of lines 29 and 30."""

TAX_REDUCTION_BASIC = AmountKind.declare(CATALOG, "tax_reduction_basic", non_negative=True)
"""Basic reduction, ON428 line 74 "Basic reduction 294.00": the amount claimed, the first part of
the Ontario tax reduction amounts."""

LIFT_EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "lift_employment_income", non_negative=True)
"""LIFT employment income, Schedule ON428-A line 3 "Line 1 plus line 2": line 1 "Amount from line
10100 of your return" (employment income) plus line 2 "Amount from line 10400 of your return"
(other employment income), in line order, the base of the LIFT rate on line 5."""

LIFT_CREDIT_BEFORE_MAXIMUM = AmountKind.declare(
    CATALOG, "lift_credit_before_maximum", non_negative=True
)
"""LIFT credit before its maximum, Schedule ON428-A line 5 "Line 3 multiplied by the percentage
from line 4 (maximum $875)" before the maximum: line 4 "Applicable rate 5.05%" on line 3 "Line 1
plus line 2", the sum of employment income (line 1 "Amount from line 10100 of your return") and
other employment income (line 2 "Amount from line 10400 of your return")."""

LIFT_MAXIMUM_CREDIT = AmountKind.declare(CATALOG, "lift_maximum_credit", non_negative=True)
"""LIFT credit at most its maximum, Schedule ON428-A line 5's "(maximum $875)", Part A line 14
"Amount from line 5 above (maximum $875)" and Part B line 29 "Amount from line 5 of the previous
page (maximum $875)"."""

LIFT_NET_INCOME = AmountKind.declare(CATALOG, "lift_net_income", non_negative=False)
"""Net income, Schedule ON428-A line 6 "Net income from line 23600 of your return (or the amount
you would have entered if the instructions on line 23600 said "if negative, show in brackets")",
which line 9 "Add lines 6 to 8." takes. Line 6 may be negative, so the kind is signed."""

LIFT_ADJUSTED_NET_INCOME = AmountKind.declare(
    CATALOG, "lift_adjusted_net_income", non_negative=True
)
"""Adjusted net income, Schedule ON428-A line 13 "Line 9 minus line 12 (if negative, enter "0")
Your adjusted net income", which Part A line 15 "Amount from line 13 above" and Part B line 30
"Amount from line 13 of the previous page" take."""

LIFT_SINGLE_EXCESS_OVER_THRESHOLD = AmountKind.declare(
    CATALOG, "lift_single_excess_over_threshold", non_negative=True
)
"""Excess over the individual threshold, Schedule ON428-A Part A line 17 "Line 15 minus line 16 (if
negative, enter "0")", line 15 being "Amount from line 13 above" and line 16 "Individual income
threshold 32,500.00"."""

LIFT_REDUCTION = AmountKind.declare(CATALOG, "lift_reduction", non_negative=True)
"""LIFT credit reduction, Schedule ON428-A Part A line 19 "Line 17 multiplied by the percentage
from line 18": line 18 "Applicable rate 5%" on line 17 "Line 15 minus line 16 (if negative, enter
"0")", line 16 "Individual income threshold 32,500.00".

Line 15 is "Amount from line 13 above", the adjusted net income (line 13). The schedule states no
eligibility rules of its own ("To find out if you are eligible for the low-income individuals and
families tax (LIFT) credit, go to canada.ca/on-tax-info.").
"""

LIFT_CREDIT_SINGLE = AmountKind.declare(CATALOG, "lift_credit_single", non_negative=True)
"""LIFT credit for a single individual, Schedule ON428-A Part A line 20 "Line 14 minus line 19 (if
negative, enter "0") Enter this amount on line 62140 of your Form ON428.": the maximum credit less
the reduction."""

LIFT_INDIVIDUAL_INCOME_THRESHOLD = AmountKind.declare(
    CATALOG, "lift_individual_income_threshold", non_negative=True
)
"""Individual income threshold, Schedule ON428-A Part A line 16 "Individual income threshold
32,500.00" and Part B line 31 "Individual income threshold 32,500.00": a printed amount, taken
whole."""

ONTARIO_SURTAX_BASE = AmountKind.declare(CATALOG, "ontario_surtax_base", non_negative=True)
"""Ontario surtax base, ON428 line 65 "Line 65: Line 63 minus line 64 (if negative, enter "0") =":
the figure on the return summary, the one amount of ON428's export of line 65 totalled into the
return's own artifact."""

ONTARIO_SURTAX_FACTOR = AmountKind.declare(CATALOG, "ontario_surtax_factor", non_negative=True)
"""Ontario surtax factor, ON428 line 66 "(Line 65 minus $5,710) multiplied by 20%" and line 67
"(Line 65 minus $7,307) multiplied by 36%": 1 plus the rate of each surtax tier line 65 is over,
the tax a further dollar of Ontario tax brings with the surtax. A plain figure with no unit, not
printed on the form."""

ONTARIO_BRACKET_RATE_RETURN = AmountKind.declare(
    CATALOG, "ontario_bracket_rate_return", non_negative=True
)
"""Ontario bracket rate, ON428 line 5 "Line 5: Rate": the printed rate of the column that line 1
falls in, read from ON428 into the return summary."""

RETURN_TAXABLE_INCOME = AmountKind.declare(CATALOG, "return_taxable_income", non_negative=True)
"""Taxable income on the Return summary: the T1 taxable income (line 26000), the base of the
health premium chart."""

RETURN_HEALTH_PREMIUM_SLOPE = AmountKind.declare(
    CATALOG, "return_health_premium_slope", non_negative=True
)
"""Health premium slope, ON428 line 89 chart: the printed rate of the chart row that the taxable
income falls in (6% or 25%), 0 for a flat row."""
