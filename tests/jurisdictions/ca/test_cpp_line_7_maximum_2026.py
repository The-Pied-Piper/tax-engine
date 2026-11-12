"""The 2026 maximum of Schedule 8 Part 3 line 7, checked against CRA's T4127 (Jan 2026).

CRA T4127 (122nd Edition, effective January 1, 2026), as taken into the dataset. The 2026 Schedule
8 (form 5000-S8) is not yet published, so the dataset is provisional. Table 8.3 prints the Year's
Maximum Contributory Earnings (YMCE) as $71,100.00, the figure line 7 caps at.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)
FAMILY = "ca/cpp_line_7_maximum"


def test_2026_line_7_maximum_is_71100_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(Decimal("71100"))
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2026_line_7_maximum_cites_t4127_jan_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    )
