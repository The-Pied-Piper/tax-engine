"""The 2025 `ca-qc/schedule_k_line_44_one_child_amount` dataset (Schedule K, Part A, line 44).

Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part A, line 44: "If you did not have a spouse on
December 31, 2025, but you had a dependent child (see line 447 in the guide for the definition),
enter $12,350. If you had more than one dependent child, enter $16,570." The dataset holds the
printed 12,350 as printed (claimed whole), the `credit` kind. The line is a dollars-and-cents line,
so the figure rounds half-up to the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-qc/schedule_k_line_44_one_child_amount"
SOURCE_FORM = "Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part A"


def test_2025_amount_is_12350() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("12350"))


def test_2025_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (SOURCE_FORM,)
