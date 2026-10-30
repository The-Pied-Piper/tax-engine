"""The federal catalog: Form T2017 (2025), "Summary of Reserves on Dispositions of Capital
Property", Part 1 (pages 1 and 2), in ten row forms and one summary form. The row forms are
`ca/t2017_line_N_reserve` for the reserve lines N that take a list of dispositions (2, 3, 4, 8,
9, 10, 17, 21, 24 and 27), each run once for each record of its list
`ca/t2017_line_N_reserve_rows`. The record fields are the reserve calculation's inputs; only the
records of lines 2 and 8 hold the nine-year answer. The summary form `ca/t2017` is run once: it
adds the lines of Part 1. The starting inputs are the 2024 figures of lines 1, 7, 16, 20, 23 and
30, and the 2024 figure that line 26 is computed from; line 14 is entered and read by no step. The
intermediate kinds are the steps of the calculation of reserve; the claim of each
row (`ca/t2017_row_reserve`) and the lines of the summary are the forms' exports."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

T2017_LINE_1 = CATALOG.declare("t2017_line_1", Decimal, non_negative=True)
"""Amount of 2024 reserve, Form T2017 line 1 "Amount of 2024 reserve for dispositions of QFFP to
your child after 2015, under a qualifying business transfer (QBT) after 2023 or a qualifying
cooperative conversion (QCC) after 2023, and all other dispositions of QFFP after 2020 (lines
66844 and 67055 of Form T2017 for 2024)": the filer's figure from last year's form, a starting
amount."""

T2017_LINE_7 = CATALOG.declare("t2017_line_7", Decimal, non_negative=True)
"""Amount of 2024 reserve, Form T2017 line 7 "Amount of 2024 reserve for dispositions of QSBCS to
your child after 2015, under a QBT after 2023 or QCC after 2023, and all other dispositions of
QSBCS after 2020 (lines 66850 and 67056 of Form T2017 for 2024)": the filer's figure from last
year's form, a starting amount."""

T2017_LINE_16 = CATALOG.declare("t2017_line_16", Decimal, non_negative=True)
"""Amount of 2024 reserve, Form T2017 line 16 "Amount of 2024 reserve for dispositions of family
farm or fishing property to your child after 2015 (other than QFFP) (lines 66920 and 67057 of
Form T2017 for 2024)": the filer's figure from last year's form, a starting amount."""

T2017_LINE_20 = CATALOG.declare("t2017_line_20", Decimal, non_negative=True)
"""Amount of 2024 reserve, Form T2017 line 20 "Amount of 2024 reserve for dispositions of property
under a QBT (other than QFFP and QSBCS) after 2023 (lines 66935 and 66839 of Form T2017 for
2024)": the filer's figure from last year's form, a starting amount."""

T2017_LINE_23 = CATALOG.declare("t2017_line_23", Decimal, non_negative=True)
"""Amount of 2024 reserve, Form T2017 line 23 "Amount of 2024 reserve for dispositions of property
under a QCC (other than QFFP and QSBCS) after 2023": the filer's figure from last year's form, a
starting amount."""

T2017_LINES_66990_AND_67058_FOR_2024 = CATALOG.declare(
    "t2017_lines_66990_and_67058_for_2024", Decimal, non_negative=True
)
"""Amount of 2024 reserve, Form T2017 line 26 "Amount of 2024 reserve for dispositions of property
after 2020, other than dispositions listed on lines 66843, 66883, 66910, and 66930 (lines 66990
and 67058 of Form T2017 for 2024)": the filer's figure from last year's form, a starting amount
that line 26 of the 2025 form is computed from (less line 23)."""

T2017_LINE_14 = CATALOG.declare("t2017_line_14", Decimal, non_negative=True)
"""Line 14 of Form T2017 page 1 "Enter the amount of the most recent reserves claimed on line
66850." (complete line 66905 "Complete line 66905 only if you are reporting or claiming reserves on
line 66883, line 66850, or both for at least two dispositions of QSBCS that originated in more than
one year after 2015."): the amount the filer enters; no step of the form reads it."""

T2017_LINE_30 = CATALOG.declare("t2017_line_30", Decimal, non_negative=True)
"""Amount of 2024 reserve, Form T2017 line 30 "Amount of 2024 reserve for dispositions before
November 13, 1981 (as reported in 2024)": the filer's figure from last year's form, a starting
amount, entered only for a disposition before November 13, 1981."""

