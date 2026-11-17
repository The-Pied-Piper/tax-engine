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

