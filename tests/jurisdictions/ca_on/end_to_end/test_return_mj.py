"""CA-ON 2025 end to end: return mj (Form T777 Part B vehicles with a change in use and bought from
a non-arm's-length person, Guide T4044 "Part B - Class 10.1 property", column 3)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_CHANGE_IN_USE,
    CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH,
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
    CCA_VEHICLE_SELLER_COST,
    T777_CLASS_8_ROWS,
    T777_LINE_25,
    T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS,
    T777_PART_B_CLOSING_UCC,
    T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS,
    T777_PART_B_ROWS,
    T777_VEHICLE_ROWS,
    T777_VEHICLE_SALES_TAX_RATE,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# Return MJ's first vehicle (as in `returns/2025_return_mj.yaml`): a car bought in 2018 for $45,000
# (Class 10.1), owned for personal use and used for employment from 2025, worth $40,000 then, so
# column 3 is $40,000 and the claim is a chosen $500.
CHANGE_IN_USE_VEHICLE: Mapping[Any, str] = {
    CCA_VEHICLE_ACQUIRED_YEAR: "2018",
    CCA_VEHICLE_COST: "45000",
    CCA_VEHICLE_CHANGE_IN_USE: "1",
    CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE: "40000",
    CCA_CLASS_NUMBER: "10.1",
    CCA_ADDITIONS: "40000",
    CCA_CLAIMED: "500",
}

# Return MJ's second vehicle: bought in 2025 for $40,000 before tax from a relative, worth $35,000
# then, the seller's cost $30,000, and the limit with tax at 13 percent $42,940, so column 3 is the
# least of the three, $30,000, and the claim is a chosen $1,000.
RELATIVE_VEHICLE: Mapping[Any, str] = {
    CCA_VEHICLE_ACQUIRED_YEAR: "2025",
    CCA_VEHICLE_COST: "40000",
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH: "1",
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE: "35000",
    CCA_VEHICLE_SELLER_COST: "30000",
    CCA_CLASS_NUMBER: "10.1",
    CCA_ADDITIONS: "30000",
    CCA_CLAIMED: "1000",
}

T777_KINDS = {T777_CLASS_8_ROWS, T777_VEHICLE_ROWS, T777_PART_B_ROWS, T777_VEHICLE_SALES_TAX_RATE}


def t777_rows(kind: RecordListKind, *records: Mapping[Any, str]) -> Artifact[RecordList]:
    """One record of the row list `kind` for each mapping of its columns (by kind): the columns the
    mapping does not give are 0."""
    built: list[dict[Any, object]] = []
    for record in records:
        assert set(record) <= set(kind.fields), kind.identifier
        entry: dict[Any, object] = {}
        for field in kind.fields:
            if field in record:
                entry[field] = int(record[field]) if field.value_type is int else D(record[field])
            else:
                entry[field] = 0 if field.value_type is int else D(0)
        built.append(entry)
    return Artifact(kind, RecordList(kind.fields, built))


def run_mj(*part_b: Mapping[Any, str]) -> Worksheet:
    """The Form T777 worksheet for the Part B rows `part_b` (by default Return MJ's two vehicles) at
    the 13 percent sales tax rate; the form has no other row, and the return reads none of its
    exports but line 17."""
    artifacts = [
        each for each in starting("0", (), "0", "0", "0", "0", "0") if each.kind not in T777_KINDS
    ]
    inputs: list[Artifact[Any]] = [
        t777_rows(T777_CLASS_8_ROWS),
        t777_rows(T777_VEHICLE_ROWS),
        t777_rows(T777_PART_B_ROWS, *(part_b or (CHANGE_IN_USE_VEHICLE, RELATIVE_VEHICLE))),
        Artifact(T777_VEHICLE_SALES_TAX_RATE, D("13")),
    ]
    return service().compute(CA_ON, 2025, *artifacts, *inputs)["ca/t777"][0]


# --- the two vehicles of Return MJ ---------------------------------------------------------------


def test_return_mjs_two_vehicles_pass_every_check_and_the_claims_total_line_25() -> None:
    worksheet = run_mj()

    assert worksheet.get(T777_LINE_25).value == D("1500.00")
    for kind in (T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS, T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS):
        assert [r[CCA_ADDITIONS] for r in worksheet.get(kind).value.records] == [
            D("40000"),
            D("30000"),
        ]


def test_return_mjs_vehicles_close_at_their_additions_less_their_claims() -> None:
    # Column 8 is column 3 less column 7: 40000 - 500 and 30000 - 1000.
    worksheet = run_mj()

    assert [
        record[CCA_UCC_AT_END] for record in worksheet.get(T777_PART_B_CLOSING_UCC).value.records
    ] == [D("39500.00"), D("29000.00")]


# --- a change in use: column 3 is the fair market value ---------------------------------------


def test_the_original_cost_in_column_3_of_a_vehicle_with_a_change_in_use_is_refused() -> None:
    # A $41,000 price entered instead of the $40,000 it is worth when it starts being used for
    # employment (under the limit with tax, so the additions check passes it).
    with pytest.raises(InvalidRecordError) as error:
        run_mj({**CHANGE_IN_USE_VEHICLE, CCA_ADDITIONS: "41000"})

    assert str(error.value).endswith(
        "item 1: additions (41000.00) of a vehicle with a change in use are not its fair market "
        "value (40000.00) when it started being used for employment"
    )


# --- bought from a non-arm's-length person: column 3 is the least of three amounts ----------------


def test_the_price_in_column_3_of_a_vehicle_bought_from_a_relative_is_refused() -> None:
    # $40,000 entered, but the seller's cost of $30,000 is the least of the three amounts.
    with pytest.raises(InvalidRecordError) as error:
        run_mj({**RELATIVE_VEHICLE, CCA_ADDITIONS: "40000"})

    assert str(error.value).endswith(
        "item 1: additions (40000.00) of a vehicle bought from a non-arm's-length person are not "
        "the least of its fair market value (35000.00), the limit with tax (42940.00) at a sales "
        "tax rate of 13% and the seller's cost (30000.00), which is 30000.00"
    )


def test_the_limit_with_tax_is_the_least_when_the_value_and_the_sellers_cost_are_higher() -> None:
    # Worth $50,000, the seller's cost $60,000: the least is $38,000 + 13% = $42,940.
    worksheet = run_mj(
        {
            **RELATIVE_VEHICLE,
            CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE: "50000",
            CCA_VEHICLE_SELLER_COST: "60000",
            CCA_ADDITIONS: "42940",
        }
    )

    assert worksheet.get(T777_LINE_25).value == D("1000.00")


def test_a_vehicle_not_answered_as_bought_from_a_relative_is_not_limited() -> None:
    worksheet = run_mj(
        {**RELATIVE_VEHICLE, CCA_VEHICLE_FROM_NON_ARMS_LENGTH: "0", CCA_ADDITIONS: "40000"}
    )

    assert worksheet.get(T777_LINE_25).value == D("1000.00")
