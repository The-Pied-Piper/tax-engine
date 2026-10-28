"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.manifest import CapabilitySelection

INPUTS = frozenset(
    {
        "ca/rl_10_labour_sponsored_fund_amount",
        "ca/political_contributions",
        "ca/wage_loss_replacement_plan_income",
        "ca/resident_in_canada_throughout_2025",
        "ca/aged_18_or_older_at_end_of_2025",
        "ca/spouse_net_income_before_adjustments",
        "ca/spouse_uccb_repayment",
        "ca/spouse_rdsp_income_repayment",
        "ca/spouse_universal_child_care_benefit",
        "ca/spouse_rdsp_income",
        # T1 line 26600 "Line 26600: Did you own or hold specified foreign property where the total
        # cost amount of all such property, at any time in 2025, was more than CAN$100,000? 1 Yes or
        # 2 No": the form computes nothing from it, so it is also an output (0 for No, 1 for Yes).
        "ca/specified_foreign_property_over_100k",
    }
)

OUTPUTS = frozenset(
    {
        "ca/specified_foreign_property_over_100k",
    }
)

STEPS = set[CapabilitySelection]()

WIRING = set[object]()
