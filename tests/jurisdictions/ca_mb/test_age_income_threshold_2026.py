"""The 2026 `ca-mb/age_income_threshold` dataset, Worksheet MB428 (5007-d-25e.txt), "Line 58080 -
Age amount", line 3 "Income threshold 27,749.00": the printed figure, claimed whole (the `credit`
kind). Rounds half-up to the cent, the project's choice, as the form states no rounding rule."""

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
FAMILY = "ca-mb/age_income_threshold"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-d/5007-d-25e.txt"


def test_2026_age_income_threshold_is_27749_00() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("27749.00"))


def test_2026_age_income_threshold_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_income_threshold_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
