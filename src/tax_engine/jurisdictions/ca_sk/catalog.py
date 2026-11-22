"""The Saskatchewan artifact catalog: Saskatchewan's own kinds, named from the Saskatchewan forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_sk import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

SK428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "sk428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form SK428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3 and 4."""

SK428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "sk428_tax_on_taxable_income_line_8", non_negative=True
)
"""Saskatchewan tax on taxable income, SK428 line 8 "Line 6 plus line 7 Saskatchewan tax on taxable
income =": line 6 plus line 7, read by line 58 on the tax form."""

SK428_EI_PREMIUMS_LINE_24 = AmountKind.declare(
    CATALOG, "sk428_ei_premiums_line_24", non_negative=True
)
"""EI premiums credit amount, SK428 line 24 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

SK428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "sk428_pension_income_amount", non_negative=True
)
"""Pension income amount, SK428 line 33 "Line 33 and line 58360: Pension income amount (maximum
$1,000)": the amount the filer claims, a caller input that is read as 0 when it is left out;
the line 33 step checks it against the printed maximum."""

SK428_MEDICAL_EXPENSES_LINE_43 = AmountKind.declare(
    CATALOG, "sk428_medical_expenses_line_43", non_negative=True
)
"""Medical expenses, SK428 line 43 (line 58689) "Amount from line 33099 of your return": a
record total of the T1's export (`ca/medical_expenses_line_33099`), 0 for a salary-only caller."""

SK428_NET_INCOME_LINE_44 = AmountKind.declare(
    CATALOG, "sk428_net_income_line_44", non_negative=True
)
"""Net income, SK428 line 44 "Amount from line 23600 of your return": the T1 net income, read from
the T1 taxable income form."""

SK428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_46 = AmountKind.declare(
    CATALOG, "sk428_medical_expenses_rate_amount_line_46", non_negative=True
)
"""Medical expenses threshold, SK428 line 46 "Line 44 multiplied by the percentage from line 45 =":
line 44 times the 3% of line 45."""

SK428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_47 = AmountKind.declare(
    CATALOG, "sk428_medical_expenses_limited_amount_line_47", non_negative=True
)
"""Medical expenses threshold, limited, SK428 line 47 "Enter whichever is less: $2,681 or the amount
on line 46.": the lesser of the printed ceiling and line 46."""

SK428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48 = AmountKind.declare(
    CATALOG, "sk428_medical_expenses_over_limit_line_48", non_negative=True
)
"""Medical expenses over the limit, SK428 line 48 "Line 43 minus line 47 (if negative, enter "0")
=": line 43 minus line 47, never below 0; a blank line 43 is read as 0."""

SK428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49 = AmountKind.declare(
    CATALOG, "sk428_other_dependants_medical_expenses_line_49", non_negative=True
)
"""Allowable amount of medical expenses for other dependants, SK428 line 49 (line 58729) "from line
33199 of your return": a record total of the T1's export
(`ca/other_dependants_medical_expenses_line_33199`), 0 for a salary-only caller."""

SK428_MEDICAL_EXPENSES_LINE_50 = AmountKind.declare(
    CATALOG, "sk428_medical_expenses_line_50", non_negative=True
)
"""Medical expenses, SK428 line 50 (line 58769) "Line 48 plus line 49 =": line 48 plus line 49 (a
blank line 49 is read as 0)."""

SK428_DONATIONS_AMOUNT_LINE_54 = AmountKind.declare(
    CATALOG, "sk428_donations_amount_line_54", non_negative=True
)
"""Donations amount, SK428 line 54 box A "Amount from line 13 of your federal Schedule 9": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

SK428_DONATIONS_CREDIT_AT_RATE_LINE_54 = AmountKind.declare(
    CATALOG, "sk428_donations_credit_at_rate_line_54", non_negative=True
)
"""Donations credit at 10.5%, SK428 line 54 box B "Amount from line 13 of your federal Schedule 9
multiplied by 10.5% =": the Schedule 9 amount times 10.5%; a blank amount is read as 0."""

SK428_DONATIONS_AMOUNT_LINE_55 = AmountKind.declare(
    CATALOG, "sk428_donations_amount_line_55", non_negative=True
)
"""Donations amount, SK428 line 55 box A "Amount from line 14 of your federal Schedule 9": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

SK428_DONATIONS_CREDIT_AT_RATE_LINE_55 = AmountKind.declare(
    CATALOG, "sk428_donations_credit_at_rate_line_55", non_negative=True
)
"""Donations credit at 14.5%, SK428 line 55 box B "Amount from line 14 of your federal Schedule 9
multiplied by 14.5% =": the Schedule 9 amount times 14.5%; a blank amount is read as 0."""

