"""CA-ON 2025 end to end: return av."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError, InvalidRecordError, ValidationError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities import (
    short_term_rental_non_compliant_cca_by_class as rental_cca,
)
from tax_calculator.jurisdictions.ca.capabilities.short_term_rental_non_compliant_cca import (
    ShortTermRentalNonCompliantCca,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_RENTAL_INCOME,
    NON_COMPLIANT_CCA,
    REFUND_OR_BALANCE_OWING,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLAIM_LESS_PERSONAL_PART,
    RENTAL_CCA_CLAIM_SHARE,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NON_COMPLIANT_CCA,
    RENTAL_NON_COMPLIANT_EXPENSES,
    SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

# Chart B rows as (column 1, column 4, column 5, column 6): class 1 with 900 and 30 days of 90,
# class 1 with 100 and 1 day of 3, class 8 with 500 and 45 days of 90.
ROWS: tuple[tuple[str, str, int, int], ...] = (
    ("1", "900", 30, 90),
    ("1", "100", 1, 3),
    ("8", "500", 45, 90),
)

# Area A rows as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
# property left): class 1 with a UCC of 10000 (maximum 10000 x 4% = 400.00, column 22 333.33, so
# at most 66.67) and class 8 with a UCC of 2000 (maximum 2000 x 20% = 400.00, column 22 250.00, so
# at most 150.00), each claiming the most.
CLASS_1_ROW = ("1", "10000", "0", "0", "0", "0", "66.67", 0, "0", "0", "0", "0")
CLASS_8_ROW = ("8", "2000", "0", "0", "0", "0", "150.00", 0, "0", "0", "0", "0")


RETURN_AV_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "24000"),),
    "rental_expenses": {
        "insurance": ("1200", "0", "0"),
        "interest_and_bank_charges": ("6000", "0", "0"),
        "repairs_and_maintenance": ("1300", "0", "0"),
        "property_taxes": ("3500", "0", "0"),
    },
    "short_term_rental_cca_units_rows": ROWS,
    "rental_cca_classes_rows": (CLASS_1_ROW, CLASS_8_ROW),
}


def return_av(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return AV's inputs, as in `returns/2025_return_av.yaml`: Return AD's landlord with three
    Chart B rows and two Area A classes whose claims are limited by column 22.

    Gross rents of 24000 (one property, two units) are the only income; the expenses are the
    insurance 1200, the interest 6000, the property taxes 3500 and the repairs 1300, 12000 in all.
    The claims are 66.67 and 150.00, so line 9936 is 216.67 and line 9946 and T1 line 12600 are
    12000 - 216.67 = 11783.33.
    """
    return rental_return(RETURN_AV_STATEMENT, changes, **overrides)


def test_return_avs_line_9367_is_583_33_from_three_chart_b_rows() -> None:
    # Chart B column 7 is column 4 x column 5 / column 6, each row rounded half-up to the cent:
    # 900 x 30 / 90 = 300.00, 100 x 1 / 3 = 33.33 and 500 x 45 / 90 = 250.00; line C, and so
    # line 9367, is 300.00 + 33.33 + 250.00 = 583.33.
    result = return_av()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NON_COMPLIANT_CCA).value == D("583.33")
    assert isinstance(
        statement.producer_of(RENTAL_NON_COMPLIANT_CCA), ShortTermRentalNonCompliantCca
    )


def test_return_avs_column_22_is_333_33_for_class_1_and_250_for_class_8() -> None:
    # "For each class, add the amounts from column 7 of Chart B and enter each total in column
    # 22 of Area A": class 1 is 300.00 + 33.33, class 8 is 250.00, in the order the classes appear.
    result = return_av()
    statement = result["ca/t776"][0]

    records = statement.get(SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS).value.records
    assert [(record[CCA_CLASS_NUMBER], record[NON_COMPLIANT_CCA]) for record in records] == [
        (D("1"), D("333.33")),
        (D("8"), D("250.00")),
    ]
    assert isinstance(
        statement.producer_of(SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS),
        rental_cca.ShortTermRentalNonCompliantCcaByClass,
    )