T2017_RESERVE_CAPITAL_GAIN = CATALOG.declare(
    "t2017_reserve_capital_gain", Decimal, non_negative=True
)
"""Capital gain of a disposition with a reserve, Form T2017 page 3 "Calculation of reserve" "(i)
Capital gain ×" and "(ii) Capital gain ×": a field of each disposition record."""

T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END = CATALOG.declare(
    "t2017_reserve_amount_payable_after_year_end", Decimal, non_negative=True
)
"""Amount payable after the end of the year, Form T2017 page 3 "Amount payable to you after the end
of the year" over "Proceeds of disposition": a field of each disposition record."""

T2017_RESERVE_PROCEEDS = CATALOG.declare("t2017_reserve_proceeds", Decimal, non_negative=True)
"""Proceeds of disposition, Form T2017 page 3 "Proceeds of disposition": a field of each
disposition record."""

T2017_RESERVE_YEARS_AFTER_DISPOSITION = CATALOG.declare(
    "t2017_reserve_years_after_disposition", int, non_negative=True
)
"""Years after the disposition, Form T2017 page 3 "Year of disposition (A)" and "Year after the
disposition (B)": 0 for the year of disposition, 1 for the 1st year, 2 for the 2nd year and so
on to the 9th year, a field of each disposition record."""

T2017_RESERVE_CLAIMED = CATALOG.declare("t2017_reserve_claimed", Decimal, non_negative=True)
"""Reserve claimed for a disposition, Form T2017 page 3 "Your reserve for the year cannot be more
than the lesser of the following": the filer's election, the reserve claimed for the
disposition, up to the maximum of the two calculations, a field of each disposition record."""

T2017_RESERVE_PREVIOUS_YEAR_CLAIM = CATALOG.declare(
    "t2017_reserve_previous_year_claim", Decimal, non_negative=True
)
"""Reserve claimed for the property in the previous year, Form T2017 page 3 "However, the amount you
claim in a later year (Year B) cannot be more than the amount you claimed for that property in the
previous year (Year A)": the filer's figure for the property's reserve in the year before, a field
of each disposition record, read only in a later year; it is not read for a disposition in 2025."""

T2017_RESERVE_PERIOD_1_OF_2024 = CATALOG.declare(
    "t2017_reserve_period_1_of_2024", int, non_negative=True
)
"""Disposed of in Period 1 of 2024, Form T657 Chart 2024 and Chart 2025 "do not include reserves
from dispositions of QFFP in any year or period other than Period 1 of 2024" (Period 1 is before
June 25, 2024, Period 2 is June 25, 2024 to December 31, 2024): 1 if the disposition was made in
Period 1 of 2024, else 0, a field of each record of lines 2, 3, 4, 8, 9 and 10, which Form T657
reads; Form T2017 does not ask it."""

T2017_RESERVE_REPORTED_ON_SLIP = CATALOG.declare(
    "t2017_reserve_reported_on_slip", int, non_negative=True
)
"""Reserve reported on a T5013 slip or letter, Form T657 Chart 2025 Part 1 "only include reserves
reported on a T5013 slip or letter from dispositions of QFFP for Period 1 of 2024": 1 if the
reserve of the disposition is reported on a T5013 slip or in a letter to the partner, else 0, a
field of each record of lines 2, 3, 4, 8, 9 and 10, which Form T657 reads; Form T2017 does not ask
it."""

T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024 = CATALOG.declare(
    "t2017_reserve_partnership_year_began_before_june_25_2024", int, non_negative=True
)
"""Partnership year began before June 25, 2024, Guide T4037 (Capital gains deduction): for capital
gains reported by a partnership whose fiscal period begins before June 25, 2024 and ends on or
after January 1, 2025, and which disposed of QFFP or QSBCS in Period 1 of 2024, "you must use Part 1
of Chart 2025"; for a partnership whose fiscal period begins after June 25, 2024 and that indicates
the gains relate to a reserve claimed in 2024 for a disposition before June 25, 2024, "you must use
Period 1 of Chart 2024": 1 if the partnership's fiscal period began before June 25, 2024, else 0,
a field of each record of lines 2, 3, 4, 8, 9 and 10, read only for a disposition in Period 1 of
2024 whose reserve is reported on a T5013 slip or letter (the 2025 slip of Chart 2025 Part 1, so the
fiscal period ends after 2024); Form T2017 does not ask it. The Guide prints neither case for a
fiscal period that begins on June 25, 2024: the answer 0 sends it to Chart 2024 Period 1."""

