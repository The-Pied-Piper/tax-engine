"""The federal catalog: Form T1139 (2025), "Reconciliation of 2025 Business Income for Tax
Purposes", Parts 2 to 5, in a row form for each business and a summary form for the return.

The row form `ca/t1139` is the form filled in for one business ("fill in another Form T1139 for
each business"), run once for each record of its list `ca/t1139_businesses`. The filer names the
statements of the business by their positions in the statements of its form (T2125, T2042 or
T2121); amounts A, H and I are those statements' line 9946, never typed again. The row form works
Part 2 (formula B or formula C), Part 3 (the death of a proprietor), Part 4 (D, E and G) and Part 5
(J and L) and gives, for the line the business is reported on, the net income the form tells the
filer to report (G or L) and the net income of the statements it takes the place of. The summary
form `ca/t1139_return` runs once: for each of the lines 13500, 13700, 13900, 14100 and 14300 it
takes the statements' net income, leaves out the statements a Form T1139 takes the place of and
adds the net income the forms report. A return with no Form T1139 reports the statements' net
income as before. Amounts 2G, 2O and 3G are exact fractions inside the steps of B, C and 3H, not
artifacts of their own."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

T1139_LINE = CATALOG.declare("t1139_line", int, non_negative=True)
"""Line of the return a business is reported on, Form T1139 Part 4 "Report amount G as
self-employment income on your return: For business income, enter it at line 13500 ... For
professional income, enter it at line 13700 ... For commission income, enter it at line 13900
... For farming income, enter it at line 14100 ... For fishing income, enter it at line 14300"
and the same list under Part 5 for amount L: the number of the filer's choice in that list, 1
for line 13500, 2 for line 13700, 3 for line 13900, 4 for line 14100 and 5 for line 14300 (the
form names no codes), one for each business, a starting count. It also names the statements of
amounts A, H and I: the T2125 statements for 1 to 3, the T2042 statements for 4 and the T2121
statements for 5."""

T1139_FORMULA = CATALOG.declare("t1139_formula", int, non_negative=True)
"""Formula used, Form T1139 Part 2 "Use only one of the formulas below" and Part 4 "Enter either
amount B, C, or 3H based on the formula you used above": the number of the filer's choice, 1 for
amount B (a fiscal period ending in 2025), 2 for amount C (a business started in 2025 with a fiscal
period ending in 2026), 3 for amount 3H (death of a proprietor), 0 when none is used (Part 5; the
form names no codes), one for each business, a starting count refused above 3 by
`ca/t1139_formula_checked`. Only the formula chosen counts; the boxes of the others are ignored."""

T1139_STATEMENT_NUMBER = CATALOG.declare("t1139_statement_number", int, non_negative=True)
"""Statement of the business, Form T1139 amount A "You can find the net income (loss) amount you
need to enter at amount A from your income and expenses statement for the fiscal period ending
in 2025": the position, from 1, of a statement in the list of the statements of its form, in the
order the filer gave them, a starting count."""

T1139_A_STATEMENTS = RecordListKind.declare(
    CATALOG, "t1139_a_statements", fields=(T1139_STATEMENT_NUMBER,)
)
"""Statements of amount A, Form T1139 Part 2 amount A: a starting list with one record for each
statement of the business, holding its position (`ca/t1139_statement_number`), added by
`ca/statement_amounts_total`. More than one when the business had more than one fiscal period
("amount A is the total of the net income (loss) of these fiscal periods"); none when the
business started in 2025 and has no fiscal period ending in 2025."""

T1139_H_STATEMENTS = RecordListKind.declare(
    CATALOG, "t1139_h_statements", fields=(T1139_STATEMENT_NUMBER,)
)
"""Statements of amount H, Form T1139 Part 5 amount H "Net income (loss) for your first fiscal
period that ends between January 1, 2025, and December 30, 2025": a starting list with one
record for each statement of that fiscal period, holding its position."""

T1139_I_STATEMENTS = RecordListKind.declare(
    CATALOG, "t1139_i_statements", fields=(T1139_STATEMENT_NUMBER,)
)
"""Statements of amount I, Form T1139 Part 5 amount I "Net income (loss) for the period that
starts after the end of your first fiscal period in 2025, and ends on December 31, 2025": a
starting list with one record for each statement of that period, holding its position."""

T1139_CANCELLING_ELECTION = CATALOG.declare("t1139_cancelling_election", int, non_negative=True)
"""Cancelling the election, Form T1139 Part 6 "I am cancelling my previous election to have a
fiscal period that does not end on December 31 in order to have a fiscal period ending on
December 31.": 1 when the box is ticked, so Part 5 applies, 0 when not, a starting count refused
above 1 by `ca/t1139_cancelling_election_checked`. The other two boxes of Part 6 make no
difference to a figure and are not inputs."""

T1139_AMOUNT_2A = CATALOG.declare("t1139_amount_2a", Decimal, non_negative=True)
"""Capital gain in amount A, Form T1139 Part 2 line 2A "Total of amount A considered to be a
taxable capital gain for the capital gains deduction": the amount the filer enters, a starting
amount."""

T1139_AMOUNT_2B = CATALOG.declare("t1139_amount_2b", Decimal, non_negative=True)
"""Capital gains deduction for 2025, Form T1139 Part 2 line 2B "Your total capital gains
deduction for 2025": the amount the filer enters, a starting amount (a figure of another form,
which cannot read the return)."""

T1139_AMOUNT_2E = CATALOG.declare("t1139_amount_2e", Decimal, non_negative=True)
"""Days after the fiscal period, Form T1139 Part 2 line 2E "Number of days in 2025 that you
carried on the business after your fiscal period ending in 2025 up to December 31, 2025": the
number the filer enters, a starting amount."""

T1139_AMOUNT_2F = CATALOG.declare("t1139_amount_2f", Decimal, non_negative=True)
"""Days in the fiscal period, Form T1139 Part 2 line 2F "Number of days that you carried on the
business in your fiscal period ending in 2025": the number the filer enters, a starting amount."""

