"""The 2025 Part 1 line 89 fraction of Form T691: twice line 25395, the capital gains deduction on a
qualifying business transfer, checked against Form T691. Form T691 (2025) Part 1 line 89: "Amount
from line 25395 of your return × 2 =". The multiplier 2 is the printed figure of the form; it is
above one, which the rate kind refuses, so it is a fraction, 2/1, applied to a dollars-and-cents
amount, so the product is rounded half-up to the cent, the owner's decision, as the form states no
rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FAMILY = "ca/amt_qbt_capital_gains_deduction_multiplier"

# Made up for this test and not registered: the amount the fraction is applied to, and the product.
BASE = ArtifactKind("ex/amt_line_25395", Decimal)
AMOUNT = ArtifactKind("ex/amt_line_89", Decimal)


def test_2025_amt_qbt_capital_gains_deduction_multiplier_is_2_over_1() -> None:
    data = SOURCE.get(FAMILY, 2025, FRACTION)

    assert data.values == Fraction(2, 1)
    # Part 1 line 89, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == CENT


def test_2025_amt_qbt_capital_gains_deduction_multiplier_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, FRACTION)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("base", "result"),
    [
        ("1234.56", "2469.12"),
        ("5000", "10000.00"),
    ],
)
def test_applies_to_the_base(base: str, result: str) -> None:
    capability = ApplyFraction(SOURCE.get(FAMILY, 2025, FRACTION), BASE, AMOUNT)

    outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert outputs == (Artifact(AMOUNT, D(result)),)
