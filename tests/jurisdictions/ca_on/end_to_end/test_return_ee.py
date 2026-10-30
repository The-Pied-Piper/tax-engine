"""CA-ON 2025 end to end: return ee, Form T777 Parts A and B (capital cost allowance for employees).

Return EE (returns/2025_return_ee.yaml) carries the examples of the T777 schedule together: a
Class 8 row
(line 13), a Class 54 zero-emission vehicle that is an AIIP (the vehicle list of Part A) and a Class
10.1 vehicle owned all year (Part B). Line 25 is the vehicle rows plus the Part B total.

Each example below runs the form alone, with the rows it needs, and reads the form's exports:
line 13, line 25 and the closing UCC of Parts A and B. The columns of T777 (7 to 16 of Part A, 5, 7
and 8 of Part B) are computed inside the form and are checked through those exports. The Class 54
row follows the proceeds rule for sold vehicles: its proceeds come only from its sold-vehicle list.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_NO_PROPERTY_LEFT,
    CCA_PROCEEDS,
    CCA_RIIP_ADDITIONS,
    CCA_UCC_AT_END,
    CCA_UCC_AT_START,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    T777_CLASS_8_CLOSING_UCC,
    T777_CLASS_8_ROWS,
    T777_LINE_13,
    T777_LINE_25,
    T777_MUSICIAN_EMPLOYMENT_INCOME,
    T777_PART_B_CLOSING_UCC,
    T777_PART_B_ROWS,
    T777_VEHICLE_CLOSING_UCC,
    T777_VEHICLE_ROWS,
    T777_VEHICLE_SALES_TAX_RATE,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, sold_zepvs, starting

Row = Mapping[Any, str]

# The "Date acquired" (its year) and "Cost of vehicle" a Part B row must have (the form prints them
# on every row, so they are required): a Class 10.1 vehicle acquired in 2024 for $37,000.01.
DATED: Row = {CCA_VEHICLE_ACQUIRED_YEAR: "2024", CCA_VEHICLE_COST: "37000.01"}


def rows(kind: RecordListKind, *records: Row) -> Artifact[RecordList]:
    """One record of the row list `kind` for each mapping of its columns (by kind): the columns the
    mapping does not give are 0, and the nested list of sold vehicles is empty."""
    built: list[dict[Any, object]] = []
    for record in records:
        assert set(record) <= set(kind.fields), kind.identifier
        entry: dict[Any, object] = {}
        for field in kind.fields:
            if isinstance(field, RecordListKind):
                entry[field] = sold_zepvs(field)
            elif field in record:
                entry[field] = int(record[field]) if field.value_type is int else D(record[field])
            else:
                entry[field] = 0 if field.value_type is int else D(0)
        built.append(entry)
    return Artifact(kind, RecordList(kind.fields, built))


def run(
    *,
    class_8: Sequence[Row] = (),
    vehicles: Sequence[Row] = (),
    part_b: Sequence[Row] = (),
    sales_tax_rate: str = "13",
    musician_income: str = "60000",
) -> Worksheet:
    """The worksheet of Form T777 for the three row lists, the rate of the Class 54 sale and the
    income as a musician (the limit of the musical instrument expenses of Guide T4044 "Part 2");
    the return's employment income is that income and it has no other income."""
    # `starting` gives the five T777 inputs blank; this run gives its own, so they are left out.
    t777_kinds = {
        T777_CLASS_8_ROWS,
        T777_MUSICIAN_EMPLOYMENT_INCOME,
        T777_VEHICLE_ROWS,
        T777_PART_B_ROWS,
        T777_VEHICLE_SALES_TAX_RATE,
    }
    artifacts = [
        each
        for each in starting(musician_income, (), "0", "0", "0", "0", "0")
        if each.kind not in t777_kinds
    ]
    inputs: list[Artifact[Any]] = [
        rows(T777_CLASS_8_ROWS, *class_8),
        rows(T777_VEHICLE_ROWS, *vehicles),
        rows(T777_PART_B_ROWS, *part_b),
        Artifact(T777_VEHICLE_SALES_TAX_RATE, D(sales_tax_rate)),
        Artifact(T777_MUSICIAN_EMPLOYMENT_INCOME, D(musician_income)),
    ]
    result = service().compute(CA_ON, 2025, *artifacts, *inputs)
    (worksheet,) = result["ca/t777"]
    return worksheet


def closing(worksheet: Worksheet, kind: RecordListKind) -> dict[Decimal, Decimal]:
    """The closing UCC of a closing list, by class number."""
    return {
        record[CCA_CLASS_NUMBER]: record[CCA_UCC_AT_END]
        for record in worksheet.get(kind).value.records
    }


