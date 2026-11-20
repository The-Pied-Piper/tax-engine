"""The 2026 dataset of Form T2204 line 3, checked against CRA T4127, 122nd Edition (January 2026).

The 2026 Form T2204 is not published. T4127 Table 8.7 "Employment Insurance 2026 rates and
amounts", row "Canada except QC": maximum annual insurable earnings $68,900.00. Provisional until
the 2026 form text is published.
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
FAMILY = "ca/t2204_maximum_insurable_earnings"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"


def test_2026_line_3_maximum_is_68900() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(value=D("68900.00"))


def test_2026_line_3_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.rounding == CENT


def test_2026_line_3_maximum_cites_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert T4127 in data.sources
