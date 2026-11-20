"""The 2025 `ca-qc/schedule_k_line_84_maximum` dataset (Schedule K, Part C, line 84).
Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C, line 83 "Add lines 81 and 82 (maximum
$766)" and "is more than $14,669, enter $766 on line 84". The dataset holds the printed 766 as
printed, the `amount` kind. The line is a dollars-and-cents line, so the figure rounds half-up to
the cent, the project's choice, as the form states no rounding rule.
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
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
FAMILY = "ca-qc/schedule_k_line_84_maximum"
SOURCE_FORM = "Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C"


def test_2025_line_84_maximum_is_766() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(value=D("766"))


def test_2025_line_84_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_84_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (SOURCE_FORM,)