# --- the acceptance examples -------------------------------------------------------------------


def test_a_class_8_row_gives_line_13_of_250_and_a_closing_ucc_of_1250() -> None:
    # Column 7 is 1,000.00 + 500.00 = 1,500.00; column 12 is 500.00 / 2 = 250.00; column 13 is
    # 1,250.00; column 15 is 20% of it, 250.00; column 16 is 1,500.00 - 250.00 = 1,250.00.
    worksheet = run(
        class_8=[
            {
                CCA_CLASS_NUMBER: "8",
                CCA_UCC_AT_START: "1000",
                CCA_ADDITIONS: "500",
                CCA_CLAIMED: "250",
            }
        ]
    )

    assert worksheet.get(T777_LINE_13).value == D("250.00")
    assert worksheet.get(T777_LINE_25).value == D("0")
    assert closing(worksheet, T777_CLASS_8_CLOSING_UCC) == {D("8"): D("1250.00")}


def test_a_class_54_zev_aiip_row_adds_one_and_a_half_times_its_cost_to_the_base() -> None:
    # Column 7 is 40,000.00; column 9 is (40,000.00 - 0) x 1 1/2 = 60,000.00 (the AIIP factor of
    # Class 54); column 13 is 100,000.00; column 15 is 30% of it, 30,000.00; column 16 is
    # 40,000.00 - 30,000.00 = 10,000.00. The same row is the T2125 Area A row of the shared dataset
    # (`ca/cca_class_rates`, Class 54), which the vehicle dataset matches.
    worksheet = run(
        vehicles=[
            {
                CCA_CLASS_NUMBER: "54",
                CCA_ADDITIONS: "40000",
                CCA_AIIP_ADDITIONS: "40000",
                CCA_CLAIMED: "30000",
            }
        ]
    )

    assert worksheet.get(T777_LINE_25).value == D("30000.00")
    assert worksheet.get(T777_LINE_13).value == D("0")
    assert closing(worksheet, T777_VEHICLE_CLOSING_UCC) == {D("54"): D("10000.00")}


def test_a_class_10_1_vehicle_owned_all_year_claims_30_percent_of_its_ucc() -> None:
    # Column 5 is the amount of column 2 (note (11)), 20,000.00; column 7 is 30%, 6,000.00; column 8
    # is 20,000.00 - 6,000.00 = 14,000.00.
    worksheet = run(
        part_b=[{**DATED, CCA_CLASS_NUMBER: "10.1", CCA_UCC_AT_START: "20000", CCA_CLAIMED: "6000"}]
    )

    assert worksheet.get(T777_LINE_25).value == D("6000.00")
    assert worksheet.get(T777_LINE_13).value == D("0")
    assert closing(worksheet, T777_PART_B_CLOSING_UCC) == {D("10.1"): D("14000.00")}


def test_line_25_is_the_vehicle_rows_plus_the_part_b_total() -> None:
    # The Class 54 row gives 30,000.00 and the Class 10.1 vehicle 6,000.00: 36,000.00 in all.
    worksheet = run(
        vehicles=[
            {
                CCA_CLASS_NUMBER: "54",
                CCA_ADDITIONS: "40000",
                CCA_AIIP_ADDITIONS: "40000",
                CCA_CLAIMED: "30000",
            }
        ],
        part_b=[
            {**DATED, CCA_CLASS_NUMBER: "10.1", CCA_UCC_AT_START: "20000", CCA_CLAIMED: "6000"}
        ],
    )

    assert worksheet.get(T777_LINE_25).value == D("36000.00")


def test_the_worked_return_examples_together_give_250_on_line_13_and_36000_on_line_25() -> None:
    worksheet = run(
        class_8=[
            {
                CCA_CLASS_NUMBER: "8",
                CCA_UCC_AT_START: "1000",
                CCA_ADDITIONS: "500",
                CCA_CLAIMED: "250",
            }
        ],
        vehicles=[
            {
                CCA_CLASS_NUMBER: "54",
                CCA_ADDITIONS: "40000",
                CCA_AIIP_ADDITIONS: "40000",
                CCA_CLAIMED: "30000",
            }
        ],
        part_b=[
            {**DATED, CCA_CLASS_NUMBER: "10.1", CCA_UCC_AT_START: "20000", CCA_CLAIMED: "6000"}
        ],
    )

    assert worksheet.get(T777_LINE_13).value == D("250.00")
    assert worksheet.get(T777_LINE_25).value == D("36000.00")


# --- the Class 10.1 vehicles -------------------------------------------------------------------


