"""The federal catalog: Form T1212, "Statement of Deferred Security Options Benefits", the form
`ca/t1212`.

The form runs once (it has no instances). Its two starting amounts are the printed line 1 and
line 2; the steps compute line 3 and the 50% of line 2 that footnote (1) says to enter on line 24900
of the return. The exports are line 2 (to be entered on line 10100), line 3 and that 50% amount,
which the security options deduction of line 24900 and Form T691 Part 1 line 29 read through
`ca/t1212.<name>`."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

T1212_LINE_1_OPENING_BALANCE = CATALOG.declare(
    "t1212_line_1_opening_balance", Decimal, non_negative=True
)
"""Opening balance of deferred security options benefits, T1212 line 1 "Opening balance of deferred
security options benefits: (from your previous year's notice of assessment or reassessment)": the
amount the filer enters, a starting amount."""

T1212_LINE_2_BENEFITS_NO_LONGER_DEFERRED = CATALOG.declare(
    "t1212_line_2_benefits_no_longer_deferred", Decimal, non_negative=True
)
"""Benefits that can no longer be deferred, T1212 line 2 "Benefits that can no longer be deferred.
Enter this amount on line 10100 of your return" "65210": the amount the filer enters, a starting
amount, subtracted from line 1 at line 3. It is part of the employment income the filer enters on
line 10100, which is not added again. The form prints no bound of line 2 against line 10100, so none
is checked."""

T1212_LINE_3_CLOSING_BALANCE = CATALOG.declare(
    "t1212_line_3_closing_balance", Decimal, non_negative=True
)
"""Closing balance of deferred security options benefits, T1212 line 3 "Closing balance of deferred
security options benefits: line 1 minus line 2" "65220 =": line 1 less line 2, the amount the CRA
shows on the notice of assessment. A line 2 above line 1 is refused."""

T1212_LINE_24900_AMOUNT = CATALOG.declare("t1212_line_24900_amount", Decimal, non_negative=True)
"""Security options deduction on the benefits of line 2, T1212 footnote (1) "To claim your security
options deduction on this amount, enter 50% of the amount from line 2 on line 24900 of your
return": line 2 at the 50% of its dataset, rounded to the cent. Form T691 Part 1 line 29 footnote
(7) "include 50% of the amount from line 2 of Form T1212" is the same amount."""