SK428_DONATIONS_CREDIT_LINE_56 = AmountKind.declare(
    CATALOG, "sk428_donations_credit_line_56", non_negative=True
)
"""Donations and gifts credit, SK428 line 56 (58969) "Line 56 and 58969: Line 54 plus line 55 =":
line 54 plus line 55; line 57 reads it."""

SK428_NON_REFUNDABLE_CREDITS_LINE_57 = AmountKind.declare(
    CATALOG, "sk428_non_refundable_credits_line_57", non_negative=True
)
"""Saskatchewan non-refundable tax credits, SK428 line 57 "Line 57 and line 61500: Line 53 plus line
56 Enter this amount on line 63. Saskatchewan non-refundable tax credits =": line 53 plus line 56,
read by line 63 on the tax form."""

SK428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_70 = AmountKind.declare(
    CATALOG, "sk428_provincial_foreign_tax_credit_line_70", non_negative=True
)
"""Provincial foreign tax credit, SK428 line 70 "Line 70: Provincial foreign tax credit (complete
Form T2036)": the credit from Form T2036, an optional input that a salary-only caller leaves out."""

SK428_GRADUATE_TUITION_CREDIT_LINE_81 = AmountKind.declare(
    CATALOG, "sk428_graduate_tuition_credit_line_81", non_negative=True
)
"""Saskatchewan graduate tuition tax credit, SK428 line 81 (line 63640) "Line 81 and line 63640:
Saskatchewan graduate tuition tax credit (complete Form RC360)": the credit from Form RC360, an
optional input that a salary-only caller leaves out."""

SK428_SASKATCHEWAN_TAX_LINE_82 = AmountKind.declare(
    CATALOG, "sk428_saskatchewan_tax_line_82", non_negative=True
)
"""Saskatchewan tax, SK428 line 82 "Enter this amount on line 42800 of your return.": the
Saskatchewan tax, entered on T1 line 42800."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, SK428 line 9 and line 58040 "Basic personal amount Claim $19,491": the
amount claimed, one of the credit amounts that the Saskatchewan non-refundable credits total is
built from."""

SK428_CPP_CONTRIBUTIONS_LINE_22 = AmountKind.declare(
    CATALOG, "sk428_cpp_contributions_line_22", non_negative=True
)
"""CPP or QPP contributions, SK428 line 22 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

SK428_FARM_CAPITAL_GAINS_CREDIT_LINE_59 = AmountKind.declare(
    CATALOG, "sk428_farm_capital_gains_credit_line_59", non_negative=True
)
"""Saskatchewan farm and small business capital gains tax credit, SK428 line 59 (line 61499) "Line
59 and line 61499: Saskatchewan farm and small business capital gains tax credit (complete Form
T1237)": a caller input, read as blank when left out; line 60 reads it."""

SK428_TAX_ON_SPLIT_INCOME_LINE_61 = AmountKind.declare(CATALOG, "sk428_tax_on_split_income_line_61")
"""Saskatchewan tax on split income, SK428 line 61 (line 61510) "Line 61 and line 61510:
Saskatchewan tax on split income (complete Form T1206)": a caller input, read as blank when left
out."""

SK428_DIVIDEND_TAX_CREDIT_LINE_64 = AmountKind.declare(
    CATALOG, "sk428_dividend_tax_credit_line_64", non_negative=True
)
"""Saskatchewan dividend tax credit, SK428 line 64 (line 61520) "Line 64 and line 61520:
Saskatchewan dividend tax credit (use Worksheet SK428)": computed from Worksheet SK428 (5008-D), the
sum of its line 1 and line 2 over the T1 lines 12000 and 12010. A caller who gives neither line has
a credit of 0.00."""

SK428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_A = AmountKind.declare(
    CATALOG, "sk428_dividend_tax_credit_worksheet_line_a", non_negative=True
)
"""Saskatchewan dividend tax credit worksheet, SK428 line 64 (Worksheet SK428, 5008-D), Line A
"Amount from line 12000 of your return": the T1 line 12000 total."""

SK428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_B = AmountKind.declare(
    CATALOG, "sk428_dividend_tax_credit_worksheet_line_b", non_negative=True
)
"""Saskatchewan dividend tax credit worksheet, SK428 line 64 (Worksheet SK428, 5008-D), Line B
"Amount from line 12010 of your return": the T1 line 12010 total."""

