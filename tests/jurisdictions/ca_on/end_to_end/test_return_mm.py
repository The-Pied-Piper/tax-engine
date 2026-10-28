"""CA-ON 2025 end to end: return mm, Schedule 6 line 38102 "Are you claiming the basic CWB?".

Return MM is `returns/2025_return_mm.yaml`: the single resident of Return MC with employment income
of 20,000 who is eligible for the disability tax credit, answering no to line 38102, so line 41 is
0 and T1 line 45300 is line 40 alone, 843.00. The other tests here vary the answers: yes, no without
the DTC, and an answer of 2.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    ADVANCED_CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_LINE_28,
    CANADA_WORKERS_BENEFIT_LINE_41,
    CANADA_WORKERS_BENEFIT_LINE_42,
    CWB_CLAIMED,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def test_not_claiming_the_basic_cwb_leaves_only_the_supplement() -> None:
    # Line 28 is still 1,633.00 (27% x 17,000 = 4,590.00, at most 1,633), but line 41 "If you
    # completed Step 2, enter the amount from line 28. If not, enter "0"." is 0, so line 42 is
    # line 40 alone, 843.00, and with the DTC (line 38103) that is line 45300.
    worksheet = compute(
        "20000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=1,
        cwb_claiming_basic=0,
    )

    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_28).value == D("1633.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_41).value == D("0.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_42).value == D("843.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("843.00")


def test_claiming_the_basic_cwb_adds_line_28_as_line_41() -> None:
    worksheet = compute(
        "20000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=1,
        cwb_claiming_basic=1,
    )

    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_41).value == D("1633.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("2476.00")


def test_not_claiming_the_basic_cwb_without_the_dtc_is_nothing() -> None:
    # Line 38103 is no: "If you are not completing Step 3, enter this amount [line 28] on line
    # 45300", and line 28 is not paid when Step 2 is not completed (line 38102 is no).
    worksheet = compute(
        "20000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=0,
        cwb_claiming_basic=0,
    )

    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0.00")


def test_a_basic_cwb_answer_of_2_is_refused_and_not_read_as_yes() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match="ca/cwb_claiming_basic 2 is above a yes or no answer of 1",
    ):
        compute(
            "20000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            cwb_claiming_basic=2,
        )


def test_line_43_takes_line_28_only_when_step_2_is_completed() -> None:
    # Line 43 "Enter whichever is more: amount from line 28 or line 42": Step 2 is not completed
    # (line 38102 is no), so line 28 is not entered, as line 41 is 0, and line 43 is line 42,
    # 843.00. With 1,000.00 of box 10 ACWB paid (line 46), line 49 is the lesser of lines 43 and 48,
    # 843.00.
    worksheet = compute(
        "20000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=1,
        cwb_claiming_basic=0,
        acwb_paid_to_you="1000",
    )

    assert worksheet.get(CWB_CLAIMED).value == D("843.00")
    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("843.00")
