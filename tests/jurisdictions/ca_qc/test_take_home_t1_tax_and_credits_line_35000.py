"""5005-R (2025) line 122 and line 35000, "Add lines 119 to 121", real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 122 and line 35000: Add lines 119 to 121. Total federal non-refundable tax credits =".
Line 119 is the credits at the 14.5% rate; line 120 (line 34900, donations and gifts) and line 121
(line 34990, top-up tax credit, an optional input and not the Federal Worksheet, owner ruling of
19 Nov 2026) are left blank by a salary-only filer and read as 0, so the line equals line 119:
2,733.51, 3,247.63 and 3,213.59 at 20,000, 70,000 and 200,000 (hand-computed from the printed
forms, not a CRA example). One core/sum, rounded half-up to the cent. The line is exported by the
real form.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    CREDITS_AT_CREDIT_RATE_LINE_119,
    DONATIONS_AND_GIFTS_LINE_120,
    NON_REFUNDABLE_TAX_CREDITS_LINE_122,
    TOP_UP_TAX_CREDIT_LINE_121,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2733.51"), ("70000", "3247.63"), ("200000", "3213.59")],
)
def test_a_salary_only_line_122_is_line_119(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(NON_REFUNDABLE_TAX_CREDITS_LINE_122).value == D(expected)
    assert (
        sheet.get(NON_REFUNDABLE_TAX_CREDITS_LINE_122).value
        == sheet.get(CREDITS_AT_CREDIT_RATE_LINE_119).value
    )


@pytest.mark.parametrize(
    ("kind", "expected"),
    [(DONATIONS_AND_GIFTS_LINE_120, "3347.73"), (TOP_UP_TAX_CREDIT_LINE_121, "3347.73")],
)
def test_each_optional_line_is_added(
    take_home_service: TakeHomeService, kind: AmountKind, expected: str
) -> None:
    _, sheet = sheets(take_home_service, "70000", (kind, "100.10"))

    assert sheet.get(NON_REFUNDABLE_TAX_CREDITS_LINE_122).value == D(expected)


def test_lines_120_and_121_are_added_in_one_sum(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(
        take_home_service,
        "70000",
        (DONATIONS_AND_GIFTS_LINE_120, "100.10"),
        (TOP_UP_TAX_CREDIT_LINE_121, "50.05"),
    )

    assert sheet.get(NON_REFUNDABLE_TAX_CREDITS_LINE_122).value == D("3397.78")


def test_the_trace_adds_the_lines_in_form_order(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 33800 (CA$3247.63) plus line 34900 (CA$0.00) plus line 34990 (CA$0.00) "
        "gives CA$3247.63 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_122_kind_is_non_negative() -> None:
    assert non_negative(NON_REFUNDABLE_TAX_CREDITS_LINE_122) is True
