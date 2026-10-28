"""The CA-ON manifest entries of the shared fact "has investment expenses in 2025" (see
`test_manifest_has_investment_expenses.py`).

Form T2048 Part 3 line 24 asks "If you have investment expenses in 2025, complete Chart A ...
Otherwise, enter "0"". That is one answer for the year, and the Chart A amounts it gates are
entered once for the return, so it is entered once, in the form `ca/has_investment_expenses`, a
form of its own with no instances, one input and one step, in the part
`01n_has_investment_expenses.yaml` under the `form:` key, and not for each disposition of the form
`ca/t2048`.

The form exports the checked count. The form `ca/t2048` does not read the export as it is: its
step `core/first_record_count` makes `ca/qbt_has_investment_expenses` of the derived kind
`ca/has_investment_expenses.has_investment_expenses_checked` (`t2048.py`), so the return's own
selections here are none: `STEPS`, `WIRING` and `OUTPUTS` are empty.
"""

from __future__ import annotations

from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca.catalog import (
    HAS_INVESTMENT_EXPENSES,
    HAS_INVESTMENT_EXPENSES_CHECKED,
)

# The one input of the form: the answer, a count of 1 for "Yes" and 0 for "No". It stays in the
# return's inputs list (`01_inputs.yaml`).
INPUTS = frozenset({HAS_INVESTMENT_EXPENSES.identifier})

# The form's export: the checked count, read by the form `ca/t2048` as a record list of one record.
FORM_EXPORTS = (HAS_INVESTMENT_EXPENSES_CHECKED.identifier,)

# The return declares no output for the form and selects no step of its own for it.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

FORM_STEPS = {
    # Form T2048 Part 3 line 24 "If you have investment expenses in 2025": the answer taken as a
    # count, 1 for yes and 0 for no, checked to be 0 or 1.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/has_investment_expenses"},
        produces={"output": "ca/has_investment_expenses_checked"},
    ),
}

FORM_WIRING = {
    (
        YesOrNoCount,
        frozenset({HAS_INVESTMENT_EXPENSES}),
        frozenset({HAS_INVESTMENT_EXPENSES_CHECKED}),
    ),
}
