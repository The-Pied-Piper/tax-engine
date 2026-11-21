"""The Manitoba artifact catalog: Manitoba's own kinds, named from the Manitoba forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_mb import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

MB428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "mb428_tax_on_taxable_income_line_8", non_negative=True
)
"""Manitoba tax on taxable income, MB428 line 8 "Line 6 plus line 7 Manitoba tax on taxable income
=": line 6 plus line 7 of the column that line 1 falls in, read by line 58 on the tax form."""

MB428_BASIC_PERSONAL_AMOUNT_LINE_9 = AmountKind.declare(
    CATALOG, "mb428_basic_personal_amount_line_9", non_negative=True
)
"""Basic personal amount, MB428 line 9 and line 58040 "Basic personal amount (use Worksheet MB428)":
the amount of Worksheet MB428 line 9, which says to enter it on line 58040."""

MB428_CREDITS_SUBTOTAL_LINE_18 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_18", non_negative=True
)
"""Credits subtotal, MB428 line 18 "Line 18: Add lines 9, 10, 13, 16, and 17. = ^": only the basic
personal amount, line 9, is summed here, because a salary-only single filer has no age, spouse,
eligible dependant or infirm dependant amount."""

MB428_CPP_CONTRIBUTIONS_LINE_19 = AmountKind.declare(
    CATALOG, "mb428_cpp_contributions_line_19", non_negative=True
)
"""CPP or QPP contributions, MB428 line 19 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

MB428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "mb428_pension_income_amount", non_negative=True
)
"""Pension income amount, MB428 line 31 "Line 31 and line 58360: Pension income amount (maximum
$1,000)": the amount the filer claims, a caller input that is read as blank when left out; the
line 31 step checks it against the printed maximum."""

MB428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "mb428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on MB428 line 31 "(maximum $1,000)": the printed
maximum, from the `ca-mb/pension_income_amount_maximum` dataset; the bound line 31 cannot pass."""

MB428_PENSION_INCOME_AMOUNT_LINE_31 = AmountKind.declare(
    CATALOG, "mb428_pension_income_amount_line_31", non_negative=True
)
"""Pension income amount, MB428 line 31 "Line 31 and line 58360: Pension income amount (maximum
$1,000)": the entered amount, passed on unchanged when it is at most the printed maximum, blank when
left out; above the maximum it is refused, not capped."""

MB428_MEDICAL_EXPENSES_LINE_43 = AmountKind.declare(
    CATALOG, "mb428_medical_expenses_line_43", non_negative=True
)
"""Medical expenses, MB428 line 43 (line 58689) "Amount from line 33099 of your return": the amount
as the filer gives it, an optional input; a blank input is read as blank."""

MB428_NET_INCOME_LINE_44 = AmountKind.declare(
    CATALOG, "mb428_net_income_line_44", non_negative=True
)
"""Net income, MB428 line 44 "Amount from line 23600 of your return": the T1 net income, read from
the T1 taxable income form."""

MB428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_46 = AmountKind.declare(
    CATALOG, "mb428_medical_expenses_rate_amount_line_46", non_negative=True
)
"""Medical expenses threshold, MB428 line 46 "Line 44 multiplied by the percentage from line 45 =":
line 44 times the 3% of line 45."""

MB428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_47 = AmountKind.declare(
    CATALOG, "mb428_medical_expenses_limited_amount_line_47", non_negative=True
)
"""Medical expenses threshold, limited, MB428 line 47 "Enter whichever is less: $1,728 or the amount
from line 46.": the lesser of the printed ceiling and line 46."""

MB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48 = AmountKind.declare(
    CATALOG, "mb428_medical_expenses_over_limit_line_48", non_negative=True
)
"""Medical expenses over the limit, MB428 line 48 "Line 43 minus line 47 (if negative, enter "0")
=": line 43 minus line 47, never below 0; a blank line 43 is read as 0."""

MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49 = AmountKind.declare(
    CATALOG, "mb428_other_dependants_medical_expenses_line_49", non_negative=True
)
"""Allowable amount of medical expenses for other dependants, MB428 line 49 (line 58729) "(use
Worksheet MB428)": the amount as the filer gives it, an optional input; a blank input is read as
blank."""

MB428_MEDICAL_EXPENSES_LINE_50 = AmountKind.declare(
    CATALOG, "mb428_medical_expenses_line_50", non_negative=True
)
"""Medical expenses, MB428 line 50 (line 58769) "Line 48 plus line 49 =": line 48 plus line 49
(a blank line 49 is read as 0), read by line 51."""

MB428_DONATIONS_AMOUNT_LINE_54 = AmountKind.declare(
    CATALOG, "mb428_donations_amount_line_54", non_negative=True
)
"""Donations amount, MB428 line 54 box A "Amount from line 13 of your federal Schedule 9": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

MB428_DONATIONS_CREDIT_AT_RATE_LINE_54 = AmountKind.declare(
    CATALOG, "mb428_donations_credit_at_rate_line_54", non_negative=True
)
"""Donations credit at 10.8%, MB428 line 54 box B "Amount from line 13 of your federal Schedule 9
multiplied by 10.8% =": the Schedule 9 amount times 10.8%; a blank amount is read as 0."""

MB428_DONATIONS_AMOUNT_LINE_55 = AmountKind.declare(
    CATALOG, "mb428_donations_amount_line_55", non_negative=True
)
"""Donations amount, MB428 line 55 box A "Amount from line 14 of your federal Schedule 9": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

MB428_DONATIONS_CREDIT_AT_RATE_LINE_55 = AmountKind.declare(
    CATALOG, "mb428_donations_credit_at_rate_line_55", non_negative=True
)
"""Donations credit at 17.4%, MB428 line 55 box B "Amount from line 14 of your federal Schedule 9
multiplied by 17.4% =": the Schedule 9 amount times 17.4%; a blank amount is read as 0."""

MB428_DONATIONS_CREDIT_LINE_56 = AmountKind.declare(
    CATALOG, "mb428_donations_credit_line_56", non_negative=True
)
"""Donations and gifts credit, MB428 line 56 (line 58969) "Line 56 and line 58969: Line 54 plus line
55 =": line 54 plus line 55, read by line 57."""

MB428_NON_REFUNDABLE_CREDITS_LINE_57 = AmountKind.declare(
    CATALOG, "mb428_non_refundable_credits_line_57", non_negative=True
)
"""Manitoba non-refundable tax credits, MB428 line 57 "Line 57 and line 61500: Line 53 plus line 56
Enter this amount on line 61. Manitoba non-refundable tax credits =": line 53 plus line 56, read by
line 61 on the tax form."""

MB428_MANITOBA_TAX_ON_TAXABLE_INCOME_LINE_58 = AmountKind.declare(
    CATALOG, "mb428_manitoba_tax_on_taxable_income_line_58", non_negative=True
)
"""Manitoba tax on taxable income, MB428 line 58 "Line 58: Manitoba tax on taxable income from
line 8": line 8 of the Manitoba tax form's Part A, read across the forms."""

