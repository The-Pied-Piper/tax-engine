"""The 2025 rate of `ca/cwb_rate`, checked against Schedule 6 (5000-S6, 2025).

Schedule 6 (2025) line 19: "Rate 27%". The 27% is the printed percentage of the form, a rate of
0.27. Line 20 ("Line 18 multiplied by the percentage from line 19") is a dollars-and-cents line, so
the rate is rounded half-up to the cent, as the other Schedule 6 dollar lines are.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
CWB_RATE = "ca/cwb_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"


def test_2025_cwb_rate_is_27_percent() -> None:
    data = SOURCE.get(CWB_RATE, 2025, RATE)

    assert data.values == Rate(D("0.27"))


def test_2025_cwb_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(CWB_RATE, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_rate_cites_schedule_6() -> None:
    data = SOURCE.get(CWB_RATE, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
