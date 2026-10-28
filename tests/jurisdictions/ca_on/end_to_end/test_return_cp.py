"""CA-ON 2025 end to end: return cp."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError, InvalidRecordError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
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
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_RECAPTURED_CCA,
    RENTAL_TERMINAL_LOSS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, RentalCcaRow, rental_return

# Return CP's figures, by hand (Guide T4036 2025, "Class 1 (4%)", Form T776 Area A). Gross rents
# 24000 less the expenses insurance 1200, repairs 800 and property taxes 2100, 4100 in all, make
# amount 5, the net income before the capital cost allowance, 19900. Class 1 has the half-year
# rule, an AII factor of 0 and an RII factor of one half; each row below has no UCC at the start,
# no disposition and no AIIP or RIIP, so column 7 is its additions, columns 14 to 17 are 0,
# column 18 is one half of its additions and column 19 is the other half.
#
# Row 1, election 1 (a new purpose-built residential rental, 10%): column 3 200000.00; column 7
#   200000.00; column 18 100000.00; column 19 200000.00 - 100000.00 = 100000.00; the maximum
#   (column 21) 100000.00 x 10% = 10000.00, claimed; column 24 200000.00 - 10000.00 = 190000.00.
# Row 2, election 2 (a non-residential building in a separate class, 6%): column 3 50000.00;
#   column 7 50000.00; column 18 25000.00; column 19 25000.00; the maximum 25000.00 x 6% =
#   1500.00, claimed; column 24 50000.00 - 1500.00 = 48500.00.
# Row 3, no election (the class's 4%): column 3 20000.00; column 7 20000.00; column 18 10000.00;
#   column 19 10000.00; the maximum 10000.00 x 4% = 400.00, claimed; column 24 20000.00 - 400.00 =
#   19600.00.
# Line ii, the total of column 23: 10000.00 + 1500.00 + 400.00 = 11900.00, at most amount 5
# (19900), so line 9936 is 11900.00 and amount 6, line 9946 and T1 line 12600 are 19900 -
# 11900.00 = 8000.00, the net rental income of Return BS, so every figure that depends on income
# is Return BS's.
PURPOSE_BUILT_RENTAL = ("1", "0", "200000.00", "0", "0", "0", "10000.00", 0, "0", "0", "0", "0", 1)
SEPARATE_CLASS = ("1", "0", "50000.00", "0", "0", "0", "1500.00", 0, "0", "0", "0", "0", 2)
NO_ELECTION = ("1", "0", "20000.00", "0", "0", "0", "400.00", 0, "0", "0", "0", "0", 0)
ROWS: tuple[RentalCcaRow, ...] = (PURPOSE_BUILT_RENTAL, SEPARATE_CLASS, NO_ELECTION)

RETURN_CP_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "24000"),),
    "rental_expenses": {
        "insurance": ("1200", "0", "0"),
        "repairs_and_maintenance": ("800", "0", "0"),
        "property_taxes": ("2100", "0", "0"),
    },
    "rental_cca_classes_rows": ROWS,
}


def return_cp(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CP's inputs, as in `returns/2025_return_cp.yaml`: Return BS's landlord with three
    Class 1 buildings bought in the year, at the rate of their election (10%, 6% and the class's
    4%), and no immediate expensing.

    Gross rents of 24000 (one property, two units) are the only income; the expenses are the
    insurance 1200, the repairs 800 and the property taxes 2100, 4100 in all. The claim is
    11900.00, so line 9936 is 11900.00 and line 9946 and T1 line 12600 are 24000 - 4100 -
    11900.00 = 8000.00, the net rental income of Return BS.
    """
    return rental_return(RETURN_CP_STATEMENT, changes, **overrides)


def row_of(
    additions: str, claim: str, election: int
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str, int]:
    """A Class 1 row of additions bought in the year with the given claim and election."""
    return ("1", "0", additions, "0", "0", "0", claim, 0, "0", "0", "0", "0", election)


def test_return_cps_purpose_built_rental_is_claimed_at_10_percent() -> None:
    # Row 1: column 19 is 100000.00 and the maximum 10% of it, 10000.00 (4% would give 4000.00).
    rendered = EnglishTraceRenderer().render_all(return_cp()["ca/t776"][0].trace)

    assert (
        "rental_cca_table_claim: item 1 class 1: column 7 200000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 100000, column 19 100000, "
        "maximum 10% of column 19 = 10000 (half-up to 0.01), claim 10000"
    ) in rendered


