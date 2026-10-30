"""CA-ON 2025 end to end: return r."""

from __future__ import annotations

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.parameters.amount import Amount
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.trace import ItemsTotalLine, QuotientLine, RecordCountLine
from tax_engine.jurisdictions.ca.catalog import (
    PROVINCIAL_CREDITS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    COOP_EDUCATION_CREDIT,
    COOP_EDUCATION_FULL_SHARE,
    COOP_EDUCATION_PAYROLL,
    COOP_EDUCATION_PAYROLL_OVER_THRESHOLD,
    COOP_EDUCATION_PAYROLL_RANGE,
    COOP_EDUCATION_PAYROLL_THRESHOLD,
    COOP_EDUCATION_PHASE_OUT_SHARE,
    COOP_EDUCATION_PLACEMENT_COUNT,
    COOP_EDUCATION_PLACEMENT_EXPENDITURES,
    COOP_EDUCATION_PLACEMENTS,
    COOP_EDUCATION_REMAINING_SHARE,
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
    ONTARIO_TAX,
)
from tax_engine.jurisdictions.ca_on.trace import PlacementCreditLine
from tests.jurisdictions.ca_on.end_to_end.support import (
    CENT,
    D,
    placement_list,
    return_f_with_credits,
    return_r,
)


def test_return_rs_co_operative_education_credit_is_5200_and_lowers_the_refund_by_that_much() -> (
    None
):
    # Return R is Return M with two work placements, of eligible expenditures 8000 and 15000, and
    # total salaries and wages paid in 2024 of 500000. Worksheet ON479 line 6 is 500000 -
    # 400000.00 = 100000.00, line 8 is 100000.00 / 200000.00 = 0.5 and line 11 is 1.00 - 0.5 =
    # 0.5. Placement 1: line 1 is 2000.00, line 3 400.00, line 12 200.00, line 13 2200.00.
    # Placement 2: line 1 is 3750.00, line 3 750.00, line 12 375.00, line 13 4125.00, capped at
    # 3000. ON479 line 20 is 5200.00; line 21 is 8230.00 + 5200.00 = 13430.00, T1 line 47900 the
    # same; the total credits are 8000 + 0 + 13430.00 = 21430.00 and line 167 is 4240.69 -
    # 21430.00 = -17189.31, Return M's -11989.31 less 5200.00.
    return_m = return_f_with_credits("24000", "1200", ("6000", "4000"))
    worksheet = return_r()

    assert worksheet.get(COOP_EDUCATION_PAYROLL).value == D("500000")
    assert worksheet.get(COOP_EDUCATION_PLACEMENTS) == placement_list("8000", "15000")
    assert worksheet.get(COOP_EDUCATION_PAYROLL_THRESHOLD).value == D("400000.00")
    assert worksheet.get(COOP_EDUCATION_PAYROLL_OVER_THRESHOLD).value == D("100000.00")
    assert worksheet.get(COOP_EDUCATION_PAYROLL_RANGE).value == D("200000.00")
    assert worksheet.get(COOP_EDUCATION_PHASE_OUT_SHARE).value == D("0.5")
    assert worksheet.get(COOP_EDUCATION_FULL_SHARE).value == D("1.00")
    assert worksheet.get(COOP_EDUCATION_REMAINING_SHARE).value == D("0.5")
    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("5200.00")
    assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 2
    assert type(worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value) is int
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("8230.00")
    assert worksheet.get(ONTARIO_CREDITS).value == D("13430.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("13430.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4240.69")
    assert worksheet.get(TOTAL_CREDITS).value == D("21430.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-17189.31")
    assert return_m.get(COOP_EDUCATION_CREDIT).value == D("0")
    assert return_m.get(REFUND_OR_BALANCE_OWING).value == D("-11989.31")
    assert return_m.get(REFUND_OR_BALANCE_OWING).value - worksheet.get(
        REFUND_OR_BALANCE_OWING
    ).value == D("5200.00")
    first, second = [line for line in worksheet.trace if isinstance(line, PlacementCreditLine)]
    assert first == PlacementCreditLine(
        output=COOP_EDUCATION_CREDIT,
        position=1,
        field=COOP_EDUCATION_PLACEMENT_EXPENDITURES,
        expenditure=D("8000"),
        line_1=D("2000.00"),
        line_3=D("400.00"),
        line_12=D("200.00"),
        line_13=D("2200.00"),
        remaining_share=COOP_EDUCATION_REMAINING_SHARE,
        remaining_share_amount=D("0.5"),
        expenditure_rate=Rate(D("0.25")),
        supplement_rate=Rate(D("0.05")),
        maximum=Amount(D("3000")),
        rounding=CENT,
    )
    assert second == PlacementCreditLine(
        output=COOP_EDUCATION_CREDIT,
        position=2,
        field=COOP_EDUCATION_PLACEMENT_EXPENDITURES,
        expenditure=D("15000"),
        line_1=D("3750.00"),
        line_3=D("750.00"),
        line_12=D("375.00"),
        line_13=D("3000.00"),
        remaining_share=COOP_EDUCATION_REMAINING_SHARE,
        remaining_share_amount=D("0.5"),
        expenditure_rate=Rate(D("0.25")),
        supplement_rate=Rate(D("0.05")),
        maximum=Amount(D("3000")),
        rounding=CENT,
    )
    (credit_total,) = [
        line
        for line in worksheet.trace
        if isinstance(line, ItemsTotalLine) and line.output is COOP_EDUCATION_CREDIT
    ]
    assert credit_total == ItemsTotalLine(
        COOP_EDUCATION_CREDIT, ((1, D("2200.00")), (2, D("3000.00"))), D("5200.00")
    )
    (quotient,) = [line for line in worksheet.trace if isinstance(line, QuotientLine)]
    assert quotient == QuotientLine(
        output=COOP_EDUCATION_PHASE_OUT_SHARE,
        dividend=COOP_EDUCATION_PAYROLL_OVER_THRESHOLD,
        dividend_amount=D("100000.00"),
        divisor=COOP_EDUCATION_PAYROLL_RANGE,
        divisor_amount=D("200000.00"),
        result=D("0.5"),
    )
    (count,) = [line for line in worksheet.trace if isinstance(line, RecordCountLine)]
    assert count == RecordCountLine(COOP_EDUCATION_PLACEMENT_COUNT, COOP_EDUCATION_PLACEMENTS, 2)
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "coop_education_payroll_threshold: credit amount 400000 (half-up to 0.01)" in rendered
    assert (
        "coop_education_payroll_over_threshold: coop_education_payroll 500000 "
        "less coop_education_payroll_threshold 400000, not below 0 = 100000"
    ) in rendered
    assert "coop_education_payroll_range: credit amount 200000 (half-up to 0.01)" in rendered
    assert (
        "coop_education_phase_out_share: coop_education_payroll_over_threshold 100000 "
        "divided by coop_education_payroll_range 200000 = 0.5"
    ) in rendered
    assert "coop_education_full_share: credit amount 1 (half-up to 0.01)" in rendered
    assert (
        "coop_education_remaining_share: coop_education_full_share 1 "
        "less coop_education_phase_out_share 0.5, not below 0 = 0.5"
    ) in rendered
    assert (
        "coop_education_credit: item 1 coop_education_placement_expenditures 8000: "
        "line 1 2000, line 3 400, line 12 200, line 13 2200 (half-up to 0.01)"
    ) in rendered
    assert (
        "coop_education_credit: item 2 coop_education_placement_expenditures 15000: "
        "line 1 3750, line 3 750, line 12 375, line 13 3000 (half-up to 0.01)"
    ) in rendered
    assert "coop_education_credit: item 1 2200 + item 2 3000 = 5200" in rendered
    assert ("coop_education_placement_count: 2 items in coop_education_placements = 2") in rendered
    assert (
        "ontario_credits: ontario_credits_subtotal 8230 + coop_education_credit 5200 = 13430"
    ) in rendered
    assert "provincial_credits: ontario_credits 13430 = 13430" in rendered
    assert (
        "total_credits: income_tax_deducted_after_election 8000 + cpp_overpayment 0 "
        "+ ei_overpayment 0 "
        "+ refundable_medical_expense_supplement 0 "
        "+ canada_workers_benefit 0 "
        "+ canada_training_credit 0 + multigenerational_home_renovation_credit 0 "
        "+ investment_tax_credit_refund 0 + part_xii_2_tax_credit 0 + "
        "employee_and_partner_gst_hst_rebate 0 "
        "+ educator_school_supply_credit 0 + journalism_labour_tax_credit 0 "
        "+ fuel_charge_credit_farmers_total 0 "
        "+ tax_paid_by_instalments 0 + provincial_credits 13430 = 21430"
    ) in rendered
    assert (
        "refund_or_balance_owing: total_payable 4240.69 less total_credits 21430 = -17189.31"
    ) in rendered


@pytest.mark.parametrize(
    ("payroll", "line_8", "line_11", "credit"),
    [
        # The worked examples, for placements of 8000 and 15000.
        ("500000", "0.5", "0.5", "5200"),
        ("700000", "1.5", "0", "5000"),
        ("300000", "0", "1", "5400"),
        # 400000 is the 30% result and 600000 the 25% result for each placement.
        ("400000", "0", "1", "5400"),
        ("600000", "1", "0", "5000"),
    ],
)
def test_the_worksheets_worked_examples_for_two_placements(
    payroll: str, line_8: str, line_11: str, credit: str
) -> None:
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll=payroll, coop_education_placements=("8000", "15000")
    )

    assert worksheet.get(COOP_EDUCATION_PHASE_OUT_SHARE).value == D(line_8)
    assert worksheet.get(COOP_EDUCATION_REMAINING_SHARE).value == D(line_11)
    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D(credit)
    # Line 21 adds line 20 to line 18, which is Return F's care credit of 2550.00 (line 2).
    assert worksheet.get(ONTARIO_CREDITS).value == D(credit) + D("2550.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D(credit) + D("2550.00")
    assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 2


@pytest.mark.parametrize(
    ("payroll", "credit"),
    [
        # At or below 400000 the percentage is 30%, at 600000 or more 25%, in between 25% plus 5%
        # times the remaining share: 8000 x 30% = 2400, 8000 x 25% = 2000, and 2000 + 400 x 0.75.
        ("0", "2400"),
        ("300000", "2400"),
        ("400000", "2400"),
        ("450000", "2300"),
        ("500000", "2200"),
        ("550000", "2100"),
        ("600000", "2000"),
        ("700000", "2000"),
    ],
)
def test_one_placement_of_8000_is_30_percent_to_25_percent_across_the_payroll_range(
    payroll: str, credit: str
) -> None:
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll=payroll, coop_education_placements=("8000",)
    )

    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D(credit)
    assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 1


