"""The federal catalog: Form T936, "Calculation of Cumulative Net Investment Loss (CNIL) to December
31, 2025", the form `ca/t936`.

The form runs once (it has no instances). Its five starting amounts are the printed lines the filer
enters: Part 3 line 15 (the investment expenses of previous years), line 20 (the investment income
of previous years), the 2024 part of line 17 (the amount from line 17218 of Form T2048 for 2024)
and Chart A lines 15 and 16 (boxes 21 and 30 of the 2025 T3 slips). Every other line that computes
is a step of the form that reads the return's figures, so it is a kind of its own; a line that is
another line's amount (Part 3 line 14 is line A, line 19 is line B, Chart A line 10 and line 18 are
rates) has none. The exports are Chart A line 14 and Part 3 line C, which Form T657 Step 1 line 15
and Step 2 line 16 read through `ca/t936.<name>`."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

T936_INVESTMENT_EXPENSES_PREVIOUS_YEARS = CATALOG.declare(
    "t936_investment_expenses_previous_years", Decimal, non_negative=True
)
"""Investment expenses of previous years, T936 Part 3 line 15 "Total investment expenses claimed in
previous years after 1987: Amount from line 16 in Part 3 of Form T936 for 2024 (if you did not
complete Form T936 for 2024, see note (1))": the amount the filer enters, a starting amount."""

T936_INVESTMENT_INCOME_PREVIOUS_YEARS = CATALOG.declare(
    "t936_investment_income_previous_years", Decimal, non_negative=True
)
"""Investment income of previous years, T936 Part 3 line 20 "Total investment income reported in
previous years after 1987: Amount from line 19 of Part 3 of Form T936 for 2024. (if you did not
complete Form T936 for 2024, see note (2))": the amount the filer enters, a starting amount."""

T936_T2048_LINE_17218_FOR_2024 = CATALOG.declare(
    "t936_t2048_line_17218_for_2024", Decimal, non_negative=True
)
"""The 2024 part of T936 Part 3 line 17 "Amount from line 17218 of Form T2048 for 2024 to 2025": the
amount of line 17218 of the Form T2048 for 2024 that the filer enters, a starting amount; the 2025
part is the total of this return's Form T2048."""

T936_T3_BOX_21_CAPITAL_GAINS = CATALOG.declare(
    "t936_t3_box_21_capital_gains", Decimal, non_negative=True
)
"""Box 21 of the 2025 T3 slips, T936 Chart A line 15 (68140) "Enter the amount from box 21 of all
2025 T3 slips.": the amount the filer enters, one total for all the slips, a starting amount."""

T936_T3_BOX_30_CAPITAL_GAINS = CATALOG.declare(
    "t936_t3_box_30_capital_gains", Decimal, non_negative=True
)
"""Box 30 of the 2025 T3 slips, T936 Chart A line 16 "Enter the amount from box 30 of all 2025 T3
slips.": the amount the filer enters, one total for all the slips, a starting amount."""

T936_NET_RENTAL_LOSS = CATALOG.declare("t936_net_rental_loss", Decimal, non_negative=True)
"""Net rental losses, T936 Part 1 line 2 "Net rental losses (line 12600)": the loss in the signed
net rental income of line 12600, 0 when it is a profit."""

T936_PARTNERSHIP_LOSSES = CATALOG.declare("t936_partnership_losses", Decimal, non_negative=True)
"""Partnership losses, T936 Part 1 line 3 "Limited or non-active partnership losses (line 12200)
other than allowable capital losses": the total of the non-active partnership losses."""

T936_EXPLORATION_EXPENSES_AT_HALF = CATALOG.declare(
    "t936_exploration_expenses_at_half", Decimal, non_negative=True
)
"""Exploration and development expenses at 50%, T936 Part 1 line 5 "50% of exploration and
development expenses (line 22400)": line 22400 times the rate of the dataset
`ca/t936_exploration_expenses_rate`."""

T936_OTHER_INVESTMENT_EXPENSES = CATALOG.declare(
    "t936_other_investment_expenses", Decimal, non_negative=True
)
"""Other investment expenses, T936 Part 1 line 6 (68080) "Any other investment expenses claimed in
2025 to earn property income (see the list "Other investment expenses" on the next page)": the
total of the other investment expenses."""

