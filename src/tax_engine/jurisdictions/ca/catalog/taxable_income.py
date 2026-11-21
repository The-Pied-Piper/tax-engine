"""The federal catalog: losses of other years and taxable income.

The non-capital and net capital losses of other years, the deductions from net income, taxable
income and the federal tax on taxable income (T1 line 76).
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

NET_CAPITAL_LOSS_NUMERATOR_ONE_2000 = AmountKind.declare(
    CATALOG, "net_capital_loss_numerator_one_2000", non_negative=True
)
"""The 1 of the Chart A column (B) factor, Form T1436 Chart A column (B) "1/(IR × 2)", row
"In 2000": the 1 printed in the factor, a credit of 1."""

DEDUCTIONS_FROM_NET_INCOME = AmountKind.declare(
    CATALOG, "deductions_from_net_income", non_negative=True
)
"""Deductions from net income, T1 line 68 and line 25700 "Add lines 58 to 67.": the sum of the ten
printed lines 24400 to 25600 (`t1_taxable_income_line_25700.yaml`), each an optional input of
`t1_taxable_income_line_25700_inputs.yaml` read as 0 when blank. Line 26000 takes it off net income.
"""

T1_LINES_24400_TO_25200_SUBTOTAL = AmountKind.declare(
    CATALOG, "t1_lines_24400_to_25200_subtotal", non_negative=True
)
"""Unprinted subtotal of the first parts of T1 line 68 and line 25700, so that the sentence of the
line stays short: lines 58 to 62 (24400 to 25200) added up."""

T1_LINES_25300_TO_25600_SUBTOTAL = AmountKind.declare(
    CATALOG, "t1_lines_25300_to_25600_subtotal", non_negative=True
)
"""Unprinted subtotal of the last parts of T1 line 68 and line 25700, so that the sentence of the
line stays short: lines 63 to 67 (25300 to 25600) added up."""

T1_LINE_24400 = AmountKind.declare(CATALOG, "t1_line_24400", non_negative=True)
"""Canadian Armed Forces personnel and police deduction, T1 line 58 and line 24400: an optional
input, taken as the form takes it; a blank is read as 0 by the line 25700 step."""

T1_LINE_24900 = AmountKind.declare(CATALOG, "t1_line_24900", non_negative=True)
"""Security options deductions, T1 line 59 and line 24900: an optional input, taken as the
form takes it; a blank is read as 0 by the line 25700 step."""

T1_LINE_25000 = AmountKind.declare(CATALOG, "t1_line_25000", non_negative=True)
"""Other payments deduction, T1 line 60 and line 25000: an optional input, taken as the
form takes it; a blank is read as 0 by the line 25700 step."""

T1_LINE_25100 = AmountKind.declare(CATALOG, "t1_line_25100", non_negative=True)
"""Limited partnership losses of other years, T1 line 61 and line 25100: an optional input, taken as
the form takes it; a blank is read as 0 by the line 25700 step."""

T1_LINE_25200 = AmountKind.declare(CATALOG, "t1_line_25200", non_negative=True)
"""Non-capital losses of other years, T1 line 62 and line 25200: an optional input, taken as the
form takes it; a blank is read as 0 by the line 25700 step."""

T1_LINE_25300 = AmountKind.declare(CATALOG, "t1_line_25300", non_negative=True)
"""Net capital losses of other years, T1 line 63 and line 25300: an optional input, taken as the
form takes it; a blank is read as 0 by the line 25700 step."""

T1_LINE_25395 = AmountKind.declare(CATALOG, "t1_line_25395", non_negative=True)
"""Capital gains deduction for qualifying business transfers or qualifying cooperative conversions,
T1 line 64 and line 25395: an optional input, taken as the form takes it; a blank is read as 0 by
the line 25700 step."""

T1_LINE_25400 = AmountKind.declare(CATALOG, "t1_line_25400", non_negative=True)
"""Capital gains deduction, T1 line 65 and line 25400: an optional input, taken as the form takes
it; a blank is read as 0 by the line 25700 step."""

T1_LINE_25500 = AmountKind.declare(CATALOG, "t1_line_25500", non_negative=True)
"""Northern residents deductions, T1 line 66 and line 25500: an optional input, taken as the
form takes it; a blank is read as 0 by the line 25700 step."""

T1_LINE_25600 = AmountKind.declare(CATALOG, "t1_line_25600", non_negative=True)
"""Additional deductions, T1 line 67 and line 25600: an optional input, taken as the form takes
it; a blank is read as 0 by the line 25700 step."""

TAXABLE_INCOME = AmountKind.declare(CATALOG, "taxable_income", non_negative=True)
"""Taxable income, T1 line 69 "Line 57 minus line 68 (if negative, enter "0") Taxable income"
(line 26000, as Step 5 refers to it): net income less the deductions from net income, not below
zero; the base the federal and provincial brackets apply to.

Line 57 is "Enter the amount from line 56 of the previous page" (net income); line 68 (25700) is
"Add lines 58 to 67".
"""

CHART_2_NUMERATOR_ONE = AmountKind.declare(CATALOG, "chart_2_numerator_one", non_negative=True)
"""The 1 of the Chart 2 line 16 quotient, Form T657 Chart 2 line 16 "Adjustment of 2000 capital
gains deduction: Amount from line 14 × [ 1 – ( 2 × IR )]": the 1 printed in the bracket, a credit of
1."""

CHART_2025_PART_1_AMOUNT_A = AmountKind.declare(
    CATALOG, "chart_2025_part_1_amount_a", non_negative=True
)
"""Maximum capital gains deduction for QFFP and/or QSBCS reported in 2025 but disposed of in period
1 of 2024, Form T657 Chart 2025 Part 1 amount A: 522,145.00, a dataset."""

CHART_2025_PART_2_AMOUNT_A = AmountKind.declare(
    CATALOG, "chart_2025_part_2_amount_a", non_negative=True
)
"""Maximum capital gains deduction for QFFP and/or QSBCS disposed of in 2025 or disposed of after
June 24, 2024 and reported in 2025, Form T657 Chart 2025 Part 2 amount A: 625,000.00, a dataset."""
