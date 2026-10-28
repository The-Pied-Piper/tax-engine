"""The 2025 Form T691 Part 4 line 7 rate, 66.6666%, checked against Form T691.

Form T691 (2025) Part 4 line 7: "Total non-business income tax paid to a foreign country (12)"
"× 66.6666%". The percentage is printed as 66.6666%, so the rate is 0.666666, as printed and not
two thirds, applied to a dollars-and-cents line, so the product is rounded half-up to the cent, the
owner's decision, as the form states no rounding rule. Footnote (12) is the caller's definition of
the amount, so the amount is an input and not computed here.
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

FAMILY = "ca/amt_special_foreign_tax_credit_rate"

# Made up for this test and not registered: the amount the rate is applied to, and the product.
BASE = ArtifactKind("ex/amt_part_4_line_7_base", Decimal)
AMOUNT = ArtifactKind("ex/amt_part_4_line_7", Decimal)


def test_2025_special_foreign_tax_credit_rate_is_66_6666_percent_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.666666"))
    # Part 4 line 7, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == CENT


def test_2025_special_foreign_tax_credit_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("base", "result"),
    [
        # 30 × 0.666666 = 19.99998, rounded half-up to 20.00.
        ("30", "20.00"),
        # 600 × 0.666666 = 399.9996, rounded half-up to 400.00 (the Return BG tax paid).
        ("600", "400.00"),
        # 1000 × 0.666666 = 666.666, rounded half-up to 666.67.
        ("1000", "666.67"),
        ("0", "0.00"),
    ],
)
def test_applies_to_the_base(base: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    result_outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert result_outputs == (Artifact(AMOUNT, D(result)),)
