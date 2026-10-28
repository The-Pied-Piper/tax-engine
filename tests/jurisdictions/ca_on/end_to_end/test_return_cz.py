"""CA-ON 2025 end to end: return cz."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
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
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import BusinessCcaRow, D, run

# Return CZ's T2125, Return BT's with the gross sales raised to 60540 (a chosen figure, so that
# line 9946 stays Return BB's 30000 after the 12540.00 of capital cost allowance below): the six
# expense lines 1500 + 1200 + 800 + 2500 + 6000 + 1500 = 13500 and the motor vehicle expenses of
# 2500 from Charts A to C (the seven lines 16000), and the business-use-of-home expenses 600 + 500
# + 300 + 200 + 400 = 2000.
BUSINESS = {
    "gross_sales": "60540",
    "advertising": "1500",
    "insurance": "1200",
    "office_expenses": "800",
    "professional_fees": "2500",
    "rent": "6000",
    "utilities": "1500",
    "vehicle_sales_tax_rate": "13",
    "home_heat": "600",
    "home_electricity": "500",
    "home_insurance": "300",
    "home_maintenance": "200",
    "home_property_taxes": "400",
}
# Charts A to C for one leased passenger vehicle used half for business, as in Return BT: Chart A
# line 16 (line 9281) is 2500.
VEHICLE = {
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


def class_10_1_row(
    year: int = 2025,
    cost: str = "56500.00",
    assistance: str = "0",
    expensed: str = "12540",
    claim: str = "12540.00",
    class_number: str = "10.1",
) -> BusinessCcaRow:
    """Area A, a passenger vehicle bought in `year` for `cost` (with the HST), `assistance` of
    government assistance received less repaid, sold for 40000, all of it a DIEP's (columns 5 and
    6); capital cost 42940 (38000 + 13%, columns 3 and 4); column 9 `expensed`; the claim
    (column 21) `claim`; no property left (a chosen 1)."""
    return (
        class_number,
        "0",
        "42940",
        "40000",
        "0",
        "0",
        claim,
        1,
        "42940",
        "40000",
        expensed,
        0,
        "0",
        year,
        cost,
        assistance,
    )


def run_cz(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CZ's inputs, as in `returns/2025_return_cz.yaml`: Return BT's sole proprietor with a
    Class 10.1 passenger vehicle bought and sold in 2025 whose cost is above the prescribed amount.

    One T2125 statement for the business: gross sales of 60540 (amount 3A, and so line 8299 and T1
    line 13499), expenses of 16000 on seven lines (the motor vehicle line, 2500, from Charts A to
    C) and 12540.00 of capital cost allowance (the vehicle's immediate expensing amount), 28540.00
    in all (line 9368), so line 9369 is 32000.00; business-use-of-home expenses of 2000, so line
    9945 is 2000 and line 9946 and T1 line 13500 are 30000.00, Return BT's.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (class_10_1_row(),),
        "business_vehicles_rows": (VEHICLE,),
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


def statement_cz(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CZ's one T2125 statement: its lines, as the form computes them."""
    return run_cz(changes)["ca/t2125"][0]


def adjusted_proceeds(statement: Worksheet) -> list[tuple[Any, Any, Any]]:
    """Class number, column 5 and column 6 of each row of the adjusted Area A list."""
    value = statement.get(BUSINESS_CCA_CLASSES_ADJUSTED).value
    return [
        (record[CCA_CLASS_NUMBER], record[CCA_PROCEEDS], record[CCA_DIEP_PROCEEDS])
        for record in value.records
    ]


def test_return_czs_proceeds_are_adjusted_by_the_prescribed_amount_over_the_actual_cost() -> None:
    # Area A endnote 2: the vehicle was bought in 2025, so the prescribed amount is 38000 plus the
    # HST of 13% (4940), 42940.00; the actual cost is 56500.00 - 0 = 56500.00, more than that, so
    # the proceeds of 40000 (column 5, all of it column 6) are adjusted by the factor 42940.00 /
    # 56500.00 = 0.76: 40000 x 0.76 = 30400.00 each.
    statement = statement_cz()

    assert adjusted_proceeds(statement) == [(D("10.1"), D("30400.00"), D("30400.00"))]


def test_return_czs_trace_names_the_adjustment() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_cz().trace)

    assert (
        "business_cca_classes_adjusted: item 1: proceeds 40000 and DIEP proceeds 40000 adjusted by "
        "prescribed amount 42940 / actual cost 56500 = proceeds 30400 and DIEP proceeds 30400"
    ) in rendered


def test_return_czs_column_8_is_the_adjusted_12540_so_column_9_can_be_the_whole_of_it() -> None:
    # Column 7 is 0 + 42940 - 30400.00 = 12540.00; column 8 is column 4 minus column 6, 42940 -
    # 30400.00 = 12540.00, not more than column 7; column 9 is a chosen 12540, not more than
    # column 8; line i is 12540.
    statement = statement_cz()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("12540")
    assert (
        "business_immediate_expensing_claim: item 1 class 10.1: column 4 42940 less column 6 "
        "30400, column 7 12540: column 8 12540, column 9 12540"
    ) in rendered


