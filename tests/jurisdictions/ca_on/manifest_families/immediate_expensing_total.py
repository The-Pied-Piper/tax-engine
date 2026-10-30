"""The CA-ON manifest's immediate expensing total: one limit per person across the statements of
Forms T776, T2125, T2042 and T2121.

Area A endnote 5 of each of the four forms: "The total immediate expensing amount for the tax year
(total of column 9) is limited to the lesser of: the immediate expensing limit, which is equal to
one of the following, whichever is applicable: $1.5 million, if you are not associated with any
other eligible person or partnership (EPOP) in the tax year; amount iii of Area G, if you are
associated with one or more EPOPs in the tax year; zero, if you are associated with one or more
EPOPs and an agreement ... was not filed with the minister in a prescribed form; any amount
allocated by the minister under subsection 1104(3.4) of the Regulations". Guides T4002 and T4036:
"The deduction is limited to $1.5 million per tax year". The forms print the limit for each
statement and are silent on a person who files several; the Guides' "per tax year" is the only
statement of the rule across statements.

These are steps of the return's own form (the once-per-return group, in `03g_immediate_expensing_
total.yaml`, no `form:` key): each of the four forms exports its claim (already) and its limit,
and the return reads the eight derived record lists. The claim is the caller's column 9 and stays an
input; the check refuses a total above the limit and never picks the claim.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.immediate_expensing_agreed_limit import (
    ImmediateExpensingAgreedLimit,
)
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    IMMEDIATE_EXPENSING_AGREED_LIMIT,
    IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    IMMEDIATE_EXPENSING_TOTAL_CLAIM,
    RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
)
from tests.jurisdictions.ca_on.manifest_families import t776, t2042, t2121, t2125

INPUTS: frozenset[str] = frozenset()

OUTPUTS = frozenset({"ca/immediate_expensing_total_claim"})

# One total of column 9 for each form, over its statements (T776 line i, T2125, T2042 and T2121
# Area A "Total of column 9"): the trace shows one line for each form, then the grand total.
STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t776.rental_immediate_expensing_claim"},
        produces={"output": "ca/rental_immediate_expensing_claims_total"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.business_immediate_expensing_claim"},
        produces={"output": "ca/business_immediate_expensing_claims_total"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2042.farm_immediate_expensing_claim"},
        produces={"output": "ca/farm_immediate_expensing_claims_total"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2121.fish_immediate_expensing_claim"},
        produces={"output": "ca/fish_immediate_expensing_claims_total"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rental_immediate_expensing_claims_total",
                "ca/business_immediate_expensing_claims_total",
                "ca/farm_immediate_expensing_claims_total",
                "ca/fish_immediate_expensing_claims_total",
            )
        },
        produces={"output": "ca/immediate_expensing_claims_total"},
    ),
    # The person's one limit, before the days scaling of each statement's fiscal period: the common
    # limit of the statements that claim above 0, in the order rental, business, farm, fish;
    # statements whose limits disagree are refused.
    CapabilitySelection(
        name="ca/immediate_expensing_agreed_limit",
        params={},
        consumes={
            "rental_claims": "ca/t776.rental_immediate_expensing_claim",
            "rental_limits": "ca/t776.rental_immediate_expensing_limit_unprorated",
            "business_claims": "ca/t2125.business_immediate_expensing_claim",
            "business_limits": "ca/t2125.business_immediate_expensing_limit_unprorated",
            "farm_claims": "ca/t2042.farm_immediate_expensing_claim",
            "farm_limits": "ca/t2042.farm_immediate_expensing_limit_unprorated",
            "fish_claims": "ca/t2121.fish_immediate_expensing_claim",
            "fish_limits": "ca/t2121.fish_immediate_expensing_limit_unprorated",
        },
        produces={"output": "ca/immediate_expensing_agreed_limit"},
    ),
    # The total of every statement's column 9 may not be more than the person's limit: refused
    # above it, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/immediate_expensing_claims_total",
            "bound": "ca/immediate_expensing_agreed_limit",
        },
        produces={"output": "ca/immediate_expensing_total_claim"},
    ),
}

WIRING = {
    (
        RecordTotal,
        frozenset({t776.RENTAL_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT}),
        frozenset({RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL}),
    ),
    (
        RecordTotal,
        frozenset({t2125.BUSINESS_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT}),
        frozenset({BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL}),
    ),
    (
        RecordTotal,
        frozenset({t2042.FARM_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT}),
        frozenset({FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL}),
    ),
    (
        RecordTotal,
        frozenset({t2121.FISH_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT}),
        frozenset({FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
                BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
                FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
                FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
            }
        ),
        frozenset({IMMEDIATE_EXPENSING_CLAIMS_TOTAL}),
    ),
    (
        ImmediateExpensingAgreedLimit,
        frozenset(
            {
                t776.RENTAL_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT,
                t776.RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT,
                t2125.BUSINESS_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT,
                t2125.BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT,
                t2042.FARM_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT,
                t2042.FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT,
                t2121.FISH_IMMEDIATE_EXPENSING_CLAIM_PER_STATEMENT,
                t2121.FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED_PER_STATEMENT,
            }
        ),
        frozenset({IMMEDIATE_EXPENSING_AGREED_LIMIT}),
    ),
    (
        AtMost,
        frozenset({IMMEDIATE_EXPENSING_CLAIMS_TOTAL, IMMEDIATE_EXPENSING_AGREED_LIMIT}),
        frozenset({IMMEDIATE_EXPENSING_TOTAL_CLAIM}),
    ),
}
