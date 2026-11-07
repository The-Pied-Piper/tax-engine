"""The 2025 Ontario LIFT single-filer rate, checked against CRA's ON428-A, Part A, line 18.

2025 Schedule ON428-A (form 5006-A), Part A, "If you were single at the end of the year": line 17
"Line 15 minus line 16 (if negative, enter "0")"; line 18 "Applicable rate 5%"; line 19 "Line 17
multiplied by the percentage from line 18 =". The 5% is a rate (the `rate` kind), and line 19 a
dollars-and-cents box, so the product is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
SINGLE_RATE = "ca-on/lift_single_rate"
ON428_A_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-a/5006-a-25e.txt"

# Made up for this test and not registered: line 17 (the excess over the threshold, the base) and
# line 19 (the product, the reduction).
LINE_17 = AmountKind("ex/line_17")
LINE_19 = AmountKind("ex/line_19")


def test_2025_single_rate_is_5_percent() -> None:
    data = SOURCE.get(SINGLE_RATE, 2025, RATE)

    assert data.values == Rate(D("0.05"))
    # ON428-A line 19, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_single_rate_cites_only_the_on428_a_text() -> None:
    assert SOURCE.get(SINGLE_RATE, 2025, RATE).sources == (ON428_A_TEXT,)


@pytest.mark.parametrize(
    ("line_17", "line_19"),
    [
        # Line 17 of 36,835.00 (a $70,000 salary): 36,835.00 x 5% = 1,841.75, already in cents.
        ("36835.00", "1841.75"),
        # Line 17 of 7,135.00 (a $40,000 salary): 7,135.00 x 5% = 356.75.
        ("7135.00", "356.75"),
        # Line 17 of 0, under the threshold: no reduction.
        ("0", "0"),
        # 0.10 x 5% = 0.005, a tie, rounded half-up to 0.01.
        ("0.10", "0.01"),
        # 0.09 x 5% = 0.0045, rounded down to 0.00.
        ("0.09", "0.00"),
        # 10.10 x 5% = 0.505, a tie, rounded half-up to 0.51.
        ("10.10", "0.51"),
    ],
)
def test_5_percent_of_line_17_rounded_half_up_to_the_cent(line_17: str, line_19: str) -> None:
    capability = ApplyRate(SOURCE.get(SINGLE_RATE, 2025, RATE), LINE_17, LINE_19)

    result = capability.compute((Artifact(LINE_17, D(line_17)),))

    assert result.outputs == (Artifact(LINE_19, D(line_19)),)
