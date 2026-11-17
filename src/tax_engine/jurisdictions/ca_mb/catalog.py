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
$1,000)": the amount the filer claims, a caller input that is read as blank when left out."""

MB428_MEDICAL_EXPENSES_LINE_50 = AmountKind.declare(
    CATALOG, "mb428_medical_expenses_line_50", non_negative=True
)
"""Medical expenses, MB428 line 50 (line 58769) "Line 48 plus line 49 =": line 48 plus line 49, an
optional input; a blank is read as 0 by the line 51 step."""

MB428_DONATIONS_CREDIT_LINE_56 = AmountKind.declare(
    CATALOG, "mb428_donations_credit_line_56", non_negative=True
)
"""Donations and gifts credit, MB428 line 56 (line 58969) "Line 56 and line 58969: Line 54 plus line
55 =": a caller input, read as blank when left out; line 57 reads it."""

MB428_NON_REFUNDABLE_CREDITS_LINE_57 = AmountKind.declare(
    CATALOG, "mb428_non_refundable_credits_line_57", non_negative=True
)
"""Manitoba non-refundable tax credits, MB428 line 57 "Line 57 and line 61500: Line 53 plus line 56
Enter this amount on line 61. Manitoba non-refundable tax credits =": line 53 plus line 56, read by
line 61 on the tax form."""

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
repayment (included on line 23200 of the return)": the total of the two repayments, a caller input
that is read as blank when left out, column 1 (you) only."""

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
