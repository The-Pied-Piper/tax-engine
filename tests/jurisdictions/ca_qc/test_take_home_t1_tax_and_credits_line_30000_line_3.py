"""Federal Worksheet 5000-D1 (2025), line 30000 line 3 "Amount from line 23600 of your return", as
the Quebec manifest part wires it for 5005-R line 78.

Form text (CRA 5000-D1, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt):
"Line 3: Amount from line 23600 of your return". The step is one core/record_total over the
net income export of the Quebec T1 taxable-income form (`ca-qc/t1_taxable_income.net_income`).

The parts are the real ones: the Step 3 chain from the salary to line 23600, the real form
declarations and the real Schedule 8 import. The header is made up.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import BASIC_PERSONAL_AMOUNT_NET_INCOME_LINE_3
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "line_3"),
    [("20000", "19835.00"), ("70000", "69335.00"), ("200000", "198926.00")],
)
def test_line_3_is_the_line_23600_amount(
    take_home_service: TakeHomeService, salary: str, line_3: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(BASIC_PERSONAL_AMOUNT_NET_INCOME_LINE_3).value == D(line_3)


def test_the_line_3_kind_is_non_negative() -> None:
    assert non_negative(BASIC_PERSONAL_AMOUNT_NET_INCOME_LINE_3) is True