T2017_RESERVE_NINE_YEAR = CATALOG.declare("t2017_reserve_nine_year", int, non_negative=True)
"""Nine-year answer of a disposition, Form T2017 page 3 "You can claim a reserve up to a maximum of
nine years" for "Family farm or fishing property and small business corporation shares disposed
of to your child, or disposition under a QBT or QCC": 1 for that kind, which takes the nine-year
table, and 0 for the four-year rule, a field of each record of lines 2 and 8 only."""

T2017_LINE_2_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_2_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
        T2017_RESERVE_PERIOD_1_OF_2024,
        T2017_RESERVE_REPORTED_ON_SLIP,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
        T2017_RESERVE_NINE_YEAR,
    ),
)
"""Dispositions with a reserve on line 2, Form T2017 page 1 "Amount of 2025 reserve for
dispositions of QFFP to your child after 2016, and all other dispositions of QFFP after 2021
other than QBT or QCC": one record for each disposition, holding its capital gain, amount
payable after the end of the year, proceeds of disposition, years after the disposition, the
reserve claimed, the reserve claimed for the property in the previous year and the nine-year
answer, "Family farm or fishing property and small business corporation shares disposed of to
your child, or disposition under a QBT or QCC". The form runs once for each record
(`ca/t2017_line_2_reserve`); the caller lists only the dispositions with a reserve (one with a 2024
reserve of which
nothing is claimed in 2025 is listed with a claim of 0), and none is an empty list.
Each record also holds the three yes or no answers that Form T657 and Guide T4037 read
(`ca/t2017_reserve_period_1_of_2024`, `ca/t2017_reserve_reported_on_slip` and
`ca/t2017_reserve_partnership_year_began_before_june_25_2024`)."""

T2017_LINE_3_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_3_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
        T2017_RESERVE_PERIOD_1_OF_2024,
        T2017_RESERVE_REPORTED_ON_SLIP,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    ),
)
"""Dispositions with a reserve on line 3, Form T2017 page 1 "Amount of 2025 reserve for
dispositions of QFFP under a QBT after 2023": one record for each disposition, holding its
capital gain, amount payable after the end of the year, proceeds of disposition, years after the
disposition, the reserve claimed and the reserve claimed for the property in the previous year.
The form runs once for each record (`ca/t2017_line_3_reserve`); none is an empty list.
Each record also holds the three yes or no answers that Form T657 and Guide T4037 read
(`ca/t2017_reserve_period_1_of_2024`, `ca/t2017_reserve_reported_on_slip` and
`ca/t2017_reserve_partnership_year_began_before_june_25_2024`)."""

T2017_LINE_4_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_4_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
        T2017_RESERVE_PERIOD_1_OF_2024,
        T2017_RESERVE_REPORTED_ON_SLIP,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    ),
)
"""Dispositions with a reserve on line 4, Form T2017 page 1 "Amount of 2025 reserve for
dispositions of QFFP under a QCC after 2023": one record for each disposition, holding its
capital gain, amount payable after the end of the year, proceeds of disposition, years after the
disposition, the reserve claimed and the reserve claimed for the property in the previous year.
The form runs once for each record (`ca/t2017_line_4_reserve`); none is an empty list.
Each record also holds the three yes or no answers that Form T657 and Guide T4037 read
(`ca/t2017_reserve_period_1_of_2024`, `ca/t2017_reserve_reported_on_slip` and
`ca/t2017_reserve_partnership_year_began_before_june_25_2024`)."""

T2017_LINE_8_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_8_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
        T2017_RESERVE_PERIOD_1_OF_2024,
        T2017_RESERVE_REPORTED_ON_SLIP,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
        T2017_RESERVE_NINE_YEAR,
    ),
)
"""Dispositions with a reserve on line 8, Form T2017 page 1 "Amount of 2025 reserve for
dispositions of QSBCS to your child after 2016 and all other dispositions of QSBCS other than a
QBT or QCC after 2021": one record for each disposition, holding its capital gain, amount
payable after the end of the year, proceeds of disposition, years after the disposition, the
reserve claimed, the reserve claimed for the property in the previous year and the nine-year
answer, "Family farm or fishing property and small business corporation shares disposed of to
your child, or disposition under a QBT or QCC". The form runs once for each record
(`ca/t2017_line_8_reserve`); none is an empty list.
Each record also holds the three yes or no answers that Form T657 and Guide T4037 read
(`ca/t2017_reserve_period_1_of_2024`, `ca/t2017_reserve_reported_on_slip` and
`ca/t2017_reserve_partnership_year_began_before_june_25_2024`)."""

