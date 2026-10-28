"""The 2025 rate on gifts of publicly listed securities under a security option plan, Form T691.

Form T691 (2025) Part 1 line 31: "Gifts of publicly listed securities acquired under a security
option plan included on line 24900 of your return" "67914" "× 40%", the product subtracted on line
32. The 40% is the printed percentage of the form, a rate of 0.4, and the product is a
dollars-and-cents line, so it is rounded half-up to the cent, the owner's decision, as the form
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
FAMILY = "ca/security_option_gifts_rate"
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"

# Made up for this test and not registered: the gifts under a security option plan, and line 31.
GIFTS = ArtifactKind("ex/security_option_gifts", Decimal)
DEDUCTION = ArtifactKind("ex/security_option_gifts_deduction", Decimal)


def test_2025_rate_is_40_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.4"))
    # Part 1 line 31, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("gifts", "deduction"),
    [
        ("500", "200.00"),
        ("1234.57", "493.83"),
        # Rounded half-up to the cent: 1.2625 × 40% is 0.505, a tie, up to 0.51.
        ("1.2625", "0.51"),
        # Not floored: a negative gift amount gives a negative line 31.
        ("-500", "-200.00"),
        ("0", "0"),
    ],
)
def test_applies_to_the_gifts_under_a_security_option_plan(gifts: str, deduction: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), GIFTS, DEDUCTION)

    result = capability.compute((Artifact(GIFTS, D(gifts)),))

    assert result.outputs == (Artifact(DEDUCTION, D(deduction)),)
