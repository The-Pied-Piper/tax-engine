"""The 2025 `ca-qc/work_chart_414_line_14_maximum` dataset (Work Chart 414, TP-1.D.GR-V 2025-12):
the printed $155
held as printed (the `amount` kind), rounded half-up to the cent, the project's choice, as the form
states no rounding rule.
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
FAMILY = "ca-qc/work_chart_414_line_14_maximum"


def test_2025_line_14_maximum_is_the_printed_figure() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(value=D("155"))


def test_2025_line_14_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_14_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == ("Revenu Quebec TP-1.D.GR-V (2025-12), Work Chart 414",)