T1139_AMOUNT_2H = CATALOG.declare("t1139_amount_2h", Decimal)
"""Net income for the fiscal period ending in 2026, Form T1139 Part 2 line 2H "Net income for
the fiscal period ending in 2026" ("If the net income for the fiscal period ending in 2026 is
unknown, use reasonable estimated amounts"): the amount the filer enters, a starting amount,
which may be a loss."""

T1139_AMOUNT_2I = CATALOG.declare("t1139_amount_2i", Decimal, non_negative=True)
"""Capital gain in the 2026 net income, Form T1139 Part 2 line 2I "Total of the net income
considered to be a taxable capital gain for the capital gains deduction": the amount the filer
enters, a starting amount."""

T1139_AMOUNT_2J = CATALOG.declare("t1139_amount_2j", Decimal, non_negative=True)
"""Capital gains deduction for 2026, Form T1139 Part 2 line 2J "Your total capital gains
deduction for 2026": the amount the filer enters, a starting amount (a figure of another form,
which cannot read the return)."""

T1139_AMOUNT_2M = CATALOG.declare("t1139_amount_2m", Decimal, non_negative=True)
"""Days in 2025, Form T1139 Part 2 line 2M "Number of days in 2025 that you carried on the
business in your fiscal period ending in 2026": the number the filer enters, a starting amount."""

T1139_AMOUNT_2N = CATALOG.declare("t1139_amount_2n", Decimal, non_negative=True)
"""Days in the fiscal period, Form T1139 Part 2 line 2N "Number of days that you carried on the
business in your fiscal period ending in 2026": the number the filer enters, a starting amount."""

T1139_DESIGNATES_AMOUNT = CATALOG.declare("t1139_designates_amount", int, non_negative=True)
"""Designating an amount, Form T1139 Part 2 "Enter at amount C the lesser of any amount you
designate as your additional business income or the result of the following formula": 1 when the
filer designates an amount, 0 when not, a starting count refused above 1 by
`ca/t1139_designates_amount_checked`."""

T1139_DESIGNATED_AMOUNT = CATALOG.declare("t1139_designated_amount", Decimal, non_negative=True)
"""Designated additional business income, Form T1139 Part 2 "any amount you designate as your
additional business income": the amount the filer enters when `ca/t1139_designates_amount` is 1,
a starting amount."""

T1139_AMOUNT_3A = CATALOG.declare("t1139_amount_3a", Decimal, non_negative=True)
"""Capital gain in amount A, Form T1139 Part 3 line 3A "Total of amount A considered to be a
taxable capital gain for the capital gains deduction": the amount the filer enters, a starting
amount."""

T1139_AMOUNT_3B = CATALOG.declare("t1139_amount_3b", Decimal, non_negative=True)
"""Capital gains deduction for 2025, Form T1139 Part 3 line 3B "Your total capital gains
deduction for 2025": the amount the filer enters, a starting amount (a figure of another form,
which cannot read the return)."""

T1139_AMOUNT_3E = CATALOG.declare("t1139_amount_3e", Decimal, non_negative=True)
"""Days up to the death, Form T1139 Part 3 line 3E "Number of days the business is carried on
after the end of the 2025 fiscal period, up to and including the date of death": the number the
filer enters, a starting amount."""

T1139_AMOUNT_3F = CATALOG.declare("t1139_amount_3f", Decimal, non_negative=True)
"""Days in the regular fiscal period, Form T1139 Part 3 line 3F "Number of days the business is
carried on that are in the regular fiscal period ending in 2025": the number the filer enters, a
starting amount."""

T1139_LAST_YEARS_ADDITIONAL_INCOME = CATALOG.declare(
    "t1139_last_years_additional_income", Decimal, non_negative=True
)
"""Last year's additional business income, Form T1139 Part 4 line F "Last year's additional
business income: Enter amount D from last year's Form T1139" and Part 5 line K, the same words:
the amount the filer enters, once for both lines, a starting amount (a figure of last year's
form, which the engine does not compute)."""

T1139_BUSINESSES = RecordListKind.declare(
    CATALOG,
    "t1139_businesses",
    fields=(
        T1139_LINE,
        T1139_FORMULA,
        T1139_A_STATEMENTS,
        T1139_H_STATEMENTS,
        T1139_I_STATEMENTS,
        T1139_CANCELLING_ELECTION,
        T1139_AMOUNT_2A,
        T1139_AMOUNT_2B,
        T1139_AMOUNT_2E,
        T1139_AMOUNT_2F,
        T1139_AMOUNT_2H,
        T1139_AMOUNT_2I,
        T1139_AMOUNT_2J,
        T1139_AMOUNT_2M,
        T1139_AMOUNT_2N,
        T1139_DESIGNATES_AMOUNT,
        T1139_DESIGNATED_AMOUNT,
        T1139_AMOUNT_3A,
        T1139_AMOUNT_3B,
        T1139_AMOUNT_3E,
        T1139_AMOUNT_3F,
        T1139_LAST_YEARS_ADDITIONAL_INCOME,
    ),
)
"""Businesses with a Form T1139, Form T1139 Parts 2 to 5: a starting list with one record for
each business, holding the line it is reported on, the positions of its statements for amounts
A, H and I, the box ticked in Part 6 and the figures the filer enters on the lines of the
formulas. The row form `ca/t1139` runs once for each record."""

