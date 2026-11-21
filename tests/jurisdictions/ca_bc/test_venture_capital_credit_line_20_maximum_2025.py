"""The 2025 `ca-bc/venture_capital_credit_line_20_maximum` dataset: $120,000, printed on Form BC479
line 20 (CRA 5010). It is a dollars-and-cents or rate figure, so it rounds half-up to the cent,
the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)

D = Decimal
FAMILY = "ca-bc/venture_capital_credit_line_20_maximum"
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(),
    british_columbia_parameter_parsers(),
    british_columbia_units(),
)


def test_2025_figure_is_120000() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("120000"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.tax_year == 2025
