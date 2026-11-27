"""The 2025 `ca-ab/age_rate` dataset, Worksheet AB428 (5009-d-25e.txt) line 5 "Applicable rate 15%".

Rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/age_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt"
YEAR = 2025


def test_2025_age_rate_is_0_15() -> None:
    data = SOURCE.get(FAMILY, YEAR, RATE)

    assert data.values == Rate(D("0.15"))


def test_2025_age_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_age_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