T936_ADDITIONAL_INVESTMENT_EXPENSES = CATALOG.declare(
    "t936_additional_investment_expenses", Decimal, non_negative=True
)
"""Additional investment expenses, T936 Part 1 line 7 "Additional investment expenses: if you did
not complete Chart A on page 4 of this form, enter "0". Otherwise, enter whichever is less: line 20
in Chart A or line 25300 of your return.": the lesser of the two, Chart A always being computed."""

T936_TOTAL_INVESTMENT_EXPENSES = CATALOG.declare(
    "t936_total_investment_expenses", Decimal, non_negative=True
)
"""Total investment expenses claimed in 2025, T936 Part 1 line A "Add lines 1 to 7. Total investment
expenses claimed in 2025": lines 1 to 7, also Part 3 line 14."""

T936_NET_RENTAL_INCOME = CATALOG.declare("t936_net_rental_income", Decimal, non_negative=True)
"""Net rental income, T936 Part 2 line 9 "Net rental income, including recaptured capital cost
allowance (line 12600)": the profit in the signed net rental income of line 12600, 0 when it is a
loss."""

T936_INVESTMENT_INCOME = CATALOG.declare("t936_investment_income", Decimal, non_negative=True)
"""Investment income, T936 Part 2 line 8 "Investment income (lines 12000 and 12100)": the taxable
dividends and the interest and other investment income."""

T936_PARTNERSHIP_TAXABLE_CAPITAL_GAINS = CATALOG.declare(
    "t936_partnership_taxable_capital_gains", Decimal, non_negative=True
)
"""Taxable capital gains in line 12200, the part of T936 Part 2 line 10 "Net income from limited or
non-active partnership (line 12200) other than taxable capital gains" that is taken off: the total
of the partnership taxable capital gains."""

T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS = CATALOG.declare(
    "t936_partnership_income_other_than_gains", Decimal
)
"""Partnership income other than gains, T936 Part 2 line 10 "Net income from limited or non-active
partnership (line 12200) other than taxable capital gains": line 12200 less the taxable capital
gains in it.
The form prints no floor, so it is signed."""

T936_OTHER_PROPERTY_INCOME = CATALOG.declare(
    "t936_other_property_income", Decimal, non_negative=True
)
"""Other property income, T936 Part 2 line 11 (68100) "Any other property income reported in 2025
(see the list "Other property income" on the next page) including annuity payments taxable under
paragraph 56(1)(d) minus the capital portion deducted under paragraph 60(a)": the total of the other
property income."""

T936_EXPLORATION_RECOVERY_INCOME_CHECKED = CATALOG.declare(
    "t936_exploration_recovery_income_checked", Decimal, non_negative=True
)
"""Income from the recovery of exploration and development expenses, checked, T936 Part 2 line 12
(68110) "50% of income from the recovery of exploration and development expenses (line 13000)": the
input `ca/qbt_exploration_recovery_income`, a part of line 13000 "Other income" that may not exceed
that line (`core/at_most`, refused and not capped)."""

T936_RECOVERY_OF_EXPLORATION_EXPENSES = CATALOG.declare(
    "t936_recovery_of_exploration_expenses", Decimal, non_negative=True
)
"""Recovery of exploration and development expenses at 50%, T936 Part 2 line 12 (68110) "50% of
income from the recovery of exploration and development expenses (line 13000)": the checked recovery
income times the rate of the dataset `ca/t936_exploration_recovery_rate`."""

T936_ADDITIONAL_INVESTMENT_INCOME = CATALOG.declare(
    "t936_additional_investment_income", Decimal, non_negative=True
)
"""Additional investment income, T936 Chart A line 20 "Line 14 minus line 19 (if negative, enter
"0") Additional investment income": line 14 less line 19, not below 0; also Part 2 line 13."""

T936_TOTAL_INVESTMENT_INCOME = CATALOG.declare("t936_total_investment_income", Decimal)
"""Total investment income reported in 2025, T936 Part 2 line B "Add lines 8 to 13. Total investment
income reported in 2025": lines 8 to 13, also Part 3 line 19.
The form prints no floor, so it is signed."""

