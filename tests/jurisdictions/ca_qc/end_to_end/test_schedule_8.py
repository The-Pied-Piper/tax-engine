"""Schedule 8 (Quebec edition 5005-S8, 2025, QPP contributions) from the salary alone: the shared
federal form composed with the Quebec dataset swap, one test per printed line.

The Quebec manifest imports `ca/schedule_8` with `datasets` that read the Quebec figure of line 11
in place of the federal one. This module composes a test-only Quebec header (the real header's
other forms are not built yet) that imports Schedule 8 with the same swap and types in only the
gross salary (`ca/employment_income`). The service is built over the Quebec package list of
`tests/jurisdictions/ca_qc/support.py`, as Quebec is not in `registrations.JURISDICTIONS`. This is
not a worked return: no return file, no slips, one form. The shared form keeps the federal titles
("Required base contributions on CPP pensionable earnings"); the Quebec edition prints "QPP", and
the owner accepted the shared wording for 2025. A filer who lived alone, or is a
tenant, gets the same figures: these lines do not read those answers. Lines 25 and 28 are the Part
2a route, as the federal precedent builds it (the owner's ruling of 19 Nov 2026). With lines 8
and 21 blank, the printed text would send a negative line 24 to Part 2b or Part 4, which limit
the credit to contributions actually paid; this module does not build that route.

Form text: CRA 5005-S8 (2025), Schedule 8 Part 2 (page 3), form 5005-S8 raw text under
canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s8/:
"Line 1 and line 50329: Total QPP pensionable earnings from box 26 of all of your T4 slips (if
box 26 is blank, enter the amount from box 14) (maximum $81,200 per slip)"; "Line 2: Enter
whichever is less: amount from line D of Part 1 or line 1."; "Line 4: Line 2 minus line 3 (if
negative, enter "0")"; "Line 5: Line 2 minus line 4 (if negative, enter "0")"; "Line 7: Line 5
minus line 6 (if negative, enter "0") (maximum $67,800)"; "Line 11: amount from line 7 multiplied
by 5.4% (maximum $3,661.20)"; "Line 12: amount from line 7 multiplied by 1% (maximum $678.00)";
"Line 22: Amount from line 4 multiplied by 4% (maximum $396.00)"; "Line 25: Enter the amount from
line 15. Enter this amount (in dollars and cents) on line 30800 of your return."; "Line 28: Line 26
plus line 27. Enter this amount (in dollars and cents) on line 22215 of your return."

The expected figures are hand-computed from the printed lines for a full year (12 months: line B
71,300.00, line D 81,200.00, line E 3,500.00; line 3 is line B), not from a CRA example.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.deductions import (
    CPP_PART_3_LINE_2,
    CPP_PART_3_LINE_4,
    CPP_PART_3_LINE_5,
    CPP_PART_3_LINE_7,
    CPP_PART_3_LINE_11,
)
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.rc381_cpp_qpp import (
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)
from tests.jurisdictions.ca_qc.support import quebec_service

D = Decimal
HEADER_TEMPLATE = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    inputs:
      - name: ca/employment_income
        title: "Employment income"
        reference: "10100"
        unit: ca/cad
        required: true
    imports:
      - {schedule_8}
    """)
SWAPPED = (
    "form: ca/schedule_8\n"
    "    datasets:\n"
    "      ca/cpp_line_11_base_contribution: ca-qc/qpp_line_11_base_contribution"
)
HEADER = HEADER_TEMPLATE.replace("{schedule_8}", SWAPPED)
BARE_HEADER = HEADER_TEMPLATE.replace("{schedule_8}", "ca/schedule_8")


def schedule_8(tmp_path: Path, salary: str, header: str = HEADER) -> Worksheet:
    worksheets = quebec_service(tmp_path, header).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "81200.00")]
)
def test_line_1_matches_the_printed_form(tmp_path: Path, salary: str, expected: str) -> None:
    # Line 1: the salary, at most 81,200.00 per slip.
    sheet = schedule_8(tmp_path, salary)

    assert sheet.get(T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "81200.00")]
)
def test_line_2_matches_the_printed_form(tmp_path: Path, salary: str, expected: str) -> None:
    # Line 2: the lesser of line D (81,200.00) and line 1.
    sheet = schedule_8(tmp_path, salary)

    assert sheet.get(CPP_PART_3_LINE_2).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "0.00"), ("70000", "0.00"), ("200000", "9900.00")]
)
def test_line_4_matches_the_printed_form(tmp_path: Path, salary: str, expected: str) -> None:
    # Line 4: line 2 less line 3 (71,300.00), not below 0.
    sheet = schedule_8(tmp_path, salary)

    assert sheet.get(CPP_PART_3_LINE_4).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "71300.00")]
)
def test_line_5_matches_the_printed_form(tmp_path: Path, salary: str, expected: str) -> None:
    # Line 5: line 2 less line 4, not below 0.
    sheet = schedule_8(tmp_path, salary)

    assert sheet.get(CPP_PART_3_LINE_5).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "16500.00"), ("70000", "66500.00"), ("200000", "67800.00")]
)
def test_line_7_matches_the_printed_form(tmp_path: Path, salary: str, expected: str) -> None:
    # Line 7: line 5 less line 6 (3,500.00), not below 0, at most 67,800.00.
    sheet = schedule_8(tmp_path, salary)

    assert sheet.get(CPP_PART_3_LINE_7).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "891.00"), ("70000", "3591.00"), ("200000", "3661.20")]
)
def test_line_11_matches_the_printed_form(tmp_path: Path, salary: str, expected: str) -> None:
    # Line 11: 5.4% of line 7, at most 3,661.20 (the federal 4.95% would give 3,291.75 at 70,000).
    sheet = schedule_8(tmp_path, salary)

    assert sheet.get(CPP_PART_3_LINE_11).value == D(expected)


def test_line_11_without_the_swap_is_the_federal_figure(tmp_path: Path) -> None:
    # The shared form's own files still read the federal dataset: a manifest that imports
    # `ca/schedule_8` bare gets 4.95% of 66,500.00 = 3,291.75, so the swap is local to Quebec.
    sheet = schedule_8(tmp_path, "70000", BARE_HEADER)

    assert sheet.get(CPP_PART_3_LINE_11).value == D("3291.75")
