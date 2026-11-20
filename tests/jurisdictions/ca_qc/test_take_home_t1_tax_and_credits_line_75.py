"""5005-R (2025) Step 5 Part A line 75, from the salary alone.

Form text (CRA 5005-R Step 5 Part A, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 75: Line 73 multiplied by the percentage from line 74 =". The figure is line 73 times line 74,
rounded half-up to the cent (14.5% of 19,835.00 is 2,876.075).

The parts are the real ones: the Step 3 and Step 4 chain from the salary to taxable income (line
26000) and the real Part A parts (line 75 and the lines it reads), with a test-local form
declaration. The expected figures are hand figures from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_75
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = "ca-qc/federal_excess_times_column_rate_line_75"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2876.08"), ("70000", "2451.80"), ("200000", "6102.76")],
)
def test_line_75_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, IDENTIFIER, 71, 72, 73, 74, 75)

    assert sheet.get(FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_75).value == D(expected)


def test_the_line_75_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_75) is True
