"""CA-ON 2025 end to end: return ec."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    NET_RENTAL_INCOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLASSES_ADJUSTED,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_LAND_ADDITIONS,
    RENTAL_LAND_DISPOSITIONS,
    RENTAL_NET_INCOME_AFTER_CCA,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

# Area A, the one row, as (column 1, column 2, column 3, column 5, column 11, column 12, the claim,
# no property left, column 4, column 6, column 9, the remaining personal part), as in Return EC:
# class 1 with no UCC at the start of the year, an addition of 79166.67 (the building's capital
# cost: 75000 + 75000 / 90000 x 5000 = 79166.67, a filer's input), no DIEP, no proceeds and no
# immediate expensing, claimed at 1100.00, the income before CCA, with property left in the class.
CLASS_1_ROW = ("1", "0", "79166.67", "0", "0", "0", "1100.00", 0, "0", "0", "0", "0")

# Return EC's T776 statement: one property with one unit, gross rents of 6000 (line 8141) less
# expenses of 4900 (property taxes, line 9180), so amount 5 is 1100.00 and the CCA is limited to it.
RETURN_EC_STATEMENT: dict[str, Any] = {
    "rental_properties": ((1, "0", "6000"),),
    "rental_expenses": {"property_taxes": ("4900", "0", "0")},
    "rental_cca_classes_rows": (CLASS_1_ROW,),
    "rental_land_additions": "15833.33",
}


def return_ec(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return EC's inputs, as in `returns/2025_return_ec.yaml`: a single filer whose only income
    is the net rental income of one new rental house bought in 2025 (Guide T4036, "Example")."""
    return rental_return(RETURN_EC_STATEMENT, changes, **overrides)


def class_1_claim(claim: str) -> dict[str, tuple[Worksheet, ...]]:
    """Return EC with the Class 1 row claimed at `claim`, all else as in Return EC."""
    row = CLASS_1_ROW[:6] + (claim,) + CLASS_1_ROW[7:]
    return return_ec({"rental_cca_classes_rows": (row,)})


def test_return_ecs_building_capital_cost_of_79166_67_is_accepted_in_area_a() -> None:
    # Guide T4036: "Paul enters $79,166.67 in column 3 of Area C", the building's capital cost of
    # 75000 + 4166.67 of the 5000 of fees. The row is accepted, with column 7 79166.67 (no UCC at
    # the start of the year, no proceeds), and its maximum is 4% of column 19, which is the half
    # of the addition (column 18 39583.34): 39583.33 x 4% = 1583.33, the CCA Paul would otherwise
    # claim, "$1,583.33 ([$79,166.67 × 50%] × 4%)".
    result = return_ec()
    statement = result["ca/t776"][0]

    (record,) = statement.get(RENTAL_CCA_CLASSES_ADJUSTED).value.records
    assert record[CCA_CLASS_NUMBER] == D("1")
    assert record[CCA_ADDITIONS] == D("79166.67")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert any(
        "rental_cca_table_claim: item 1 class 1: column 7 79166.67" in line
        and "column 18 39583.34, column 19 39583.33, maximum 4% of column 19 = 1583.33" in line
        for line in rendered
    )


def test_return_ecs_claim_is_limited_to_the_income_before_cca_of_1100() -> None:
    # Guide T4036: "Paul cannot claim CCA for more than $1,100". Amount 5 is 6000 - 4900 = 1100.00,
    # the limit; the claim (line ii, line 9936) is 1100.00, not the 1583.33 of the row's maximum.
    statement = return_ec()["ca/t776"][0]

    assert statement.get(RENTAL_CCA_LIMIT).value == D("1100")
    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("1100.00")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("1100.00")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("0.00")


def test_return_ecs_net_rental_income_is_zero_on_t1_line_12600() -> None:
    # Amount 6 is 1100.00 - 1100.00 = 0.00, which is line 9946 and T1 line 12600; with no other
    # income in the return, the total income is 0.00.
    result = return_ec()
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(NET_RENTAL_INCOME).value == D("0.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0.00")


def test_return_ecs_closing_ucc_of_class_1_is_the_capital_cost_less_the_claim() -> None:
    # Column 24: 79166.67 - 1100.00 = 78066.67, the UCC carried to the next year, with no terminal
    # loss or recapture, as the class has property left.
    statement = return_ec()["ca/t776"][0]

    (record,) = statement.get(RENTAL_CLOSING_UCC).value.records
    assert record[CCA_CLASS_NUMBER] == D("1")
    assert record[CCA_UCC_AT_END] == D("78066.67")


def test_return_ecs_land_lines_are_15833_33_on_line_9923_and_0_on_line_9924() -> None:
    # Guide T4036: "Paul enters ... $15,833.33 ($15,000 + $833.33) on line 9923 of Area F as the
    # capital cost of the land." Line 9923 "Total cost of all land additions in the year" is the
    # entered figure; line 9924 "Total proceeds from all land dispositions in the year" is 0 for
    # Paul. Nothing earlier on the form computes either line.
    statement = return_ec()["ca/t776"][0]

    assert statement.get(RENTAL_LAND_ADDITIONS).value == D("15833.33")
    assert statement.get(RENTAL_LAND_DISPOSITIONS).value == D("0")


def test_a_land_disposition_is_carried_through_and_reads_nothing_on_the_net_rental_income() -> None:
    # Area F line 9924 "Total proceeds from all land dispositions in the year", entered as
    # 250000.00 with no land additions: both lines are carried through unchanged, and neither
    # feeds the net rental income, which is the same as in Return EC: amount 6 and line 9946 are
    # 0.00 and T1 line 12600 is 0.00.
    result = return_ec({"rental_land_additions": "0", "rental_land_dispositions": "250000.00"})
    statement = result["ca/t776"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(RENTAL_LAND_DISPOSITIONS).value == D("250000.00")
    assert statement.get(RENTAL_LAND_ADDITIONS).value == D("0")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("0.00")
    assert statement.get(NET_RENTAL_INCOME).value == D("0.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("0.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0.00")


def test_a_claim_above_the_income_before_cca_is_refused_not_capped() -> None:
    # The half-year maximum of Class 1 is 1583.33, so a claim of 1583.33 is within the row, but it
    # is above amount 5, 1100.00: refused, not capped to 1100, as "You cannot use CCA to create or
    # increase a rental loss" (Guide T4036, "Limits on CCA"; the rule that makes Paul's claim
    # 1100.00, not 1583.33).
    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 1583\.33 is above ca/rental_cca_limit_all_statements 1100",
    ):
        class_1_claim("1583.33")