T2017_LINE_9_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_9_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
        T2017_RESERVE_PERIOD_1_OF_2024,
        T2017_RESERVE_REPORTED_ON_SLIP,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    ),
)
"""Dispositions with a reserve on line 9, Form T2017 page 1 "Amount of 2025 reserve for
dispositions of QSBCS under a QBT after 2023": one record for each disposition, holding its
capital gain, amount payable after the end of the year, proceeds of disposition, years after the
disposition, the reserve claimed and the reserve claimed for the property in the previous year.
The form runs once for each record (`ca/t2017_line_9_reserve`); none is an empty list.
Each record also holds the three yes or no answers that Form T657 and Guide T4037 read
(`ca/t2017_reserve_period_1_of_2024`, `ca/t2017_reserve_reported_on_slip` and
`ca/t2017_reserve_partnership_year_began_before_june_25_2024`)."""

T2017_LINE_10_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_10_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
        T2017_RESERVE_PERIOD_1_OF_2024,
        T2017_RESERVE_REPORTED_ON_SLIP,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    ),
)
"""Dispositions with a reserve on line 10, Form T2017 page 1 "Amount of 2025 reserve for
dispositions of QSBCS under a QCC after 2023": one record for each disposition, holding its
capital gain, amount payable after the end of the year, proceeds of disposition, years after the
disposition, the reserve claimed and the reserve claimed for the property in the previous year.
The form runs once for each record (`ca/t2017_line_10_reserve`); none is an empty list.
Each record also holds the three yes or no answers that Form T657 and Guide T4037 read
(`ca/t2017_reserve_period_1_of_2024`, `ca/t2017_reserve_reported_on_slip` and
`ca/t2017_reserve_partnership_year_began_before_june_25_2024`)."""

T2017_LINE_17_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_17_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    ),
)
"""Dispositions with a reserve on line 17, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of family farm or fishing property to your child (other than QFFP) after 2016": one
record for each disposition, holding its capital gain, amount payable after the end of the year,
proceeds of disposition, years after the disposition and the reserve claimed, the reserve
claimed for the property in the previous year. The form runs once for each record
(`ca/t2017_line_17_reserve`); none is an empty list."""

T2017_LINE_21_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_21_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    ),
)
"""Dispositions with a reserve on line 21, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of property under a QBT (other than QFFP and QSBCS) after 2023": one record for
each disposition, holding its capital gain, amount payable after the end of the year, proceeds
of disposition, years after the disposition and the reserve claimed, the reserve claimed for the
property in the previous year. The form runs once for each record (`ca/t2017_line_21_reserve`);
none is an empty list."""

T2017_LINE_24_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_24_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    ),
)
"""Dispositions with a reserve on line 24, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of property under a QCC (other than QFFP and QSBCS) after 2023": one record for
each disposition, holding its capital gain, amount payable after the end of the year, proceeds
of disposition, years after the disposition and the reserve claimed, the reserve claimed for the
property in the previous year. The form runs once for each record (`ca/t2017_line_24_reserve`);
none is an empty list."""

T2017_LINE_27_RESERVE_ROWS = RecordListKind.declare(
    CATALOG,
    "t2017_line_27_reserve_rows",
    fields=(
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_YEARS_AFTER_DISPOSITION,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    ),
)
"""Dispositions with a reserve on line 27, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of property after 2021, other than dispositions listed on lines 66844, 66850,
66920, 66935, and 66939": one record for each disposition, holding its capital gain, amount
payable after the end of the year, proceeds of disposition, years after the disposition, the
reserve claimed and the reserve claimed for the property in the previous year. The form runs once
for each record (`ca/t2017_line_27_reserve`); none is an empty list."""

T2017_RESERVE_NINE_YEAR_CHECKED = CATALOG.declare(
    "t2017_reserve_nine_year_checked", int, non_negative=True
)
"""Nine-year answer of a disposition, checked, Form T2017 page 3 "Family farm or fishing property
and small business corporation shares disposed of to your child, or disposition under a QBT or
QCC": 0 for the four-year rule and 1 for the nine-year rule, a count above 1 refused, which the
form's two calculations read."""