MB428_TAX_ON_SPLIT_INCOME_LINE_59 = AmountKind.declare(
    CATALOG, "mb428_tax_on_split_income_line_59", non_negative=True
)
"""Manitoba tax on split income, MB428 line 59 (line 61510) "Line 59 and line 61510: Manitoba tax on
split income (complete Form T1206)": a caller input, read as blank when left out; line 60 reads
it."""

MB428_TAX_BEFORE_CREDITS_LINE_60 = AmountKind.declare(
    CATALOG, "mb428_tax_before_credits_line_60", non_negative=True
)
"""MB428 line 60 "Line 60: Line 58 plus line 59 =": the sum of line 58 and line 59, where a blank
line 59 is read as 0."""

MB428_NON_REFUNDABLE_CREDITS_LINE_61 = AmountKind.declare(
    CATALOG, "mb428_non_refundable_credits_line_61", non_negative=True
)
"""Manitoba non-refundable tax credits, MB428 line 61 "Line 61: Manitoba non-refundable tax credits
from line 57 ^": line 57 of the credits form, read across the forms."""

MB428_MINIMUM_TAX_CARRYOVER_LINE_63 = AmountKind.declare(
    CATALOG, "mb428_minimum_tax_carryover_line_63", non_negative=True
)
"""Minimum tax carryover amount, MB428 line 63 (line 40427) "Line 63 and line 61540: Amount from
line 40427 of your return": a caller input, read as blank when left out; the carryover credit step
reads it."""

MB428_MINIMUM_TAX_CARRYOVER_CREDIT_LINE_63 = AmountKind.declare(
    CATALOG, "mb428_minimum_tax_carryover_credit_line_63", non_negative=True
)
"""Manitoba minimum tax carryover, MB428 line 63 and line 61540 "Amount from line 40427 of your
return multiplied by 50% =": calculated, the amount from line 40427 multiplied by 50%."""

MB428_CREDITS_TOTAL_LINE_64 = AmountKind.declare(
    CATALOG, "mb428_credits_total_line_64", non_negative=True
)
"""Total credits, MB428 line 64 "Line 64: Add lines 61 to 63. =": calculated, lines 61 to 63 added
(line 62 read as 0 when left blank)."""

MB428_TAX_AFTER_CREDITS_LINE_65 = AmountKind.declare(
    CATALOG, "mb428_tax_after_credits_line_65", non_negative=True
)
"""Manitoba tax after credits, MB428 line 65 "Line 65: Line 60 minus line 64 (if negative, enter
"0") =": calculated, line 60 less line 64, not below 0."""

MB428_ADDITIONAL_TAX_MINIMUM_TAX_LINE_66 = AmountKind.declare(
    CATALOG, "mb428_additional_tax_minimum_tax_line_66", non_negative=True
)
"""Manitoba additional tax for minimum tax purposes, MB428 line 66 "Line 66: Form T691: line 1 minus
line 2 of Part 7 multiplied by 50% =": calculated, the Form T691 amount multiplied by 50%."""

MB428_TAX_LINE_67 = AmountKind.declare(CATALOG, "mb428_tax_line_67", non_negative=True)
"""Manitoba tax, MB428 line 67 "Line 67: Line 65 plus line 66 =": calculated, line 65 plus line
66."""

MB428_TAX_LINE_70 = AmountKind.declare(CATALOG, "mb428_tax_line_70", non_negative=True)
"""Manitoba tax, MB428 line 70 "Line 70: Line 67 minus line 69 (if negative, enter "0") =":
calculated, line 67 less line 69 (line 69 read as 0 when blank), not below 0."""

MB428_TAX_LINE_72 = AmountKind.declare(CATALOG, "mb428_tax_line_72", non_negative=True)
"""Manitoba tax, MB428 line 72 "Line 72: Line 70 minus line 71 (if negative, enter "0") =":
calculated, line 70 less line 71 (line 71 read as 0 when blank), not below 0."""

MB428_TAX_LINE_74 = AmountKind.declare(CATALOG, "mb428_tax_line_74", non_negative=True)
"""Manitoba tax, MB428 line 74 "Line 74: Line 72 minus line 73 (if negative, enter "0") =":
calculated, line 72 less line 73 (line 73 read as 0 when blank), not below 0."""

MB428_TAX_LINE_76 = AmountKind.declare(CATALOG, "mb428_tax_line_76", non_negative=True)
"""Manitoba tax, MB428 line 76 "Line 76: Line 74 minus line 75 (if negative, enter "0") =":
calculated, line 74 less line 75 (line 75 read as 0 when blank), not below 0."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_9 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_9", non_negative=True
)
"""Manitoba basic personal amount, Worksheet MB428 line 9 "Line 9: Line 1 minus line 8 (if negative,
enter "0") Enter this amount on line 58040 of your Form MB428.": the basic personal amount entered
on line 58040 of Form MB428."""

MB479_MANITOBA_CREDITS_LINE_81 = AmountKind.declare(
    CATALOG, "mb479_manitoba_credits_line_81", non_negative=True
)
"""Manitoba credits, MB479 line 81 "Add lines 78 to 80. Enter this amount on line 47900 of your
return.": the Manitoba credits, entered on T1 line 47900."""

MB428_DIVIDEND_TAX_CREDIT_LINE_62 = AmountKind.declare(
    CATALOG, "mb428_dividend_tax_credit_line_62", non_negative=True
)
"""Manitoba dividend tax credit, MB428 line 62 (line 61520) "Line 62 and line 61520: Manitoba
dividend tax credit (use Worksheet MB428)": a caller input, read as blank when left out."""

MB428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_69 = AmountKind.declare(
    CATALOG, "mb428_political_contribution_tax_credit_line_69", non_negative=True
)
"""Manitoba political contribution tax credit, MB428 line 69 "Line 69: Manitoba political
contribution tax credit (use Worksheet MB428) (maximum $1,000)": a caller input, read as blank
when left out."""

MB428_LABOUR_SPONSORED_FUNDS_CREDIT_LINE_71 = AmountKind.declare(
    CATALOG, "mb428_labour_sponsored_funds_credit_line_71", non_negative=True
)
"""Labour-sponsored funds tax credit, MB428 line 71 (line 60800) "Enter your labour-sponsored funds
tax credit from Slip T2C (MAN.).": a caller input, read as blank when left out."""

MB428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_73 = AmountKind.declare(
    CATALOG, "mb428_provincial_foreign_tax_credit_line_73", non_negative=True
)
"""Provincial foreign tax credit, MB428 line 73 "Line 73: Provincial foreign tax credit (complete
Form T2036)": a caller input, read as blank when left out."""

MB428_COMMUNITY_ENTERPRISE_DEVELOPMENT_TAX_CREDIT_LINE_75 = AmountKind.declare(
    CATALOG, "mb428_community_enterprise_development_tax_credit_line_75", non_negative=True
)
"""Manitoba community enterprise development tax credit, MB428 line 75 "Line 75 and line 60830:
Manitoba community enterprise development tax credit (complete Form T1256)": a caller input, read
as blank when left out."""

MB428_VENTURE_CAPITAL_CREDIT = AmountKind.declare(
    CATALOG, "mb428_venture_capital_credit", non_negative=True
)
"""Manitoba small business venture capital tax credit for individuals, MB428 line 77 "Line 77 and
line 60850: Manitoba small business venture capital tax credit for individuals (complete Form
T1256-1) (maximum $120,000)": the amount the filer claims, a caller input that is read as blank when
left out; the line 77 step checks it against the printed maximum."""

