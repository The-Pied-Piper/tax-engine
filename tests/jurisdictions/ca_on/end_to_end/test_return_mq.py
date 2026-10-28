"""CA-ON 2025 end to end: return mq (Form T777 Part A, a Class 10 vehicle with a change in use,
Guide T4044 "Part A - Classes 8, 10, 54, and 55 property", column 3)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CHANGE_IN_USE,
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS,
    T777_CLASS_8_ROWS,
    T777_LINE_25,
    T777_PART_B_ROWS,
    T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS,
    T777_VEHICLE_CLOSING_UCC,
    T777_VEHICLE_ROWS,
    T777_VEHICLE_SALES_TAX_RATE,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, sold_zepvs, starting

Row = Mapping[Any, str]

# Return MQ's vehicle (as in `returns/2025_return_mp.yaml`): a Class 10 car bought in 2018 for
# $19,000, owned for personal use and used for employment from 2025, worth $11,000 then, so column 3
# is $11,000 (the Guide's example) and the claim is $1,650, the most the form allows for $11,000 of
# additions in the year (30% of half the additions).
CHANGE_IN_USE_VEHICLE: Row = {
    CCA_CLASS_NUMBER: "10",
    CCA_ADDITIONS: "11000",
    CCA_CHANGE_IN_USE: "1",
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE: "11000",
    CCA_CLAIMED: "1650",
}

# A Class 8 row (musical instrument, Part A) with a change in use: worth $1,500 when it started
# being used for employment, so column 3 is $1,500. No claim is chosen for it.
CHANGE_IN_USE_CLASS_8: Row = {
    CCA_CLASS_NUMBER: "8",
    CCA_ADDITIONS: "1500",
    CCA_CHANGE_IN_USE: "1",
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE: "1500",
    CCA_CLAIMED: "0",
}

T777_KINDS = {T777_CLASS_8_ROWS, T777_VEHICLE_ROWS, T777_PART_B_ROWS, T777_VEHICLE_SALES_TAX_RATE}


def t777_rows(kind: RecordListKind, *records: Row) -> Artifact[RecordList]:
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


def run_mp(*vehicles: Row, class_8: Sequence[Row] = ()) -> Worksheet:
    """The Form T777 worksheet for the Part A vehicle rows `vehicles` (by default Return MQ's one
    vehicle) and the Class 8 rows `class_8`, at the 13 percent sales tax rate; the form has no
    Part B row, and the return reads none of its exports but line 17."""
    artifacts = [
        each for each in starting("0", (), "0", "0", "0", "0", "0") if each.kind not in T777_KINDS
    ]
    inputs: list[Artifact[Any]] = [
        t777_rows(T777_CLASS_8_ROWS, *class_8),
        t777_rows(T777_VEHICLE_ROWS, *(vehicles or (CHANGE_IN_USE_VEHICLE,))),
        t777_rows(T777_PART_B_ROWS),
        Artifact(T777_VEHICLE_SALES_TAX_RATE, D("13")),
    ]
    return service().compute(CA_ON, 2025, *artifacts, *inputs)["ca/t777"][0]


# --- the Class 10 vehicle of Return MQ -----------------------------------------------------------


def test_return_mqs_vehicle_passes_its_change_in_use_check_and_its_claim_totals_line_25() -> None:
    worksheet = run_mp()

    assert worksheet.get(T777_LINE_25).value == D("1650.00")
    assert [
        record[CCA_ADDITIONS]
        for record in worksheet.get(T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS).value.records
    ] == [D("11000")]


def test_return_mqs_vehicle_closes_at_its_additions_less_its_claim() -> None:
    # Column 16 is column 7 less column 15: 11000 - 1650.
    worksheet = run_mp()

    assert [
        record[CCA_UCC_AT_END] for record in worksheet.get(T777_VEHICLE_CLOSING_UCC).value.records
    ] == [D("9350.00")]


# --- a change in use: column 3 is the fair market value ----------------------------------------


def test_the_original_cost_in_column_3_of_a_vehicle_with_a_change_in_use_is_refused() -> None:
    # The $19,000 the car cost in 2018, entered instead of the $11,000 it is worth when it starts
    # being used for employment.
    with pytest.raises(InvalidRecordError) as error:
        run_mp({**CHANGE_IN_USE_VEHICLE, CCA_ADDITIONS: "19000"})

    assert str(error.value).endswith(
        "item 1: additions (19000.00) of property with a change in use are not its fair market "
        "value (11000.00) when it started being used for employment"
    )


def test_a_change_in_use_answer_other_than_0_or_1_is_refused() -> None:
    with pytest.raises(InvalidRecordError) as error:
        run_mp({**CHANGE_IN_USE_VEHICLE, CCA_CHANGE_IN_USE: "2"})

    assert str(error.value).endswith("item 1: change in use is 2")


def test_a_class_8_row_with_a_change_in_use_is_checked_like_a_vehicle_row() -> None:
    with pytest.raises(InvalidRecordError) as error:
        run_mp(class_8=({**CHANGE_IN_USE_CLASS_8, CCA_ADDITIONS: "2000"},))

    assert str(error.value).endswith(
        "item 1: additions (2000.00) of property with a change in use are not its fair market "
        "value (1500.00) when it started being used for employment"
    )


def test_a_class_8_row_whose_additions_are_its_fair_market_value_passes_the_check() -> None:
    worksheet = run_mp(class_8=(CHANGE_IN_USE_CLASS_8,))

    assert [
        record[CCA_ADDITIONS]
        for record in worksheet.get(T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS).value.records
    ] == [D("1500")]


# --- a row without a change in use is not checked against its fair market value ---------------


def test_a_vehicle_with_no_change_in_use_is_unaffected_by_its_figures() -> None:
    # Column 3 of a vehicle bought for $19,000 that did not change use is not refused.
    worksheet = run_mp(
        {
            CCA_CLASS_NUMBER: "10",
            CCA_ADDITIONS: "19000",
            CCA_CHANGE_IN_USE: "0",
            CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE: "0",
            CCA_CLAIMED: "1650",
        }
    )

    assert worksheet.get(T777_LINE_25).value == D("1650.00")
    assert [
        record[CCA_ADDITIONS]
        for record in worksheet.get(T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS).value.records
    ] == [D("19000")]
