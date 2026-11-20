"""5005-R (2025) Step 5 Part A line 73, from the salary alone.

Form text (CRA 5005-R Step 5 Part A, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 73: Line 71 minus line 72 (cannot be negative) =". The figure is line 71 less line 72.

The parts are the real ones: the Step 3 and Step 4 chain from the salary to taxable income (line
26000) and the real Part A parts (line 73 and the lines it reads), with a test-local form
declaration. The expected figures are hand figures from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_73
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = "ca-qc/federal_taxable_income_over_lower_bound_line_73"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "19835.00"), ("70000", "11960.00"), ("200000", "21044.00")],
)
def test_line_73_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, IDENTIFIER, 71, 72, 73)

    assert sheet.get(FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_73).value == D(expected)


def test_the_line_73_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_73) is True
