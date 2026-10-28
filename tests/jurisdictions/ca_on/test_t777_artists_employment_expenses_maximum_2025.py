"""The artists' employment expenses limit of Guide T4044 (2025) "Part 1 - Artists' employment
expenses", end to end.

Each test fills Form T777 with the Guide's example (advertising 950 paid; artistic employment income
20,000; musical instrument expenses 350; claim 650) and changes the limit's figures:
- the most that can be claimed is the lesser of a) the expenses paid plus the carry forward and b)
  the lesser of $1,000 and 20% of the artistic income, minus the musical instrument expenses, the
  motor vehicle interest and the motor vehicle capital cost allowance deducted from artistic income;
- a line 14 claim above it is refused, never capped;
- the income from artistic activities is a part of the employment income of the return, so more
  than it is refused.
"""

from __future__ import annotations

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_START,
    T777_ARTISTS_DEDUCTIONS_FROM_ARTISTIC_INCOME,
    T777_ARTISTS_EMPLOYMENT_EXPENSES_MAXIMUM_DEDUCTION,
    T777_ARTISTS_EMPLOYMENT_INCOME_CHECKED,
    T777_ARTISTS_EXPENSES_AVAILABLE,
    T777_ARTISTS_EXPENSES_CARRIED_FORWARD_OUT,
    T777_ARTISTS_LIMIT,
    T777_CLASS_8_ROWS,
    T777_LINE_14,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting
from tests.jurisdictions.ca_on.end_to_end.test_return_ee import rows
from tests.jurisdictions.ca_on.end_to_end.test_return_hi import t777_form

SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
MAXIMUM = "ca/t777_artists_employment_expenses_maximum"
RATE_DATASET = "ca/t777_artists_employment_expenses_rate"
T4044_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4044/t4044-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
# The Guide's example: the lesser of 950 and (the lesser of 1,000 and 4,000) minus 350: 650.
EXAMPLE = {
    "artists_expenses_paid": "950",
    "artists_employment_income": "20000",
    "musical_instrument_expenses": "350",
    "artists_employment_expenses": "650",
    # The limit of Guide T4044 "Part 2" on the instrument expenses needs the income as a musician:
    # the Guide's 20,000, taken as the same income.
    "musician_employment_income": "20000",
}


def form(**changes: str) -> Worksheet:
    """The T777 worksheet of the Guide's example with the figures `changes`."""
    return t777_form(employment="20000", **{**EXAMPLE, **changes})


def test_2025_maximum_is_1000_and_rate_is_20_percent_rounded_to_the_cent() -> None:
    maximum = SOURCE.get(MAXIMUM, 2025, AMOUNT)
    rate = SOURCE.get(RATE_DATASET, 2025, RATE)

    assert maximum.values == Amount(D("1000"))
    assert rate.values == Rate(D("0.20"))
    assert maximum.rounding == CENT
    assert rate.rounding == CENT
    assert T4044_TXT in maximum.sources
    assert T4044_TXT in rate.sources


def test_the_guide_example_has_a_maximum_of_650() -> None:
    worksheet = form()

    assert worksheet.get(T777_ARTISTS_EXPENSES_AVAILABLE).value == D("950")
    assert worksheet.get(T777_ARTISTS_DEDUCTIONS_FROM_ARTISTIC_INCOME).value == D("350")
    assert worksheet.get(T777_ARTISTS_LIMIT).value == D("650.00")
    assert worksheet.get(T777_ARTISTS_EMPLOYMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("650.00")
    assert worksheet.get(T777_LINE_14).value == D("650")


def test_a_claim_of_one_cent_above_the_maximum_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError, match="t777_artists_employment_expenses_maximum_deduction"
    ):
        form(artists_employment_expenses="650.01")


def test_twenty_percent_of_a_small_income_is_the_lesser_of_the_two() -> None:
    # 20% of 3,000 is 600, less than $1,000; less the instrument expenses 350 is 250.
    worksheet = form(artists_employment_income="3000", artists_employment_expenses="250")

    assert worksheet.get(T777_ARTISTS_LIMIT).value == D("250.00")
    assert worksheet.get(T777_LINE_14).value == D("250")
    with pytest.raises(InputAboveBoundError):
        form(artists_employment_income="3000", artists_employment_expenses="250.01")


