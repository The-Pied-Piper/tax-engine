"""The 2025 Part 1 line 99 rate of Form T691: 80% of line 34900, the donations and gifts, checked
against Form T691. Form T691 (2025) Part 1 line 99: "Donations and gifts (line 34900 of your
return) × 80% =". The 80% is the printed percentage of the form, a rate of 0.8, applied to a
dollars-and-cents product, so it is rounded half-up to the cent, the owner's decision, as the form
states no rounding rule.
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
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FAMILY = "ca/amt_donations_and_gifts_rate"

# Made up for this test and not registered: the amount the rate is applied to, and the product.
BASE = ArtifactKind("ex/amt_line_34900", Decimal)
AMOUNT = ArtifactKind("ex/amt_line_99", Decimal)


def test_2025_amt_donations_and_gifts_rate_is_80_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.8"))
    # Part 1 line 99, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == CENT


def test_2025_amt_donations_and_gifts_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("base", "result"),
    [
        ("12.34", "9.87"),
        ("1000", "800.00"),
    ],
)
def test_applies_to_the_base(base: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    result_outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert result_outputs == (Artifact(AMOUNT, D(result)),)
