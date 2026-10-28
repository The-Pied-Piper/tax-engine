"""The federal catalog: the advanced Canada workers benefit and RESP income payments.

The advanced Canada workers benefit and the RESP accumulated income payments lines.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

ADVANCED_CANADA_WORKERS_BENEFIT = CATALOG.declare(
    "advanced_canada_workers_benefit", Decimal, non_negative=True
)
"""Advanced Canada workers benefit, T1 line 140 (line 41500) "Advanced Canada workers benefit (ACWB)
(complete Schedule 6)": Schedule 6 line 49 "Enter whichever is less: amount from line 43 or line 48.
Enter this amount on line 41500 of your return.", the lesser of the Canada workers benefit claimed
(`ca/cwb_claimed`) and the advance payments received (`ca/acwb_paid`)."""

RESP_AIPS_RECEIVED_PART_A = CATALOG.declare("resp_aips_received_part_a", Decimal, non_negative=True)
"""AIPs received, Form T1172 Part A, line 1 (68270) "Total of all AIPs you received or the promoter
had transferred to an RRSP, PRPP or SPP on your behalf, during the year.": the caller's amount, as
entered."""

RESP_AIPS_RRSP_CONTRIBUTIONS = CATALOG.declare(
    "resp_aips_rrsp_contributions", Decimal, non_negative=True
)
"""RRSP contributions deducted, Form T1172 Part A, line 2 "Total amounts you or your promoter
contributed on your behalf to your RRSP, PRPP, or SPP, or the RRSP or SPP of your spouse or
common-law partner, in the year you received the AIPs or the first 60 days of the following year,
that you deducted on line 20800 of your income tax and benefit return for the year you received the
AIPs. This amount cannot be more than your RRSP deduction limit for that year": the caller's
amount, as entered; keeping it within the RRSP deduction limit is the caller's, the engine does not
bound it."""

RESP_AIPS_CONTRIBUTIONS_COUNTED = CATALOG.declare(
    "resp_aips_contributions_counted", Decimal, non_negative=True
)
"""Contributions counted, Form T1172 Part A, line 3 "Amount from line 1 or 2, whichever is less":
the AIPs received and the RRSP contributions deducted, the lesser."""

RESP_AIPS_LIFETIME_LIMIT = CATALOG.declare("resp_aips_lifetime_limit", Decimal, non_negative=True)
"""Lifetime limit, Form T1172 Part A, line 4 "Maximum lifetime RRSP contribution limit that can be
used to reduce or eliminate the amount of AIPs subject to the additional tax $ 50,000.00"."""

RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS = CATALOG.declare(
    "resp_aips_reduction_used_in_previous_years", Decimal, non_negative=True
)
"""Amounts used in previous years, Form T1172 Part A, line 5 "Total of all amounts used to reduce
the amount of additional tax payable on AIPs received in previous years (if applicable). This
amount is the total of the amount entered at line 5 of all T1172 forms you filed for 1998 and at
line 7 of all T1172 forms you filed for 1999 and later": the caller's figure, as entered, and not
bounded by the engine."""

RESP_AIPS_LIMIT_REMAINING = CATALOG.declare("resp_aips_limit_remaining", Decimal)
"""Limit remaining, Form T1172 Part A, line 6 "Line 4 minus line 5": the lifetime limit less the
amounts used in previous years. The form prints no "(if negative, enter "0")", so the kind is
signed."""

RESP_AIPS_REDUCTION = CATALOG.declare("resp_aips_reduction", Decimal)
"""Reduction, Form T1172 Part A, line 7 "Amount from line 3 or 6, whichever is less": the
contributions counted and the limit remaining, the lesser. It follows line 6, which the form does
not floor, so the kind is signed."""

RESP_AIPS_SUBJECT_TO_TAX = CATALOG.declare("resp_aips_subject_to_tax", Decimal, non_negative=True)
"""AIPs subject to the additional tax, Form T1172 Part A, line 8 "Amount of AIPs subject to the
additional tax: line 1 minus line 7"."""

RESP_AIPS_PART_A_TAX = CATALOG.declare("resp_aips_part_a_tax", Decimal, non_negative=True)
"""Additional tax on AIPs, Form T1172 Part A, line 10 "Additional tax on AIPs: line 8 multiplied by
line 9." (line 9 "Rate of the additional tax on AIPs × 20%"). Part C, for a resident of Quebec on
December 31, is not triggered on an Ontario resident's return."""

RESP_AIPS_RECEIVED_PART_B = CATALOG.declare("resp_aips_received_part_b", Decimal, non_negative=True)
"""AIPs received, Form T1172 Part B, line 11 (68280) "Total of all AIPs you received from RESPs
during the year.": the caller's amount, as entered."""

RESP_AIPS_PART_B_TAX = CATALOG.declare("resp_aips_part_b_tax", Decimal, non_negative=True)
"""Additional tax on AIPs, Form T1172 Part B, line 13 "Additional tax on AIPs: line 11 multiplied by
line 12." (line 12 "Rate of the additional tax on AIPs × 20%")."""

RESP_AIPS_PART_A_APPLIES = CATALOG.declare("resp_aips_part_a_applies", int, non_negative=True)
"""Part A applies, Form T1172 "Part B - Fill out this part only if Part A does not apply to you.":
the caller's count, 1 when Part A applies (the original subscriber and the other listed cases) and
0 when Part B does."""

RESP_AIPS_PART_A_APPLIES_CHECKED = CATALOG.declare(
    "resp_aips_part_a_applies_checked", int, non_negative=True
)
"""Part A applies, Form T1172 Part B "Fill out this part only if Part A does not apply to you.": the
answer of `ca/resp_aips_part_a_applies` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

RESP_AIPS_ADDITIONAL_TAX = CATALOG.declare("resp_aips_additional_tax", Decimal, non_negative=True)
"""Additional tax on AIPs, Form T1172 line 10 or 13: the amount the form says to "enter on line
41800 of your income tax and benefit return", line 10 when Part A applies and line 13 when it does
not."""
