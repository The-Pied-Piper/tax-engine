"""5005-R (2025) line 134, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 134: Line 132 minus line 133 ="
The form prints no floor, so the difference is not floored and may be negative. Line 133 is an
optional input, a blank for a salary-only filer and read as 0.
The figures at 20,000, 70,000 and 200,000 are hand-computed from the printed forms, not a CRA
example. One core/subtract, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    FEDERAL_FOREIGN_TAX_CREDIT_LINE_133,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT_LINE_134,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.net_federal_tax_support import sheets
from tests.kinds import non_negative

D = Decimal
LAST = "t1_tax_and_credits_line_134.yaml"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "142.57"), ("70000", "7523.55"), ("200000", "39384.74")],
)
def test_a_salary_only_line_134_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = sheets(take_home_service, salary, LAST)

    assert sheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT_LINE_134).value == D(expected)


@pytest.mark.parametrize(("kind", "expected"), [(FEDERAL_FOREIGN_TAX_CREDIT_LINE_133, "7423.45")])
def test_each_optional_line_is_taken(
    take_home_service: TakeHomeService, kind: AmountKind, expected: str
) -> None:
    sheet = sheets(take_home_service, "70000", LAST, (kind, "100.10"))

    assert sheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT_LINE_134).value == D(expected)


def test_a_negative_figure_is_kept(take_home_service: TakeHomeService) -> None:
    sheet = sheets(take_home_service, "70000", LAST, (FEDERAL_FOREIGN_TAX_CREDIT_LINE_133, "10000"))

    assert sheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT_LINE_134).value == D("-2476.45")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    sheet = sheets(take_home_service, "70000", LAST)

    assert (
        "Line 132 (CA$7523.55) less line 40500 (CA$0.00)"
        " gives CA$7523.55 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_134_kind_is_not_non_negative() -> None:
    assert non_negative(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT_LINE_134) is False
