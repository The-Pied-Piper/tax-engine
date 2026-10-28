"""The 2025 Schedule 8 Part 5 lines 70 to 88 rates, checked against CRA's 5000-S8.

2025 Schedule 8 (form 5000-S8), Part 5 "Contributions on self-employment income and other earnings
when you also have employment income": "Line 70: Enter the result of the following calculation
(in dollars and cents) on line 31000 of your return. amount from line 43 multiplied by 50% =";
"Line 71: Amount from line 44 multiplied by 50% ="; "Enter whichever is less: Line 75: amount
from line 72 or line 73 Line A multiply by 83.1933 =" and "Line 84: Amount from line 45
multiplied by 50% =".

One dataset per printed rate, as Part 5 lines 48 and 50 each have their own: the 50% of lines 70,
71 and 84 are three `rate` datasets and the 83.1933 of line 75 is a fourth, the same factor as
Part 3 line 9 (`ca/cpp_actual_base_share`, tested in `test_cpp_actual_base_share_2025.py`) as the
dataset of this line. 83.1933 is read as 83.1933%, 0.831933, as line 9 prints it. Each line is a
dollars-and-cents box, so each rounds half-up to the cent, as the form states no rounding rule.
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
S8_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

LINE_70 = "ca/cpp_part_5_line_70_rate"
LINE_71 = "ca/cpp_part_5_line_71_rate"
LINE_75 = "ca/cpp_part_5_line_75_rate"
LINE_84 = "ca/cpp_part_5_line_84_rate"

# Made up for this test and not registered.
LINE_IN = ArtifactKind("ex/line_in", Decimal)
LINE_OUT = ArtifactKind("ex/line_out", Decimal)


@pytest.mark.parametrize(
    ("family", "rate"),
    [
        (LINE_70, "0.5"),
        (LINE_71, "0.5"),
        (LINE_84, "0.5"),
        # 83.1933 is the factor of Part 3 line 9, 83.1933%.
        (LINE_75, "0.831933"),
    ],
)
def test_2025_lines_70_71_75_and_84_are_rates_to_the_cent(family: str, rate: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(D(rate))
    # A dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (S8_TEXT,)


@pytest.mark.parametrize("family", [LINE_70, LINE_71, LINE_84])
@pytest.mark.parametrize(
    ("line_in", "line_out"),
    [
        # The ticket's example: line 43 of 1,118.70 and line 44 of 226.00 give 559.35 and 113.00;
        # line 45 of 696.00 gives 348.00.
        ("1118.70", "559.35"),
        ("226.00", "113.00"),
        ("696.00", "348.00"),
        ("0", "0.00"),
        # Half-up to the cent: 0.01 x 50% is 0.005, a tie, up to 0.01; 0.03 x 50% is 0.015, up to
        # 0.02; 0.02 x 50% is exactly 0.01.
        ("0.01", "0.01"),
        ("0.03", "0.02"),
        ("0.02", "0.01"),
    ],
)
def test_lines_70_71_and_84_are_half_of_their_line_to_the_cent(
    family: str, line_in: str, line_out: str
) -> None:
    capability = ApplyRate(SOURCE.get(family, 2025, RATE), LINE_IN, LINE_OUT)

    result = capability.compute((Artifact(LINE_IN, D(line_in)),))

    assert result.outputs == (Artifact(LINE_OUT, D(line_out)),)


@pytest.mark.parametrize(
    ("line_a", "line_75"),
    [
        # Return BN as filed (line 27 of 20,000, box 16 of 3,500.00): line A is line 73, 138.25.
        # 138.25 x 0.831933 = 115.0147... to 115.01.
        ("138.25", "115.01"),
        # Line A is line 72 (672.35) when line 24 of Part 3 is the more: 672.35 x 0.831933 =
        # 559.3501... to 559.35.
        ("672.35", "559.35"),
        # The maximum: line 72 is 3,356.10 + 678.00 = 4,034.10, and 4,034.10 x 0.831933 =
        # 3,356.1009... to 3,356.10, the maximum of line 11.
        ("4034.10", "3356.10"),
        ("0", "0.00"),
        # 0.08 x 0.831933 = 0.0666... to 0.07, a cent more than 0.06 (line 70 of 1.25).
        ("0.08", "0.07"),
    ],
)
def test_line_75_is_line_a_times_83_1933_percent_to_the_cent(line_a: str, line_75: str) -> None:
    capability = ApplyRate(SOURCE.get(LINE_75, 2025, RATE), LINE_IN, LINE_OUT)

    result = capability.compute((Artifact(LINE_IN, D(line_a)),))

    assert result.outputs == (Artifact(LINE_OUT, D(line_75)),)
