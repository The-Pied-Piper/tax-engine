"""The 2025 `ca-qc/work_chart_201_maximum` dataset: the maximum of Work Chart 201 line 9.

Revenu Quebec TP-1.D.GR-V (2025-12), Work Chart "Deduction for workers", line 9: "Carry the result
to line 201 of your return (maximum $1,420)." Line 9 is a dollars-and-cents box, so the capped
amount rounds half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.core.capabilities.capped_amount import CappedAmount
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
FAMILY = "ca-qc/work_chart_201_maximum"

# Made up for this test and not registered: the amount capped and the capped result.
BASE = AmountKind("ex/base")
CAPPED = AmountKind("ex/capped")


def test_2025_the_maximum_is_1420() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1420"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_the_maximum_cites_the_form() -> None:
    assert SOURCE.get(FAMILY, 2025, AMOUNT).sources == ("Revenu Quebec TP-1.D.GR-V (2025-12)",)


@pytest.mark.parametrize(
    ("base", "capped"),
    [("1200", "1200.00"), ("1420", "1420.00"), ("4200", "1420.00"), ("0.005", "0.01")],
)
def test_the_lesser_of_the_amount_and_the_maximum(base: str, capped: str) -> None:
    capability = CappedAmount(SOURCE.get(FAMILY, 2025, AMOUNT), BASE, CAPPED)

    result = capability.compute((Artifact(BASE, D(base)),))

    assert str(result.outputs[0].value) == capped
