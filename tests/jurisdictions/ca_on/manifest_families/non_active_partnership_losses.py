"""The CA-ON manifest entries of the shared fact "non active partnership losses" (see
`test_manifest_non_active_partnership_losses.py`).

Two CRA forms ask the very same fact: Form T936 Part 1 line 3 and Form T2048 Chart A line 3 both ask
"Limited or non-active partnership losses (line 12200) other than allowable capital losses". It is
entered once, in the form `ca/non_active_partnership_losses`, a form of its own with no instances,
no step and no computed line, in the part `01j_non_active_partnership_losses.yaml` under the `form:`
key. A targeted exception to taking inputs the way the form does, only for a fact two forms ask
identically.

The form exports the input itself. The form `ca/t2048` reads the export as a record list of one
record and totals it with `core/record_total` into `ca/qbt_partnership_losses` (`t2048.py`), so the
return's own selections here are none: `STEPS`, `WIRING` and `OUTPUTS` are empty.
"""

from __future__ import annotations

from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.catalog import NON_ACTIVE_PARTNERSHIP_LOSSES

# The one input of the form: the amount, entered once. It stays in the return's inputs list
# (`01_inputs.yaml`).
INPUTS = frozenset({NON_ACTIVE_PARTNERSHIP_LOSSES.identifier})

# The form's export is the input itself, read by the other forms as a record list of one record.
FORM_EXPORTS = (NON_ACTIVE_PARTNERSHIP_LOSSES.identifier,)

# The return declares no output for the form and selects no step of its own for it.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

# The form has no step of its own: the export is the input as entered.
FORM_STEPS: set[CapabilitySelection] = set()
FORM_WIRING: set[object] = set()
