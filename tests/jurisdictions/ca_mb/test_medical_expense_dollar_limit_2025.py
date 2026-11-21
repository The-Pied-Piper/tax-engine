"""The 2025 `ca-mb/medical_expense_dollar_limit` dataset, from Form MB428 (5007-c-25e.txt) line 47:
"Line 47: Enter whichever is less: $1,728 or the amount from line 46."

The figure rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
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
FAMILY = "ca-mb/medical_expense_dollar_limit"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt"


def test_2025_medical_expense_dollar_limit_value_and_rounding() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1728"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
    assert data.tax_year == 2025
