"""5005-R (2025) Step 5 Part A line 77, from the salary alone.

Form text (CRA 5005-R Step 5 Part A, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 77: Line 75 plus line 76 Federal tax on taxable income =". The figure is line 75 plus line 76.

The parts are the real ones: the Step 3 and Step 4 chain from the salary to taxable income (line
26000) and the real Part A parts (line 77 and the lines it reads), with a test-local form
declaration. The expected figures are hand figures from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
IDENTIFIER = "ca-qc/federal_tax_on_taxable_income_line_77"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2876.08"), ("70000", "10771.18"), ("200000", "42598.33")],
)
def test_line_77_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, IDENTIFIER, 71, 72, 73, 74, 75, 76, 77)

    assert sheet.get(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77).value == D(expected)


def test_the_line_77_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77) is True
