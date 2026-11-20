"""5005-R (2025) Step 5 Part A line 76, from the salary alone.

Form text (CRA 5005-R Step 5 Part A, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 76:" with the printed 0.00, 8,319.38, 20,081.25, 36,495.57 and 58,399.85. The figure is the
printed constant of the column line 71 falls in.

The parts are the real ones: the Step 3 and Step 4 chain from the salary to taxable income (line
26000) and the real Part A parts (line 76 and the lines it reads), with a test-local form
declaration. The expected figures are hand figures from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import FEDERAL_TAX_AT_COLUMN_START_LINE_76
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = "ca-qc/federal_tax_at_column_start_line_76"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "8319.38"), ("200000", "36495.57")],
)
def test_line_76_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, IDENTIFIER, 71, 76)

    assert sheet.get(FEDERAL_TAX_AT_COLUMN_START_LINE_76).value == D(expected)


def test_the_line_76_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_TAX_AT_COLUMN_START_LINE_76) is True