T2017_RESERVE_LATER_YEAR = CATALOG.declare("t2017_reserve_later_year", int, non_negative=True)
"""Later-year answer of a disposition, Form T2017 page 3 "the amount you claim in a later year (Year
B)": 1 for a year after the year of disposition (a count of years after the disposition above 0),
and 0 for the year of disposition (Year A) itself."""

T2017_RESERVE_PAYABLE_CHECKED = CATALOG.declare(
    "t2017_reserve_payable_checked", Decimal, non_negative=True
)
"""Amount payable after the end of the year of a disposition, checked, Form T2017 page 3 "Amount
payable to you after the end of the year" over "Proceeds of disposition": the amount payable,
refused above the proceeds (the form prints no bound), which the form passes on."""

T2017_RESERVE_BY_PAYMENT = CATALOG.declare("t2017_reserve_by_payment", Decimal, non_negative=True)
"""Calculation (i) of a disposition's reserve, Form T2017 page 3 "(i) Capital gain × Amount payable
to you after the end of the year / Proceeds of disposition", rounded half-up to the cent once,
zero when the proceeds are zero."""

T2017_RESERVE_FOUR_YEAR_PERCENTAGE = CATALOG.declare(
    "t2017_reserve_four_year_percentage", Decimal, non_negative=True
)
"""Applicable percentage of a disposition with a four-year maximum, Form T2017 page 3 "Enter the
applicable percentage from the table": 80% for the year of disposition (A), 60% for the 1st
year, 40% for the 2nd year, 20% for the 3rd year and zero for the 4th year, as the percentage
figure (80 is 80%)."""

T2017_RESERVE_NINE_YEAR_PERCENTAGE = CATALOG.declare(
    "t2017_reserve_nine_year_percentage", Decimal, non_negative=True
)
"""Applicable percentage of a disposition with a nine-year maximum, Form T2017 page 3 "Enter the
applicable percentage from the table": 90% for the year of disposition (A), 80% for the 1st
year, 70% for the 2nd year, 60% for the 3rd year, 50% for the 4th year, 40% for the 5th year,
30% for the 6th year, 20% for the 7th year, 10% for the 8th year and zero for the 9th year, as
the percentage figure (90 is 90%)."""

T2017_RESERVE_APPLICABLE_PERCENTAGE = CATALOG.declare(
    "t2017_reserve_applicable_percentage", Decimal, non_negative=True
)
"""Applicable percentage of a disposition, Form T2017 page 3 "(ii) Capital gain × Enter the
applicable percentage from the table": the percentage of the table that the disposition takes,
by its maximum period and its years after the disposition, as the percentage figure (80 is 80%)."""

T2017_RESERVE_BY_PERCENTAGE = CATALOG.declare(
    "t2017_reserve_by_percentage", Decimal, non_negative=True
)
"""Calculation (ii) of a disposition's reserve, Form T2017 page 3 "(ii) Capital gain × Enter the
applicable percentage from the table", rounded half-up to the cent once."""

T2017_RESERVE_MAXIMUM = CATALOG.declare("t2017_reserve_maximum", Decimal, non_negative=True)
"""Maximum reserve of a disposition, Form T2017 page 3 "Your reserve for the year cannot be more
than the lesser of the following": the lesser of (i) and (ii), the most the reserve claimed for
the disposition can be."""

T2017_RESERVE_LATER_YEAR_MAXIMUM = CATALOG.declare(
    "t2017_reserve_later_year_maximum", Decimal, non_negative=True
)
"""Maximum reserve of a disposition in a later year, Form T2017 page 3 "the amount you claim in a
later year (Year B) cannot be more than the amount you claimed for that property in the previous
year (Year A)": the lesser of the maximum and the reserve claimed for the property in the previous
year, the most a later year's reserve can be."""

T2017_RESERVE_CLAIM_LIMIT = CATALOG.declare("t2017_reserve_claim_limit", Decimal, non_negative=True)
"""Claim limit of a disposition, Form T2017 page 3 "You do not have to claim the maximum reserve in
a tax year (Year A)" and "the amount you claim in a later year (Year B) cannot be more than the
amount you claimed for that property in the previous year (Year A)": the maximum in the year of
disposition, and the later-year maximum in a later year, the most the reserve claimed can be."""

