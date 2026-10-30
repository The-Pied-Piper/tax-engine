"""The federal catalog: Form T1206, Tax on Split Income, "Dispositions of certain capital property
- shares subject to TOSI" (page 6), the form `ca/t1206_share_dispositions`, and its calculation
of reserve, the form `ca/t1206_share_reserve`, run once for each disposition of the row list.
The starting inputs are lines A, B and F and the row list; the age answer is the return's
existing input `ca/aged_18_or_older_at_end_of_2025`. The row fields are the reserve form's
inputs, the reserve claimed among them. The intermediate kinds are the steps between the inputs and
the exports; the lines and the reserve of each row are the forms' exports."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

T1206_CAPITAL_GAIN_ON_DISPOSITIONS = CATALOG.declare(
    "t1206_capital_gain_on_dispositions", Decimal, non_negative=True
)
"""Capital gain on dispositions in 2025, Form T1206 line A "Capital gain on dispositions in 2025":
the amount the filer enters, a starting amount."""

T1206_RESERVE_2024 = CATALOG.declare("t1206_reserve_2024", Decimal, non_negative=True)
"""Amount of 2024 reserve, Form T1206 line B "Amount of 2024 reserve (from line C of Form T1206 for
2024)": the filer's figure from last year's form, a starting amount."""

T1206_T3_BOX_21_CAPITAL_GAINS = CATALOG.declare(
    "t1206_t3_box_21_capital_gains", Decimal, non_negative=True
)
"""Capital gains from box 21 of the T3 slips, Form T1206 line F "Capital gains from box 21 of your
T3 slip(s) (relating to dispositions in 2025)": the amount the filer enters, a starting amount."""

T1206_RESERVE_CAPITAL_GAIN = CATALOG.declare(
    "t1206_reserve_capital_gain", Decimal, non_negative=True
)
"""Capital gain of a disposition with a reserve, Form T1206 "Calculation of reserve" "(i) Capital
gain x Amount payable after the end of the year / Proceeds of disposition" and "(ii) Capital
gain x Applicable percentage for year of sale or year after sale": a field of each disposition
record."""

T1206_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END = CATALOG.declare(
    "t1206_reserve_amount_payable_after_year_end", Decimal, non_negative=True
)
"""Amount payable after the end of the year, Form T1206 "Calculation of reserve" (i) "Amount
payable after the end of the year": a field of each disposition record."""

T1206_RESERVE_PROCEEDS = CATALOG.declare("t1206_reserve_proceeds", Decimal, non_negative=True)
"""Proceeds of disposition, Form T1206 "Calculation of reserve" (i) "Proceeds of disposition": a
field of each disposition record."""

T1206_RESERVE_YEARS_AFTER_SALE = CATALOG.declare(
    "t1206_reserve_years_after_sale", int, non_negative=True
)
"""Years after the sale, Form T1206 "Calculation of reserve" (ii) "Applicable percentage for year
of sale or year after sale (1)": 0 for the year of sale, 1 for the 1st year, 2 for the 2nd year,
3 for the 3rd year and 4 for the 4th year after the sale, a field of each disposition record."""

T1206_RESERVE_CLAIMED = CATALOG.declare("t1206_reserve_claimed", Decimal, non_negative=True)
"""Reserve claimed for a disposition, Form T1206 "Calculation of reserve" "Complete this calculation
and include the total amount of your 2025 reserve on line C above" and "Your reserve in each year
cannot be more than whichever of the following two calculations is less": the filer's election,
the reserve claimed for the disposition, up to the maximum of the two calculations, a field of
each disposition record."""

T1206_SHARE_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t1206_share_reserve_rows",
    fields=(
        T1206_RESERVE_CAPITAL_GAIN,
        T1206_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T1206_RESERVE_PROCEEDS,
        T1206_RESERVE_YEARS_AFTER_SALE,
        T1206_RESERVE_CLAIMED,
    ),
)
"""Dispositions with a reserve, Form T1206 page 6 "Calculation of reserve" "Complete this
calculation and include the total amount of your 2025 reserve on line C above": one record for
each disposition, holding its capital gain, amount payable after the end of the year, proceeds
of disposition, years after the sale and the reserve claimed. The form runs once for each record
(`ca/t1206_share_reserve`); the caller lists only the dispositions with a reserve, and none
is an empty list."""

T1206_RESERVE_PAYABLE_CHECKED = CATALOG.declare(
    "t1206_reserve_payable_checked", Decimal, non_negative=True
)
"""Amount payable after the end of the year of a disposition, checked, Form T1206 "Calculation of
reserve" (i) "Amount payable after the end of the year" over "Proceeds of disposition": the
amount payable, refused above the proceeds (the form prints no bound), which the form passes on."""

T1206_RESERVE_BY_PAYMENT = CATALOG.declare("t1206_reserve_by_payment", Decimal, non_negative=True)
"""Calculation (i) of a disposition's reserve, Form T1206 "Calculation of reserve" "(i) Capital
gain x Amount payable after the end of the year / Proceeds of disposition", rounded half-up to
the cent once, zero when the proceeds are zero."""

