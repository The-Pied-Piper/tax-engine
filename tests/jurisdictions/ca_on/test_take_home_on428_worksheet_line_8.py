"""Worksheet ON428 (ON428 line 72) lines 7 and 8, from the real part.

Form text (Worksheet ON428, CRA 5006-d-25e.txt): "Line 7: Amount from line 68 of your Form ON428"
and "Line 8: Line 6 minus line 7 =". Line 7 is a copy of line 68, read from its own part, so line 8
is line 6 less line 68. The worksheet prints no floor, so a negative difference stands.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.on428_worksheet_support import figure, steps

D = Decimal
PART = "on428_worksheet_line_8.yaml"
LINE_6 = "ca-on/on428_worksheet_surtax_total_line_6"
LINE_68 = "ca-on/on428_surtax_total_line_68"
LINE_8 = "ca-on/on428_worksheet_surtax_on_additional_tax_line_8"


@pytest.mark.parametrize(
    ("line_6", "line_68", "line_8"),
    [
        # Line 6 is 3,206.76 and line 68 is 2,100.00, so line 8 is 1,106.76.
        ("3206.76", "2100.00", "1106.76"),
        # No surtax either side: 0.
        ("0.00", "0.00", "0.00"),
        # No floor is printed: a negative difference is kept.
        ("100.00", "150.25", "-50.25"),
    ],
)
def test_line_8_is_line_6_minus_line_68(
    take_home_service: TakeHomeService, line_6: str, line_68: str, line_8: str
) -> None:
    given = {LINE_6: line_6, LINE_68: line_68}

    assert figure(take_home_service, PART, LINE_8, given) == D(line_8)


def test_line_8_is_one_subtraction_of_line_68_from_line_6_rounded_to_the_cent() -> None:
    (step,) = steps(PART)

    assert step["name"] == "core/subtract"
    assert step["params"] == {"rounding": "ca-on/cent_rounding"}
    assert step["consumes"] == {"amount": LINE_6, "less": LINE_68}
    assert step["produces"] == {"output": LINE_8}
