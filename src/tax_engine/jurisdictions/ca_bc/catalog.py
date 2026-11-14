"""The British Columbia artifact catalog: British Columbia's own kinds, named from the British
Columbia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_bc import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BC428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "bc428_taxable_income_line_1", non_negative=True
)
"""Taxable income, BC428 line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3, 4, 10 and 11."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, BC428 line 16 (line 58040) "Basic personal amount Claim $12,932": the
amount claimed, the first part of the total of the British Columbia credit amounts."""

BC428_SUBTOTAL_LINE_25 = AmountKind.declare(CATALOG, "bc428_subtotal_line_25", non_negative=True)
"""Subtotal of credit amounts, BC428 line 25 "Line 25: Add lines 16, 17, 20, 23 and 24.": the sum of
those lines, here the basic personal amount (line 16) alone."""

BC428_BRACKET_LOWER_BOUND_LINE_10 = AmountKind.declare(
    CATALOG, "bc428_bracket_lower_bound_line_10", non_negative=True
)
"""Lower bound of the column, BC428 line 10 "Line 10: 137,407.00": the printed lower bound of the
column of lines 9 to 15 that line 1 falls in, blank when line 1 is 137,407 or less."""

BC428_BRACKET_TAX_AT_START_LINE_14 = AmountKind.declare(
    CATALOG, "bc428_bracket_tax_at_start_line_14", non_negative=True
)
"""Tax at the start of the column, BC428 line 14 "Line 14: 10,801.15": the printed tax at the start
of the column of lines 9 to 15 that line 1 falls in, blank when line 1 is 137,407 or less."""

BC428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_11 = AmountKind.declare(
    CATALOG, "bc428_taxable_income_over_lower_bound_line_11", non_negative=True
)
"""Taxable income over the lower bound, BC428 line 11 "Line 11: Line 9 minus line 10 (cannot be
negative)": line 1 minus the lower bound of line 10, not below 0; blank when line 1 is 137,407.00
or less, where line 10 is blank."""

BC428_BRACKET_RATE_LINE_12 = AmountKind.declare(
    CATALOG, "bc428_bracket_rate_line_12", non_negative=True
)
"""Rate, BC428 line 12 "Line 12: Rate 14.7%; 16.8%; 20.5%": the printed rate of the column of lines
9 to 15 that line 1 falls in, blank when line 1 is 137,407 or less."""

BC428_CPP_CONTRIBUTIONS_LINE_27 = AmountKind.declare(
    CATALOG, "bc428_cpp_contributions_line_27", non_negative=True
)
"""CPP or QPP contributions, BC428 line 27 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

BC428_BRITISH_COLUMBIA_TAX_LINE_91 = AmountKind.declare(
    CATALOG, "bc428_british_columbia_tax_line_91", non_negative=True
)
"""British Columbia tax, BC428 line 91 "Enter this amount on line 42800 of your return.": the
British Columbia tax, entered on T1 line 42800."""

BC428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "bc428_pension_income_amount", non_negative=True
)
"""Pension income amount, BC428 line 36 "Line 36 and line 58360: Pension income amount (maximum
$1,000)": the amount the filer claims, a caller input that is read as blank when left out."""

BC428_MINIMUM_TAX_CARRYOVER_AMOUNT = AmountKind.declare(
    CATALOG, "bc428_minimum_tax_carryover_amount", non_negative=True
)
"""Amount from line 40427 of the return, BC428 line 66 "Line 66 and line 61540: Amount from line
40427 of your return": the minimum tax carryover amount, a caller input that is read as blank when
left out."""

BC428_DONATIONS_AND_GIFTS_LINE_57 = AmountKind.declare(
    CATALOG, "bc428_donations_and_gifts_line_57", non_negative=True
)
"""Donations and gifts, BC428 line 57 and line 58969 "Donations and gifts (use Worksheet BC428)":
the amount the filer claims, a caller input that is read as blank when left out."""

BC428_EI_PREMIUMS_LINE_29 = AmountKind.declare(
    CATALOG, "bc428_ei_premiums_line_29", non_negative=True
)
"""EI premiums credit amount, BC428 line 29 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

BC428_MEDICAL_EXPENSES_LINE_53 = AmountKind.declare(
    CATALOG, "bc428_medical_expenses_line_53", non_negative=True
)
"""Medical expenses, BC428 line 53 (line 58769) "Line 51 plus line 52 =": line 51 plus line 52, an
optional input; a blank is read as 0 by the step that reads it."""

BC428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "bc428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, BC428 line 3 "Line 3: 0.00" (49,279.00; 98,560.00; 113,158.00): the
printed lower bound of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is
above 137,407, where lines 9 to 15 apply."""

BC428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "bc428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column, BC428 line 7 "Line 7: 0.00" (2,493.52; 6,288.15; 7,820.94): the
printed tax at the start of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1
is above 137,407, where lines 9 to 15 apply."""

BC428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "bc428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, BC428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero; blank when line 3 is blank."""

BC428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "bc428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, BC428 line 5 "Line 5: Rate" (5.06%; 7.7%; 10.5%; 12.29%): the printed rate of
the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is above 137,407, where
lines 9 to 15 apply."""

BC428_CPP_EI_AND_OTHER_LINE_33 = AmountKind.declare(
    CATALOG, "bc428_cpp_ei_and_other_line_33", non_negative=True
)
"""BC428 line 33 "Add lines 27 to 32.": the sum of lines
27 and 29. Lines 28, 30, 31 and 32 are not built: a salary-only filer has none of them."""

BC428_SUBTOTAL_LINE_35 = AmountKind.declare(CATALOG, "bc428_subtotal_line_35", non_negative=True)
"""Subtotal, BC428 line 35 "Line 35: Add lines 26, 33 and 34.": the sum of line 26 (a copy of line
25), line 33 and line 34. Line 34 (adoption expenses) is not built: a salary-only filer has none."""

BC428_SUBTOTAL_LINE_37 = AmountKind.declare(CATALOG, "bc428_subtotal_line_37", non_negative=True)
"""Subtotal, BC428 line 37 "Line 37: Line 35 plus line 36 = ^": the sum of line 35 and line 36, the
pension income amount, an optional input read as 0 when the filer has none."""

BC428_SUBTOTAL_LINE_40 = AmountKind.declare(CATALOG, "bc428_subtotal_line_40", non_negative=True)
"""Subtotal, BC428 line 40 "Line 40: Add lines 37 to 39. = ^": the sum of line 37. Lines 38 and 39
are the disability amounts, not built: a salary-only filer has none."""

BC479_BRITISH_COLUMBIA_CREDITS_LINE_45 = AmountKind.declare(
    CATALOG, "bc479_british_columbia_credits_line_45", non_negative=True
)
"""British Columbia credits, BC479 line 45 "Enter this amount on line 47900 of your return.": the
British Columbia credits, entered on T1 line 47900."""