T1206_RESERVE_APPLICABLE_PERCENTAGE = CATALOG.declare(
    "t1206_reserve_applicable_percentage", Decimal, non_negative=True
)
"""Applicable percentage for year of sale or year after sale, Form T1206 "Calculation of reserve"
"(ii) Capital gain x Applicable percentage for year of sale or year after sale (1)": 80% for the
year of sale, 60% for the 1st year, 40% for the 2nd year, 20% for the 3rd year and 0% for the
4th year, as the percentage figure (80 is 80%)."""

T1206_RESERVE_BY_PERCENTAGE = CATALOG.declare(
    "t1206_reserve_by_percentage", Decimal, non_negative=True
)
"""Calculation (ii) of a disposition's reserve, Form T1206 "Calculation of reserve" "(ii) Capital
gain x Applicable percentage for year of sale or year after sale (1)", rounded half-up to the
cent once."""

T1206_RESERVE_MAXIMUM = CATALOG.declare("t1206_reserve_maximum", Decimal, non_negative=True)
"""Maximum reserve of a disposition, Form T1206 "Calculation of reserve" "Your reserve in each year
cannot be more than whichever of the following two calculations is less": the lesser of (i) and
(ii), the most the reserve claimed for the disposition can be."""

T1206_ROW_RESERVE = CATALOG.declare("t1206_row_reserve", Decimal, non_negative=True)
"""Reserve of a disposition, Form T1206 "Calculation of reserve" "Complete this calculation and
include the total amount of your 2025 reserve on line C above": the reserve claimed, up to the
maximum, which the form adds to line C for that disposition. A claim above the maximum is refused,
not capped."""

T1206_AGED_18_OR_OLDER_CHECKED = CATALOG.declare(
    "t1206_aged_18_or_older_checked", int, non_negative=True
)
"""Age answer of Form T1206 page 6, checked, "If you were under 18 years of age at the end of the
year" and "If you were 18 years of age or older at the end of the year": 0 for under 18 and 1
for 18 or older, a count above 1 refused, which the form's two branches read."""

T1206_LINE_C = CATALOG.declare("t1206_line_c", Decimal, non_negative=True)
"""Amount of 2025 reserve, Form T1206 line C "Amount of 2025 reserve (calculated below)": the total
of the reserves of all the dispositions of the row list."""

T1206_LINES_A_AND_B = CATALOG.declare("t1206_lines_a_and_b", Decimal, non_negative=True)
"""Lines A and B of Form T1206 page 6, "Capital gain on dispositions in 2025" and "Amount of 2024
reserve (from line C of Form T1206 for 2024)": their sum, the most that line C can be."""

T1206_LINE_C_CHECKED = CATALOG.declare("t1206_line_c_checked", Decimal, non_negative=True)
"""Amount of 2025 reserve, checked, Form T1206 line C "Amount of 2025 reserve (calculated below)":
the line C amount, refused above the sum of lines A and B (the form prints no bound), which line
D reads."""

T1206_LINE_D = CATALOG.declare("t1206_line_d", Decimal)
"""Line D of Form T1206 page 6, "Line B minus line C (if negative, show in brackets)": the amount
of line B less the checked line C, which may be negative (the form prints no floor)."""

T1206_LINE_E = CATALOG.declare("t1206_line_e", Decimal, non_negative=True)
"""Net capital gain, Form T1206 line E "Line A plus line D Net capital gain": line A plus line D,
which is never below zero as line C is checked against lines A and B."""

T1206_LINE_G = CATALOG.declare("t1206_line_g", Decimal, non_negative=True)
"""Line G of Form T1206 page 6, "Line E plus line F": the net capital gain plus the box 21 capital
gains of the T3 slips. It feeds the under-18 dividend amount and the Part 1 line 3 amount."""

T1206_UNDER_18_PERCENT = CATALOG.declare("t1206_under_18_percent", Decimal, non_negative=True)
"""Percentage of line G for a filer under 18, Form T1206 page 6 "If you were under 18 years of age
at the end of the year, the amount at line G is deemed to be a dividend (other than eligible
dividend). Multiply the amount from line G by 1.15": 115 for 1.15 (115%) under 18, and 0 for 18
or older."""

T1206_UNDER_18_DIVIDEND_AMOUNT = CATALOG.declare(
    "t1206_under_18_dividend_amount", Decimal, non_negative=True
)
"""Amount deemed to be a dividend, Form T1206 page 6 "Multiply the amount from line G by 1.15 and
include this amount under "Taxable amount of dividends (eligible and other than eligible)" on
the Federal Worksheet, and on lines 12000 and 12010 of your return": line G at the under-18
percentage, rounded half-up to the cent once, zero for a filer 18 or older."""

T1206_PART_1_LINE_3_PERCENT = CATALOG.declare(
    "t1206_part_1_line_3_percent", Decimal, non_negative=True
)
"""Percentage of the capital gains for a filer 18 or older, Form T1206 page 6 "multiply the capital
gain for each disposition reported on lines A, B, C and F by 50%": 50 for 50% for a filer 18 or
older, and 0 for under 18."""

T1206_PART_1_LINE_3_AMOUNT = CATALOG.declare(
    "t1206_part_1_line_3_amount", Decimal, non_negative=True
)
"""Part 1 line 3 amount, Form T1206 page 6 "multiply the capital gain for each disposition reported
on lines A, B, C and F by 50% and enter the total on line 3 in Part 1 on page 7": 50% of line G
(the capital gains of lines A, B, C and F), rounded half-up to the cent once, zero for a filer
under 18."""
