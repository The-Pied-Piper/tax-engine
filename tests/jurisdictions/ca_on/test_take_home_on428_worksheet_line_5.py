"""Worksheet ON428 (ON428 line 72) line 5, from the real part.

Form text (Worksheet ON428, CRA 5006-d-25e.txt): "Line 5: (Line 3 Minus $7,307) multiplied by 36%
(if negative, enter "0") =". The threshold and rate are the `ca-on/surtax_line_67` dataset, the
figures ON428 line 67 prints too.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.on428_worksheet_support import figure, steps

D = Decimal
PART = "on428_worksheet_line_5.yaml"
LINE_3 = "ca-on/on428_worksheet_surtax_base_line_3"
LINE_5 = "ca-on/on428_worksheet_surtax_36_percent_tier_line_5"


@pytest.mark.parametrize(
    ("line_3", "line_5"),
    [
        # (12,463.00 - 7,307) x 36% = 1,856.16.
        ("12463.00", "1856.16"),
        # (7,307.01 - 7,307) x 36% = 0.0036, rounded half-up to 0.00; 7,307.02 gives 0.0072 = 0.01.
        ("7307.01", "0.00"),
        ("7307.02", "0.01"),
        # At the threshold, and below it, the difference is not positive: 0.
        ("7307.00", "0.00"),
        ("5710.05", "0.00"),
    ],
)
def test_line_5_is_36_percent_of_line_3_over_7307_not_below_zero(
    take_home_service: TakeHomeService, line_3: str, line_5: str
) -> None:
    assert figure(take_home_service, PART, LINE_5, {LINE_3: line_3}) == D(line_5)


def test_line_5_is_one_tiered_surcharge_over_the_line_67_dataset() -> None:
    (step,) = steps(PART)

    assert step["name"] == "core/tiered_surcharge"
    assert step["params"] == {"tiers": "ca-on/surtax_line_67"}
    assert step["consumes"] == {"base": LINE_3}
    assert step["produces"] == {"output": LINE_5}
