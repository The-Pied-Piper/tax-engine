"""Worksheet ON428 (ON428 line 72) line 6, from the real part.

Form text (Worksheet ON428, CRA 5006-d-25e.txt): "Line 6: Line 4 plus line 5 =".
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.on428_worksheet_support import figure, steps

D = Decimal
PART = "on428_worksheet_line_6.yaml"
LINE_4 = "ca-on/on428_worksheet_surtax_20_percent_tier_line_4"
LINE_5 = "ca-on/on428_worksheet_surtax_36_percent_tier_line_5"
LINE_6 = "ca-on/on428_worksheet_surtax_total_line_6"


@pytest.mark.parametrize(
    ("line_4", "line_5", "line_6"),
    [
        # Line 4 is 1,350.60 and line 5 is 1,856.16, so line 6 is 3,206.76.
        ("1350.60", "1856.16", "3206.76"),
        # Only the 20% tier applies: line 5 is 0.
        ("858.00", "0.00", "858.00"),
        ("0.00", "0.00", "0.00"),
    ],
)
def test_line_6_is_line_4_plus_line_5(
    take_home_service: TakeHomeService, line_4: str, line_5: str, line_6: str
) -> None:
    given = {LINE_4: line_4, LINE_5: line_5}

    assert figure(take_home_service, PART, LINE_6, given) == D(line_6)


def test_line_6_is_one_sum_of_line_4_and_line_5_rounded_to_the_cent() -> None:
    (step,) = steps(PART)

    assert step["name"] == "core/sum"
    assert step["params"] == {"rounding": "ca-on/cent_rounding"}
    assert step["consumes"] == {"parts": [LINE_4, LINE_5]}
    assert step["produces"] == {"output": LINE_6}