MB428_VENTURE_CAPITAL_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "mb428_venture_capital_credit_maximum", non_negative=True
)
"""Venture capital credit maximum, printed on MB428 line 77 "(maximum $120,000)": the printed
maximum, from the `ca-mb/venture_capital_credit_maximum` dataset; the bound line 77 cannot pass."""

MB428_VENTURE_CAPITAL_CREDIT_LINE_77 = AmountKind.declare(
    CATALOG, "mb428_venture_capital_credit_line_77", non_negative=True
)
"""Manitoba small business venture capital tax credit for individuals, MB428 line 77 "Line 77 and
line 60850: Manitoba small business venture capital tax credit for individuals (complete Form
T1256-1) (maximum $120,000)": the entered amount, passed on unchanged when it is at most the printed
maximum, blank when left out; above the maximum it is refused, not capped."""

MB428_TAX_LINE_78 = AmountKind.declare(CATALOG, "mb428_tax_line_78", non_negative=True)
"""Manitoba tax, MB428 line 78 "Line 78: Line 76 minus line 77 (if negative, enter "0") =":
calculated, line 76 less line 77 (line 77 read as 0 when blank), not below 0."""

MB428_EMPLOYEE_SHARE_PURCHASE_TAX_CREDIT_LINE_79 = AmountKind.declare(
    CATALOG, "mb428_employee_share_purchase_tax_credit_line_79", non_negative=True
)
"""Manitoba employee share purchase tax credit, MB428 line 79 "Line 79 and line 60860: Manitoba
employee share purchase tax credit (complete Form T1256-2)": a caller input, read as blank when left
out."""

MB428_TAX_LINE_80 = AmountKind.declare(CATALOG, "mb428_tax_line_80", non_negative=True)
"""Manitoba tax, MB428 line 80 "Line 80: Line 78 minus line 79 (if negative, enter "0") =":
calculated, line 78 less line 79 (line 79 read as 0 when blank), not below 0."""

MB428_MINERAL_EXPLORATION_TAX_CREDIT_LINE_81 = AmountKind.declare(
    CATALOG, "mb428_mineral_exploration_tax_credit_line_81", non_negative=True
)
"""Manitoba mineral exploration tax credit, MB428 line 81 "Line 81 and line 60920: Manitoba mineral
exploration tax credit (complete Form T1241)": a caller input, read as blank when left out."""

MB428_MANITOBA_TAX_LINE_82 = AmountKind.declare(
    CATALOG, "mb428_manitoba_tax_line_82", non_negative=True
)
"""Manitoba tax, MB428 line 82 "Enter this amount on line 42800 of your return.": the Manitoba
tax, entered on T1 line 42800."""

MB428_A_FAMILY_TAX_BENEFIT_LINE_12 = AmountKind.declare(
    CATALOG, "mb428_a_family_tax_benefit_line_12", non_negative=True
)
"""Family tax benefit, Schedule MB428-A line 12 "Line 12: Line 10 minus line 11 (if negative, enter
"0") Enter this amount on line 61470 of your Form MB428.": the family tax benefit entered on line
61470 of Form MB428."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_3 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_3", non_negative=True
)
"""Income threshold, Worksheet MB428 line 3 "Line 3: Income threshold 200,000.00": the income
threshold of the basic personal amount section."""

WORKSHEET_MB428_LINE_2 = AmountKind.declare(CATALOG, "worksheet_mb428_line_2", non_negative=True)
"""Net income, Worksheet MB428 line 2 "Line 2: Amount from line 23600 of your return": the T1 net
income, line 23600 after its floor."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_1 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_1", non_negative=True
)
"""Base amount, Worksheet MB428 line 1 "Line 1: Base amount 15,780.00": the base amount of the
basic personal amount section."""

MB428_EI_PREMIUMS_LINE_21 = AmountKind.declare(
    CATALOG, "mb428_ei_premiums_line_21", non_negative=True
)
"""EI premiums credit amount, MB428 line 21 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_5 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_5", non_negative=True
)
"""Income threshold, Worksheet MB428 line 5 "Line 5: Income threshold 200,000.00": the income
threshold of the basic personal amount section."""

WORKSHEET_MB428_LINE_4 = AmountKind.declare(CATALOG, "worksheet_mb428_line_4", non_negative=True)
"""Net income over the threshold, Worksheet MB428 line 4 "Line 4: Line 2 minus line 3 (if negative,
enter "0")": line 2 minus line 3, not below zero."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_7 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_7", non_negative=True
)
"""Base amount, Worksheet MB428 line 7 "Line 7: Base amount 15,780.00": the base amount of the
basic personal amount section."""

MB428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "mb428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form MB428 Line 1 "Enter your taxable income from line 26000 of your return":
the T1 taxable income, read directly by lines 3 and 4."""

WORKSHEET_MB428_LINE_6 = AmountKind.declare(CATALOG, "worksheet_mb428_line_6", non_negative=True)
"""Net income over the threshold as a share of the threshold, Worksheet MB428 line 6 "Line 6: Line 4
divided by line 5 = ^": the ratio of line 4 to line 5, a fraction (0.25 is a quarter), not money."""

MB428_A_BASIC_AMOUNT_LINE_1 = AmountKind.declare(
    CATALOG, "mb428_a_basic_amount_line_1", non_negative=True
)
"""Basic amount, Schedule MB428-A line 1 "Line 1: Basic amount 2,065.00": the basic amount of the
family tax benefit."""

MB428_A_NET_INCOME_LINE_11 = AmountKind.declare(
    CATALOG, "mb428_a_net_income_line_11", non_negative=True
)
"""Net income, Schedule MB428-A (CRA 5007-A) line 11 "Line 11: Net income from line 23600 of your
return": the first box of the line, the net income read from the T1, before the multiplication
by 9%."""

MB479_NET_INCOME_LINE_1 = AmountKind.declare(CATALOG, "mb479_net_income_line_1", non_negative=False)
"""Net income, MB479 line 1 "Line 1: Net income from line 23600 of the return (or the amount you
would have entered if the instructions on line 23600 said "if negative, show in brackets")": the
net income of the T1 return before its floor, read from the signed T1 net income export
(`ca/net_income_signed`, not the floored `ca/net_income`). Column 1 only. The form shows a negative
net income in brackets, so the kind is signed."""

MB479_UCCB_RDSP_REPAYMENTS_LINE_2 = AmountKind.declare(
    CATALOG, "mb479_uccb_rdsp_repayments_line_2", non_negative=True
)
"""UCCB and RDSP repayments, MB479 line 2 "Total of the universal child care benefit (UCCB)
repayment (line 21300 of the return) and the registered disability savings plan (RDSP) income
repayment (included on line 23200 of the return)": the total of the two repayments, the sum of
the two T1 lines (read from the T1 form's exports), column 1 (you) only."""

MB479_UCCB_REPAYMENT_LINE_21300 = AmountKind.declare(
    CATALOG, "mb479_uccb_repayment_line_21300", non_negative=True
)
"""MB479 line 2, the part from T1 line 21300 (UCCB repayment): the T1's line, read as the form's
export."""

