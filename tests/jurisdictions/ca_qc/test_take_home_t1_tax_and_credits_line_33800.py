"""5005-R (2025) line 119 and line 33800, "Line 117 multiplied by the percentage from line 118".

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 118: Federal non-refundable tax credit rate 14.5%" and "Line 119 and line 33800: Line 117
multiplied by the percentage from line 118 =". Line 118 is a printed rate held in the shared
`ca/credit_rate` dataset, so it has no step; one core/apply_rate, rounded half-up to the cent. The
figures of the ticket at 20,000, 70,000 and 200,000 are 18,851.80, 22,397.47 and 22,162.72 times
14.5%: 2,733.51, 3,247.63 and 3,213.59 (hand-computed from the printed forms, not a CRA example).
With medical expenses of 3,000.00 at 70,000, line 117 is 23,317.42 and line 119 is 3,381.03.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    CREDITS_AT_CREDIT_RATE_LINE_119,
    MEDICAL_EXPENSES_LINE_111,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2733.51"), ("70000", "3247.63"), ("200000", "3213.59")],
)
def test_line_119_is_line_117_at_14_5_percent(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CREDITS_AT_CREDIT_RATE_LINE_119).value == D(expected)


def test_the_medical_expenses_are_in_the_credit(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (MEDICAL_EXPENSES_LINE_111, "3000"))

    assert sheet.get(CREDITS_AT_CREDIT_RATE_LINE_119).value == D("3381.03")


def test_the_trace_names_the_rate(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "14.5% of line 33500 (CA$22397.47) gives CA$3247.63 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_119_kind_is_non_negative() -> None:
    assert non_negative(CREDITS_AT_CREDIT_RATE_LINE_119) is True
