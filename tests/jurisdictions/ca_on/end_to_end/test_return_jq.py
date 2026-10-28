"""CA-ON 2025 end to end: return jq, the U.S. Social Security treaty deduction on T1 line 25600.

Return JQ is `returns/2025_return_jq.yaml`: a single Ontario resident with employment income of
10000 and other pensions of 20000 (line 11500), of which 12000 is U.S. Social Security benefits,
received by a resident of Canada since before January 1, 1996. Guide 5000-G "Line 25600 -
Additional deductions" gives a deduction of 15% of the benefits, or 50% for that resident: 6000.00
here, so line 25600 is 6000.00 and taxable income is 29935.00 - 6000.00 = 23935.00.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS_TOTAL,
    DEDUCTIONS_FROM_NET_INCOME,
    EXEMPT_INCOME_DEDUCTIONS_CHECKED,
    NET_INCOME,
    TAXABLE_INCOME,
    US_SOCIAL_SECURITY_BENEFITS_CHECKED,
    US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE,
    US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE,
    US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996_CHECKED,
    US_SOCIAL_SECURITY_TREATY_DEDUCTION,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_jq(**overrides: Any) -> Worksheet:
    """Return JQ's inputs over the keyword overrides given: employment income of 10000, other
    pensions of 20000 with 12000 of U.S. Social Security benefits, a resident since before 1996."""
    inputs: dict[str, Any] = {
        "other_pensions_and_superannuation": "20000",
        "us_social_security_benefits": "12000",
        "us_social_security_resident_since_before_1996": 1,
    }
    inputs.update(overrides)
    return compute("10000", (), "0", "0", "0", "0", "0", **inputs)


def test_a_resident_since_before_1996_deducts_50_percent_of_the_benefits() -> None:
    worksheet = return_jq()

    assert worksheet.get(US_SOCIAL_SECURITY_BENEFITS_CHECKED).value == D("12000")
    assert worksheet.get(US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE).value == D("1800.00")
    assert worksheet.get(US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE).value == D("6000.00")
    assert worksheet.get(US_SOCIAL_SECURITY_TREATY_DEDUCTION).value == D("6000.00")
    assert worksheet.get(ADDITIONAL_DEDUCTIONS_TOTAL).value == D("6000.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("6000.00")
    assert worksheet.get(NET_INCOME).value == D("29935.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("23935.00")


def test_any_other_filer_deducts_15_percent_of_the_benefits() -> None:
    worksheet = return_jq(us_social_security_resident_since_before_1996=0)

    assert worksheet.get(US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996_CHECKED).value == 0
    assert worksheet.get(US_SOCIAL_SECURITY_TREATY_DEDUCTION).value == D("1800.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("28135.00")


def test_no_benefits_leaves_line_25600_as_the_filer_entered_it() -> None:
    worksheet = return_jq(us_social_security_benefits="0", additional_deductions="500")

    assert worksheet.get(US_SOCIAL_SECURITY_TREATY_DEDUCTION).value == D("0.00")
    assert worksheet.get(ADDITIONAL_DEDUCTIONS_TOTAL).value == D("500")
    assert worksheet.get(TAXABLE_INCOME).value == D("29435.00")


def test_the_treaty_deduction_is_added_to_the_filers_other_additional_deductions() -> None:
    worksheet = return_jq(additional_deductions="500")

    assert worksheet.get(ADDITIONAL_DEDUCTIONS_TOTAL).value == D("6500.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("6500.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("23435.00")


def test_the_benefits_are_rounded_to_the_cent_at_each_rate() -> None:
    worksheet = return_jq(us_social_security_benefits="12345.67")

    assert worksheet.get(US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE).value == D("1851.85")
    assert worksheet.get(US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE).value == D("6172.84")


def test_benefits_above_line_11500_are_refused_and_not_capped() -> None:
    # The benefits are "reported as income on line 11500", so they are part of the 20000.
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/us_social_security_benefits 20000.01 is above "
        r"ca/other_pensions_and_superannuation 20000",
    ):
        return_jq(us_social_security_benefits="20000.01")


def test_a_resident_since_before_1996_answer_of_2_is_refused_and_not_read_as_yes() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match="us_social_security_resident_since_before_1996 2 is above a yes or no answer of 1",
    ):
        return_jq(us_social_security_resident_since_before_1996=2)


def test_exempt_treaty_income_can_be_the_whole_of_line_25600_including_the_treaty_deduction() -> (
    None
):
    # Form T2209 note (3): the part of line 25600 that is foreign income exempt under a treaty is at
    # most the whole of line 25600, which includes the computed deduction, not only the amount the
    # filer specifies (0 here).
    worksheet = return_jq(exempt_income_deductions="6000")

    assert worksheet.get(EXEMPT_INCOME_DEDUCTIONS_CHECKED).value == D("6000")

    with pytest.raises(
        InputAboveBoundError,
        match=re.escape(
            "ca/exempt_income_deductions 6000.01 is above ca/additional_deductions_total"
        ),
    ):
        return_jq(exempt_income_deductions="6000.01")


def test_the_trace_shows_the_50_percent_deduction_chosen_and_added_to_line_25600() -> None:
    rendered = EnglishTraceRenderer().render_all(return_jq().trace)

    assert (
        "us_social_security_benefits_checked: us_social_security_benefits 12000, "
        "at most other_pensions_and_superannuation 20000"
    ) in rendered
    assert (
        "us_social_security_deduction_at_resident_rate: "
        "50% of us_social_security_benefits_checked 12000 (half-up to 0.01)"
    ) in rendered
    assert (
        "us_social_security_treaty_deduction: us_social_security_deduction_at_resident_rate 6000, "
        "chosen as us_social_security_resident_since_before_1996_checked is 1"
    ) in rendered
    assert (
        "additional_deductions_total: additional_deductions 0 + "
        "us_social_security_treaty_deduction 6000 = 6000"
    ) in rendered