MB479_RDSP_INCOME_REPAYMENT_LINE_23200 = AmountKind.declare(
    CATALOG, "mb479_rdsp_income_repayment_line_23200", non_negative=True
)
"""MB479 line 2, the RDSP income repayment included on T1 line 23200: the T1's line, read as the
form's export."""

MB479_UCCB_INCOME_LINE_11700 = AmountKind.declare(
    CATALOG, "mb479_uccb_income_line_11700", non_negative=True
)
"""MB479 line 4, the part from T1 line 11700 (UCCB income): the T1's line, read as the form's
export."""

MB479_RDSP_INCOME_LINE_12500 = AmountKind.declare(
    CATALOG, "mb479_rdsp_income_line_12500", non_negative=True
)
"""MB479 line 4, the part from T1 line 12500 (RDSP income): the T1's line, read as the form's
export."""

WORKSHEET_MB428_LINE_8 = AmountKind.declare(CATALOG, "worksheet_mb428_line_8", non_negative=True)
"""Worksheet MB428 line 8 "Line 8: Line 6 multiplied by line 7 = ^": line 6 times line 7, money."""

MB428_A_LINE_10 = AmountKind.declare(CATALOG, "mb428_a_line_10", non_negative=True)
"""Sum of lines 1 to 9, Schedule MB428-A line 10 "Line 10: Add lines 1 to 9.": the basic amount of
the family tax benefit, the only line of the block that is built."""

MB428_A_LINE_11 = AmountKind.declare(CATALOG, "mb428_a_line_11", non_negative=True)
"""Net income multiplied by 9%, Schedule MB428-A (CRA 5007-A) line 11 "Line 11: Net income from line
23600 of your return multiplied by 9%": the net income of the first box times the printed rate."""

MB479_UCCB_RDSP_INCOME_LINE_4 = AmountKind.declare(
    CATALOG, "mb479_uccb_rdsp_income_line_4", non_negative=True
)
"""UCCB and RDSP income, MB479 line 4 "Total of the UCCB income (line 11700 of the return) and RDSP
income (line 12500 of the return)": the total of the two incomes, a caller input that is read as
blank when left out, column 1 (you) only."""

MB479_FAMILY_INCOME_COLUMN_2_LINE_5 = AmountKind.declare(
    CATALOG, "mb479_family_income_column_2_line_5", non_negative=True
)
"""Family income of your spouse or common-law partner, MB479 line 5 "Line 3 minus line 4 (if
negative, enter "0")": column 2 (your spouse or common-law partner), taken as one figure because the
spouse's own lines 1 to 4 are not modelled, a caller input that is read as blank when left out."""

MB479_FAMILY_INCOME_BEFORE_BENEFITS_LINE_3 = AmountKind.declare(
    CATALOG, "mb479_family_income_before_benefits_line_3", non_negative=False
)
"""Family income before benefits, MB479 line 3 "Line 3: Line 1 plus line 2": the net income of
line 1 plus the UCCB and RDSP repayments of line 2, column 1 (you) only. Line 1 can be negative, so
the kind is signed."""

MB479_BASIC_CREDIT_LINE_7 = AmountKind.declare(
    CATALOG, "mb479_basic_credit_line_7", non_negative=True
)
"""Basic credit, MB479 line 7 "Line 7: Basic credit 195.00": the basic credit of the Manitoba
personal tax credits."""

MB479_PRIMARY_CAREGIVER_CREDIT_LINE_59 = AmountKind.declare(
    CATALOG, "mb479_primary_caregiver_credit_line_59", non_negative=True
)
"""Primary caregiver tax credit, MB479 line 59 "Line 59 and line 61260: Primary caregiver tax
credit": a caller input that is read as blank when left out."""

MB479_ODOUR_CONTROL_CREDIT_LINE_65 = AmountKind.declare(
    CATALOG, "mb479_odour_control_credit_line_65", non_negative=True
)
"""Unused odour-control tax credit, MB479 line 65 "Line 65 and line 61340: Enter your unused
odour-control tax credit from your 2024 notice of assessment or reassessment.": a caller input that
is read as blank when left out."""

MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_LINE_77 = AmountKind.declare(
    CATALOG, "mb479_employee_share_purchase_credit_line_77", non_negative=True
)
"""Employee share purchase tax credit, MB479 line 77 "Line 77 and line 61490: Enter your Manitoba
employee share purchase tax credit from line 6 of Form T1256-2. (maximum $27,000)": a caller input
that is read as blank when left out; the line 77 step checks it against the printed maximum."""

MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "mb479_employee_share_purchase_credit_maximum", non_negative=True
)
"""Employee share purchase tax credit maximum, printed on MB479 line 77 "(maximum $27,000)": the
printed maximum, from the `ca-mb/employee_share_purchase_credit_maximum` dataset; the bound line 77
cannot pass."""

MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_CHECKED_LINE_77 = AmountKind.declare(
    CATALOG, "mb479_employee_share_purchase_credit_checked_line_77", non_negative=True
)
"""Employee share purchase tax credit, MB479 line 77 "Line 77 and line 61490: Enter your Manitoba
employee share purchase tax credit from line 6 of Form T1256-2. (maximum $27,000)": the entered
amount, passed on unchanged when it is at most the printed maximum, blank when left out; above the
maximum it is refused, not capped."""

MB428_CPP_EI_AND_OTHER_LINE_28 = AmountKind.declare(
    CATALOG, "mb428_cpp_ei_and_other_line_28", non_negative=True
)
"""CPP, EI and other credit amounts subtotal, MB428 line 28 "Line 28: Add lines 19 to 27. = ^": the
sum of lines 19 and 21. Lines 20 and 22 to 27 are not built: a salary-only filer has none."""

MB428_FAMILY_TAX_BENEFIT_LINE_41 = AmountKind.declare(
    CATALOG, "mb428_family_tax_benefit_line_41", non_negative=True
)
"""Family tax benefit, MB428 line 41 and line 61470 "Line 41 and line 61470: Family tax benefit
(attach Schedule MB428-A)": the amount of Schedule MB428-A line 12, which says to enter it on line
61470 of Form MB428."""

MB428_CREDITS_SUBTOTAL_LINE_29 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_29", non_negative=True
)
"""Credits subtotal, MB428 line 29 "Line 29: Line 18 plus line 28.": the sum of line 18 and line
28."""

MB428_CREDITS_SUBTOTAL_LINE_33 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_33", non_negative=True
)
"""Credits subtotal, MB428 line 33 "Line 33: Add lines 30 to 32. = ^": the sum of line 30 (a copy of
line 29) and the line 31 pension income amount; line 32, the caregiver amount, is not built."""

MB428_CREDITS_SUBTOTAL_LINE_36 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_36", non_negative=True
)
"""Credits subtotal, MB428 line 36 "Line 36: Add lines 33 to 35. = ^": lines 34 and 35, the
disability amounts, are not built, so the sum reads line 33 alone."""

MB428_CREDITS_SUBTOTAL_LINE_42 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_42", non_negative=True
)
"""Credits subtotal, MB428 line 42 "Line 42: Add lines 36 to 41. = ^": the sum of line 36 and the
line 41 family tax benefit; lines 37 to 40, the optional student loan, tuition and transfer amounts,
are left blank and not built."""

