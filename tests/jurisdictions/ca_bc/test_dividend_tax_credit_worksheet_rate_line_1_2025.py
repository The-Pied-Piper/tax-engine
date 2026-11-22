"""The 2025 `ca-bc/dividend_tax_credit_worksheet_rate_line_1` dataset, Worksheet 5010-D line 1:
"... multiplied by 1.96% =".

The figure is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice,
as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)
FAMILY = "ca-bc/dividend_tax_credit_worksheet_rate_line_1"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-d/5010-d-25e.txt"


def test_2025_rate_is_0_0196() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.0196"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_cites_the_worksheet() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
