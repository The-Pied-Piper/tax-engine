"""5005-R (2025) Step 5 Part A line 72, from the salary alone.

Form text (CRA 5005-R Step 5 Part A, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 72:" with the printed 0.00, 57,375.00, 114,750.00, 177,882.00 and 253,414.00. The figure is
the printed lower bound of the column line 71 falls in (columns 1, 2 and 4).

The parts are the real ones: the Step 3 and Step 4 chain from the salary to taxable income (line
26000) and the real Part A parts (line 72 and the lines it reads), with a test-local form
declaration. The expected figures are hand figures from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import FEDERAL_BRACKET_LOWER_BOUND_LINE_72
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = "ca-qc/federal_bracket_lower_bound_line_72"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "57375.00"), ("200000", "177882.00")],
)
def test_line_72_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, IDENTIFIER, 71, 72)

    assert sheet.get(FEDERAL_BRACKET_LOWER_BOUND_LINE_72).value == D(expected)


def test_the_line_72_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_BRACKET_LOWER_BOUND_LINE_72) is True