MB428_CREDITS_TOTAL_LINE_51 = AmountKind.declare(
    CATALOG, "mb428_credits_total_line_51", non_negative=True
)
"""MB428 line 51 "Line 51 and line 58800: Line 42 plus line 50 = ^": the sum of line 42 and the
line 50 medical expense amount; lines 43 to 49, the medical expense working, are not built."""

MB428_CREDITS_AT_RATE_LINE_53 = AmountKind.declare(
    CATALOG, "mb428_credits_at_rate_line_53", non_negative=True
)
"""MB428 line 53 (line 58840) "Line 51 multiplied by the percentage from line 52 = ^": line 51
multiplied by the 10.8% of line 52, rounded half-up to the cent."""

MB479_FAMILY_INCOME_COLUMN_1_LINE_5 = AmountKind.declare(
    CATALOG, "mb479_family_income_column_1_line_5", non_negative=True
)
"""Family income, MB479 line 5 "Line 3 minus line 4 (if negative, enter "0")": line 3 less the UCCB
and RDSP income of line 4, floored at 0, column 1 (you) only."""

MB428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "mb428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, MB428 line 3 "Line 3: 0.00" (47,000.00; 100,000.00): the printed lower
bound of the column of lines 2 to 8 that line 1 falls in."""

MB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "mb428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, MB428 line 4 "Line 4: Line 2 minus line 3 (can not be
negative) =": line 1 minus line 3, not below zero."""

MB428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "mb428_bracket_rate_line_5", non_negative=True
)
"""Bracket column rate, MB428 line 5 (each column prints "Line 5: Rate" with 10.8%, 12.75% or
17.4%): the printed rate of the column of lines 2 to 8 that line 1 falls in."""

MB428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "mb428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the taxable income over the lower bound, MB428 line 6 "Line 6: Line 4 multiplied by the
percentage from line 5 =": line 4 times the line 5 rate, rounded half-up to the cent."""

MB479_AGE_CREDIT_LINE_8 = AmountKind.declare(CATALOG, "mb479_age_credit_line_8", non_negative=True)
"""Age credit for self, MB479 line 8 "Age credit for self (if you were born in 1960 or earlier)
Claim $113": the credit of the first box, a caller input that is read as blank when left out."""

MB479_SPOUSE_CREDITS_LINE_12 = AmountKind.declare(
    CATALOG, "mb479_spouse_credits_line_12", non_negative=True
)
"""Spouse or common-law partner credits, MB479 line 12 "Line 12 and line 60900: Add lines 9 to 11.":
the printed sum of lines 9 to 11, taken as one figure because those lines are not modelled, a caller
input that is read as blank when left out."""

MB479_ELIGIBLE_DEPENDANT_CREDIT_LINE_13 = AmountKind.declare(
    CATALOG, "mb479_eligible_dependant_credit_line_13", non_negative=True
)
"""Eligible dependant credit, MB479 line 13 "Credit for an eligible dependant claimed on line 58160
of your Form MB428 Claim $195": the credit of the box, a caller input that is read as blank when
left out."""

MB479_DISABILITY_CLAIMS_NUMBER_LINE_14 = AmountKind.declare(
    CATALOG, "mb479_disability_claims_number_line_14", non_negative=True
)
"""Number of disability claims, MB479 line 14 box A "Number of disability claims Line 60950": the
number as the filer gives it, an optional input; left out, it is 0."""

MB479_DISABILITY_CREDIT_AMOUNT_LINE_14 = AmountKind.declare(
    CATALOG, "disability_credit_amount_line_14", non_negative=True
)
"""Amount for each of the disability claims, MB479 line 14 "multiplied by $113 =": the printed $113,
from the `ca-mb/disability_credit_amount_line_14` dataset."""

MB479_DISABILITY_CREDIT_LINE_14 = AmountKind.declare(
    CATALOG, "mb479_disability_credit_line_14", non_negative=True
)
"""Disability credit, MB479 line 14 box B "Number of disability claims Line 60950 multiplied by $113
=": the number in box A times $113, rounded to the cent; line 17 adds it."""

MB479_DISABLED_DEPENDANTS_NUMBER_LINE_15 = AmountKind.declare(
    CATALOG, "mb479_disabled_dependants_number_line_15", non_negative=True
)
"""Number of disabled dependants, MB479 line 15 box A "Number of disabled dependants Line 60970":
the number as the filer gives it, an optional input; left out, it is 0."""

MB479_DISABLED_DEPENDANTS_CREDIT_AMOUNT_LINE_15 = AmountKind.declare(
    CATALOG, "disabled_dependants_credit_amount_line_15", non_negative=True
)
"""Amount for each of the disabled dependants, MB479 line 15 "multiplied by $62 =": the printed $62,
from the `ca-mb/disabled_dependants_credit_amount_line_15` dataset."""

MB479_DISABLED_DEPENDANTS_CREDIT_LINE_15 = AmountKind.declare(
    CATALOG, "mb479_disabled_dependants_credit_line_15", non_negative=True
)
"""Disabled dependants credit, MB479 line 15 box B "Number of disabled dependants Line 60970
multiplied by $62 =": the number in box A times $62, rounded to the cent; line 17 adds it."""

MB479_DEPENDENT_CHILDREN_NUMBER_LINE_16 = AmountKind.declare(
    CATALOG, "mb479_dependent_children_number_line_16", non_negative=True
)
"""Number of dependent children, MB479 line 16 box A "Number of dependent children Line 60999": the
number as the filer gives it, an optional input; left out, it is 0."""

MB479_DEPENDENT_CHILDREN_CREDIT_AMOUNT_LINE_16 = AmountKind.declare(
    CATALOG, "dependent_children_credit_amount_line_16", non_negative=True
)
"""Amount for each of the dependent children, MB479 line 16 "multiplied by $26 =": the printed $26,
from the `ca-mb/dependent_children_credit_amount_line_16` dataset."""

MB479_DEPENDENT_CHILDREN_CREDIT_LINE_16 = AmountKind.declare(
    CATALOG, "mb479_dependent_children_credit_line_16", non_negative=True
)
"""Dependent children credit, MB479 line 16 box B "Number of dependent children Line 60999
multiplied by $26 =": the number in box A times $26, rounded to the cent; line 17 adds it."""

MB479_TOTAL_CREDITS_LINE_17 = AmountKind.declare(
    CATALOG, "mb479_total_credits_line_17", non_negative=True
)
"""Total credits, MB479 line 17 "Line 17 and line 61050: Add lines 7, 8, and 12 to 16. Total
credits": the basic credit of line 7 plus the credits of lines 8 and 12 to 16, each blank one taken
as 0."""

MB479_HOMEOWNER_RENTER_SENIOR_CREDITS_LINE_53 = AmountKind.declare(
    CATALOG, "mb479_homeowner_renter_senior_credits_line_53", non_negative=True
)
"""Homeowners, renters and seniors credits, MB479 line 53 "Line 53: Line 41 plus line 52 = ^": the
printed collecting sum of the skipped block of lines 20 to 52 (homeowners affordability, renters
affordability, seniors school tax rebate), a caller input that is read as blank when left out."""

