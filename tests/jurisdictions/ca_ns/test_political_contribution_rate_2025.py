"""The 2025 `ca-ns/political_contribution_rate` dataset, against Form NS428 (5003-C, 2025).

Form NS428: line 86: "multiplied by 75%". The printed percentage is a rate of 0.75; the
product is a dollars-and-cents line, so it rounds half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns.ns428_credits_support import parameter_source

D = Decimal
FAMILY = "ca-ns/political_contribution_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"


def test_2025_political_contribution_rate_is_75_percent() -> None:
    assert parameter_source().get(FAMILY, 2025, RATE).values == Rate(D("0.75"))


def test_2025_political_contribution_rate_rounds_half_up_to_the_cent() -> None:
    data = parameter_source().get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_political_contribution_rate_cites_the_form() -> None:
    assert parameter_source().get(FAMILY, 2025, RATE).sources == (CRA_FORM_TEXT,)
