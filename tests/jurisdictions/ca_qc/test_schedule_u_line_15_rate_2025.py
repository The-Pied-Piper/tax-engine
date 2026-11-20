"""The 2025 `ca-qc/schedule_u_line_15_rate` dataset (Schedule U, Part B). Revenu Quebec TP-1.D-V
(2025-12), Schedule U, Part B, line 15: the printed figure is 1%. It is a printed figure, so
the dataset holds it as printed (a rate), the `rate` kind. The line is a dollars-and-cents
line, so the figure rounds half-up to the cent, the project's choice, as the form states no
rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/schedule_u_line_15_rate"
SOURCE_FORM = "Revenu Quebec TP-1.D-V (2025-12), Schedule U (TP-1.D.U-V), Part B"


def test_2025_schedule_u_line_15_rate_is_0_01() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.01"))


def test_2025_schedule_u_line_15_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_schedule_u_line_15_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (SOURCE_FORM,)
