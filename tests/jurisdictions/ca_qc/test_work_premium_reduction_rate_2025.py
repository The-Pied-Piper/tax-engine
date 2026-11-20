"""The 2025 `ca-qc/work_premium_reduction_rate` dataset (Schedule P, Part E, column 1 "Work
premium"). Revenu Quebec TP-1.D-V (2025-12), Schedule P (TP-1.D.P-V), Part E, section 2, line 83:
"Multiply line 82 by 10%." The dataset holds the printed 10% (a rate), the `rate` kind. Line 83 is a
dollars-and-cents line, so the product rounds half-up to the cent, the project's choice, as the form
states no rounding rule.
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
FAMILY = "ca-qc/work_premium_reduction_rate"
SOURCE_FORM = "Revenu Quebec TP-1.D-V (2025-12), Schedule P (TP-1.D.P-V), Part E"


def test_2025_work_premium_reduction_rate_is_0_1() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.1"))


def test_2025_work_premium_reduction_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_work_premium_reduction_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (SOURCE_FORM,)
