"""The 2025 `ca-qc/ppip_premium_maximum` dataset (5005-R line 91).

5005-R (CRA, 5005-r-25e.txt), page 6: "Line 91 and line 31205: Provincial parental insurance plan
(PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)". The dataset holds the printed
484.12 as printed, the `credit` kind, rounded half-up to the cent (a dollars-and-cents box).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import CONTRIBUTION_TIER
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

D = Decimal
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
FAMILY = "ca-qc/ppip_premium_maximum"
FORM = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt"


def test_2025_line_91_maximum_is_484_12() -> None:
    assert SOURCE.get(FAMILY, 2025, CREDIT).values == Credit(amount=D("484.12"))


def test_2025_line_91_maximum_equals_the_tier_maximum() -> None:
    # The printed maximum and the tier's maximum are the same printed figure.
    tier = SOURCE.get("ca-qc/ppip_premium", 2025, CONTRIBUTION_TIER).values
    assert SOURCE.get(FAMILY, 2025, CREDIT).values.amount == tier.maximum


def test_2025_line_91_maximum_rounds_half_up_to_the_cent() -> None:
    assert SOURCE.get(FAMILY, 2025, CREDIT).rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_91_maximum_cites_the_form() -> None:
    assert SOURCE.get(FAMILY, 2025, CREDIT).sources == (FORM,)
