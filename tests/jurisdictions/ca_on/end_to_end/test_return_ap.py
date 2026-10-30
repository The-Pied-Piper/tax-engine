"""CA-ON 2025 end to end: return ap."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_RENTAL_INCOME,
    REFUND_OR_BALANCE_OWING,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLAIM_LESS_PERSONAL_PART,
    RENTAL_CCA_CLAIM_SHARE,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CCA_TABLE_RECAPTURE,
    RENTAL_CCA_TABLE_TERMINAL_LOSS,
    RENTAL_CLOSING_UCC,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NET_INCOME_SHARE,
    RENTAL_NET_INCOME_WITH_RECAPTURE,
    RENTAL_RECAPTURED_CCA,
    RENTAL_TERMINAL_LOSS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

BUILDING = ("1", "200000", "0", "0", "0", "0", "8000", 0, "0", "0", "0", "0")
FURNITURE = ("8", "5000", "2000", "0", "0", "0", "1200", 0, "0", "0", "0", "0")
# A class with a recapture of 500 (column 7 of -500.00) and one with a terminal loss of 1000 (no
# property left), for the co-owner's shares of lines 9947 and 9948 (see the test below).
RECAPTURE_ROW = ("10", "1000.00", "0", "1500.00", "0", "0", "0", 0, "0", "0", "0", "0")
TERMINAL_LOSS_ROW = ("9", "1000.00", "0", "0", "0", "0", "0", 1, "0", "0", "0", "0")


RETURN_AP_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "24000"),),
    "rental_expenses": {
        "insurance": ("1200", "0", "0"),
        "interest_and_bank_charges": ("6000", "0", "0"),
        "repairs_and_maintenance": ("1300", "0", "0"),
        "property_taxes": ("3500", "0", "0"),
    },
    "rental_cca_classes_rows": (BUILDING, FURNITURE),
}


def return_ap(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return AP's inputs, as in `returns/2025_return_ap.yaml`: Return AD's landlord with two
    capital cost allowance classes.

    Gross rents of 24000 (one property, two units) are the only income; the expenses are the
    insurance 1200, the interest 6000, the property taxes 3500 and the repairs 1300, 12000 in all.
    Area A has the Class 1 building (opening UCC 200000, claim 8000) and the Class 8 furniture
    (opening UCC 5000, additions 2000, claim 1200), so line 9936 is 9200 and line 9946 and T1
    line 12600 are 12000 - 9200 = 2800.
    """
    return rental_return(RETURN_AP_STATEMENT, changes, **overrides)


def test_return_aps_area_a_claims_9200_on_line_9936() -> None:
    # Area A, Class 1: column 7 is 200000 + 0 - 0 = 200000; with no additions the half-year
    # adjustment (column 18) is 0, column 19 is 200000, and the maximum is 200000 x 4% = 8000.00;
    # 8000 is claimed. Class 8: column 7 is 5000 + 2000 - 0 = 7000; column 18 is one half of
    # (2000 - 0 - 0 - 0) = 1000.00, column 19 is 7000 - 1000 = 6000.00 and the maximum is 6000.00
    # x 20% = 1200.00; 1200 is claimed. Line ii (the total of column 23) is 8000 + 1200 = 9200;
    # with no co-owner, personal part or business-use-of-home CCA, line 9936 is 9200, within the
    # 12000 of amount 5.
    result = return_ap()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("9200")
    assert statement.get(RENTAL_CCA_CLAIM_SHARE).value == D("9200")
    assert statement.get(RENTAL_CCA_CLAIM_LESS_PERSONAL_PART).value == D("9200")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("12000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("9200")


def test_return_aps_classes_have_no_recapture_and_no_terminal_loss() -> None:
    # Neither class has a negative column 7 (200000 and 7000), and both have property left
    # (the count of no property left is 0), so lines 9947 and 9948 are 0 and amounts 4 and 5 are
    # amount 3, 12000.
    result = return_ap()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_RECAPTURE).value == D("0")
    assert statement.get(RENTAL_RECAPTURED_CCA).value == D("0")
    assert statement.get(RENTAL_CCA_TABLE_TERMINAL_LOSS).value == D("0")
    assert statement.get(RENTAL_TERMINAL_LOSS).value == D("0")
    assert statement.get(RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_WITH_RECAPTURE).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("12000")


def test_return_aps_net_rental_income_is_2800_on_line_12600() -> None:
    # Amount 6 is amount 5 less line 9936: 12000 - 9200 = 2800, which is line 9946 and T1 line
    # 12600; it is the whole of total income.
    result = return_ap()
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("2800")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("2800")
    assert worksheet.get(TOTAL_INCOME).value == D("2800")


def test_return_aps_closing_ucc_is_192000_for_class_1_and_5800_for_class_8() -> None:
    # Column 24 is column 7 less column 23: 200000 - 8000 = 192000 and 7000 - 1200 = 5800, the
    # next year's column 2, with each record's class number.
    result = return_ap()
    statement = result["ca/t776"][0]

    closing = statement.get(RENTAL_CLOSING_UCC).value
    assert [list(record.values()) for record in closing.records] == [
        [D("1"), D("192000")],
        [D("8"), D("5800")],
    ]


