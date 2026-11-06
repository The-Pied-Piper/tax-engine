"""The 2025 maximum of Schedule 8 Part 3 line 7, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 3 line 7: "Line 5 minus line 6 (if negative, enter "0")
(maximum $67,800)". The dataset holds that printed figure as an amount. The ca_on manifest tests
pin what line 7 produces from it.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/cpp_line_7_maximum"


def test_2025_line_7_maximum_is_67800_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(Decimal("67800"))
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_line_7_maximum_cites_the_schedule_8_text() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
    )
