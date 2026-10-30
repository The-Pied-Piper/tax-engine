"""The CA-ON manifest entries of T1 line 22900 "Other employment expenses (see Guide T4044)" (see
`test_manifest_other_employment_expenses.py`).

Line 22900 is computed, no longer a starting amount: it is the total of Form T777 line 17 (the
employment expenses, `ca/t777_line_17`, the form `ca/t777`) and the total of Form RC359 line 7 over
the copies (`ca/rc359_excess_epsp_total`, a `core/record_total` over
`ca/rc359.rc359_excess_epsp_amount`).
Both steps are in the part `05s_other_employment_expenses.yaml`. The line 23300 sum of
`05_deductions.yaml` takes the total as one of its parts, so the family `deductions` lists it there;
the line 45200 and T691 line 77 steps read the total as before (their own families).

The return declares no output for the line: it is read by the return's own steps.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    OTHER_EMPLOYMENT_EXPENSES,
    RC359_EXCESS_EPSP_AMOUNT,
    RC359_EXCESS_EPSP_TOTAL,
    T777_LINE_17,
    T777_LINE_17_TOTAL,
)

# The record kinds read by the two record totals: one record for each copy of Form RC359 (its line 7
# field) and the one record of the export `ca/t777.t777_line_17` of Form T777.
RC359_EXCESS_EPSP_AMOUNT_PER_EMPLOYER = RecordListKind(
    "ca/rc359.rc359_excess_epsp_amount", fields=(RC359_EXCESS_EPSP_AMOUNT,)
)
T777_LINE_17_PER_FORM = RecordListKind("ca/t777.t777_line_17", fields=(T777_LINE_17,))

# The return's inputs: none. Line 22900 was a starting input until this ticket; it is now computed.
INPUTS: frozenset[str] = frozenset()

# The return's outputs: none (line 22900 is read by the return's own steps).
OUTPUTS: frozenset[str] = frozenset()

STEPS = {
    # Form RC359 line 7 "Excess EPSP amount", the total over the copies: "Add the amount from line 7
    # of each form and include the total on line 22900 of your return."
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/rc359.rc359_excess_epsp_amount"},
        produces={"output": "ca/rc359_excess_epsp_total"},
    ),
    # Form T777 line 17 "Total expenses", the export of the form ca/t777 (one record), read as its
    # total.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t777.t777_line_17"},
        produces={"output": "ca/t777_line_17_total"},
    ),
    # T1 line 22900 "Other employment expenses (see Guide T4044)": the total of Form T777 line 17
    # and the RC359 line 7 total.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t777_line_17_total", "ca/rc359_excess_epsp_total")},
        produces={"output": "ca/other_employment_expenses"},
    ),
}

# The classes of the three steps: the record total of the RC359 copies, the record total of the T777
# line 17 export (one record, the derived kind `ca/t777.t777_line_17`) and the core sum.
WIRING = {
    (
        RecordTotal,
        frozenset({RC359_EXCESS_EPSP_AMOUNT_PER_EMPLOYER}),
        frozenset({RC359_EXCESS_EPSP_TOTAL}),
    ),
    (
        RecordTotal,
        frozenset({T777_LINE_17_PER_FORM}),
        frozenset({T777_LINE_17_TOTAL}),
    ),
    (
        Sum,
        frozenset({T777_LINE_17_TOTAL, RC359_EXCESS_EPSP_TOTAL}),
        frozenset({OTHER_EMPLOYMENT_EXPENSES}),
    ),
}
