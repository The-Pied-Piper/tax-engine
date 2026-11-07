"""The 2025 rate of `ca/cwb_rate`, checked against Schedule 6 (5000-S6, 2025).

Schedule 6 (2025) line 19: "Rate 27%". The 27% is the printed percentage of the form, a rate of
0.27. Line 20 ("Line 18 multiplied by the percentage from line 19") is a dollars-and-cents line, so
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
CWB_RATE = "ca/cwb_rate"

# Made up for this test and not registered: line 18 (the base) and line 20 (the product).
LINE_18 = AmountKind("ex/line_18")
LINE_20 = AmountKind("ex/line_20")
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"


def test_2025_cwb_rate_is_27_percent() -> None:
    data = SOURCE.get(CWB_RATE, 2025, RATE)

    assert data.values == Rate(D("0.27"))


def test_2025_cwb_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(CWB_RATE, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_rate_cites_schedule_6() -> None:
    data = SOURCE.get(CWB_RATE, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)


@pytest.mark.parametrize(
    ("line_18", "line_20"),
    [
        # Line 18 of 67,000.00 (a $70,000 salary): 67,000.00 x 27% = 18,090.00, already in cents.
        ("67000.00", "18090.00"),
        # Line 18 of 3,000.00 (a $6,000 salary): 3,000.00 x 27% = 810.00.
        ("3000.00", "810.00"),
        # Line 18 of 0, under the base amount: nothing.
        ("0", "0"),
        # 0.50 x 27% = 0.135, a tie, rounded half-up to 0.14.
        ("0.50", "0.14"),
        # 0.01 x 27% = 0.0027, rounded down to 0.00.
        ("0.01", "0.00"),
        # 0.10 x 27% = 0.027, rounded up to 0.03.
        ("0.10", "0.03"),
    ],
)
def test_27_percent_of_line_18_rounded_half_up_to_the_cent(line_18: str, line_20: str) -> None:
    capability = ApplyRate(SOURCE.get(CWB_RATE, 2025, RATE), LINE_18, LINE_20)

    result = capability.compute((Artifact(LINE_18, D(line_18)),))

    assert result.outputs == (Artifact(LINE_20, D(line_20)),)
