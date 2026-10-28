"""The 2025 Part 1 line 98 rate of Form T691: 50% of line 33800, the net non-refundable tax credits,
checked against Form T691. Form T691 (2025) Part 1 line 98: "Net non-refundable tax credits (line
33800 of your return) × 50% =". The 50% is the printed percentage of the form, a rate of 0.5,
applied to a dollars-and-cents product, so it is rounded half-up to the cent, the owner's
decision, as the form states no rounding rule.
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

FAMILY = "ca/amt_non_refundable_credits_rate"

# Made up for this test and not registered: the amount the rate is applied to, and the product.
BASE = ArtifactKind("ex/amt_line_33800", Decimal)
AMOUNT = ArtifactKind("ex/amt_line_98", Decimal)


def test_2025_amt_non_refundable_credits_rate_is_50_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    # Part 1 line 98, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == CENT


def test_2025_amt_non_refundable_credits_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("base", "result"),
    [
        ("3194.87", "1597.44"),
        ("3100.21", "1550.11"),
    ],
)
def test_applies_to_the_base(base: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    result_outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert result_outputs == (Artifact(AMOUNT, D(result)),)
