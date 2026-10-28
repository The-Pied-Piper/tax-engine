"""The 2025 capital gains inclusion rate, checked against CRA's Schedule 3.

T1-2025 Schedule 3 (form 5000-S3): line 23 "Inclusion rate 50%"; line 24 multiplies line 22
by that percentage; line 26 (line 19900), if positive, goes to T1 line 12700 (taxable capital
gains). Line 24 is a dollars-and-cents box, so the product is rounded half-up to the cent. The
2024 proposal to raise the rate did not proceed: Finance's Report on Federal Tax Expenditures
2026 records that Budget 2025 confirmed the increase would not go ahead.
Netting gains against losses (Schedule 3 line 21) is not modelled yet.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
FAMILY = "ca/capital_gains_inclusion_rate"

# Made up for this test and not registered: the gain the rate applies to, and its taxable part.
GAIN = ArtifactKind("ex/gain", Decimal)
TAXABLE_PART = ArtifactKind("ex/taxable_part", Decimal)


def test_2025_inclusion_rate_is_half() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    # Schedule 3 line 24, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


@pytest.mark.parametrize(
    "source",
    [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s3/5000-s3-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s3/5000-s3-25e.pdf",
        "https://www.canada.ca/en/department-finance/services/publications/federal-tax-expenditures/2026/part-2.html",
    ],
)
def test_2025_inclusion_rate_cites_its_sources(source: str) -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert source in data.sources


@pytest.mark.parametrize(
    ("gain", "taxable"),
    [
        # Return A: a capital gain of $20,000, half of it taxable.
        ("20000", "10000"),
        # Rounded half-up to the cent: 1234.57 × 50% is 617.285, a tie, up to 617.29.
        ("1234.57", "617.29"),
        ("0", "0"),
    ],
)
def test_applies_to_a_capital_gain(gain: str, taxable: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), GAIN, TAXABLE_PART)

    result = capability.compute((Artifact(GAIN, D(gain)),))

    assert result.outputs == (Artifact(TAXABLE_PART, D(taxable)),)
