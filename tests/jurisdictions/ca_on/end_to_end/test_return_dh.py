"""CA-ON 2025 end to end: return dh."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_CLASSES_ADJUSTED,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIM,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT,
    BUSINESS_INCOME,
    BUSINESS_INCOME_BEFORE_CCA,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_RECAPTURED_CCA,
    BUSINESS_TERMINAL_LOSS,
    BUSINESS_TOTAL_EXPENSES,
    CCA_CLASS_NUMBER,
    CCA_DIEP_PROCEEDS,
    CCA_PROCEEDS,
    CCA_UCC_AT_END,
    CCA_VEHICLE_ACQUIRED_YEAR,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import BusinessCcaRow, D, SoldZepvRow, run

# Return DH's T2125, Return BT's without Charts A to C and with the gross sales raised to 60500 (a
# chosen figure, so that line 9946 stays Return BB's 30000 after the 15000.00 of capital cost
# allowance below): the six expense lines 1500 + 1200 + 800 + 2500 + 6000 + 1500 = 13500, no motor
# vehicle expenses, and the business-use-of-home expenses 600 + 500 + 300 + 200 + 400 = 2000. The
# sales tax rate is a chosen 0, so the prescribed amounts of Class 54 are the printed ones.
BUSINESS = {
    "gross_sales": "60500",
    "advertising": "1500",
    "insurance": "1200",
    "office_expenses": "800",
    "professional_fees": "2500",
    "rent": "6000",
    "utilities": "1500",
    "vehicle_sales_tax_rate": "0",
    "home_heat": "600",
    "home_electricity": "500",
    "home_insurance": "300",
    "home_maintenance": "200",
    "home_property_taxes": "400",
}

# Guide T4036 2025, "Class 54 (30%)": car A, acquired in 2024 for 65000 and sold for 30000, is over
# the limit of 61000 ("after December 31, 2022"); car B, acquired in 2022 for 50000 and sold for
# 20000, is under the limit of 59000. The vehicles are (year, cost, assistance, proceeds, the DIEP
# part of the proceeds).
CAR_A: SoldZepvRow = (2024, "65000", "0", "30000", "0")
CAR_B: SoldZepvRow = (2022, "50000", "0", "20000", "0")


def class_54_row(
    *sold: SoldZepvRow,
    class_number: str = "54",
    proceeds: str = "0",
    year: int = 0,
    cost: str = "0",
) -> BusinessCcaRow:
    """Area A, a Class 54 row: column 2 a chosen 100000, no additions, `proceeds` an amount entered
    in column 5 (0 unless the test exercises the refusal), the vehicles `sold` listed on the row,
    the claim (column 21) a chosen 15000.00, property left in the class; and the year and cost of a
    Class 10.1 vehicle, 0 for none."""
    return (
        class_number,
        "100000",
        "0",
        proceeds,
        "0",
        "0",
        "15000.00",
        0,
        "0",
        "0",
        "0",
        0,
        "0",
        year,
        cost,
        "0",
        sold,
    )


def run_dh(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return DH's inputs, as in `returns/2025_return_dh.yaml`: Return BT's sole proprietor with a
    Class 54 row that sold two zero-emission passenger vehicles in 2025, one of them over the
    prescribed amount.

    One T2125 statement for the business: gross sales of 60500 (amount 3A, and so line 8299 and T1
    line 13499), expenses of 13500 on six lines and 15000.00 of capital cost allowance, 28500.00
    in all (line 9368), so line 9369 is 32000.00; business-use-of-home expenses of 2000, so line
    9945 is 2000 and line 9946 and T1 line 13500 are 30000.00, Return BT's.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (class_54_row(CAR_A, CAR_B),),
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_dh(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return DH's one T2125 statement: its lines, as the form computes them."""
    return run_dh(changes)["ca/t2125"][0]


def rows_dh(*rows: BusinessCcaRow) -> Worksheet:
    """The worksheet of Return DH's statement with `rows` as the Area A rows."""
    return statement_dh({"business_cca_classes_rows": rows})


def adjusted_proceeds(statement: Worksheet) -> list[tuple[Any, Any, Any]]:
    """Class number, column 5 and column 6 of each row of the adjusted Area A list."""
    value = statement.get(BUSINESS_CCA_CLASSES_ADJUSTED).value
    return [
        (record[CCA_CLASS_NUMBER], record[CCA_PROCEEDS], record[CCA_DIEP_PROCEEDS])
        for record in value.records
    ]


def test_return_dhs_proceeds_are_each_vehicles_scaled_and_summed() -> None:
    # Area A endnote 2 and Guide T4036 "Class 54 (30%)": car A was acquired in 2024, so its
    # prescribed amount is 61000 (plus the sales tax, a chosen 0%); its actual cost is 65000 - 0 =
    # 65000, more than that, so its proceeds of 30000 are adjusted by the factor 61000 / 65000:
    # 30000 x 61000 / 65000 = 28153.846..., 28153.85 to the cent. Car B was acquired in 2022
    # (59000) for 50000, not more than that, so its 20000 stays. Column 5 is 0 + 28153.85 +
    # 20000 = 48153.85; no DIEP, so column 6 is 0.
    statement = statement_dh()

    assert adjusted_proceeds(statement) == [(D("54"), D("48153.85"), D("0"))]