def test_return_aps_figures_that_depend_on_income_are_return_ads_recomputed_for_2800() -> None:
    # Net income and taxable income are 2800.00 (no deductions). The federal tax on it is 2800.00
    # x 14.5% = 406.00 and the Ontario tax 2800.00 x 5.05% = 141.40, each below its
    # non-refundable credits (2338.71 and 643.72), so there is no tax payable and the refund or
    # balance owing is 0.
    result = return_ap()
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(NET_INCOME).value == D("2800.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("2800.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("406.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("141.40")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_return_aps_trace_names_each_line_of_the_capital_cost_allowance() -> None:
    result = return_ap()
    rendered = EnglishTraceRenderer().render_all(result["ca/t776"][0].trace)

    for line in (
        "rental_cca_table_recapture: item 1 class 1: column 7 200000 is not negative: recapture 0",
        "rental_cca_table_recapture: item 2 class 8: column 7 7000 is not negative: recapture 0",
        "rental_cca_table_recapture: item 1 0 + item 2 0 = 0",
        "rental_recaptured_cca: rental_cca_table_recapture 0, "
        "chosen as rental_coowner_checked is 0",
        "rental_cca_table_terminal_loss: item 1 class 1: column 7 200000 with property left: "
        "terminal loss 0",
        "rental_cca_table_terminal_loss: item 1 0 + item 2 0 = 0",
        "rental_terminal_loss: rental_cca_table_terminal_loss 0, "
        "chosen as rental_coowner_checked is 0",
        "rental_cca_table_claim: item 1 class 1: column 7 200000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 200000, "
        "maximum 4% of column 19 = 8000 (half-up to 0.01), claim 8000",
        "rental_cca_table_claim: item 2 class 8: column 7 7000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 1000, column 19 6000, "
        "maximum 20% of column 19 = 1200 (half-up to 0.01), claim 1200",
        "rental_cca_table_claim: item 1 8000 + item 2 1200 = 9200",
        "rental_cca_claim_share: rental_cca_table_claim 9200, "
        "chosen as rental_coowner_checked is 0",
        "rental_cca_claim_less_personal_part: rental_cca_claim_share 9200 "
        "less rental_cca_personal_part 0 = 9200",
        "rental_cca_claim: rental_cca_claim_less_personal_part 9200 "
        "less rental_cca_business_use_of_home 0 = 9200",
        "rental_cca_limit: rental_net_income_after_terminal_loss 12000, not below 0 = 12000",
        "rental_closing_ucc: item 1 class 1: column 7 200000 less claim 8000 = 192000",
        "rental_closing_ucc: item 2 class 8: column 7 7000 less claim 1200 = 5800",
        "rental_net_income_after_cca: rental_net_income_after_terminal_loss 12000 "
        "less rental_cca_claim 9200 = 2800",
        "net_rental_income: rental_net_income_after_cca 2800, "
        "chosen as rental_partner_checked is 0",
    ):
        assert line in rendered, line


def test_a_co_owners_share_of_amount_ii_replaces_the_table_total_on_line_9936() -> None:
    # A co-owner (count 1) enters only their share of the total CCA claim from amount ii: 3000 of
    # the 9200, and their share of line 2 is 6000 (amount 2, so amount 5, 6000). Line 9936 is
    # 3000, within the 6000 of amount 5, so amount 6 is 6000 - 3000 = 3000.
    result = return_ap(
        {"rental_coowner": 1, "rental_coowner_share": "6000", "rental_coowner_cca_claim": "3000"}
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_SHARE).value == D("6000")
    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("9200")
    assert statement.get(RENTAL_CCA_CLAIM_SHARE).value == D("3000")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("6000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("3000")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("3000")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_cca_claim_share: rental_coowner_cca_claim_checked 3000, "
        "chosen as rental_coowner_checked is 1"
    ) in rendered


def test_a_co_owners_shares_of_lines_9947_and_9948_replace_the_tables() -> None:
    # The co-owner's share of the recapture (line 9947) is 200 and of the terminal loss (line
    # 9948) 100, entered as the form says ("co-owners: enter your share of the amount"), and the
    # classes give 500 of recapture (class 10) and 1000 of terminal loss (class 9), so each share
    # is within its whole. Amount 3 is 6000 - 0 = 6000, amount 4 is 6200 and amount 5 is 6100; the
    # claim of 3000 is within it, so amount 6 is 3100.
    result = return_ap(
        {
            "rental_cca_classes_rows": (BUILDING, FURNITURE, RECAPTURE_ROW, TERMINAL_LOSS_ROW),
            "rental_coowner": 1,
            "rental_coowner_share": "6000",
            "rental_coowner_recaptured_cca": "200",
            "rental_coowner_terminal_loss": "100",
            "rental_coowner_cca_claim": "3000",
        }
    )
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_RECAPTURED_CCA).value == D("200")
    assert statement.get(RENTAL_TERMINAL_LOSS).value == D("100")
    assert statement.get(RENTAL_NET_INCOME_WITH_RECAPTURE).value == D("6200")
    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("6100")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("6100")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("3100")


def test_a_sole_proprietor_with_the_co_owners_share_of_amount_ii_uses_the_table_total() -> None:
    # Answer 0: the 3000 typed is not line 9936; the table's 9200 is, so amount 6 stays 2800.
    result = return_ap({"rental_coowner": 0, "rental_coowner_cca_claim": "3000"})

    assert result["ca/t776"][0].get(RENTAL_CCA_CLAIM).value == D("9200")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("2800")


def test_the_personal_part_and_the_business_use_of_home_cca_come_off_line_9936() -> None:
    # Line 9936 is "amount ii from Area A minus any personal part of CCA, and any CCA for
    # business-use-of home expenses": 9200 - 700 - 300 = 8200, so amount 6 is 12000 - 8200 = 3800.
    result = return_ap(
        {"rental_cca_personal_part": "700", "rental_cca_business_use_of_home": "300"}
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_CLAIM_LESS_PERSONAL_PART).value == D("8500")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("8200")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("3800")
