"""The CA-ON manifest entries of the U.S. Social Security treaty deduction (see `test_manifest.py`).

Guide 5000-G "Line 25600 - Additional deductions", "Exempt foreign income": under the Canada-U.S.
tax treaty a filer can deduct 15% of the U.S. Social Security benefits, including U.S. Medicare
premiums paid on their behalf, reported on line 11500, or 50% for a resident of Canada receiving
the benefits continuously since before January 1, 1996. The benefits and the 0 or 1 answer are
inputs (`01i_us_social_security_inputs.yaml`); the steps are in
`06i_us_social_security_treaty_deduction.yaml`. The deduction is added to the filer's other
additional deductions in `ca/additional_deductions_total`, the line 25600 total that T1 line 68 and
the forms naming amounts "included on line 25600" read.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS,
    ADDITIONAL_DEDUCTIONS_TOTAL,
    OTHER_PENSIONS_AND_SUPERANNUATION,
    US_SOCIAL_SECURITY_BENEFITS,
    US_SOCIAL_SECURITY_BENEFITS_CHECKED,
    US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE,
    US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE,
    US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996,
    US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996_CHECKED,
    US_SOCIAL_SECURITY_TREATY_DEDUCTION,
)

INPUTS = frozenset(
    {
        "ca/us_social_security_benefits",
        "ca/us_social_security_resident_since_before_1996",
    }
)

# Every kind is read by a later step, so the part exports none.
OUTPUTS = frozenset[str]()

STEPS = {
    # The benefits are part of line 11500, so at most it; refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/us_social_security_benefits",
            "bound": "ca/other_pensions_and_superannuation",
        },
        produces={"output": "ca/us_social_security_benefits_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/us_social_security_resident_since_before_1996"},
        produces={"output": "ca/us_social_security_resident_since_before_1996_checked"},
    ),
    # "a deduction equal to 15% of the U.S. Social Security benefits".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/us_social_security_treaty_deduction_rate"},
        consumes={"base": "ca/us_social_security_benefits_checked"},
        produces={"output": "ca/us_social_security_deduction_at_standard_rate"},
    ),
    # "a deduction equal to 50% of the U.S. Social Security benefits received in 2025".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/us_social_security_treaty_deduction_rate_since_before_1996"},
        consumes={"base": "ca/us_social_security_benefits_checked"},
        produces={"output": "ca/us_social_security_deduction_at_resident_rate"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/us_social_security_resident_since_before_1996_checked",
            "when_none": "ca/us_social_security_deduction_at_standard_rate",
            "when_any": "ca/us_social_security_deduction_at_resident_rate",
        },
        produces={"output": "ca/us_social_security_treaty_deduction"},
    ),
    # Line 25600: the filer's specified deductions plus the treaty deduction.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/additional_deductions",
                "ca/us_social_security_treaty_deduction",
            )
        },
        produces={"output": "ca/additional_deductions_total"},
    ),
}

WIRING = {
    (
        AtMost,
        frozenset({US_SOCIAL_SECURITY_BENEFITS, OTHER_PENSIONS_AND_SUPERANNUATION}),
        frozenset({US_SOCIAL_SECURITY_BENEFITS_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996}),
        frozenset({US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996_CHECKED}),
    ),
    (
        ApplyRate,
        frozenset({US_SOCIAL_SECURITY_BENEFITS_CHECKED}),
        frozenset({US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE}),
    ),
    (
        ApplyRate,
        frozenset({US_SOCIAL_SECURITY_BENEFITS_CHECKED}),
        frozenset({US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996_CHECKED,
                US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE,
                US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE,
            }
        ),
        frozenset({US_SOCIAL_SECURITY_TREATY_DEDUCTION}),
    ),
    (
        Sum,
        frozenset({ADDITIONAL_DEDUCTIONS, US_SOCIAL_SECURITY_TREATY_DEDUCTION}),
        frozenset({ADDITIONAL_DEDUCTIONS_TOTAL}),
    ),
}