def test_expenses_paid_below_the_limit_are_the_maximum() -> None:
    worksheet = form(artists_expenses_paid="400", artists_employment_expenses="400")

    assert worksheet.get(T777_ARTISTS_EMPLOYMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("400")


def test_the_amounts_carried_forward_count_with_the_expenses_paid() -> None:
    worksheet = form(
        artists_expenses_paid="100",
        artists_expenses_carry_forward="300",
        artists_employment_expenses="400",
    )

    assert worksheet.get(T777_ARTISTS_EXPENSES_AVAILABLE).value == D("400")
    assert worksheet.get(T777_ARTISTS_EMPLOYMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("400")


def test_the_motor_vehicle_interest_and_allowance_are_deducted_from_the_limit() -> None:
    # 1,000 minus 350 of instruments, 100 of interest and 50 of allowance is 500.
    worksheet = form(
        artists_vehicle_interest_deducted="100",
        artists_vehicle_cca_deducted="50",
        artists_employment_expenses="500",
    )

    assert worksheet.get(T777_ARTISTS_LIMIT).value == D("500.00")
    with pytest.raises(InputAboveBoundError):
        form(
            artists_vehicle_interest_deducted="100",
            artists_vehicle_cca_deducted="50",
            artists_employment_expenses="500.01",
        )


def test_deductions_above_the_limit_leave_nothing_to_claim() -> None:
    # 1,000 minus 1,200 of instruments is below zero: no claim, a claim of 0 is accepted.
    worksheet = form(musical_instrument_expenses="1200", artists_employment_expenses="0")

    assert worksheet.get(T777_ARTISTS_LIMIT).value == D("0")
    assert worksheet.get(T777_LINE_14).value == D("0")
    with pytest.raises(InputAboveBoundError):
        form(musical_instrument_expenses="1200", artists_employment_expenses="0.01")


def test_a_claim_without_any_limit_figures_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        t777_form(artists_employment_expenses="1")


def test_the_capital_cost_allowance_for_musical_instruments_of_line_13_is_deducted_too() -> None:
    # Part 2: the "Musical instrument expenses" line and the "Capital cost allowance for musical
    # instruments" line (13). A Class 8 row gives line 13 of 250.00 (as in Return EE): 1,000 minus
    # 350 and 250 is 400.
    artifacts = [
        each
        for each in starting(
            "20000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            t777_amounts={**EXAMPLE, "artists_employment_expenses": "400"},
        )
        if each.kind is not T777_CLASS_8_ROWS
    ]
    class_8 = rows(
        T777_CLASS_8_ROWS,
        {
            CCA_CLASS_NUMBER: "8",
            CCA_UCC_AT_START: "1000",
            CCA_ADDITIONS: "500",
            CCA_CLAIMED: "250",
        },
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts, class_8)["ca/t777"]

    assert worksheet.get(T777_ARTISTS_DEDUCTIONS_FROM_ARTISTIC_INCOME).value == D("600.00")
    assert worksheet.get(T777_ARTISTS_LIMIT).value == D("400.00")


def test_the_guide_example_carries_300_forward() -> None:
    # 950 available, 650 allowed: "expenses you cannot claim because of the 20% or $1,000 limit".
    worksheet = form()

    assert worksheet.get(T777_ARTISTS_EXPENSES_CARRIED_FORWARD_OUT).value == D("300.00")


def test_the_expenses_paid_below_the_limit_leave_nothing_to_carry_forward() -> None:
    worksheet = form(artists_expenses_paid="400", artists_employment_expenses="400")

    assert worksheet.get(T777_ARTISTS_EXPENSES_CARRIED_FORWARD_OUT).value == D("0")


def test_the_amounts_carried_in_that_the_limit_does_not_allow_are_carried_on() -> None:
    # 100 paid plus 1,200 carried in is 1,300 available; 1,000 less the instruments 350 is 650.
    worksheet = form(
        artists_expenses_paid="100",
        artists_expenses_carry_forward="1200",
        artists_employment_expenses="650",
    )

    assert worksheet.get(T777_ARTISTS_EXPENSES_CARRIED_FORWARD_OUT).value == D("650.00")


def test_a_claim_below_the_maximum_does_not_change_the_amount_carried_forward() -> None:
    # The Guide carries forward the expenses that "cannot" be claimed because of the limit, not
    # those the filer chose to leave out: 950 available less the maximum 650 is 300 at a claim of 0.
    worksheet = form(artists_employment_expenses="0")

    assert worksheet.get(T777_ARTISTS_EXPENSES_CARRIED_FORWARD_OUT).value == D("300.00")


def test_deductions_above_the_limit_carry_all_the_expenses_forward() -> None:
    worksheet = form(musical_instrument_expenses="1200", artists_employment_expenses="0")

    assert worksheet.get(T777_ARTISTS_EXPENSES_CARRIED_FORWARD_OUT).value == D("950")


def test_the_artistic_income_is_a_part_of_the_employment_income_of_the_return() -> None:
    # The return's employment income is 20,000: all of it from artistic activities is accepted.
    worksheet = form(artists_employment_income="20000")

    assert worksheet.get(T777_ARTISTS_EMPLOYMENT_INCOME_CHECKED).value == D("20000")


def test_an_artistic_income_of_one_cent_above_the_employment_income_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="t777_work_space_employment_income"):
        form(artists_employment_income="20000.01")


def test_the_other_employment_income_of_line_10400_counts_in_the_whole() -> None:
    # Line 51 of the line 16 chart reads T1 lines 10100 and 10400 as the employment income.
    artifacts = starting(
        "12000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_employment_income="8000",
        t777_amounts={**EXAMPLE},
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)["ca/t777"]

    assert worksheet.get(T777_ARTISTS_EMPLOYMENT_INCOME_CHECKED).value == D("20000")
