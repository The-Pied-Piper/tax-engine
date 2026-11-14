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

BC428_BRACKET_LOWER_BOUND_LINE_10 = AmountKind.declare(
    CATALOG, "bc428_bracket_lower_bound_line_10", non_negative=True
)
"""Lower bound of the column, BC428 line 10 "Line 10: 137,407.00": the printed lower bound of the
column of lines 9 to 15 that line 1 falls in, blank when line 1 is 137,407 or less."""

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

BC428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "bc428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, BC428 line 3 "Line 3: 0.00" (49,279.00; 98,560.00; 113,158.00): the
printed lower bound of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is
above 137,407, where lines 9 to 15 apply."""

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
