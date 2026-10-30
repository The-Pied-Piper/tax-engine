"""CA-ON 2025 end to end: return bs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidRecordError,
)
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_RENTAL_INCOME,
    REFUND_OR_BALANCE_OWING,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_EPOP_PERCENTAGE_MAXIMUM,
    RENTAL_EPOP_PERCENTAGE_ROOM,
    RENTAL_IMMEDIATE_EXPENSING_ALLOCATED,
    RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    RENTAL_IMMEDIATE_EXPENSING_CAP,
    RENTAL_IMMEDIATE_EXPENSING_CLAIM,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    RENTAL_IMMEDIATE_EXPENSING_SHARE,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

# Area A rows as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
# property left, column 4, column 6, column 9): class 1 with a UCC of 10000 (maximum 10000 x 4% =
# 400.00, claimed in full) and class 8 with a UCC of 2000 and additions of 5000, all DIEPs
# (column 4 5000), of which 3000 is expensed at once (column 9): column 21 is 3000.00 x 20% =
# 600.00 plus 3000, so 3600.00, claimed in full.
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

RETURN_BS_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "24000"),),
    "rental_expenses": {
        "insurance": ("1200", "0", "0"),
        "interest_and_bank_charges": ("6000", "0", "0"),
        "repairs_and_maintenance": ("1300", "0", "0"),
        "property_taxes": ("3500", "0", "0"),
    },
    "rental_cca_classes_rows": (CLASS_1_ROW, CLASS_8_ROW),
    **AREA_G,
}


def return_bs(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return BS's inputs, as in `returns/2025_return_bs.yaml`: Return AV's landlord without
    Chart B, with two Area A classes, one of which has a DIEP expensed at once, and Area G.

    Gross rents of 24000 (one property, two units) are the only income; the expenses are the
    insurance 1200, the interest 6000, the property taxes 3500 and the repairs 1300, 12000 in all.
    The claims are 400.00 and 3600.00, so line 9936 is 4000.00 and line 9946 and T1 line 12600 are
    12000 - 4000.00 = 8000.00.
    """
    return rental_return(RETURN_BS_STATEMENT, changes, **overrides)


def class_8_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str]:
    """Class 8 of Return BS with the given claim (column 23) and column 9."""
    return ("8", "2000", "5000", "0", "0", "0", claim, 0, "5000", "0", expensed, "0")


def test_return_bss_class_8_works_the_diep_columns_to_a_column_21_of_3600() -> None:
    # Area A, class 8: column 7 is 2000 + 5000 - 0 = 7000; column 8 is column 4 minus column 6,
    # 5000 - 0 = 5000, not more than column 7; column 9 is a chosen 3000, not more than column 8;
    # column 10 is 5000 - 3000 = 2000 and column 13 is 7000 - 3000 = 4000; columns 11, 12, 14, 15,
    # 16 and 17 are 0; column 18 is one half x (2000 - 0 - 0 - 0) = 1000.00; column 19 is 4000 + 0
    # + 0 - 1000.00 = 3000.00; the maximum (column 19 x column 20) is 3000.00 x 20% = 600.00 and
    # column 21 is 600.00 + 3000 = 3600.00; column 22 is 0, so column 23, the claim, is 3600.00.
    # Class 1: column 7 and column 19 are 10000, the maximum 10000 x 4% = 400.00, claimed.
    result = return_bs()
    statement = result["ca/t776"][0]
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    for line in (
        "rental_cca_table_claim: item 1 class 1: column 7 10000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 10000, "
        "maximum 4% of column 19 = 400 (half-up to 0.01), claim 400",
        "rental_cca_table_claim: item 2 class 8: column 7 7000, column 9 3000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 1000, column 19 3000, "
        "maximum 20% of column 19 = 600 (half-up to 0.01), claim 3600",
        "rental_cca_table_claim: item 1 400 + item 2 3600 = 4000",
    ):
        assert line in rendered, line
    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("4000.00")


