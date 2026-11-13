"""Schedule 6 (2025, Alberta edition 5009-S6, basic CWB, single filer) from the salary alone: the
shared federal form composed with the Alberta dataset swap.

The Alberta manifest imports `ca/schedule_6` with `datasets` that read the Alberta figures of the
5009-S6 in place of the federal ones. This module composes a test-only Alberta header (so the real
header's unbuilt output is not needed) that imports the forms Schedule 6 reads (T1 taxable income
and Schedule 8) and Schedule 6 with the same swap, and types in only the gross salary
(`ca/employment_income`). The service is built over the Alberta package list of
`tests/jurisdictions/ca_ab/support.py`, as Alberta is not in `registrations.JURISDICTIONS`.

Form text: "Line 16: Family working income from line 6";
"Line 17: Base amount 2,760.00"; "Line 18: Line 16 minus line 17 (if negative, enter "0")";
"Line 19:
Rate 21%"; "Line 20: Line 18 multiplied by the percentage from line 19"; "Line 21: If you had an
eligible spouse or an eligible dependant, enter $2,619. If not, enter $1,750."; "Line 22: Enter
whichever is less: amount from line 20 or line 21."; "Line 24: ... If not, enter $26,159."; "Line
25: Line 23 minus line 24 (if negative, enter "0")"; "Line 26: Rate 15%"; "Line 27: Line 25
multiplied by the percentage from line 26"; "Line 28: Line 22 minus line 27 (if negative, enter
"0")". Line 18 reads line 16, the family working income (the salary); line 25 reads line 23, the
adjusted family net income (the salary less the Schedule 8 enhanced contributions).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
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
from tests.jurisdictions.ca_ab.support import alberta_service

D = Decimal
HEADER_TEMPLATE = dedent("""\
    jurisdiction: CA-AB
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
      - ca/t1_taxable_income
      - {schedule_6}
      - ca/schedule_8
    """)
SWAPPED = (
    "form: ca/schedule_6\n"
    "    datasets:\n"
    "      ca/cwb_base_amount: ca-ab/cwb_base_amount\n"
    "      ca/cwb_rate: ca-ab/cwb_rate\n"
    "      ca/cwb_maximum: ca-ab/cwb_maximum\n"
    "      ca/cwb_reduction_threshold: ca-ab/cwb_reduction_threshold"
)
HEADER = HEADER_TEMPLATE.replace("{schedule_6}", SWAPPED)
BARE_HEADER = HEADER_TEMPLATE.replace("{schedule_6}", "ca/schedule_6")

AMOUNT_LINES: dict[str, AmountKind] = {
    "17": CWB_BASE_AMOUNT,
    "18": CWB_WORKING_INCOME_OVER_BASE_AMOUNT,
    "20": CWB_WORKING_INCOME_RATE_LINE_20,
    "21": CWB_MAXIMUM,
    "22": CWB_BASIC_BENEFIT_LINE_22,
    "24": CWB_REDUCTION_THRESHOLD,
    "25": CWB_NET_INCOME_OVER_BASE_AMOUNT,
    "27": CWB_REDUCTION_LINE_27,
    "28": CWB_BENEFIT_LINE_28,
}

# Net income (lines 7 to 15, and the adjusted family net income of line 23) is the salary less the
# Schedule 8 enhanced CPP contributions (T1 line 22215): 165.00 at $20,000, as the Ontario test
# shows. Line 18 is the salary (line 16) less 2,760.00.
CASES: list[tuple[str, dict[str, str]]] = [
    # 20,000 - 2,760 = 17,240; x 21% = 3,620.40; less of that and 1,750 is 1,750. Line 23 is
    # 19,835.00, under 26,159, so line 25 and line 27 are 0 and line 28 is 1,750.
    ("20000", {"17": "2760.00", "18": "17240.00", "20": "3620.40", "21": "1750.00",
               "22": "1750.00", "24": "26159.00", "25": "0.00", "27": "0.00", "28": "1750.00"}),
    # 70,000 - 2,760 = 67,240; x 21% = 14,120.40; line 22 is 1,750. Line 23 is 69,335.00;
    # 69,335 - 26,159 = 43,176; x 15% = 6,476.40; 1,750 - 6,476.40 is negative, so line 28 is 0.
    ("70000", {"17": "2760.00", "18": "67240.00", "20": "14120.40", "21": "1750.00",
               "22": "1750.00", "24": "26159.00", "25": "43176.00", "27": "6476.40",
               "28": "0.00"}),
]  # fmt: skip


def schedule_6(tmp_path: Path, salary: str, header: str = HEADER) -> Worksheet:
    worksheets = alberta_service(tmp_path, header).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_every_line_matches_the_printed_alberta_form(
    tmp_path: Path, salary: str, expected: dict[str, str]
) -> None:
    sheet = schedule_6(tmp_path, salary)

    assert {line: sheet.get(kind).value for line, kind in AMOUNT_LINES.items()} == {
        line: D(figure) for line, figure in expected.items()
    }


def test_the_benefit_at_twenty_thousand_is_the_alberta_figure(tmp_path: Path) -> None:
    # The federal edition gives 1,633.00 at $20,000; the Alberta edition's maximum is 1,750.00.
    assert schedule_6(tmp_path, "20000").get(CWB_BENEFIT_LINE_28).value == D("1750.00")


def test_the_benefit_at_two_hundred_thousand_is_zero(tmp_path: Path) -> None:
    # Net income is far past the phase-out (line 25 is over 170,000), so line 27 exceeds line 22
    # (1,750.00) and line 28 floors to 0.
    sheet = schedule_6(tmp_path, "200000")

    assert sheet.get(CWB_BASIC_BENEFIT_LINE_22).value == D("1750.00")
    assert sheet.get(CWB_REDUCTION_LINE_27).value > D("1750.00")
    assert sheet.get(CWB_BENEFIT_LINE_28).value == D("0.00")


def test_the_same_salary_without_the_swap_still_gets_the_federal_figure(tmp_path: Path) -> None:
    # The shared form's own files still read the federal datasets: a manifest that imports
    # `ca/schedule_6` bare gets 1,633.00 at $20,000, so the swap is local to the importing manifest.
    sheet = schedule_6(tmp_path, "20000", BARE_HEADER)

    assert sheet.get(CWB_BENEFIT_LINE_28).value == D("1633.00")
