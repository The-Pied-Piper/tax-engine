"""The 2025 `ca-qc/schedule_k_line_83_maximum` dataset (Schedule K, Part C, line 83).
Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C, line 83 "Add lines 81 and 82 (maximum
$766)" and "is more than $14,669, enter $766 on line 84". The dataset holds the printed 766 as
printed, the `amount` kind. The line is a dollars-and-cents line, so the figure rounds half-up to
the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-qc/schedule_k_line_83_maximum"
# Made up for this test and not registered: the amount capped and the capped result.
BASE = AmountKind("ex/base")
CAPPED = AmountKind("ex/capped")
SOURCE_FORM = "Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C"


def test_2025_line_83_maximum_is_766() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(value=D("766"))


def test_2025_line_83_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_83_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (SOURCE_FORM,)


@pytest.mark.parametrize(
    ("base", "capped"),
    [("744.80", "744.80"), ("766", "766.00"), ("1529.07", "766.00"), ("0.005", "0.01")],
)
def test_the_lesser_of_the_amount_and_the_maximum(base: str, capped: str) -> None:
    capability = CappedAmount(SOURCE.get(FAMILY, 2025, AMOUNT), BASE, CAPPED)

    result = capability.compute((Artifact(BASE, D(base)),))

    assert str(result.outputs[0].value) == capped
