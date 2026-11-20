"""The 2025 `ca-qc/schedule_u_line_18_8_additional_maximum_pensionable_earnings` dataset (Schedule
U, Part B). Revenu Quebec TP-1.D-V (2025-12), Schedule U, Part B, line 18.8: the printed figure is
$81,200. It is a printed figure, so the dataset holds it as printed, the `credit` kind. The line is
a dollars-and-cents line, so the figure rounds half-up to the cent, the project's choice, as the
form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/schedule_u_line_18_8_additional_maximum_pensionable_earnings"
SOURCE_FORM = "Revenu Quebec TP-1.D-V (2025-12), Schedule U (TP-1.D.U-V), Part B"


def test_2025_line_18_8_is_81200() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("81200"))


def test_2025_line_18_8_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_18_8_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (SOURCE_FORM,)
