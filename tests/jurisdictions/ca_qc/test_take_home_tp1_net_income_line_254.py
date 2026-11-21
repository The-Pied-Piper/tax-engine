"""Revenu Quebec TP-1 (2025) line 254, "Add lines 201 through 207, 214 through 231, and 234 through
252. Total deductions", as the Quebec take-home manifest part wires it: line 201, line 248 and the
other printed lines. Each of lines 205, 207, 214, 215, 225, 228, 231, 234, 236, 241, 245, 246,
250 and 252 is its own optional input, read as 0 when the caller leaves it out. The sum is
`core/sum`, rounded half-up to the cent by `ca-qc/cent_rounding`. The expected figures are
hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_205,
    TP1_LINE_250,
    TP1_LINE_252,
    TP1_TOTAL_DEDUCTIONS_LINE_254,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_TOTAL_DEDUCTIONS_LINE_254
EXPORTS = ("ca-qc/tp1_total_deductions_line_254",)
PARTS = (
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_inputs.yaml",
    "tp1_net_income_line_254.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1365.00"), ("70000", "2085.00"), ("200000", "2494.00")],
)
def test_line_254_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_the_other_deductions_are_added(take_home_service: TakeHomeService) -> None:
    given = (TP1_LINE_250, "1000.50")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "3085.50"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    given = (TP1_LINE_250, "0.005")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "2085.01"


def test_two_printed_lines_are_each_added(take_home_service: TakeHomeService) -> None:
    given = ((TP1_LINE_205, "1000.50"), (TP1_LINE_252, "250.25"))
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, *given).get(LINE).value

    assert str(value) == "3335.75"


def test_the_sentence_words_the_long_sum_as_line_201_plus_lines_205_to_252(
    take_home_service: TakeHomeService,
) -> None:
    given = ((TP1_LINE_205, "1000.50"), (TP1_LINE_250, "250.25"))
    sheet = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, *given)

    sentences = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert (
        "Line 201 (CA$1420.00) plus lines 205 to 252 (CA$1915.75 in total) gives CA$3335.75 "
        "(rounded to the nearest cent)."
    ) in sentences
