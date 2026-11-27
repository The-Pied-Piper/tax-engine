"""The 2026 `ca-pe/age_rate` dataset, Form PE428 (5002-d-25e.txt) line 5 "Applicable rate 15%"

Rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

D = Decimal
# Prince Edward Island is not in `registrations.JURISDICTIONS` yet, so the source is built over
# its own packages.
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(),
    prince_edward_island_parameter_parsers(),
)
FAMILY = "ca-pe/age_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-d/5002-d-25e.txt"


def test_2026_age_rate_is_0_15() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.15"))


def test_2026_age_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
