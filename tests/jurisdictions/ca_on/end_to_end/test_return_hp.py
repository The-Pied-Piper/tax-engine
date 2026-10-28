"""CA-ON 2025 end to end: return hp (a Class 10.1 vehicle in Form T776 and in Form T777 Part B)."""

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
    CCA_UCC_AT_START,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    NET_RENTAL_INCOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLASSES_CHECKED,
    RENTAL_CCA_LIMIT,
    RENTAL_CLOSING_UCC,
    T777_CLASS_8_ROWS,
    T777_LINE_25,
    T777_PART_B_ADDITIONS_CHECKED_ROWS,
    T777_PART_B_CLOSING_UCC,
    T777_PART_B_ROWS,
    T777_VEHICLE_ROWS,
    T777_VEHICLE_SALES_TAX_RATE,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# Return HP's rental vehicle, a Class 10.1 row of Form T776 Area A (as in
# `returns/2025_return_hp.yaml`): bought in 2025 for $39,000.00 before tax, with additions of
# $42,940.00 (the limit for 2025, $38,000 plus 13 percent). Half-year rule: 42940.00 x 50% x 30% =
# 6441.00, claimed in full, so the UCC at the end of the year is 42940.00 - 6441.00 = 36499.00.
# The row's fields are those of `rental_cca_classes` (the vehicle's year, cost and government
# assistance last).
RENTAL_VEHICLE: tuple[Any, ...] = (
    "10.1",
    "0",
    "42940.00",
    "0",
    "0",
    "0",
    "6441.00",
    0,
    "0",
    "0",
    "0",
    "0",
    0,
    2025,
    "39000",
    "0",
)
# The same rental vehicle with its cost of additions at $44,070 (the price with tax): refused.
UNCAPPED_RENTAL_VEHICLE: tuple[Any, ...] = ("10.1", "0", "44070.00", *RENTAL_VEHICLE[3:])

# Return HP's rental statement: gross rents of 24000 and expenses of 17559, so the net income before
# the capital cost allowance is 6441.00, which the claim of the rental vehicle takes in full.
RETURN_HP_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "24000"),),
    "rental_expenses": {"repairs_and_maintenance": ("17559", "0", "0")},
    "rental_vehicle_sales_tax_rate": "13",
    "rental_cca_classes_rows": (RENTAL_VEHICLE,),
}

# Return HP's employment vehicle, a Class 10.1 row of Form T777 Part B: bought in 2025, with
# additions (column 3) of $42,940.00, half of them the base of column 5 (the half-year rule):
# 21470.00 x 30% = 6441.00, and 42940.00 - 6441.00 = 36499.00 at the end of the year.
# The "Date acquired" (its year) and "Cost of vehicle" a Part B row must have (the form prints them
# on every row, so they are required): a Class 10.1 vehicle acquired in 2024 for $37,000.01.
DATED: Mapping[Any, str] = {CCA_VEHICLE_ACQUIRED_YEAR: "2024", CCA_VEHICLE_COST: "37000.01"}

EMPLOYMENT_VEHICLE: Mapping[Any, str] = {
    **DATED,
    CCA_CLASS_NUMBER: "10.1",
    CCA_ADDITIONS: "42940.00",
    CCA_CLAIMED: "6441.00",
}
UNCAPPED_EMPLOYMENT_VEHICLE: Mapping[Any, str] = {**EMPLOYMENT_VEHICLE, CCA_ADDITIONS: "44070.00"}

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


def run_hp(
    *part_b: Mapping[Any, str],
    rental: Mapping[str, Any] | None = None,
) -> dict[str, tuple[Worksheet, ...]]:
    """Return HP's inputs, as in `returns/2025_return_hp.yaml`: the rental statement of
    `RETURN_HP_STATEMENT` (`rental` changes its fields), the Part B rows of Form T777 (by default
    the employment vehicle), and the 13 percent sales tax rate of both vehicles. Form T777 has no
    other row, and the return reads none of its exports."""
    statement: dict[str, Any] = {**RETURN_HP_STATEMENT, **(rental or {})}
    artifacts = [
        each
        for each in starting("0", (), "0", "0", "0", "0", "0", rental_statements=(statement,))
        if each.kind not in T777_KINDS
    ]
    inputs: list[Artifact[Any]] = [
        t777_rows(T777_CLASS_8_ROWS),
        t777_rows(T777_VEHICLE_ROWS),
        t777_rows(T777_PART_B_ROWS, *(part_b or (EMPLOYMENT_VEHICLE,))),
        Artifact(T777_VEHICLE_SALES_TAX_RATE, D("13")),
    ]
    return service().compute(CA_ON, 2025, *artifacts, *inputs)