def test_a_class_10_1_vehicle_bought_and_sold_in_the_year_has_no_base_cca_or_closing_ucc() -> None:
    # Note (11): "If you bought and sold a Class 10.1 vehicle in the current year, enter "0" in
    # column 5." Column 5 is 0, so the CCA and the closing UCC are 0.
    worksheet = run(
        part_b=[
            {
                **DATED,
                CCA_CLASS_NUMBER: "10.1",
                CCA_ADDITIONS: "30000",
                CCA_PROCEEDS: "30000",
                CCA_CLAIMED: "0",
                CCA_NO_PROPERTY_LEFT: "1",
            }
        ]
    )

    assert worksheet.get(T777_LINE_25).value == D("0")
    assert closing(worksheet, T777_PART_B_CLOSING_UCC) == {D("10.1"): D("0")}


def test_a_class_10_1_vehicle_sold_in_the_year_takes_half_its_ucc_as_the_base() -> None:
    # Note (11): "If you sold the vehicle in the current year and owned the vehicle at the end of
    # the previous year, enter 1/2 of the amount from column 2 in column 5." 10,000.00; the CCA is
    # 30% of it, 3,000.00, and the closing UCC is 0 (note (12): the year of the sale).
    worksheet = run(
        part_b=[
            {
                **DATED,
                CCA_CLASS_NUMBER: "10.1",
                CCA_UCC_AT_START: "20000",
                CCA_PROCEEDS: "20000",
                CCA_CLAIMED: "3000",
                CCA_NO_PROPERTY_LEFT: "1",
            }
        ]
    )

    assert worksheet.get(T777_LINE_25).value == D("3000.00")
    assert closing(worksheet, T777_PART_B_CLOSING_UCC) == {D("10.1"): D("0")}


def test_a_riip_vehicle_bought_in_the_year_has_a_base_of_three_halves_of_its_cost() -> None:
    # Note (11): "enter 3/2 of the amount from column 3 in column 5" for a RIIP that became
    # available for use in the year: 45,000.00; the CCA is 30% of it, 13,500.00; the closing UCC
    # is the cost less the CCA, 16,500.00 (column 2 or column 3 minus column 7).
    worksheet = run(
        part_b=[
            {
                **DATED,
                CCA_CLASS_NUMBER: "10.1",
                CCA_ADDITIONS: "30000",
                CCA_RIIP_ADDITIONS: "30000",
                CCA_CLAIMED: "13500",
            }
        ]
    )

    assert worksheet.get(T777_LINE_25).value == D("13500.00")
    assert closing(worksheet, T777_PART_B_CLOSING_UCC) == {D("10.1"): D("16500.00")}


def test_an_aiip_vehicle_bought_in_the_year_has_a_base_of_its_full_cost() -> None:
    # Note (11): "enter 100% of the amount from column 3 in column 5" for an AIIP that became
    # available for use in the year: 30,000.00; the CCA is 30% of it, 9,000.00; the closing UCC is
    # 21,000.00.
    worksheet = run(
        part_b=[
            {
                **DATED,
                CCA_CLASS_NUMBER: "10.1",
                CCA_ADDITIONS: "30000",
                CCA_AIIP_ADDITIONS: "30000",
                CCA_CLAIMED: "9000",
            }
        ]
    )

    assert worksheet.get(T777_LINE_25).value == D("9000.00")
    assert closing(worksheet, T777_PART_B_CLOSING_UCC) == {D("10.1"): D("21000.00")}


def test_with_no_rows_lines_13_and_25_are_0() -> None:
    worksheet = run()

    assert worksheet.get(T777_LINE_13).value == D("0")
    assert worksheet.get(T777_LINE_25).value == D("0")
    assert len(worksheet.get(T777_CLASS_8_CLOSING_UCC).value.records) == 0
    assert len(worksheet.get(T777_VEHICLE_CLOSING_UCC).value.records) == 0
    assert len(worksheet.get(T777_PART_B_CLOSING_UCC).value.records) == 0


# --- the refusals a filer can trigger ----------------------------------------------------------


def test_a_class_8_row_in_the_vehicle_list_is_refused() -> None:
    with pytest.raises(InvalidRecordError):
        run(vehicles=[{CCA_CLASS_NUMBER: "8", CCA_UCC_AT_START: "1000"}])


def test_a_class_10_row_in_the_class_8_list_is_refused() -> None:
    with pytest.raises(InvalidRecordError):
        run(class_8=[{CCA_CLASS_NUMBER: "10", CCA_UCC_AT_START: "1000"}])


