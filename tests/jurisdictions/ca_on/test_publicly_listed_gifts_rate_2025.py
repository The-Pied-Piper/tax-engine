"""The 2025 rate on gifts of publicly listed securities, checked against Form T691.

Form T691 (2025) Part 1 line 26: "Line 24 minus line 25" then "30%", the product on line 26. The
30% is the printed percentage of the form, a rate of 0.3, and the product is a dollars-and-cents
line, so it is rounded half-up to the cent, the owner's decision, as the form states no rounding
rule.
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
FAMILY = "ca/publicly_listed_gifts_rate"
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"

# Made up for this test and not registered: the net of line 24 less line 25, and line 26.
NET = ArtifactKind("ex/gifts_net", Decimal)
ADJUSTMENT = ArtifactKind("ex/gifts_adjustment", Decimal)


def test_2025_rate_is_30_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.3"))
    # Part 1 line 26, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("net", "adjustment"),
    [
        ("1000", "300.00"),
        # Rounded half-up to the cent: 1.65 × 30% is 0.495, a tie, up to 0.50.
        ("1.65", "0.50"),
        ("1234.57", "370.37"),
        # Not floored: a net loss gives a negative line 26.
        ("-500", "-150.00"),
        ("0", "0"),
    ],
)
def test_applies_to_the_net_of_lines_24_and_25(net: str, adjustment: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), NET, ADJUSTMENT)

    result = capability.compute((Artifact(NET, D(net)),))

    assert result.outputs == (Artifact(ADJUSTMENT, D(adjustment)),)
