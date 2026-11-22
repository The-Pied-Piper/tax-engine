"""ON428 (2025) line 72 and Worksheet ON428 line 9, from the real part.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 72: If you entered an amount on line 11 of Part
5 of Form T691, use Worksheet ON428 to calculate your additional tax for minimum tax purposes."
Worksheet ON428 (CRA 5006-d-25e.txt): "Line 9: Line 1 plus line 8 Enter this amount on line 72 of
your Form ON428." The worksheet's "If the amount on line 3 is more than $5,710, complete lines 4 to
9. If not, enter the amount from line 1 on line 72" needs no step: line 8 is 0 then.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.on428_worksheet_support import figure, steps

D = Decimal
PART = "on428_line_72.yaml"
LINE_1 = "ca-on/on428_worksheet_basic_additional_tax_line_1"
LINE_8 = "ca-on/on428_worksheet_surtax_on_additional_tax_line_8"
LINE_72 = "ca-on/on428_additional_tax_for_minimum_tax_line_72"


@pytest.mark.parametrize(
    ("line_1", "line_8", "line_72"),
    [
        # Line 1 is 2,463.00 and line 8 is 1,106.76, so line 72 is 3,569.76.
        ("2463.00", "1106.76", "3569.76"),
        # Line 3 not over $5,710: line 8 is 0 and line 72 is line 1.
        ("2463.00", "0.00", "2463.00"),
        # No T691 Part 5 line 11: lines 1 and 8 are 0, so line 72 is 0.
        ("0.00", "0.00", "0.00"),
    ],
)
def test_line_72_is_worksheet_line_1_plus_line_8(
    take_home_service: TakeHomeService, line_1: str, line_8: str, line_72: str
) -> None:
    given = {LINE_1: line_1, LINE_8: line_8}

    assert figure(take_home_service, PART, LINE_72, given) == D(line_72)


def test_line_72_is_one_sum_of_worksheet_line_1_and_line_8_rounded_to_the_cent() -> None:
    (step,) = steps(PART)

    assert step["name"] == "core/sum"
    assert step["reference"] == "72"
    assert step["params"] == {"rounding": "ca-on/cent_rounding"}
    assert step["consumes"] == {"parts": [LINE_1, LINE_8]}
    assert step["produces"] == {"output": LINE_72}
