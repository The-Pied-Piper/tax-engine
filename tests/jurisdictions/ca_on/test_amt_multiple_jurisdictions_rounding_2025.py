"""The 2025 rounding of Form T691 Part 3 line 3, checked against Form T691 and Form T2203.

Form T691 (2025) Part 3 line 3: "If you have to pay tax to multiple jurisdictions, multiply the
amount from line 2 by the percentage in Column 5 of line 52220 on Form T2203." The form prints no
figure of its own and no rounding rule, so the repo convention applies: the product is a dollars
and cents line, rounded half-up to the cent once, the owner's decision. The dataset is rounding
only: it holds no rate, and the percentage is the caller's, as printed (50 for 50%).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FAMILY = "ca/amt_multiple_jurisdictions_rounding"

# Made up for this test and not registered: the amount, the percentage and the product.
AMOUNT = ArtifactKind("ex/amt_line_2", Decimal)
PERCENTAGE = ArtifactKind("ex/t2203_column_5_percentage", Decimal)
OUTPUT = ArtifactKind("ex/amt_line_3", Decimal)


def test_2025_amt_multiple_jurisdictions_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.rounding == CENT


def test_2025_amt_multiple_jurisdictions_rounding_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("amount", "percentage", "result"),
    [
        # 2806.31 × 50 / 100 = 1403.155, a tie, rounded half-up to 1403.16.
        ("2806.31", "50", "1403.16"),
        # 100 × 33 / 100 = 33.00, exactly.
        ("100", "33", "33.00"),
        # Not a multiple jurisdictions case: the percentage is "0", so line 3 is 0.00.
        ("2806.31", "0", "0.00"),
    ],
)
def test_applies_the_percentage_as_printed_and_rounds_once(
    amount: str, percentage: str, result: str
) -> None:
    capability = ApplyPercentage(
        SOURCE.get(FAMILY, 2025, ROUNDING_ONLY), AMOUNT, PERCENTAGE, OUTPUT
    )

    result_outputs = capability.compute(
        (Artifact(AMOUNT, D(amount)), Artifact(PERCENTAGE, D(percentage)))
    ).outputs

    assert result_outputs == (Artifact(OUTPUT, D(result)),)
