"""Schedule 6 (Quebec edition 5005-S6, 2025, Canada workers benefit) from the salary alone: the
shared federal form composed with the Quebec dataset swaps, one test per printed line.

The Quebec manifest imports `ca/schedule_6` with `datasets` that read the Quebec figures of lines
17, 19, 21, 24 and 26 in place of the federal ones. This module composes a test-only Quebec header
(the real header's other forms are not built yet) that imports Schedule 6 and Schedule 8 with the
same swaps, and the real Quebec T1 parts (5005-R Steps 2 and 3) that supply line 7's net income,
and types in only the gross salary (`ca/employment_income`). The service is built over the Quebec
package list of `tests/jurisdictions/ca_qc/support.py`, as Quebec is not in
`registrations.JURISDICTIONS`. This is not a worked return: no return file, no slips, one form. A
filer who lived alone, or is a tenant, gets the same figures: these lines do not read those answers.

Form text: CRA 5005-S6 (2025), Schedule 6, Canada Workers Benefit (pages 4 and 5), raw text under
canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s6/:
"Line 17: If you had an eligible spouse or you had both an eligible spouse and an eligible
dependant, enter $3,600. If not, enter $2,400."; "Line 18: Line 16 minus line 17 (if negative,
enter "0")"; "Line 19: ... If not, enter 37.3%."; "Line 20: Line 18 multiplied by the percentage
from line 19"; "Line 21: If you did not have an eligible spouse or an eligible dependant, enter
$3,812.06. ..."; "Line 22: Enter whichever is less: amount from line 20 or line 21."; "Line 24: If
you did not have an eligible spouse or an eligible dependant, enter $14,170.05. ..."; "Line 25:
Line 23 minus line 24 (if negative, enter "0")"; "Line 26: Rate 20%"; "Line 27: Line 25
multiplied by the percentage from line 26"; "Line 28: Line 22 minus line 27 (if negative, enter
"0") If you are not completing Step 3, enter this amount on line 45300 of your return."

The expected figures are hand-computed from the printed lines (line 23, the adjusted family net
income, is the net income of 5005-R line 23600: the salary less the Schedule 8 enhanced QPP
deduction, 165.00 at $20,000, 665.00 at $70,000 and 1,074.00 at $200,000), not from a CRA example.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import (
    CWB_BASE_AMOUNT,
    CWB_BASIC_BENEFIT_LINE_22,
    CWB_BENEFIT_LINE_28,
    CWB_MAXIMUM,
    CWB_NET_INCOME_OVER_BASE_AMOUNT,
    CWB_REDUCTION_LINE_27,
    CWB_REDUCTION_THRESHOLD,
    CWB_WORKING_INCOME_OVER_BASE_AMOUNT,
    CWB_WORKING_INCOME_RATE_LINE_20,
)
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import real_import

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
    """)
# The real Quebec manifest's imports of Schedules 8 and 6, with their dataset swaps.
HEADER = HEADER_TEMPLATE + real_import("ca/schedule_8") + real_import("ca/schedule_6")
BARE_HEADER = HEADER_TEMPLATE + "  - ca/schedule_8\n  - ca/schedule_6\n"
# The real Quebec T1 parts that give Schedule 6 line 7 its net income; the form declaration is the
# first of them. Every other T1 input is blank for a salary-only filer.
T1_PARTS = sorted(path.name for path in QUEBEC_PARTS.glob("t1_taxable_income*.yaml"))
FORM_PART = "capabilities: []\n"

AMOUNT_LINES: dict[str, AmountKind] = {
    "17": CWB_BASE_AMOUNT,
    "21": CWB_MAXIMUM,
    "24": CWB_REDUCTION_THRESHOLD,
}


def schedule_6(take_home_service: TakeHomeService, salary: str, header: str = HEADER) -> Worksheet:
    worksheets = take_home_service(header, FORM_PART, *T1_PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 16 (the salary) less line 17 (2,400.00).
        ("20000", "17600.00"),
        ("70000", "67600.00"),
        ("200000", "197600.00"),
    ],
)
def test_line_18_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_6(take_home_service, salary)

    assert sheet.get(CWB_WORKING_INCOME_OVER_BASE_AMOUNT).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 18 x 37.3% (line 19): 17,600 x 0.373 = 6,564.80.
        ("20000", "6564.80"),
        ("70000", "25214.80"),
        ("200000", "73704.80"),
    ],
)
def test_line_20_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_6(take_home_service, salary)

    assert sheet.get(CWB_WORKING_INCOME_RATE_LINE_20).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # The lesser of line 20 and line 21 (3,812.06): line 21 at every salary here.
        ("20000", "3812.06"),
        ("70000", "3812.06"),
        ("200000", "3812.06"),
    ],
)
def test_line_22_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_6(take_home_service, salary)

    assert sheet.get(CWB_BASIC_BENEFIT_LINE_22).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 23 (19,835.00; 69,335.00; 198,926.00) less line 24 (14,170.05).
        ("20000", "5664.95"),
        ("70000", "55164.95"),
        ("200000", "184755.95"),
    ],
)
def test_line_25_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_6(take_home_service, salary)

    assert sheet.get(CWB_NET_INCOME_OVER_BASE_AMOUNT).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 25 x 20% (line 26): 5,664.95 x 0.20 = 1,132.99.
        ("20000", "1132.99"),
        ("70000", "11032.99"),
        ("200000", "36951.19"),
    ],
)
def test_line_27_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_6(take_home_service, salary)

    assert sheet.get(CWB_REDUCTION_LINE_27).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 22 less line 27, floored at 0: 3,812.06 - 1,132.99 = 2,679.07; then negative.
        ("20000", "2679.07"),
        ("70000", "0.00"),
        ("200000", "0.00"),
    ],
)
def test_line_28_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_6(take_home_service, salary)

    assert sheet.get(CWB_BENEFIT_LINE_28).value == D(expected)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_the_swapped_lines_read_the_quebec_figures(
    take_home_service: TakeHomeService, salary: str
) -> None:
    # Lines 17, 21 and 24 print a figure that the Quebec datasets hold as printed.
    sheet = schedule_6(take_home_service, salary)

    assert {line: sheet.get(kind).value for line, kind in AMOUNT_LINES.items()} == {
        "17": D("2400.00"),
        "21": D("3812.06"),
        "24": D("14170.05"),
    }


def test_the_same_salary_without_the_swaps_still_gets_the_federal_figures(
    take_home_service: TakeHomeService,
) -> None:
    # The shared form's own files still read the federal datasets (3,000, 27%, 1,633, 26,855, 15%):
    # a manifest that imports `ca/schedule_6` bare gets 1,633.00 at $20,000, so the swap is local.
    sheet = schedule_6(take_home_service, "20000", BARE_HEADER)

    assert sheet.get(CWB_BASE_AMOUNT).value == D("3000.00")
    assert sheet.get(CWB_BENEFIT_LINE_28).value == D("1633.00")
