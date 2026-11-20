"""The 2025 `ca-qc/tp1_zero_line_474_475` dataset (TP-1 lines 474 and 475).

Revenu Quebec TP-1.D-V (2025-12), page 5: line 474 is "Amount from line 470, if it is negative" and
line 475 is "Amount from line 470, if it is positive". No capability returns the positive or
negative part of a signed amount, so each line compares line 470 with a zero (owner decision, 19 Nov
2026). The dataset holds that zero, the `credit` kind. The lines are dollars-and-cents boxes, so
the figure rounds half-up to the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-qc/tp1_zero_line_474_475"
SOURCE_FORM = "Revenu Quebec TP-1.D-V (2025-12), page 5"


def test_2025_zero_is_0() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("0"))


def test_2025_zero_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_zero_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (SOURCE_FORM,)
