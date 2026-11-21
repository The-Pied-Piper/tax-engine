"""The 2026 `ca-nl/venture_capital_credit_lifetime_maximum` dataset, NL428 line 82 guide
(5001-pc-25e.txt): "The lifetime maximum you can claim is $75,000." Provisional, carried forward
from 2025.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/venture_capital_credit_lifetime_maximum"


def test_2026_lifetime_maximum_is_75000() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("75000"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
