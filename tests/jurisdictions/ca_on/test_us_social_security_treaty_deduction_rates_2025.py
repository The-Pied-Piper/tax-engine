"""The 2025 U.S. Social Security treaty deduction rates, checked against Guide 5000-G.

Guide 5000-G (2025), "Line 25600 - Additional deductions", "Exempt foreign income": "you can claim a
deduction equal to 15% of the U.S. Social Security benefits, including U.S. Medicare premiums paid
on your behalf, that you reported as income on line 11500 of your return" and "If you have been a
resident of Canada receiving U.S. Social Security benefits continuously during the period starting
before January 1, 1996, and ending in 2025, you can claim a deduction equal to 50% of the U.S.
Social Security benefits received in 2025." Both are `rate` datasets applied to a dollars-and-cents
amount, so each product is rounded half-up to the cent, the owner's decision, as the guide states no
rounding rule.
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
GUIDE_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-g/5000-g-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

STANDARD = "ca/us_social_security_treaty_deduction_rate"
SINCE_BEFORE_1996 = "ca/us_social_security_treaty_deduction_rate_since_before_1996"

# Made up for this test and not registered: the benefits the rate is applied to, and the deduction.
BASE = ArtifactKind("ex/us_social_security_benefits", Decimal)
AMOUNT = ArtifactKind("ex/us_social_security_deduction", Decimal)


@pytest.mark.parametrize(("family", "rate"), [(STANDARD, "0.15"), (SINCE_BEFORE_1996, "0.5")])
def test_2025_rates_are_the_printed_percentages(family: str, rate: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(D(rate))
    assert data.rounding == CENT
    assert GUIDE_TEXT in data.sources


@pytest.mark.parametrize(
    ("family", "base", "result"),
    [
        (STANDARD, "20000", "3000.00"),
        (STANDARD, "12345.67", "1851.85"),
        (SINCE_BEFORE_1996, "20000", "10000.00"),
        (SINCE_BEFORE_1996, "12345.67", "6172.84"),
        (SINCE_BEFORE_1996, "0", "0.00"),
    ],
)
def test_applies_to_the_benefits(family: str, base: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(family, 2025, RATE), BASE, AMOUNT)

    outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert outputs == (Artifact(AMOUNT, D(result)),)
