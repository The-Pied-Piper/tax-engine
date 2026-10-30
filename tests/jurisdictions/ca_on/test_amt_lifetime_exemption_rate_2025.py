"""The 2025 Part 1 line 87 rate of Form T691: 40% of line 25400, the lifetime capital gains
exemption, checked against Form T691. Form T691 (2025) Part 1 line 87: "Lifetime capital gains
exemption: Enter the amount from line 25400 of your return × 40% =". The 40% is the printed
percentage of the form, a rate of 0.40, applied to a dollars-and-cents product, so it is rounded
half-up to the cent, the owner's decision, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FAMILY = "ca/amt_lifetime_exemption_rate"

# Made up for this test and not registered: the amount the rate is applied to, and the product.
BASE = ArtifactKind("ex/amt_line_25400", Decimal)
AMOUNT = ArtifactKind("ex/amt_line_87", Decimal)


def test_2025_amt_lifetime_exemption_rate_is_40_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.40"))
    # Part 1 line 87, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == CENT


def test_2025_amt_lifetime_exemption_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("base", "result"),
    [
        ("2000", "800.00"),
        ("1000.01", "400.00"),
    ],
)
def test_applies_to_the_base(base: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    result_outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert result_outputs == (Artifact(AMOUNT, D(result)),)
