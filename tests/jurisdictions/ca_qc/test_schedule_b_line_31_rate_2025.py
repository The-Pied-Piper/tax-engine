"""The 2025 `ca-qc/schedule_b_line_31_rate` dataset, checked against the printed Schedule B.

Revenu Quebec TP-1.D.B-V (2025-12), Schedule B, Part B, line 31: "Amount from line 18 x 18.75%". The
printed 18.75% is a rate of 0.1875. The product is a dollars-and-cents line, so it rounds half-up to
the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-qc/schedule_b_line_31_rate"
SOURCE_FORM = "Revenu Quebec TP-1.D.B-V (2025-12), Schedule B, Part B"


def test_2025_schedule_b_line_31_rate_is_0_1875() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.1875"))


def test_2025_schedule_b_line_31_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_schedule_b_line_31_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (SOURCE_FORM,)
