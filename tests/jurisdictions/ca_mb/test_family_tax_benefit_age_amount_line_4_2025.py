"""The 2025 `ca-mb/family_tax_benefit_age_amount_line_4` dataset, Schedule MB428-A (5007-a-25e.txt)
line 4 "Claim $2,065": the printed figure, claimed whole (the `credit` kind). Rounds half-up to the
cent, the project's choice, as the form states no rounding rule."""

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
FAMILY = "ca-mb/family_tax_benefit_age_amount_line_4"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-a/5007-a-25e.txt"


def test_2025_family_tax_benefit_age_amount_line_4_is_2065() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("2065"))


def test_2025_family_tax_benefit_age_amount_line_4_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_family_tax_benefit_age_amount_line_4_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
