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
"""Deductions from net income, T1 line 68 and line 25700 "Add lines 58 to 67.": in the take-home, an
optional input (`t1_taxable_income_line_25700_inputs.yaml`, default "0"). None of lines 24400 to
25600 applies to a salary-only filer, and line 26000 takes it off net income.
"""

TAXABLE_INCOME = AmountKind.declare(CATALOG, "taxable_income", non_negative=True)
"""Taxable income, T1 line 69 "Line 57 minus line 68 (if negative, enter "0") Taxable income"
(line 26000, as Step 5 refers to it): net income less the deductions from net income, not below
zero; the base the federal and Ontario brackets apply to.

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
