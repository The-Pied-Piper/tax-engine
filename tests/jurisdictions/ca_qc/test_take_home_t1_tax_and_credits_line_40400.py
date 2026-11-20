"""5005-R (2025) line 125 and line 40400, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 125 and line 40400: Line 123 plus line 124 ="
Line 123 is "Enter the amount from line 77.", a pure copy of line 77, so line 77 is read directly
and is not a step. Line 124 is an optional input, a blank for a salary-only filer and read as 0.
The figures at 20,000, 70,000 and 200,000 are hand-computed from the printed forms, not a CRA
example. One core/sum, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    FEDERAL_TAX_ON_SPLIT_INCOME_LINE_124,
    FEDERAL_TAX_WITH_SPLIT_INCOME_LINE_125,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.net_federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
LAST = "t1_tax_and_credits_line_40400.yaml"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2876.08"), ("70000", "10771.18"), ("200000", "42598.33")],
)
def test_a_salary_only_line_125_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = sheets(take_home_service, salary, LAST)

    assert sheet.get(FEDERAL_TAX_WITH_SPLIT_INCOME_LINE_125).value == D(expected)


@pytest.mark.parametrize(("kind", "expected"), [(FEDERAL_TAX_ON_SPLIT_INCOME_LINE_124, "10871.28")])
def test_each_optional_line_is_taken(
    take_home_service: TakeHomeService, kind: AmountKind, expected: str
) -> None:
    sheet = sheets(take_home_service, "70000", LAST, (kind, "100.10"))

    assert sheet.get(FEDERAL_TAX_WITH_SPLIT_INCOME_LINE_125).value == D(expected)


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    sheet = sheets(take_home_service, "70000", LAST)

    assert (
        "Line 77 (CA$10771.18) plus line 40424 (CA$0.00)"
        " gives CA$10771.18 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_125_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_TAX_WITH_SPLIT_INCOME_LINE_125) is True
