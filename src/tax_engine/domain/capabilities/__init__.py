"""Capabilities: jurisdiction-agnostic mechanisms; parameters come from data.

Each capability registers itself with `@capability` when its module is imported; this package
imports every one of them, so importing the package fills the shared CapabilityRegistry.
`NAMESPACE` comes first because the decorators read it while this file is still being imported.
"""

NAMESPACE = "core"

from tax_engine.domain.capabilities import (  # noqa: E402
    amount_by_count,
    apply_fraction,
    apply_rate,
    apply_ratio,
    at_most,
    capped_amount,
    choose_by_count,
    contribution_tier,
    credit_amount,
    first_record_count,
    greater_of,
    lesser_of,
    multiple_over,
    per_unit_amount,
    progressive_tax,
    record_positive_total,
    record_total,
    subtract,
    subtract_not_below_zero,
    sum,
    sum_not_below_zero,
    tapered_amount,
    tiered_surcharge,
    times_count,
)

__all__ = [
    "NAMESPACE",
    "amount_by_count",
    "apply_fraction",
    "apply_rate",
    "apply_ratio",
    "at_most",
    "capped_amount",
    "choose_by_count",
    "contribution_tier",
    "credit_amount",
    "first_record_count",
    "greater_of",
    "lesser_of",
    "multiple_over",
    "per_unit_amount",
    "progressive_tax",
    "record_positive_total",
    "record_total",
    "subtract",
    "subtract_not_below_zero",
    "sum",
    "sum_not_below_zero",
    "tapered_amount",
    "tiered_surcharge",
    "times_count",
]
