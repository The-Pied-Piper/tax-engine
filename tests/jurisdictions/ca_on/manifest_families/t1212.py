"""The CA-ON manifest entries of Form T1212 "Statement of Deferred Security Options Benefits" (see
`test_manifest_t1212.py`).

The form `ca/t1212` runs once (it has no instances): the two amounts the filer enters on line 1 and
line 2, the printed difference of line 3 and the 50% of line 2 that footnote (1) says to enter on
line 24900. Its exports are line 3 and that 50% amount. The return reads the 50% amount only
through `core/record_total` in `05v_security_options_deduction.yaml`, for the security options
deduction of line 24900 and for Form T691 Part 1 line 29 (`deductions.py`), and selects none of the
steps of the form.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.catalog import (
    T1212_LINE_1_OPENING_BALANCE,
    T1212_LINE_2_BENEFITS_NO_LONGER_DEFERRED,
    T1212_LINE_3_CLOSING_BALANCE,
    T1212_LINE_24900_AMOUNT,
)

FORM = "ca/t1212"

# The two amounts of the form, as the filer enters them, in `01p_t1212_inputs.yaml`.
INPUTS = frozenset(
    {
        "ca/t1212_line_1_opening_balance",
        "ca/t1212_line_2_benefits_no_longer_deferred",
    }
)

# The exports of the form: line 3 and the 50% amount of footnote (1).
EXPORTS = frozenset({"ca/t1212_line_3_closing_balance", "ca/t1212_line_24900_amount"})

# The return selects no step of the form and reads no output of it in this family.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

# The steps of the form, one for each printed line that computes, with its line in the comment.
FORM_STEPS = {
    # Line 3 "Closing balance of deferred security options benefits: line 1 minus line 2".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1212_line_1_opening_balance",
            "less": "ca/t1212_line_2_benefits_no_longer_deferred",
        },
        produces={"output": "ca/t1212_line_3_closing_balance"},
    ),
    # Footnote (1) "enter 50% of the amount from line 2 on line 24900 of your return".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/t1212_line_24900_rate"},
        consumes={"base": "ca/t1212_line_2_benefits_no_longer_deferred"},
        produces={"output": "ca/t1212_line_24900_amount"},
    ),
}

FORM_WIRING = {
    (
        Subtract,
        frozenset({T1212_LINE_1_OPENING_BALANCE, T1212_LINE_2_BENEFITS_NO_LONGER_DEFERRED}),
        frozenset({T1212_LINE_3_CLOSING_BALANCE}),
    ),
    (
        ApplyRate,
        frozenset({T1212_LINE_2_BENEFITS_NO_LONGER_DEFERRED}),
        frozenset({T1212_LINE_24900_AMOUNT}),
    ),
}