T936_LINE_16 = CATALOG.declare("t936_line_16", Decimal, non_negative=True)
"""Line 16 of Form T936 Part 3, "Line 14 plus line 15": line A plus the investment expenses of
previous years."""

T936_T2048_LINE_17218_FOR_2025 = CATALOG.declare(
    "t936_t2048_line_17218_for_2025", Decimal, non_negative=True
)
"""The 2025 part of T936 Part 3 line 17 "Amount from line 17218 of Form T2048 for 2024 to 2025": the
total over this return's dispositions of line 17218 of Form T2048."""

T936_T2048_LINE_17218 = CATALOG.declare("t936_t2048_line_17218", Decimal, non_negative=True)
"""Line 17 of Form T936 Part 3, "Amount from line 17218 of Form T2048 for 2024 to 2025": the 2024
amount the filer enters plus the total of this return's Form T2048."""

T936_CUMULATIVE_INVESTMENT_EXPENSES = CATALOG.declare(
    "t936_cumulative_investment_expenses", Decimal
)
"""Cumulative investment expenses, T936 Part 3 line 18 "Cumulative investment expenses (line 16
minus line 17)": line 16 less line 17, which may be negative as the form prints no floor."""

T936_CUMULATIVE_INVESTMENT_INCOME = CATALOG.declare("t936_cumulative_investment_income", Decimal)
"""Cumulative investment income, T936 Part 3 line 21 "Cumulative investment income (total of lines
19 and 20)": line B plus the investment income of previous years.
The form prints no floor, so it is signed."""

T936_CNIL = CATALOG.declare("t936_cnil", Decimal, non_negative=True)
"""Cumulative net investment loss, T936 Part 3 line C "Line 18 minus line 21 (if negative, enter
"0") CNIL to December 31, 2025": line 18 less line 21, not below 0. The export Form T657 Step 2
line 16 reads as `ca/t936.t936_cnil`."""

T936_T2048_LINE_17215 = CATALOG.declare("t936_t2048_line_17215", Decimal, non_negative=True)
"""Line 17215 of Form T2048, T936 Chart A line 2 "Amount from line 17215 of Form T2048": the total
over this return's dispositions."""

T936_CHART_A_LINE_3 = CATALOG.declare("t936_chart_a_line_3", Decimal)
"""Line 3 of T936 Chart A, "Line 1 minus line 2": Schedule 3 line 19900 less line 17215 of Form
T2048, which may be negative as the form prints no floor."""

T936_CHART_A_LINE_7 = CATALOG.declare("t936_chart_a_line_7", Decimal)
"""Line 7 of T936 Chart A, "Add lines 4 to 6 (if negative, show in brackets).": Schedule 3 lines
10700, 11000 and 12400, which may be negative."""

T936_T2017_LINE_13 = CATALOG.declare("t936_t2017_line_13", Decimal)
"""The amount on line 13 of Form T2017, read by T936 Chart A line 8: the total of the one record of
the form's export, which may be negative."""

T936_CHART_A_LINE_8_WHEN_POSITIVE = CATALOG.declare("t936_chart_a_line_8_when_positive", Decimal)
"""Line 8 of T936 Chart A for a Schedule 3 line 19200 above 0: the amount on line 13 of Form T2017,
else 0. It is one of the two branches of "If you reported an amount on line 19200 of Schedule 3"
(an amount of more or less than 0), which line 8 adds."""

T936_CHART_A_LINE_8_WHEN_NEGATIVE = CATALOG.declare("t936_chart_a_line_8_when_negative", Decimal)
"""Line 8 of T936 Chart A for a Schedule 3 line 19200 below 0: the amount on line 13 of Form T2017,
else 0. It is one of the two branches of "If you reported an amount on line 19200 of Schedule 3"
(an amount of more or less than 0), which line 8 adds."""

T936_CHART_A_LINE_8 = CATALOG.declare("t936_chart_a_line_8", Decimal)
"""Line 8 of T936 Chart A, "If you reported an amount on line 19200 of Schedule 3, enter the amount
from line 13 of Form T2017, Summary of Reserves on Dispositions of Capital Property (if negative,
show in brackets).": line 13 of Form T2017 when line 19200 is more or less than 0, else 0."""

