"""Worksheet ON428 (ON428 line 72) lines 2 and 3, from the real part.

Form text (Worksheet ON428, CRA 5006-d-25e.txt): "Line 2: Amount from line 65 of your Form ON428"
and "Line 3: Line 1 plus line 2 =". Line 2 is a copy of line 65, read from its own part, so line 3
is line 1 plus line 65.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.on428_worksheet_support import figure, steps

D = Decimal
PART = "on428_worksheet_line_3.yaml"
LINE_1 = "ca-on/on428_worksheet_basic_additional_tax_line_1"
LINE_65 = "ca-on/on428_surtax_base_line_65"
LINE_3 = "ca-on/on428_worksheet_surtax_base_line_3"


@pytest.mark.parametrize(
    ("line_1", "line_65", "line_3"),
    [
        # Line 1 is 2,463.00 and line 65 is 12,000.50, so line 3 is 14,463.50.
        ("2463.00", "12000.50", "14463.50"),
        # Line 1 is 0 (no T691 line), so line 3 is line 65.
        ("0.00", "300.14", "300.14"),
        ("0.00", "0.00", "0.00"),
    ],
)
def test_line_3_is_line_1_plus_line_65(
    take_home_service: TakeHomeService, line_1: str, line_65: str, line_3: str
) -> None:
    given = {LINE_1: line_1, LINE_65: line_65}

    assert figure(take_home_service, PART, LINE_3, given) == D(line_3)


def test_line_3_is_one_sum_of_line_1_and_line_65_rounded_to_the_cent() -> None:
    (step,) = steps(PART)

    assert step["name"] == "core/sum"
    assert step["params"] == {"rounding": "ca-on/cent_rounding"}
    assert step["consumes"] == {"parts": [LINE_1, LINE_65]}
    assert step["produces"] == {"output": LINE_3}
