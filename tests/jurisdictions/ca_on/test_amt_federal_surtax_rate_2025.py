"""The 2025 Form T691 Part 3 line 2 rate, 48%, checked against Form T691.

Form T691 (2025) Part 3 line 2: "Federal surtax on business income earned outside Canada" "Multiply
the amount from line 1 by 48%.", where line 1 is the amount from line 7 of Part 2 (the basic
federal tax). The 48% is the printed percentage of the form, a rate of 0.48, applied to a
dollars-and-cents line, so it is rounded half-up to the cent, the owner's decision, as the form
states no rounding rule. The form prints no floor on line 2, so a negative basic federal tax gives
a negative surtax, which the kind holds.

The same printed 48% is Form T691 (2025) Part 6 line 9, "Federal surtax on business income earned
outside Canada" "Multiply the amount from line 7 by 48%.", which applies to line 7, the federal tax
under the minimum tax, rather than line 1. One rate dataset serves both lines.
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

FAMILY = "ca/amt_federal_surtax_rate"

# Made up for this test and not registered: the amount the rate is applied to, and the product.
BASE = ArtifactKind("ex/amt_line_1", Decimal)
AMOUNT = ArtifactKind("ex/amt_line_2", Decimal)


def test_2025_amt_federal_surtax_rate_is_48_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.48"))
    # Part 3 line 2, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == CENT


def test_2025_amt_federal_surtax_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("base", "result"),
    [
        # 5846.47 × 0.48 = 2806.3056, rounded half-up to 2806.31 (the Return BG basic federal tax).
        ("5846.47", "2806.31"),
        # 100 × 0.48 = 48.00.
        ("100", "48.00"),
        # -1181.85 × 0.48 = -567.288, rounded to the nearest cent, -567.29 (the low-income return,
        # whose basic federal tax is negative); the form prints no floor, so it stays negative.
        ("-1181.85", "-567.29"),
    ],
)
def test_applies_to_the_base_and_keeps_a_negative_base_negative(base: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    result_outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert result_outputs == (Artifact(AMOUNT, D(result)),)


def test_applies_to_part_6_line_9_for_the_surtax_on_line_7() -> None:
    # Part 6 line 9: line 7 of 16951.38 multiplied by the 48%, 8136.6624, rounded half-up to
    # 8136.66.
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    result_outputs = capability.compute((Artifact(BASE, D("16951.38")),)).outputs

    assert result_outputs == (Artifact(AMOUNT, D("8136.66")),)
