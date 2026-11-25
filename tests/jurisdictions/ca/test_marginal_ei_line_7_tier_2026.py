"""The 2026 `ca/marginal_ei_line_7_tier` dataset: the band over which a further dollar of T2204
line 3 is a further dollar of line 7.

Not a printed rate: Form T2204 line 7 prints "Amount from line 3 – $2,000 = (if negative, enter
\"0\")". The take-home marginal rate reads the band so that line 7's rate is 1 from the $2,000
exemption (included) up to the maximum insurable earnings (excluded), 0 outside it.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.jurisdictions.ca.capabilities.contribution_tier_rate import TieredContributionRate
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)

D = Decimal
YEAR = 2026
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/marginal_ei_line_7_tier"
MAXIMUM_INSURABLE_EARNINGS = D("68900")

# Made up for this test and not registered: the earnings the tier reads, and its rate.
EARNINGS = AmountKind("ex/earnings")
RATE = AmountKind("ex/rate")


def test_2026_tier_is_one_from_the_exemption_to_the_maximum_insurable_earnings() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(
        Rate(D("1")), D("2000"), MAXIMUM_INSURABLE_EARNINGS, MAXIMUM_INSURABLE_EARNINGS - D("2000")
    )


@pytest.mark.parametrize(
    ("earnings", "rate"),
    [
        ("0", "0"),
        ("1999.99", "0"),
        ("2000", "1"),
        ("2000.01", "1"),
        (str(MAXIMUM_INSURABLE_EARNINGS - D("0.01")), "1"),
        (str(MAXIMUM_INSURABLE_EARNINGS), "0"),
        ("200000", "0"),
    ],
)
def test_2026_rate_starts_at_the_exemption_and_stops_at_the_maximum(
    earnings: str, rate: str
) -> None:
    capability = TieredContributionRate(SOURCE.get(FAMILY, YEAR, CONTRIBUTION_TIER), EARNINGS, RATE)

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(RATE, D(rate)),)
