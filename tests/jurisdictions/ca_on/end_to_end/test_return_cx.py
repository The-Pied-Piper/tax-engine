"""CA-ON 2025 end to end: return cx."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_FEDERAL_SURTAX,
    AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX,
    DIVIDEND_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
    FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_SURTAX_OUTSIDE_CANADA,
    FEDERAL_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    FEDERAL_TAX_WITH_SURTAX,
    FOREIGN_SURTAX_ALLOCATED_TOTAL_CHECKED,
    FOREIGN_SURTAX_LIMIT,
    FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
    ITC_RECAPTURE,
    SPLIT_INCOME_LINE_22,
    T2203_FEDERAL_SURTAX_OUTSIDE_CANADA,
    T2203_HAS_TAX_ON_SPLIT_INCOME,
    T2203_LINE_5,
    T2203_LINE_6,
    T2203_LINE_8,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_cx(**overrides: Any) -> Worksheet:
    """Return CX's inputs, as in `returns/2025_return_cx.yaml`, over the keyword overrides given.

    A filer with 40000 of other income and no employment income, with 40000 of net foreign
    business income (equal to net income, so not reduced), 3600 of business income tax paid to
    one country and the surtax on income allocated to "Other (Outside Canada)" of 415.35, the
    amount of Form T2203 line 10 at 25 per cent. The filer is not subject to minimum tax.
    """
    inputs: dict[str, Any] = {
        "other_income": "40000",
        "amt_t2203_column_5_percentage": "25",
        "foreign_tax_countries_rows": (("0", "0", "3600", "0", "40000", "415.35"),),
    }
    inputs.update(overrides)
    return compute("0", (), "0", "0", "0", "0", "0", **inputs)


def test_t2203_part_2_takes_the_basic_federal_tax_and_applies_the_percentage_and_the_rate() -> None:
    worksheet = return_cx()

    # Line 5 is "0" (no tax on split income), so line 6 is the basic federal tax of 3461.29. Line 8
    # is 3461.29 x 25% = 865.3225, rounded half-up to 865.32, and line 10 is 865.32 x 48% =
    # 415.3536, rounded half-up to 415.35.
    assert worksheet.get(T2203_HAS_TAX_ON_SPLIT_INCOME).value == 0
    assert worksheet.get(T2203_LINE_5).value == D("0")
    assert worksheet.get(T2203_LINE_6).value == D("3461.29")
    assert worksheet.get(T2203_LINE_8).value == D("865.32")
    assert worksheet.get(T2203_FEDERAL_SURTAX_OUTSIDE_CANADA).value == D("415.35")


def test_t1_line_127_is_t2203_line_10_when_not_subject_to_minimum_tax() -> None:
    worksheet = return_cx()

    # T1 line 127 is line 10 of Part 2 of Form T2203, 415.35. T1 line 128 "Line 126 plus line 127 ="
    # is 3461.29 + 415.35 = 3876.64.
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3461.29")
    assert worksheet.get(FEDERAL_SURTAX_OUTSIDE_CANADA).value == D("415.35")
    assert worksheet.get(FEDERAL_TAX_WITH_SURTAX).value == D("3876.64")


def test_the_credit_is_within_line_42900_plus_line_127_so_it_is_not_cut_to_line_42900() -> None:
    worksheet = return_cx()

    # The credit before the limit is 3600.00, the business tax paid. The limit is line 42900 plus
    # line 127, 3461.29 + 415.35 = 3876.64, so 3600.00 stands and is not cut to 3461.29. T1 line 130
    # "Line 128 minus line 129 =" is 3876.64 - 3600.00 = 276.64.
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT).value == D("3600.00")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("3600.00")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("276.64")


def test_the_credit_is_capped_at_line_42900_plus_line_127_when_it_is_above_that() -> None:
    worksheet = return_cx(foreign_tax_countries_rows=(("0", "0", "4000", "0", "40000", "415.35"),))

    # Business tax paid of 4000.00 is more than 3876.64, so the credit is 3876.64 and T1 line 130 is
    # 0.00.
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("3876.64")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("0.00")


def test_subject_to_minimum_tax_takes_the_t691_surtax_for_t1_line_127() -> None:
    worksheet = return_cx(amt_subject_to_minimum_tax=1)

    # Subject to minimum tax, Form T2203 Part 2 is not completed and T1 line 127 is Form T691 Part 3
    # line 4: 48% of 3461.29 is 1661.42, times 25% is 415.355, rounded half-up to 415.36. Line 128
    # is 3461.29 + 415.36 = 3876.65 and line 130 is 3876.65 - 3600.00 = 276.65.
    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("415.36")
    assert worksheet.get(FEDERAL_SURTAX_OUTSIDE_CANADA).value == D("415.36")
    assert worksheet.get(FEDERAL_TAX_WITH_SURTAX).value == D("3876.65")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("276.65")


def test_a_negative_surtax_with_no_positive_line_128_gives_no_credit_and_no_crash() -> None:
    worksheet = return_cx(
        other_income="10000",
        amt_subject_to_minimum_tax=1,
        foreign_tax_countries_rows=(("0", "0", "500", "0", "10000", "0"),),
    )

    # Subject to minimum tax, T1 line 127 is Form T691 Part 3 line 4, which prints no floor and is
    # negative here (-106.65). Line 126 is 0 on 10000 of income (below the basic personal amount),
    # so line 128 is -106.65, not positive. The limit on T2209 line 13 is then 0, not a negative
    # credit, and T1 line 130 "Line 128 minus line 129" prints no "(if negative, enter "0")": the
    # plain difference, -106.65 - 0.00 = -106.65.
    # Form T2209 note (4), basic federal tax with the surtax, is the plain sum, 0 plus -106.65 =
    # -106.65 (the surtax prints no floor). Less the First Nations abatement, 0, it is -106.65, and
    # the abatement step is not below zero: 0.00.
    assert worksheet.get(BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX).value == D("-106.65")
    assert worksheet.get(FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX).value == D("0.00")
    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("-106.65")
    assert worksheet.get(FEDERAL_SURTAX_OUTSIDE_CANADA).value == D("-106.65")
    assert worksheet.get(FEDERAL_TAX_WITH_SURTAX).value == D("-106.65")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("0.00")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("-106.65")


def test_a_negative_line_130_takes_the_itc_recapture_off_before_line_134() -> None:
    worksheet = return_cx(
        other_income="10000",
        amt_subject_to_minimum_tax=1,
        foreign_tax_countries_rows=(("0", "0", "500", "0", "10000", "0"),),
        itc_recapture_expenditure_at_15_percent="1000",
    )

    # Line 130 is -106.65 as above. Line 131 is 15% of 1000 = 150.00. Line 132 "Line 130 plus line
    # 131" prints no "(if negative, enter "0")": -106.65 + 150.00 = 43.35, which line 134 carries
    # (it floors only a negative). With line 130 floored to 0 line 132 would be 150.00, not 43.35.
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("-106.65")
    assert worksheet.get(ITC_RECAPTURE).value == D("150.00")
    assert worksheet.get(FEDERAL_TAX_WITH_ITC_RECAPTURE).value == D("43.35")
    assert worksheet.get(FEDERAL_TAX).value == D("43.35")


def test_a_negative_line_127_allows_no_part_of_it_to_be_allocated_to_a_country() -> None:
    # Line 127 is -106.65 (Form T691 Part 3 line 4 prints no floor): no surtax to allocate. The
    # limit on the allocated parts is 0, so 0 is accepted and 0.01 is refused.
    worksheet = return_cx(
        other_income="10000",
        amt_subject_to_minimum_tax=1,
        foreign_tax_countries_rows=(("0", "0", "500", "0", "10000", "0"),),
    )
    assert worksheet.get(FOREIGN_SURTAX_LIMIT).value == D("0")
    assert worksheet.get(FOREIGN_SURTAX_ALLOCATED_TOTAL_CHECKED).value == D("0")

    with pytest.raises(InputAboveBoundError, match="foreign_surtax_allocated_total 0.01"):
        return_cx(
            other_income="10000",
            amt_subject_to_minimum_tax=1,
            foreign_tax_countries_rows=(("0", "0", "500", "0", "10000", "0.01"),),
        )


def test_a_negative_surtax_past_the_dividend_credit_does_not_make_the_abatement_base_negative() -> (
    None
):
    worksheet = return_cx(
        other_income="0",
        other_dividends_received_without_a_slip="2000",
        amt_subject_to_minimum_tax=1,
        amt_t2203_column_5_percentage="100",
        first_nations_abatement="1",
        foreign_tax_countries_rows=(),
    )

    # Other dividends of 2000 are grossed up 15% to 2300, which is the taxable income. Form T691
    # Part 2 line 1 (line 40400) is 14.5% x 2300 = 333.50. Line 2 is the non-refundable credits,
    # 2338.71 (the basic personal amount, 16129 x 14.5% = 2338.705, rounded half-up), and line 3
    # is the dividend tax credit (line 40425): 2300 x 9.0301% = 207.69. Line 7, the basic federal
    # tax, is 333.50 - 2338.71 - 207.69 = -2212.90, unfloored, so T1 line 126 (line 42900) is 0.00
    # and T691
    # Part 3 line 4 is 48% x -2212.90 = -1062.19 at 100%. T1 line 127 is -1062.19. Note (4) is
    # line 42900 plus the dividend tax credit (207.69) plus line 127: 207.69 - 1062.19 = -854.50
    # (the plain sum, not floored), and less the First Nations abatement of 1.00 it is -855.50,
    # which is held at 0.00, so the basic tax for the foreign tax credit is 0.00 and not a
    # negative amount. T1 line 128 is 0.00 + -1062.19 = -1062.19, so the limit on T2209 line 13 is
    # 0.00, and the credit is 0.00, so T1 line 130 (no floor printed) is -1062.19 - 0.00 =
    # -1062.19.
    assert worksheet.get(DIVIDEND_TAX_CREDIT).value == D("207.69")
    assert worksheet.get(BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT).value == D("207.69")
    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("-1062.19")
    assert worksheet.get(BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX).value == D("-854.50")
    assert worksheet.get(FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX).value == D("0.00")
    assert worksheet.get(FEDERAL_TAX_WITH_SURTAX).value == D("-1062.19")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("0.00")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("-1062.19")


def test_a_first_nations_abatement_larger_than_the_basic_tax_gives_0_not_a_negative_base() -> None:
    worksheet = return_cx(
        other_income="0", first_nations_abatement="50", foreign_tax_countries_rows=()
    )

    # No income: the basic federal tax (line 42900) is 0, no dividend credit, no surtax (no minimum
    # tax, and the percentage on line 7 of Form T2203 gives 0). The sum is 0 and the abatement of 50
    # is more than it, so the basic federal tax for the foreign tax credit is 0.00, not -50.00.
    assert worksheet.get(BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX).value == D("0.00")
    assert worksheet.get(FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX).value == D("0.00")


def test_the_non_business_credit_is_not_cut_to_basic_federal_tax_without_the_surtax() -> None:
    worksheet = return_cx(foreign_tax_countries_rows=(("3800", "40000", "0", "0", "0", "415.35"),))

    # Form T2209 note (4), basic federal tax, takes the surtax on income allocated to "Other
    # (Outside Canada)" as well as line 42900 and the dividend credit: 3461.29 + 415.35 = 3876.64.
    # Line 2 of the non-business sheet is 40000 / 40000 x 3876.64 = 3876.64, and line 3 is the
    # lesser of 3800.00 (line 1, the non-business tax) and 3876.64, so 3800.00. The business lines
    # are note (8) and have no non-business tax here, so the credit is 3800.00 and is within line
    # 128 (3876.64), leaving 76.64 on T1 line 130.
    assert worksheet.get(FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX).value == D("3876.64")
    assert worksheet.get(FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT).value == D("3800.00")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("3800.00")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("76.64")


def test_the_split_income_branch_takes_line_22_of_form_t1206_when_it_is_more_than_line_42900() -> (
    None
):
    worksheet = return_cx(other_split_income="40000")

    # Split income of 40000 (T1206 line 7) is taxed at 33% on T1206 line 8: 13200.00. Line 22 is
    # line 15 less line 21, with no disability amounts (line 9 is line 41500, the advanced Canada
    # workers benefit, 0) and no dividend credit on split income, so line 22 is 13200.00. T2203
    # line 5 is line 22 times a count of 1 (there is tax on split income): 13200.00, which is more
    # than line 4, so line 6 is 13200.00. Line 8 is 13200.00 x 25% = 3300.00 and line 10 is
    # 3300.00 x 48% = 1584.00, so T1 line 127 is 1584.00. Basic federal tax, T1 line 126, is
    # 10861.29 as this engine computes it on this return (not confirmed against T1 lines 119 to
    # 125 for a return with split income), so line 128 is 10861.29 + 1584.00 = 12445.29. The
    # credit is 3600.00 (line 13 limit 12445.29), and line 130 is 12445.29 - 3600.00 = 8845.29.
    assert worksheet.get(SPLIT_INCOME_LINE_22).value == D("13200.00")
    assert worksheet.get(T2203_LINE_5).value == D("13200.00")
    assert worksheet.get(T2203_LINE_6).value == D("13200.00")
    assert worksheet.get(T2203_LINE_8).value == D("3300.00")
    assert worksheet.get(T2203_FEDERAL_SURTAX_OUTSIDE_CANADA).value == D("1584.00")
    assert worksheet.get(FEDERAL_SURTAX_OUTSIDE_CANADA).value == D("1584.00")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("10861.29")
    assert worksheet.get(FEDERAL_TAX_WITH_SURTAX).value == D("12445.29")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("3600.00")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("8845.29")


@pytest.mark.parametrize(
    ("percentage", "line_8"),
    [
        # 0 per cent of the basic federal tax of 3461.29 is 0.
        ("0", "0"),
        # 100 per cent is the whole of it, so line 8 is the basic federal tax of 3461.29.
        ("100", "3461.29"),
    ],
)
def test_a_column_5_percentage_of_0_or_100_is_accepted_and_checked_as_entered(
    percentage: str, line_8: str
) -> None:
    # The form prints no maximum on the percentage in Column 5 of line 52220: 100 is a choice.
    # No part of the surtax is allocated to the country: at 0 per cent line 127 is 0.
    worksheet = return_cx(
        amt_t2203_column_5_percentage=percentage,
        foreign_tax_countries_rows=(("0", "0", "3600", "0", "40000", "0"),),
    )

    assert worksheet.get(AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED).value == D(percentage)
    assert worksheet.get(T2203_LINE_8).value == D(line_8)


@pytest.mark.parametrize("percentage", ["100.01", "250"])
def test_a_column_5_percentage_above_100_is_an_input_error_not_a_cap(percentage: str) -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        return_cx(amt_t2203_column_5_percentage=percentage)

    assert str(raised.value) == (
        "ca-on/return, instance 1: ca/amt_t2203_column_5_percentage "
        f"{percentage} is above ca/amt_t2203_column_5_percentage_maximum 100.00"
    )
