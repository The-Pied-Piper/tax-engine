"""The federal catalog: Form T2205, "Amounts from a Spousal or Common-law Partner RRSP, RRIF, or SPP
to Include in Income", the form `ca/t2205`.

The form runs once (it has no instances). Its twelve starting amounts are the printed lines 1, 2,
4, 6, 7, 12, 13, 14, 17, 18 and 20 and the part of line 11 that relates to SPP withdrawals (line 11
prints "If part of this amount relates to withdrawals from an SPP"); the steps compute the other
printed lines and check each part against its whole. The exports are the RRSP part of line 11, the
SPP part of line 11 and line 22, which the return reports, and line 10 and line 21, which are the
spouse's or common-law partner's amounts (exported, never read into this return).

The form cannot read the age of the filer, a figure of the return. The return totals the three
exports and sends the SPP part and line 22 to T1 line 11500 (the filer is 65 or older at the end of
the year) or to T1 line 13000, and the RRSP part to T1 line 12900; the kinds at the end of this
module are those amounts."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.jurisdictions.ca.catalog.base import CATALOG

T2205_LINE_1 = CATALOG.declare("t2205_line_1", Decimal, non_negative=True)
"""Amounts received from a spousal RRSP or SPP, T2205 line 1 "Add the amounts from boxes 20, 22 and
26 of all your T4RSP slips and part of the amount from box 18 of your T4A slips that relate to SPP
amount you received from spousal or common-law partner's RRSPs or SPP for the year you indicated
above. Enter the total.": the amount the filer enters, one total, a starting amount."""

T2205_LINE_2 = CATALOG.declare("t2205_line_2", Decimal, non_negative=True)
"""Transfers to the filer's FHSAs, T2205 line 2 "Enter the amount of transfers from your spousal or
common-law partner's RRSPs to your FHSAs that are considered to be a taxable withdrawal from your
spousal or common-law partner's RRSPs for the year indicated above.": the amount the filer enters,
a starting amount, added to line 1 at line 3."""

T2205_LINE_3 = CATALOG.declare("t2205_line_3", Decimal, non_negative=True)
"""Line 3 of Form T2205, "Line 1 plus line 2": the sum of the two starting amounts, also line 9
("Enter the amount from line 3."). Part 1 is filled in when this is more than 0."""

T2205_LINE_4 = CATALOG.declare("t2205_line_4", Decimal, non_negative=True)
"""Amount transferred on, T2205 line 4 "Enter the part of the amount from line 1 that was directly
transferred to an RRSP, PRPP, SPP, RRIF or that was used to buy an annuity that cannot be commuted
(converted into a lump sum at the current value) for at least three years from the day it was
bought.": the amount the filer enters, a starting amount, checked against line 1."""

T2205_LINE_4_CHECKED = CATALOG.declare("t2205_line_4_checked", Decimal, non_negative=True)
"""Line 4 of Form T2205 checked, "Enter the part of the amount from line 1": the line 4 amount,
refused above line 1 (it is a part of line 1, and the form prints no cap), never capped."""

T2205_LINE_5 = CATALOG.declare("t2205_line_5", Decimal, non_negative=True)
"""Line 5 of Form T2205, "Line 3 minus line 4": line 3 less the checked line 4."""

T2205_LINE_6 = CATALOG.declare("t2205_line_6", Decimal, non_negative=True)
"""Spouse's contributions, T2205 line 6 "Enter the total amount that your spouse or common-law
partner contributed to your RRSPs and SPP in the year you indicated above and the two preceding
years.": the amount the filer enters, a starting amount."""

T2205_LINE_7 = CATALOG.declare("t2205_line_7", Decimal, non_negative=True)
"""Contributions already included, T2205 line 7 "Enter the part of the amount from line 6 that your
spouse or common-law partner contributed to your RRSPs and SPP in the two preceding years and
included in their income for one of those two preceding years.": the amount the filer enters, a
starting amount, checked against line 6."""

T2205_LINE_7_CHECKED = CATALOG.declare("t2205_line_7_checked", Decimal, non_negative=True)
"""Line 7 of Form T2205 checked, "Enter the part of the amount from line 6": the line 7 amount,
refused above line 6 (it is a part of line 6, and the form prints no cap), never capped."""

T2205_LINE_8 = CATALOG.declare("t2205_line_8", Decimal, non_negative=True)
"""Line 8 of Form T2205, "Line 6 minus line 7": line 6 less the checked line 7."""

T2205_LINE_10 = CATALOG.declare("t2205_line_10", Decimal, non_negative=True)
"""Line 10 of Form T2205, "Enter the amount from line 5 or line 8, whichever is less.": the
lesser of line 5 and line 8, the amount the spouse or common-law partner reports (on line
12900, or for an SPP withdrawal on line 11500 or line 13000). The filer's return does not read it;
it is exported and traced."""