T1139_CANCELLING_ELECTION_CHECKED = CATALOG.declare(
    "t1139_cancelling_election_checked", int, non_negative=True
)
"""Cancelling the election as checked, Form T1139 Part 6: the answer, 0 or 1; an answer above 1
is refused, not capped."""

T1139_DESIGNATES_AMOUNT_CHECKED = CATALOG.declare(
    "t1139_designates_amount_checked", int, non_negative=True
)
"""Designating an amount as checked, Form T1139 Part 2: the answer, 0 or 1; an answer above 1 is
refused, not capped."""

T1139_LINE_CHECKED = CATALOG.declare("t1139_line_checked", int, non_negative=True)
"""The line of the business as checked, Form T1139 Part 4 "Report amount G as self-employment
income on your return": the number the filer chose, 1 to 5; a number outside them names no line
and is refused."""

T1139_FORMULA_CHECKED = CATALOG.declare("t1139_formula_checked", int, non_negative=True)
"""The formula used as checked, Form T1139 Part 2 "Use only one of the formulas below": the number
the filer chose, 0 to 3; a number above 3 names no formula and is refused, not capped."""

T1139_FORMULA_IS_B = CATALOG.declare("t1139_formula_is_b", int, non_negative=True)
"""Whether the formula used is that of amount B, Form T1139 Part 2 "Additional business income if
your fiscal period ends in 2025": 1 when `ca/t1139_formula_checked` is 1, else 0."""

T1139_FORMULA_IS_C = CATALOG.declare("t1139_formula_is_c", int, non_negative=True)
"""Whether the formula used is that of amount C, Form T1139 Part 2 "Additional business income if
your business started in 2025 and your fiscal period ends in 2026": 1 when
`ca/t1139_formula_checked` is 2, else 0."""

T1139_FORMULA_IS_3H = CATALOG.declare("t1139_formula_is_3h", int, non_negative=True)
"""Whether the formula used is that of amount 3H, Form T1139 Part 3 "Death of a proprietor" ("Enter
amount 3H at amount D below"): 1 when `ca/t1139_formula_checked` is 3, else 0."""

T1139_AMOUNT_B_CHOSEN = CATALOG.declare("t1139_amount_b_chosen", Decimal)
"""Amount B when the formula used is B, Form T1139 Part 4 "Enter either amount B, C, or 3H based on
the formula you used above": amount B times `ca/t1139_formula_is_b`, 0 for any other formula."""

T1139_AMOUNT_C_CHOSEN = CATALOG.declare("t1139_amount_c_chosen", Decimal)
"""Amount C when the formula used is C, Form T1139 Part 4 "Enter either amount B, C, or 3H based on
the formula you used above": amount C times `ca/t1139_formula_is_c`, 0 for any other formula."""

T1139_AMOUNT_3H_CHOSEN = CATALOG.declare("t1139_amount_3h_chosen", Decimal)
"""Amount 3H when the formula used is 3H, Form T1139 Part 4 "Enter either amount B, C, or 3H based
on the formula you used above": amount 3H times `ca/t1139_formula_is_3h`, 0 for any other
formula."""

T1139_AMOUNT_A = CATALOG.declare("t1139_amount_a", Decimal)
"""Amount A, Form T1139 Part 2 "Net income (loss) for your fiscal period ending in 2025 (if
applicable)": the net income of the statements of the business, "the amount found on line 9946",
added when there is more than one fiscal period ("amount A is the total of the net income (loss)
of these fiscal periods"), 0 with no statement named ("leave this field blank")."""

T1139_AMOUNT_H = CATALOG.declare("t1139_amount_h", Decimal)
"""Amount H, Form T1139 Part 5 "Net income (loss) for your first fiscal period that ends between
January 1, 2025, and December 30, 2025": the net income, line 9946, of the statement of that
fiscal period, 0 with no statement named."""

T1139_AMOUNT_I = CATALOG.declare("t1139_amount_i", Decimal)
"""Amount I, Form T1139 Part 5 "Net income (loss) for the period that starts after the end of
your first fiscal period in 2025, and ends on December 31, 2025": the net income, line 9946, of
the statement of that period ("You need a separate income and expense statement for each fiscal
period"), 0 with no statement named."""

T1139_AMOUNT_2C = CATALOG.declare("t1139_amount_2c", Decimal, non_negative=True)
"""Line 2C, Form T1139 Part 2 "Amount 2A or 2B, whichever is less"."""

T1139_AMOUNT_2D = CATALOG.declare("t1139_amount_2d", Decimal)
"""Line 2D, Form T1139 Part 2 "Amount A minus amount 2C"."""

