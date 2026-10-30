"""The CA-ON manifest entries of the restricted farm loss applied to farmland (see
`test_manifest.py`).

Guide T4037 p.34 "The amount of RFLs that you can apply cannot be more than the property taxes and
interest on money you borrowed to buy the farmland that were included in the calculation of the RFLs
for each year." and "Also, you have to reduce your RFL balance by these amounts." The filer's
unapplied balance of the property taxes and interest part is one input,
`ca/unapplied_restricted_farm_loss_taxes_and_interest`, declared in `01e_farm_loss_inputs.yaml`.
The steps are in `06h_restricted_farm_loss_applied.yaml`: one capability per list of farmland
dispositions (the four lists: real estate, qualified farm or fishing property, its mortgage
foreclosures list and the other mortgage foreclosures list), their sum, and the check that the sum
is at most the unapplied balance (`core/at_most`; an amount above it is refused, not capped).

The checked total is the amount that reduces the filer's restricted farm loss balance (Guide T4037
p.34); nothing in the return reads it, so it is declared an output, as the other unread checked
amounts in `02_outputs.yaml` are.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.restricted_farm_loss_applied import (
    RestrictedFarmLossApplied,
)
from tax_engine.jurisdictions.ca.catalog import (
    OTHER_FORECLOSURE_DISPOSITIONS,
    OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    QFFP_DISPOSITIONS,
    QFFP_FORECLOSURE_DISPOSITIONS,
    QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    QFFP_RESTRICTED_FARM_LOSS_APPLIED,
    REAL_ESTATE_DISPOSITIONS,
    REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
    RESTRICTED_FARM_LOSS_APPLIED_CHECKED,
    RESTRICTED_FARM_LOSS_APPLIED_TOTAL,
    UNAPPLIED_RESTRICTED_FARM_LOSS_TAXES_AND_INTEREST,
)

# The one input of the part: the unapplied balance of the property taxes and interest part, entered
# once for the return.
INPUTS = frozenset({UNAPPLIED_RESTRICTED_FARM_LOSS_TAXES_AND_INTEREST.identifier})

# The part exports nothing to another form.
OUTPUTS: frozenset[str] = frozenset({"ca/restricted_farm_loss_applied_checked"})

# Guide T4037 p.34: the amount applied on each list, the sum of the three, and the check against the
# unapplied balance (06h_restricted_farm_loss_applied.yaml).
STEPS: set[CapabilitySelection] = {
    CapabilitySelection(
        name="ca/restricted_farm_loss_applied",
        params={},
        consumes={"dispositions": "ca/real_estate_dispositions"},
        produces={"output": "ca/real_estate_restricted_farm_loss_applied"},
    ),
    CapabilitySelection(
        name="ca/restricted_farm_loss_applied",
        params={},
        consumes={"dispositions": "ca/qffp_dispositions"},
        produces={"output": "ca/qffp_restricted_farm_loss_applied"},
    ),
    CapabilitySelection(
        name="ca/restricted_farm_loss_applied",
        params={},
        consumes={"dispositions": "ca/qffp_foreclosure_dispositions"},
        produces={"output": "ca/qffp_foreclosure_restricted_farm_loss_applied"},
    ),
    CapabilitySelection(
        name="ca/restricted_farm_loss_applied",
        params={},
        consumes={"dispositions": "ca/other_foreclosure_dispositions"},
        produces={"output": "ca/other_foreclosure_restricted_farm_loss_applied"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/real_estate_restricted_farm_loss_applied",
                "ca/qffp_restricted_farm_loss_applied",
                "ca/qffp_foreclosure_restricted_farm_loss_applied",
                "ca/other_foreclosure_restricted_farm_loss_applied",
            )
        },
        produces={"output": "ca/restricted_farm_loss_applied_total"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/restricted_farm_loss_applied_total",
            "bound": "ca/unapplied_restricted_farm_loss_taxes_and_interest",
        },
        produces={"output": "ca/restricted_farm_loss_applied_checked"},
    ),
}

WIRING: set[object] = {
    (
        RestrictedFarmLossApplied,
        frozenset({REAL_ESTATE_DISPOSITIONS}),
        frozenset({REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED}),
    ),
    (
        RestrictedFarmLossApplied,
        frozenset({QFFP_DISPOSITIONS}),
        frozenset({QFFP_RESTRICTED_FARM_LOSS_APPLIED}),
    ),
    (
        RestrictedFarmLossApplied,
        frozenset({QFFP_FORECLOSURE_DISPOSITIONS}),
        frozenset({QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED}),
    ),
    (
        RestrictedFarmLossApplied,
        frozenset({OTHER_FORECLOSURE_DISPOSITIONS}),
        frozenset({OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED}),
    ),
    (
        Sum,
        frozenset(
            {
                REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
                QFFP_RESTRICTED_FARM_LOSS_APPLIED,
                QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
                OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
            }
        ),
        frozenset({RESTRICTED_FARM_LOSS_APPLIED_TOTAL}),
    ),
    (
        AtMost,
        frozenset(
            {RESTRICTED_FARM_LOSS_APPLIED_TOTAL, UNAPPLIED_RESTRICTED_FARM_LOSS_TAXES_AND_INTEREST}
        ),
        frozenset({RESTRICTED_FARM_LOSS_APPLIED_CHECKED}),
    ),
}