def test_line_8_is_an_exact_fraction_and_is_not_rounded() -> None:
    # 0.07 / 200000.00 = 0.00000035, so line 11 is 1.00 - 0.00000035 = 0.99999965.
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="400000.07", coop_education_placements=("8000",)
    )

    assert worksheet.get(COOP_EDUCATION_PAYROLL_OVER_THRESHOLD).value == D("0.07")
    assert worksheet.get(COOP_EDUCATION_PHASE_OUT_SHARE).value == D("0.00000035")
    assert worksheet.get(COOP_EDUCATION_REMAINING_SHARE).value == D("0.99999965")
    # 2000 + 400 x 0.99999965 = 2399.9998600, rounded half-up to the cent: 2400.00.
    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("2400.00")
    assert (
        "coop_education_phase_out_share: coop_education_payroll_over_threshold 0.07 "
        "divided by coop_education_payroll_range 200000 = 0.00000035"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_a_payroll_over_600000_leaves_line_11_at_zero_not_negative() -> None:
    # Line 8 is 1.5, 1.00 - 1.5 is negative, so line 11 is "0".
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="700000", coop_education_placements=("8000",)
    )

    assert worksheet.get(COOP_EDUCATION_PHASE_OUT_SHARE).value == D("1.5")
    assert worksheet.get(COOP_EDUCATION_REMAINING_SHARE).value == D("0")
    assert (
        "coop_education_remaining_share: coop_education_full_share 1 "
        "less coop_education_phase_out_share 1.5, not below 0 = 0"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_a_payroll_of_less_than_400000_leaves_line_6_at_zero_not_negative() -> None:
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="300000", coop_education_placements=("8000",)
    )

    assert worksheet.get(COOP_EDUCATION_PAYROLL_OVER_THRESHOLD).value == D("0")
    assert worksheet.get(COOP_EDUCATION_PHASE_OUT_SHARE).value == D("0")
    assert (
        "coop_education_payroll_over_threshold: coop_education_payroll 300000 "
        "less coop_education_payroll_threshold 400000, not below 0 = 0"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


@pytest.mark.parametrize("payroll", ["0", "300000", "500000", "700000"])
def test_no_placements_leave_the_credit_and_the_count_at_zero_whatever_the_payroll(
    payroll: str,
) -> None:
    worksheet = return_f_with_credits("0", "0", (), coop_education_payroll=payroll)

    assert worksheet.get(COOP_EDUCATION_PLACEMENTS) == placement_list()
    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("0")
    assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 0
    assert worksheet.get(ONTARIO_CREDITS).value == D("2550.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6309.31")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "coop_education_placement_count: no items in coop_education_placements = 0" in rendered
    assert "coop_education_credit: no items = 0" in rendered


def test_one_placement_gives_a_count_of_one_in_the_singular() -> None:
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="400000", coop_education_placements=("8000",)
    )

    assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 1
    assert (
        "coop_education_placement_count: 1 item in coop_education_placements = 1"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_the_count_of_placements_is_not_the_number_of_dollars_or_the_credit() -> None:
    worksheet = return_f_with_credits(
        "0",
        "0",
        (),
        coop_education_payroll="400000",
        coop_education_placements=("100", "200", "300", "400", "500"),
    )

    assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 5
    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("450.00")
    assert (
        "coop_education_placement_count: 5 items in coop_education_placements = 5"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_the_maximum_of_3000_applies_to_each_student_and_not_to_the_total() -> None:
    # Ten placements of 15000 at 30%: 4500 each, capped at 3000 each, 30000 in all.
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="400000", coop_education_placements=("15000",) * 10
    )

    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("30000.00")
    assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 10


def test_the_co_operative_education_credit_is_not_limited_by_the_tax() -> None:
    # ON479 is a refundable-credits form: line 20 is not taken off the Ontario tax of 1786.52; it
    # is added to line 21 and T1 line 47900 whole, with the care credit of 2550.00 (line 2).
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="400000", coop_education_placements=("15000",) * 10
    )

    assert worksheet.get(ONTARIO_TAX).value == D("1786.52")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("32550.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("40550.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-36309.31")


def test_each_placements_line_13_is_rounded_before_they_are_added() -> None:
    # Two placements of 0.10 at 25% (payroll 600000): 0.025 each, 0.03 each half-up, 0.06 in all.
    # Rounding their sum 0.05 once would give 0.05.
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="600000", coop_education_placements=("0.10", "0.10")
    )

    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("0.06")
    assert worksheet.get(ONTARIO_CREDITS).value == D("2550.06")


