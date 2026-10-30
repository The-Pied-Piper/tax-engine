"""CA-ON 2025 end to end: return dc."""

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
    NET_INCOME,
    NET_RENTAL_INCOME,
    REFUND_OR_BALANCE_OWING,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLASSES_ADJUSTED,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_IMMEDIATE_EXPENSING_CLAIM,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT,
    RENTAL_NET_INCOME_AFTER_CCA,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

# Area A rows as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
# property left, column 4, column 6, column 9, the remaining personal part), as in Return BS:
# class 1 with a UCC of 10000, claimed in full at 400.00, and class 8 with a UCC of 2000 and DIEP
# additions of 5000, of which 3000 is expensed at once, claimed as 3600.00.
CLASS_1_ROW = ("1", "10000", "0", "0", "0", "0", "400.00", 0, "0", "0", "0", "0")
CLASS_8_ROW = ("8", "2000", "5000", "0", "0", "0", "3600.00", 0, "5000", "0", "3000", "0")

# Area G and Note 5: associated with one other EPOP (1) under an agreement that was filed (1), the
# percentage assigned to the filer 40 and the total of column 3 100, so line iii is
# 1500000 x 40% = 600000.00; no amount allocated by the minister.
AREA_G = {
    "rental_epop_associated": 1,
    "rental_epop_agreement_filed": 1,
    "rental_epop_percentage": "40",
    "rental_epop_percentage_total": "100",
}


def class_10_1_row(
    year: int = 2025,
    cost: str = "56500.00",
    assistance: str = "0",
    expensed: str = "12540",
    claim: str = "12540.00",
    class_number: str = "10.1",
) -> tuple[Any, ...]:
    """Area A, a passenger vehicle bought in `year` for `cost` (with the HST), `assistance` of
    government assistance received less repaid, sold for 40000, all of it a DIEP's (columns 5 and
    6); capital cost 42940 (38000 + 13%, columns 3 and 4); column 9 `expensed`; the claim
    (column 23) `claim`; no property left (a chosen 1); the remaining personal part 0."""
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
        0,
        year,
        cost,
        assistance,
    )


# Return DC's T776 statement: Return BS's two classes and a Class 10.1 vehicle; gross rents 36540
# (a chosen figure) less the expenses of 12000, so amount 5 is 24540.00, and the 13% HST rate
# of the vehicle gives its prescribed amount with tax.
RETURN_DC_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "36540"),),
    "rental_expenses": {
        "insurance": ("1200", "0", "0"),
        "interest_and_bank_charges": ("6000", "0", "0"),
        "repairs_and_maintenance": ("1300", "0", "0"),
        "property_taxes": ("3500", "0", "0"),
    },
    "rental_vehicle_sales_tax_rate": "13",
    "rental_cca_classes_rows": (CLASS_1_ROW, CLASS_8_ROW, class_10_1_row()),
    **AREA_G,
}


def return_dc(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return DC's inputs, as in `returns/2025_return_dc.yaml`: Return BS's filer with a Class 10.1
    passenger vehicle bought and sold in 2025 whose cost is above the prescribed amount.

    The gross rents of 36540 less the expenses of 12000 are 24540 of income before CCA; the claims
    are 400.00, 3600.00 and 12540.00, 16540.00 in all, so line 9936 is 16540.00 and the net rental
    income is 24540.00 - 16540.00 = 8000.00, Return BS's, as are the T1 figures.
    """
    return rental_return(RETURN_DC_STATEMENT, changes, **overrides)


def statement_dc(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return DC's one T776 statement: its lines, as the form computes them."""
    return return_dc(changes)["ca/t776"][0]


def adjusted_proceeds(statement: Worksheet) -> list[tuple[Any, Any, Any]]:
    """Class number, column 5 and column 6 of each row of the adjusted Area A list."""
    value = statement.get(RENTAL_CCA_CLASSES_ADJUSTED).value
    return [
        (record[CCA_CLASS_NUMBER], record[CCA_PROCEEDS], record[CCA_DIEP_PROCEEDS])
        for record in value.records
    ]


def test_return_dcs_proceeds_are_adjusted_by_the_prescribed_amount_over_the_actual_cost() -> None:
    # Area A Note 2: the vehicle was bought in 2025, so the prescribed amount is 38000 plus the
    # HST of 13% (4940), 42940.00; the actual cost is 56500.00 - 0 = 56500.00, more than that, so
    # the proceeds of 40000 (column 5, all of it column 6) are adjusted by the factor 42940.00 /
    # 56500.00 = 0.76: 40000 x 0.76 = 30400.00 each. Classes 1 and 8 have no proceeds.
    statement = statement_dc()

    assert adjusted_proceeds(statement) == [
        (D("1"), D("0"), D("0")),
        (D("8"), D("0"), D("0")),
        (D("10.1"), D("30400.00"), D("30400.00")),
    ]


def test_return_dcs_trace_names_the_adjustment() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_dc().trace)

    assert (
        "rental_cca_classes_adjusted: item 3: proceeds 40000 and DIEP proceeds 40000 adjusted by "
        "prescribed amount 42940 / actual cost 56500 = proceeds 30400 and DIEP proceeds 30400"
    ) in rendered


