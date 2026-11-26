"""The Nova Scotia artifact catalog: Nova Scotia's own kinds, named
from the Nova Scotia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ns import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

NS428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "ns428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form NS428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3 and 4."""

NS428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "ns428_tax_on_taxable_income_line_8", non_negative=True
)
"""Nova Scotia tax on taxable income, NS428 line 8 "Line 6 plus line 7 Nova Scotia tax on taxable
income =": line 6 plus line 7, copied to line 53 and read by the tax after credits."""

NS428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "ns428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form NS428 line 3 "Column 1: Line 1 is $30,507 or less / Line 3: 0.00"
(30,507.00; 61,015.00; 95,883.00; 154,650.00): the printed lower bound of the column of lines 2 to
8 that line 1 falls in."""

NS428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "ns428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, NS428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

NS428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "ns428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form NS428 line 5 "Column 1: Line 1 is $30,507 or less / Line 5: Rate 8.79%"
(14.95%; 16.67%; 17.5%; 21%): the printed rate of the column of lines 2 to 8 that line 1 falls
in."""

NS428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "ns428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, NS428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5 =":
line 4 times the rate of line 5, rounded to the cent."""

NS428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "ns428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column of lines 2 to 8 (the engine's description; the form prints no
title for line 7), Form NS428 line 7 "Column 1: Line 1 is $30,507 or less / Line 7: 0.00"
(2,681.57; 7,242.51; 13,055.01; 23,339.23): the figure printed on line 7 of the column that line 1
falls in."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, NS428 line 9 "Line 9 and line 58040: Basic personal amount Claim
$11,744": the printed $11,744, claimed whole and not income-tested."""

NS428_CREDITS_SUBTOTAL_LINE_19 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_19", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 19 "Add lines 9 to 18.": the sum of the personal amounts
claimed, here the basic personal amount alone."""

NS428_CPP_CONTRIBUTIONS_LINE_21 = AmountKind.declare(
    CATALOG, "ns428_cpp_contributions_line_21", non_negative=True
)
"""CPP or QPP contributions, NS428 line 21 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

NS428_QPP_CONTRIBUTIONS_LINE_22 = AmountKind.declare(
    CATALOG, "ns428_qpp_contributions_line_22", non_negative=True
)
"""Quebec Pension Plan contributions, NS428 line 22 "Amount from line 31000 of your return": a
record total of the T1's export (`ca/self_employment_cpp_qpp_contributions_line_31000`), 0 for a
salary-only caller."""

NS428_EI_PREMIUMS_LINE_23 = AmountKind.declare(
    CATALOG, "ns428_ei_premiums_line_23", non_negative=True
)
"""EI premiums credit amount, NS428 line 23 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

NS428_EI_PREMIUMS_LINE_24 = AmountKind.declare(
    CATALOG, "ns428_ei_premiums_line_24", non_negative=True
)
"""Employment insurance premiums, NS428 line 24 "Amount from line 31217 of your return": a record
total of the T1's export (`ca/ei_premiums_on_self_employment_line_31217`), 0 for a salary-only
caller."""

NS428_CPP_EI_AND_OTHER_LINE_25 = AmountKind.declare(
    CATALOG, "ns428_cpp_ei_and_other_line_25", non_negative=True
)
"""CPP or QPP, EI and other credit amounts, NS428 line 25 "Add lines 21 to 24.": the sum of the CPP
or QPP contributions, the QPP contributions and the EI premiums on lines 21 to 24."""

NS428_CREDITS_SUBTOTAL_LINE_26 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_26", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 26 "Line 20 plus line 25": line 20, a copy of line 19,
plus line 25, read by the next line of the credits."""

NS428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "ns428_pension_income_amount", non_negative=True
)
"""Pension income amount, NS428 line 27 "Line 27 and line 58360: Pension income amount (maximum
$1,173)": the amount the filer claims, a caller input that is read as 0 when it is left out; the
line 27 step checks it against the printed maximum."""

NS428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "ns428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on NS428 line 27 "(maximum $1,173)": the printed maximum,
from the `ca-ns/pension_income_amount_maximum` dataset; the bound line 27 cannot pass."""

NS428_PENSION_INCOME_AMOUNT_CHECKED_LINE_27 = AmountKind.declare(
    CATALOG, "ns428_pension_income_amount_checked_line_27", non_negative=True
)
"""Pension income amount, NS428 line 27 "Line 27 and line 58360: Pension income amount (maximum
$1,173)": the entered amount, passed on unchanged when it is at most the printed maximum, read as 0
when left out; above the maximum it is refused, not capped."""

NS428_CREDITS_SUBTOTAL_LINE_29 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_29", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 29 "Add lines 26 to 28.": line 26 plus the checked
pension income amount of line 27, line 28 (the caregiver amount) not being built."""

NS428_CREDITS_SUBTOTAL_LINE_32 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_32", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 32 "Add lines 29 to 31.": line 29, lines 30 and 31 (the
disability amounts) not being built."""

NS428_STUDENT_LOAN_INTEREST_LINE_33 = AmountKind.declare(
    CATALOG, "ns428_student_loan_interest_line_33", non_negative=True
)
"""Interest paid on student loans, NS428 line 33 (line 58520) "Interest paid on your student loans
(amount from line 31900 of your return)": a record total of the T1's export
(`ca/student_loan_interest_line_31900`), 0 for a salary-only caller."""

NS428_CREDITS_SUBTOTAL_LINE_37 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_37", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 37 "Add lines 32 to 36.": line 32 plus line 33, lines 34
to 36 (tuition and transfers) not being built."""

NS428_MEDICAL_EXPENSES_LINE_38 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_line_38", non_negative=True
)
"""Medical expenses, NS428 line 38 (line 58689) "Amount from line 33099 of your return": a record
total of the T1's export (`ca/medical_expenses_line_33099`), 0 for a salary-only caller."""

NS428_NET_INCOME_LINE_39 = AmountKind.declare(
    CATALOG, "ns428_net_income_line_39", non_negative=True
)
"""Net income, NS428 line 39 "Amount from line 23600 of your return": a record total of the T1's
net income, line 23600 as the T1 floors it."""

NS428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_41 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_rate_amount_line_41", non_negative=True
)
"""Medical expenses threshold, NS428 line 41 "Line 39 multiplied by the percentage from line 40 =":
line 39 times the 3% of line 40."""

NS428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_42 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_limited_amount_line_42", non_negative=True
)
"""Medical expenses threshold, limited, NS428 line 42 "Enter whichever is less: $1,637 or the amount
on line 41.": the lesser of the printed ceiling and line 41."""

NS428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_43 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_over_limit_line_43", non_negative=True
)
"""Medical expenses over the limit, NS428 line 43 "Line 38 minus line 42 (if negative, enter "0")
=": line 38 minus line 42, never below 0; a blank line 38 is read as 0."""
