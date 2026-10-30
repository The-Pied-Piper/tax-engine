"""CA-ON 2025 end to end: return db."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_DIEP_PROCEEDS,
    CCA_PROCEEDS,
    CCA_UCC_AT_END,
    CCA_VEHICLE_ACQUIRED_YEAR,
    FEDERAL_BASIC_TAX,
    FISH_CCA_CLAIM,
    FISH_CCA_CLASSES_ADJUSTED,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_IMMEDIATE_EXPENSING_CLAIM,
    FISH_IMMEDIATE_EXPENSING_LIMIT,
    FISH_INCOME_BEFORE_CCA,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_RECAPTURED_CCA,
    FISH_TERMINAL_LOSS,
    FISH_TOTAL_EXPENSES,
    FISHING_INCOME,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, FishCcaRow, run

# Return DB's T2121, Return BY's fishing business with the fish products raised to 52540 (a chosen
# figure, so that line 9369 stays Return BY's 15000 after the 12540.00 of capital cost allowance
# below): expenses of 25000 on two lines (salt, bait and ice 10000, fishing gear 15000), with no
# partner and no business-use-of-home expenses.
FISH = {
    "fish_products": "52540",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "15000",
    "vehicle_sales_tax_rate": "13",
}
# Charts A to C for one leased passenger vehicle used for no fishing, as in Return BY.
VEHICLE = {
    "business_kilometres": "0",
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
# Area G and endnote 5: associated with one other EPOP (1) under an agreement that was filed (1),
# the percentage assigned to the business 40 and the total of column 3 100, so amount iii is
# 1500000 x 40% = 600000.00; no amount allocated by the minister.
AREA_G = {
    "fish_epop_associated": 1,
    "fish_epop_agreement_filed": 1,
    "fish_epop_percentage": "40",
    "fish_epop_percentage_total": "100",
}


def class_10_1_row(
    year: int = 2025,
    cost: str = "56500.00",
    assistance: str = "0",
    expensed: str = "12540",
    claim: str = "12540.00",
    class_number: str = "10.1",
) -> FishCcaRow:
    """Area A, a passenger vehicle bought in `year` for `cost` (with the HST), `assistance` of
    government assistance received less repaid, sold for 40000, all of it a DIEP's (columns 5 and
    6); capital cost 42940 (38000 + 13%, columns 3 and 4); column 9 `expensed`; the claim
    (column 21) `claim`; no property left (a chosen 1); the remaining personal part 0."""
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
        "0",
        year,
        cost,
        assistance,
    )


def run_db(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return DB's inputs, as in `returns/2025_return_db.yaml`: Return BY's sole proprietor with a
    Class 10.1 passenger vehicle bought and sold in 2025 whose cost is above the prescribed amount.

    One T2121 statement for the fishing business: income of 52540 (line 8299 and T1 line 14299),
    expenses of 25000 (4Q) and 12540.00 of capital cost allowance (the vehicle's immediate expensing
    amount), 37540.00 in all (line 9368), so line 9369 is 15000.00, which is line 9946 and T1 line
    14300, Return BY's.
    """
    statement: dict[str, Any] = {
        "fish": FISH,
        "fish_cca_classes_rows": (class_10_1_row(),),
        "fish_vehicles_rows": (VEHICLE,),
        **AREA_G,
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        fish_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_db(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return DB's one T2121 statement: its lines, as the form computes them."""
    return run_db(changes)["ca/t2121"][0]


def adjusted_proceeds(statement: Worksheet) -> list[tuple[Any, Any, Any]]:
    """Class number, column 5 and column 6 of each row of the adjusted Area A list."""
    value = statement.get(FISH_CCA_CLASSES_ADJUSTED).value
    return [
        (record[CCA_CLASS_NUMBER], record[CCA_PROCEEDS], record[CCA_DIEP_PROCEEDS])
        for record in value.records
    ]


def test_return_dbs_proceeds_are_adjusted_by_the_prescribed_amount_over_the_actual_cost() -> None:
    # Area A endnote 2: the vehicle was bought in 2025, so the prescribed amount is 38000 plus the
    # HST of 13% (4940), 42940.00; the actual cost is 56500.00 - 0 = 56500.00, more than that, so
    # the proceeds of 40000 (column 5, all of it column 6) are adjusted by the factor 42940.00 /
    # 56500.00 = 0.76: 40000 x 0.76 = 30400.00 each.
    statement = statement_db()

    assert adjusted_proceeds(statement) == [(D("10.1"), D("30400.00"), D("30400.00"))]


def test_return_dbs_trace_names_the_adjustment() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_db().trace)

    assert (
        "fish_cca_classes_adjusted: item 1: proceeds 40000 and DIEP proceeds 40000 adjusted by "
        "prescribed amount 42940 / actual cost 56500 = proceeds 30400 and DIEP proceeds 30400"
    ) in rendered


def test_return_dbs_column_8_is_the_adjusted_12540_so_column_9_can_be_the_whole_of_it() -> None:
    # Column 7 is 0 + 42940 - 30400.00 = 12540.00; column 8 is column 4 minus column 6, 42940 -
    # 30400.00 = 12540.00, not more than column 7; column 9 is a chosen 12540, not more than
    # column 8; line i is 12540.
    statement = statement_db()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("12540")
    assert (
        "fish_immediate_expensing_claim: item 1 class 10.1: column 4 42940 less column 6 "
        "30400, column 7 12540: column 8 12540, column 9 12540"
    ) in rendered


def test_return_dbs_column_9_would_be_refused_above_the_unadjusted_column_8() -> None:
    # Without the adjustment (the row marked as not a vehicle for immediate expensing, year 0),
    # column 8 is 42940 - 40000 = 2940, below the 12540 of column 9.
    with pytest.raises(InvalidRecordError) as raised:
        run_db({"fish_cca_classes_rows": (class_10_1_row(year=0, cost="0"),)})

    assert str(raised.value) == (
        "ca/t2121, instance 1: item 1: column 9 (12540) is above column 8 (2940)"
    )


def test_return_dbs_class_closes_at_zero_with_no_recapture_or_terminal_loss() -> None:
    # No property is left in the class and column 7 is positive, so the maximum is 0 and column
    # 21 is 0 + column 9 = 12540.00; column 22 is 0; the terminal loss (column 7 less column 9)
    # and the recapture are 0.
    statement = statement_db()

    records = statement.get(FISH_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("10.1"), D("0")),
    ]
    assert statement.get(FISH_TERMINAL_LOSS).value == D("0")
    assert statement.get(FISH_RECAPTURED_CCA).value == D("0")