SK428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_1 = AmountKind.declare(
    CATALOG, "sk428_dividend_tax_credit_worksheet_line_1", non_negative=True
)
"""Saskatchewan dividend tax credit worksheet, SK428 line 64 (Worksheet SK428, 5008-D), Line 1
"Amount from line 12010 of your return Line B multiplied by 2.519% =": line B at the first printed
rate, rounded half-up to the cent."""

SK428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_C = AmountKind.declare(
    CATALOG, "sk428_dividend_tax_credit_worksheet_line_c", non_negative=True
)
"""Saskatchewan dividend tax credit worksheet, SK428 line 64 (Worksheet SK428, 5008-D), Line C
"Amount A minus amount B": line A less line B."""

SK428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_2 = AmountKind.declare(
    CATALOG, "sk428_dividend_tax_credit_worksheet_line_2", non_negative=True
)
"""Saskatchewan dividend tax credit worksheet, SK428 line 64 (Worksheet SK428, 5008-D), Line 2
"Amount A minus amount B Line C = multiplied by 11% =": line C at the second printed rate, rounded
half-up to the cent."""

SK428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_65 = AmountKind.declare(
    CATALOG, "sk428_minimum_tax_carryover_amount_line_65", non_negative=True
)
"""Saskatchewan minimum tax carryover amount, SK428 line 65 (line 61540) "Amount from line 40427
of your return": the amount from line 40427 of the T1 return, box A of the line, a record total of
the T1's export (`ca/minimum_tax_carryover_line_40427`), 0 for a salary-only caller."""

SK428_MINIMUM_TAX_CARRYOVER_LINE_65 = AmountKind.declare(
    CATALOG, "sk428_minimum_tax_carryover_line_65", non_negative=True
)
"""Saskatchewan minimum tax carryover, SK428 line 65 "Amount from line 40427 of your return
multiplied by 50% =": calculated, box B of the line, the amount from line 40427 multiplied by
50%."""

SK428_MINIMUM_TAX_T691_AMOUNT_LINE_68 = AmountKind.declare(
    CATALOG, "sk428_minimum_tax_t691_amount_line_68"
)
"""Saskatchewan additional tax for minimum tax purposes, SK428 line 68 "Line 68: Form T691: Line 1
minus Line 2 of Part 7 multiplied by 50%": the amount from Form T691, an optional input that a
salary-only caller leaves out. The 50% multiply is a separate step."""

SK428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_73 = AmountKind.declare(
    CATALOG, "sk428_political_contributions_credit_line_73", non_negative=True
)
"""Saskatchewan political contribution tax credit, SK428 line 73 "Line 73: Saskatchewan political
contribution tax credit (use Worksheet SK428) (maximum $650)": the credit from the worksheet, an
optional input that a salary-only caller leaves out; the line 73 step checks it against the printed
maximum."""

SK428_VENTURE_CAPITAL_CREDIT_SASKATCHEWAN_LINE_75 = AmountKind.declare(
    CATALOG, "sk428_venture_capital_credit_saskatchewan_line_75", non_negative=True
)
"""Venture capital tax credit, Saskatchewan corporations, SK428 line 75 "For investments in venture
capital corporations registered in Saskatchewan: Enter your tax credit from T2C Slip (Sask.).
(maximum $875)": the amount as the filer gives it, an optional input; a blank input is read as
blank."""

SK428_VENTURE_CAPITAL_CREDIT_FEDERAL_LINE_76 = AmountKind.declare(
    CATALOG, "sk428_venture_capital_credit_federal_line_76", non_negative=True
)
"""Venture capital tax credit, federally registered corporations, SK428 line 76 "For investments in
venture capital corporations registered federally: Enter your tax credit from T2C Slip (Sask.).
(maximum $875)": the amount as the filer gives it, an optional input; a blank input is read as
blank."""

SK428_LABOUR_SPONSORED_CREDIT_LINE_77 = AmountKind.declare(
    CATALOG, "sk428_labour_sponsored_credit_line_77", non_negative=True
)
"""Labour-sponsored venture capital tax credit before the maximum check, SK428 line 77 (line 63557)
"Line 77 and line 63557: Line 75 plus line 76 (maximum $875)": line 75 plus line 76 (a blank line is
read as 0); the line 77 step checks it against the printed maximum."""

