"""The 2025 rate of `ca-ab/cwb_rate`, checked against Schedule 6
(5009-S6, 2025).

Schedule 6 (2025, Alberta edition) line 19: "Rate 21%". The printed percentage is a rate of 0.21;
line 20 is a dollars-and-cents line, so the rate rounds half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/cwb_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-s6/5009-s6-25e.txt"


def test_2025_cwb_rate_is_21_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.21"))


def test_2025_cwb_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_rate_cites_schedule_6() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
