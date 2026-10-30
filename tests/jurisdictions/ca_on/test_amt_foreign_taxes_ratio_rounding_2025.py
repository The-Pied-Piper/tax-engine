"""The 2025 rounding of Form T691 Part 7 line 12, checked against Form T691.

Form T691 (2025) Part 7 line 12: "Line 11 × [Foreign taxes paid for special foreign tax credit (line
9 of Part 4)] / [Foreign taxes paid ...]". The form prints no figure of its own and no rounding
rule, so the repo convention applies: the product over the denominator is a dollars and cents line,
rounded half-up to the cent once, the owner's decision. The dataset is rounding only: it holds no
rate, and the three figures of the fraction are the caller's, as the return carries them.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FAMILY = "ca/amt_foreign_taxes_ratio_rounding"

# Made up for this test and not registered: the amount, the numerator, the denominator and the
# quotient.
AMOUNT = ArtifactKind("ex/amt_part_7_line_11", Decimal)
NUMERATOR = ArtifactKind("ex/amt_part_4_line_9", Decimal)
DENOMINATOR = ArtifactKind("ex/amt_part_7_foreign_taxes_paid", Decimal)
OUTPUT = ArtifactKind("ex/amt_part_7_line_12", Decimal)


def test_2025_amt_foreign_taxes_ratio_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.rounding == CENT


def test_2025_amt_foreign_taxes_ratio_rounding_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("amount", "numerator", "denominator", "result"),
    [
        # 2806.31 × 50 / 100 = 1403.155, a tie, rounded half-up to 1403.16.
        ("2806.31", "50", "100", "1403.16"),
        # 100 × 1 / 3 = 33.333..., rounded once to 33.33.
        ("100", "1", "3", "33.33"),
        # The whole of the foreign taxes is special foreign tax credit: 500 × 300 / 300 = 500.00.
        ("500", "300", "300", "500.00"),
        # No foreign taxes paid: the denominator is 0, so line 12 is 0.00, not an error.
        ("2806.31", "50", "0", "0.00"),
        # No special foreign tax credit: the numerator is 0, so line 12 is 0.00.
        ("2806.31", "0", "100", "0.00"),
    ],
)
def test_applies_the_ratio_as_printed_and_rounds_once(
    amount: str, numerator: str, denominator: str, result: str
) -> None:
    capability = ApplyRatioOrZero(
        SOURCE.get(FAMILY, 2025, ROUNDING_ONLY), AMOUNT, NUMERATOR, DENOMINATOR, OUTPUT
    )

    result_outputs = capability.compute(
        (
            Artifact(AMOUNT, D(amount)),
            Artifact(NUMERATOR, D(numerator)),
            Artifact(DENOMINATOR, D(denominator)),
        )
    ).outputs

    assert result_outputs == (Artifact(OUTPUT, D(result)),)
