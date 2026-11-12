"""The 2026 per-slip maximum of CPP pensionable earnings, checked against CRA's T4127 (Jan 2026).

CRA T4127 (122nd Edition, effective January 1, 2026), as taken into the dataset. The 2026 Schedule
8 (form 5000-S8) is not yet published, so the dataset is provisional. Table 8.6 prints the Year's
Additional Maximum Pensionable Earnings (YAMPE) as $85,000.00, the figure Schedule 8 Part 3 line 1
caps the earnings at.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)
FAMILY = "ca/cpp_pensionable_earnings_per_slip_maximum"


def test_2026_per_slip_maximum_is_85000_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("85000"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_per_slip_maximum_cites_t4127_jan_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    )
