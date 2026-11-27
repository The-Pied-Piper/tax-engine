"""The 2025 `ca-pe/equity_tax_credit_maximum` dataset. The printed maximum of PE428 line 96,
a plain cap on the sum of lines 94 and 95, not a credit.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 96: Line 94 plus line 95 (maximum $7,000) =". The
form states no rounding rule, so the figure rounds half-up to the cent (the project's choice).
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
FAMILY = "ca-pe/equity_tax_credit_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt"


def test_2025_equity_tax_credit_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("7000"))


def test_2025_equity_tax_credit_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_equity_tax_credit_maximum_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (CRA_FORM_TEXT,)