def test_return_bss_line_i_is_3000_the_total_of_column_9() -> None:
    # Line i "Total immediate expensing claim for the year: Total of column 9" is 0 + 3000 = 3000,
    # within the least of Note 5's three amounts: the immediate expensing limit 600000.00, the
    # UCC of DIEPs in column 8 (0 + 5000 = 5000) and the income before CCA, amount 5, 12000.
    result = return_bs()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")
    assert isinstance(
        statement.producer_of(RENTAL_IMMEDIATE_EXPENSING_CLAIM), ImmediateExpensingClaim
    )
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("12000")


def test_return_bss_trace_shows_each_class_of_line_i() -> None:
    result = return_bs()
    rendered = EnglishTraceRenderer().render_all(result["ca/t776"][0].trace)

    for line in (
        "rental_immediate_expensing_claim: item 1 class 1: column 4 0 less column 6 0, "
        "column 7 10000: column 8 0, column 9 0",
        "rental_immediate_expensing_claim: item 2 class 8: column 4 5000 less column 6 0, "
        "column 7 7000: column 8 5000, column 9 3000",
        "rental_immediate_expensing_claim: item 1 0 + item 2 3000 = 3000",
    ):
        assert line in rendered, line


def test_return_bss_line_iii_is_600000_from_40_percent_of_1_5_million() -> None:
    # Note 5 and Area G: the filer is associated with one EPOP (1) and an agreement was filed (1),
    # so the limit is amount iii. "Line iii: Immediate expensing limit allocated to you: Multiply
    # $1.5 million by the percentage assigned to you in column 3 (see note 11)": 1500000 x 40% =
    # 600000.00. The total of column 3 is 100, so 100% less it is 0, not negative, and Note 11
    # ("If the total of column 3 is more than 100%, enter "0."") does not apply. Line iii times the
    # 1 agreement filed is 600000.00, chosen by the 1 for associated over the $1.5 million; no
    # amount is allocated by the minister (0), so the limit is 600000.00.
    result = return_bs()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CAP).value == D("1500000")
    assert statement.get(RENTAL_EPOP_PERCENTAGE_MAXIMUM).value == D("100")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_SHARE).value == D("600000.00")
    assert statement.get(RENTAL_EPOP_PERCENTAGE_ROOM).value == D("0")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_ALLOCATED).value == D("600000.00")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT).value == D("600000.00")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER).value == D("600000.00")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")


def test_return_bss_trace_shows_the_limit_chain() -> None:
    result = return_bs()
    rendered = EnglishTraceRenderer().render_all(result["ca/t776"][0].trace)

    for line in (
        "rental_immediate_expensing_cap: credit amount 1500000 (half-up to 0.01)",
        "rental_epop_percentage_maximum: credit amount 100 (half-up to 0.01)",
        "rental_immediate_expensing_share: rental_epop_percentage 40% of "
        "rental_immediate_expensing_cap 1500000 = 600000 (half-up to 0.01)",
        "rental_epop_percentage_room: rental_epop_percentage_maximum 100 less "
        "rental_epop_percentage_total 100 = 0",
        "rental_immediate_expensing_allocated: rental_immediate_expensing_share 600000, "
        "chosen as rental_epop_percentage_room 0 is zero",
        "rental_immediate_expensing_associated_limit: rental_immediate_expensing_allocated "
        "600000 for each of 1 rental_epop_agreement_filed_checked = 600000",
        "rental_immediate_expensing_limit_before_minister: "
        "rental_immediate_expensing_associated_limit 600000, chosen as "
        "rental_epop_associated_checked is 1",
        "rental_immediate_expensing_limit_before_proration: "
        "rental_immediate_expensing_limit_before_minister 600000, chosen as "
        "rental_minister_allocation_given_checked is 0",
        "rental_immediate_expensing_limit: rental_immediate_expensing_limit_before_proration "
        "600000 = 600000, not prorated as rental_fiscal_period_days 365 is not below 357 days",
    ):
        assert line in rendered, line


