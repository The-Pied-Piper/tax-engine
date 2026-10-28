"""CA-ON 2025 end to end: return dr, the supplement's self-employment income.

Return DR is `returns/2025_return_dr.yaml`: a single resident with employment income of 3,000 and
one T2125 statement with a net profit of 1,500, so the working income of the supplement is 4,500
and only the profit lifts it over the $4,390 test; the medical claim is 1,867.08 and the
supplement 466.77. The other tests here vary the statements: a profit with a loss, a T2042 and a
T2121 statement, no statement, and the professional and commission income that Form T929 reads.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.trace import RecordTotalLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    MEDICAL_CLAIM,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME,
    MEDICAL_SUPPLEMENT_LINE_13,
    MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_WORKING_INCOME,
    NET_BUSINESS_INCOME,
    NET_COMMISSION_INCOME,
    NET_FARMING_INCOME,
    NET_FISHING_INCOME,
    NET_INCOME,
    NET_PROFESSIONAL_INCOME,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_dr(employment: str = "3000", **overrides: Any) -> Worksheet:
    """Return DR's inputs, as in `returns/2025_return_dr.yaml`, over the keyword overrides given.

    Medical expenses paid of 2,000 (line 107), Schedule 8 Part 5 completed for the employment and
    the self-employment income, and no CPP or QPP contributions deducted at source (T4 box 16 and
    box 22, chosen $0). Without any statement the return has no self-employment income at all.
    """
    inputs: dict[str, Any] = {
        "medical_expenses": "2000",
        "cpp_part_5_completed": 1,
        "cpp_t4_base_and_first_additional_contributions": "0",
        "cpp_t4_second_additional_contributions": "0",
    }
    inputs.update(overrides)
    return compute(employment, (), "0", "0", "0", "0", "0", **inputs)


def test_return_dr_pays_the_supplement_because_the_self_employment_profit_lifts_it_to_4390() -> (
    None
):
    worksheet = return_dr(business_statements=({"business": {"gross_sales": "1500"}},))

    # The T2125 profit of 1,500 is the net self-employment income of line 13500, a positive
    # statement counted as it is.
    assert worksheet.get(NET_BUSINESS_INCOME).value == D("1500")
    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("1500")
    # "your employment income ... minus the amounts from lines 20700, 21200, 22900, and 23100" is
    # 3,000, under the $4,390 on its own; with the 1,500 the working income is 4,500, which is 4,390
    # or more.
    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME).value == D("3000")
    assert worksheet.get(MEDICAL_SUPPLEMENT_WORKING_INCOME).value == D("4500")
    # Net income 4,430.50 after the self-employment CPP deduction of 69.50 (line 22200); the claim
    # is 2,000 less 3% of the net income, 132.92, so 1,867.08; 25% of it is 466.77.
    assert worksheet.get(NET_INCOME).value == D("4430.50")
    assert worksheet.get(MEDICAL_CLAIM).value == D("1867.08")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_13).value == D("466.77")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("466.77")


def test_without_the_statement_the_employment_income_of_3000_alone_gives_no_supplement() -> None:
    worksheet = return_dr()

    assert worksheet.get(MEDICAL_SUPPLEMENT_WORKING_INCOME).value == D("3000")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("0")


def test_a_t2125_profit_of_6000_and_a_loss_of_2000_gives_6000_as_the_loss_counts_0() -> None:
    # "use only the profit amounts": the loss of the second statement is not included, although
    # the return's line 13500 is the net of both, 4,000.
    worksheet = return_dr(
        business_statements=(
            {"business": {"gross_sales": "6000"}},
            {"business": {"advertising": "2000"}},
        ),
    )

    assert worksheet.get(NET_BUSINESS_INCOME).value == D("6000")
    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("6000")


def test_a_t2042_profit_of_1000_and_a_t2121_profit_of_500_add_to_the_t2125_profit() -> None:
    worksheet = return_dr(
        business_statements=({"business": {"gross_sales": "6000"}},),
        farm_statements=({"farm": {"wheat": "1000"}},),
        fish_statements=({"fish": {"fish_products": "500"}},),
    )

    assert worksheet.get(NET_FARMING_INCOME).value == D("1000")
    assert worksheet.get(NET_FISHING_INCOME).value == D("500")
    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("7500")


def test_no_statement_gives_0_for_the_total_and_the_total_is_computed_from_the_records() -> None:
    worksheet = return_dr()

    assert worksheet.get(NET_BUSINESS_INCOME).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("0")
    # The total is the record list's total of the profits read through Form T1139's summary form
    # (a step of the return, a loss counting 0 there), not an amount entered.
    assert any(
        isinstance(line, RecordTotalLine) and line.output == NET_BUSINESS_INCOME
        for line in worksheet.trace
    )


def test_professional_and_commission_income_count_as_form_t929_reads_them() -> None:
    # A professional statement of 2,000 (code 2) counts; a commission statement with 500 of
    # expenses and no sales (code 3) is a loss of 500, which counts 0 (not below zero).
    worksheet = return_dr(
        business_statements=(
            {"business": {"gross_sales": "2000"}, "business_income_line": 2},
            {"business": {"office_expenses": "500"}, "business_income_line": 3},
        )
    )

    assert worksheet.get(NET_PROFESSIONAL_INCOME).value == D("2000")
    assert worksheet.get(NET_COMMISSION_INCOME).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("2000")