def test_return_dbs_line_ii_and_line_9936_are_12540_and_line_9369_is_15000() -> None:
    # Line ii, the total of column 21, is 12540.00, so is line 9936. Line 9368 is 25000 + 12540.00
    # = 37540.00 and line 9369 is 52540 - 37540.00 = 15000.00; the income before CCA (endnote 5) is
    # 15000.00 + 12540.00 = 27540.00, above the 12540 of line i; the business is associated with one
    # other EPOP under a filed agreement, so the limit is 1500000 x 40% = 600000.00.
    statement = statement_db()

    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("12540.00")
    assert statement.get(FISH_CCA_CLAIM).value == D("12540.00")
    assert statement.get(FISH_TOTAL_EXPENSES).value == D("37540.00")
    assert statement.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("15000.00")
    assert statement.get(FISH_INCOME_BEFORE_CCA).value == D("27540.00")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")


def test_return_dbs_net_fishing_income_is_15000_on_line_9946_and_t1_line_14300() -> None:
    result = run_db()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2121"][0].get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("15000.00")
    assert worksheet.get(FISHING_INCOME).value == D("15000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("15000.00")


def test_return_dbs_figures_that_depend_on_income_are_return_bys() -> None:
    # Line 9946 is Return BY's 15000.00: the federal tax 15000.00 x 14.5% = 2175.00, the Ontario
    # tax 15000.00 x 5.05% = 757.50 and the total payable 0.00, as in Return BY.
    worksheet = run_db()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("15000.00")
    assert worksheet.get(NET_INCOME).value == D("15000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("15000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("2175.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("757.50")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0.00")
    # The Canada workers benefit of 1633.00 (27% of the working income over 3000.00 is capped
    # at 1633.00, and the adjusted family net income is under 26855.00) is a refund: the
    # total payable of 0.00 less 1633.00 is -1633.00.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1633.00")


def test_a_cost_at_the_prescribed_amount_with_tax_leaves_the_proceeds() -> None:
    # "whose cost is more than the prescribed amount": a cost of 42940.00 is not more than 42940.00,
    # so column 5 and 6 stay 40000; column 8 is 42940 - 40000 = 2940, the most of column 9.
    statement = statement_db(
        {
            "fish_cca_classes_rows": (
                class_10_1_row(cost="42940.00", expensed="2940", claim="2940.00"),
            )
        }
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("40000"), D("40000"))]
    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("2940")


def test_government_assistance_received_brings_the_actual_cost_to_the_prescribed_amount() -> None:
    # "you will have to adjust the actual cost of the vehicle for any payments or repayments of
    # government assistance": 56500.00 - 13560.00 = 42940.00, not more than the prescribed amount.
    statement = statement_db(
        {
            "fish_cca_classes_rows": (
                class_10_1_row(assistance="13560.00", expensed="2940", claim="2940.00"),
            )
        }
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("40000"), D("40000"))]