def test_a_class_10_1_vehicle_in_the_part_a_vehicle_list_is_refused() -> None:
    with pytest.raises(InvalidRecordError):
        run(vehicles=[{CCA_CLASS_NUMBER: "10.1", CCA_UCC_AT_START: "20000", CCA_CLAIMED: "6000"}])


def test_a_class_54_row_with_an_amount_in_its_proceeds_column_is_refused() -> None:
    # A Class 54 sale is listed as a vehicle of the sold-vehicle list (the sold-vehicle rule),
    # never as proceeds.
    with pytest.raises(InvalidRecordError):
        run(
            vehicles=[
                {
                    CCA_CLASS_NUMBER: "54",
                    CCA_ADDITIONS: "40000",
                    CCA_AIIP_ADDITIONS: "40000",
                    CCA_PROCEEDS: "1000",
                }
            ]
        )


def test_aiip_and_riip_additions_above_the_additions_are_refused() -> None:
    with pytest.raises(InvalidRecordError):
        run(
            vehicles=[
                {
                    CCA_CLASS_NUMBER: "10",
                    CCA_ADDITIONS: "1000",
                    CCA_AIIP_ADDITIONS: "800",
                    CCA_RIIP_ADDITIONS: "300",
                }
            ]
        )


def test_a_part_b_row_with_both_a_ucc_at_the_start_and_additions_is_refused() -> None:
    # One vehicle is either owned from the previous year (UCC at the start, note (11)) or bought in
    # the year (additions), not both.
    with pytest.raises(InvalidRecordError):
        run(
            part_b=[
                {
                    **DATED,
                    CCA_CLASS_NUMBER: "10.1",
                    CCA_UCC_AT_START: "20000",
                    CCA_ADDITIONS: "30000",
                }
            ]
        )


def test_a_part_b_row_with_no_date_acquired_is_refused() -> None:
    # Form T777 Part B prints "Date acquired (yyyy-mm-dd)" on every row, so it is required: a row
    # with no date (year 0) is refused, so the Class 10.1 condition of Guide T4044 runs on all rows.
    with pytest.raises(InvalidRecordError, match="item 1: the date acquired is required"):
        run(
            part_b=[
                {
                    CCA_VEHICLE_ACQUIRED_YEAR: "0",
                    CCA_CLASS_NUMBER: "10.1",
                    CCA_UCC_AT_START: "20000",
                    CCA_CLAIMED: "6000",
                }
            ]
        )


def test_proceeds_without_the_sold_in_year_tick_are_refused() -> None:
    with pytest.raises(InvalidRecordError):
        run(
            part_b=[
                {
                    **DATED,
                    CCA_CLASS_NUMBER: "10.1",
                    CCA_UCC_AT_START: "20000",
                    CCA_PROCEEDS: "20000",
                    CCA_NO_PROPERTY_LEFT: "0",
                }
            ]
        )


def test_the_sold_in_year_tick_without_proceeds_is_refused() -> None:
    with pytest.raises(InvalidRecordError):
        run(
            part_b=[
                {
                    **DATED,
                    CCA_CLASS_NUMBER: "10.1",
                    CCA_UCC_AT_START: "20000",
                    CCA_NO_PROPERTY_LEFT: "1",
                }
            ]
        )


# --- a Part A class listed twice (`ca/cca_part_a_checks`) ---------------------------------------

CLASS_8_ROW: Row = {
    CCA_CLASS_NUMBER: "8",
    CCA_UCC_AT_START: "1000",
    CCA_ADDITIONS: "500",
    CCA_CLAIMED: "250",
}


def test_the_same_class_8_row_listed_twice_is_refused_naming_both_items() -> None:
    # Return EE's Class 8 row (line 13 $250.00) listed twice would claim its CCA twice, $500.00 on
    # line 13; the second row is refused instead, naming the first.
    with pytest.raises(InvalidRecordError, match=r"item 2: class 8 is already listed in item 1"):
        run(class_8=[CLASS_8_ROW, CLASS_8_ROW])


def test_a_class_54_row_listed_twice_with_a_second_claim_of_0_is_refused() -> None:
    # The Class 54 row of Return EE, listed again with no claim, is still a second row of the class.
    with pytest.raises(InvalidRecordError, match=r"item 2: class 54 is already listed in item 1"):
        run(
            vehicles=[
                {
                    CCA_CLASS_NUMBER: "54",
                    CCA_ADDITIONS: "40000",
                    CCA_AIIP_ADDITIONS: "40000",
                    CCA_CLAIMED: "30000",
                },
                {
                    CCA_CLASS_NUMBER: "54",
                    CCA_ADDITIONS: "40000",
                    CCA_AIIP_ADDITIONS: "40000",
                    CCA_CLAIMED: "0",
                },
            ]
        )