T1139_AMOUNT_B = CATALOG.declare("t1139_amount_b", Decimal)
"""Amount B, Form T1139 Part 2 "Amount 2D multiplied by amount 2G", where line 2G is "Amount 2E
divided by amount 2F": 2D times 2E over 2F, one exact fraction rounded once (line 2G is not an
artifact of its own: the quotient has no finite decimal expansion), 0 when line 2F is 0 (the
formula is not used)."""

T1139_AMOUNT_2K = CATALOG.declare("t1139_amount_2k", Decimal, non_negative=True)
"""Line 2K, Form T1139 Part 2 "Amount 2I or 2J, whichever is less"."""

T1139_AMOUNT_2L = CATALOG.declare("t1139_amount_2l", Decimal)
"""Line 2L, Form T1139 Part 2 "Amount 2H minus amount 2K"."""

T1139_FORMULA_AMOUNT_FOR_C = CATALOG.declare("t1139_formula_amount_for_c", Decimal)
"""The result of the formula of amount C, Form T1139 Part 2 "Amount 2L multiplied by amount 2O",
where line 2O is "Amount 2M divided by amount 2N": 2L times 2M over 2N, one exact fraction
rounded once (line 2O is not an artifact of its own), 0 when line 2N is 0 (the formula is not
used)."""

T1139_DESIGNATED_OR_FORMULA_AMOUNT = CATALOG.declare("t1139_designated_or_formula_amount", Decimal)
"""The lesser of the designated amount and the result of the formula, Form T1139 Part 2 "Enter
at amount C the lesser of any amount you designate as your additional business income or the
result of the following formula"."""

T1139_AMOUNT_C = CATALOG.declare("t1139_amount_c", Decimal)
"""Amount C, Form T1139 Part 2 "Enter at amount C the lesser of any amount you designate as your
additional business income or the result of the following formula": that lesser amount when the
filer designates an amount, else the result of the formula."""

T1139_AMOUNT_3C = CATALOG.declare("t1139_amount_3c", Decimal, non_negative=True)
"""Line 3C, Form T1139 Part 3 "Amounts 3A or 3B, whichever is less"."""

T1139_AMOUNT_3D = CATALOG.declare("t1139_amount_3d", Decimal)
"""Line 3D, Form T1139 Part 3 "Amount A minus amount 3C"."""

T1139_AMOUNT_3H = CATALOG.declare("t1139_amount_3h", Decimal)
"""Amount 3H, Form T1139 Part 3 "Amount 3D multiplied by amount 3G", where line 3G is "Amount 3E
divided by amount 3F": 3D times 3E over 3F, one exact fraction rounded once (line 3G is not an
artifact of its own), 0 when line 3F is 0 (the formula is not used)."""

T1139_AMOUNT_D = CATALOG.declare("t1139_amount_d", Decimal, non_negative=True)
"""Amount D, Form T1139 Part 4 "Additional business income: Enter either amount B, C, or 3H
based on the formula you used above", at least 0 as Part 2 says "if the amount you calculate is
negative, the CRA considers it to be zero": the amount of the formula used (`ca/t1139_formula`),
the boxes of the other formulas being ignored, a negative amount counting as 0."""

T1139_AMOUNT_E = CATALOG.declare("t1139_amount_e", Decimal)
"""Line E, Form T1139 Part 4 "Subtotal: Amount A plus amount D"."""

T1139_AMOUNT_G = CATALOG.declare("t1139_amount_g", Decimal)
"""Amount G, Form T1139 Part 4 "Net income (loss) of the business: Amount E minus amount F
(report this amount on the appropriate line of your income tax and benefit return)", which may
be a loss."""

T1139_AMOUNT_J = CATALOG.declare("t1139_amount_j", Decimal)
"""Line J, Form T1139 Part 5 "Subtotal: Amount H plus amount I"."""

T1139_AMOUNT_L = CATALOG.declare("t1139_amount_l", Decimal)
"""Amount L, Form T1139 Part 5 "Net income (loss) of the business: Amount J minus amount K
(report this amount on the appropriate line of your return)", which may be a loss."""

T1139_NET_INCOME_REPORTED = CATALOG.declare("t1139_net_income_reported", Decimal)
"""The net income of the business to report, Form T1139 "Report amount G as self-employment
income on your return" (Part 4) or "Report amount L as self-employment income on your return"
(Part 5): amount L when the election is cancelled, else amount G."""

T1139_NET_INCOME_REPLACED = CATALOG.declare("t1139_net_income_replaced", Decimal)
"""The net income of the statements that amount G or L takes the place of on the return, Form
T1139 amount A (Part 4) or line J, amounts H plus I (Part 5): the net income, line 9946, of the
statements of the business, which the return would otherwise report on its line."""

T1139_ON_BUSINESS_LINE = CATALOG.declare("t1139_on_business_line", int, non_negative=True)
"""Whether the business is reported on line 13500, Form T1139 Part 4 "For business income, enter
it at line 13500": 1 when `ca/t1139_line` names it, else 0, from `ca/t1139_line_is_business`."""

T1139_ON_PROFESSIONAL_LINE = CATALOG.declare("t1139_on_professional_line", int, non_negative=True)
"""Whether the business is reported on line 13700, Form T1139 Part 4 "For professional income,
enter it at line 13700": 1 when `ca/t1139_line` names it, else 0, from
`ca/t1139_line_is_professional`."""