MB479_EIA_MSPD_NUMBER_LINE_56 = AmountKind.declare(
    CATALOG, "mb479_eia_mspd_number_line_56", non_negative=True
)
"""EIA or MSPD number, MB479 line 56 "Line 56 and line 61255: If you (or your spouse or common-law
partner) did receive EIA or MSPD payments from Manitoba in 2025, enter the number from box 14 of
your (or your spouse's or common-law partner's) Form T5007, Statement of Benefits (even if it is
0.00)": the number from box 14 of Form T5007, a caller input that is read as 1 when left out."""

MB479_GREEN_ENERGY_PURCHASER_CREDIT_LINE_67 = AmountKind.declare(
    CATALOG, "mb479_green_energy_purchaser_credit_line_67", non_negative=True
)
"""Green energy equipment tax credit (purchaser), MB479 line 67 "Line 67 and line 61380: Complete
Form T1294": the credit worked out on Form T1294, which is not built, a caller input that is read
as blank when left out."""

MB479_GEOTHERMAL_HEAT_PUMP_COST_LINE_68 = AmountKind.declare(
    CATALOG, "mb479_geothermal_heat_pump_cost_line_68", non_negative=True
)
"""Geothermal heat pump cost, MB479 line 68 "Line 68 and line 61390: 7.5% of the adjusted cost of
geothermal heat pumps": the adjusted cost of geothermal heat pumps the 7.5% is taken of, a caller
input that is read as blank when left out."""

MB479_GEOTHERMAL_HEAT_PUMP_CREDIT_LINE_68 = AmountKind.declare(
    CATALOG, "mb479_geothermal_heat_pump_credit_line_68", non_negative=True
)
"""Green energy equipment tax credit (manufacturer), MB479 line 68 "Line 68 and line 61390: 7.5% of
the adjusted cost of geothermal heat pumps": calculated, 7.5% of the adjusted cost of geothermal
heat pumps, rounded half-up to the cent."""

MB479_GREEN_ENERGY_CREDITS_LINE_69 = AmountKind.declare(
    CATALOG, "mb479_green_energy_credits_line_69", non_negative=True
)
"""Green energy credits, MB479 line 69 "Line 69: Line 67 plus line 68 = ^": calculated, line 67 plus
line 68, with a blank line 67 read as 0."""

MB479_BOOK_PUBLISHING_CREDIT_LINE_71 = AmountKind.declare(
    CATALOG, "mb479_book_publishing_credit_line_71", non_negative=True
)
"""Book publishing tax credit, MB479 line 71 "Line 71 and line 61430: Enter your book publishing
tax credit from Form T1299": the credit worked out on Form T1299, which is not built, a caller
input that is read as blank when left out."""

MB479_CULTURAL_INDUSTRIES_PRINTING_CREDIT_LINE_73 = AmountKind.declare(
    CATALOG, "mb479_cultural_industries_printing_credit_line_73", non_negative=True
)
"""Cultural industries printing tax credit, MB479 line 73 "Line 73 and line 61480: Cultural
industries printing tax credit (maximum $1,100,000)": the credit of the line, a caller input that is
read as blank when left out; the printed maximum $1,100,000 is checked by the step that reads it."""

MB479_CULTURAL_INDUSTRIES_PRINTING_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "mb479_cultural_industries_printing_credit_maximum", non_negative=True
)
"""Cultural industries printing tax credit maximum, printed on MB479 line 73 "(maximum $1,100,000)":
the printed maximum, from the `ca-mb/cultural_industries_printing_credit_maximum` dataset; the bound
line 73 cannot pass."""

MB479_CULTURAL_INDUSTRIES_PRINTING_CREDIT_CHECKED_LINE_73 = AmountKind.declare(
    CATALOG, "mb479_cultural_industries_printing_credit_checked_line_73", non_negative=True
)
"""Cultural industries printing tax credit, MB479 line 73 "Line 73 and line 61480: Cultural
industries printing tax credit (maximum $1,100,000)": the entered amount, passed on unchanged when
it is at most the printed maximum, blank when left out; above the maximum it is refused, not
capped."""

MB479_COMMUNITY_ENTERPRISE_DEVELOPMENT_TAX_CREDIT_LINE_75 = AmountKind.declare(
    CATALOG, "mb479_community_enterprise_development_tax_credit_line_75", non_negative=True
)
"""Community enterprise development tax credit, MB479 line 75 "Line 75 and line 61484: Enter your
Manitoba community enterprise development tax credit from line 4 of Form T1256": the credit worked
out on Form T1256, which is not built, a caller input that is read as blank when left out; the
line 75 step checks it against the printed maximum."""

MB479_COMMUNITY_ENTERPRISE_DEVELOPMENT_TAX_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "mb479_community_enterprise_development_tax_credit_maximum", non_negative=True
)
"""Community enterprise development tax credit maximum, printed on MB479 line 75 "(maximum
$27,000)": the printed maximum, from the `ca-mb/community_enterprise_development_tax_credit_maximum`
dataset; the bound line 75 cannot pass."""

MB479_COMMUNITY_ENTERPRISE_DEVELOPMENT_TAX_CREDIT_CHECKED_LINE_75 = AmountKind.declare(
    CATALOG,
    "mb479_community_enterprise_development_tax_credit_checked_line_75",
    non_negative=True,
)
"""Community enterprise development tax credit, MB479 line 75 "Line 75 and line 61484: Enter your
Manitoba community enterprise development tax credit from line 4 of Form T1256. (maximum
$27,000)": the entered amount, passed on unchanged when it is at most the printed maximum, blank
when left out; above the maximum it is refused, not capped."""

MB479_TEACHING_SUPPLIES_EXPENSES_LINE_79 = AmountKind.declare(
    CATALOG, "mb479_teaching_supplies_expenses_line_79", non_negative=True
)
"""Teaching expense tax credit, MB479 line 79 "Line 79: Eligible teaching supplies expenses
(maximum $1,000) Line 61495": the eligible teaching supplies expenses the 15% is taken of, a caller
input read as blank when left out; the printed maximum $1,000 is checked by the step that reads
it."""

MB479_TEACHING_SUPPLIES_EXPENSES_MAXIMUM = AmountKind.declare(
    CATALOG, "mb479_teaching_supplies_expenses_maximum", non_negative=True
)
"""Teaching supplies expenses maximum, printed on MB479 line 79 "(maximum $1,000)": the printed
maximum, from the `ca-mb/teaching_supplies_expenses_maximum` dataset; the bound line 79 cannot
pass."""

MB479_TEACHING_SUPPLIES_EXPENSES_CHECKED_LINE_79 = AmountKind.declare(
    CATALOG, "mb479_teaching_supplies_expenses_checked_line_79", non_negative=True
)
"""Teaching expense tax credit, MB479 line 79 "Line 79: Eligible teaching supplies expenses
(maximum $1,000) Line 61495": the entered amount, passed on unchanged when it is at most the printed
maximum, blank when left out; above the maximum it is refused, not capped."""

