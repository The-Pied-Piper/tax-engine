"""The federal Canada artifact catalog: artifact kinds named from Canada's own return (§2, §8).

Only the kinds in use are declared, each non-negative except the lines that print no floor: none of
these lines can be negative on the return as modelled except the refund or balance owing, where
negative means a refund, lines 5 and 9 of the Federal Worksheet for line 25000, the five "Net"
self-employment income lines (T1 lines 22 to 26), line 27, Schedule 8 Part 4 line 1, the net income
before adjustments (line 23400, "if negative, show in brackets"), line 23600 before its floor and
the lines of Form T1436 and of Schedule 15 that print no "(if negative, enter "0")", and Form T1223
Part C lines 8 to 10 and its (C) totals, and Form RC359 lines 4 and 6. Amounts are Decimal; the
counts of eligible dependants, of infirm children, of the eligible children for child care (Form
T778 Part B lines 1 to 3), of the Schedule 6 eligible dependants (line 38100), the two starting
counts of the Federal Worksheet for line 25000, the Schedule 15 count of a maximum participation
period that ended in a prior year, the months of Schedule 8 box A, the Schedule 8 Part 4 and
Schedule 13 counts, the ticks of T1 line 26600 and of Schedule 11 line 32005 and Schedule 15 lines
68930 and 68965, and the months of Schedule 11 lines 32010 and 32020, the capital cost allowance
count of no property left in a class, the 0 or 1 depreciable property answer of a real estate
disposition, the day counts of Form T2222 Step 2, the individual and the
zone of a trip, the months in qualifying employment and the Part C (B) choice of Form T1223, the
province code of Form RC359 line 8, the years after the sale of a Form T1206 reserve, the 0 or 1
age answer of Form T1206 page 6, the three 0 or 1 answers of Form T1032 (an RCA life annuity at 65
or older, a change of marital status in the year, this return being the transferring spouse's), the
years after the disposition and the 0 or 1 nine-year answer of a Form T2017 reserve and the 0 or 1
Schedule 6 election of line 38105 are int. Chart A and Chart B of Form T2222 are record lists, each
a `RecordListKind` declared here; the dispositions of a Form T1206 reserve and the ten lists of the
dispositions of Form T2017 Part 1 are too. The sixteen starting amounts of Form T90 are Decimal,
its lines 4, 14, 16, 18 and 20 and its checked line 10019 are its steps (`ca/t90`, run once). The
years of Form T746 lines 1 and 5 are int, and its years of unused contributions are a record list.
five starting amounts of Form T936 are Decimal, every other line of it is a step (`ca/t936`, run
once), signed where the form prints no floor.
The twelve starting amounts of Form T2205 are Decimal, its other printed lines, the checks of its
parts and the amounts the return sends to T1 lines 12900, 11500 and 13000 are its steps (`ca/t2205`,
run once).
The two starting amounts of Form T1212 are Decimal, its line 3 and its 50% amount are its steps
(`ca/t1212`).
The line, the box ticked and the positions of the statements of Form T1139 are int, and its
businesses and the statements of its amounts A, H and I are record lists.
Identifiers are stable: `tests/jurisdictions/ca/test_catalog.py` snapshots them.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca.catalog.base import CATALOG as CATALOG

# The family modules are imported in the order of the T1, which is the order the kinds are
# declared on CATALOG, so they are not sorted.
# isort: off
from tax_engine.jurisdictions.ca.catalog.income import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.rrsp_fhsa import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.deductions import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t777 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1032_pension_income_splitting import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1043 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1139 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1206_share_dispositions import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t746 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t90 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t936 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t2205 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1212 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t2017_reserve import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.taxable_income import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.capital_gains_deduction_charts import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.personal_amounts import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.non_refundable_credits import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.credits_against_federal_tax import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.investment_tax_credit import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.resp_aips import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.other_inputs import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.net_tax import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.alternative_minimum_tax import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.refundable_credits import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.refund import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.rc381_cpp_qpp import *  # noqa: F403
# isort: on
