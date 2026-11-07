"""The 2025 rate of `ca/cwb_reduction_rate`, checked against Schedule 6 (5000-S6, 2025).

Schedule 6 (2025) line 26: "Rate 15%". The 15% is the printed percentage of the form, a rate of
0.15. Line 27 ("Line 25 multiplied by the percentage from line 26") is a dollars-and-cents line, so
the rate is rounded half-up to the cent, as the other Schedule 6 dollar lines are.
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
CWB_REDUCTION_RATE = "ca/cwb_reduction_rate"

# Made up for this test and not registered: line 25 (the base) and line 27 (the product).
LINE_25 = AmountKind("ex/line_25")
LINE_27 = AmountKind("ex/line_27")
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"


def test_2025_cwb_reduction_rate_is_15_percent() -> None:
    data = SOURCE.get(CWB_REDUCTION_RATE, 2025, RATE)

    assert data.values == Rate(D("0.15"))


def test_2025_cwb_reduction_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(CWB_REDUCTION_RATE, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_reduction_rate_cites_schedule_6() -> None:
    data = SOURCE.get(CWB_REDUCTION_RATE, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)


@pytest.mark.parametrize(
    ("line_25", "line_27"),
    [
        # Line 25 of 42,480.00 (a $70,000 salary): 42,480.00 x 15% = 6,372.00, already in cents.
        ("42480.00", "6372.00"),
        # Line 25 of 7,830.00 (a $35,000 salary): 7,830.00 x 15% = 1,174.50, already in cents.
        ("7830.00", "1174.50"),
        # Line 25 of 2,880.00 (a $30,000 salary): 2,880.00 x 15% = 432.00.
        ("2880.00", "432.00"),
        # Line 25 of 0, floored at zero: nothing.
        ("0", "0"),
        # 0.10 x 15% = 0.015, a tie, rounded half-up to 0.02.
        ("0.10", "0.02"),
        # 0.30 x 15% = 0.045, a tie, rounded half-up to 0.05.
        ("0.30", "0.05"),
        # 0.50 x 15% = 0.075, a tie, rounded half-up to 0.08.
        ("0.50", "0.08"),
        # 0.70 x 15% = 0.105, a tie, rounded half-up to 0.11.
        ("0.70", "0.11"),
        # 0.01 x 15% = 0.0015, rounded down to 0.00.
        ("0.01", "0.00"),
        # 0.03 x 15% = 0.0045, rounded down to 0.00.
        ("0.03", "0.00"),
        # 1.01 x 15% = 0.1515, rounded up to 0.15.
        ("1.01", "0.15"),
    ],
)
def test_15_percent_of_line_25_rounded_half_up_to_the_cent(line_25: str, line_27: str) -> None:
    capability = ApplyRate(SOURCE.get(CWB_REDUCTION_RATE, 2025, RATE), LINE_25, LINE_27)

    result = capability.compute((Artifact(LINE_25, D(line_25)),))

    assert result.outputs == (Artifact(LINE_27, D(line_27)),)
