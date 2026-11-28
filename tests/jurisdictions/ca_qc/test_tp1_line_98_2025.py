"""The 2025 `ca-qc/tp1_line_98_qpp_contribution` dataset: the tier behind TP-1 line 98, "QPP
contribution. RL-1 slip, box B.A".

The form prints no rate or ceiling for the slip box. The figures are 6.40% from $3,500 to $71,300,
at most $4,339.20, from the Revenu
Quebec page "Maximum Pensionable Earnings and Quebec Pension Plan Contribution Rate" (a web page: a
listed check).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.contribution_tier import TieredContribution
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/tp1_line_98_qpp_contribution"

# Made up for this test and not registered: the earnings the tier reads, and its contribution.
EARNINGS = AmountKind("ex/earnings")
CONTRIBUTION = AmountKind("ex/contribution")


def test_2025_tier_is_98_figures_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.064")), D("0"), D("67800"), D("4339.20"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_the_full_band_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum


def test_2025_tier_cites_the_form_and_the_revenu_quebec_page() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.sources == (
        "Revenu Quebec TP-1.D-V (2025-12)",
        "Revenu Quebec, "
        "Maximum Pensionable Earnings and Quebec Pension Plan Contribution Rate (web page)",
    )


@pytest.mark.parametrize(
    ("earnings", "contribution"),
    [
        ("0", "0.00"),
        ("67800", "4339.20"),
        ("1000000", "4339.20"),
    ],
)
def test_contributes_inside_its_band(earnings: str, contribution: str) -> None:
    capability = TieredContribution(
        SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)
