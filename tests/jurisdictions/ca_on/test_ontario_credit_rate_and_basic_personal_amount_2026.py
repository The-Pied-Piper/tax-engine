"""The 2026 Ontario `credit_rate` and `basic_personal_amount` datasets, checked against T4127
(122nd edition, Jan 2026): Table 8.1 row ON lowest rate V 0.0505, and Table 8.2 row ON basic amount
12,989."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"


def test_2026_credit_rate_is_the_lowest_ontario_rate() -> None:
    data = SOURCE.get("ca-on/credit_rate", 2026, RATE)

    assert data.values == Rate(D("0.0505"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (T4127,)
    assert data.tax_year == 2026


def test_2026_basic_personal_amount() -> None:
    data = SOURCE.get("ca-on/basic_personal_amount", 2026, CREDIT)

    assert data.values == Credit(amount=D("12989"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (T4127,)
    assert data.tax_year == 2026
