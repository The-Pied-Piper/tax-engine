"""The CA-ON manifest entries of the shared fact "spouse on December 31" (see
`test_manifest_spouse_on_december_31.py`).

Two CRA forms ask the very same fact: whether the filer had a spouse or common-law partner on
December 31, 2025 (the T1's "Marital status on December 31, 2025" Box 1 Married or Box 2 Living
common-law). Form ON428 reads it before lines 75 and 76, and Schedule ON428-A reads it to choose
Part A or Part B. It is entered once, in the form `ca/spouse_on_december_31`, a form of its own
with no instances, one input and no computed line, in the part `01e_spouse_on_december_31.yaml`
under the `form:` key. A targeted exception to taking inputs the way the form does, only
for a fact two forms ask identically.

The form exports the checked count. The return does not read the export as it is: its steps read
the total `ca/spouse_or_common_law_partner_on_december_31_total` that `core/first_record_count`
makes of the derived kind `ca/spouse_on_december_31.spouse_or_common_law_partner_on_december_31_
checked` (`ontario_tax_reduction.py`), so the return's own selections here are none: `STEPS`,
`WIRING` and `OUTPUTS` are empty.
"""

from __future__ import annotations

from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED,
)

# The one input of the form: the answer, a count of 1 for "Yes" and 0 for "No". It stays in the
# return's inputs list (`01_inputs.yaml`).
INPUTS = frozenset({SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31.identifier})

# The form's export: the checked count, read by the return as a record list of one record.
FORM_EXPORTS = (SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED.identifier,)

# The return declares no output for the form and selects no step of its own for it.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

FORM_STEPS = {
    # T1 "Marital status on December 31, 2025" Box 1 Married or Box 2 Living common-law, the fact
    # that ON428 (before lines 75 and 76) and Schedule ON428-A (Part A or Part B) ask: the answer
    # taken as a count, 1 for a spouse or common-law partner and 0 for none, checked to be 0 or 1.
    # A spouse who died in the year is entered as 0.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/spouse_or_common_law_partner_on_december_31"},
        produces={"output": "ca/spouse_or_common_law_partner_on_december_31_checked"},
    ),
}

FORM_WIRING = {
    (
        YesOrNoCount,
        frozenset({SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31}),
        frozenset({SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED}),
    ),
}
