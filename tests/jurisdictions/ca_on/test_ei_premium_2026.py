"""The 2026 EI premium tier, checked against CRA T4127, 122nd Edition (January 2026).

T4127 Table 8.7 "Employment Insurance 2026 rates and amounts", row "Canada except QC": maximum
annual insurable earnings $68,900.00; employee contribution rate 0.0163; maximum annual employee
premium $1,123.07. Provisional until the 2026 form text is published. Same tier as 2025: the
earnings from 0 to the maximum insurable earnings, with no exemption.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
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

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/ei_premium"
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"

# Made up for this test and not registered: the earnings the tier reads, and its premium.
EARNINGS = AmountKind("ex/earnings")
PREMIUM = AmountKind("ex/premium")


def test_2026_ei_tier_is_1_63_percent_from_0_to_68900_at_most_1123_07() -> None:
    data = SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.0163")), D("0"), D("68900"), D("1123.07"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_ei_tier_cites_t4127() -> None:
    assert T4127 in SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER).sources


def test_2026_ei_tier_does_not_change_2025() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.0164")), D("0"), D("65700"), D("1077.48"))


@pytest.mark.parametrize(
    ("earnings", "premium"),
    [
        # A $70,000 salary is capped at the maximum insurable earnings: the printed maximum.
        ("70000", "1123.07"),
        ("68900", "1123.07"),
        ("20000", "326.00"),
        ("0", "0"),
    ],
)
def test_charges_2026_premiums_on_employment_income(earnings: str, premium: str) -> None:
    capability = TieredContribution(SOURCE.get(FAMILY, 2026, CONTRIBUTION_TIER), EARNINGS, PREMIUM)

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(PREMIUM, D(premium)),)
