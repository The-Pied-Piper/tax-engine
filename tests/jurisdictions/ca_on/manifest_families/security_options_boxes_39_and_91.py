"""The CA-ON manifest entries of the shared fact "T4 boxes 39 and 91" (see
`test_manifest_security_options_boxes_39_and_91.py`).

Two CRA forms ask the very same fact: the total of all amounts in boxes 39 and 91 of the T4 slips.
Form T691 Part 1 line 28 asks it as "Total of all amounts in boxes 39 and 91 of your T4 slips",
the security options deduction under paragraph 110(1)(d) "included on line 24900 of your return".
The Guide 5000-G line 24900 claims "the total of the amounts shown in boxes 39, 41, 91, and 92 of
your T4 slips" on the T1 line 24900. It is entered once, in the form
`ca/security_options_boxes_39_and_91`, a form of its own with no instances, no step and no computed
line, in the part `01f_security_options_boxes_39_and_91.yaml` under the `form:` key. A targeted
exception to taking inputs the way the form does, only for a fact two forms ask identically.

The form exports the input itself. The return does not read the export as it is: its line 24900
sum and T691 line 28 read the total `ca/t4_security_options_boxes_39_and_91_total` that
`core/record_total` makes of the derived kind
`ca/security_options_boxes_39_and_91.t4_security_options_boxes_39_and_91` (`deductions.py`), so the
return's own selections here are none: `STEPS`, `WIRING` and `OUTPUTS` are empty.
"""

from __future__ import annotations

from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.catalog import (
    T4_SECURITY_OPTIONS_BOXES_39_AND_91,
)

# The one input of the form: the total of the T4 amounts, entered once. It stays in the return's
# inputs list (`01_inputs.yaml`).
INPUTS = frozenset({T4_SECURITY_OPTIONS_BOXES_39_AND_91.identifier})

# The form's export is the input itself, read by the return as a record list of one record.
FORM_EXPORTS = (T4_SECURITY_OPTIONS_BOXES_39_AND_91.identifier,)

# The return declares no output for the form and selects no step of its own for it.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

# The form has no step of its own: the export is the input as entered.
FORM_STEPS: set[CapabilitySelection] = set()
FORM_WIRING: set[object] = set()
