"""The 2025 `ca-pe/teacher_school_supply_amount_maximum` dataset. The printed maximum of PE428 line
33, claimed whole.

Form text (Form PE428, CRA 5002-c-25e.txt): Line 33 and line 58500: Teacher school supply amount
(maximum $500) The form states no rounding rule, so the figure rounds half-up to the cent (the
project's choice).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/teacher_school_supply_amount_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt"


def test_2025_teacher_school_supply_amount_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("500"))


def test_2025_teacher_school_supply_amount_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_teacher_school_supply_amount_maximum_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
