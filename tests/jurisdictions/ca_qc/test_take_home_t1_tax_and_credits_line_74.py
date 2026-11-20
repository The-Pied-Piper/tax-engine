"""5005-R (2025) Step 5 Part A line 74, from the salary alone.

Form text (CRA 5005-R Step 5 Part A, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 74: Rate" with the printed 14.5%, 20.5%, 26%, 29% and 33%. The figure is the printed rate of
the column line 71 falls in.

The parts are the real ones: the Step 3 and Step 4 chain from the salary to taxable income (line
26000) and the real Part A parts (line 74 and the lines it reads), with a test-local form
declaration. The expected figures are hand figures from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import FEDERAL_BRACKET_COLUMN_RATE_LINE_74
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = "ca-qc/federal_bracket_column_rate_line_74"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.145"), ("70000", "0.205"), ("200000", "0.29")],
)
def test_line_74_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, IDENTIFIER, 71, 74)

    assert sheet.get(FEDERAL_BRACKET_COLUMN_RATE_LINE_74).value == D(expected)


def test_the_line_74_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_BRACKET_COLUMN_RATE_LINE_74) is True
