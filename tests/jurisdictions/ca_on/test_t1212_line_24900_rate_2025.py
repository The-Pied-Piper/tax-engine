"""The 2025 rate of the security options deduction on Form T1212 line 2.

Form T1212 (2025) footnote (1): "To claim your security options deduction on this amount, enter
50% of the amount from line 2 on line 24900 of your return". The 50% is the printed percentage of
the form, a rate of 0.5, and the product is a dollars-and-cents amount, so it is rounded half-up to
the cent, the owner's decision, as the form states no rounding rule.
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
FAMILY = "ca/t1212_line_24900_rate"
T1212_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1212/t1212-25e.pdf"

# Made up for this test and not registered: line 2 and the amount for line 24900.
LINE_2 = ArtifactKind("ex/deferred_benefits_line_2", Decimal)
AMOUNT = ArtifactKind("ex/deferred_benefits_line_24900", Decimal)


def test_2025_rate_is_50_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_cites_the_form_it_is_printed_on() -> None:
    assert T1212_PDF in SOURCE.get(FAMILY, 2025, RATE).sources


@pytest.mark.parametrize(
    ("line_2", "amount"),
    [
        ("5000", "2500.00"),
        ("1234.57", "617.29"),
        # Rounded half-up to the cent: 0.01 × 50% is 0.005, a tie, up to 0.01.
        ("0.01", "0.01"),
        ("0", "0"),
    ],
)
def test_applies_to_line_2(line_2: str, amount: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), LINE_2, AMOUNT)

    result = capability.compute((Artifact(LINE_2, D(line_2)),))

    assert result.outputs == (Artifact(AMOUNT, D(amount)),)