T1139_ON_COMMISSION_LINE = CATALOG.declare("t1139_on_commission_line", int, non_negative=True)
"""Whether the business is reported on line 13900, Form T1139 Part 4 "For commission income,
enter it at line 13900": 1 when `ca/t1139_line` names it, else 0, from
`ca/t1139_line_is_commission`."""

T1139_ON_FARMING_LINE = CATALOG.declare("t1139_on_farming_line", int, non_negative=True)
"""Whether the business is reported on line 14100, Form T1139 Part 4 "For farming income, enter
it at line 14100": 1 when `ca/t1139_line` names it, else 0, from `ca/t1139_line_is_farming`."""

T1139_ON_FISHING_LINE = CATALOG.declare("t1139_on_fishing_line", int, non_negative=True)
"""Whether the business is reported on line 14300, Form T1139 Part 4 "For fishing income, enter
it at line 14300": 1 when `ca/t1139_line` names it, else 0, from `ca/t1139_line_is_fishing`."""

T1139_REPORTED_ON_BUSINESS_LINE = CATALOG.declare("t1139_reported_on_business_line", Decimal)
"""Net income of the business reported on line 13500, Form T1139 "For business income, enter it
at line 13500": amount G or L if the business is on this line, else 0; the export of the row
form."""

T1139_REPORTED_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_reported_on_professional_line", Decimal
)
"""Net income of the business reported on line 13700, Form T1139 "For professional income, enter
it at line 13700": amount G or L if the business is on this line, else 0; the export of the row
form."""

T1139_REPORTED_ON_COMMISSION_LINE = CATALOG.declare("t1139_reported_on_commission_line", Decimal)
"""Net income of the business reported on line 13900, Form T1139 "For commission income, enter
it at line 13900": amount G or L if the business is on this line, else 0; the export of the row
form."""

T1139_REPORTED_ON_FARMING_LINE = CATALOG.declare("t1139_reported_on_farming_line", Decimal)
"""Net income of the business reported on line 14100, Form T1139 "For farming income, enter it
at line 14100": amount G or L if the business is on this line, else 0; the export of the row
form."""

T1139_REPORTED_ON_FISHING_LINE = CATALOG.declare("t1139_reported_on_fishing_line", Decimal)
"""Net income of the business reported on line 14300, Form T1139 "For fishing income, enter it
at line 14300": amount G or L if the business is on this line, else 0; the export of the row
form."""

T1139_REPLACED_ON_BUSINESS_LINE = CATALOG.declare("t1139_replaced_on_business_line", Decimal)
"""Net income of the statements that the business replaces on line 13500, Form T1139 amount A or
line J: the net income of its statements if the business is on this line, else 0; the export of
the row form."""

T1139_REPLACED_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_replaced_on_professional_line", Decimal
)
"""Net income of the statements that the business replaces on line 13700, Form T1139 amount A or
line J: the net income of its statements if the business is on this line, else 0; the export of
the row form."""

T1139_REPLACED_ON_COMMISSION_LINE = CATALOG.declare("t1139_replaced_on_commission_line", Decimal)
"""Net income of the statements that the business replaces on line 13900, Form T1139 amount A or
line J: the net income of its statements if the business is on this line, else 0; the export of
the row form."""

T1139_REPLACED_ON_FARMING_LINE = CATALOG.declare("t1139_replaced_on_farming_line", Decimal)
"""Net income of the statements that the business replaces on line 14100, Form T1139 amount A or
line J: the net income of its statements if the business is on this line, else 0; the export of
the row form."""

T1139_REPLACED_ON_FISHING_LINE = CATALOG.declare("t1139_replaced_on_fishing_line", Decimal)
"""Net income of the statements that the business replaces on line 14300, Form T1139 amount A or
line J: the net income of its statements if the business is on this line, else 0; the export of
the row form."""

T1139_STATEMENTS_ON_BUSINESS_LINE = CATALOG.declare("t1139_statements_on_business_line", Decimal)
"""Net income of all the statements reported on line 13500, Form T1139 "For business income,
enter it at line 13500": the statements' line 9946 on that line, added."""

T1139_REPLACED_TOTAL_ON_BUSINESS_LINE = CATALOG.declare(
    "t1139_replaced_total_on_business_line", Decimal
)
"""Net income of the statements that a Form T1139 takes the place of on line 13500, added over
the forms."""

T1139_REPORTED_TOTAL_ON_BUSINESS_LINE = CATALOG.declare(
    "t1139_reported_total_on_business_line", Decimal
)
"""Net income of the businesses that a Form T1139 reports on line 13500 (amount G or L), added
over the forms."""

T1139_KEPT_ON_BUSINESS_LINE = CATALOG.declare("t1139_kept_on_business_line", Decimal)
"""Net income reported on line 13500 by statements with no Form T1139: the statements less those
a Form T1139 takes the place of."""

T1139_BUSINESS_INCOME_ON_RETURN = CATALOG.declare("t1139_business_income_on_return", Decimal)
"""Net income on line 13500 of the return, Form T1139 "For business income, enter it at line
13500" and Form T2125, T2042 or T2121 line 9946: the net income of the statements with no Form
T1139 plus the net income of the businesses with one; the export of the summary form, which T1
reads."""

T1139_STATEMENTS_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_statements_on_professional_line", Decimal
)
"""Net income of all the statements reported on line 13700, Form T1139 "For professional income,
enter it at line 13700": the statements' line 9946 on that line, added."""