def test_return_czs_column_9_would_be_refused_above_the_unadjusted_column_8() -> None:
    # Without the adjustment (the row marked as not a vehicle for immediate expensing, year 0),
    # column 8 is 42940 - 40000 = 2940, below the 12540 of column 9.
    with pytest.raises(InvalidRecordError) as raised:
        run_cz({"business_cca_classes_rows": (class_10_1_row(year=0, cost="0"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: column 9 (12540) is above column 8 (2940)"
    )


def test_return_czs_class_closes_at_zero_with_no_recapture_or_terminal_loss() -> None:
    # No property is left in the class and column 7 is positive, so the maximum is 0 and column
    # 21 is 0 + column 9 = 12540.00; column 22 is 0; the terminal loss (column 7 less column 9)
    # and the recapture are 0.
    statement = statement_cz()

    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("10.1"), D("0")),
    ]
    assert statement.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert statement.get(BUSINESS_RECAPTURED_CCA).value == D("0")


def test_return_czs_line_ii_and_line_9936_are_12540_and_line_9369_is_32000() -> None:
    # Line ii, the total of column 21, is 12540.00, so is line 9936. Line 9368 is 16000 + 12540.00
    # + 0 = 28540.00 and line 9369 is 60540 - 28540.00 = 32000.00; the income before CCA
    # (endnote 5) is 32000.00 + 12540.00 = 44540.00, above the 12540 of line i; the business is
    # not associated with another EPOP, so the limit is 1500000.
    statement = statement_cz()

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("12540.00")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("12540.00")
    assert statement.get(BUSINESS_TOTAL_EXPENSES).value == D("28540.00")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000.00")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("44540.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")


def test_return_czs_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    result = run_cz()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_czs_figures_that_depend_on_income_are_return_bbs() -> None:
    # Line 9946 is Return BB's 30000.00: the federal tax 30000.00 x 14.5% = 4350.00, the Ontario
    # tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57, as in Return BT.
    worksheet = run_cz()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_cost_at_the_prescribed_amount_with_tax_leaves_the_proceeds() -> None:
    # "whose cost is more than the prescribed amount": a cost of 42940.00 is not more than 42940.00,
    # so column 5 and 6 stay 40000; column 8 is 42940 - 40000 = 2940, the most of column 9.
    statement = statement_cz(
        {
            "business_cca_classes_rows": (
                class_10_1_row(cost="42940.00", expensed="2940", claim="2940.00"),
            )
        }
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("40000"), D("40000"))]
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("2940")


def test_government_assistance_received_brings_the_actual_cost_to_the_prescribed_amount() -> None:
    # "you will have to adjust the actual cost of the vehicle for any payments or repayments of
    # government assistance": 56500.00 - 13560.00 = 42940.00, not more than the prescribed amount.
    statement = statement_cz(
        {
            "business_cca_classes_rows": (
                class_10_1_row(assistance="13560.00", expensed="2940", claim="2940.00"),
            )
        }
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("40000"), D("40000"))]


def test_government_assistance_repaid_raises_the_actual_cost() -> None:
    # A repayment is negative: 42940.00 - (-7060.00) = 50000.00, over 42940.00, so the factor is
    # 42940.00 / 50000.00 = 0.8588 and the proceeds are 40000 x 0.8588 = 34352.00; column 8 is
    # 42940 - 34352.00 = 8588.00.
    statement = statement_cz(
        {
            "business_cca_classes_rows": (
                class_10_1_row(
                    cost="42940.00", assistance="-7060.00", expensed="8588", claim="8588.00"
                ),
            )
        }
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("34352.00"), D("34352.00"))]
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("8588")


def test_a_vehicle_acquired_in_2022_has_the_prescribed_amount_of_2022() -> None:
    # 34000 + 13% = 38420.00; 40000 x 38420.00 / 56500.00 = 27200.00 (0.68 exactly); column 8 is
    # 42940 - 27200.00 = 15740.00.
    statement = statement_cz(
        {
            "business_cca_classes_rows": (
                class_10_1_row(year=2022, expensed="15740", claim="15740.00"),
            )
        }
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("27200.00"), D("27200.00"))]


def test_a_vehicle_acquired_before_2021_is_refused() -> None:
    # A DIEP is acquired after April 18, 2021: nothing is printed for 2020.
    with pytest.raises(InvalidRecordError, match=r"^ca/t2125, instance 1: item 1: .*2020"):
        run_cz({"business_cca_classes_rows": (class_10_1_row(year=2020),)})


def test_a_year_on_a_row_of_another_class_is_refused() -> None:
    # Only Class 10.1 is adjusted (Class 54 is not modelled): a year on a Class 8 row is refused.
    with pytest.raises(InvalidRecordError, match=r"^ca/t2125, instance 1: item 1: .*10\.1"):
        run_cz({"business_cca_classes_rows": (class_10_1_row(class_number="8"),)})


def test_the_year_of_the_row_is_not_part_of_the_adjusted_list() -> None:
    fields = statement_cz().get(BUSINESS_CCA_CLASSES_ADJUSTED).value.fields

    assert CCA_VEHICLE_ACQUIRED_YEAR not in fields
