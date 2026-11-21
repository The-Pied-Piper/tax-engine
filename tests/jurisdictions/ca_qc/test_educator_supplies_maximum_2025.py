"""The 2025 figure of `ca-qc/educator_supplies_maximum`, checked against 5005-R (2025) line 167.

CRA 5005-R (2025), page 8, "Line 167 and line 46900: Eligible educator school supply tax credit
Supplies expenses (maximum $1,000) Line 46800 multiplied by 25% =". The dataset holds the printed
1,000, rounded half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

D = Decimal
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
FAMILY = "ca-qc/educator_supplies_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt"


def test_2025_educator_supplies_maximum_is_1000_00() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1000.00"))


def test_2025_educator_supplies_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_educator_supplies_maximum_cites_5005_r() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (CRA_FORM_TEXT,)
