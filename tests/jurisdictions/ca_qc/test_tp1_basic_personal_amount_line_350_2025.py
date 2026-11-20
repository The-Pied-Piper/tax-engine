"""The 2025 `ca-qc/tp1_basic_personal_amount_line_350` dataset (TP-1 line 350).

Revenu Quebec TP-1.D-V (2025-12), page 4, Non-refundable tax credits, line 350: "Basic personal
amount ... 350 18,571 00". It is a printed figure, so the dataset holds it as printed (claimed
whole), the `credit` kind. Line 350 is a dollars-and-cents line, so the figure rounds half-up to the
cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-qc/tp1_basic_personal_amount_line_350"
SOURCE_FORM = "Revenu Quebec TP-1.D-V (2025-12), page 4, Non-refundable tax credits"


def test_2025_tp1_basic_personal_amount_line_350_is_18571() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("18571"))


def test_2025_tp1_basic_personal_amount_line_350_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_tp1_basic_personal_amount_line_350_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (SOURCE_FORM,)