# --- a Class 10.1 vehicle at the limit with tax, in each form ----------------------------------


def test_return_hps_rental_vehicle_at_42940_is_checked_and_passed_on_as_entered() -> None:
    # The limit is $38,000 plus 13 percent, $42,940.00: additions at the limit pass, and the row is
    # passed on to the proceeds step unchanged.
    statement = run_hp()["ca/t776"][0]

    checked = statement.get(RENTAL_CCA_CLASSES_CHECKED).value
    assert [record[CCA_CLASS_NUMBER] for record in checked.records] == [D("10.1")]
    assert [record[CCA_ADDITIONS] for record in checked.records] == [D("42940.00")]


def test_return_hps_rental_vehicle_is_claimed_at_6441_and_closes_at_36499() -> None:
    # The half-year rule: 42940.00 x 50% x 30% = 6441.00, claimed in full (line 9936), and the UCC
    # at the end of the year is 42940.00 - 6441.00 = 36499.00.
    statement = run_hp()["ca/t776"][0]

    assert statement.get(RENTAL_CCA_CLAIM).value == D("6441.00")
    (record,) = statement.get(RENTAL_CLOSING_UCC).value.records
    assert record[CCA_UCC_AT_END] == D("36499.00")


def test_return_hps_employment_vehicle_at_42940_is_checked_and_claimed_at_6441() -> None:
    # Form T777 Part B: the same limit, the same claim, and line 25 is the Part B total.
    result = run_hp()
    worksheet = result["ca/t777"][0]

    checked = worksheet.get(T777_PART_B_ADDITIONS_CHECKED_ROWS).value
    assert [record[CCA_ADDITIONS] for record in checked.records] == [D("42940.00")]
    assert worksheet.get(T777_LINE_25).value == D("6441.00")
    assert [
        record[CCA_UCC_AT_END] for record in worksheet.get(T777_PART_B_CLOSING_UCC).value.records
    ] == [D("36499.00")]


def test_return_hps_net_rental_income_is_0_as_the_claim_takes_all_of_amount_5() -> None:
    # Gross rents of 24000.00 less expenses of 17559.00 are amount 5, 6441.00, and the claim of
    # 6441.00 takes all of it: line 9946 and T1 line 12600 are 0.00, and total income is 0.00 (as in
    # Return HM). The Form T777 schedule is not read by T1, so it changes no line of the return.
    result = run_hp()
    statement = result["ca/t776"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(RENTAL_CCA_LIMIT).value == D("6441")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("0.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0.00")


# --- a Class 10.1 vehicle above the limit with tax, refused in each form -----------------------


def test_return_hps_rental_vehicle_at_44070_is_refused_naming_item_1() -> None:
    # $44,070 (the vehicle with its tax) is above the limit of $42,940.00: the form asks for the
    # capped amount, so the row is refused, not capped.
    with pytest.raises(InvalidRecordError) as error:
        run_hp(rental={"rental_cca_classes_rows": (UNCAPPED_RENTAL_VEHICLE,)})

    assert str(error.value).endswith(
        "item 1: additions (44070.00) are more than the Class 10.1 limit with tax (42940.00) "
        "at a sales tax rate of 13%, which is GST plus PST, or HST"
    )


def test_return_hps_employment_vehicle_at_44070_is_refused_naming_item_1() -> None:
    with pytest.raises(InvalidRecordError) as error:
        run_hp(UNCAPPED_EMPLOYMENT_VEHICLE)

    assert str(error.value).endswith(
        "item 1: additions (44070.00) are more than the Class 10.1 limit with tax (42940.00) "
        "at a sales tax rate of 13%, which is GST plus PST, or HST"
    )


# --- a Part B row that is not a Class 10.1 addition is not checked ----------------------------


def test_return_hps_part_b_vehicle_with_only_a_ucc_at_the_start_is_not_checked() -> None:
    # A vehicle owned from the previous year has no additions (note (11)): its UCC at the start,
    # $60,000.00, is above the limit but the row is not checked, so it is not refused. Its CCA is
    # 30% of it, 18000.00, and its closing UCC is 60000.00 - 18000.00 = 42000.00.
    result = run_hp(
        {**DATED, CCA_CLASS_NUMBER: "10.1", CCA_UCC_AT_START: "60000.00", CCA_CLAIMED: "18000.00"}
    )

    worksheet = result["ca/t777"][0]
    assert [
        record[CCA_UCC_AT_END] for record in worksheet.get(T777_PART_B_CLOSING_UCC).value.records
    ] == [D("42000.00")]
