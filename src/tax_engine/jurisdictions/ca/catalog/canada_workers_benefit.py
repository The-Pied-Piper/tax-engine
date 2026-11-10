"""The federal catalog: the Canada workers benefit.

The Canada workers benefit lines.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

CWB_EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "cwb_employment_income", non_negative=True)
"""Employment income for the Canada workers benefit, Schedule 6 line 1 "Employment income and other
employment income from line 10100 and line 10400 of the return": the employment income and the
other employment income added. The take-home sum has the salary alone (line 10400 is out of
scope). The quote is from Schedule 6 (5000-S6)."""

WORKING_INCOME = AmountKind.declare(CATALOG, "working_income", non_negative=True)
"""Working income, Schedule 6 line 5 "Add lines 1 to 4. Enter the result, even if it is "0".
Working income". The take-home sum has line 1 only: line 1 "Employment income and other employment
income from line 10100 and line 10400 of the return" (the employment income and the other
employment income, see CWB_EMPLOYMENT_INCOME). Lines 2 "Taxable scholarships, fellowships,
bursaries, and artists' project grants from line 13010 of the return", 3 "Total self-employment
income from lines 13500, 13700, 13900, 14100, and 14300 of the return (excluding losses) (Note 2)",
and 4 "Tax-exempt working income earned on a reserve" (`ca/cwb_tax_exempt_working_income`) are not
built, so they are not added here.

This is column 1 ("You") only; line 6 "Add the amounts from line 5 in columns 1 and 2. Enter this
amount on line 16. Family working income" adds column 2 (`ca/cwb_spouse_working_income`), see
`ca/cwb_family_working_income`."""

CWB_NET_INCOME_LINE_7 = AmountKind.declare(CATALOG, "cwb_net_income_line_7", non_negative=False)
"""Your column, Schedule 6 line 7 "Net income from line 23600 of the return (or the amount you would
have entered if the instructions on line 23600 said "if negative, show in brackets")": the net
income of the T1 return before its floor, read from the signed T1 net income export
(`ca/net_income_signed`, not the floored `ca/net_income`). Column 1 ("You") only; line 7 of
column 2 is for the eligible spouse. The form asks for the amount with a negative shown in
brackets, so the kind is signed."""

CWB_NET_INCOME_TOTAL_LINE_10 = AmountKind.declare(CATALOG, "cwb_net_income_total_line_10")
"""Your column, Schedule 6 Part B line 10 "Add lines 7 to 9.": the net income of line 7 "Net income
from line 23600 of the return (or the amount you would have entered if the instructions on line
23600 said "if negative, show in brackets")" (here the signed T1 net income, `ca/net_income_signed`;
Form T1206 is not built), plus lines 8 and 9. Line 8 is "Total of net exempt income earned on a
reserve" (`ca/cwb_tax_exempt_net_income`, zero unless the election is yes), and line 9 is "Total of
universal child care benefit (UCCB) repayment (line 21300 of the return) and registered disability
savings plan (RDSP) income repayment (included on line 23200 of the return)" (the UCCB and RDSP
income repayments of the other payments worksheet). The take-home calculator builds only line 7 and
does not add lines 8 and 9. The form prints no "(if negative, enter "0")" on line 10, so the kind is
signed."""

CWB_NET_INCOME_LESS_UCCB_RDSP_LINE_12 = AmountKind.declare(
    CATALOG, "cwb_net_income_less_uccb_rdsp_line_12", non_negative=True
)
"""Your column, Schedule 6 Part B line 12 "Line 10 minus line 11 (if negative, enter "0")": line 11
is "Total of UCCB (line 11700 of the return) and RDSP income (line 12500 of the return)" (the UCCB
and RDSP income of the other payments worksheet)."""

CWB_FAMILY_WORKING_INCOME = AmountKind.declare(
    CATALOG, "cwb_family_working_income", non_negative=True
)
"""Family working income, Schedule 6 Part A line 6 "Add the amounts from line 5 in columns 1 and 2.
Enter this amount on line 16. Family working income". The take-home sum has line 5 of column 1
(`ca/working_income`) only; column 2 (`ca/cwb_spouse_working_income`) is not built, so it is not
added here."""

CWB_FAMILY_NET_INCOME_LINE_13 = AmountKind.declare(
    CATALOG, "cwb_family_net_income_line_13", non_negative=True
)
"""Schedule 6 Part B line 13 "Add the amounts from line 12 in columns 1 and 2. If you had an
eligible spouse, continue at line 14; if not, continue at line 15.": the line 12 of column 1
(`ca/cwb_net_income_less_uccb_rdsp_line_12`) alone. Column 2, the eligible spouse's line 12
(`ca/cwb_spouse_net_income_less_uccb_rdsp_line_12`), is not built: the take-home calculator is single."""

CWB_SECONDARY_EARNER_EXEMPTION = AmountKind.declare(
    CATALOG, "cwb_secondary_earner_exemption", non_negative=True
)
"""Schedule 6 line 14 "Secondary earner exemption (maximum $16,386)" as an input: the optional input
of schedule_6_line_14_inputs.yaml, left out by the salary-only caller and read as 0 by line 15
(blank rule of core/subtract). Nothing caps it: the printed maximum $16,386 is not applied (a single
filer never fills the line)."""

ADJUSTED_FAMILY_NET_INCOME = AmountKind.declare(CATALOG, "adjusted_family_net_income")
"""Adjusted family net income, Schedule 6 line 15 "Line 13 minus line 14 Enter this amount on line
23 and line 35. Adjusted family net income": line 13 (`ca/cwb_family_net_income_line_13`) less line
14 (`ca/cwb_secondary_earner_exemption`, 0 with no eligible spouse). Signed: the form prints no "if
negative, enter 0" on this line."""

