"""CA-ON 2025 end to end: return mc, the Canada workers benefit disability supplement.

Return MC is `returns/2025_return_mc.yaml`: a single resident with employment income of 20,000 who
is eligible for the disability tax credit, so Schedule 6 Step 3 adds a supplement of 843.00 to the
basic benefit of 1,633.00 and T1 line 45300 is 2,476.00. The other tests here vary the answers:
no DTC, an eligible dependant, an eligible spouse (also eligible for the DTC or not), an
adjusted family net income over the base amount, and a working income under 1,150.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_LINE_28,
    CANADA_WORKERS_BENEFIT_LINE_42,
    CWB_DISABILITY_REDUCTION,
    CWB_DISABILITY_SUPPLEMENT,
    CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, compute_with_spouse


def test_return_mc_adds_the_disability_supplement_of_843_to_the_basic_benefit() -> None:
    # Working income 20,000 (line 29): line 31 is 20,000 - 1,150 = 18,850 and line 33 27% of it,
    # 5,089.50, so line 34 is the least of that and 843. The adjusted family net income (line 35)
    # is 19,835.00, under the 37,740 of line 36, so lines 37 and 39 are 0 and line 40 is 843.00.
    # Line 41 is line 28, 1,633.00 (27% x 17,000 = 4,590.00, at most 1,633; nothing to reduce it),
    # so line 42, and T1 line 45300, is 2,476.00.
    worksheet = compute("20000", (), "0", "0", "0", "0", "0", eligible_for_disability_amount=1)

    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("19835.00")
    assert worksheet.get(CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION).value == D("843.00")
    assert worksheet.get(CWB_DISABILITY_REDUCTION).value == D("0.00")
    assert worksheet.get(CWB_DISABILITY_SUPPLEMENT).value == D("843.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_28).value == D("1633.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_42).value == D("2476.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("2476.00")


def test_without_the_dtc_the_benefit_is_the_basic_benefit_alone() -> None:
    # Line 38103 is no: "If you are not completing Step 3, enter this amount on line 45300", so
    # line 28, 1,633.00. The supplement is still worked out from the lines, 843.00, and not paid.
    worksheet = compute("20000", (), "0", "0", "0", "0", "0", eligible_for_disability_amount=0)

    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_42).value == D("2476.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1633.00")


def test_the_reduction_takes_15_percent_of_the_family_net_income_over_37740() -> None:
    # Employment income 38,500: the enhanced CPP deduction is 1% x (38,500 - 3,500) = 350.00, so the
    # adjusted family net income is 38,150.00 and line 37 is 38,150.00 - 37,740 = 410.00. Line 39 is
    # 15% of it, 61.50, and line 40 is 843.00 - 61.50 = 781.50. Step 2's reduction (line 27, 15% x
    # (38,150.00 - 26,855) = 1,694.25) is over the 1,633 of line 22, so line 28 and line 41 are 0
    # and the benefit is line 42, 781.50.
    worksheet = compute("38500", (), "0", "0", "0", "0", "0", eligible_for_disability_amount=1)

    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("38150.00")
    assert worksheet.get(CWB_DISABILITY_REDUCTION).value == D("61.50")
    assert worksheet.get(CWB_DISABILITY_SUPPLEMENT).value == D("781.50")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_28).value == D("0.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("781.50")


def test_the_supplement_is_gone_when_the_reduction_passes_843() -> None:
    # Employment income 45,000: adjusted family net income 44,585.00, line 37 is 6,845.00 and
    # line 39 is 1,026.75, over the 843.00 of line 34, so line 40 is 0 and the benefit is 0.
    worksheet = compute("45000", (), "0", "0", "0", "0", "0", eligible_for_disability_amount=1)

    assert worksheet.get(CWB_DISABILITY_REDUCTION).value == D("1026.75")
    assert worksheet.get(CWB_DISABILITY_SUPPLEMENT).value == D("0.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0.00")


def test_a_working_income_of_1150_or_less_has_no_supplement() -> None:
    # Line 31 "Line 29 minus line 30 (if negative, enter "0")": 1,000 - 1,150 is below zero.
    worksheet = compute("1000", (), "0", "0", "0", "0", "0", eligible_for_disability_amount=1)

    assert worksheet.get(CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION).value == D("0.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0.00")


def test_an_eligible_dependant_moves_line_36_to_49389() -> None:
    # Employment income 50,000, an eligible dependant (line 38100): the adjusted family net income
    # is 50,000 - 1% x 46,500 = 49,535.00, line 36 is 49,389, line 37 is 146.00 and line 39 is 15%
    # of it, 21.90, so line 40 is 843.00 - 21.90 = 821.10. Step 2's line 28 (2,813 less 15% x
    # (49,535.00 - 30,639), 2,834.40) is 0, so the benefit is 821.10.
    worksheet = compute(
        "50000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=1,
        cwb_eligible_dependants=1,
    )

    assert worksheet.get(CWB_DISABILITY_REDUCTION).value == D("21.90")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("821.10")


def test_an_eligible_spouse_who_is_also_eligible_for_the_dtc_takes_7_point_5_percent() -> None:
    # The same return with an eligible spouse (line 38101) with no income: line 36 is 49,389 and
    # line 38 is 7.5% when the spouse is also eligible for the DTC (line 38104), so line 39 is 7.5%
    # x 146.00 = 10.95 and line 40 is 832.05; with a spouse who is not, 15%, 21.90 and 821.10.
    with_dtc = compute_with_spouse(
        "0",
        "50000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=1,
        spouse_or_common_law_partner_on_december_31=1,
        cwb_eligible_spouse_eligible_for_dtc=1,
    )
    without_dtc = compute_with_spouse(
        "0",
        "50000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=1,
        spouse_or_common_law_partner_on_december_31=1,
        cwb_eligible_spouse_eligible_for_dtc=0,
    )

    assert with_dtc.get(CWB_DISABILITY_REDUCTION).value == D("10.95")
    assert with_dtc.get(CANADA_WORKERS_BENEFIT).value == D("832.05")
    assert without_dtc.get(CWB_DISABILITY_REDUCTION).value == D("21.90")
    assert without_dtc.get(CANADA_WORKERS_BENEFIT).value == D("821.10")


def test_a_dtc_spouse_answer_of_yes_with_no_eligible_spouse_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="cwb_eligible_spouse_eligible_for_dtc_checked"):
        compute(
            "20000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            eligible_for_disability_amount=1,
            cwb_eligible_spouse_eligible_for_dtc=1,
        )


def test_a_dtc_spouse_answer_of_2_is_refused_and_not_read_as_yes() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match="ca/cwb_eligible_spouse_eligible_for_dtc 2 is above a yes or no answer of 1",
    ):
        compute(
            "20000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            eligible_for_disability_amount=1,
            cwb_eligible_spouse_eligible_for_dtc=2,
        )
