"""CA-ON 2025 end to end: return k ontario dividends."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.jurisdictions.ca.catalog import (
    DIVIDEND_TAX_CREDIT,
    DIVIDENDS_AMOUNT_A,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_SURTAX,
    ONTARIO_TAX_AFTER_REDUCTION,
    ONTARIO_TAX_REDUCTION,
    ONTARIO_TAX_WITH_SURTAX,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, return_k


def test_return_ks_ontario_dividend_tax_credit_uses_the_whole_lines_12000_and_12010() -> None:
    # Worksheet ON428's "Line 61520" has no Note 1: line A is the whole line 12000, 2455.00, and
    # line B the whole line 12010, 775.00 (the federal lines A and B, 1955.00 and 575.00, count
    # the no-slip dividends only). Line 1 is 775.00 x 2.9863% = 23.143825, 23.14; line C is
    # 2455.00 - 775.00 = 1680.00; line 2 is 1680.00 x 10% = 168.00; line 3, and so line 61520
    # and ON428 line 57, is 23.14 + 168.00 = 191.14. The slip credit of 60.00 is the federal
    # credit's and is not read.
    worksheet = return_k()

    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A).value == D("2455.00")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_B).value == D("775.00")
    assert worksheet.get(ontario.OTHER_DIVIDENDS_CREDIT).value == D("23.14")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A_LESS_B).value == D("1680.00")
    assert worksheet.get(ontario.ELIGIBLE_DIVIDENDS_CREDIT).value == D("168.00")
    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("191.14")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    for line in (
        "dividends_amount_a: taxable_dividends 2455 = 2455",
        "dividends_amount_b: taxable_dividends_other_than_eligible 775 = 775",
        "other_dividends_credit: 2.9863% of dividends_amount_b 775 (half-up to 0.01)",
        "dividends_amount_a_less_b: dividends_amount_a 2455 less dividends_amount_b 775 = 1680",
        "eligible_dividends_credit: 10% of dividends_amount_a_less_b 1680 (half-up to 0.01)",
        "dividend_tax_credit: other_dividends_credit 23.14 + eligible_dividends_credit 168 "
        "= 191.14",
    ):
        assert line in rendered, line


def test_the_ontario_dividend_tax_credit_comes_off_the_tax_at_lines_58_and_71() -> None:
    # ON428 line 56 is line 53, 1824.13, and line 58 "Line 56 minus line 57" is 1824.13 -
    # 191.14 = 1632.99. Line 69 is 1824.13 (no surtax below 5710) and line 70 is line 57,
    # 191.14, so line 71 "Line 69 minus line 70" is 1632.99, as is line 73. Twice the reduction
    # amounts, 588.00, is below it, so line 80 is 0 and line 81 is 1632.99; the lift credit
    # (line 85) is 0; the health premium of 600.00 is added: line 90, the Ontario tax, is
    # 2232.99.
    worksheet = return_k()

    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_DIVIDEND_CREDIT).value == D("1824.13")
    assert worksheet.get(ontario.ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("1632.99")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SURTAX).value == D("1824.13")
    assert worksheet.get(ontario.DIVIDEND_CREDIT_FROM_LINE_57).value == D("191.14")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("1632.99")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_REDUCTION).value == D("1632.99")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("1632.99")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("2232.99")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    for line in (
        "ontario_tax_before_dividend_credit: ontario_tax_after_credits 1824.13 = 1824.13",
        "ontario_tax_less_dividend_credit: ontario_tax_before_dividend_credit 1824.13 "
        "less dividend_tax_credit 191.14, not below 0 = 1632.99",
        "dividend_credit_from_line_57: dividend_tax_credit 191.14 = 191.14",
        "ontario_tax_after_dividend_credit: ontario_tax_with_surtax 1824.13 "
        "less dividend_credit_from_line_57 191.14, not below 0 = 1632.99",
        "ontario_tax_after_reduction: ontario_tax_before_reduction 1632.99 "
        "less ontario_tax_reduction 0, not below 0 = 1632.99",
    ):
        assert line in rendered, line


def test_dividends_received_with_no_slip_give_the_ontario_credit_of_155_17() -> None:
    # The worked example of the Worksheet: eligible dividends received 1000 and dividends other
    # than eligible 500, no slips. Line 13 is 1380.00 and line 16 575.00, so line 12000 is
    # 1955.00 and line 12010 575.00. Ontario line B is 575.00 x 2.9863% = 17.171225, 17.17;
    # line C is 1955.00 - 575.00 = 1380.00 and line 2 is 1380.00 x 10% = 138.00; line 3 is
    # 17.17 + 138.00 = 155.17.
    worksheet = compute(
        "50000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_dividends_received_without_a_slip="1000",
        other_dividends_received_without_a_slip="500",
    )

    assert worksheet.get(TAXABLE_DIVIDENDS).value == D("1955.00")
    assert worksheet.get(TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE).value == D("575.00")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A).value == D("1955.00")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_B).value == D("575.00")
    assert worksheet.get(ontario.OTHER_DIVIDENDS_CREDIT).value == D("17.17")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A_LESS_B).value == D("1380.00")
    assert worksheet.get(ontario.ELIGIBLE_DIVIDENDS_CREDIT).value == D("138.00")
    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("155.17")
    assert worksheet.get(DIVIDEND_TAX_CREDIT).value == D("259.19")


def test_dividends_on_slips_alone_are_the_whole_ontario_lines_a_and_b() -> None:
    # Slip amounts of 800 (T5 boxes 11 and 25) and 300 (box 11) are lines 12000 and 12010, and
    # the Ontario worksheet reads both whole (the federal lines A and B are 0 here): line 1 is
    # 300 x 2.9863% = 8.9589, 8.96; line C is 800 - 300 = 500; line 2 is 500 x 10% = 50.00; line
    # 3 is 58.96.
    worksheet = compute(
        "50000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t5_taxable_dividends_other_than_eligible="300",
        t5_taxable_dividends="800",
        t5_dividend_tax_credit="70.00",
    )

    assert worksheet.get(DIVIDENDS_AMOUNT_A).value == D("0")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A).value == D("800")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_B).value == D("300")
    assert worksheet.get(ontario.OTHER_DIVIDENDS_CREDIT).value == D("8.96")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A_LESS_B).value == D("500")
    assert worksheet.get(ontario.ELIGIBLE_DIVIDENDS_CREDIT).value == D("50.00")
    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("58.96")


def test_slip_credits_alone_give_no_ontario_dividend_tax_credit() -> None:
    # The Ontario credit is computed from lines 12000 and 12010, not taken from the slips'
    # credit boxes: with no dividends the federal line 40425 is the slip credit of 100.00 and
    # ON428 line 57 is 0.
    worksheet = compute("50000", (), "0", "0", "0", "0", "0", t5_dividend_tax_credit="100.00")

    assert worksheet.get(DIVIDEND_TAX_CREDIT).value == D("100.00")
    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == (
        worksheet.get(ONTARIO_TAX_WITH_SURTAX).value
    )


def test_the_dividend_credit_is_taken_off_line_69_after_the_surtax() -> None:
    # Line 70 comes off line 69, the tax plus the surtax (line 68), and the surtax is still
    # computed on line 65 before it: line 71 is line 69 less the credit.
    worksheet = compute("100000", (), "0", "0", "0", "0", "0", t5_taxable_dividends="100000")

    credit = worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value
    assert credit == D("10000.00")
    assert worksheet.get(ONTARIO_SURTAX).value > D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == (
        worksheet.get(ONTARIO_TAX_WITH_SURTAX).value - credit
    )


def test_the_ontario_tax_reduction_is_set_against_line_71_not_line_69() -> None:
    # Employment income of 26000 and a T5 slip with boxes 11 and 25 of 1000 (box 11 0): line 12000
    # is 1000 and line 12010 is 0, so line 1 is 0, line C is 1000.00 and line 2 is 100.00, line
    # 57 being 100.00. Line 69 is 630.64, above twice the reduction amounts, 588.00; line 71,
    # and so line 73, is 630.64 - 100.00 = 530.64, so line 80 "Line 78 minus line 79" is 588.00
    # - 530.64 = 57.36 and line 81 is 530.64 - 57.36 = 473.28.
    worksheet = compute("26000", (), "0", "0", "0", "0", "0", t5_taxable_dividends="1000")

    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("100.00")
    assert worksheet.get(ONTARIO_TAX_WITH_SURTAX).value == D("630.64")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("530.64")
    assert worksheet.get(ONTARIO_TAX_REDUCTION).value == D("57.36")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("473.28")


def test_an_ontario_dividend_credit_above_the_tax_leaves_zero_not_a_negative() -> None:
    # Employment income of 20000 and slip dividends of 20000: the credit (line 57) is 2000.00,
    # above the Ontario tax of 1310.14, so lines 58 and 71 are "0" (if negative, enter "0").
    worksheet = compute("20000", (), "0", "0", "0", "0", "0", t5_taxable_dividends="20000")

    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("2000.00")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_DIVIDEND_CREDIT).value == D("1310.14")
    assert worksheet.get(ontario.ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("0")
