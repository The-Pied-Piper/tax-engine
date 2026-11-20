"""5005-R (2025) line 110, "Add lines 105 to 109", from the salary alone, real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 110: Add lines 105 to 109. =". Line 105 is the credits step before it; lines 106 (line
31900), 107 (line 32300), 108 (line 32400) and 109 (line 32600) are optional inputs, each left
blank by a salary-only filer and read as 0. One core/sum, rounded half-up to the cent. With every
optional line blank the line is the line 117 figure of the ticket at 20,000, 70,000 and 200,000:
18,851.80, 22,397.47 and 22,162.72 (hand-computed from the printed forms, not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    AMOUNTS_TRANSFERRED_FROM_SPOUSE_LINE_109,
    CREDITS_LINE_110,
    FEDERAL_TUITION_AMOUNT_LINE_107,
    STUDENT_LOAN_INTEREST_LINE_106,
    TUITION_AMOUNT_TRANSFERRED_LINE_108,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal
OPTIONAL_LINES = (
    STUDENT_LOAN_INTEREST_LINE_106,
    FEDERAL_TUITION_AMOUNT_LINE_107,
    TUITION_AMOUNT_TRANSFERRED_LINE_108,
    AMOUNTS_TRANSFERRED_FROM_SPOUSE_LINE_109,
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18851.80"), ("70000", "22397.47"), ("200000", "22162.72")],
)
def test_a_salary_only_line_110_is_line_105(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CREDITS_LINE_110).value == D(expected)


@pytest.mark.parametrize("kind", OPTIONAL_LINES)
def test_each_optional_line_is_added(take_home_service: TakeHomeService, kind: AmountKind) -> None:
    _, sheet = sheets(take_home_service, "70000", (kind, "100.10"))

    assert sheet.get(CREDITS_LINE_110).value == D("22497.57")


def test_every_optional_line_is_added_in_one_sum(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", *((kind, "100.10") for kind in OPTIONAL_LINES))

    assert sheet.get(CREDITS_LINE_110).value == D("22797.87")


def test_the_trace_adds_the_lines_in_form_order(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 105 (CA$22397.47) plus line 31900 (CA$0.00) plus line 32300 (CA$0.00) "
        "plus line 32400 (CA$0.00) plus line 32600 (CA$0.00) gives CA$22397.47 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_110_kind_is_non_negative() -> None:
    assert non_negative(CREDITS_LINE_110) is True
