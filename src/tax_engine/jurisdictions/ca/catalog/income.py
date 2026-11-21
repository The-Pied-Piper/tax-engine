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

EMPLOYMENT_INCOME_LINE_10100 = AmountKind.declare(
    CATALOG, "employment_income_line_10100", non_negative=True
)
"""Employment income as T1 line 10100 prints it (`t1_employment_income_line_10100.yaml`): the salary
input (`ca/employment_income`), exported by the T1 employment income form."""

OTHER_EMPLOYMENT_INCOME_LINE_10400 = AmountKind.declare(
    CATALOG, "other_employment_income_line_10400", non_negative=True
)
"""Other employment income as T1 line 10400 prints it (`t1_employment_income_line_10400.yaml`): the
optional input (`ca/other_employment_income`), exported by the T1 employment income form."""

RETURN_EMPLOYMENT_INCOME = AmountKind.declare(
    CATALOG, "return_employment_income", non_negative=True
)
"""The default form's own copy of T1 line 10100 (`return.yaml`): a `core/record_total` of the T1
employment income form's export `employment_income_line_10100`, which a province's average income
tax rate divides by."""

UCCB_INCOME = AmountKind.declare(CATALOG, "uccb_income", non_negative=True)
"""Universal child care benefit (UCCB), T1 line 7 and line 11700 "Universal child care benefit
(UCCB) (see the RC62 slip)": the optional input
(`t1_taxable_income_line_11700_inputs.yaml`), blank when the filer has none.
The T1 owns it; every other form that prints it imports line 11700."""

UCCB_INCOME_LINE_11700 = AmountKind.declare(CATALOG, "uccb_income_line_11700", non_negative=True)
"""UCCB income as T1 line 11700 prints it (`t1_taxable_income_line_11700.yaml`): the optional input
(`ca/uccb_income`), read as 0 when blank, exported by the T1 taxable income form."""

RDSP_INCOME = AmountKind.declare(CATALOG, "rdsp_income", non_negative=True)
"""Registered disability savings plan (RDSP) income, T1 line 12 and line 12500 "Registered
disability savings plan (RDSP) income (box 131 of the T4A slip)": the optional input
(`t1_taxable_income_line_12500_inputs.yaml`), blank when the filer has none. The T1 owns it; every
other form that prints it imports line 12500."""

RDSP_INCOME_LINE_12500 = AmountKind.declare(CATALOG, "rdsp_income_line_12500", non_negative=True)
"""RDSP income as T1 line 12500 prints it (`t1_taxable_income_line_12500.yaml`): the optional input
(`ca/rdsp_income`), read as 0 when blank, exported by the T1 taxable income form."""

UCCB_REPAYMENT = AmountKind.declare(CATALOG, "uccb_repayment", non_negative=True)
"""Universal child care benefit (UCCB) repayment, T1 line 40 and line 21300 "Universal child care
benefit (UCCB) repayment (box 12 of all RC62 slips)": the optional input
(`t1_taxable_income_line_21300_inputs.yaml`), blank when the filer has none. The T1 owns it; every
other form that prints it imports line 21300."""

UCCB_REPAYMENT_LINE_21300 = AmountKind.declare(
    CATALOG, "uccb_repayment_line_21300", non_negative=True
)
"""UCCB repayment as T1 line 21300 prints it (`t1_taxable_income_line_21300.yaml`): the optional
input (`ca/uccb_repayment`), read as 0 when blank, exported by the T1 taxable income form."""

RDSP_INCOME_REPAYMENT = AmountKind.declare(CATALOG, "rdsp_income_repayment", non_negative=True)
"""Registered disability savings plan (RDSP) income repayment, included on T1 line 52 and line 23200
"Other deductions (specify)": the optional input (`t1_taxable_income_line_23200_inputs.yaml`), the
part of line 23200 that is the RDSP income repayment, blank when the filer has none. The T1 owns
it; every other form that prints it imports it from line 23200."""

RDSP_INCOME_REPAYMENT_LINE_23200 = AmountKind.declare(
    CATALOG, "rdsp_income_repayment_line_23200", non_negative=True
)
"""RDSP income repayment included on T1 line 23200 (`t1_taxable_income_line_23200.yaml`): the
optional input (`ca/rdsp_income_repayment`), read as 0 when blank, exported by the T1 taxable income
form."""

TOTAL_INCOME_EMPLOYMENT_INCOME_LINE_10100 = AmountKind.declare(
    CATALOG, "total_income_employment_income_line_10100", non_negative=True
)
"""Total income, the part from T1 line 10100 (employment income): the T1 employment income form's
export, read by line 15000 (`t1_taxable_income_line_15000.yaml`)."""

TOTAL_INCOME_OTHER_EMPLOYMENT_INCOME_LINE_10400 = AmountKind.declare(
    CATALOG, "total_income_other_employment_income_line_10400", non_negative=True
)
"""Total income, the part from T1 line 10400 (other employment income): the T1 employment income
form's export, read by line 15000 (`t1_taxable_income_line_15000.yaml`)."""

CREDITS_AGAINST_BASIC_FEDERAL_TAX = AmountKind.declare(
    CATALOG, "credits_against_basic_federal_tax", non_negative=True
)
"""Credits against the basic federal tax, T1 line 125 "Add lines 122 to 124.", as built for the
take-home return: the sum of one part, line 122 (`non_refundable_tax_credits`, line 35000, "Amount
from line 35000"). Lines 123 (40425) and 124 (40427) are absent for the take-home filer and are left
out.
"""


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
