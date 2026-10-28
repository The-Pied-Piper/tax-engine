"""The 2025 Ontario minimum tax rate, 24.63%, checked against Form ON428 and Worksheet ON428.

Form ON428 (2025) line 59: "Amount from line 40427 of your return multiplied by 24.63% =", the
Ontario minimum tax carryover credit; Worksheet ON428 "Line 72 - Ontario additional tax for
minimum tax purposes" line 1: "Amount from line 11 of Part 5 of your Form T691 multiplied by
24.63% =". The 24.63% is the
printed percentage of the form, a rate of 0.2463, applied to a dollars-and-cents line, so it is
rounded half-up to the cent, the owner's decision, as the form states no rounding rule. One rate
dataset serves both lines.
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
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FAMILY = "ca-on/minimum_tax_rate"

# Made up for this test and not registered: the amount the rate is applied to, and the product.
BASE = ArtifactKind("ex/on428_line_40427", Decimal)
AMOUNT = ArtifactKind("ex/on428_line_59", Decimal)


def test_2025_ontario_minimum_tax_rate_is_24_63_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.2463"))
    # Line 59 and Worksheet ON428 line 1 are dollars-and-cents lines: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ontario_minimum_tax_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert ON428_TEXT in data.sources


@pytest.mark.parametrize(
    ("base", "result"),
    [
        # 2000 × 0.2463 = 492.6, the carryover claim of Return BG: 492.60.
        ("2000", "492.60"),
        # 1558.95 × 0.2463 = 383.969385, rounded half-up to 383.97 (Return BG's Part 5 line 11 with
        # 150000.00 of security options).
        ("1558.95", "383.97"),
        # 7239.72 × 0.2463 = 1783.143036, rounded half-up to 1783.14 (Return AO's Part 5 line 11).
        ("7239.72", "1783.14"),
        # 0 × 0.2463 = 0.00.
        ("0", "0.00"),
    ],
)
def test_applies_to_the_base(base: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), BASE, AMOUNT)

    outputs = capability.compute((Artifact(BASE, D(base)),)).outputs

    assert outputs == (Artifact(AMOUNT, D(result)),)