def test_lines_1_and_12_are_added_before_line_13_is_rounded() -> None:
    # 0.14 at 30% (payroll 400000): line 1 is 0.035 and line 12 is 0.007, so line 13 is 0.042,
    # rounded half-up to 0.04. Rounding the two lines first would give 0.04 + 0.01 = 0.05.
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="400000", coop_education_placements=("0.14",)
    )

    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("0.04")


def test_the_credit_follows_the_order_of_the_placements_in_the_trace() -> None:
    worksheet = return_f_with_credits(
        "0", "0", (), coop_education_payroll="500000", coop_education_placements=("15000", "8000")
    )

    lines = [line for line in worksheet.trace if isinstance(line, PlacementCreditLine)]
    assert [(line.position, line.expenditure) for line in lines] == [
        (1, D("15000")),
        (2, D("8000")),
    ]
    assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("5200.00")


def test_a_negative_payroll_is_refused() -> None:
    with pytest.raises(NegativeArtifactError, match="coop_education_payroll"):
        return_f_with_credits("0", "0", (), coop_education_payroll="-1")


def test_a_negative_eligible_expenditure_is_refused_naming_the_placement() -> None:
    with pytest.raises(
        NegativeArtifactError, match="item 2: .*coop_education_placement_expenditures"
    ):
        return_f_with_credits("0", "0", (), coop_education_placements=("8000", "-1"))