def test_return_dcs_column_8_is_the_adjusted_12540_so_column_9_can_be_the_whole_of_it() -> None:
    # Column 7 is 0 + 42940 - 30400.00 = 12540.00; column 8 is column 4 minus column 6, 42940 -
    # 30400.00 = 12540.00, not more than column 7; column 9 is a chosen 12540, not more than
    # column 8. Line i is 3000 + 12540 = 15540, which is within the least of Note 5's three amounts:
    # the limit 600000.00, the UCC of DIEPs in column 8 (5000 + 12540 = 17540) and the income before
    # CCA, 24540.00.
    statement = statement_dc()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("15540")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("24540")
    assert (
        "rental_immediate_expensing_claim: item 3 class 10.1: column 4 42940 less column 6 "
        "30400, column 7 12540: column 8 12540, column 9 12540"
    ) in rendered


def test_return_dcs_column_9_would_be_refused_above_the_unadjusted_column_8() -> None:
    # Without the adjustment (the row not a vehicle of this year, 0), column 8 is 42940 - 40000 =
    # 2940, below the 12540 of column 9.
    with pytest.raises(InvalidRecordError) as raised:
        return_dc(
            {
                "rental_cca_classes_rows": (
                    CLASS_1_ROW,
                    CLASS_8_ROW,
                    class_10_1_row(year=0, cost="0"),
                )
            }
        )

    assert str(raised.value) == (
        "ca/t776, instance 1: item 3: column 9 (12540) is above column 8 (2940)"
    )


def test_return_dcs_class_closes_at_zero_and_the_other_classes_close_as_in_return_bs() -> None:
    # No property is left in the class 10.1 and column 7 is positive, so the maximum is 0 and column
    # 23 is 0 + column 9 = 12540.00; column 24 is 0. Classes 1 and 8 close at 9600.00 and 3400.00.
    statement = statement_dc()

    records = statement.get(RENTAL_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("1"), D("9600.00")),
        (D("8"), D("3400.00")),
        (D("10.1"), D("0")),
    ]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_closing_ucc: item 3 class 10.1: column 7 12540 with no property left: 0" in rendered
    )