SK428_MINERAL_EXPLORATION_CREDIT_LINE_79 = AmountKind.declare(
    CATALOG, "sk428_mineral_exploration_credit_line_79", non_negative=True
)
"""Saskatchewan mineral exploration tax credit, SK428 line 79 "Line 79: Saskatchewan mineral
exploration tax credit (complete Form T1279)": a caller input, read as blank when left out."""

SK428_CREDITS_SUBTOTAL_LINE_20 = AmountKind.declare(
    CATALOG, "sk428_credits_subtotal_line_20", non_negative=True
)
"""Saskatchewan credits subtotal, SK428 line 20 "Line 20: Add lines 9, 10, 13, and 16 to 19. =": the
sum of the personal amounts claimed, here the basic personal amount alone."""

SK428_CPP_EI_AND_OTHER_LINE_31 = AmountKind.declare(
    CATALOG, "sk428_cpp_ei_and_other_line_31", non_negative=True
)
"""CPP or QPP, EI and other credit amounts, SK428 line 31 "Line 31: Add lines 22 to 30.": the sum of
the CPP or QPP contributions on line 22 and the EI premiums on line 24, the other lines being blank
optional lines."""

SK428_MINIMUM_TAX_ADDITIONAL_LINE_68 = AmountKind.declare(
    CATALOG, "sk428_minimum_tax_additional_line_68"
)
"""Saskatchewan additional tax for minimum tax purposes, SK428 line 68 "Line 68: Form T691: Line 1
minus Line 2 of Part 7 multiplied by 50% =": 50% of the Form T691 amount."""

SK428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "sk428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form SK428 line 3 "Column 1: Line 1 is $53,463 or less / Line 3: 0.00"
(53,463.00; 152,750.00): the printed lower bound of the column of lines 2 to 8 that line 1 falls
in."""

SK428_CREDITS_SUBTOTAL_LINE_32 = AmountKind.declare(
    CATALOG, "sk428_credits_subtotal_line_32", non_negative=True
)
"""Saskatchewan credit amounts subtotal, SK428 line 32 "Line 32: Line 21 plus line 31 =": line 21,
a copy of line 20, plus line 31, read by line 35."""

SK428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "sk428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form SK428 line 5 "Column 1: Line 1 is $53,463 or less / Line 5: Rate 10.5%"
(12.5%; 14.5%): the printed rate of the column of lines 2 to 8 that line 1 falls in."""

SK428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "sk428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, SK428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

SK428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "sk428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column of lines 2 to 8 (the engine's description; the form prints no
title for line 7), Form SK428 line 7 "Column 1: Line 1 is $53,463 or less / Line 7: 0.00" (5,613.62;
18,024.49): the figure printed on line 7 of the column that line 1 falls in."""

SK428_CREDITS_SUBTOTAL_LINE_35 = AmountKind.declare(
    CATALOG, "sk428_credits_subtotal_line_35", non_negative=True
)
"""Saskatchewan credits subtotal, SK428 line 35 "Line 35: Add lines 32 to 34. =": line 32 plus
the pension income amount on line 33 after the line 33 step has checked it, line 34 (the caregiver
amount) not being built."""

SK428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "sk428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, SK428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5 =":
line 4 times the rate of line 5, rounded to the cent."""

SK428_CREDITS_SUBTOTAL_LINE_38 = AmountKind.declare(
    CATALOG, "sk428_credits_subtotal_line_38", non_negative=True
)
"""Saskatchewan credits subtotal, SK428 line 38 "Line 38: Add lines 35 to 37. =": line 35, lines 36
and 37 (the disability amounts) not being built."""

SK428_CREDITS_SUBTOTAL_LINE_42 = AmountKind.declare(
    CATALOG, "sk428_credits_subtotal_line_42", non_negative=True
)
"""Saskatchewan credits subtotal, SK428 line 42 "Line 42: Add lines 38 to 41. =": line 38, lines 39
to 41 (student loan interest, unused tuition and education amounts, amounts transferred from a
spouse) not being built."""