def test_return_cps_separate_class_building_is_claimed_at_6_percent() -> None:
    # Row 2: column 19 is 25000.00 and the maximum 6% of it, 1500.00.
    rendered = EnglishTraceRenderer().render_all(return_cp()["ca/t776"][0].trace)

    assert (
        "rental_cca_table_claim: item 2 class 1: column 7 50000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 25000, column 19 25000, "
        "maximum 6% of column 19 = 1500 (half-up to 0.01), claim 1500"
    ) in rendered


def test_return_cps_building_without_an_election_keeps_the_class_rate_of_4_percent() -> None:
    # Row 3: column 19 is 10000.00 and the maximum 4% of it, 400.00.
    rendered = EnglishTraceRenderer().render_all(return_cp()["ca/t776"][0].trace)

    assert (
        "rental_cca_table_claim: item 3 class 1: column 7 20000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 10000, column 19 10000, "
        "maximum 4% of column 19 = 400 (half-up to 0.01), claim 400"
    ) in rendered


def test_return_cps_line_9936_is_11900_within_amount_5() -> None:
    # Line ii is 10000.00 + 1500.00 + 400.00 = 11900.00; amount 5 is 24000 - 4100 = 19900, so
    # the limit does not bind; there is no recapture and no terminal loss.
    statement = return_cp()["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("11900.00")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("19900")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("11900.00")
    assert statement.get(RENTAL_RECAPTURED_CCA).value == D("0")
    assert statement.get(RENTAL_TERMINAL_LOSS).value == D("0")


def test_return_cps_closing_ucc_is_each_rows_column_7_less_its_claim() -> None:
    # Column 24 is column 7 less column 23: 200000.00 - 10000.00, 50000.00 - 1500.00 and
    # 20000.00 - 400.00.
    statement = return_cp()["ca/t776"][0]

    records = statement.get(RENTAL_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("1"), D("190000.00")),
        (D("1"), D("48500.00")),
        (D("1"), D("19600.00")),
    ]


def test_return_cps_net_rental_income_is_8000_on_line_12600() -> None:
    # Amount 5 is 24000 - 4100 = 19900; amount 6 is 19900 - 11900.00 = 8000.00, which is line
    # 9946 and T1 line 12600. It is the whole of total income.
    result = return_cp()
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("19900")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("8000.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("8000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("8000.00")


def test_return_cps_tax_lines_are_return_bss() -> None:
    # Net income and taxable income are 8000.00 (no deductions), as in Return BS: the federal tax
    # on it is 8000.00 x 14.5% = 1160.00 and the Ontario tax 8000.00 x 5.05% = 404.00, each below
    # its non-refundable credits, so there is no tax payable.
    worksheet = return_cp()["ca-on/return"][0]

    assert worksheet.get(NET_INCOME).value == D("8000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("8000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("1160.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("404.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_without_the_election_the_purpose_built_rental_is_claimed_at_4_percent() -> None:
    # Election 0: the maximum is 4% of 100000.00, 4000.00; a claim of 10000.00 is refused.
    rows = (row_of("200000.00", "4000.00", 0),)
    statement = return_cp({"rental_cca_classes_rows": rows})["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("4000.00")
    with pytest.raises(InputAboveBoundError) as raised:
        return_cp({"rental_cca_classes_rows": (row_of("200000.00", "10000.00", 0),)})
    assert str(raised.value) == (
        "ca/t776, instance 1: item 1: ca/cca_claimed 10000.00 is above the maximum 4000.00"
    )


def test_a_claim_above_the_maximum_at_the_elected_rate_is_refused() -> None:
    # Election 1: the maximum is 10000.00; one cent more is refused.
    with pytest.raises(InputAboveBoundError) as raised:
        return_cp({"rental_cca_classes_rows": (row_of("200000.00", "10000.01", 1),)})

    assert str(raised.value) == (
        "ca/t776, instance 1: item 1: ca/cca_claimed 10000.01 is above the maximum 10000.00"
    )


def test_an_election_the_class_does_not_list_is_refused() -> None:
    # Class 1 lists the elections 1, 2 and 3; a 4 is not a rate the class has.
    with pytest.raises(InvalidRecordError, match=r"^ca/t776, instance 1: item 1: .*election 4\b"):
        return_cp({"rental_cca_classes_rows": (row_of("200000.00", "0", 4),)})


def test_an_election_on_a_class_that_lists_none_is_refused() -> None:
    # Class 8 (20%) lists no election.
    rows = (("8", "0", "10000.00", "0", "0", "0", "0", 0, "0", "0", "0", "0", 1),)
    with pytest.raises(InvalidRecordError, match=r"^ca/t776, instance 1: item 1: .*election 1\b"):
        return_cp({"rental_cca_classes_rows": rows})