T936_CHART_A_LINE_9 = CATALOG.declare("t936_chart_a_line_9", Decimal)
"""Line 9 of T936 Chart A, "Line 7 plus line 8 (if negative, show in brackets)": the sum, which may
be negative."""

T936_CHART_A_LINE_9_AT_INCLUSION_RATE = CATALOG.declare(
    "t936_chart_a_line_9_at_inclusion_rate", Decimal
)
"""Line 9 of T936 Chart A at the inclusion rate, "Line 9 multiplied by the percentage on line 10":
line 9 times the rate of the dataset `ca/t936_chart_a_inclusion_rate`, which may be negative; line
11 is its positive part."""

T936_CHART_A_LINE_11 = CATALOG.declare("t936_chart_a_line_11", Decimal, non_negative=True)
"""Line 11 of T936 Chart A, "Line 9 multiplied by the percentage on line 10 (if negative, enter
"0")": the product, not below 0."""

T936_T2048_LINE_17216 = CATALOG.declare("t936_t2048_line_17216", Decimal, non_negative=True)
"""Line 17216 of Form T2048, T936 Chart A line 12 "Amount from line 17216 of Form T2048": the total
over this return's dispositions."""

T936_CHART_A_LINE_13 = CATALOG.declare("t936_chart_a_line_13", Decimal)
"""Line 13 of T936 Chart A, "Line 11 minus line 12": line 11 less line 17216 of Form T2048, which
may be negative as the form prints no floor."""

T936_CHART_A_LINE_14_BEFORE_GATE = CATALOG.declare(
    "t936_chart_a_line_14_before_gate", Decimal, non_negative=True
)
"""Line 14 of T936 Chart A before the gate of line 1, "Line 3 minus line 13 (if negative, enter
"0")": line 3 less line 13, not below 0, which line 1 switches off when it is 0."""

T936_CHART_A_LINE_14_WHEN_LINE_1_POSITIVE = CATALOG.declare(
    "t936_chart_a_line_14_when_line_1_positive", Decimal, non_negative=True
)
"""Line 14 of T936 Chart A for a line 1 above 0: the computed line 14, else 0. It is one of the two
branches of the instruction "If the amount is "0", do not complete lines 2 to 17" of line 1, which
switches line 14 off for a line 1 of 0 only; line 14 adds the two."""

T936_CHART_A_LINE_14_WHEN_LINE_1_NEGATIVE = CATALOG.declare(
    "t936_chart_a_line_14_when_line_1_negative", Decimal, non_negative=True
)
"""Line 14 of T936 Chart A for a line 1 below 0: the computed line 14, else 0. It is one of the two
branches of the instruction "If the amount is "0", do not complete lines 2 to 17" of line 1, which
switches line 14 off for a line 1 of 0 only; line 14 adds the two."""

T936_CHART_A_LINE_14 = CATALOG.declare("t936_chart_a_line_14", Decimal, non_negative=True)
"""Line 14 of T936 Chart A, "Line 3 minus line 13 (if negative, enter "0")" after the instruction of
line 1, "If the amount is "0", do not complete lines 2 to 17, and enter "0" on line 20": the
computed line 14, 0 when line 1 is 0 (the sum of the two branches). The export Form T657 Step 1
line 15 reads as `ca/t936.t936_chart_a_line_14`."""

T936_CHART_A_LINE_17 = CATALOG.declare("t936_chart_a_line_17", Decimal)
"""Line 17 of T936 Chart A (68150), "Line 15 minus line 16": box 21 less box 30 of the 2025 T3
slips, which may be negative as the form prints no floor."""

T936_CHART_A_LINE_19_BEFORE_GATE = CATALOG.declare("t936_chart_a_line_19_before_gate", Decimal)
"""Line 19 of T936 Chart A before the gate of line 14, "Line 17 multiplied by the percentage on line
18": line 17 times the rate of the dataset `ca/t936_t3_inclusion_rate`, which may be negative as the
form prints no floor."""

T936_CHART_A_LINE_19 = CATALOG.declare("t936_chart_a_line_19", Decimal)
"""Line 19 of T936 Chart A after the instruction of line 14, "If the total from line 14 is "0", do
not complete lines 15 to 19, and enter "0" on line 20": the product of lines 17 and 18 when line 14
is more than 0, else 0."""
