"""The federal catalog: income.

The T1 income lines, total income, the dividend and investment income lines that feed them, and
the short-term rental rows of Form T776 Chart A and the business statement of Form T2125.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind, RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
    CCA_ZEPV_DIEP_PROCEEDS,
    CCA_ZEPV_PROCEEDS,
)

EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "employment_income", non_negative=True)
"""Employment income, T1 line 10100: a starting amount that total income sums directly."""

TOTAL_INCOME = AmountKind.declare(CATALOG, "total_income")
"""Total income, T1 line 15000 "Line 28 plus line 32 Total income": in the take-home, one core/sum
of line 10100 (`ca/employment_income`) and line 10400 (`ca/other_employment_income`), in form line
order (`t1_taxable_income_line_15000.yaml`). The subtotals on lines 21, 28 and 33 fold into that
step. Not floored, so a loss larger than the other income is shown in brackets as the form prints it
(T1 line 33 prints no floor; the General Guide says "If you have a loss, show it on the applicable
line using brackets").
"""

OTHER_EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "other_employment_income", non_negative=True)
"""Other employment income, T1 line 10400 "Other employment income": a starting amount."""

CREDITS_AGAINST_BASIC_FEDERAL_TAX = AmountKind.declare(
    CATALOG, "credits_against_basic_federal_tax", non_negative=True
)
"""Credits against the basic federal tax, T1 line 125 "Add lines 122 to 124.": line 122 "Amount from
line 35000", line 123 (40425), the federal dividend tax credit, and line 124 (40427), the minimum
tax carryover applied on Form T691 Part 8 line 12, in line order."""


CCA_SOLD_ZEPVS = RecordListKind.declare(
    CATALOG,
    "cca_sold_zepvs",
    fields=(
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_ZEPV_PROCEEDS,
        CCA_ZEPV_DIEP_PROCEEDS,
    ),
)
"""Sold zero-emission passenger vehicles of a Class 54 row, Guide T4036 2025 "Class 54 (30%)":
"Class 54 may include both zero-emission passenger vehicles that do and do not exceed the
prescribed threshold. However, unlike Class 10.1, Class 54 does not establish a separate class for
each vehicle whose cost exceeds the threshold", and "If a zero-emission passenger vehicle is
disposed of to a person or partnership with whom you deal at arm's length, and its cost exceeds the
prescribed amount [...], the proceeds of disposition will be adjusted based on a factor equal to the
prescribed amount as a proportion of the actual cost of the vehicle." One record for each vehicle
sold from the row: the year it was acquired (0 when the rule does not apply to it), its cost, the
government assistance for it, its proceeds and the DIEP part of them. A field of each record of a
list of capital cost allowance classes."""

# Form T2125 Charts A to C, motor vehicle expenses: the caller's amounts of one vehicle, the
# printed constants (each a dataset of the same name); the lines the charts compute are
# not artifacts.


# Form T2121 (Statement of Fishing Activities), Parts 3 to 7 and Area A (T1 lines 14299 and 14300).
# Each kind is one line of the form; the caller's amounts are starting amounts, the rest are
# computed by the T2121 steps of the manifest part `03d_t2121.yaml`.
