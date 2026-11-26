"""The 2025 `ca-pe/medical_expense_dollar_limit` dataset. The printed ceiling of line 44, a plain
cap, not a credit.

Form text (Form PE428, CRA 5002-c-25e.txt): Line 44: Enter whichever is less: $1,678 or the amount
on line 43. The form states no rounding rule, so the figure rounds half-up to the cent (the
project's choice).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
    prince_edward_island_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(),
    prince_edward_island_parameter_parsers(),
    prince_edward_island_units(),
)
FAMILY = "ca-pe/medical_expense_dollar_limit"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt"


def test_2025_medical_expense_dollar_limit_value() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1678"))
    assert data.unit == prince_edward_island_units().unit("ca/cad")


def test_2025_medical_expense_dollar_limit_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_medical_expense_dollar_limit_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (CRA_FORM_TEXT,)
