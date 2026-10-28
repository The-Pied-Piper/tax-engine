"""The 2025 datasets of Form T2125 Charts A to C (motor vehicle expenses, line 9281), checked
against CRA's form, and the charts worked for one leased passenger vehicle and for several
vehicles, by the capability `ca/business_vehicle_expenses` (one record of the statement's
`ca/business_vehicles` for each vehicle; the lines of each vehicle are in its trace line).

Form T2125 (Statement of Business or Professional Activities, 2025 edition, confirmed 2026-10-19
from the PDF; no .txt is published, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2125/
t2125-25e.pdf):

- Chart A line 16 "Allowable motor vehicle expenses: Add amounts 13 to 15 (enter this total on line
  9281 of Part 4)", line 13 "Business use part: amount 1 ÷ amount 2 × amount 12 = 13" and line 12
  "Total motor vehicle expenses: Add amounts 3 to 11.";
- Chart B line 18 "($350*** ÷ 30) × the number of days in the fiscal period for which interest was
  payable (accrual method) or paid (cash method)", and line 19 "Available interest expense: Amount
  17 or 18, whichever is less (include this in amount 4 of Chart A above)";
- Chart C line 23 "Amount 23 or ($44,706 + GST and PST, or $44,706 + HST), whichever is
  more", line 24 "× 85%", line 25 "[($1,100 + GST and PST, or $1,100 + HST) × amount 22] ÷ 30",
  line 27 "[($38,000 + GST and PST, or $38,000 + HST) × amount 20] ÷ amount 24" and line 28
  "Eligible leasing cost: Amount 26 or 27, whichever is less (enter in amount 8 of Chart A
  above)"; the sales tax rate is "Use a GST rate of 5% or HST rate applicable to your province."

The printed constants are the 2025 figures in the chart body, and the footnote and endnotes give
the figures of earlier years, which are modelled as rows of two `year_amounts` datasets
(`ca/business_vehicle_interest_limits` and `ca/business_vehicle_lease_limits`) that the vehicle's
`purchase_year` and `lease_year` choose among:

- Chart B footnote "*** For passenger vehicles bought after 2023. For passenger vehicles bought
  after 2000 and before 2024, the amount is $300.";
- Chart C endnotes 11 to 13: leases entered into in 2024 (line 24 base 43,529, line 25 $1,050,
  line 27 $37,000), 2023 (42,353, $950, $36,000), 2022 (40,000, $900, $34,000) and before 2022
  (35,294, $800, $30,000); the 2025 set is 44,706, $1,100 and $38,000.

Every product and quotient is a
dollars-and-cents box and rounds half-up to the cent (the dataset `ca/business_vehicle_rounding`),
the owner's decision, as the form states no rounding rule. Amount 26 is a subtraction the form
prints without a floor; a vehicle whose amount 26 is below zero is refused. A vehicle whose
business kilometres (Chart A amount 1) are above its total kilometres (amount 2) is refused too
(`InputAboveBoundError`, "item N: ..." naming amounts 1 and 2 of Chart A).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import tax_calculator.jurisdictions.ca
import tax_calculator.registrations
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.errors import InputAboveBoundError, InvalidRecordError
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts, YearAmountsRow
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_MOTOR_VEHICLE_EXPENSES,
    BUSINESS_TOTAL_EXPENSES,
)
from tax_calculator.jurisdictions.ca.trace import BusinessVehicleLine
from tests.jurisdictions.ca_on.end_to_end.support import D, run

SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T2125_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2125/t2125-25e.pdf"
T4002_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4002/t4002-25e.pdf"

# The printed 30 of Chart B line 18 and Chart C line 25, a dataset of the same name.
DAYS_DIVISOR = "ca/business_vehicle_days_divisor"
DEPOSIT_MINIMUM = "ca/business_vehicle_deposit_minimum"
INTEREST_LIMITS = "ca/business_vehicle_interest_limits"
LEASE_LIMITS = "ca/business_vehicle_lease_limits"
FIGURES = (
    INTEREST_LIMITS,
    LEASE_LIMITS,
    DAYS_DIVISOR,
    "ca/business_vehicle_lease_price_rate",
    "ca/business_vehicle_rounding",
)


def test_2025_the_days_divisor_is_the_printed_30() -> None:
    data = SOURCE.get(DAYS_DIVISOR, 2025, CREDIT)

    assert data.values == Credit(amount=D("30"))
    assert data.rounding == CENT


def test_2025_the_deposit_minimum_is_the_guides_1000() -> None:
    # Guide T4002 printed page 56: "the total of the deposits is more than $1,000".
    data = SOURCE.get(DEPOSIT_MINIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("1000"))
    assert data.rounding == CENT
    assert T4002_PDF in data.sources


def test_2025_the_interest_limits_are_the_350_and_300_of_chart_b() -> None:
    # Footnote "***": "For passenger vehicles bought after 2023" the amount is $350 (line 18
    # "($350*** ÷ 30)"); "For passenger vehicles bought after 2000 and before 2024, the amount is
    # $300". Nothing is printed for a vehicle bought in 2000 or earlier.
    data = SOURCE.get(INTEREST_LIMITS, 2025, YEAR_AMOUNTS)

    assert data.values == YearAmounts(
        (
            YearAmountsRow(2024, {"interest_limit": D("350")}),
            YearAmountsRow(2001, {"interest_limit": D("300")}),
        )
    )
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("year", "expected"),
    [(2025, "350"), (2024, "350"), (2023, "300"), (2001, "300"), (2000, None), (0, None)],
)
def test_2025_the_interest_limit_for_the_year_the_vehicle_was_bought(
    year: int, expected: str | None
) -> None:
    row = SOURCE.get(INTEREST_LIMITS, 2025, YEAR_AMOUNTS).values.row_for(year)

    assert (None if row is None else row.amount("interest_limit")) == (
        None if expected is None else D(expected)
    )


def test_2025_the_lease_limits_are_the_five_sets_of_chart_c() -> None:
    # Line 23 "($44,706 + GST and PST, or $44,706 + HST)", line 25 "($1,100 + ...)" and line 27
    # "($38,000 + ...)" for 2025 and endnotes 11 to 13 for leases entered into in 2024, 2023, 2022
    # and before 2022.
    data = SOURCE.get(LEASE_LIMITS, 2025, YEAR_AMOUNTS)

    def entry(from_year: int | None, price: str, charge: str, cost: str) -> YearAmountsRow:
        return YearAmountsRow(
            from_year,
            {
                "list_price_limit": D(price),
                "lease_charge_limit": D(charge),
                "lease_cost_limit": D(cost),
            },
        )

    assert data.values == YearAmounts(
        (
            entry(2025, "44706", "1100", "38000"),
            entry(2024, "43529", "1050", "37000"),
            entry(2023, "42353", "950", "36000"),
            entry(2022, "40000", "900", "34000"),
            entry(None, "35294", "800", "30000"),
        )
    )
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("year", "figures"),
    [
        (2026, ("44706", "1100", "38000")),
        (2025, ("44706", "1100", "38000")),
        (2024, ("43529", "1050", "37000")),
        (2023, ("42353", "950", "36000")),
        (2022, ("40000", "900", "34000")),
        (2021, ("35294", "800", "30000")),
        (2000, ("35294", "800", "30000")),
        (0, ("35294", "800", "30000")),
    ],
)
def test_2025_the_lease_limits_for_the_year_the_lease_was_entered_into(
    year: int, figures: tuple[str, str, str]
) -> None:
    row = SOURCE.get(LEASE_LIMITS, 2025, YEAR_AMOUNTS).values.row_for(year)

    assert row is not None
    assert (
        row.amount("list_price_limit"),
        row.amount("lease_charge_limit"),
        row.amount("lease_cost_limit"),
    ) == tuple(D(figure) for figure in figures)


@pytest.mark.parametrize("family", FIGURES)
def test_2025_each_chart_figure_cites_the_form(family: str) -> None:
    if family.endswith("_rate"):
        assert T2125_PDF in SOURCE.get(family, 2025, RATE).sources
    elif family.endswith("_rounding"):
        assert T2125_PDF in SOURCE.get(family, 2025, ROUNDING_ONLY).sources
    elif family.endswith("_limits"):
        assert T2125_PDF in SOURCE.get(family, 2025, YEAR_AMOUNTS).sources
    else:
        assert T2125_PDF in SOURCE.get(family, 2025, CREDIT).sources


# The four single-figure datasets that the two year tables replace: deleted, so the forms read the
# figure by year.
CREDIT_LIMITS = (
    "ca/business_vehicle_interest_limit",
    "ca/business_vehicle_list_price_limit",
    "ca/business_vehicle_lease_charge_limit",
    "ca/business_vehicle_lease_cost_limit",
)


@pytest.mark.parametrize("family", CREDIT_LIMITS)
def test_2025_the_four_credit_limit_datasets_are_deleted(family: str) -> None:
    parameters = Path(tax_calculator.jurisdictions.ca.__file__).parent / "parameters"

    assert not (parameters / family.removeprefix("ca/") / "2025.yaml").exists()
    assert not (parameters / family.removeprefix("ca/")).exists()


def test_2025_the_leasing_price_rate_is_85_percent() -> None:
    # Chart C line 24: "Amount 23 or ($44,706 + GST and PST, or $44,706 + HST), whichever is more ×
    # 85%".
    data = SOURCE.get("ca/business_vehicle_lease_price_rate", 2025, RATE)

    assert data.values == Rate(D("0.85"))
    assert data.rounding == CENT


def test_2025_the_chart_rounding_is_half_up_to_the_cent_with_no_values() -> None:
    # One rounding for every product and quotient of Charts A to C (lines 13, 18, 24, 25 and 27 and
    # the sales tax on the printed amounts): the form states none, so the owner's decision.
    data = SOURCE.get("ca/business_vehicle_rounding", 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT


# The five per-line roundings that Charts A to C had for each form before the one
# `ca/business_vehicle_rounding` (the form states none): the datasets are deleted, so the forms
# that take the vehicles as a list round with the one dataset.
PER_LINE_ROUNDINGS = (
    "ca/business_vehicle_business_use_rounding",
    "ca/business_vehicle_interest_rounding",
    "ca/business_vehicle_sales_tax_rounding",
    "ca/business_vehicle_lease_charge_rounding",
    "ca/business_vehicle_lease_cost_rounding",
)


@pytest.mark.parametrize("family", PER_LINE_ROUNDINGS)
def test_2025_the_per_line_chart_roundings_are_deleted(family: str) -> None:
    parameters = Path(tax_calculator.jurisdictions.ca.__file__).parent / "parameters"

    assert not (parameters / family.removeprefix("ca/") / "2025.yaml").exists()


# A leased passenger vehicle used half for business, the figures of Return BB (see
# returns/2025_return_bb.yaml): Chart B interest 400 on 183 days, Chart C lease charges 2550 over
# 183 days at a list price of 60000 and a 13% HST rate, and the other Chart A lines.
LEASED: dict[str, str] = {
    "business_kilometres": "5000",
    "total_kilometres": "10000",
    "fuel_and_oil": "1000",
    "insurance": "600",
    "maintenance_and_repairs": "200",
    "other_expenses_10": "653",
    "interest_payable": "400",
    "interest_days": "183",
    "lease_charges": "2550",
    "lease_days": "183",
    "list_price": "60000",
}


def statement(
    *vehicles: dict[str, str],
    rate: str = "13",
    fiscal_period_from: int = 0,
    fiscal_period_to: int = 0,
) -> Worksheet:
    """A T2125 of gross sales of 50000 and office expenses of 20000, with the vehicles given (one
    record of `ca/business_vehicles` for each; the amounts not given are 0) and the sales tax
    rate of the province, and the fiscal period entered as its from and to dates, YYYYMMDD (none,
    0 and 0, a full year, by default)."""
    amounts = {"gross_sales": "50000", "office_expenses": "20000", "vehicle_sales_tax_rate": rate}
    result = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(
            {
                "business": amounts,
                "business_vehicles_rows": vehicles,
                "business_fiscal_period_from": fiscal_period_from,
                "business_fiscal_period_to": fiscal_period_to,
            },
        ),
    )
    return result["ca/t2125"][0]


def line(worksheet: Worksheet, kind: Any) -> Any:
    return worksheet.get(kind).value


def vehicle_lines(worksheet: Worksheet) -> list[BusinessVehicleLine]:
    return [each for each in worksheet.trace if isinstance(each, BusinessVehicleLine)]


def test_a_leased_vehicle_gives_line_9281_of_2500_and_the_expenses_of_22500() -> None:
    # Chart A: line 12 is 1000 (3) + 400 (4, line 19) + 600 (5) + 200 (7) + 2147 (8, line 28)
    # + 653 (10) = 5000; line 13 is 5000 x 5000 / 10000 = 2500; line 16 is 2500 + 0 + 0 = 2500,
    # line 9281. Line 9368 is 20000 + 2500 = 22500 and line 9369 is 50000 - 22500 = 27500.
    worksheet = statement(LEASED)

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_12 == D("5000")
    assert vehicle.line_13 == D("2500")
    assert line(worksheet, BUSINESS_MOTOR_VEHICLE_EXPENSES) == D("2500")
    assert line(worksheet, BUSINESS_TOTAL_EXPENSES) == D("22500")


def test_line_9281_is_the_total_of_the_vehicles_trace() -> None:
    worksheet = statement(LEASED)

    (total,) = [
        each
        for each in worksheet.trace
        if isinstance(each, ItemsTotalLine) and each.output is BUSINESS_MOTOR_VEHICLE_EXPENSES
    ]
    assert total.items == ((1, D("2500")),)
    assert total.total == D("2500")


def test_chart_b_interest_is_the_amount_payable_when_that_is_the_lesser() -> None:
    # Chart B line 18: 350 ÷ 30 × 183 days = 64050 ÷ 30 = 2135.00; line 17 is 400, the lesser,
    # so line 19, the available interest expense, is 400.
    (vehicle,) = vehicle_lines(statement(LEASED))

    assert vehicle.line_19 == D("400.00")


def test_chart_b_interest_is_capped_at_the_350_over_30_a_day_amount() -> None:
    # Line 17 is 3000, more than line 18 of 2135.00 (350 ÷ 30 × 183), so line 19 is 2135.00.
    (vehicle,) = vehicle_lines(statement({**LEASED, "interest_payable": "3000"}))

    assert vehicle.line_19 == D("2135.00")


def test_chart_b_interest_of_a_vehicle_bought_in_2022_is_capped_at_the_300_a_day_amount() -> None:
    # "For passenger vehicles bought after 2000 and before 2024, the amount is $300": line 18 is
    # 300 ÷ 30 × 183 = 1830.00, less than the 3000 payable, so line 19 is 1830.00 (not 2135.00).
    (vehicle,) = vehicle_lines(
        statement({**LEASED, "interest_payable": "3000", "purchase_year": "2022"})
    )

    assert vehicle.line_19 == D("1830.00")


def test_chart_c_leasing_cost_of_a_lease_entered_into_in_2023_uses_endnote_12() -> None:
    # Endnote 12 (2023): 42353, $950 and $36,000. Line 23: 42353 + 13% (5505.89) = 47858.89 is
    # below the list price of 60000, so line 24 is 51000.00; line 25 is (950 + 123.50 = 1073.50) ×
    # 183 ÷ 30 = 6548.35; line 27 is (36000 + 4680.00 = 40680.00) × 2550 ÷ 51000.00 = 2034.00.
    (vehicle,) = vehicle_lines(statement({**LEASED, "lease_year": "2023"}))

    assert vehicle.line_28 == D("2034.00")


def test_chart_c_takes_the_price_plus_tax_when_it_is_more_than_the_list_price() -> None:
    # Line 23 is 40000; 44706 plus 13% (5811.78) is 50517.78, the greater, and 85% of it is
    # 42940.113, which rounds to 42940.11 (line 24). Line 27 is 42940.00 x 2550 / 42940.11 =
    # 2549.99 and line 28 is the lesser of it and line 26 (7582.30): 2549.99.
    (vehicle,) = vehicle_lines(statement({**LEASED, "list_price": "40000"}))

    assert vehicle.line_28 == D("2549.99")


def test_chart_c_takes_the_list_price_when_it_is_more_than_the_price_plus_tax() -> None:
    # Line 23 is 60000, more than 50517.78, so line 24 is 60000 x 85% = 51000.00.
    (vehicle,) = vehicle_lines(statement(LEASED))

    assert vehicle.line_28 == D("2147.00")


def test_chart_c_leasing_cost_is_the_lesser_of_line_26_and_line_27() -> None:
    # Line 25 is (1100 + 13% of 1100 = 1243.00) x 183 days = 227469.00 ÷ 30 = 7582.30, so line 26 is
    # 7582.30 - 0 = 7582.30; line 27 is (38000 + 13% = 42940.00) x 2550 lease charges = 109497000
    # ÷ 51000.00 = 2147.00, so line 28, the leasing cost, is the lesser, 2147.00.
    (vehicle,) = vehicle_lines(statement(LEASED))

    assert vehicle.line_28 == D("2147.00")


def test_chart_c_leasing_cost_is_line_26_when_the_payments_before_make_it_the_lesser() -> None:
    # Line 25 is 7582.30 and line 21 is 7000, so line 26 is 582.30, less than line 27 (2147.00):
    # line 28 is 582.30, line 12 is 1000 + 400 + 600 + 200 + 582.30 + 653 = 3435.30 and line 13 is
    # 3435.30 x 5000 / 10000 = 1717.65, line 9281.
    worksheet = statement({**LEASED, "lease_payments_before": "7000"})

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_28 == D("582.30")
    assert vehicle.line_12 == D("3435.30")
    assert line(worksheet, BUSINESS_MOTOR_VEHICLE_EXPENSES) == D("1717.65")


def test_chart_c_line_28_below_zero_is_refused() -> None:
    # Line 25 is 7582.30 and line 21 (payments before the year) is 9000, so line 26 is
    # 7582.30 - 9000 = -1417.70. The form prints no floor, but the eligible leasing cost (line 28)
    # is a non-negative amount, so the computation refuses it rather than inventing a floor.
    with pytest.raises(InputAboveBoundError, match="Chart C amount 21"):
        statement({**LEASED, "lease_payments_before": "9000"})


def test_business_kilometres_above_total_kilometres_is_refused() -> None:
    # Business kilometres of 20000 of a total of 10000 would give a business use part of 200% of
    # the vehicle's total expenses (line 12), so the vehicle is refused, naming amounts 1 and 2 of
    # Chart A.
    with pytest.raises(InputAboveBoundError, match=r"item 1: .*amount 1.*amount 2"):
        statement({**LEASED, "business_kilometres": "20000"})


def test_interest_days_above_the_fiscal_period_days_are_refused() -> None:
    # A statement whose fiscal period is 153 days (1 August to 31 December 2025, entered on the
    # statement): the vehicle's 183 days of interest are more days than the period has, so the
    # vehicle is refused, naming both.
    with pytest.raises(InputAboveBoundError, match=r"item 1: (?=.*\b183\b)(?=.*\b153\b)"):
        statement(LEASED, fiscal_period_from=20250801, fiscal_period_to=20251231)


@pytest.mark.parametrize("year_input", ["purchase_year", "lease_year"])
def test_a_purchase_or_lease_year_after_2025_is_refused(year_input: str) -> None:
    # The charts print the limits of 2025 only: a vehicle bought or leased in 2030 would silently
    # get them, so it is refused, naming the year.
    with pytest.raises(InvalidRecordError, match=r"item 1: .*2030 is after 2025"):
        statement({**LEASED, year_input: "2030"})


def test_chart_a_business_use_part_is_rounded_half_up_to_the_cent() -> None:
    # Amount 1 of 1 and amount 2 of 3: 100 x 1 ÷ 3 = 33.333..., which rounds to 33.33 (line 13),
    # and line 16 is 33.33 + 0 + 0.
    worksheet = statement(
        {"business_kilometres": "1", "total_kilometres": "3", "fuel_and_oil": "100"}
    )

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_13 == D("33.33")
    assert line(worksheet, BUSINESS_MOTOR_VEHICLE_EXPENSES) == D("33.33")


def test_chart_a_business_use_part_is_0_when_there_are_no_total_kilometres() -> None:
    # A total of 0 kilometres with 0 business kilometres gives a business use part of 0 (no
    # division), so line 16 is only the parking fees of 300.
    worksheet = statement(
        {"business_kilometres": "0", "total_kilometres": "0", "parking_fees": "300"}
    )

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_13 == D("0")
    assert line(worksheet, BUSINESS_MOTOR_VEHICLE_EXPENSES) == D("300")


# Two vehicles, as in Return BQ (returns/2025_return_bq.yaml): an owned one with Chart B interest
# and a leased one with Chart C leasing.
OWNED: dict[str, str] = {
    "business_kilometres": "7000",
    "total_kilometres": "16000",
    "fuel_and_oil": "1200",
    "insurance": "900",
    "licence_and_registration": "150",
    "maintenance_and_repairs": "450",
    "interest_payable": "600",
    "interest_days": "183",
    "parking_fees": "120",
}
SECOND: dict[str, str] = {
    "business_kilometres": "3000",
    "total_kilometres": "12000",
    "fuel_and_oil": "600",
    "insurance": "450",
    "maintenance_and_repairs": "108",
    "other_expenses_10": "200",
    "lease_charges": "2550",
    "lease_payments_before": "1000",
    "lease_days": "183",
    "list_price": "60000",
    "supplementary_insurance": "60",
}


def test_two_vehicles_give_line_9281_of_the_line_16_amounts_added() -> None:
    # Owned: line 19 is 600 (less than 2135.00), line 12 is 1200 + 600 + 900 + 150 + 450 = 3300,
    # line 13 is 3300 x 7000 / 16000 = 1443.75 and line 16 is 1443.75 + 120 = 1563.75. Leased:
    # line 26 is 7582.30 - 1000 = 6582.30, line 28 is 2147.00, line 12 is 600 + 450 + 108 + 2147 +
    # 200 = 3505, line 13 is 3505 x 3000 / 12000 = 876.25 and line 16 is 876.25 + 60 = 936.25.
    # Line 9281 is 1563.75 + 936.25 = 2500.00; line 9368 is 20000 + 2500 = 22500.
    worksheet = statement(OWNED, SECOND)

    first, second = vehicle_lines(worksheet)
    assert (first.line_12, first.line_13, first.line_19, first.line_28, first.line_16) == (
        D("3300"),
        D("1443.75"),
        D("600"),
        D("0"),
        D("1563.75"),
    )
    assert (second.line_12, second.line_13, second.line_19, second.line_28, second.line_16) == (
        D("3505"),
        D("876.25"),
        D("0"),
        D("2147.00"),
        D("936.25"),
    )
    assert line(worksheet, BUSINESS_MOTOR_VEHICLE_EXPENSES) == D("2500")
    assert line(worksheet, BUSINESS_TOTAL_EXPENSES) == D("22500")


def test_no_vehicles_give_line_9281_of_zero() -> None:
    worksheet = statement()

    assert vehicle_lines(worksheet) == []
    assert line(worksheet, BUSINESS_MOTOR_VEHICLE_EXPENSES) == D("0")
    assert line(worksheet, BUSINESS_TOTAL_EXPENSES) == D("20000")


def test_the_vehicles_trace_names_each_vehicle_then_the_total() -> None:
    worksheet = statement(OWNED, SECOND)

    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    for rendered_line in (
        "business_motor_vehicle_expenses: item 1: line 12 3300, line 13 1443.75, line 19 600, "
        "line 28 0, line 16 1563.75",
        "business_motor_vehicle_expenses: item 2: line 12 3505, line 13 876.25, line 19 0, "
        "line 28 2147, line 16 936.25",
        "business_motor_vehicle_expenses: item 1 1563.75 + item 2 936.25 = 2500",
    ):
        assert rendered_line in rendered, rendered_line
