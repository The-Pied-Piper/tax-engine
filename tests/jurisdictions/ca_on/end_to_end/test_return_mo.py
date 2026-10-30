"""CA-ON 2025 end to end: return mo, Schedule 6 Step 4 line 46 when the spouse claims the basic CWB.

Return MO is `returns/2025_return_mo.yaml`: the filer of Return MM (eligible for the disability tax
credit, not claiming the basic CWB) with an eligible spouse who is claiming the basic CWB for her,
box 10 of $600.00 (line 44) and box 11 of $100.00 (line 47). Line 46 is 0, so line 48 is 100.00 and
line 49, T1 line 41500, is 100.00. The other tests vary the answers.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ACWB_BASIC_PAID,
    ACWB_LINE_46_APPLIES,
    ACWB_LINES_44_AND_45,
    ACWB_PAID,
    ADVANCED_CANADA_WORKERS_BENEFIT,
    CWB_CLAIMED,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_mo(
    eligible_for_disability_amount: int = 1,
    cwb_eligible_spouses: int = 1,
    spouse_or_common_law_partner_on_december_31: int = 1,
    cwb_spouse_claiming_basic: int = 1,
    cwb_claiming_basic: int = 0,
) -> Worksheet:
    """Return MO's inputs over the answers given: an eligible spouse claiming the basic CWB for the
    filer, who is claiming the disability supplement, with 600 of box 10 and 100 of box 11."""
    return compute(
        "20000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=eligible_for_disability_amount,
        cwb_claiming_basic=cwb_claiming_basic,
        cwb_eligible_spouses=cwb_eligible_spouses,
        spouse_or_common_law_partner_on_december_31=spouse_or_common_law_partner_on_december_31,
        cwb_spouse_claiming_basic=cwb_spouse_claiming_basic,
        acwb_paid_to_you="600",
        acwb_disability_supplement_paid="100",
    )


def test_a_spouse_claiming_the_basic_cwb_zeroes_line_46_for_a_filer_with_the_supplement() -> None:
    # Line 46 "enter "0" on line 46 and continue on line 47": line 48 is line 47 alone, 100.00, and
    # line 49 is the lesser of line 43, 843.00, and line 48, 100.00.
    worksheet = return_mo()

    assert worksheet.get(ACWB_LINES_44_AND_45).value == D("600.00")
    assert worksheet.get(ACWB_LINE_46_APPLIES).value == 0
    assert worksheet.get(ACWB_BASIC_PAID).value == D("0")
    assert worksheet.get(ACWB_PAID).value == D("100.00")
    assert worksheet.get(CWB_CLAIMED).value == D("843.00")
    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("100.00")


def test_line_46_is_lines_44_and_45_when_the_spouse_is_not_claiming_the_basic_cwb() -> None:
    # Neither of them claims the basic CWB: "one of you must report the amount from box 10 of all
    # RC210 slips as if you were claiming it", so line 46 is 600.00, line 48 is 700.00 and line 49
    # is the lesser of 843.00 and 700.00.
    worksheet = return_mo(cwb_spouse_claiming_basic=0)

    assert worksheet.get(ACWB_LINE_46_APPLIES).value == 1
    assert worksheet.get(ACWB_BASIC_PAID).value == D("600.00")
    assert worksheet.get(ACWB_PAID).value == D("700.00")
    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("700.00")


def test_line_46_is_lines_44_and_45_when_the_filer_is_not_claiming_the_supplement() -> None:
    # The rule is for a filer who is claiming the disability supplement (line 38103).
    worksheet = return_mo(eligible_for_disability_amount=0)

    assert worksheet.get(ACWB_LINE_46_APPLIES).value == 1
    assert worksheet.get(ACWB_BASIC_PAID).value == D("600.00")


def test_a_spouse_claiming_answer_of_2_is_refused_and_not_read_as_yes() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match="ca/cwb_spouse_claiming_basic 2 is above a yes or no answer of 1",
    ):
        return_mo(cwb_spouse_claiming_basic=2)


def test_a_filer_claiming_the_basic_cwb_keeps_line_46_whatever_the_spouse_answer() -> None:
    # Step 2: "If you had an eligible spouse, only one of you can claim the basic CWB", and the rule
    # is for the filer whose spouse claims it "for you", so a filer who answers yes to line 38102
    # is outside it and line 46 is lines 44 and 45.
    worksheet = return_mo(cwb_claiming_basic=1)

    assert worksheet.get(ACWB_LINE_46_APPLIES).value == 1
    assert worksheet.get(ACWB_BASIC_PAID).value == D("600.00")


def test_a_spouse_claiming_answer_with_no_eligible_spouse_is_refused() -> None:
    # The rule is about "an eligible spouse who is claiming the basic CWB for you".
    with pytest.raises(
        InputAboveBoundError,
        match="ca/cwb_spouse_claiming_basic_checked 1 is above ca/cwb_eligible_spouses_checked 0",
    ):
        return_mo(cwb_eligible_spouses=0, spouse_or_common_law_partner_on_december_31=0)
