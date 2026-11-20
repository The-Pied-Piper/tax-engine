"""5005-R (2025) line 113, "Enter whichever is less: $2,834 or the amount from line 112".


Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 113: Enter whichever is less: $2,834 or the amount from line 112." One core/capped_amount at
the printed $2,834 (the shared dataset `ca/medical_threshold_ceiling`). Line 112 is 595.05 at 20,000
and 2,080.05 at 70,000, both under the cap, and 5,967.78 at 200,000, which the cap takes down to
2,834.00 (hand-computed from the printed forms, not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import MEDICAL_THRESHOLD_LINE_113
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "595.05"), ("70000", "2080.05"), ("200000", "2834.00")],
)
def test_line_113_is_the_lesser_of_line_112_and_2834(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(MEDICAL_THRESHOLD_LINE_113).value == D(expected)


def test_the_trace_names_the_lesser(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "200000")

    assert (
        "Lesser of line 112 (CA$5967.78) and the medical threshold ceiling (CA$2834.00) "
        "gives CA$2834.00 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_113_kind_is_non_negative() -> None:
    assert non_negative(MEDICAL_THRESHOLD_LINE_113) is True
