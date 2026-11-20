"""The 2025 `ca-qc/tp1_line_457_maximum_premium` dataset (TP-1 line 457).
Revenu Quebec TP-1.G-V (2025-12), guide, line 457: "If the amount on line 97 is more than $484.12,
enter the overpayment (that is, the excess) on line 457." The printed figure is 484.12. It is a
printed figure, so the dataset holds it as printed (claimed whole), the `credit` kind. The line is a
dollars-and-cents line, so the figure rounds half-up to the cent, the project's choice, as the form
states no rounding rule.
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
FAMILY = "ca-qc/tp1_line_457_maximum_premium"
SOURCE_FORM = "Revenu Quebec TP-1.G-V (2025-12), guide, line 457"


def test_2025_line_457_maximum_premium_is_484_12() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("484.12"))


def test_2025_line_457_maximum_premium_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_457_maximum_premium_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (SOURCE_FORM,)
