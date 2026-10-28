"""CA-ON 2025 end to end: return ca."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.trace import RatioAppliedLine, SubtractedLine, SubtractedNotBelowZeroLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FEDERAL_FOREIGN_TAX_CREDIT,
    NET_FEDERAL_TAX,
    OTHER_SPLIT_INCOME,
    OTHER_SPLIT_INCOME_CHECKED,
    SPLIT_INCOME_DIVIDENDS_CHECKED,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1,
    SPLIT_INCOME_FROM_FOREIGN_SOURCES,
    SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
    SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3,
    SPLIT_INCOME_LINE_22,
    SPLIT_INCOME_LINE_23,
    SPLIT_INCOME_LINE_24,
    SPLIT_INCOME_LINE_29,
    SPLIT_INCOME_LINE_30,
    SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES,
    SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED,
    SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370,
    TOTAL_INCOME,
    TOTAL_INCOME_FROM_FOREIGN_SOURCES,
    TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES,
    TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute, routed_statement


def return_ca(**overrides: Any) -> Worksheet:
    """Return CA's inputs, as in `returns/2025_return_ca.yaml`, over the keyword overrides given.

    Return AL's filer (10000 of dividends with no slip, 11500 of split income on lines 1 and 2 of
    Form T1206) with 40000 of other income that is all split income from foreign sources (line 3)
    and 10000 of other foreign investment income, 15000 of foreign tax paid to one country, the
    whole 50000 being net foreign non-business income. Lines 68370 and 68380 are 40000 and 50000,
    and so are their non-business parts.
    """
    inputs: dict[str, Any] = {
        "other_dividends_received_without_a_slip": "10000",
        "other_income": "40000",
        "foreign_investment_income": "10000",
        "foreign_tax_countries_rows": (("15000", "50000"),),
        "split_income_dividends": "11500",
        "split_income_dividends_other_than_eligible": "11500",
        "other_split_income": "40000",
        "split_income_from_foreign_sources": "40000",
        "total_income_from_foreign_sources": "50000",
        "split_income_non_business_from_foreign_sources": "40000",
        "total_non_business_income_from_foreign_sources": "50000",
    }
    inputs.update(overrides)
    return compute("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_cas_line_23_is_the_foreign_share_of_the_federal_foreign_tax_credit() -> None:
    worksheet = return_ca()

    # T2209: 50000 x 16106.29 / 61500.00 = 13094.5447..., less than the 15000 paid, so line 40500
    # is 13094.54. T1206 line 23 is that x 40000 / 50000 = 10475.632, rounded half-up to the cent.
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("13094.54")
    assert worksheet.get(SPLIT_INCOME_FROM_FOREIGN_SOURCES).value == D("40000")
    assert worksheet.get(TOTAL_INCOME_FROM_FOREIGN_SOURCES).value == D("50000")
    assert worksheet.get(SPLIT_INCOME_LINE_23).value == D("10475.63")


def test_return_cas_line_24_takes_line_23_off_line_22_and_line_30_follows_it() -> None:
    worksheet = return_ca()

    # Line 22 is 16995.00 - 1038.46 = 15956.54; line 24 is 15956.54 - 10475.63 = 5480.91, more than
    # line 29 (1973.29), so it is line 30 and the net federal tax.
    assert worksheet.get(SPLIT_INCOME_LINE_22).value == D("15956.54")
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("5480.91")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("1973.29")
    assert worksheet.get(SPLIT_INCOME_LINE_30).value == D("5480.91")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("5480.91")


def test_return_cas_ontario_line_49_is_the_non_business_share_of_on428_line_82() -> None:
    worksheet = return_ca()

    # T2036 line 3 is 15000 - 13094.54 = 1905.46 (line 4, 8595.89, is more), so ON428 line 82 is
    # 1905.46. T1206 line 49 is that x 40000 / 50000 = 1524.368, rounded half-up to the cent;
    # line 50 is 10229.53 - 1524.37 = 8705.16, more than ON428 line 88 (8324.07), so it is line 52.
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("1905.46")
    assert worksheet.get(SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES).value == D("40000")
    assert worksheet.get(TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES).value == D("50000")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_47).value == D("10229.53")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_49).value == D("1524.37")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("8705.16")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("8324.07")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_52).value == D("8705.16")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("9305.16")
    assert worksheet.get(TOTAL_PAYABLE).value == D("14786.07")


def test_the_ontario_share_reads_its_own_non_business_figures() -> None:
    # 30000 of the 40000 is non-business income: line 49 is 1905.46 x 30000 / 50000 = 1143.276,
    # rounded half-up to the cent, while line 23 still uses lines 68370 and 68380.
    worksheet = return_ca(split_income_non_business_from_foreign_sources="30000")

    assert worksheet.get(SPLIT_INCOME_LINE_23).value == D("10475.63")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_49).value == D("1143.28")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("9086.25")


def test_all_the_split_income_from_foreign_sources_takes_the_whole_credit() -> None:
    # 68370 and 68380 both 40000: all the foreign income is split income from foreign sources, so
    # each share is 1 and line 23 is the whole federal foreign tax credit.
    worksheet = return_ca(
        split_income_from_foreign_sources="40000",
        total_income_from_foreign_sources="40000",
        split_income_non_business_from_foreign_sources="40000",
        total_non_business_income_from_foreign_sources="40000",
    )

    assert worksheet.get(SPLIT_INCOME_LINE_23).value == D("13094.54")
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("2862.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_49).value == D("1905.46")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("8324.07")


def test_no_income_from_foreign_sources_gives_lines_23_and_49_of_zero() -> None:
    # With 0 on lines 68380 (total income from foreign sources) the shares are 0: the whole of
    # line 22 and of line 47 stands, as in Return AL, although the credits themselves are not 0.
    worksheet = return_ca(
        split_income_from_foreign_sources="0",
        total_income_from_foreign_sources="0",
        split_income_non_business_from_foreign_sources="0",
        total_non_business_income_from_foreign_sources="0",
    )

    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("13094.54")
    assert worksheet.get(SPLIT_INCOME_LINE_23).value == D("0.00")
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("15956.54")
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("1905.46")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_49).value == D("0.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("10229.53")


def test_line_24_is_not_below_zero_and_line_50_may_be() -> None:
    # 200000 of employment income and 1000 of other income that is all split income from foreign
    # sources, with 50000 of foreign income in all: line 8 is 330.00, so line 22 is 330.00; the
    # credit (10878.83) is all of it for line 23, so line 24 is 330.00 - 10878.83, entered as 0
    # ("if negative, enter "0""). Line 50 prints no floor: 205.30 - 4121.17 = -3915.87.
    worksheet = compute(
        "200000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="1000",
        foreign_investment_income="49000",
        foreign_tax_countries_rows=(("15000", "50000"),),
        other_split_income="1000",
        split_income_from_foreign_sources="1000",
        total_income_from_foreign_sources="1000",
        split_income_non_business_from_foreign_sources="1000",
        total_non_business_income_from_foreign_sources="1000",
    )

    assert worksheet.get(SPLIT_INCOME_LINE_22).value == D("330.00")
    assert worksheet.get(SPLIT_INCOME_LINE_23).value == D("10878.83")
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("0")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_47).value == D("205.30")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_49).value == D("4121.17")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("-3915.87")


def test_the_trace_records_lines_23_and_24_and_lines_49_and_50() -> None:
    trace = return_ca().trace

    assert (
        RatioAppliedLine(
            SPLIT_INCOME_LINE_23,
            FEDERAL_FOREIGN_TAX_CREDIT,
            D("13094.54"),
            SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
            D("40000"),
            TOTAL_INCOME_FROM_FOREIGN_SOURCES,
            D("50000"),
            CENT,
            D("10475.63"),
        )
        in trace
    )
    assert (
        SubtractedNotBelowZeroLine(
            output=SPLIT_INCOME_LINE_24,
            minuend=SPLIT_INCOME_LINE_22,
            minuend_amount=D("15956.54"),
            subtrahend=SPLIT_INCOME_LINE_23,
            subtrahend_amount=D("10475.63"),
            result=D("5480.91"),
        )
        in trace
    )
    assert (
        RatioAppliedLine(
            ontario.SPLIT_INCOME_LINE_49,
            ontario.PROVINCIAL_FOREIGN_TAX_CREDIT,
            D("1905.46"),
            SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED,
            D("40000"),
            TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
            D("50000"),
            CENT,
            D("1524.37"),
        )
        in trace
    )
    assert (
        SubtractedLine(
            output=ontario.SPLIT_INCOME_LINE_50,
            minuend=ontario.SPLIT_INCOME_LINE_47,
            minuend_amount=D("10229.53"),
            subtrahend=ontario.SPLIT_INCOME_LINE_49,
            subtrahend_amount=D("1524.37"),
            result=D("8705.16"),
        )
        in trace
    )


def test_the_english_trace_reads_lines_23_and_24_and_lines_49_and_50() -> None:
    rendered = EnglishTraceRenderer().render_all(return_ca().trace)

    for line in (
        "split_income_line_23: federal_foreign_tax_credit 13094.54 "
        "× split_income_from_foreign_sources_checked 40000 "
        "/ total_income_from_foreign_sources 50000 "
        "(half-up to 0.01)",
        "split_income_line_24: split_income_line_22 15956.54 less split_income_line_23 10475.63, "
        "not below 0 = 5480.91",
        "split_income_line_49: provincial_foreign_tax_credit 1905.46 "
        "× split_income_non_business_from_foreign_sources_checked 40000 "
        "/ total_non_business_income_from_foreign_sources_checked 50000 (half-up to 0.01)",
        "split_income_line_50: split_income_line_47 10229.53 less split_income_line_49 1524.37 "
        "= 8705.16",
    ):
        assert line in rendered, line


def test_68370_above_line_3_is_refused_not_capped() -> None:
    # Line 3 is 40000, so 68370 of 99999 is refused, not capped at 40000; 68380 of 99999 is the
    # same figure, which nothing else on the return bounds.
    message = (
        "ca/split_income_from_foreign_sources 99999 is above ca/other_split_income_total 40000.00"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(
            split_income_from_foreign_sources="99999",
            total_income_from_foreign_sources="99999",
        )


def test_68370_above_68380_is_refused_not_capped() -> None:
    # 68370 of 60000 is above 68380 of 50000, so the line 23 share would be more than 1. Line 3 is
    # raised to 60000 so that 68370 passes its check against line 3; at line 3 of 40000 the first
    # check refuses it instead.
    message = (
        "ca/split_income_from_foreign_sources_part_of_line_3 60000 is above "
        "ca/total_income_from_foreign_sources 50000"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(
            other_split_income="60000",
            split_income_from_foreign_sources="60000",
        )


def test_line_49_non_business_part_above_68370_is_refused_not_capped() -> None:
    # The non-business part of 68370 is at most the checked 68370 that line 23 reads (40000), so
    # 45000 is refused, not capped at 40000.
    message = (
        "ca/split_income_non_business_from_foreign_sources 45000 is above "
        "ca/split_income_from_foreign_sources_checked 40000"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(split_income_non_business_from_foreign_sources="45000")


def test_line_49_non_business_total_above_68380_is_refused_not_capped() -> None:
    # The non-business total is at most 68380 (50000), so 60000 is refused, not capped.
    message = (
        "ca/total_non_business_income_from_foreign_sources 60000 is above "
        "ca/total_income_from_foreign_sources 50000"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(total_non_business_income_from_foreign_sources="60000")


def test_line_49_non_business_part_above_its_total_is_refused_not_capped() -> None:
    # The non-business part of 68370 (40000) is at most the checked non-business total (10000), so
    # it is refused, not capped at 10000.
    message = (
        "ca/split_income_non_business_from_foreign_sources_part_of_68370 40000 is above "
        "ca/total_non_business_income_from_foreign_sources_checked 10000"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(total_non_business_income_from_foreign_sources="10000")


def test_equal_split_income_from_foreign_sources_amounts_are_accepted() -> None:
    # Equal is accepted: 68370 of 40000 is at most line 3 of 40000 and 68380 of 50000, and the
    # non-business parts are at most their checked bounds at 40000 and 50000, so Return CA is
    # unchanged.
    worksheet = return_ca()

    assert worksheet.get(SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3).value == D("40000")
    assert worksheet.get(SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED).value == D("40000")
    assert worksheet.get(SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370).value == D(
        "40000"
    )
    assert worksheet.get(SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED).value == D("40000")
    assert worksheet.get(TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED).value == D("50000")
    assert worksheet.get(TOTAL_PAYABLE).value == D("14786.07")


def test_line_2_above_line_1_is_refused_not_capped() -> None:
    # T1206 line 2 is "included on line 1": 20000 against line 1 of 11500 is an input error.
    message = (
        "ca/split_income_dividends_other_than_eligible_total 20000.00 is above "
        "ca/split_income_dividends_checked 11500"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(split_income_dividends_other_than_eligible="20000")


def test_line_1_above_the_taxable_dividends_is_refused_not_capped() -> None:
    # T1206 line 1 is part of the dividends on T1 lines 12000 and 12010, 11500 on Return CA, so
    # 99999 is refused (line 2 stays at 11500, which is at most line 1).
    message = "ca/split_income_dividends_total 99999.00 is above ca/taxable_dividends 11500.00"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(split_income_dividends="99999")


def test_line_2_above_the_taxable_dividends_other_than_eligible_is_refused_not_capped() -> None:
    # T1 line 12010 is 11500 on Return CA. Eligible dividends of 10000 make line 12000 larger, so
    # line 1 of 20000 is at most it and line 2 of 15000 is at most line 1: only line 2 is above
    # line 12010, and it is refused, not capped.
    message = (
        "ca/split_income_dividends_other_than_eligible_part_of_line_1 15000.00 is above "
        "ca/taxable_dividends_other_than_eligible 11500.00"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(
            eligible_dividends_received_without_a_slip="10000",
            split_income_dividends="20000",
            split_income_dividends_other_than_eligible="15000",
        )


def test_split_income_dividends_equal_to_the_t1_amounts_are_accepted() -> None:
    # Equal is accepted: line 1 of 11500 is at most line 12000 of 11500, and line 2 of 11500 is at
    # most line 1 and line 12010, so each checked amount is 11500 and Return CA is unchanged.
    worksheet = return_ca()

    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_CHECKED).value == D("11500")
    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1).value == D(
        "11500"
    )
    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED).value == D("11500")


# Line 3 "All other split income (see "Split income" on page 1)" is part of the total income, so it
# is at most the income before losses (the T1 income lines, a loss counted as 0), the whole it
# comes out of
# (`ca/other_split_income_checked`, `core/at_most`). The printed Form T1206 gives no limit on line
# 3, so the part-over-whole default applies. Return CA's total income is 61500.00 (its 11500 of
# split dividends, 40000 of other income and 10000 of other dividends, all in total income).
TOTAL_INCOME_BOUND = "ca/income_before_losses 61500.00"


def test_other_split_income_above_the_total_income_is_refused_not_capped() -> None:
    # Line 3 of 99999 is above the 61500.00 of total income, so it is refused, not capped at 61500.
    # Its foreign-source part (40000) still passes its own check against line 3.
    message = "ca/other_split_income 99999 is above " + TOTAL_INCOME_BOUND

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ca(other_split_income="99999")


def test_other_split_income_equal_to_the_total_income_is_accepted() -> None:
    # At most the bound: 61500 against 61500.00 is accepted and produced as entered.
    worksheet = return_ca(other_split_income="61500")

    assert worksheet.get(TOTAL_INCOME).value == D("61500.00")
    assert worksheet.get(OTHER_SPLIT_INCOME_CHECKED).value == D("61500")


def test_a_zero_other_split_income_is_accepted_with_no_other_split_income() -> None:
    # Zero is at most any bound: with no split income of line 3 the checked amount is 0.
    worksheet = compute("60000", (), "0", "0", "0", "0", "0")

    assert worksheet.get(OTHER_SPLIT_INCOME).value == D("0")
    assert worksheet.get(OTHER_SPLIT_INCOME_CHECKED).value == D("0")


# A business loss larger than the other income makes total income negative, but the income before
# losses counts the loss as 0, so the bound is the other income and line 3 is not refused for the
# loss. Employment income of 20000 with a business loss of 50000 (a T2125 net of -50000) gives a
# total income of -30000.00 and an income before losses of 20000.00.
def return_with_a_loss(**overrides: Any) -> Worksheet:
    return compute(
        "20000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("-50000", 1),),
        **overrides,
    )


def test_a_zero_other_split_income_is_accepted_when_a_loss_makes_total_income_negative() -> None:
    worksheet = return_with_a_loss(other_split_income="0")

    assert worksheet.get(TOTAL_INCOME).value == D("-30000.00")
    assert worksheet.get(OTHER_SPLIT_INCOME_CHECKED).value == D("0")


def test_other_split_income_is_accepted_when_a_loss_makes_total_income_negative() -> None:
    worksheet = return_with_a_loss(other_split_income="1000")

    assert worksheet.get(TOTAL_INCOME).value == D("-30000.00")
    assert worksheet.get(OTHER_SPLIT_INCOME_CHECKED).value == D("1000")


def test_other_split_income_above_the_income_before_losses_is_refused_with_a_loss() -> None:
    message = "ca/other_split_income 20000.01 is above ca/income_before_losses 20000.00"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_with_a_loss(other_split_income="20000.01")
