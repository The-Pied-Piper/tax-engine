"""The 2026 `ca-mb/age_amount_upper_limit` dataset, Worksheet MB428 (5007-d-25e.txt) "Line 58080 -
Age amount": "$52,602 or more, enter 0", the printed limit, claimed whole (the `credit` kind).
Rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_mb.support import (
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
)
FAMILY = "ca-mb/age_amount_upper_limit"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-d/5007-d-25e.txt"


def test_2026_age_amount_upper_limit_is_3728_00() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("52602.00"))


def test_2026_age_amount_upper_limit_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_amount_upper_limit_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
