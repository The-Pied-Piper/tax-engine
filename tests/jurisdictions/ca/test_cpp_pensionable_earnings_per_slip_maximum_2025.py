"""The 2025 per-slip maximum of CPP pensionable earnings, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 3 line 1: "Total CPP pensionable earnings from box 26
of all of your T4 slips (if box 26 is blank, enter the amount from box 14) (maximum $81,200 per
slip)". The dataset holds that printed figure as an amount, to the cent. The line's step is tested
where the manifest wires it (`ca_on/test_take_home_schedule_8_line_1.py`).
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/cpp_pensionable_earnings_per_slip_maximum"


def test_2025_per_slip_maximum_is_81200_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("81200"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_per_slip_maximum_cites_the_schedule_8_text() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
    )