def test_return_bss_line_ii_and_line_9936_are_4000_within_amount_5() -> None:
    # Line ii, the total of column 23, is 400.00 + 3600.00 = 4000.00, so is line 9936 (no personal
    # part of CCA, no CCA for business-use-of-home expenses), within the 12000 of amount 5.
    result = return_bs()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("12000")
    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("4000.00")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("12000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("4000.00")


def test_return_bss_net_rental_income_is_8000_on_line_12600() -> None:
    # Amount 6 is amount 5 less line 9936: 12000 - 4000.00 = 8000.00, which is line 9946 and T1
    # line 12600. It is the whole of total income.
    result = return_bs()
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("8000.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("8000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("8000.00")


def test_return_bss_closing_ucc_is_9600_for_class_1_and_3400_for_class_8() -> None:
    # Column 24 is column 7 less column 23: 10000 - 400.00 = 9600.00 and 7000 - 3600.00 =
    # 3400.00 (the claim includes the 3000 of column 9).
    result = return_bs()
    statement = result["ca/t776"][0]

    records = statement.get(RENTAL_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("1"), D("9600.00")),
        (D("8"), D("3400.00")),
    ]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert "rental_closing_ucc: item 1 class 1: column 7 10000 less claim 400 = 9600" in rendered
    assert (
        "rental_closing_ucc: item 2 class 8: column 7 7000 less claim 3600 "
        "(including column 9 3000) = 3400"
    ) in rendered


def test_return_bss_figures_that_depend_on_income_are_return_avs_recomputed_for_8000() -> None:
    # Net income and taxable income are 8000.00 (no deductions). The federal tax on it is
    # 8000.00 x 14.5% = 1160.00 and the Ontario tax 8000.00 x 5.05% = 404.00; each is below its
    # non-refundable credits (2338.71 and 643.72), so there is no tax payable and the refund or
    # balance owing is 0.
    result = return_bs()
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(NET_INCOME).value == D("8000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("8000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("1160.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("404.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_a_filer_not_associated_with_an_epop_has_the_whole_1_5_million() -> None:
    # Note 5 "$1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year": the Area G answers are not read, so the 40 and the
    # total of 150 (more than 100%) change nothing.
    statement = return_bs(
        {
            "rental_epop_associated": 0,
            "rental_epop_agreement_filed": 0,
            "rental_epop_percentage": "40",
            "rental_epop_percentage_total": "150",
        }
    )["ca/t776"][0]

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")


def test_an_associated_filer_with_no_agreement_filed_has_a_limit_of_zero() -> None:
    # Note 5 "zero, if you are associated with one or more EPOPs and an agreement that assigns a
    # percentage to one or more of the associated EPOPs was not filed with the minister in a
    # prescribed form": the limit is 0, below the 3000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bs({"rental_epop_agreement_filed": 0})

    assert str(raised.value) == (
        "ca/t776, instance 1: total of column 9 (3000) is above the immediate expensing limit (0)"
    )


def test_a_total_of_column_3_above_100_gives_a_limit_of_zero() -> None:
    # Note 11 "If the total of column 3 is more than 100%, enter "0."": 100% less 100.01 is
    # negative, so line iii is 0.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bs({"rental_epop_percentage_total": "100.01"})

    assert str(raised.value) == (
        "ca/t776, instance 1: total of column 9 (3000) is above the immediate expensing limit (0)"
    )


def test_a_total_of_column_3_of_exactly_100_is_not_more_than_100() -> None:
    # 100% less 100 is 0, which is not negative: line iii is 1500000 x 100% = 1500000.00.
    statement = return_bs({"rental_epop_percentage": "100"})["ca/t776"][0]

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_ALLOCATED).value == D("1500000.00")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000.00")


def test_a_percentage_of_0_2_gives_a_limit_of_exactly_the_3000_of_column_9() -> None:
    # Line iii is 1500000 x 0.2% = 3000.00; a total above the limit is refused, not one equal to it.
    statement = return_bs({"rental_epop_percentage": "0.2"})["ca/t776"][0]

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_ALLOCATED).value == D("3000.00")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")


def test_a_percentage_of_0_1_gives_a_limit_of_1500_so_column_9_is_refused() -> None:
    # Line iii is 1500000 x 0.1% = 1500.00, below the 3000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bs({"rental_epop_percentage": "0.1"})

    assert str(raised.value) == (
        "ca/t776, instance 1: total of column 9 (3000) is above the immediate expensing limit "
        "(1500.00)"
    )


def test_an_amount_allocated_by_the_minister_replaces_the_limit() -> None:
    # Note 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": with no agreement filed the limit would be 0, but the minister's 5000 is the
    # limit; 2000 is below the 3000 of column 9.
    statement = return_bs(
        {
            "rental_epop_agreement_filed": 0,
            "rental_minister_allocation_given": 1,
            "rental_minister_allocation": "5000",
        }
    )["ca/t776"][0]

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT).value == D("5000")
    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")
    with pytest.raises(InputAboveBoundError) as raised:
        return_bs(
            {
                "rental_epop_agreement_filed": 0,
                "rental_minister_allocation_given": 1,
                "rental_minister_allocation": "2000",
            }
        )
    assert str(raised.value) == (
        "ca/t776, instance 1: total of column 9 (3000) is above the immediate expensing limit "
        "(2000)"
    )


