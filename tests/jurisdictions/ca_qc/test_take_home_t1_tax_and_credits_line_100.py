"""5005-R (2025) line 100, "Add lines 87 to 99", from the salary alone, real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 100: Add lines 87 to 99. =". Lines 87, 89, 91 and 96 are steps; lines 88, 90, 92 to 95 and 97
to 99 are optional inputs, each left blank by a salary-only filer and read as 0. One core/sum,
rounded half-up to the cent. The hand figures at 20,000, 70,000 and 200,000 add the printed lines:
891.00 + 262.00 + 98.80 + 1,471.00, 3,591.00 + 860.67 + 345.80 + 1,471.00 and 3,661.20 + 860.67 +
484.12 + 1,471.00 (not a CRA example), which with line 85 give the line 117 figures of the ticket.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    ADOPTION_EXPENSES_LINE_99,
    CREDIT_AMOUNTS_LINE_85,
    CREDITS_LINE_100,
    EI_PREMIUMS_SELF_EMPLOYMENT_LINE_90,
    HOME_ACCESSIBILITY_EXPENSES_LINE_98,
    HOME_BUYERS_AMOUNT_LINE_97,
    PPIP_PREMIUMS_PAYABLE_LINE_92,
    PPIP_PREMIUMS_PAYABLE_SELF_EMPLOYMENT_LINE_93,
    QPP_BASE_SELF_EMPLOYMENT_LINE_88,
    SEARCH_AND_RESCUE_AMOUNT_LINE_95,
    VOLUNTEER_FIREFIGHTERS_AMOUNT_LINE_94,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal
OPTIONAL_LINES = (
    QPP_BASE_SELF_EMPLOYMENT_LINE_88,
    EI_PREMIUMS_SELF_EMPLOYMENT_LINE_90,
    PPIP_PREMIUMS_PAYABLE_LINE_92,
    PPIP_PREMIUMS_PAYABLE_SELF_EMPLOYMENT_LINE_93,
    VOLUNTEER_FIREFIGHTERS_AMOUNT_LINE_94,
    SEARCH_AND_RESCUE_AMOUNT_LINE_95,
    HOME_BUYERS_AMOUNT_LINE_97,
    HOME_ACCESSIBILITY_EXPENSES_LINE_98,
    ADOPTION_EXPENSES_LINE_99,
)


@pytest.mark.parametrize(
    ("salary", "line_100", "line_117"),
    [
        ("20000", "2722.80", "18851.80"),
        ("70000", "6268.47", "22397.47"),
        # Lines 87, 89 and 91 are all at their printed maximums.
        ("200000", "6476.99", "22162.72"),
    ],
)
def test_a_salary_only_line_100_adds_lines_87_89_91_and_96(
    take_home_service: TakeHomeService, salary: str, line_100: str, line_117: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CREDITS_LINE_100).value == D(line_100)
    assert sheet.get(CREDIT_AMOUNTS_LINE_85).value + sheet.get(CREDITS_LINE_100).value == D(
        line_117
    )


@pytest.mark.parametrize("kind", OPTIONAL_LINES)
def test_each_optional_line_is_added(take_home_service: TakeHomeService, kind: AmountKind) -> None:
    _, sheet = sheets(take_home_service, "70000", (kind, "100.10"))

    assert sheet.get(CREDITS_LINE_100).value == D("6368.57")


def test_every_optional_line_is_added_in_one_sum(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", *((kind, "100.10") for kind in OPTIONAL_LINES))

    assert sheet.get(CREDITS_LINE_100).value == D("7169.37")


def test_the_trace_adds_the_lines_in_form_order(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 30800 (CA$3591.00) plus line 31000 (CA$0.00) plus line 31200 (CA$860.67) plus line "
        "31217 (CA$0.00) plus line 31205 (CA$345.80) plus line 31210 (CA$0.00) plus line 31215 "
        "(CA$0.00) plus line 31220 (CA$0.00) plus line 31240 (CA$0.00) plus line 31260 "
        "(CA$1471.00) plus line 31270 (CA$0.00) plus line 31285 (CA$0.00) plus line 31300 "
        "(CA$0.00) gives CA$6268.47 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_100_kind_is_non_negative() -> None:
    assert non_negative(CREDITS_LINE_100) is True