T2017_ROW_RESERVE = CATALOG.declare("t2017_row_reserve", Decimal, non_negative=True)
"""Reserve of a disposition, Form T2017 page 3 "Your reserve for the year cannot be more than the
lesser of the following": the reserve claimed, up to the claim limit, which the summary adds to
the line of the form the disposition is listed on. A claim above the limit is refused, not
capped."""

T2017_RESERVE_PERIOD_1_OF_2024_CHECKED = CATALOG.declare(
    "t2017_reserve_period_1_of_2024_checked", int, non_negative=True
)
"""Disposed of in Period 1 of 2024, checked: 0 or 1, a count above 1 refused, exported by each row
form so that Form T657's totals are of a checked answer."""

T2017_RESERVE_REPORTED_ON_SLIP_CHECKED = CATALOG.declare(
    "t2017_reserve_reported_on_slip_checked", int, non_negative=True
)
"""Reserve reported on a T5013 slip or letter, checked: 0 or 1, a count above 1 refused, exported
by each row form so that Form T657's totals are of a checked answer."""

T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024_CHECKED = CATALOG.declare(
    "t2017_reserve_partnership_year_began_before_june_25_2024_checked", int, non_negative=True
)
"""Partnership year began before June 25, 2024, checked: 0 or 1, a count above 1 refused, exported
by each row form so that Form T657's totals are of a checked answer."""

T2017_ROW_PREVIOUS_RESERVE = CATALOG.declare(
    "t2017_row_previous_reserve", Decimal, non_negative=True
)
"""2024 reserve of a disposition, Form T2017 line 1 "Amount of 2024 reserve" for one disposition:
the reserve claimed for the property in the previous year in a year after the year of disposition,
and 0 for a disposition in 2025 (it had no 2024 reserve)."""

T2017_ROW_CHANGE = CATALOG.declare("t2017_row_change", Decimal)
"""Reserve change of a disposition, Form T2017 line 6 "Line 1 minus line 5 (if negative, show in
brackets)" for one disposition: its 2024 reserve less its 2025 reserve, signed, which the summary
adds over the dispositions of a year for Form T657."""