def test_return_avs_claims_are_limited_to_the_maximum_less_column_22() -> None:
    # Area A, class 1: column 7 is 10000 + 0 - 0 = 10000, columns 10 and 18 are 0, column 19 is
    # 10000 and the maximum (column 21) is 10000 x 4% = 400.00; column 22 is 333.33, so column 23
    # is at most 400.00 - 333.33 = 66.67. Class 8: column 7 and column 19 are 2000 and the maximum
    # is 2000 x 20% = 400.00; column 22 is 250.00, so column 23 is at most 400.00 - 250.00 =
    # 150.00. Both claim the most; line ii (the total of column 23) is 66.67 + 150.00 = 216.67 and
    # so is line 9936 (no personal part of CCA, no CCA for business-use-of-home expenses), within
    # the 12000 of amount 5.
    result = return_av()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("216.67")
    assert statement.get(RENTAL_CCA_CLAIM_SHARE).value == D("216.67")
    assert statement.get(RENTAL_CCA_CLAIM_LESS_PERSONAL_PART).value == D("216.67")
    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("12000")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("12000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("216.67")


def test_return_avs_net_rental_income_is_11783_33_on_line_12600() -> None:
    # Amount 6 is amount 5 less line 9936: 12000 - 216.67 = 11783.33, which is line 9946 and T1
    # line 12600; Chart A's line 9366 is 0. It is the whole of total income.
    result = return_av()
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NON_COMPLIANT_EXPENSES).value == D("0")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("11783.33")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("11783.33")
    assert worksheet.get(TOTAL_INCOME).value == D("11783.33")


def test_return_avs_closing_ucc_is_9933_33_for_class_1_and_1850_for_class_8() -> None:
    # Column 24 is column 7 less column 23: 10000 - 66.67 = 9933.33 and 2000 - 150.00 = 1850.00;
    # column 22 only limits the claim, it does not change the column 7 minus claim rule.
    result = return_av()
    statement = result["ca/t776"][0]

    records = statement.get(RENTAL_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("1"), D("9933.33")),
        (D("8"), D("1850.00")),
    ]


def test_return_avs_figures_that_depend_on_income_are_return_ads_recomputed_for_11783_33() -> None:
    # Net income and taxable income are 11783.33 (no deductions). The federal tax on it is
    # 11783.33 x 14.5% = 1708.58285, 1708.58 to the cent, and the Ontario tax 11783.33 x 5.05% =
    # 595.058165, 595.06; each is below its non-refundable credits (2338.71 and 643.72), so there
    # is no tax payable and the refund or balance owing is 0.
    result = return_av()
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(NET_INCOME).value == D("11783.33")
    assert worksheet.get(TAXABLE_INCOME).value == D("11783.33")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("1708.58")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("595.06")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_a_class_1_claim_above_400_less_333_33_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        return_av(
            {
                "rental_cca_classes_rows": (
                    ("1", "10000", "0", "0", "0", "0", "66.68", 0, "0", "0", "0", "0"),
                    CLASS_8_ROW,
                )
            }
        )

    assert str(raised.value) == (
        "ca/t776, instance 1: "
        "item 1: ca/cca_claimed 66.68 is above the maximum 66.67 (400.00 less column 22 333.33)"
    )


def test_a_class_8_claim_above_400_less_250_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        return_av(
            {
                "rental_cca_classes_rows": (
                    CLASS_1_ROW,
                    ("8", "2000", "0", "0", "0", "0", "150.01", 0, "0", "0", "0", "0"),
                )
            }
        )

    assert str(raised.value) == (
        "ca/t776, instance 1: "
        "item 2: ca/cca_claimed 150.01 is above the maximum 150.00 (400.00 less column 22 250.00)"
    )


def test_the_unlimited_maximum_is_claimable_when_chart_b_has_no_rows() -> None:
    # Without Chart B rows column 22 is 0 for every class: the whole maximum, 400.00 each, may be
    # claimed, so line 9936 is 800.00.
    statement = return_av(
        {
            "short_term_rental_cca_units_rows": (),
            "rental_cca_classes_rows": (
                ("1", "10000", "0", "0", "0", "0", "400.00", 0, "0", "0", "0", "0"),
                ("8", "2000", "0", "0", "0", "0", "400.00", 0, "0", "0", "0", "0"),
            ),
        }
    )["ca/t776"][0]

    assert statement.get(RENTAL_CCA_CLAIM).value == D("800.00")


