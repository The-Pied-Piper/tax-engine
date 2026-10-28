"""The 2025 applicable rate of Form T691 Part 1, checked against Form T691.

Form T691 (2025) Part 1 line 79: "Applicable Rate" "× 50%", and line 80: "Line 78 multiply by the
percentage from line 79" "=". The 50% is the printed percentage of the form, a rate of 0.5, and the
product is a dollars-and-cents line, so it is rounded half-up to the cent, the owner's decision, as
the form states no rounding rule.
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
FAMILY = "ca/amt_applicable_rate"
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"

# Made up for this test and not registered: line 78, and line 80.
BASE = ArtifactKind("ex/amt_line_78", Decimal)
AMOUNT = ArtifactKind("ex/amt_line_80", Decimal)


def test_2025_rate_is_50_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    # Part 1 line 80, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("line_78", "line_80"),
    [
        ("365", "182.50"),
        # Rounded half-up to the cent: 1.01 × 50% is 0.505, a tie, up to 0.51.
        ("1.01", "0.51"),
        # Not floored: a negative line 78 gives a negative line 80.
        ("-150", "-75.00"),
        ("0", "0"),
    ],
)
def test_applies_to_line_78(line_78: str, line_80: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    result = capability.compute((Artifact(BASE, D(line_78)),))

    assert result.outputs == (Artifact(AMOUNT, D(line_80)),)