T1139_REPLACED_TOTAL_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_replaced_total_on_professional_line", Decimal
)
"""Net income of the statements that a Form T1139 takes the place of on line 13700, added over
the forms."""

T1139_REPORTED_TOTAL_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_reported_total_on_professional_line", Decimal
)
"""Net income of the businesses that a Form T1139 reports on line 13700 (amount G or L), added
over the forms."""

T1139_KEPT_ON_PROFESSIONAL_LINE = CATALOG.declare("t1139_kept_on_professional_line", Decimal)
"""Net income reported on line 13700 by statements with no Form T1139: the statements less those
a Form T1139 takes the place of."""

T1139_PROFESSIONAL_INCOME_ON_RETURN = CATALOG.declare(
    "t1139_professional_income_on_return", Decimal
)
"""Net income on line 13700 of the return, Form T1139 "For professional income, enter it at line
13700" and Form T2125, T2042 or T2121 line 9946: the net income of the statements with no Form
T1139 plus the net income of the businesses with one; the export of the summary form, which T1
reads."""

T1139_STATEMENTS_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_statements_on_commission_line", Decimal
)
"""Net income of all the statements reported on line 13900, Form T1139 "For commission income,
enter it at line 13900": the statements' line 9946 on that line, added."""

T1139_REPLACED_TOTAL_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_replaced_total_on_commission_line", Decimal
)
"""Net income of the statements that a Form T1139 takes the place of on line 13900, added over
the forms."""

T1139_REPORTED_TOTAL_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_reported_total_on_commission_line", Decimal
)
"""Net income of the businesses that a Form T1139 reports on line 13900 (amount G or L), added
over the forms."""

T1139_KEPT_ON_COMMISSION_LINE = CATALOG.declare("t1139_kept_on_commission_line", Decimal)
"""Net income reported on line 13900 by statements with no Form T1139: the statements less those
a Form T1139 takes the place of."""

T1139_COMMISSION_INCOME_ON_RETURN = CATALOG.declare("t1139_commission_income_on_return", Decimal)
"""Net income on line 13900 of the return, Form T1139 "For commission income, enter it at line
13900" and Form T2125, T2042 or T2121 line 9946: the net income of the statements with no Form
T1139 plus the net income of the businesses with one; the export of the summary form, which T1
reads."""

T1139_STATEMENTS_ON_FARMING_LINE = CATALOG.declare("t1139_statements_on_farming_line", Decimal)
"""Net income of all the statements reported on line 14100, Form T1139 "For farming income,
enter it at line 14100": the statements' line 9946 on that line, added."""

T1139_REPLACED_TOTAL_ON_FARMING_LINE = CATALOG.declare(
    "t1139_replaced_total_on_farming_line", Decimal
)
"""Net income of the statements that a Form T1139 takes the place of on line 14100, added over
the forms."""

T1139_REPORTED_TOTAL_ON_FARMING_LINE = CATALOG.declare(
    "t1139_reported_total_on_farming_line", Decimal
)
"""Net income of the businesses that a Form T1139 reports on line 14100 (amount G or L), added
over the forms."""

T1139_KEPT_ON_FARMING_LINE = CATALOG.declare("t1139_kept_on_farming_line", Decimal)
"""Net income reported on line 14100 by statements with no Form T1139: the statements less those
a Form T1139 takes the place of."""

T1139_FARMING_INCOME_ON_RETURN = CATALOG.declare("t1139_farming_income_on_return", Decimal)
"""Net income on line 14100 of the return, Form T1139 "For farming income, enter it at line
14100" and Form T2125, T2042 or T2121 line 9946: the net income of the statements with no Form
T1139 plus the net income of the businesses with one; the export of the summary form, which T1
reads."""

T1139_STATEMENTS_ON_FISHING_LINE = CATALOG.declare("t1139_statements_on_fishing_line", Decimal)
"""Net income of all the statements reported on line 14300, Form T1139 "For fishing income,
enter it at line 14300": the statements' line 9946 on that line, added."""

T1139_REPLACED_TOTAL_ON_FISHING_LINE = CATALOG.declare(
    "t1139_replaced_total_on_fishing_line", Decimal
)
"""Net income of the statements that a Form T1139 takes the place of on line 14300, added over
the forms."""

T1139_REPORTED_TOTAL_ON_FISHING_LINE = CATALOG.declare(
    "t1139_reported_total_on_fishing_line", Decimal
)
"""Net income of the businesses that a Form T1139 reports on line 14300 (amount G or L), added
over the forms."""

T1139_KEPT_ON_FISHING_LINE = CATALOG.declare("t1139_kept_on_fishing_line", Decimal)
"""Net income reported on line 14300 by statements with no Form T1139: the statements less those
a Form T1139 takes the place of."""

T1139_FISHING_INCOME_ON_RETURN = CATALOG.declare("t1139_fishing_income_on_return", Decimal)
"""Net income on line 14300 of the return, Form T1139 "For fishing income, enter it at line
14300" and Form T2125, T2042 or T2121 line 9946: the net income of the statements with no Form
T1139 plus the net income of the businesses with one; the export of the summary form, which T1
reads."""

T1139_PROFIT_A = CATALOG.declare("t1139_profit_a", Decimal, non_negative=True)
"""The profit of the statements of amount A, Form T1139 Part 2 amount A and the note "use only the
profit amounts" of a business that shows a loss while another shows a profit (Form T1-M line 28,
Form T929 line 4, the medical expense supplement): the line 9946 amount of each statement of the
business, a loss counted as 0, added; 0 with no statement named."""