def test_return_dhs_trace_names_each_vehicle() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_dh().trace)

    assert (
        "business_cca_classes_adjusted: item 1 vehicle 1: proceeds 30000 and DIEP proceeds 0 "
        "adjusted by prescribed amount 61000 / actual cost 65000 = proceeds 28153.85 and DIEP "
        "proceeds 0"
    ) in rendered
    assert (
        "business_cca_classes_adjusted: item 1 vehicle 2: proceeds 20000 and DIEP proceeds 0 "
        "not adjusted"
    ) in rendered


def test_return_dhs_class_closes_at_36846_15_with_no_recapture_or_terminal_loss() -> None:
    # Column 7 is 100000 + 0 - 48153.85 = 51846.15, positive with property left in the class; the
    # claim (column 21) is a chosen 15000.00, not more than 30% of column 19, 15553.845; column 22
    # is 51846.15 - 15000.00 = 36846.15.
    statement = statement_dh()

    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("54"), D("36846.15")),
    ]
    assert statement.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert statement.get(BUSINESS_RECAPTURED_CCA).value == D("0")


def test_return_dhs_line_ii_and_line_9936_are_15000_and_line_9369_is_32000() -> None:
    # Line ii, the total of column 21, is 15000.00, so is line 9936. Line 9368 is 13500 + 15000.00
    # + 0 = 28500.00 and line 9369 is 60500 - 28500.00 = 32000.00; the income before CCA
    # (endnote 5) is 32000.00 + 15000.00 = 47000.00; no class has a DIEP, so line i is 0 and the
    # business is not associated with another EPOP, so the limit is 1500000.
    statement = statement_dh()

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("15000.00")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("15000.00")
    assert statement.get(BUSINESS_TOTAL_EXPENSES).value == D("28500.00")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000.00")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("47000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("0")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")


def test_return_dhs_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    result = run_dh()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_dhs_figures_that_depend_on_income_are_return_bbs() -> None:
    # Line 9946 is Return BB's 30000.00: the federal tax 30000.00 x 14.5% = 4350.00, the Ontario
    # tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57, as in Return BT.
    worksheet = run_dh()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_car_at_the_prescribed_amount_leaves_the_proceeds() -> None:
    # "whose cost is more than the prescribed amount": a cost of 61000 is not more than 61000, so
    # car A's 30000 stays; column 5 is 30000 + 20000 = 50000 and column 22 is 50000 - 15000.00 =
    # 35000.00.
    car = (2024, "61000", "0", "30000", "0")

    statement = rows_dh(class_54_row(car, CAR_B))

    assert adjusted_proceeds(statement) == [(D("54"), D("50000"), D("0"))]
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [record[CCA_UCC_AT_END] for record in records] == [D("35000.00")]


def test_government_assistance_received_brings_the_actual_cost_to_the_prescribed_amount() -> None:
    # "you will have to adjust the actual cost of the vehicle for any payments or repayments of
    # government assistance": 65000 - 4000 = 61000, not more than the prescribed amount.
    car = (2024, "65000", "4000", "30000", "0")

    statement = rows_dh(class_54_row(car, CAR_B))

    assert adjusted_proceeds(statement) == [(D("54"), D("50000"), D("0"))]


def test_a_car_of_year_0_is_not_adjusted() -> None:
    # Year 0: the rule does not apply to the car (not sold at arm's length, say), so its 30000
    # stays.
    car = (0, "0", "0", "30000", "0")

    statement = rows_dh(class_54_row(car, CAR_B))

    assert adjusted_proceeds(statement) == [(D("54"), D("50000"), D("0"))]


def test_an_amount_entered_in_column_5_of_a_class_54_row_is_refused() -> None:
    with pytest.raises(
        InvalidRecordError,
        match=r"^ca/t2125, instance 1: item 1: .*must be listed as a vehicle$",
    ):
        rows_dh(class_54_row(CAR_A, CAR_B, proceeds="1000"))


def test_a_car_acquired_before_2019_is_refused() -> None:
    # Class 54 is for vehicles "acquired after March 18, 2019": nothing is printed for 2018.
    with pytest.raises(
        InvalidRecordError, match=r"^ca/t2125, instance 1: item 1 vehicle 2: .*2018"
    ):
        rows_dh(class_54_row(CAR_A, (2018, "65000", "0", "30000", "0")))


def test_sold_cars_on_a_row_of_another_class_are_refused() -> None:
    # Only a Class 54 row holds the list of sold vehicles.
    with pytest.raises(InvalidRecordError, match=r"^ca/t2125, instance 1: item 1 vehicle 1: .*54"):
        rows_dh(class_54_row(CAR_A, class_number="8"))


def test_a_year_on_the_class_54_row_is_refused_as_a_class_10_1_vehicle() -> None:
    with pytest.raises(InvalidRecordError, match=r"^ca/t2125, instance 1: item 1: .*10\.1"):
        rows_dh(class_54_row(year=2024, cost="65000"))


def test_the_sold_cars_are_not_part_of_the_adjusted_list() -> None:
    fields = statement_dh().get(BUSINESS_CCA_CLASSES_ADJUSTED).value.fields

    assert CCA_VEHICLE_ACQUIRED_YEAR not in fields
    assert len(fields) == 14
