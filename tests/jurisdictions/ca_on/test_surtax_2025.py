"""The 2025 Ontario surtax tiers, checked against CRA's ON428.

2025 ON428 (form 5006-C): line 65 "Line 63 minus line 64 (if negative, enter "0")" is the surtax
base; line 66 "(Line 65 minus $5,710) multiplied by 20% (if negative, enter "0")"; line 67 "(Line
65 minus $7,307) multiplied by 36% (if negative, enter "0")"; line 68 "Line 66 plus line 67" is
the surtax. Each tier is a separate line, so each is its own part; lines 66 and 67 are
dollars-and-cents boxes, so each part is rounded half-up to the cent before line 68 adds them.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FAMILY = "ca-on/surtax"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the tax the surtax is on, and the surtax.
TAX = ArtifactKind("ex/tax", Decimal)
SURTAX = ArtifactKind("ex/surtax", Decimal)


def test_2025_tiers_are_20_percent_over_5710_and_36_percent_over_7307() -> None:
    data = SOURCE.get(FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers(
        (
            SurchargeTier(D("5710"), Rate(D("0.20"))),
            SurchargeTier(D("7307"), Rate(D("0.36"))),
        )
    )
    # ON428 lines 66 and 67, dollars-and-cents boxes: each part half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_tiers_cite_only_the_on428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, SURCHARGE_TIERS)

    assert data.sources == (ON428_TEXT,)


@pytest.mark.parametrize(
    ("tax", "surtax"),
    [
        # Return A: Ontario tax after credits of 7671.98, above both thresholds:
        # (7671.98 - 5710) x 20% = 392.396, so 392.40, plus (7671.98 - 7307) x 36% = 131.3928,
        # so 131.39.
        ("7671.98", "523.79"),
        # Returns C and D: below the first threshold, so no surtax.
        ("1700.15", "0"),
        ("3750.97", "0"),
        # At the first threshold nothing is over it; a cent above, 20% of the cent is 0.002,
        # rounded half-up to 0.00.
        ("5710", "0"),
        ("5710.01", "0.00"),
        # At the second threshold only the first tier charges: 1597 x 20%.
        ("7307", "319.40"),
        # A cent above it: 1597.01 x 20% = 319.402, so 319.40, plus 0.01 x 36% = 0.0036, so
        # 0.00; each part is rounded, not the sum, which would give 319.41.
        ("7307.01", "319.40"),
        ("0", "0"),
    ],
)
def test_surcharges_the_ontario_tax(tax: str, surtax: str) -> None:
    capability = TieredSurcharge(SOURCE.get(FAMILY, 2025, SURCHARGE_TIERS), TAX, SURTAX)

    result = capability.compute((Artifact(TAX, D(tax)),))

    assert result.outputs == (Artifact(SURTAX, D(surtax)),)
