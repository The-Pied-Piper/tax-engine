"""The 2025 Quebec EI premium tier (`ca-qc/ei_premium`), checked against the printed forms.

CRA 5005-R, T1-2025 (page 6): "Line 89 and line 31200: through employment (maximum $860.67)".
CRA 5005-S10, T1-2025, Schedule 10, Part C: "Line 18: ... (maximum $65,700)", "Line 19: EI rate on
self-employment and other earnings 1.31%" and "Line 20: Line 18 multiplied by the percentage on
line 19 (maximum $860.67)". So the tier is 1.31% of the earnings from 0 to the $65,700 maximum
insurable earnings, with no exemption, and 1.31% of 65,700 is exactly the printed $860.67. Premiums
are in dollars and cents, so the tier rounds half-up to the cent. The T2204 wording for Quebec is a
listed check on the ticket (the form text is not in the repository).
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
FAMILY = "ca-qc/ei_premium"

# Made up for this test and not registered: the earnings the tier reads, and its premium.
EARNINGS = AmountKind("ex/earnings")
PREMIUM = AmountKind("ex/premium")


def test_2025_ei_tier_is_1_31_percent_from_0_to_65700_at_most_860_67() -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert data.values == ContributionTier(Rate(D("0.0131")), D("0"), D("65700"), D("860.67"))
    # Premiums are in dollars and cents.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_is_the_maximum_insurable_earnings_at_the_rate() -> None:
    tier = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER).values

    # No exemption: 65,700 x 1.31% is exactly the printed "(maximum $860.67)".
    assert tier.lower == D("0")
    assert tier.upper * tier.rate.value == tier.maximum


@pytest.mark.parametrize(
    "source",
    [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s10/5005-s10-25e.txt",
    ],
)
def test_2025_ei_tier_cites_its_sources(source: str) -> None:
    data = SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER)

    assert source in data.sources


@pytest.mark.parametrize(
    ("earnings", "premium"),
    [
        # 20,000 x 1.31% = 262.00.
        ("20000", "262.00"),
        # Above the $65,700 maximum insurable earnings, so the printed maximum.
        ("70000", "860.67"),
        ("200000", "860.67"),
        # At the maximum insurable earnings, and at zero.
        ("65700", "860.67"),
        ("0", "0"),
        # Rounded half-up to the cent: 1.31% of 0.30 is 0.00393, down to 0.00; of 3.82 is
        # 0.050042, down to 0.05.
        ("0.30", "0.00"),
        ("3.82", "0.05"),
    ],
)
def test_charges_premiums_on_employment_income(earnings: str, premium: str) -> None:
    capability = TieredContribution(SOURCE.get(FAMILY, 2025, CONTRIBUTION_TIER), EARNINGS, PREMIUM)

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(PREMIUM, D(premium)),)