CWB_REDUCTION_THRESHOLD = AmountKind.declare(CATALOG, "cwb_reduction_threshold", non_negative=True)
"""Canada workers benefit reduction threshold, Schedule 6 line 24 "If you had an eligible spouse or
an eligible dependant, enter $30,639. If not, enter $26,855.": the base amount for a filer with no
eligible spouse and no eligible dependant, here $26,855, the printed figure taken whole. Line 25
takes it as line 24, "Line 23 minus line 24 (if negative, enter "0")"."""

CWB_BASE_AMOUNT = AmountKind.declare(CATALOG, "cwb_base_amount", non_negative=True)
"""Schedule 6 line 17 "Base amount 3,000.00": the $3,000 base amount of the Canada workers benefit,
a dataset figure, claimed whole."""

CWB_WORKING_INCOME_OVER_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "cwb_working_income_over_base_amount", non_negative=True
)
"""Schedule 6 Step 2 (Basic CWB) line 18 "Line 16 minus line 17 (if negative, enter "0")": line 16
(a copy of line 6, `ca/cwb_family_working_income`) less line 17 (`ca/cwb_base_amount`), floored at
zero."""

CWB_WORKING_INCOME_RATE_LINE_20 = AmountKind.declare(
    CATALOG, "cwb_working_income_rate_line_20", non_negative=True
)
"""Schedule 6 line 20 "Line 18 multiplied by the percentage from line 19": line 18
(`ca/cwb_working_income_over_base_amount`) times the 27% of line 19 (`ca/cwb_rate`), to the cent."""

CWB_BASIC_BENEFIT_LINE_22 = AmountKind.declare(
    CATALOG, "cwb_basic_benefit_line_22", non_negative=True
)
"""Schedule 6 line 22 "Enter whichever is less: amount from line 20 or line 21.": the lesser of
line 20 (`ca/cwb_working_income_rate_line_20`) and line 21 (`ca/cwb_maximum`), the basic CWB before
reduction."""

CWB_NET_INCOME_OVER_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "cwb_net_income_over_base_amount", non_negative=True
)
"""Schedule 6 Step 2 (Basic CWB) line 25 "Line 23 minus line 24 (if negative, enter "0")": line 23
(a copy of line 15, `ca/adjusted_family_net_income`) less line 24 (`ca/cwb_reduction_threshold`),
floored at zero."""

CWB_REDUCTION_LINE_27 = AmountKind.declare(CATALOG, "cwb_reduction_line_27", non_negative=True)
"""Schedule 6 line 27 "Line 25 multiplied by the percentage from line 26": line 25
(`ca/cwb_net_income_over_base_amount`) times the 15% of line 26 (`ca/cwb_reduction_rate`), to the
cent."""

CWB_BENEFIT_LINE_28 = AmountKind.declare(CATALOG, "cwb_benefit_line_28", non_negative=True)
"""Schedule 6 line 28 "Line 22 minus line 27 (if negative, enter "0")": line 22
(`ca/cwb_basic_benefit_line_22`) less line 27 (`ca/cwb_reduction_line_27`), floored at zero. If
you are not completing Step 3, the form has this amount go to T1 line 45300."""

CWB_MAXIMUM = AmountKind.declare(CATALOG, "cwb_maximum", non_negative=True)
"""Schedule 6 line 21 "If you had an eligible spouse or an eligible dependant, enter $2,813. If not,
enter $1,633.": the $1,633 maximum benefit for a filer with no eligible spouse or dependant, claimed
whole, a dataset figure."""
