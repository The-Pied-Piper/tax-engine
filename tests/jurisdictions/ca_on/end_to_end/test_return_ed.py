"""CA-ON 2025 end to end: return ed, Guide T4036's Salvador, three rental properties on three Forms
T776 with no CCA."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_RENTAL_INCOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, run

# Guide T4036, "Limits on CCA" and "Example", Salvador: three rental properties, two Class 1
# buildings and one Class 3 building, all with Class 8 appliances. The net rental income of each
# is 1,500, 2,000 and (4,000), an overall net loss of (500), so "he cannot claim any CCA on his
# rental buildings or appliances". The net income before CCA of each statement is a chosen figure,
# other income (line 8230) of 1,500 and 2,000 and an advertising expense (line 8521) of 4,000.
# The UCC at the start of each class is a chosen figure too: building 1 has Class 1 at 100,000.00
# and Class 8 at 10,000.00; building 2 has Class 1 at 80,000.00 and Class 8 at 5,000.00; building 3
# has Class 3 at 60,000.00 and Class 8 at 8,000.00. No CCA is claimed on any class (column 23 is 0),
# so every line 9936 is 0 and each line 9946 is its line 9369.


def class_row(
    class_number: str, ucc_at_start: str, claim: str = "0"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str]:
    """An Area A row: the class, its UCC at the start (column 2, a chosen figure), no additions,
    no proceeds, the CCA claimed (column 23), property left in the class, no DIEP, no immediate
    expensing and no remaining personal part of the property's cost."""
    return (class_number, ucc_at_start, "0", "0", "0", "0", claim, 0, "0", "0", "0", "0")


BUILDING_1: dict[str, Any] = {
    "rental_other_income": "1500",
    "rental_cca_classes_rows": (class_row("1", "100000.00"), class_row("8", "10000.00")),
}
BUILDING_2: dict[str, Any] = {
    "rental_other_income": "2000",
    "rental_cca_classes_rows": (class_row("1", "80000.00"), class_row("8", "5000.00")),
}
BUILDING_3: dict[str, Any] = {
    "rental_expenses": {"advertising": ("4000", "0", "0")},
    "rental_cca_classes_rows": (class_row("3", "60000.00"), class_row("8", "8000.00")),
}


def ed_inputs(statements: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    """Return ED's inputs, as in `returns/2025_return_ed.yaml`: a landlord with the T776
    `statements` given, no employment income, no RRSP, no union dues, no business, no farm, no
    fishing and no other income."""
    return {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "rental_statements": statements,
        "business_statements": (),
        "farm_statements": (),
        "fish_statements": (),
    }


def return_ed(*statements: dict[str, Any]) -> Worksheet:
    """The worksheet of return ED's form `ca-on/return` with the T776 `statements`."""
    return compute(**ed_inputs(statements))


def run_ed(*statements: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return ED with the T776 `statements`."""
    return run(**ed_inputs(statements))


def three_buildings() -> dict[str, tuple[Worksheet, ...]]:
    return run_ed(BUILDING_1, BUILDING_2, BUILDING_3)


def test_each_building_is_one_t776_statement_and_each_has_its_own_worksheet() -> None:
    statements = three_buildings()["ca/t776"]

    assert len(statements) == 3


def test_no_building_or_appliance_has_cca_claimed_so_line_9936_is_0_on_every_statement() -> None:
    # Guide T4036: "he cannot claim any CCA on his rental buildings or appliances". Each class's
    # claim (column 23) is 0, so the total of the claims, line 9936, is 0 on each statement.
    statements = three_buildings()["ca/t776"]

    assert [statement.get(RENTAL_CCA_TABLE_CLAIM).value for statement in statements] == [
        D("0"),
        D("0"),
        D("0"),
    ]
    assert [statement.get(RENTAL_CCA_CLAIM).value for statement in statements] == [
        D("0"),
        D("0"),
        D("0"),
    ]


def test_each_class_keeps_its_chosen_ucc_at_the_end_of_the_year() -> None:
    # With no additions, no proceeds, no personal part and no claim, column 24 is column 2: the
    # chosen UCCs of building 1 (classes 1 and 8), building 2 (classes 1 and 8) and building 3
    # (classes 3 and 8).
    statements = three_buildings()["ca/t776"]

    closing = [
        [
            (record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END])
            for record in statement.get(RENTAL_CLOSING_UCC).value.records
        ]
        for statement in statements
    ]
    assert closing == [
        [(D("1"), D("100000.00")), (D("8"), D("10000.00"))],
        [(D("1"), D("80000.00")), (D("8"), D("5000.00"))],
        [(D("3"), D("60000.00")), (D("8"), D("8000.00"))],
    ]


def test_each_statements_net_income_before_cca_is_1500_2000_and_minus_4000() -> None:
    # Line 9369 of each statement: 1,500 of other income, 2,000 of other income, and 4,000 of
    # advertising, which is -4,000.
    statements = three_buildings()["ca/t776"]

    assert [
        statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value for statement in statements
    ] == [
        D("1500"),
        D("2000"),
        D("-4000"),
    ]


def test_each_statements_line_9946_is_its_net_income_before_cca_as_no_cca_is_claimed() -> None:
    statements = three_buildings()["ca/t776"]

    assert [statement.get(RENTAL_NET_INCOME_AFTER_CCA).value for statement in statements] == [
        D("1500"),
        D("2000"),
        D("-4000"),
    ]


def test_line_12600_is_the_sum_of_the_statements_which_is_a_net_loss_of_500() -> None:
    # T1 line 12600 "Net": 1,500 + 2,000 + (-4,000) = -500.00, the overall net loss in the Guide.
    worksheet = return_ed(BUILDING_1, BUILDING_2, BUILDING_3)

    assert worksheet.get(NET_RENTAL_INCOME).value == D("-500.00")


def test_total_income_is_the_negative_line_12600_as_it_is_the_only_income() -> None:
    # Total income (line 15000) is the sum of the income lines, line 13 being the net rental
    # income: -500.00, entered as a negative amount.
    worksheet = return_ed(BUILDING_1, BUILDING_2, BUILDING_3)

    assert worksheet.get(TOTAL_INCOME).value == D("-500.00")


def test_net_income_before_adjustments_is_minus_500_and_net_income_is_0() -> None:
    # T1 line 23400 "Net income before adjustments" is shown in brackets when negative: -500.00.
    # T1 line 23600 "Net income" is 0 when negative (line 23600 "if negative, enter 0").
    worksheet = return_ed(BUILDING_1, BUILDING_2, BUILDING_3)

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-500.00")
    assert worksheet.get(NET_INCOME).value == D("0")
