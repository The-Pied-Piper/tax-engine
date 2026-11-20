"""5005-R (2025) line 112, "Amount from line 23600 multiplied by 3%", real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 112: Amount from line 23600 multiplied by 3% =". Two steps: a core/record_total copy of net
income (line 23600), then a core/apply_rate at the printed 3% (the shared dataset
`ca/medical_net_income_rate`), rounded half-up to the cent. Net income is the taxable income of the
ticket (19,835.00, 69,335.00 and 198,926.00) because no deduction from net income is given, so the
hand figures are 595.05, 2,080.05 and 5,967.78 (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    MEDICAL_NET_INCOME_SHARE_LINE_112,
    NET_INCOME_LINE_112,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "net_income", "share"),
    [
        ("20000", "19835.00", "595.05"),
        ("70000", "69335.00", "2080.05"),
        ("200000", "198926.00", "5967.78"),
    ],
)
def test_line_112_is_three_percent_of_net_income(
    take_home_service: TakeHomeService, salary: str, net_income: str, share: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(NET_INCOME_LINE_112).value == D(net_income)
    assert sheet.get(MEDICAL_NET_INCOME_SHARE_LINE_112).value == D(share)


def test_the_trace_names_the_copy_and_the_rate(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")
    trace = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert (
        "Line 23600 of T1 Income Tax and Benefit Return (CA$69335.00) gives CA$69335.00." in trace
    )
    assert (
        '3% of "Amount from line 23600" (CA$69335.00) gives CA$2080.05 '
        "(rounded to the nearest cent)."
    ) in trace


def test_the_line_112_kinds_are_non_negative() -> None:
    assert non_negative(NET_INCOME_LINE_112) is True
    assert non_negative(MEDICAL_NET_INCOME_SHARE_LINE_112) is True
