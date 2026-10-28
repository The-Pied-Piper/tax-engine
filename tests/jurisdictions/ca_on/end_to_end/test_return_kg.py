"""CA-ON 2025 end to end: return kg (T1 line 12599, the gross rental income).

Guide T4036 (2025), "Line 8299 - Total gross rental income": "Enter this amount on line 12599 of
your income tax return. If you are a co-owner of the rental property or a member of a partnership
that does not need to provide you with a T5013 slip, enter the gross rental income for the entire
property on line 12599. Do not split the gross income according to your ownership share." Line
12599 is the total of Form T776 line 8299 over the statements, as typed.

The worked return `returns/2025_return_kg.yaml` (a co-owned duplex and a sole-owner house) is
checked by `test_worked_returns.py`. This module reads the cases the worked return does not
express: a co-owner's gross that the share does not scale, and a return with no statement.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    GROSS_RENTAL_INCOME,
    NET_RENTAL_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return, run

# A duplex of two units with gross rents of 12000 for the entire property and property taxes of
# 4000 for the entire property, as Return KG: line 9369 is 8000 and the co-owner's share is 4000.
CO_OWNED_DUPLEX: dict[str, Any] = {
    "rental_properties": ((2, "0", "12000"),),
    "rental_expenses": {"property_taxes": ("4000", "0", "0")},
    "rental_coowner": 1,
    "rental_coowner_share": "4000",
}

# A house of one unit with gross rents of 5000 (line 8141) and other income of 200 (line 8230).
SOLE_OWNER_HOUSE: dict[str, Any] = {
    "rental_properties": ((1, "0", "5000"),),
    "rental_other_income": "200",
}


def return_kg(statements: tuple[dict[str, Any], ...]) -> dict[str, tuple[Worksheet, ...]]:
    """Return KG's run: no income but the T776 `statements`."""
    return run(
        employment_income="0",
        share_dispositions=(),
        unused_rrsp_contributions="0",
        rrsp_contributions="0",
        rrsp_deduction_limit="0",
        rrsp_amount_deducted="0",
        union_dues="0",
        rental_statements=statements,
    )


def test_a_co_owners_gross_rental_income_is_the_whole_property_not_their_share() -> None:
    # The statement's gross rents of 12000 are for the entire property: line 12599 is 12000.00 and
    # is not scaled by the share (4000 of the 8000 of line 9369), while line 12600 and the total
    # income are the share, 4000.
    result = rental_return(CO_OWNED_DUPLEX)
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(GROSS_RENTAL_INCOME).value == D("12000")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("4000")
    assert worksheet.get(TOTAL_INCOME).value == D("4000")


def test_line_12599_adds_line_8299_over_the_statements_with_other_income_on_line_8230() -> None:
    # 12000 (the duplex) + 5000 + 200 (the house, lines 8141 and 8230) = 17200.
    result = return_kg((CO_OWNED_DUPLEX, SOLE_OWNER_HOUSE))
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(GROSS_RENTAL_INCOME).value == D("17200")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("9200")


def test_line_12599_is_zero_with_no_statement() -> None:
    result = return_kg(())

    assert result["ca-on/return"][0].get(GROSS_RENTAL_INCOME).value == D("0")
