"""The CA-ON manifest entries of Form ON-BEN Part B, the principal residences (see
`test_manifest_on_ben_residences.py`).

Part B is the form `ca-on/on_ben_residences`, one run for each row of the table (the record list
`ca-on/on_ben_residence_rows`, any number), in the part `28a_on_ben_residences.yaml`. The
caller's inputs of one row are the list's fields (the months resident, the amount paid and the
long-term care tick); the form checks the tick and the months against the 12 months of the year
and exports them with the amount; rows are not added. The return reads nothing of the form.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca_on.catalog import (
    ON_BEN_MONTHS_IN_YEAR,
    ON_BEN_RESIDENCE_AMOUNT,
    ON_BEN_RESIDENCE_LONG_TERM_CARE,
    ON_BEN_RESIDENCE_LONG_TERM_CARE_CHECKED,
    ON_BEN_RESIDENCE_MONTHS,
    ON_BEN_RESIDENCE_MONTHS_CHECKED,
)

# The instances input: the rows of the return, any number.
INPUTS = frozenset({"ca-on/on_ben_residence_rows"})

# The caller's inputs of one row, the fields of the list, in the form's column order.
FORM_INPUTS = frozenset(
    {
        ON_BEN_RESIDENCE_MONTHS.identifier,
        ON_BEN_RESIDENCE_AMOUNT.identifier,
        ON_BEN_RESIDENCE_LONG_TERM_CARE.identifier,
    }
)

FORM_EXPORTS = (
    ON_BEN_RESIDENCE_MONTHS_CHECKED.identifier,
    ON_BEN_RESIDENCE_AMOUNT.identifier,
    ON_BEN_RESIDENCE_LONG_TERM_CARE_CHECKED.identifier,
)

# The return declares no output and selects no step for the form; it reads none of its exports.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

FORM_STEPS = {
    # Part B column 5 "Tick this box if it is a long-term care home": 0 or 1, 2 or more refused.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/on_ben_residence_long_term_care"},
        produces={"output": "ca-on/on_ben_residence_long_term_care_checked"},
    ),
    # The 12 months of the year (the dataset as an artifact) and column 3 "Number of months
    # resident in 2025" checked to be at most that, refused above it.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/on_ben_months_in_year"},
        consumes={},
        produces={"output": "ca-on/on_ben_months_in_year"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/on_ben_residence_months",
            "bound": "ca-on/on_ben_months_in_year",
        },
        produces={"output": "ca-on/on_ben_residence_months_checked"},
    ),
}

FORM_WIRING = {
    (
        YesOrNoCount,
        frozenset({ON_BEN_RESIDENCE_LONG_TERM_CARE}),
        frozenset({ON_BEN_RESIDENCE_LONG_TERM_CARE_CHECKED}),
    ),
    (CreditAmount, frozenset(), frozenset({ON_BEN_MONTHS_IN_YEAR})),
    (
        AtMost,
        frozenset({ON_BEN_RESIDENCE_MONTHS, ON_BEN_MONTHS_IN_YEAR}),
        frozenset({ON_BEN_RESIDENCE_MONTHS_CHECKED}),
    ),
}
