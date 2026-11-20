"""The 2025 Quebec PPIP premium tier (`ca-qc/ppip_premium`), checked against the printed forms.

CRA 5005-R, T1-2025 (page 6): "Line 91 and line 31205: Provincial parental insurance plan (PPIP)
premiums paid (box 55 of all T4 slips) (maximum $484.12)". CRA 5005-S10, Schedule 10, Part B: "Line
12: Maximum PPIP insurable income 98,000.00" and "Line 16: PPIP rate on employment income 0.494%".
So the tier is 0.494% of the earnings from 0 to the $98,000 maximum insurable income, with no
exemption, and 0.494% of 98,000 is exactly the printed $484.12. Premiums are in dollars and cents,
so the tier rounds half-up to the cent.
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
FAMILY = "ca-qc/ppip_premium"

# Made up for this test and not registered: the earnings the tier reads, and its premium.
EARNINGS = AmountKind("ex/earnings")
PREMIUM = AmountKind("ex/premium")


def test_2025_ppip_tier_is_0_494_percent_from_0_to_98000_at_most_484_12() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.00494")), D("0"), D("98000"), D("484.12"))
    # Premiums are in dollars and cents.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_the_maximum_insurable_income_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    # No exemption: 98,000 x 0.494% is exactly the printed "(maximum $484.12)".
    assert tier.lower == D("0")
    assert tier.upper * tier.rate.value == tier.maximum


@pytest.mark.parametrize(
    "source",
    [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s10/5005-s10-25e.txt",
    ],
)
def test_2025_ppip_tier_cites_its_sources(source: str) -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert source in data.sources


@pytest.mark.parametrize(
    ("earnings", "premium"),
    [
        # 20,000 x 0.494% = 98.80; 70,000 x 0.494% = 345.80.
        ("20000", "98.80"),
        ("70000", "345.80"),
        # Above the $98,000 maximum insurable income, so the printed maximum.
        ("200000", "484.12"),
        # At the maximum insurable income, and at zero.
        ("98000", "484.12"),
        ("0", "0"),
        # Rounded half-up to the cent: 0.494% of 0.50 is 0.00247, down to 0.00; of 1,012 is
        # 4.99928, up to 5.00.
        ("0.50", "0.00"),
        ("1012", "5.00"),
    ],
)
def test_charges_premiums_on_employment_income(earnings: str, premium: str) -> None:
    capability = TieredContribution(SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, PREMIUM)

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(PREMIUM, D(premium)),)