def test_a_class_without_a_chart_b_row_has_a_column_22_of_zero() -> None:
    # Class 10: 30% of 1000 = 300.00, with no Chart B row, may claim all of it: 66.67 + 150 + 300.
    statement = return_av(
        {
            "rental_cca_classes_rows": (
                CLASS_1_ROW,
                CLASS_8_ROW,
                ("10", "1000", "0", "0", "0", "0", "300.00", 0, "0", "0", "0", "0"),
            )
        }
    )["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("516.67")
    with pytest.raises(
        InputAboveBoundError,
        match=r"^ca/t776, instance 1: item 3: ca/cca_claimed 300.01 is above the",
    ):
        return_av(
            {
                "rental_cca_classes_rows": (
                    CLASS_1_ROW,
                    CLASS_8_ROW,
                    ("10", "1000", "0", "0", "0", "0", "300.01", 0, "0", "0", "0", "0"),
                )
            }
        )


def test_return_avs_trace_shows_each_chart_b_row_and_class() -> None:
    result = return_av()
    rendered = EnglishTraceRenderer().render_all(result["ca/t776"][0].trace)

    for line in (
        "rental_non_compliant_cca: row 1: class 1 CCA 900 for 30 non-compliant days of 90 "
        "short-term days = 300 (half-up to 0.01)",
        "rental_non_compliant_cca: row 2: class 1 CCA 100 for 1 non-compliant days of 3 "
        "short-term days = 33.33 (half-up to 0.01)",
        "rental_non_compliant_cca: row 3: class 8 CCA 500 for 45 non-compliant days of 90 "
        "short-term days = 250 (half-up to 0.01)",
        "rental_non_compliant_cca: item 1 300 + item 2 33.33 + item 3 250 = 583.33",
        "short_term_rental_non_compliant_cca_by_class: item 1 class 1: column 7 300 + 33.33 "
        "= 333.33",
        "short_term_rental_non_compliant_cca_by_class: item 2 class 8: column 7 250 = 250",
        "rental_cca_table_claim: item 1 class 1: column 7 10000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 10000, "
        "maximum 4% of column 19 = 400 (half-up to 0.01), claim 66.67",
        "rental_cca_table_claim: item 2 class 8: column 7 2000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 2000, "
        "maximum 20% of column 19 = 400 (half-up to 0.01), claim 150",
        "rental_cca_table_claim: item 1 66.67 + item 2 150 = 216.67",
        "rental_cca_claim: rental_cca_claim_less_personal_part 216.67 "
        "less rental_cca_business_use_of_home 0 = 216.67",
        "rental_closing_ucc: item 1 class 1: column 7 10000 less claim 66.67 = 9933.33",
        "rental_closing_ucc: item 2 class 8: column 7 2000 less claim 150 = 1850",
    ):
        assert line in rendered, line


def test_no_chart_b_rows_give_zero_and_an_empty_list() -> None:
    result = return_av({"short_term_rental_cca_units_rows": ()})
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NON_COMPLIANT_CCA).value == D("0")
    assert statement.get(SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS).value.records == ()
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert "rental_non_compliant_cca: no items = 0" in rendered


def test_a_row_with_900_of_cca_and_30_of_90_days_is_300_on_line_9367() -> None:
    result = return_av({"short_term_rental_cca_units_rows": (("1", "900", 30, 90),)})
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NON_COMPLIANT_CCA).value == D("300.00")


def test_a_chart_b_row_with_no_short_term_days_is_refused_naming_the_row() -> None:
    with pytest.raises(ValidationError, match="row 1: ca/short_term_rental_days cannot be 0"):
        return_av({"short_term_rental_cca_units_rows": (("1", "900", 0, 0),)})


def test_a_chart_b_row_with_more_non_compliant_days_than_days_is_refused() -> None:
    with pytest.raises(ValidationError, match="row 2.*short_term_rental_non_compliant_days"):
        return_av({"short_term_rental_cca_units_rows": (ROWS[0], ("1", "900", 91, 90))})


# Form T776 Chart B "*** For each class, add the amounts from column 7 of Chart B and enter each
# total in column 22 of Area A, in the respective row.": Area A has Classes 1 and 8 only, so a Chart
# B row of another class has no row of Area A to enter its total in. It is refused, not dropped.


def test_a_chart_b_row_of_a_class_with_no_area_a_row_is_refused_naming_the_row() -> None:
    # Chart B row 1 changed from class 1 to class 5, which Area A does not list.
    with pytest.raises(InvalidRecordError, match=r"Chart B class 5 has no row in Area A"):
        return_av({"short_term_rental_cca_units_rows": (("5", "900", 30, 90), ROWS[1], ROWS[2])})


def test_a_later_chart_b_row_of_a_class_with_no_area_a_row_is_refused_naming_the_row() -> None:
    # Chart B row 3 changed from class 8 to class 6, which Area A does not list.
    with pytest.raises(InvalidRecordError, match=r"Chart B class 6 has no row in Area A"):
        return_av({"short_term_rental_cca_units_rows": (ROWS[0], ROWS[1], ("6", "500", 45, 90))})
