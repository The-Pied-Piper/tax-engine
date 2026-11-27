"""The 2025 `ca-mb/age_maximum` dataset, Worksheet MB428 (5007-d-25e.txt), "Line 58080 - Age
amount", line 1 "Maximum amount 3,728.00": the printed figure, claimed whole (the `credit` kind).
Rounds half-up to the cent, the project's choice, as the form states no rounding rule."""

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
FAMILY = "ca-mb/age_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-d/5007-d-25e.txt"


def test_2025_age_maximum_is_3728_00() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("3728.00"))


def test_2025_age_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_age_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