T1139_PROFIT_H = CATALOG.declare("t1139_profit_h", Decimal, non_negative=True)
"""The profit of the statement of amount H, Form T1139 Part 5: the line 9946 amount of the
statement of the first fiscal period, a loss counted as 0; 0 with no statement named."""

T1139_PROFIT_I = CATALOG.declare("t1139_profit_i", Decimal, non_negative=True)
"""The profit of the statement of amount I, Form T1139 Part 5: the line 9946 amount of the statement
of the period after the first fiscal period, a loss counted as 0; 0 with no statement named."""

T1139_PROFIT_HI = CATALOG.declare("t1139_profit_hi", Decimal, non_negative=True)
"""The profit of the statements of amounts H and I added, Form T1139 Part 5 line J "Subtotal: Amount
H plus amount I", each statement's loss counted as 0."""

T1139_PROFIT_REPLACED = CATALOG.declare("t1139_profit_replaced", Decimal, non_negative=True)
"""The profit of the statements that Form T1139 amount G or L takes the place of on the return: the
profit of the statements of amount A (Part 4) or of amounts H and I added (Part 5), each
statement's loss counted as 0."""

T1139_PROFIT_REPLACED_ON_BUSINESS_LINE = CATALOG.declare(
    "t1139_profit_replaced_on_business_line", Decimal, non_negative=True
)
"""Profit of the statements that the business replaces on line 13500, Form T1139 amount A or
line J: the profit of its statements if the business is on this line, else 0; the export of the
row form."""

T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_profit_replaced_on_professional_line", Decimal, non_negative=True
)
"""Profit of the statements that the business replaces on line 13700, Form T1139 amount A or
line J: the profit of its statements if the business is on this line, else 0; the export of the
row form."""

T1139_PROFIT_REPLACED_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_profit_replaced_on_commission_line", Decimal, non_negative=True
)
"""Profit of the statements that the business replaces on line 13900, Form T1139 amount A or
line J: the profit of its statements if the business is on this line, else 0; the export of the
row form."""

T1139_PROFIT_REPLACED_ON_FARMING_LINE = CATALOG.declare(
    "t1139_profit_replaced_on_farming_line", Decimal, non_negative=True
)
"""Profit of the statements that the business replaces on line 14100, Form T1139 amount A or
line J: the profit of its statements if the business is on this line, else 0; the export of the
row form."""

T1139_PROFIT_REPLACED_ON_FISHING_LINE = CATALOG.declare(
    "t1139_profit_replaced_on_fishing_line", Decimal, non_negative=True
)
"""Profit of the statements that the business replaces on line 14300, Form T1139 amount A or
line J: the profit of its statements if the business is on this line, else 0; the export of the
row form."""

T1139_STATEMENT_PROFITS_ON_BUSINESS_LINE = CATALOG.declare(
    "t1139_statement_profits_on_business_line", Decimal, non_negative=True
)
"""Profit of all the statements reported on line 13500, Form T1139 "enter it at line 13500":
each statement's line 9946 amount, a loss counted as 0, added."""

T1139_REPLACED_PROFITS_TOTAL_ON_BUSINESS_LINE = CATALOG.declare(
    "t1139_replaced_profits_total_on_business_line", Decimal, non_negative=True
)
"""Profit of the statements that a Form T1139 takes the place of on line 13500, added over the
forms."""

T1139_REPORTED_PROFITS_TOTAL_ON_BUSINESS_LINE = CATALOG.declare(
    "t1139_reported_profits_total_on_business_line", Decimal, non_negative=True
)
"""Profit of the businesses that a Form T1139 reports on line 13500 (amount G or L, a loss counted
as 0), added over the forms."""

T1139_KEPT_PROFITS_ON_BUSINESS_LINE = CATALOG.declare(
    "t1139_kept_profits_on_business_line", Decimal
)
"""Profit reported on line 13500 by statements with no Form T1139: the profit of the statements
less the profit of those a Form T1139 takes the place of."""

T1139_BUSINESS_PROFIT_ON_RETURN = CATALOG.declare("t1139_business_profit_on_return", Decimal)
"""Profit on line 13500 of the return, each business counting its own profit and a loss counting
0: the profit of the statements with no Form T1139 plus the profit of the businesses with one; the
export of the summary form, which the readers of "net self-employment income (not including
losses)" (Form T1-M line 28, Form T929 line 4, the medical expense supplement) read."""

T1139_STATEMENT_PROFITS_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_statement_profits_on_professional_line", Decimal, non_negative=True
)
"""Profit of all the statements reported on line 13700, Form T1139 "enter it at line 13700":
each statement's line 9946 amount, a loss counted as 0, added."""

T1139_REPLACED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_replaced_profits_total_on_professional_line", Decimal, non_negative=True
)
"""Profit of the statements that a Form T1139 takes the place of on line 13700, added over the
forms."""

T1139_REPORTED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_reported_profits_total_on_professional_line", Decimal, non_negative=True
)
"""Profit of the businesses that a Form T1139 reports on line 13700 (amount G or L, a loss counted
as 0), added over the forms."""

T1139_KEPT_PROFITS_ON_PROFESSIONAL_LINE = CATALOG.declare(
    "t1139_kept_profits_on_professional_line", Decimal
)
"""Profit reported on line 13700 by statements with no Form T1139: the profit of the statements
less the profit of those a Form T1139 takes the place of."""

