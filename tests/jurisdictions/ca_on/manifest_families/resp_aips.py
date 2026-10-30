"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.catalog import (
    RESP_AIPS_ADDITIONAL_TAX,
    RESP_AIPS_CONTRIBUTIONS_COUNTED,
    RESP_AIPS_LIFETIME_LIMIT,
    RESP_AIPS_LIMIT_REMAINING,
    RESP_AIPS_PART_A_APPLIES_CHECKED,
    RESP_AIPS_PART_A_TAX,
    RESP_AIPS_PART_B_TAX,
    RESP_AIPS_RECEIVED_PART_A,
    RESP_AIPS_RECEIVED_PART_B,
    RESP_AIPS_REDUCTION,
    RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS,
    RESP_AIPS_RRSP_CONTRIBUTIONS,
    RESP_AIPS_SUBJECT_TO_TAX,
)

INPUTS = frozenset(
    {
        "ca/resp_aips_received_part_a",
        "ca/resp_aips_rrsp_contributions",
        "ca/resp_aips_reduction_used_in_previous_years",
        "ca/resp_aips_received_part_b",
        "ca/resp_aips_part_a_applies",
    }
)

OUTPUTS = frozenset[str]()

STEPS = {
    # Form T1172 Part A, line 3 "Amount from line 1 or 2, whichever is less": line 1 (68270)
    # "Total of all AIPs you received or the promoter had transferred to an RRSP, PRPP or SPP on
    # your behalf, during the year." and line 2 "Total amounts you or your promoter contributed
    # on your behalf to your RRSP, PRPP, or SPP, or the RRSP or SPP of your spouse or common-law
    # partner, in the year you received the AIPs or the first 60 days of the following year,
    # that you deducted on line 20800 of your income tax and benefit return for the year you
    # received the AIPs.", both the caller's.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/resp_aips_received_part_a", "ca/resp_aips_rrsp_contributions")},
        produces={"output": "ca/resp_aips_contributions_counted"},
    ),
    # Line 4 "Maximum lifetime RRSP contribution limit that can be used to reduce or eliminate
    # the amount of AIPs subject to the additional tax $ 50,000.00", the dataset as an artifact
    # of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/resp_aips_lifetime_limit"},
        consumes={},
        produces={"output": "ca/resp_aips_lifetime_limit"},
    ),
    # Line 6 "Line 4 minus line 5": line 5 "Total of all amounts used to reduce the amount of
    # additional tax payable on AIPs received in previous years (if applicable). This amount is
    # the total of the amount entered at line 5 of all T1172 forms you filed for 1998 and at
    # line 7 of all T1172 forms you filed for 1999 and later", the caller's, with no floor on
    # the line.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/resp_aips_lifetime_limit",
            "less": "ca/resp_aips_reduction_used_in_previous_years",
        },
        produces={"output": "ca/resp_aips_limit_remaining"},
    ),
    # Line 7 "Amount from line 3 or 6, whichever is less".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/resp_aips_contributions_counted", "ca/resp_aips_limit_remaining")
        },
        produces={"output": "ca/resp_aips_reduction"},
    ),
    # Line 8 "Amount of AIPs subject to the additional tax: line 1 minus line 7".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/resp_aips_received_part_a", "less": "ca/resp_aips_reduction"},
        produces={"output": "ca/resp_aips_subject_to_tax"},
    ),
    # Line 9 "Rate of the additional tax on AIPs" (20%) and line 10 "Additional tax on AIPs:
    # line 8 multiplied by line 9." (Part C, for a resident of Quebec on December 31, is not
    # triggered on an Ontario resident's return).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/resp_aips_part_a_rate"},
        consumes={"base": "ca/resp_aips_subject_to_tax"},
        produces={"output": "ca/resp_aips_part_a_tax"},
    ),
    # Part B "Fill out this part only if Part A does not apply to you.": line 11 (68280) "Total
    # of all AIPs you received from RESPs during the year.", the caller's, line 12 "Rate of the
    # additional tax on AIPs" (20%) and line 13 "Additional tax on AIPs: line 11 multiplied by
    # line 12.".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/resp_aips_part_b_rate"},
        consumes={"base": "ca/resp_aips_received_part_b"},
        produces={"output": "ca/resp_aips_part_b_tax"},
    ),
    # A count of 1 when Part A applies (a caller's 0 or 1, as the form takes the original
    # subscriber and the other listed cases) chooses line 10 over line 13, the amount the form
    # says to enter on line 41800; a count of 0 is Part B.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/resp_aips_part_a_applies_checked",
            "when_none": "ca/resp_aips_part_b_tax",
            "when_any": "ca/resp_aips_part_a_tax",
        },
        produces={"output": "ca/resp_aips_additional_tax"},
    ),
}

WIRING = {
    (
        LesserOf,
        frozenset({RESP_AIPS_RECEIVED_PART_A, RESP_AIPS_RRSP_CONTRIBUTIONS}),
        frozenset({RESP_AIPS_CONTRIBUTIONS_COUNTED}),
    ),
    (CreditAmount, frozenset({}), frozenset({RESP_AIPS_LIFETIME_LIMIT})),
    (
        Subtract,
        frozenset({RESP_AIPS_LIFETIME_LIMIT, RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS}),
        frozenset({RESP_AIPS_LIMIT_REMAINING}),
    ),
    (
        LesserOf,
        frozenset({RESP_AIPS_CONTRIBUTIONS_COUNTED, RESP_AIPS_LIMIT_REMAINING}),
        frozenset({RESP_AIPS_REDUCTION}),
    ),
    (
        Subtract,
        frozenset({RESP_AIPS_RECEIVED_PART_A, RESP_AIPS_REDUCTION}),
        frozenset({RESP_AIPS_SUBJECT_TO_TAX}),
    ),
    (ApplyRate, frozenset({RESP_AIPS_SUBJECT_TO_TAX}), frozenset({RESP_AIPS_PART_A_TAX})),
    (ApplyRate, frozenset({RESP_AIPS_RECEIVED_PART_B}), frozenset({RESP_AIPS_PART_B_TAX})),
    (
        ChooseByCount,
        frozenset({RESP_AIPS_PART_A_APPLIES_CHECKED, RESP_AIPS_PART_B_TAX, RESP_AIPS_PART_A_TAX}),
        frozenset({RESP_AIPS_ADDITIONAL_TAX}),
    ),
}
