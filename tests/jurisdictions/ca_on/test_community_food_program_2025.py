"""The 2025 Ontario community food program donation tax credit rate, checked against CRA's ON428.

2025 ON428 (form 5006-C): line 86 "Line 84 minus line 85 (if negative, enter "0")"; "Community
food program donation tax credit for farmers:"; line 87 and line 62150 "Enter the amount of
qualifying donations that have also been claimed as a charitable donation." "multiplied by 25%
="; line 88 "Line 86 minus line 87 (if negative, enter "0")"; line 90 "Line 88 plus line 89 Enter
this amount on line 42800 of your return. Ontario tax". The 25% is a rate (the `rate` kind), and
line 87 is a dollars-and-cents box, so the product rounds half-up to the cent. The donations are
a caller input, taken as entered: nothing checks them against Schedule 9. Line 88 is line 86 less
line 87, not below zero.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
RATE_FAMILY = "ca-on/community_food_program_rate"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the qualifying donations (line 87's input), the credit
# (line 87), the tax after the LIFT credit (line 86) and the tax after the credit (line 88).
DONATIONS = ArtifactKind("ex/donations", Decimal)
CREDIT = ArtifactKind("ex/credit", Decimal)
TAX_BEFORE = ArtifactKind("ex/tax_before", Decimal)
TAX_AFTER = ArtifactKind("ex/tax_after", Decimal)


def test_2025_rate_is_25_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.25"))
    # ON428 line 87, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_cites_only_the_on428_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (ON428_TEXT,)


@pytest.mark.parametrize(
    ("donations", "credit"),
    [
        # The worked example and Return I: 25% x 1,000.
        ("1000", "250.00"),
        ("1000.00", "250.00"),
        ("0", "0"),
        ("4", "1.00"),
        # 1234.57 x 25% = 308.6425, rounded half-up to 308.64.
        ("1234.57", "308.64"),
        # 0.02 x 25% = 0.005, a tie, up to 0.01; 0.01 x 25% = 0.0025, down to 0.00.
        ("0.02", "0.01"),
        ("0.01", "0.00"),
        # 1000.10 x 25% = 250.025, a tie, up to 250.03.
        ("1000.10", "250.03"),
    ],
)
def test_25_percent_of_the_qualifying_donations(donations: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), DONATIONS, CREDIT)

    result = capability.compute((Artifact(DONATIONS, D(donations)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)


@pytest.mark.parametrize(
    ("line_86", "credit", "line_88"),
    [
        # The worked example: 1,500.00 less 25% of 1,000.
        ("1500.00", "250.00", "1250.00"),
        # Return I: 1,484.56 less 250.00.
        ("1484.56", "250.00", "1234.56"),
        # No donations: line 88 is line 86, as for Returns A to H.
        ("1500.00", "0", "1500.00"),
        # Line 86 of 200.00 is below the credit of 250.00: negative, so 0.
        ("200.00", "250.00", "0"),
        # Equal, and a cent over.
        ("250.00", "250.00", "0"),
        ("250.00", "250.01", "0"),
        ("250.01", "250.00", "0.01"),
        ("0", "250.00", "0"),
    ],
)
def test_the_tax_after_the_credit_is_line_86_less_line_87_not_below_zero(
    line_86: str, credit: str, line_88: str
) -> None:
    capability = SubtractNotBelowZero(TAX_BEFORE, CREDIT, TAX_AFTER)

    result = capability.compute((Artifact(TAX_BEFORE, D(line_86)), Artifact(CREDIT, D(credit))))

    assert result.outputs == (Artifact(TAX_AFTER, D(line_88)),)


@pytest.mark.parametrize(
    ("line_86", "donations", "line_88"),
    [
        # The worked example: line 87 = 25% x 1,000 = 250.00; line 88 = 1,250.00.
        ("1500.00", "1000", "1250.00"),
        # With line 86 of 200.00, line 88 is 0.
        ("200.00", "1000", "0"),
    ],
)
def test_the_two_lines_together(line_86: str, donations: str, line_88: str) -> None:
    credit = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), DONATIONS, CREDIT).compute(
        (Artifact(DONATIONS, D(donations)),)
    )
    (credit_artifact,) = credit.outputs

    result = SubtractNotBelowZero(TAX_BEFORE, CREDIT, TAX_AFTER).compute(
        (Artifact(TAX_BEFORE, D(line_86)), credit_artifact)
    )

    assert result.outputs == (Artifact(TAX_AFTER, D(line_88)),)