T2017_LINE_2 = CATALOG.declare("t2017_line_2", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 2, Form T2017 page 1 "Amount of 2025 reserve for dispositions
of QFFP to your child after 2016, and all other dispositions of QFFP after 2021 other than QBT
or QCC": the total of the reserves of the records of `ca/t2017_line_2_reserve_rows`."""

T2017_LINE_3 = CATALOG.declare("t2017_line_3", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 3, Form T2017 page 1 "Amount of 2025 reserve for dispositions
of QFFP under a QBT after 2023": the total of the reserves of the records of
`ca/t2017_line_3_reserve_rows`."""

T2017_LINE_4 = CATALOG.declare("t2017_line_4", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 4, Form T2017 page 1 "Amount of 2025 reserve for dispositions
of QFFP under a QCC after 2023": the total of the reserves of the records of
`ca/t2017_line_4_reserve_rows`."""

T2017_LINE_5 = CATALOG.declare("t2017_line_5", Decimal, non_negative=True)
"""Line 5 of Form T2017 page 1 "Add lines 2 to 4.": the total of lines 2, 3 and 4, the reserves of
the dispositions of QFFP."""

T2017_LINE_6 = CATALOG.declare("t2017_line_6", Decimal)
"""Line 6 of Form T2017 page 1 "Line 1 minus line 5 (if negative, show in brackets)": the amount of
line 1 less line 5, which may be negative (the form prints no floor)."""

T2017_LINE_8 = CATALOG.declare("t2017_line_8", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 8, Form T2017 page 1 "Amount of 2025 reserve for dispositions
of QSBCS to your child after 2016 and all other dispositions of QSBCS other than a QBT or QCC
after 2021": the total of the reserves of the records of `ca/t2017_line_8_reserve_rows`."""

T2017_LINE_9 = CATALOG.declare("t2017_line_9", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 9, Form T2017 page 1 "Amount of 2025 reserve for dispositions
of QSBCS under a QBT after 2023": the total of the reserves of the records of
`ca/t2017_line_9_reserve_rows`."""

T2017_LINE_10 = CATALOG.declare("t2017_line_10", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 10, Form T2017 page 1 "Amount of 2025 reserve for
dispositions of QSBCS under a QCC after 2023": the total of the reserves of the records of
`ca/t2017_line_10_reserve_rows`."""

T2017_LINE_11 = CATALOG.declare("t2017_line_11", Decimal, non_negative=True)
"""Line 11 of Form T2017 page 1 "Add lines 8 to 10.": the total of lines 8, 9 and 10, the reserves
of the dispositions of QSBCS."""

T2017_LINE_12 = CATALOG.declare("t2017_line_12", Decimal)
"""Line 12 of Form T2017 page 1 "Line 7 minus line 11 (if negative, show in brackets)": the amount
of line 7 less line 11, which may be negative (the form prints no floor)."""

T2017_LINE_13 = CATALOG.declare("t2017_line_13", Decimal)
"""Line 13 of Form T2017 page 1 "Line 6 plus line 12 (if negative, show in brackets)": line 6 plus
line 12, which may be negative (the form prints no floor). Line 15 of page 2 is this amount."""

T2017_LINE_17 = CATALOG.declare("t2017_line_17", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 17, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of family farm or fishing property to your child (other than QFFP) after 2016": the
total of the reserves of the records of `ca/t2017_line_17_reserve_rows`."""

T2017_LINE_18 = CATALOG.declare("t2017_line_18", Decimal)
"""Line 18 of Form T2017 page 2 "Line 16 minus line 17 (if negative, show in brackets)": the amount
of line 16 less line 17, which may be negative (the form prints no floor)."""

T2017_LINE_19 = CATALOG.declare("t2017_line_19", Decimal)
"""Line 19 of Form T2017 page 2 "Line 15 plus line 18 (if negative, show in brackets)": line 15
plus line 18, which may be negative (the form prints no floor)."""

T2017_LINE_21 = CATALOG.declare("t2017_line_21", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 21, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of property under a QBT (other than QFFP and QSBCS) after 2023": the total of the
reserves of the records of `ca/t2017_line_21_reserve_rows`."""

T2017_LINE_22 = CATALOG.declare("t2017_line_22", Decimal)
"""Line 22 of Form T2017 page 2 "Line 20 minus line 21 (if negative, show in brackets)": the amount
of line 20 less line 21, which may be negative (the form prints no floor)."""

T2017_LINE_24 = CATALOG.declare("t2017_line_24", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 24, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of property under a QCC (other than QFFP and QSBCS) after 2023": the total of the
reserves of the records of `ca/t2017_line_24_reserve_rows`."""

T2017_LINE_25 = CATALOG.declare("t2017_line_25", Decimal)
"""Line 25 of Form T2017 page 2 "Line 23 minus line 24 (if negative, show in brackets)": the amount
of line 23 less line 24, which may be negative (the form prints no floor)."""

T2017_LINE_26 = CATALOG.declare("t2017_line_26", Decimal)
"""Line 26 of Form T2017 page 2 "Amount of 2024 reserve for dispositions of property after 2020,
other than dispositions listed on lines 66843, 66883, 66910, and 66930 (lines 66990 and 67058 of
Form T2017 for 2024 minus amounts reported at line 66937 of Form T2017 for 2025)": the starting
2024 figure less line 23, which may be negative (the form prints no floor)."""

T2017_LINE_27 = CATALOG.declare("t2017_line_27", Decimal, non_negative=True)
"""Total of the 2025 reserves on line 27, Form T2017 page 2 "Amount of 2025 reserve for
dispositions of property after 2021, other than dispositions listed on lines 66844, 66850,
66920, 66935, and 66939": the total of the reserves of the records of
`ca/t2017_line_27_reserve_rows`."""

T2017_LINE_28 = CATALOG.declare("t2017_line_28", Decimal)
"""Line 28 of Form T2017 page 2 "Line 26 minus line 27 (if negative, show in brackets)": the amount
of line 26 less line 27, which may be negative (the form prints no floor)."""

T2017_LINE_29 = CATALOG.declare("t2017_line_29", Decimal)
"""Line 29 of Form T2017 page 2 "Add lines 19, 22, 25, and 28 (if negative, show in brackets).":
the total of lines 19, 22, 25 and 28, which may be negative (the form prints no floor)."""

T2017_LINE_31 = CATALOG.declare("t2017_line_31", Decimal)
"""Total reserve to be included in income, Form T2017 page 2 "Line 29 plus line 30" and "Enter this
amount on line 19200 of Schedule 3 (if negative, show in brackets)": line 29 plus line 30, which
may be negative (the form prints no floor)."""
