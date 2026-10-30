"""The CA-ON manifest entries of the T4 slip box 26 checks (see `test_manifest.py`).

Schedule 8 Part 3 line 1 and Form RC381 Part 3 lines 1 and 2 take the pensionable earnings from
box 26 of all of the filer's T4 slips as one total, and the form prints "(maximum $81,200 per
slip)". The total is checked against the count of slips times that maximum: an amount above it is
an input error, not capped. The steps are in the return-level manifest part
`05u_t4_cpp_qpp_slip_checks.yaml`; nothing on the return reads the checked kinds.

Boxes 16, 16A, 17 and 17A are not checked. The forms print no maximum for them; a total above the
required contributions is refunded on line 44800 by Schedule 8 line 24 and line 29 (RC381 line 69
and line 74), so the slip values flow as typed.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.catalog import (
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
    T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED,
    T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT,
    T4_CPP_SLIP_COUNT,
    T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC,
    T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED,
    T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT,
    T4_QPP_SLIP_COUNT,
)

INPUTS = frozenset(
    {
        "ca/t4_cpp_pensionable_earnings_outside_quebec",
        "ca/t4_qpp_pensionable_earnings_in_quebec",
        "ca/t4_cpp_slip_count",
        "ca/t4_qpp_slip_count",
    }
)

# The checked kinds are read by nothing on the return: each check is run and its amount refused
# above the bound, so the checked kinds are declared outputs.
OUTPUTS = frozenset(
    {
        "ca/t4_cpp_pensionable_earnings_slip_checked",
        "ca/t4_qpp_pensionable_earnings_slip_checked",
    }
)

STEPS = {
    # Schedule 8 Part 3 line 1 and Form RC381 Part 3 line 1 "Total CPP pensionable earnings from
    # box 26 of all of your T4 slips ... (maximum $81,200 per slip)": the printed maximum for
    # each of the slips counted by `ca/t4_cpp_slip_count`. The product is not a form line.
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/t4_slip_pensionable_earnings_maximum"},
        consumes={
            "count": "ca/t4_cpp_slip_count",
        },
        produces={"output": "ca/t4_cpp_pensionable_earnings_slip_limit"},
    ),
    # Line 1 at most the limit above. Box 26 is totalled over every slip, so the maximum of one
    # slip bounds it only with the count of slips. Nothing on the return reads the checked
    # amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t4_cpp_pensionable_earnings_outside_quebec",
            "bound": "ca/t4_cpp_pensionable_earnings_slip_limit",
        },
        produces={"output": "ca/t4_cpp_pensionable_earnings_slip_checked"},
    ),
    # Form RC381 Part 3 line 2 "Total QPP pensionable earnings from box 26 of all of your T4
    # slips where the province of employment is Quebec ... (maximum $81,200 per slip)": the
    # printed maximum for each of the slips counted by `ca/t4_qpp_slip_count`. The product is
    # not a form line.
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/t4_slip_pensionable_earnings_maximum"},
        consumes={
            "count": "ca/t4_qpp_slip_count",
        },
        produces={"output": "ca/t4_qpp_pensionable_earnings_slip_limit"},
    ),
    # Line 2 at most the limit above. Box 26 is totalled over every slip. Nothing on the return
    # reads the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t4_qpp_pensionable_earnings_in_quebec",
            "bound": "ca/t4_qpp_pensionable_earnings_slip_limit",
        },
        produces={"output": "ca/t4_qpp_pensionable_earnings_slip_checked"},
    ),
}

WIRING = {
    (
        PerUnitAmount,
        frozenset({T4_CPP_SLIP_COUNT}),
        frozenset({T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT}),
    ),
    (
        AtMost,
        frozenset(
            {T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC, T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT}
        ),
        frozenset({T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED}),
    ),
    (
        PerUnitAmount,
        frozenset({T4_QPP_SLIP_COUNT}),
        frozenset({T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT}),
    ),
    (
        AtMost,
        frozenset({T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC, T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT}),
        frozenset({T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED}),
    ),
}