T2205_LINE_11 = CATALOG.declare("t2205_line_11", Decimal, non_negative=True)
"""Line 11 of Form T2205, "Line 9 minus line 10.": line 3 (line 9) less line 10, the amount the
filer reports, in part on line 12900 (RRSP) and in part on line 11500 or line 13000 (SPP)."""

T2205_LINE_11_SPP_PART = CATALOG.declare("t2205_line_11_spp_part", Decimal, non_negative=True)
"""The part of T2205 line 11 that relates to SPP withdrawals, line 11 "If part of this amount
relates to withdrawals from an SPP, you must report it on line 11500 of your own income tax and
benefit return if you are 65 or older at the end of the year, or on line 13000 otherwise": the
amount the filer enters, a starting amount, checked against line 11. The form has no box that
splits line 11 between RRSP and SPP withdrawals."""

T2205_LINE_11_SPP_PART_CHECKED = CATALOG.declare(
    "t2205_line_11_spp_part_checked", Decimal, non_negative=True
)
"""The SPP part of T2205 line 11, checked: "If part of this amount relates to withdrawals from an
SPP", refused above line 11 (it is a part of line 11), never capped. The export the return sends to
T1 line 11500 or line 13000."""

T2205_LINE_11_RRSP_PART = CATALOG.declare("t2205_line_11_rrsp_part", Decimal, non_negative=True)
"""The RRSP part of T2205 line 11, "If part of this amount relates to withdrawals from an RRSP
(including transfers from an RRSP that are considered to be taxable withdrawals), you must report
it on line 12900 of your own income tax and benefit return": line 11 less the checked SPP part. The
export the return sends to T1 line 12900."""

T2205_LINE_12 = CATALOG.declare("t2205_line_12", Decimal, non_negative=True)
"""RRIF amounts received, T2205 line 12 "Enter the total amounts from box 20 of all your T4RIF slips
you received from spousal or common-law partner's RRIFs for the year you indicated above.": the
amount the filer enters, one total, a starting amount."""

T2205_LINE_13 = CATALOG.declare("t2205_line_13", Decimal, non_negative=True)
"""RRIF amounts of box 24, T2205 line 13 "Enter the total amounts from box 24 of the T4RIF slips you
received from spousal or common-law partner's RRIFs in the year you indicated above.": the amount
the filer enters, one total, a starting amount."""

T2205_LINE_14 = CATALOG.declare("t2205_line_14", Decimal, non_negative=True)
"""Amount transferred on, T2205 line 14 "Enter the part of the amount from line 13 that was directly
transferred to a RRIF, an RRSP, a PRPP, an SPP or that was used to buy an annuity that cannot be
commuted for at least three years from the day it was bought.": the amount the filer enters, a
starting amount, checked against line 13."""

T2205_LINE_14_CHECKED = CATALOG.declare("t2205_line_14_checked", Decimal, non_negative=True)
"""Line 14 of Form T2205 checked, "Enter the part of the amount from line 13": the line 14 amount,
refused above line 13 (it is a part of line 13, and the form prints no cap), never capped."""

T2205_LINE_15 = CATALOG.declare("t2205_line_15", Decimal, non_negative=True)
"""Line 15 of Form T2205, "Line 13 minus line 14 = (added at line 16)": line 13 less the checked
line 14."""

T2205_LINE_16 = CATALOG.declare("t2205_line_16", Decimal, non_negative=True)
"""Line 16 of Form T2205, "Line 12 plus line 15": the sum of line 12 and line 15."""

T2205_LINE_17 = CATALOG.declare("t2205_line_17", Decimal, non_negative=True)
"""Spouse's contributions, T2205 line 17 "Enter the total amount that your spouse or common-law
partner contributed to your RRSPs and SPP in the year you indicated above and the two preceding
years. If you filled in Part 1 above, enter the amount from line 6.": the amount the filer enters,
a starting amount, read only when Part 1 is not filled in (line 3 is 0)."""

T2205_LINE_17_USED = CATALOG.declare("t2205_line_17_used", Decimal, non_negative=True)
"""Line 17 of Form T2205 as used, "If you filled in Part 1 above, enter the amount from line
6.": line 6 when line 3 is more than 0 (Part 1 is filled in, the engine's reading of that
phrase), else the amount the filer typed on line 17."""

T2205_LINE_18 = CATALOG.declare("t2205_line_18", Decimal, non_negative=True)
"""Contributions already included, T2205 line 18 "Enter the part of the amount from line 17 that
your spouse or common-law partner contributed to your RRSPs and SPP in the two preceding years and
included in their income for one of those two preceding years. If you filled in Part 1 above, add
the amounts from line 7 and line 10 and enter the result.": the amount the filer enters, a starting
amount, read only when Part 1 is not filled in (line 3 is 0)."""

