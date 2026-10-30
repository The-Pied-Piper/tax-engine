"""CA-ON 2025 end to end: return ha, Schedule 6 Part B with the UCCB and RDSP lines.

Return HA is `returns/2025_return_ha.yaml`: a single filer with employment income of 30000, the
UCCB (5000), RDSP income (2000), the UCCB repayment (1000) and an RDSP income repayment (500, in the
500 of line 23200) all together. Schedule 6 Part B adds the repayments (line 9) to net income
(line 7) and takes the UCCB and RDSP income (line 11) away, not below zero (line 12), so each of
them alone, and all together, leaves the adjusted family net income at the 29735.00 of the filer
with employment income alone and the benefit at 1201.00. The figures are chosen and worked out by
hand from the form text, as the description of the return shows.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CWB_FAMILY_NET_INCOME_LINE_10,
    CWB_FAMILY_NET_INCOME_LINE_12,
    NET_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ha(**overrides: Any) -> Worksheet:
    """Return HA's worksheet: Return GE's filer (employment income of 30000, a deduction limit of
    5400 and 3000 deducted) with no spouse and, unless overridden, none of the four figures."""
    inputs: dict[str, Any] = {"income_tax_deducted": "3000"}
    return compute("30000", (), "0", "0", "5400", "0", "0", **{**inputs, **overrides})


def test_the_filer_with_employment_income_alone_is_the_baseline() -> None:
    # Net income 30000 - 265.00 (enhanced CPP) = 29735.00: line 7; lines 9 and 11 are 0, so lines
    # 10, 12 and 15 are the same. Line 25 = 29735 - 26855 = 2880, line 27 = 432.00, line 28 =
    # 1633 - 432 = 1201.00.
    worksheet = return_ha()

    assert worksheet.get(NET_INCOME).value == D("29735.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_10).value == D("29735.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_12).value == D("29735.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("29735.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1201.00")


@pytest.mark.parametrize(
    "overrides",
    [
        {"universal_child_care_benefit": "5000"},
        {"rdsp_income": "5000"},
    ],
)
def test_uccb_or_rdsp_income_alone_is_taken_off_on_line_11(overrides: dict[str, str]) -> None:
    # 5000 more total income: net income 34735.00 (line 7) = line 10; line 11 takes the 5000 back,
    # so line 12 = 34735 - 5000 = 29735.00 and the benefit is 1201.00, not the 451.00 that the net
    # income alone gives (line 25 = 34735 - 26855 = 7880, line 27 = 1182, 1633 - 1182 = 451).
    worksheet = return_ha(**overrides)

    assert worksheet.get(NET_INCOME).value == D("34735.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_10).value == D("34735.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_12).value == D("29735.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("29735.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1201.00")


@pytest.mark.parametrize(
    "overrides",
    [
        {"uccb_repayment": "1000"},
        {"rdsp_income_repayment": "1000", "other_deductions": "1000"},
    ],
)
def test_a_repayment_alone_is_added_back_on_line_9(overrides: dict[str, str]) -> None:
    # The 1000 is a deduction (line 21300, or in the line 23200 amount): net income 28735.00 is
    # line 7, line 9 adds the 1000 back, so line 10 = 29735.00 and, with line 11 = 0, line 12 and
    # the benefit are those of the baseline, not the 1351.00 that the net income alone gives (line
    # 25 = 28735 - 26855 = 1880, line 27 = 282, 1633 - 282 = 1351).
    worksheet = return_ha(**overrides)

    assert worksheet.get(NET_INCOME).value == D("28735.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_10).value == D("29735.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_12).value == D("29735.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("29735.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1201.00")


def test_all_four_together_are_those_of_return_ha() -> None:
    # Net income 35235.00, line 9 = 1500, line 10 = 36735.00, line 11 = 7000, line 12 = 29735.00.
    worksheet = return_ha(
        universal_child_care_benefit="5000",
        rdsp_income="2000",
        uccb_repayment="1000",
        rdsp_income_repayment="500",
        other_deductions="500",
    )

    assert worksheet.get(NET_INCOME).value == D("35235.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_10).value == D("36735.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_12).value == D("29735.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("29735.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1201.00")


def test_line_12_is_not_below_zero_when_the_uccb_is_more_than_line_10() -> None:
    # Employment income 3000 and a UCCB of 5000 less line 23200 deductions of 6000 (no CPP on 3000,
    # below the 3500 exemption): line 7 = 2000.00, line 10 = 2000.00, line 11 =
    # 5000.00 and line 12 = 2000 - 5000 is negative, so 0; the adjusted family net income is 0.
    worksheet = compute(
        "3000",
        (),
        "0",
        "0",
        "5400",
        "0",
        "0",
        universal_child_care_benefit="5000",
        other_deductions="6000",
    )
    assert worksheet.get(NET_INCOME).value == D("2000.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_10).value == D("2000.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_12).value == D("0")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("0")
