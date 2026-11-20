"""5005-R (2025) line 149 and line 42200, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 149 and line 42200: Social benefits repayment (amount from line 23500)"
The line copies line 56 (line 23500), an input of the T1 taxable-income form that the form fixes
at 0 for a salary-only filer; it is read from that form's export by one core/record_total. The
figures at 20,000, 70,000 and 200,000 are hand figures (no EI benefits or OAS), not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca.catalog.deductions import SOCIAL_BENEFITS_REPAYMENT
from tax_engine.jurisdictions.ca_qc.catalog import SOCIAL_BENEFITS_REPAYMENT_LINE_149
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_149_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(SOCIAL_BENEFITS_REPAYMENT_LINE_149).value == D("0")


def test_line_149_copies_line_23500(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (SOCIAL_BENEFITS_REPAYMENT, "100"))

    assert sheet.get(SOCIAL_BENEFITS_REPAYMENT_LINE_149).value == D("100")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 23500 of T1 Income Tax and Benefit Return (CA$0.00) gives CA$0.00."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_149_kind_is_non_negative() -> None:
    assert non_negative(SOCIAL_BENEFITS_REPAYMENT_LINE_149) is True
