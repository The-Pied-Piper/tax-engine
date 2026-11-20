"""5005-R (2025) line 129, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 129: Add lines 126 to 128. ="
Line 126 is "Amount from line 35000", a pure copy of line 122, so line 122 is read directly and is
not a step. Lines 127 and 128 are optional inputs, a blank for a salary-only filer and read as 0.
The figures at 20,000, 70,000 and 200,000 are hand-computed from the printed forms, not a CRA
example. One core/sum, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    FEDERAL_CREDITS_AND_CARRYOVERS_LINE_129,
    FEDERAL_DIVIDEND_TAX_CREDIT_LINE_127,
    MINIMUM_TAX_CARRYOVER_LINE_128,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.net_federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
LAST = "t1_tax_and_credits_line_129.yaml"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2733.51"), ("70000", "3247.63"), ("200000", "3213.59")],
)
def test_a_salary_only_line_129_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = sheets(take_home_service, salary, LAST)

    assert sheet.get(FEDERAL_CREDITS_AND_CARRYOVERS_LINE_129).value == D(expected)


@pytest.mark.parametrize(("kind", "expected"), [(FEDERAL_DIVIDEND_TAX_CREDIT_LINE_127, "3347.73"), (MINIMUM_TAX_CARRYOVER_LINE_128, "3347.73")])
def test_each_optional_line_is_taken(
    take_home_service: TakeHomeService, kind: AmountKind, expected: str
) -> None:
    sheet = sheets(take_home_service, "70000", LAST, (kind, "100.10"))

    assert sheet.get(FEDERAL_CREDITS_AND_CARRYOVERS_LINE_129).value == D(expected)


def test_lines_127_and_128_are_added_in_one_sum(take_home_service: TakeHomeService) -> None:
    sheet = sheets(
        take_home_service,
        "70000",
        LAST,
        (FEDERAL_DIVIDEND_TAX_CREDIT_LINE_127, "100.10"),
        (MINIMUM_TAX_CARRYOVER_LINE_128, "100.10"),
    )

    assert sheet.get(FEDERAL_CREDITS_AND_CARRYOVERS_LINE_129).value == D("3447.83")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    sheet = sheets(take_home_service, "70000", LAST)

    assert (
        'Line 35000 (CA$3247.63) plus line 40425 (CA$0.00) plus line 40427 (CA$0.00)'
        ' gives CA$3247.63 (rounded to the nearest cent).'
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_129_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_CREDITS_AND_CARRYOVERS_LINE_129) is True
