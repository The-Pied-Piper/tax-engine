"""The 2025 `ca-qc/schedule_k_monthly_amount_box_60` dataset (Schedule K, Part C, line 88).
Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C, line 88 "Number of months entered in box
60 x $62.00". The printed figure is 62.00. It is a printed figure, so the dataset holds it as
printed (claimed whole), the `credit` kind. The line is a dollars-and-cents line, so the figure
rounds half-up to the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-qc/schedule_k_monthly_amount_box_60"
SOURCE_FORM = "Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C"


def test_2025_monthly_amount_box_60_is_62() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("62.00"))


def test_2025_monthly_amount_box_60_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_monthly_amount_box_60_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (SOURCE_FORM,)