def test_return_dcs_line_ii_is_16540_and_net_rental_income_is_8000_as_in_return_bs() -> None:
    # Line ii, the total of column 23, is 400.00 + 3600.00 + 12540.00 = 16540.00, which is line
    # 9936. Amount 6 is amount 5 less line ii: 24540.00 - 16540.00 = 8000.00, which is line 9946 and
    # T1 line 12600.
    result = return_dc()
    statement = result["ca/t776"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("16540.00")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("16540.00")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("8000.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("8000.00")


def test_return_dcs_figures_that_depend_on_income_are_return_bss() -> None:
    # Net income and taxable income are 8000.00 (no deductions), as in Return BS: the federal tax
    # 8000.00 x 14.5% = 1160.00, the Ontario tax 8000.00 x 5.05% = 404.00, no tax payable.
    worksheet = return_dc()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("8000.00")
    assert worksheet.get(NET_INCOME).value == D("8000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("8000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("1160.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("404.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_a_cost_at_the_prescribed_amount_with_tax_leaves_the_proceeds() -> None:
    # "whose cost is more than the prescribed amount": a cost of 42940.00 is not more than 42940.00,
    # so columns 5 and 6 stay 40000; column 8 is 42940 - 40000 = 2940, the most of column 9.
    statement = statement_dc(
        {
            "rental_cca_classes_rows": (
                CLASS_1_ROW,
                CLASS_8_ROW,
                class_10_1_row(cost="42940.00", expensed="2940", claim="2940.00"),
            )
        }
    )

    assert adjusted_proceeds(statement)[-1] == (D("10.1"), D("40000"), D("40000"))
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("5940")


def test_government_assistance_received_brings_the_actual_cost_to_the_prescribed_amount() -> None:
    # "you will have to adjust the actual cost of the vehicle for any payments or repayments of
    # government assistance": 56500.00 - 13560.00 = 42940.00, not more than the prescribed amount.
    statement = statement_dc(
        {
            "rental_cca_classes_rows": (
                CLASS_1_ROW,
                CLASS_8_ROW,
                class_10_1_row(assistance="13560.00", expensed="2940", claim="2940.00"),
            )
        }
    )

    assert adjusted_proceeds(statement)[-1] == (D("10.1"), D("40000"), D("40000"))


def test_government_assistance_repaid_raises_the_actual_cost() -> None:
    # A repayment is negative: 42940.00 - (-7060.00) = 50000.00, over 42940.00, so the factor is
    # 42940.00 / 50000.00 = 0.8588 and the proceeds are 40000 x 0.8588 = 34352.00; column 8 is
    # 42940 - 34352.00 = 8588.00, which with the 3000 of the other rows is 11588.
    statement = statement_dc(
        {
            "rental_cca_classes_rows": (
                CLASS_1_ROW,
                CLASS_8_ROW,
                class_10_1_row(
                    cost="42940.00", assistance="-7060.00", expensed="8588", claim="8588.00"
                ),
            )
        }
    )

    assert adjusted_proceeds(statement)[-1] == (D("10.1"), D("34352.00"), D("34352.00"))
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("11588")


def test_a_vehicle_acquired_in_2022_has_the_prescribed_amount_of_2022() -> None:
    # 34000 + 13% = 38420.00; 40000 x 38420.00 / 56500.00 = 27200.00 (0.68 exactly); column 8 is
    # 42940 - 27200.00 = 15740.00.
    statement = statement_dc(
        {
            "rental_cca_classes_rows": (
                CLASS_1_ROW,
                CLASS_8_ROW,
                class_10_1_row(year=2022, expensed="15740", claim="15740.00"),
            )
        }
    )

    assert adjusted_proceeds(statement)[-1] == (D("10.1"), D("27200.00"), D("27200.00"))


def test_a_vehicle_acquired_before_2021_is_refused() -> None:
    # A DIEP is acquired after April 18, 2021: nothing is printed for 2020.
    with pytest.raises(InvalidRecordError, match=r"^ca/t776, instance 1: item 3: .*2020"):
        return_dc(
            {"rental_cca_classes_rows": (CLASS_1_ROW, CLASS_8_ROW, class_10_1_row(year=2020))}
        )


def test_a_year_on_a_row_of_another_class_is_refused() -> None:
    # Only Class 10.1 is adjusted (Class 54 is not modelled): a year on a Class 8 row is refused.
    with pytest.raises(InvalidRecordError, match=r"^ca/t776, instance 1: item 2: .*10\.1"):
        return_dc(
            {
                "rental_cca_classes_rows": (
                    CLASS_1_ROW,
                    CLASS_8_ROW + (0, 2025, "56500.00", "0"),
                    class_10_1_row(),
                )
            }
        )


def test_the_year_of_the_row_is_not_part_of_the_adjusted_list() -> None:
    fields = statement_dc().get(RENTAL_CCA_CLASSES_ADJUSTED).value.fields

    assert CCA_VEHICLE_ACQUIRED_YEAR not in fields
