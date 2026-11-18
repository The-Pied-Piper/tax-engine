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

SK428_MEDICAL_EXPENSES_LINE_50 = AmountKind.declare(
    CATALOG, "sk428_medical_expenses_line_50", non_negative=True
)
"""Medical expenses, SK428 line 50 (line 58769) "Line 48 plus line 49 =": line 48 plus line 49, an
optional input; a blank is read as 0 by the line 51 step."""

SK428_DONATIONS_CREDIT_LINE_56 = AmountKind.declare(
    CATALOG, "sk428_donations_credit_line_56", non_negative=True
)
"""Donations and gifts credit, SK428 line 56 (58969) "Line 56 and 58969: Line 54 plus line
55 =": a caller input, read as blank when left out; line 57 reads it."""

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
Saskatchewan dividend tax credit (use Worksheet SK428)": a caller input, read as blank when left
out."""

SK428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_65 = AmountKind.declare(
    CATALOG, "sk428_minimum_tax_carryover_amount_line_65", non_negative=True
)
"""Saskatchewan minimum tax carryover amount, SK428 line 65 (line 61540) "Amount from line 40427
of your return": the amount from line 40427 of the T1 return, an optional input, box A of the line,
read as blank when left out."""

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
optional input that a salary-only caller leaves out."""

SK428_LABOUR_SPONSORED_CREDIT_LINE_77 = AmountKind.declare(
    CATALOG, "sk428_labour_sponsored_credit_line_77", non_negative=True
)
"""Labour-sponsored venture capital tax credit, SK428 line 77 (line 63557) "Line 77 and line
63557: Line 75 plus line 76 (maximum $875)": a caller input, read as blank when left out."""

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
subtotal of line 42 plus the medical expense amount of line 50, read as 0 when blank, lines 43 to
49 (the medical expense working) not being built."""

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