MB479_TEACHING_EXPENSE_CREDIT_LINE_79 = AmountKind.declare(
    CATALOG, "mb479_teaching_expense_credit_line_79", non_negative=True
)
"""Teaching expense tax credit, MB479 line 79 "Line 79: Eligible teaching supplies expenses
(maximum $1,000) Line 61495 multiplied by 15% =": calculated, the checked eligible teaching supplies
expenses multiplied by 15%, rounded half-up to the cent, with a blank entry read as 0."""

MB479_RENTAL_HOUSING_CONSTRUCTION_INCENTIVE_TAX_CREDIT_LINE_80 = AmountKind.declare(
    CATALOG,
    "mb479_rental_housing_construction_incentive_tax_credit_line_80",
    non_negative=True,
)
"""Rental housing construction incentive tax credit, MB479 line 80 "Line 80: Certificate number:
Line 61496 Tax credit amount from your certificate": the credit amount on the certificate, a caller
input that is read as blank when left out; the certificate number is not read."""

MB428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "mb428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column, MB428 line 7 "Line 7: 0.00" (5,076.00; 11,833.50): the printed
tax at the start of the column of lines 2 to 8 that line 1 falls in. Column 3 is unbounded, so it is
never blank."""

MB479_FAMILY_INCOME_LINE_6 = AmountKind.declare(
    CATALOG, "mb479_family_income_line_6", non_negative=True
)
"""Family income, MB479 line 6: line 5 of column 1 (you) plus line 5 of column 2 (your spouse or
common-law partner), the amount that later lines refer to as "Amount from line 6". Column 2 is taken
as 0 when left out."""

MB479_REDUCTION_LINE_18 = AmountKind.declare(CATALOG, "mb479_reduction_line_18", non_negative=True)
"""Reduction, MB479 line 18: the amount from line 6 multiplied by 1%, the printed rate held in the
`ca-mb/personal_tax_credit_reduction_rate` dataset, rounded half-up to the cent."""

MB479_FERTILITY_TREATMENT_EXPENSES_LINE_61 = AmountKind.declare(
    CATALOG, "mb479_fertility_treatment_expenses_line_61", non_negative=True
)
"""Fertility treatment expenses, MB479 line 61 "Line 61: Eligible medical expenses for fertility
treatments Line 61268 multiplied by 40% (maximum $16,000)": the eligible medical expenses of the
first box, a caller input that is read as blank when left out."""

MB428_T691_AMOUNT_LINE_66 = AmountKind.declare(
    CATALOG, "mb428_t691_amount_line_66", non_negative=True
)
"""Form T691 amount, MB428 line 66 "Line 66: Form T691: line 1 minus line 2 of Part 7": a caller
input, read as blank when left out; the 50% multiplication step reads it."""

MB479_PAID_WORK_EXPERIENCE_CREDIT_LINE_63 = AmountKind.declare(
    CATALOG, "mb479_paid_work_experience_credit_line_63", non_negative=True
)
"""Paid work experience tax credit, MB479 line 63 "Line 63 and line 61310: Paid work experience tax
credit": the credit of the line, a caller input that is read as blank when left out."""

MB479_PERSONAL_TAX_CREDIT_LINE_19 = AmountKind.declare(
    CATALOG, "mb479_personal_tax_credit_line_19", non_negative=True
)
"""Personal tax credit, MB479 line 19 "Line 19: Line 17 minus line 18 (if negative, enter "0")
Enter this amount on line 54. Personal tax credit =": line 17 and line 18 (total credits less the
reduction, not below 0), rounded to the cent."""

MB479_CREDITS_LINE_55 = AmountKind.declare(CATALOG, "mb479_credits_line_55", non_negative=True)
"""Credits, MB479 line 55 "Line 55: Line 53 plus line 54 =": line 53 (the homeowner, renter and
senior credits, blank read as 0) plus line 54 (a copy of line 19), rounded to the cent."""

MB479_CREDITS_LINE_57 = AmountKind.declare(CATALOG, "mb479_credits_line_57", non_negative=True)
"""Credits, MB479 line 57 "Line 57: If you entered a number on line 56, multiply line 55 by line
56. Otherwise, enter the amount from line 55.": line 55 multiplied by line 56, a blank line 56 read
as 1, rounded to the cent."""

MB479_CREDITS_LINE_60 = AmountKind.declare(CATALOG, "mb479_credits_line_60", non_negative=True)
"""Credits, MB479 line 60 "Line 60: Line 58 plus line 59 =": line 58 (a copy of line 57) plus line
59 (the primary caregiver tax credit, blank read as 0), rounded to the cent."""

MB479_FERTILITY_TREATMENT_CREDIT_BEFORE_MAXIMUM_LINE_61 = AmountKind.declare(
    CATALOG, "mb479_fertility_treatment_credit_before_maximum_line_61", non_negative=True
)
"""Fertility treatment tax credit before its maximum, MB479 line 61 "Line 61: Eligible medical
expenses for fertility treatments Line 61268 multiplied by 40% (maximum $16,000) =" before the
maximum: the eligible medical expenses multiplied by 40%."""

MB479_FERTILITY_TREATMENT_CREDIT_LINE_61 = AmountKind.declare(
    CATALOG, "mb479_fertility_treatment_credit_line_61", non_negative=True
)
"""Fertility treatment tax credit, MB479 line 61 "Line 61: Eligible medical expenses for fertility
treatments Line 61268 multiplied by 40% (maximum $16,000) =": calculated, the eligible medical
expenses multiplied by 40%, then at most the printed maximum of $16,000."""

MB479_CREDITS_LINE_62 = AmountKind.declare(CATALOG, "mb479_credits_line_62", non_negative=True)
"""Credits, MB479 line 62 "Line 62: Line 60 plus line 61 =": line 60 plus line 61 (the fertility
treatment tax credit, already at most its $16,000 maximum), rounded to the cent."""

MB479_CREDITS_LINE_64 = AmountKind.declare(CATALOG, "mb479_credits_line_64", non_negative=True)
"""Credits, MB479 line 64 "Line 64: Line 62 plus line 63 =": line 62 plus line 63 (the paid work
experience tax credit, an optional input a caller leaves blank, read as 0), rounded to the cent."""

MB479_CREDITS_LINE_66 = AmountKind.declare(CATALOG, "mb479_credits_line_66", non_negative=True)
"""Credits, MB479 line 66 "Line 66: Line 64 plus line 65 =": line 64 plus line 65 (the odour control
credit, an optional input a caller leaves blank, read as 0), rounded to the cent."""

MB479_CREDITS_LINE_70 = AmountKind.declare(CATALOG, "mb479_credits_line_70", non_negative=True)
"""Credits, MB479 line 70 "Line 70: Line 66 plus line 69 = ^": line 66 plus line 69 (the green
energy credits), rounded to the cent."""

MB479_CREDITS_LINE_72 = AmountKind.declare(CATALOG, "mb479_credits_line_72", non_negative=True)
"""Credits, MB479 line 72 "Line 72: Line 70 plus line 71 = ^": line 70 plus line 71 (the book
publishing credit, an optional input a caller leaves blank, read as 0), rounded to the cent."""

MB479_CREDITS_LINE_74 = AmountKind.declare(CATALOG, "mb479_credits_line_74", non_negative=True)
"""Credits, MB479 line 74 "Line 74: Line 72 plus line 73 = ^": line 72 plus line 73 (the cultural
industries printing credit, checked against its printed maximum, blank when left out and read as 0),
rounded to the cent."""