T2205_LINE_18_FROM_PART_1 = CATALOG.declare("t2205_line_18_from_part_1", Decimal, non_negative=True)
"""Line 18 of Form T2205 when Part 1 is filled in, "If you filled in Part 1 above, add the amounts
from line 7 and line 10 and enter the result.": the checked line 7 plus line 10."""

T2205_LINE_18_USED = CATALOG.declare("t2205_line_18_used", Decimal, non_negative=True)
"""Line 18 of Form T2205 as used: line 7 plus line 10 when line 3 is more than 0 (Part 1 is filled
in), else the amount the filer typed on line 18."""

T2205_LINE_18_CHECKED = CATALOG.declare("t2205_line_18_checked", Decimal, non_negative=True)
"""Line 18 of Form T2205 checked, "Enter the part of the amount from line 17": line 18 as used,
refused above line 17 as used (it is a part of line 17), never capped."""

T2205_LINE_19 = CATALOG.declare("t2205_line_19", Decimal, non_negative=True)
"""Line 19 of Form T2205, "Line 17 minus line 18": line 17 as used less the checked line 18."""

T2205_LINE_20 = CATALOG.declare("t2205_line_20", Decimal, non_negative=True)
"""RRIF income, T2205 line 20 "Add the amounts from boxes 16 and 20 of all T4RIF slips you received
from spousal or common-law partner's RRIFs in the year you indicated above and enter the total.":
the amount the filer enters, one total, a starting amount."""

T2205_LINE_21 = CATALOG.declare("t2205_line_21", Decimal, non_negative=True)
"""Line 21 of Form T2205, "Enter the amount from line 16 or line 19, whichever is less.": the lesser
of line 16 and line 19, the amount the spouse or common-law partner reports on line 11500 or line
13000. The filer's return does not read it; it is exported and traced."""

T2205_LINE_22 = CATALOG.declare("t2205_line_22", Decimal)
"""Line 22 of Form T2205, "Line 20 minus line 21.": line 20 less line 21, the amount the filer
reports on line 11500 (65 or older at the end of the year) or line 13000. Signed: the form prints no
floor."""

T2205_ON_LINE_12900 = CATALOG.declare("t2205_on_line_12900", Decimal, non_negative=True)
"""The T2205 amount on T1 line 12900, from the RRSP part of line 11 ("you must report it on line
12900 of your own income tax and benefit return"): the total of the form's export, a part of the
RRSP income of the return."""

T2205_SPP_PART_TOTAL = CATALOG.declare("t2205_spp_part_total", Decimal, non_negative=True)
"""The SPP part of T2205 line 11 for the return, the total of the form's export, before it goes to
T1 line 11500 or line 13000 by the filer's age."""

T2205_LINE_22_TOTAL = CATALOG.declare("t2205_line_22_total", Decimal)
"""T2205 line 22 for the return, the total of the form's export, before it goes to T1 line 11500 or
line 13000 by the filer's age. Signed as line 22 is."""

T2205_SPP_PART_ON_LINE_11500 = CATALOG.declare(
    "t2205_spp_part_on_line_11500", Decimal, non_negative=True
)
"""The SPP part of T2205 line 11 on T1 line 11500, "if you are 65 or older at the end of the year":
the SPP part times the count of 1 for a filer born in 1960 or earlier, else 0."""

T2205_SPP_PART_ON_LINE_13000 = CATALOG.declare(
    "t2205_spp_part_on_line_13000", Decimal, non_negative=True
)
"""The SPP part of T2205 line 11 on T1 line 13000, "or on line 13000 otherwise": the SPP part less
what goes to line 11500."""

T2205_LINE_22_ON_LINE_11500 = CATALOG.declare("t2205_line_22_on_line_11500", Decimal)
"""T2205 line 22 on T1 line 11500, "If you were 65 or older at the end of the year you indicated
above, report this amount on line 11500 of your own income tax and benefit return": line 22 times
the count of 1 for a filer born in 1960 or earlier, else 0. Signed as line 22 is."""

T2205_LINE_22_ON_LINE_13000 = CATALOG.declare("t2205_line_22_on_line_13000", Decimal)
"""T2205 line 22 on T1 line 13000, "Otherwise, report it on line 13000.": line 22 less what goes to
line 11500. Signed as line 22 is."""

T2205_ON_LINE_11500 = CATALOG.declare("t2205_on_line_11500", Decimal)
"""The T2205 amount on T1 line 11500: the SPP part and line 22 of a filer 65 or older at the end of
the year, added to the other pensions and superannuation of the return. Signed, as line 22 is."""

T2205_ON_LINE_13000 = CATALOG.declare("t2205_on_line_13000", Decimal)
"""The T2205 amount on T1 line 13000: the SPP part and line 22 of a filer under 65 at the end of the
year, added to the other income of the return. Signed, as line 22 is."""