T1139_PROFESSIONAL_PROFIT_ON_RETURN = CATALOG.declare(
    "t1139_professional_profit_on_return", Decimal
)
"""Profit on line 13700 of the return, each business counting its own profit and a loss counting
0: the profit of the statements with no Form T1139 plus the profit of the businesses with one; the
export of the summary form, which the readers of "net self-employment income (not including
losses)" (Form T1-M line 28, Form T929 line 4, the medical expense supplement) read."""

T1139_STATEMENT_PROFITS_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_statement_profits_on_commission_line", Decimal, non_negative=True
)
"""Profit of all the statements reported on line 13900, Form T1139 "enter it at line 13900":
each statement's line 9946 amount, a loss counted as 0, added."""

T1139_REPLACED_PROFITS_TOTAL_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_replaced_profits_total_on_commission_line", Decimal, non_negative=True
)
"""Profit of the statements that a Form T1139 takes the place of on line 13900, added over the
forms."""

T1139_REPORTED_PROFITS_TOTAL_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_reported_profits_total_on_commission_line", Decimal, non_negative=True
)
"""Profit of the businesses that a Form T1139 reports on line 13900 (amount G or L, a loss counted
as 0), added over the forms."""

T1139_KEPT_PROFITS_ON_COMMISSION_LINE = CATALOG.declare(
    "t1139_kept_profits_on_commission_line", Decimal
)
"""Profit reported on line 13900 by statements with no Form T1139: the profit of the statements
less the profit of those a Form T1139 takes the place of."""

T1139_COMMISSION_PROFIT_ON_RETURN = CATALOG.declare("t1139_commission_profit_on_return", Decimal)
"""Profit on line 13900 of the return, each business counting its own profit and a loss counting
0: the profit of the statements with no Form T1139 plus the profit of the businesses with one; the
export of the summary form, which the readers of "net self-employment income (not including
losses)" (Form T1-M line 28, Form T929 line 4, the medical expense supplement) read."""

T1139_STATEMENT_PROFITS_ON_FARMING_LINE = CATALOG.declare(
    "t1139_statement_profits_on_farming_line", Decimal, non_negative=True
)
"""Profit of all the statements reported on line 14100, Form T1139 "enter it at line 14100":
each statement's line 9946 amount, a loss counted as 0, added."""

T1139_REPLACED_PROFITS_TOTAL_ON_FARMING_LINE = CATALOG.declare(
    "t1139_replaced_profits_total_on_farming_line", Decimal, non_negative=True
)
"""Profit of the statements that a Form T1139 takes the place of on line 14100, added over the
forms."""

T1139_REPORTED_PROFITS_TOTAL_ON_FARMING_LINE = CATALOG.declare(
    "t1139_reported_profits_total_on_farming_line", Decimal, non_negative=True
)
"""Profit of the businesses that a Form T1139 reports on line 14100 (amount G or L, a loss counted
as 0), added over the forms."""

T1139_KEPT_PROFITS_ON_FARMING_LINE = CATALOG.declare("t1139_kept_profits_on_farming_line", Decimal)
"""Profit reported on line 14100 by statements with no Form T1139: the profit of the statements
less the profit of those a Form T1139 takes the place of."""

T1139_FARMING_PROFIT_ON_RETURN = CATALOG.declare("t1139_farming_profit_on_return", Decimal)
"""Profit on line 14100 of the return, each business counting its own profit and a loss counting
0: the profit of the statements with no Form T1139 plus the profit of the businesses with one; the
export of the summary form, which the readers of "net self-employment income (not including
losses)" (Form T1-M line 28, Form T929 line 4, the medical expense supplement) read."""

T1139_STATEMENT_PROFITS_ON_FISHING_LINE = CATALOG.declare(
    "t1139_statement_profits_on_fishing_line", Decimal, non_negative=True
)
"""Profit of all the statements reported on line 14300, Form T1139 "enter it at line 14300":
each statement's line 9946 amount, a loss counted as 0, added."""

T1139_REPLACED_PROFITS_TOTAL_ON_FISHING_LINE = CATALOG.declare(
    "t1139_replaced_profits_total_on_fishing_line", Decimal, non_negative=True
)
"""Profit of the statements that a Form T1139 takes the place of on line 14300, added over the
forms."""

T1139_REPORTED_PROFITS_TOTAL_ON_FISHING_LINE = CATALOG.declare(
    "t1139_reported_profits_total_on_fishing_line", Decimal, non_negative=True
)
"""Profit of the businesses that a Form T1139 reports on line 14300 (amount G or L, a loss counted
as 0), added over the forms."""

T1139_KEPT_PROFITS_ON_FISHING_LINE = CATALOG.declare("t1139_kept_profits_on_fishing_line", Decimal)
"""Profit reported on line 14300 by statements with no Form T1139: the profit of the statements
less the profit of those a Form T1139 takes the place of."""

T1139_FISHING_PROFIT_ON_RETURN = CATALOG.declare("t1139_fishing_profit_on_return", Decimal)
"""Profit on line 14300 of the return, each business counting its own profit and a loss counting
0: the profit of the statements with no Form T1139 plus the profit of the businesses with one; the
export of the summary form, which the readers of "net self-employment income (not including
losses)" (Form T1-M line 28, Form T929 line 4, the medical expense supplement) read."""
