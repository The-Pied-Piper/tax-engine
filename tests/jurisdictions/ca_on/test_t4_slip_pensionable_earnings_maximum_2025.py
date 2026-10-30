"""The 2025 per-slip maximum `ca/t4_slip_pensionable_earnings_maximum`, checked against CRA.

Schedule 8 (5000-S8) Part 3 line 1 "(maximum $81,200 per slip)" and Form RC381 Part 3 line 2: the
most one T4 slip can show. Times the count of T4 slips it bounds the total over all the slips
(`core/per_unit_amount`). One amount, the `amount` kind, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FAMILY = "ca/t4_slip_pensionable_earnings_maximum"
BASE = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/"


def test_2025_t4_slip_pensionable_earnings_maximum_is_81200_00() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("81200.00"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (
        BASE + "5000-s8/5000-s8-25e.txt",
        BASE + "rc381/rc381-25e.pdf",
    )
