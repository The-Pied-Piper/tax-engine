"""The 2025 share of the actual base contributions, checked against CRA's Schedule 8 Part 3.

T1-2025 Schedule 8 (form 5000-S8), Part 3, line 8 and line 50340 "Total actual base and first
additional contributions on CPP pensionable earnings from box 16 of all of your T4 slips"; line 9
"amount from line 8 multiplied by 83.1933% =", the actual base contributions; line 10 "Line 8
minus line 9 =", the actual first additional contributions. So the rate is 83.1933% (0.831933).
Line 9 prints no "(if negative, ...)" and no maximum, and it is in dollars and cents like line 8,
so the product rounds half-up to the cent.
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
FAMILY = "ca/cpp_actual_base_share"
S8_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"
HALF_UP_TO_THE_CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the line 8 amount the rate applies to, and line 9.
LINE_8 = ArtifactKind("ex/line_8", Decimal)
LINE_9 = ArtifactKind("ex/line_9", Decimal)


def test_2025_actual_base_share_is_83_1933_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.831933"))
    # Schedule 8 Part 3 line 9, "amount from line 8 multiplied by 83.1933% =": to the cent.
    assert data.rounding == HALF_UP_TO_THE_CENT


def test_2025_actual_base_share_cites_schedule_8() -> None:
    assert S8_TEXT in SOURCE.get(FAMILY, 2025, RATE).sources


@pytest.mark.parametrize(
    ("line_8", "line_9"),
    [
        # Return BN: box 16 of 3,500.00 is 2,911.7655, to the cent 2,911.77.
        ("3500", "2911.77"),
        # Box 16 equal to the required base and first additional contributions on 60,000
        # (3,361.75): line 9 is 2,796.75, the required base contributions (line 11).
        ("3361.75", "2796.75"),
        ("3500.10", "2911.85"),
        ("1000", "831.93"),
        # Rounded half-up to the cent: 0.99831960 is 1.00.
        ("1.20", "1.00"),
        ("0.01", "0.01"),
        ("0", "0"),
    ],
)
def test_line_9_is_83_1933_percent_of_line_8_to_the_cent(line_8: str, line_9: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), LINE_8, LINE_9)

    result = capability.compute((Artifact(LINE_8, D(line_8)),))

    assert result.outputs == (Artifact(LINE_9, D(line_9)),)