SK428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "sk428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on SK428 line 33 "(maximum $1,000)": the printed maximum,
from the `ca-sk/pension_income_amount_maximum` dataset; the bound line 33 cannot pass."""

SK428_PENSION_INCOME_AMOUNT_CHECKED_LINE_33 = AmountKind.declare(
    CATALOG, "sk428_pension_income_amount_checked_line_33", non_negative=True
)
"""Pension income amount, SK428 line 33 "Line 33 and line 58360: Pension income amount (maximum
$1,000)": the entered amount, passed on unchanged when it is at most the printed maximum, read as 0
when left out; above the maximum it is refused, not capped."""

SK428_TAX_ON_TAXABLE_INCOME_LINE_58 = AmountKind.declare(
    CATALOG, "sk428_tax_on_taxable_income_line_58", non_negative=True
)
"""Saskatchewan tax on taxable income from line 8, SK428 line 58 "Line 58: Saskatchewan tax on
taxable income from line 8 ^" ("Enter the amount from line 8 on line 58 and continue at line 9."):
the amount of line 8, read from the credits form."""

SK428_CREDITS_TOTAL_LINE_51 = AmountKind.declare(
    CATALOG, "sk428_credits_total_line_51", non_negative=True
)
"""Saskatchewan credits total, SK428 line 51 (line 58800) "Line 42 plus line 50 =": the credits
subtotal of line 42 plus the medical expense amount of line 50."""

SK428_TAX_LINE_60 = AmountKind.declare(CATALOG, "sk428_tax_line_60")
"""Saskatchewan tax after line 59, SK428 line 60 "Line 60: Line 58 minus line 59 =": line 58 less
the farm and small business capital gains tax credit of line 59, read as 0 when left out. The form
prints no floor, so the amount is signed."""

SK428_CREDITS_AT_RATE_LINE_53 = AmountKind.declare(
    CATALOG, "sk428_credits_at_rate_line_53", non_negative=True
)
"""Saskatchewan credits at the credit rate, SK428 line 53 (line 58840) "Line 51 multiplied by the
percentage from line 52 = ^": line 51 multiplied by the 10.5% of line 52, rounded half-up to the
cent."""

SK428_TAX_LINE_62 = AmountKind.declare(CATALOG, "sk428_tax_line_62")
"""Saskatchewan tax after line 61, SK428 line 62 "Line 62: Line 60 plus line 61 =": line 60 plus the
tax on split income of line 61, read as 0 when left out. The form prints no floor, so the amount is
signed."""

SK428_CREDITS_FROM_LINE_57_LINE_63 = AmountKind.declare(
    CATALOG, "sk428_credits_from_line_57_line_63", non_negative=True
)
"""Saskatchewan non-refundable tax credits from line 57, SK428 line 63 "Line 63: Saskatchewan
non-refundable tax credits from line 57" (Form SK428, CRA 5008-c-25e): the amount of line 57, read
from the credits form."""

SK428_CREDITS_SUBTOTAL_LINE_66 = AmountKind.declare(
    CATALOG, "sk428_credits_subtotal_line_66", non_negative=True
)
"""Saskatchewan credits subtotal, SK428 line 66 "Line 66: Add lines 63 to 65. =": line 63 (the
credits from line 57) plus line 64 (the dividend tax credit, blank read as 0) plus line 65 (the
minimum tax carryover), rounded to the cent."""

SK428_TAX_AFTER_CREDITS_LINE_67 = AmountKind.declare(
    CATALOG, "sk428_tax_after_credits_line_67", non_negative=True
)
"""Saskatchewan tax after credits, SK428 line 67 "Line 67: Line 62 minus line 66 (if negative, enter
"0") =": line 62 less line 66, never below zero."""

SK428_TAX_LINE_69 = AmountKind.declare(CATALOG, "sk428_tax_line_69")
"""Saskatchewan tax, SK428 line 69 "Line 69: Line 67 plus line 68 = ^": line 67 plus line 68,
rounded to the cent. The form prints no floor, so the amount is signed."""

SK428_TAX_LINE_71 = AmountKind.declare(CATALOG, "sk428_tax_line_71", non_negative=True)
"""Saskatchewan tax after the foreign tax credit, SK428 line 71 "Line 71: Line 69 minus line 70 (if
negative, enter "0") = ^": line 69 less the provincial foreign tax credit of line 70 (blank read as
0), never below zero."""

SK428_TAX_LINE_74 = AmountKind.declare(CATALOG, "sk428_tax_line_74", non_negative=True)
"""Saskatchewan tax after the political contribution tax credit, SK428 line 74 "Line 74: Line 71
minus line 73 (if negative, enter "0") = ^": line 71 less the credit of line 73 (blank read as 0),
never below zero."""

SK428_POLITICAL_CONTRIBUTION_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "sk428_political_contribution_credit_maximum", non_negative=True
)
"""Political contribution tax credit maximum, printed on SK428 line 73 "(maximum $650)": the
printed maximum, from the `ca-sk/political_contribution_credit_maximum` dataset; the bound line 73
cannot pass."""

