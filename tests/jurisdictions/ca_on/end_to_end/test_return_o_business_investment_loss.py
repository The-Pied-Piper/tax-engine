"""CA-ON 2025 end to end: return o business investment loss."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    ALLOWABLE_BUSINESS_INVESTMENT_LOSS,
    BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION,
    BUSINESS_INVESTMENT_LOSS_REDUCTION,
    BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE,
    CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1986_TO_2024,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, step_3


def _kind(identifier: str) -> ArtifactKind[Decimal]:
    """A T1436 kind by its identifier, looked up when a test runs, so that the module loads before
    the lines 1 to 6 and their inputs are declared as catalog kinds."""
    return ArtifactRegistry.shared().kind(identifier)


@pytest.mark.parametrize(
    ("amount_2001_to_2024", "other_reductions", "line_15", "line_17", "line_18", "line_20"),
    [
        # No capital gains deduction in earlier years: the whole loss of 10000 is reduced by
        # nothing, and 50% of it is deductible.
        ("0", "0", "0", "0", "10000", "5000.00"),
        # The line 254 total for 2001 to 2024 is 2000; line 6 prints it x 2 as 4000, so line 17 is
        # 4000 and line 21700 is 3000.00.
        ("2000", "0", "4000", "4000", "6000", "3000.00"),
        # Line 6 is 3000 x 2 = 6000 and line 14 is 2000 (the 2024 amounts of Schedule 3): line 15 is
        # 4000.
        ("3000", "2000", "4000", "4000", "6000", "3000.00"),
        # Line 15 above the loss: line 17 is the loss itself, so nothing is left to deduct.
        ("6000", "0", "12000", "10000", "0", "0.00"),
        # Line 15 equal to the loss.
        ("5000", "0", "10000", "10000", "0", "0.00"),
    ],
)
def test_the_business_investment_loss_is_reduced_by_the_earlier_gains_deductions_then_halved(
    amount_2001_to_2024: str,
    other_reductions: str,
    line_15: str,
    line_17: str,
    line_18: str,
    line_20: str,
) -> None:
    # Form T1436 line 21700: line 15 "Line 7 minus line 14"; line 16 the loss in 2025; line 17
    # "Enter whichever is less: amount from line 15 or line 16."; line 18 "Line 16 minus line
    # 17"; line 20 "Line 18 multiplied by the percentage on line 19" (50 %). The amount entered is
    # the line 254 total for 2001 to 2024, before line 6's "x 2".
    worksheet = step_3(
        capital_gains_deductions_2001_to_2024=amount_2001_to_2024,
        other_business_investment_loss_reductions_2024=other_reductions,
        business_investment_loss="10000",
    )

    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE).value == D(line_15)
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION).value == D(line_17)
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION).value == D(line_18)
    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D(line_20)
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D(line_20)


def test_a_line_15_of_4000_renders_the_reduction_lines_of_the_trace() -> None:
    # Line 15 of 4000 (line 6, the 2001 to 2024 amount of 2000 printed x 2) and a loss of 10000.
    worksheet = step_3(
        capital_gains_deductions_2001_to_2024="2000", business_investment_loss="10000"
    )

    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "business_investment_loss_reduction: lesser of "
        "business_investment_loss_reduction_available 4000 and business_investment_loss 10000 "
        "= 4000"
    ) in rendered
    assert (
        "business_investment_loss_after_reduction: business_investment_loss 10000 "
        "less business_investment_loss_reduction 4000 = 6000"
    ) in rendered
    assert (
        "allowable_business_investment_loss: 50% of business_investment_loss_after_reduction "
        "6000 (half-up to 0.01)"
    ) in rendered


def test_t1436_line_15_goes_negative_when_line_14_exceeds_line_7() -> None:
    # Form T1436 line 15 "Line 7 minus line 14" prints no "(if negative, enter "0")", and line 17
    # "Enter whichever is less: amount from line 15 or line 16." prints no floor either, so the
    # lines follow the form as printed: line 7 of 0 and line 14 of 2000 give line 15 of -2000,
    # line 17 of -2000 (the lesser of -2000 and 10000), line 18 of 10000 - (-2000) = 12000 and
    # line 21700 of 12000 x 50% = 6000.00, more than half of the loss of 10000. The form states
    # no treatment of this case, so this records the printed arithmetic, not a confirmed one.
    worksheet = step_3(
        other_business_investment_loss_reductions_2024="2000", business_investment_loss="10000"
    )

    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE).value == D("-2000")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION).value == D("-2000")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION).value == D("12000")
    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("6000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("6000.00")


def test_t1436_lines_7_and_14_add_lines_1_to_6_and_8_to_13_once_each() -> None:
    # Line 7 "Add lines 1 to 6." and line 14 "Add lines 8 to 13.": the six lines 1 to 6 are each
    # the amount entered times its printed multiplier, with Schedule 3 lines 543 and 544 at 500
    # (a sum of 500) and the inclusion rate for 2000 at 0.5. Line 1 is 100 x 2 = 200.00; line 2 is
    # (a) 600 - 500 = 100, x 1.5 = 150.00; line 3 is 800 - (a) 100 = 700, the lesser of 700 and 500,
    # x 1.3333 = 666.65; line 4 is 200 x 1.3333 = 266.66; line 5 is 300 x 1/0.5 = 600.00; line 6 is
    # 50 x 2 = 100.00. Their sum, line 7, is 1983.31. The lines 8 to 13 are 64, 128, 256, 512, 1024
    # and 2048, one distinct power of two each, so 4032 in all. Line 15, "Line 7 minus line 14",
    # is -2048.69: the form prints no "(if negative, enter "0")".
    worksheet = step_3(
        capital_gains_deductions_1985_to_1987="100",
        capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property="600",
        capital_gains_deductions_1988_and_1989_eligible_capital_property="800",
        capital_gains_deductions_1990_to_1999="200",
        capital_gains_deductions_2000="300",
        capital_gains_deductions_2001_to_2024="50",
        schedule_3_line_543="300",
        schedule_3_line_544="200",
        t657_inclusion_rate_2000="0.5",
        other_business_investment_loss_reductions_1986_to_1994="64",
        other_business_investment_loss_reductions_1994_to_1996="128",
        other_business_investment_loss_reductions_1997_to_1999="256",
        other_business_investment_loss_reductions_2000="512",
        other_business_investment_loss_reductions_2001_to_2023="1024",
        other_business_investment_loss_reductions_2024="2048",
    )

    assert worksheet.get(CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024).value == D("1983.31")
    assert worksheet.get(OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1986_TO_2024).value == D("4032")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE).value == D("-2048.69")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "capital_gains_deductions_claimed_1985_to_2024: capital_gains_deductions_line_1 200 "
        "+ capital_gains_deductions_line_2 150 + capital_gains_deductions_line_3 666.65 "
        "+ capital_gains_deductions_line_4 266.66 + capital_gains_deductions_line_5 600 "
        "+ capital_gains_deductions_line_6 100 = 1983.31"
    ) in rendered
    assert (
        "other_business_investment_loss_reductions_1986_to_2024: "
        "other_business_investment_loss_reductions_1986_to_1994 64 "
        "+ other_business_investment_loss_reductions_1994_to_1996 128 "
        "+ other_business_investment_loss_reductions_1997_to_1999 256 "
        "+ other_business_investment_loss_reductions_2000 512 "
        "+ other_business_investment_loss_reductions_2001_to_2023 1024 "
        "+ other_business_investment_loss_reductions_2024 2048 = 4032"
    ) in rendered
    assert (
        "business_investment_loss_reduction_available: "
        "capital_gains_deductions_claimed_1985_to_2024 1983.31 "
        "less other_business_investment_loss_reductions_1986_to_2024 4032 = -2048.69"
    ) in rendered


@pytest.mark.parametrize(
    ("amounts", "identifier", "printed"),
    [
        # Line 1, "For 1985 to 1987: ... x 2": 137 x 2.
        (
            {"capital_gains_deductions_1985_to_1987": "137"},
            "ca/capital_gains_deductions_line_1",
            "274.00",
        ),
        # Line 4, "For 1990 to 1999: ... x 1.3333": 137 x 1.3333 = 182.6621, to the cent 182.66.
        (
            {"capital_gains_deductions_1990_to_1999": "137"},
            "ca/capital_gains_deductions_line_4",
            "182.66",
        ),
        # Line 6, "For 2001 to 2024: ... x 2": 137 x 2.
        (
            {"capital_gains_deductions_2001_to_2024": "137"},
            "ca/capital_gains_deductions_line_6",
            "274.00",
        ),
    ],
)
def test_lines_1_4_and_6_are_the_amount_entered_times_the_printed_multiplier(
    amounts: dict[str, str], identifier: str, printed: str
) -> None:
    # The amount is the line 254 total before the multiplier, and the line is the product, rounded
    # half-up to the cent (a dollars-and-cents box).
    worksheet = step_3(**amounts)

    assert worksheet.get(_kind(identifier)).value == D(printed)


def test_line_2_is_amount_a_times_one_and_a_half_with_amount_a_less_the_schedule_3_lines() -> None:
    # Line 2 "For 1988 and 1989 (other than for eligible capital property gains): Total amounts from
    # line 254 of your returns minus any amounts reported on lines 543 and 544 of Schedule 3 (if
    # negative, enter "0") (a) x 1.5": 600 less 300 and 200 is amount (a), 100, and 100 x 1.5 = 150.
    worksheet = step_3(
        capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property="600",
        schedule_3_line_543="300",
        schedule_3_line_544="200",
    )

    assert worksheet.get(_kind("ca/capital_gains_deductions_1988_and_1989_amount_a")).value == D(
        "100"
    )
    assert worksheet.get(_kind("ca/capital_gains_deductions_line_2")).value == D("150.00")


def test_line_2_is_0_when_the_schedule_3_lines_are_more_than_the_amount_entered() -> None:
    # "(if negative, enter "0")": 100 less 300 and 200 is -400, so amount (a) is 0 and line 2 is 0,
    # not -600.
    worksheet = step_3(
        capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property="100",
        schedule_3_line_543="300",
        schedule_3_line_544="200",
    )

    assert worksheet.get(_kind("ca/capital_gains_deductions_1988_and_1989_amount_a")).value == D(
        "0"
    )
    assert worksheet.get(_kind("ca/capital_gains_deductions_line_2")).value == D("0.00")


def test_line_3_is_capped_at_the_schedule_3_lines_543_and_544() -> None:
    # Line 3 "For 1988 and 1989 (for eligible capital property gains): Total amounts from line 254
    # of your returns minus amount (a) above (cannot be more than the amounts from lines 543 and 544
    # of Schedule 3) x 1.3333": 800 less no amount (a) is 800, the lesser of 800 and 500 is 500, and
    # 500 x 1.3333 = 666.65.
    worksheet = step_3(
        capital_gains_deductions_1988_and_1989_eligible_capital_property="800",
        schedule_3_line_543="300",
        schedule_3_line_544="200",
    )

    assert worksheet.get(_kind("ca/capital_gains_deductions_1988_and_1989_limited")).value == D(
        "500"
    )
    assert worksheet.get(_kind("ca/capital_gains_deductions_line_3")).value == D("666.65")


def test_line_3_takes_off_amount_a_then_multiplies_and_rounds_half_up() -> None:
    # Line 2 600 less 500 is (a) 100; line 3 150 less (a) 100 is 50, the lesser of 50 and 500 is 50,
    # and 50 x 1.3333 = 66.665, a tie, up to 66.67.
    worksheet = step_3(
        capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property="600",
        capital_gains_deductions_1988_and_1989_eligible_capital_property="150",
        schedule_3_line_543="300",
        schedule_3_line_544="200",
    )

    assert worksheet.get(
        _kind("ca/capital_gains_deductions_1988_and_1989_after_amount_a")
    ).value == D("50")
    assert worksheet.get(_kind("ca/capital_gains_deductions_line_3")).value == D("66.67")


def test_line_3_is_negative_when_line_3_is_less_than_amount_a_as_the_form_prints_no_floor() -> None:
    # Line 3 40 less (a) 100 is -60; the lesser of -60 and 500 is -60, and -60 x 1.3333 = -79.998,
    # to the cent -80.00. The form prints no floor on this difference, so the line is signed.
    worksheet = step_3(
        capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property="600",
        capital_gains_deductions_1988_and_1989_eligible_capital_property="40",
        schedule_3_line_543="300",
        schedule_3_line_544="200",
    )

    assert worksheet.get(_kind("ca/capital_gains_deductions_1988_and_1989_limited")).value == D(
        "-60"
    )
    assert worksheet.get(_kind("ca/capital_gains_deductions_line_3")).value == D("-80.00")


@pytest.mark.parametrize(
    ("inclusion_rate", "printed"),
    [
        # Line 5 "For 2000: Amount from line 254 of your return x 1/IR (1) = 5": 300 divided by 0.5.
        ("0.5", "600.00"),
        # With an inclusion rate of 0 the line is 0, as the pre-1986 row "In 2000" is.
        ("0", "0.00"),
    ],
)
def test_line_5_is_the_amount_times_one_over_the_inclusion_rate_and_0_when_the_rate_is_0(
    inclusion_rate: str, printed: str
) -> None:
    worksheet = step_3(capital_gains_deductions_2000="300", t657_inclusion_rate_2000=inclusion_rate)

    assert worksheet.get(_kind("ca/capital_gains_deductions_line_5")).value == D(printed)


def test_line_15_may_be_negative_as_the_form_prints_no_floor() -> None:
    # Other reductions (line 14) of 500 and no capital gains deductions (line 7): line 15 is -500,
    # and line 17 "Enter whichever is less: amount from line 15 or line 16." is -500 too, so line 18
    # "Line 16 minus line 17" is 10000 + 500 = 10500 and line 20 is 5250.00. The form prints no
    # floor on lines 15 and 17, so the kinds are signed and the result follows the printed lines.
    worksheet = step_3(
        other_business_investment_loss_reductions_2024="500", business_investment_loss="10000"
    )

    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE).value == D("-500")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION).value == D("-500")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION).value == D("10500")
    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("5250.00")


def test_the_allowable_business_investment_loss_is_rounded_half_up_to_the_cent() -> None:
    # Line 20 is a dollars-and-cents box: 10000.01 x 50% = 5000.005, a tie, up to 5000.01.
    worksheet = step_3(business_investment_loss="10000.01")

    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("5000.01")


def test_a_loss_of_0_gives_an_allowable_loss_of_0() -> None:
    worksheet = step_3()

    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("0")
