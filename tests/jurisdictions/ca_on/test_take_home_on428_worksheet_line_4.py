"""Worksheet ON428 (ON428 line 72) line 4, from the real part.

Form text (Worksheet ON428, CRA 5006-d-25e.txt): "Line 4: (Line 3 Minus $5,710) multiplied by 20%
(if negative, enter "0") =". The threshold and rate are the `ca-on/surtax_line_66` dataset, the
figures ON428 line 66 prints too.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.on428_worksheet_support import figure, steps

D = Decimal
PART = "on428_worksheet_line_4.yaml"
LINE_3 = "ca-on/on428_worksheet_surtax_base_line_3"
LINE_4 = "ca-on/on428_worksheet_surtax_20_percent_tier_line_4"


@pytest.mark.parametrize(
    ("line_3", "line_4"),
    [
        # (12,463.00 - 5,710) x 20% = 1,350.60.
        ("12463.00", "1350.60"),
        # (5,710.05 - 5,710) x 20% = 0.01.
        ("5710.05", "0.01"),
        # At the threshold, and below it, the difference is not positive: 0.
        ("5710.00", "0.00"),
        ("300.14", "0.00"),
    ],
)
def test_line_4_is_20_percent_of_line_3_over_5710_not_below_zero(
    take_home_service: TakeHomeService, line_3: str, line_4: str
) -> None:
    assert figure(take_home_service, PART, LINE_4, {LINE_3: line_3}) == D(line_4)


def test_line_4_is_one_tiered_surcharge_over_the_line_66_dataset() -> None:
    (step,) = steps(PART)

    assert step["name"] == "core/tiered_surcharge"
    assert step["params"] == {"tiers": "ca-on/surtax_line_66"}
    assert step["consumes"] == {"base": LINE_3}
    assert step["produces"] == {"output": LINE_4}