SK428_POLITICAL_CONTRIBUTIONS_CREDIT_CHECKED_LINE_73 = AmountKind.declare(
    CATALOG, "sk428_political_contributions_credit_checked_line_73", non_negative=True
)
"""Saskatchewan political contribution tax credit, SK428 line 73 "Line 73: Saskatchewan political
contribution tax credit (use Worksheet SK428) (maximum $650)": the entered amount, passed on
unchanged when it is at most the printed maximum, blank when left out; above the maximum it is
refused, not capped."""

SK428_TAX_LINE_78 = AmountKind.declare(CATALOG, "sk428_tax_line_78", non_negative=True)
"""Saskatchewan tax after the labour-sponsored venture capital credit, SK428 line 78 "Line 78: Line
74 minus line 77 (if negative, enter "0") = ^": line 74 less the credit of line 77, never below
zero."""

SK428_LABOUR_SPONSORED_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "sk428_labour_sponsored_credit_maximum", non_negative=True
)
"""Labour-sponsored venture capital tax credit maximum, printed on SK428 line 77 "(maximum $875)":
the printed maximum, from the `ca-sk/labour_sponsored_credit_maximum` dataset; the bound line 77
cannot pass."""

SK428_LABOUR_SPONSORED_CREDIT_CHECKED_LINE_77 = AmountKind.declare(
    CATALOG, "sk428_labour_sponsored_credit_checked_line_77", non_negative=True
)
"""Labour-sponsored venture capital tax credit, SK428 line 77 "Line 77 and line 63557: Line 75 plus
line 76 (maximum $875)": line 75 plus line 76, passed on unchanged when it is at most the printed
maximum; above the maximum it is refused, not capped."""

SK428_TAX_LINE_80 = AmountKind.declare(CATALOG, "sk428_tax_line_80", non_negative=True)
"""Saskatchewan tax after the mineral exploration tax credit, SK428 line 80 "Line 80: Line 78
minus line 79 (if negative, enter "0") = ^": line 78 less the credit of line 79 (blank read as 0),
never below zero."""

AVERAGE_INCOME_TAX_RATE = AmountKind.declare(CATALOG, "average_income_tax_rate", non_negative=True)
"""Average income tax rate, the Saskatchewan return summary's own figure (no form prints it): T1
line 43500 "Total payable" (for the take-home filer, line 143 plus line 147: the federal and the
Saskatchewan income tax) divided by the salary (`ca/return_employment_income`), as a fraction, so
0.1598 is 15.98%. CPP and EI are not income tax and are not in it. It is 0 when the salary is 0."""

SASKATCHEWAN_BRACKET_RATE_RETURN = AmountKind.declare(
    CATALOG, "saskatchewan_bracket_rate_return", non_negative=True
)
"""Saskatchewan bracket rate, SK428 line 5 "Line 5: Rate": the printed rate of the column that
line 1 falls in (10.5%, 12.5% or 14.5%), read from SK428 into the return summary."""

SASKATCHEWAN_TAX_AFTER_CREDITS_RETURN = AmountKind.declare(
    CATALOG, "saskatchewan_tax_after_credits_return", non_negative=True
)
"""Saskatchewan tax after the credits, SK428 line 67 "Line 67: Line 62 minus line 66 (if negative,
enter "0") =": the one amount of SK428's export totalled into the return summary's own artifact,
the base of the Saskatchewan rate gate."""

SASKATCHEWAN_RATE_GATE = AmountKind.declare(CATALOG, "saskatchewan_rate_gate", non_negative=True)
"""Saskatchewan rate gate: 0 where the Saskatchewan tax after the credits (SK428 line 67) is 0.00
and 1 where it is at least one cent, from the `ca-sk/marginal_rate_gate` dataset. A plain figure,
not printed on the form."""

SASKATCHEWAN_MARGINAL_RATE = AmountKind.declare(
    CATALOG, "saskatchewan_marginal_rate", non_negative=True
)
"""Saskatchewan marginal rate: the bracket rate (SK428 line 5) where the Saskatchewan tax after the
credits (SK428 line 67) is above zero, and 0 where it is not: the rate a further dollar of income
is taxed at in Saskatchewan, on the return summary. Saskatchewan has no tax reduction. Not printed
on the form."""

MARGINAL_TAX_RATE = AmountKind.declare(CATALOG, "marginal_tax_rate", non_negative=True)
"""Marginal tax rate: the income tax rate on a further dollar of salary, the sum of the federal
marginal rate and the Saskatchewan marginal rate (SK428 and T4127 print no surtax or health
premium), on the return summary. Not printed on the form."""