def test_government_assistance_repaid_raises_the_actual_cost() -> None:
    # A repayment is negative: 42940.00 - (-7060.00) = 50000.00, over 42940.00, so the factor is
    # 42940.00 / 50000.00 = 0.8588 and the proceeds are 40000 x 0.8588 = 34352.00; column 8 is
    # 42940 - 34352.00 = 8588.00.
    statement = statement_db(
        {
            "fish_cca_classes_rows": (
                class_10_1_row(
                    cost="42940.00", assistance="-7060.00", expensed="8588", claim="8588.00"
                ),
            )
        }
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("34352.00"), D("34352.00"))]
    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("8588")


def test_a_vehicle_acquired_in_2022_has_the_prescribed_amount_of_2022() -> None:
    # 34000 + 13% = 38420.00; 40000 x 38420.00 / 56500.00 = 27200.00 (0.68 exactly); column 8 is
    # 42940 - 27200.00 = 15740.00.
    statement = statement_db(
        {"fish_cca_classes_rows": (class_10_1_row(year=2022, expensed="15740", claim="15740.00"),)}
    )

    assert adjusted_proceeds(statement) == [(D("10.1"), D("27200.00"), D("27200.00"))]


def test_a_vehicle_acquired_before_2021_is_refused() -> None:
    # A DIEP is acquired after April 18, 2021: nothing is printed for 2020.
    with pytest.raises(InvalidRecordError, match=r"^ca/t2121, instance 1: item 1: .*2020"):
        run_db({"fish_cca_classes_rows": (class_10_1_row(year=2020),)})


def test_a_year_on_a_row_of_another_class_is_refused() -> None:
    # Only Class 10.1 is adjusted (Class 54 is not modelled): a year on a Class 8 row is refused.
    with pytest.raises(InvalidRecordError, match=r"^ca/t2121, instance 1: item 1: .*10\.1"):
        run_db({"fish_cca_classes_rows": (class_10_1_row(class_number="8"),)})


def test_the_year_of_the_row_is_not_part_of_the_adjusted_list() -> None:
    fields = statement_db().get(FISH_CCA_CLASSES_ADJUSTED).value.fields

    assert CCA_VEHICLE_ACQUIRED_YEAR not in fields
