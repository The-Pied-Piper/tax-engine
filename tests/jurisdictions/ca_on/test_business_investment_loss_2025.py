"""The 2025 inclusion rate of the allowable business investment loss, checked against CRA's Form
T1436, Capital Gains Worksheet.

Form T1436 (2025), "Line 21700 - Allowable business investment loss", "Calculating your allowable
business investment loss": line 19 "Inclusion rate for 2025 × 50 %"; line 20 "Line 18 multiplied by
the percentage on line 19 ... Enter this amount on line 21700 of your return. Allowable business
investment loss". Line 20 is a dollars-and-cents box, so the product is rounded half-up to the
cent.

The printed 50% is its own rate dataset, not the capital gains inclusion rate of Schedule 3: it is a
different form's printed figure, so each follows its own form.

The dataset is tested with the capability that reads it, on made-up kinds; the worksheet's lines
together, from the earlier years' deductions to line 21700, are in the `end_to_end` tests.
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
FAMILY = "ca/business_investment_loss_inclusion_rate"
T1436_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1436/t1436-25e.pdf"

# Made up for this test and not registered: the loss after the reduction (T1436 line 18) and the
# allowable part of it (line 20).
AFTER_REDUCTION = ArtifactKind("ex/after_reduction", Decimal)
ALLOWABLE = ArtifactKind("ex/allowable", Decimal)


def test_2025_inclusion_rate_is_half() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    # Line 20, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_inclusion_rate_cites_the_t1436_form() -> None:
    assert SOURCE.get(FAMILY, 2025, RATE).sources == (T1436_PDF,)


@pytest.mark.parametrize(
    ("after_reduction", "allowable"),
    [
        # The worked example: a loss of 10,000 with no earlier capital gains deduction.
        ("10000", "5000.00"),
        # Line 15 of 4,000 reduces the loss of 10,000 by line 17, 4,000: 6,000 at 50%.
        ("6000", "3000.00"),
        # Rounded half-up to the cent: 0.01 x 50% is 0.005, a tie, up to 0.01.
        ("0.01", "0.01"),
        ("0", "0.00"),
    ],
)
def test_half_of_the_loss_after_the_reduction_is_the_allowable_loss(
    after_reduction: str, allowable: str
) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), AFTER_REDUCTION, ALLOWABLE)

    result = capability.compute((Artifact(AFTER_REDUCTION, D(after_reduction)),))

    assert result.outputs == (Artifact(ALLOWABLE, D(allowable)),)