def test_a_column_9_total_above_the_income_before_cca_is_refused() -> None:
    # Note 5 "the amount of income, if any, earned from the source of income that is a property
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": amount 5
    # is 12000. Class 8 with additions of 20000, all DIEPs, expenses 13000 at once: the limit
    # 600000.00 and the UCC of DIEPs 20000 are not passed, the income 12000 is. A personal part of
    # CCA of 1500 (a chosen figure) keeps line 9936, 13400.00 - 1500 = 11900.00, within amount 5.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bs(
            {
                "rental_cca_classes_rows": (
                    CLASS_1_ROW,
                    (
                        "8",
                        "2000",
                        "20000",
                        "0",
                        "0",
                        "0",
                        "13000.00",
                        0,
                        "20000",
                        "0",
                        "13000",
                        "0",
                    ),
                ),
                "rental_cca_personal_part": "1500",
            }
        )

    assert str(raised.value) == (
        "ca/t776, instance 1: total of column 9 (13000) is above the income before CCA (12000)"
    )


def test_a_column_9_above_column_8_is_refused_naming_the_class() -> None:
    # Note 4 and Note 5: column 8 is 5000, so a column 9 of 5001 is refused.
    with pytest.raises(InvalidRecordError) as raised:
        return_bs({"rental_cca_classes_rows": (CLASS_1_ROW, class_8_row("3600.00", "5001"))})

    assert (
        str(raised.value) == "ca/t776, instance 1: item 2: column 9 (5001) is above column 8 (5000)"
    )


def test_a_class_8_claim_below_column_9_is_refused() -> None:
    # Column 23 is column 21 less column 22, column 21 including column 9 (3000): with a column 22
    # of 0 the claim is at least the 3000.
    with pytest.raises(InputBelowBoundError) as raised:
        return_bs({"rental_cca_classes_rows": (CLASS_1_ROW, class_8_row("2999.99", "3000"))})

    assert str(raised.value) == (
        "ca/t776, instance 1: item 2: ca/cca_claimed 2999.99 is below the minimum 3000"
    )


def test_a_class_8_claim_above_column_21_is_refused() -> None:
    # Column 21 is 600.00 + 3000 = 3600.00.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bs({"rental_cca_classes_rows": (CLASS_1_ROW, class_8_row("3600.01", "3000"))})

    assert str(raised.value) == (
        "ca/t776, instance 1: item 2: ca/cca_claimed 3600.01 is above the maximum 3600.00"
    )


def test_a_return_with_no_diep_has_a_line_i_of_zero() -> None:
    # Class 8 without column 4 and column 9 (a plain 2000 + 5000 of additions): line i is 0 and
    # the claim is the maximum, column 19 = 7000 - 2500.00 = 4500.00 x 20% = 900.00.
    statement = return_bs(
        {
            "rental_cca_classes_rows": (
                CLASS_1_ROW,
                ("8", "2000", "5000", "0", "0", "0", "900.00", 0, "0", "0", "0", "0"),
            )
        }
    )["ca/t776"][0]

    assert statement.get(RENTAL_IMMEDIATE_EXPENSING_CLAIM).value == D("0")
    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("1300.00")