MB479_CREDITS_LINE_76 = AmountKind.declare(CATALOG, "mb479_credits_line_76", non_negative=True)
"""Credits, MB479 line 76 "Line 76: Line 74 plus line 75 = ^": line 74 plus line 75 (the community
enterprise development tax credit, an optional input a caller leaves blank, read as 0), rounded to
the cent."""

MB479_CREDITS_LINE_78 = AmountKind.declare(CATALOG, "mb479_credits_line_78", non_negative=True)
"""Credits, MB479 line 78 "Line 78: Line 76 plus line 77 = ^": line 76 plus line 77 (the employee
share purchase tax credit, an optional input a caller leaves blank, read as 0), rounded to the
cent."""

AVERAGE_INCOME_TAX_RATE = AmountKind.declare(CATALOG, "average_income_tax_rate", non_negative=True)
"""Average income tax rate, the Manitoba return summary's own figure (no form prints it): T1 line
43500 "Total payable" (for the take-home filer, line 143 plus line 147: the federal and the Manitoba
income tax) divided by the salary (`ca/return_employment_income`), as a fraction, so 0.1598 is
15.98%. CPP and EI are not income tax and are not in it. It is 0 when the salary is 0."""

MANITOBA_BRACKET_RATE_RETURN = AmountKind.declare(
    CATALOG, "manitoba_bracket_rate_return", non_negative=True
)
"""Manitoba bracket rate, MB428 line 5 "Line 5: Rate": the printed rate of the column that line 1
falls in (10.8%, 12.75% or 17.4%), read from MB428 into the return summary. The form fills one
column, so the line is never blank."""

MANITOBA_TAX_AFTER_CREDITS_RETURN = AmountKind.declare(
    CATALOG, "manitoba_tax_after_credits_return", non_negative=True
)
"""Manitoba tax after the credits, MB428 line 65 "Line 60 minus line 64 (if negative, enter "0")":
the one amount of MB428's export totalled into the return summary's own artifact, the base of the
Manitoba rate gate."""

MANITOBA_RATE_GATE = AmountKind.declare(CATALOG, "manitoba_rate_gate", non_negative=True)
"""Manitoba rate gate: 0 where the Manitoba tax after the credits (MB428 line 65) is 0.00 and 1
where it is at least one cent, from the `ca-mb/marginal_rate_gate` dataset. A plain figure, not
printed on the form."""

MANITOBA_PHASE_OUT_AMOUNT_RETURN = AmountKind.declare(
    CATALOG, "manitoba_phase_out_amount_return", non_negative=True
)
"""Basic personal amount reduction, Worksheet MB428 line 8 "Line 6 multiplied by line 7": the one
amount of the worksheet's export totalled into the return summary's own artifact, the base of the
reduction slope."""

MANITOBA_BASIC_PERSONAL_AMOUNT_RETURN = AmountKind.declare(
    CATALOG, "manitoba_basic_personal_amount_return", non_negative=True
)
"""Basic personal amount, Worksheet MB428 line 9 "Line 1 minus line 8 (if negative, enter "0")": the
one amount of the worksheet's export totalled into the return summary's own artifact, the base of
the basic personal amount gate."""

MANITOBA_BASE_AMOUNT_RETURN = AmountKind.declare(
    CATALOG, "manitoba_base_amount_return", non_negative=True
)
"""Base amount, Worksheet MB428 line 7 "Line 7: Base amount 15,780.00": the one amount of the
worksheet's export totalled into the return summary's own artifact, the dividend of the phase-out
ratio."""

MANITOBA_INCOME_THRESHOLD_RETURN = AmountKind.declare(
    CATALOG, "manitoba_income_threshold_return", non_negative=True
)
"""Income threshold, Worksheet MB428 line 5 "Line 5: Income threshold 200,000.00": the one amount of
the worksheet's export totalled into the return summary's own artifact, the divisor of the phase-out
ratio."""

MANITOBA_BASIC_PERSONAL_AMOUNT_GATE = AmountKind.declare(
    CATALOG, "manitoba_basic_personal_amount_gate", non_negative=True
)
"""Manitoba basic personal amount gate: 0 where the basic personal amount (Worksheet MB428 line 9)
is 0.00 and 1 where it is at least one cent, from the `ca-mb/marginal_rate_gate` dataset: the
phase-out counts only up to the net income where the amount reaches zero (400,000). A plain figure,
not printed on the form."""

MANITOBA_REDUCTION_SLOPE = AmountKind.declare(
    CATALOG, "manitoba_reduction_slope", non_negative=True
)
"""Manitoba reduction slope: 0 where the basic personal amount reduction (Worksheet MB428 line 8) is
0.00 and the printed 10.8% of MB428 line 52 where it is at least one cent, from the
`ca-mb/reduction_slope` dataset, with no rounding: the credit rate of the amount that falls away
above a net income of 200,000. Not printed on the form."""

MANITOBA_PHASE_OUT_RATIO = AmountKind.declare(
    CATALOG, "manitoba_phase_out_ratio", non_negative=True
)
"""Manitoba phase-out ratio: Worksheet MB428 line 7 over line 5 (15,780 / 200,000 = 0.0789), the
amount the basic personal amount falls by for each further dollar of net income. Exact. Not printed
on the form."""

MANITOBA_PHASE_OUT_CREDIT_RATE = AmountKind.declare(
    CATALOG, "manitoba_phase_out_credit_rate", non_negative=True
)
"""Manitoba phase-out credit rate: the phase-out ratio times the reduction slope (0.0789 x 0.108 =
0.0085212), the credit a further dollar of net income takes away where the reduction is above
zero. Exact. Not printed on the form."""

MANITOBA_PHASE_OUT_RATE = AmountKind.declare(CATALOG, "manitoba_phase_out_rate", non_negative=True)
"""Manitoba phase-out rate: the basic personal amount gate (line 9 above zero) times the phase-out
credit rate: 0.0085212 inside the range where the basic personal amount falls with income, 0
outside it. Exact. Not printed on the form."""

MANITOBA_BRACKET_RATE_WITH_PHASE_OUT = AmountKind.declare(
    CATALOG, "manitoba_bracket_rate_with_phase_out", non_negative=True
)
"""Manitoba bracket rate with the phase-out: the bracket rate plus the phase-out rate, since a
further dollar of income also takes away part of the basic personal amount. Exact. Not printed on
the form."""

MANITOBA_MARGINAL_RATE = AmountKind.declare(CATALOG, "manitoba_marginal_rate", non_negative=True)
"""Manitoba marginal rate: the bracket rate with the phase-out where the Manitoba tax after the
credits (MB428 line 65) is above zero, and 0 where it is not: the rate a further dollar of income
is taxed at in Manitoba, on the return summary. Not printed on the form."""

MARGINAL_TAX_RATE = AmountKind.declare(CATALOG, "marginal_tax_rate", non_negative=True)
"""Marginal tax rate: the income tax rate on a further dollar of salary, the sum of the federal
marginal rate and the Manitoba marginal rate (Manitoba has no surtax or health premium), on the
return summary. Not printed on the form."""
