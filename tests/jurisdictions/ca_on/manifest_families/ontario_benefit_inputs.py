"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.count_at_least import CountAtLeast
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca.catalog import (
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS,
    SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS_CHECKED,
    SPOUSE_FOR_SEPARATE_RESIDENCES_CHECKED,
)

INPUTS = frozenset(
    {
        # Form ON-BEN, "Application for the 2026 Ontario Trillium Benefit and Ontario Senior
        # Homeowners' Property Tax Grant": the tick boxes of lines 61020, 61040, 61060, 61070,
        # 61080 and 61140 and the amounts of Part A's lines 61100, 61120, 61210 and 61230, as
        # the form takes them. Each is also an output: the form computes nothing from them, and
        # line 61080 is only checked against the spouse fact (part `28_on_ben_checks.yaml`).
        "ca-on/applies_for_energy_and_property_tax_credit",
        "ca-on/applies_for_northern_energy_credit",
        "ca-on/chooses_single_benefit_payment",
        "ca-on/applies_for_senior_homeowners_grant",
        "ca-on/separate_residences_for_medical_reasons",
        "ca-on/lived_in_student_residence",
        "ca-on/rent_paid",
        "ca-on/property_tax_paid",
        "ca-on/reserve_home_energy_costs",
        "ca-on/public_long_term_care_paid",
    }
)

OUTPUTS = frozenset(
    {
        "ca-on/applies_for_energy_and_property_tax_credit",
        "ca-on/applies_for_northern_energy_credit",
        "ca-on/chooses_single_benefit_payment",
        "ca-on/applies_for_senior_homeowners_grant",
        "ca-on/separate_residences_for_medical_reasons",
        "ca-on/spouse_for_separate_residences_checked",
        "ca-on/lived_in_student_residence",
        "ca-on/rent_paid",
        "ca-on/property_tax_paid",
        "ca-on/reserve_home_energy_costs",
        "ca-on/public_long_term_care_paid",
    }
)

STEPS = {
    # Form ON-BEN line 61080 "If, on December 31, 2025, you and your spouse or common-law partner
    # occupied separate principal residences for medical reasons ... tick this box": a tick box,
    # 0 or 1, a count of 2 or more is an input error.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca-on/separate_residences_for_medical_reasons"},
        produces={"output": "ca-on/separate_residences_for_medical_reasons_checked"},
    ),
    # Line 61080 needs a spouse or common-law partner on December 31, 2025 (the T1's "Marital
    # status on December 31, 2025" Box 1 Married or Box 2 Living common-law, the shared fact of the
    # form `ca/spouse_on_december_31`, read as its total, 0 or 1): the tick is at most that count,
    # a tick of 1 with no spouse is an input error.
    CapabilitySelection(
        name="ca/count_at_least",
        params={},
        consumes={
            "count": "ca/spouse_or_common_law_partner_on_december_31_total",
            "minimum": "ca-on/separate_residences_for_medical_reasons_checked",
        },
        produces={"output": "ca-on/spouse_for_separate_residences_checked"},
    ),
}

WIRING = {
    (
        YesOrNoCount,
        frozenset({SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS}),
        frozenset({SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS_CHECKED}),
    ),
    (
        CountAtLeast,
        frozenset(
            {
                SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
                SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS_CHECKED,
            }
        ),
        frozenset({SPOUSE_FOR_SEPARATE_RESIDENCES_CHECKED}),
    ),
}
