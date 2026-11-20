"""5005-R (2025) line 146 and line 42000, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 146 and line 42000: Add lines 143 to 145. Net federal tax ="
Lines 144 and 145 are optional inputs, a blank for a salary-only filer and read as 0. Line 147 is
"Amount from line 42000", a pure copy, so it is not a step. The figures at 20,000, 70,000 and
200,000 are hand-computed from the printed forms, not a CRA example. One core/sum, rounded half-up
to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    ADVANCED_CANADA_WORKERS_BENEFIT_LINE_144,
    NET_FEDERAL_TAX_LINE_146,
    SPECIAL_TAXES_LINE_145,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "142.57"), ("70000", "7523.55"), ("200000", "39384.74")],
)
def test_a_salary_only_line_146_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(NET_FEDERAL_TAX_LINE_146).value == D(expected)


@pytest.mark.parametrize("kind", [ADVANCED_CANADA_WORKERS_BENEFIT_LINE_144, SPECIAL_TAXES_LINE_145])
def test_each_optional_line_is_taken(take_home_service: TakeHomeService, kind: AmountKind) -> None:
    _, sheet = sheets(take_home_service, "70000", (kind, "100.10"))

    assert sheet.get(NET_FEDERAL_TAX_LINE_146).value == D("7623.65")


def test_lines_144_and_145_are_added_in_one_sum(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(
        take_home_service,
        "70000",
        (ADVANCED_CANADA_WORKERS_BENEFIT_LINE_144, "100.10"),
        (SPECIAL_TAXES_LINE_145, "100.10"),
    )

    assert sheet.get(NET_FEDERAL_TAX_LINE_146).value == D("7723.75")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 41700 (CA$7523.55) plus line 41500 (CA$0.00) plus line 41800 (CA$0.00)"
        " gives CA$7523.55 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_146_kind_is_non_negative() -> None:
    assert non_negative(NET_FEDERAL_TAX_LINE_146) is True
