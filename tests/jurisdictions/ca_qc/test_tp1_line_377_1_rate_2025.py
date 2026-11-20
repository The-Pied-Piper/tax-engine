"""The 2025 `ca-qc/tp1_line_377_1_rate` dataset (TP-1 line 377.1).

Revenu Quebec TP-1.D-V (2025-12), page 4, Non-refundable tax credits, line 377.1: the printed 14%
is a rate of 0.14. The product is a dollars-and-cents line, so it rounds half-up to the cent, the
project's choice, as the form states no rounding rule.
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
FAMILY = "ca-qc/tp1_line_377_1_rate"
SOURCE_FORM = "Revenu Quebec TP-1.D-V (2025-12), page 4, Non-refundable tax credits"


def test_2025_tp1_line_377_1_rate_is_0_14() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.14"))


def test_2025_tp1_line_377_1_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_tp1_line_377_1_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (SOURCE_FORM,)
