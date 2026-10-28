"""Ontario capabilities: mechanisms specific to an Ontario form, registered under `ca-on/`.

Each capability registers itself with `@capability` when its module is imported; this package
imports every one of them, so importing the package fills the shared CapabilityRegistry.
`NAMESPACE` comes first because the decorators read it while this file is still being imported.
"""

NAMESPACE = "ca-on"

from tax_calculator.jurisdictions.ca_on.capabilities import (  # noqa: E402
    capped_record_total,
    caregiver_amount,
    choose_by_range,
    coop_education_credit,
    disability_transfer_amount,
    flow_through_share_expenses,
    provincial_foreign_tax_credit,
    quotient,
    rate_by_income_band,
    record_count,
)

__all__ = [
    "NAMESPACE",
    "capped_record_total",
    "caregiver_amount",
    "choose_by_range",
    "coop_education_credit",
    "disability_transfer_amount",
    "flow_through_share_expenses",
    "provincial_foreign_tax_credit",
    "quotient",
    "rate_by_income_band",
    "record_count",
]
