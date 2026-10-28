"""CA-ON 2025 end to end: return ci."""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Decimal
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
    RENTAL_ADVERTISING_PERSONAL_PORTION,
    RENTAL_ADVERTISING_SHORT_TERM_PORTION,
    RENTAL_CCA_BUSINESS_USE_OF_HOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_PERSONAL_PART,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_COOWNER_CCA_CLAIM_CHECKED,
    RENTAL_COOWNER_CHECKED,
    RENTAL_COOWNER_RECAPTURED_CCA_CHECKED,
    RENTAL_COOWNER_SHARE_CHECKED,
    RENTAL_COOWNER_SHARE_LOWER_CHECKED,
    RENTAL_COOWNER_TERMINAL_LOSS_CHECKED,
    RENTAL_DEDUCTIBLE_EXPENSES,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    RENTAL_NET_INCOME_SHARE,
    RENTAL_PARTNER_CHECKED,
    RENTAL_PERSONAL_PORTION,
    RENTAL_RECAPTURED_CCA,
    RENTAL_SHORT_TERM_PORTION,
    RENTAL_TERMINAL_LOSS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import RENTAL_EXPENSE_KINDS, D, rental_return

# Area A rows as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
# property left, column 4, column 6, column 9, Note 9's remaining personal part): class 1 with a
# UCC of 100000.00 and proceeds of 40000.00 with property left, so column 7 is 60000.00 and the
# maximum 60000.00 x 4% = 2400.00, claimed in full; the remaining personal part of the property's
# cost is 5000.00, so column 24 is 60000.00 - 2400.00 - 5000.00 = 52600.00.
CLASS_1_ROW = ("1", "100000.00", "0", "40000.00", "0", "0", "2400.00", 0, "0", "0", "0", "5000.00")

RETURN_CI_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "24000"),),
    "rental_expenses": {
        "insurance": ("1200", "0", "0"),
        "interest_and_bank_charges": ("6000", "0", "0"),
        "repairs_and_maintenance": ("2900", "0", "0"),
        "property_taxes": ("3500", "0", "0"),
    },
    "rental_cca_classes_rows": (CLASS_1_ROW,),
}


def return_ci(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CI's inputs, as in `returns/2025_return_ci.yaml`: Return BS's landlord with one
    Area A class whose property was partly disposed of and had a personal part (Note 9), and no
    immediate expensing.

    Gross rents of 24000 (one property, two units) are the only income; the expenses are the
    insurance 1200, the interest 6000, the property taxes 3500 and the repairs 2900, 13600 in all.
    The claim is 2400.00, so line 9936 is 2400.00 and line 9946 and T1 line 12600 are
    24000 - 13600 - 2400.00 = 8000.00, the net rental income of Return BS.
    """
    return rental_return(RETURN_CI_STATEMENT, changes, **overrides)


def class_1_row(
    claim: str = "2400.00", personal_part: str = "5000.00"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str]:
    """Class 1 of Return CI with the given claim (column 23) and remaining personal part."""
    return ("1", "100000.00", "0", "40000.00", "0", "0", claim, 0, "0", "0", "0", personal_part)


def test_return_cis_class_1_closes_at_52600_after_the_remaining_personal_part() -> None:
    # Area A, class 1: column 7 is 100000.00 + 0 - 40000.00 = 60000.00; the maximum is 4% of
    # column 19, 60000.00, so 2400.00, claimed (column 23). Column 24 is column 7 minus column 23
    # (Note 9), less the remaining personal part of the property's cost: 60000.00 - 2400.00 -
    # 5000.00 = 52600.00.
    result = return_ci()
    statement = result["ca/t776"][0]

    records = statement.get(RENTAL_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("1"), D("52600.00")),
    ]


def test_return_cis_trace_names_the_remaining_personal_part() -> None:
    result = return_ci()
    rendered = EnglishTraceRenderer().render_all(result["ca/t776"][0].trace)

    for line in (
        "rental_cca_table_claim: item 1 class 1: column 7 60000, column 14 40000, column 15 0, "
        "column 16 40000, column 17 0, column 18 0, column 19 60000, "
        "maximum 4% of column 19 = 2400 (half-up to 0.01), claim 2400",
        "rental_closing_ucc: item 1 class 1: column 7 60000 less claim 2400 "
        "less personal part 5000 = 52600",
    ):
        assert line in rendered, line


def test_return_cis_personal_part_does_not_change_the_claim_or_the_recapture() -> None:
    # Note 9 changes only column 24: column 23 is still 2400.00 (line ii and line 9936), and
    # column 7 (60000.00) is positive with property left, so there is no recapture and no
    # terminal loss.
    result = return_ci()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("2400.00")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("10400")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("2400.00")
    assert statement.get(RENTAL_RECAPTURED_CCA).value == D("0")
    assert statement.get(RENTAL_TERMINAL_LOSS).value == D("0")


def test_return_cis_net_rental_income_is_8000_on_line_12600() -> None:
    # Amount 5 is 24000 - 13600 = 10400; amount 6 is 10400 - 2400.00 = 8000.00, which is line
    # 9946 and T1 line 12600. It is the whole of total income.
    result = return_ci()
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("10400")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("8000.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("8000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("8000.00")


def test_return_cis_tax_lines_are_return_bss() -> None:
    # Net income and taxable income are 8000.00 (no deductions), as in Return BS: the federal tax
    # on it is 8000.00 x 14.5% = 1160.00 and the Ontario tax 8000.00 x 5.05% = 404.00, each below
    # its non-refundable credits, so there is no tax payable.
    result = return_ci()
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(NET_INCOME).value == D("8000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("8000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("1160.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("404.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_a_personal_part_of_0_closes_the_class_at_column_7_less_the_claim() -> None:
    # 60000.00 - 2400.00 = 57600.00, and the line reads as one without a personal part.
    result = return_ci({"rental_cca_classes_rows": (class_1_row(personal_part="0"),)})
    statement = result["ca/t776"][0]

    (record,) = statement.get(RENTAL_CLOSING_UCC).value.records
    assert record[CCA_UCC_AT_END] == D("57600.00")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert "rental_closing_ucc: item 1 class 1: column 7 60000 less claim 2400 = 57600" in rendered
    assert statement.get(RENTAL_CCA_CLAIM).value == D("2400.00")


def test_a_personal_part_of_column_7_less_the_claim_closes_the_class_at_zero() -> None:
    # The part may be all that is left: 60000.00 - 2400.00 - 57600.00 = 0.00.
    result = return_ci({"rental_cca_classes_rows": (class_1_row(personal_part="57600.00"),)})

    (record,) = result["ca/t776"][0].get(RENTAL_CLOSING_UCC).value.records
    assert record[CCA_UCC_AT_END] == D("0")


def test_a_personal_part_above_column_7_less_the_claim_is_refused() -> None:
    # 57600.00 + 0.01 is more than the 57600.00 left after the claim.
    with pytest.raises(InvalidRecordError) as raised:
        return_ci({"rental_cca_classes_rows": (class_1_row(personal_part="57600.01"),)})

    assert str(raised.value) == (
        "ca/t776, instance 1: item 1: personal part (57600.01) is above column 7 less the claim "
        "(57600.00)"
    )


def test_a_smaller_claim_leaves_room_for_a_larger_personal_part() -> None:
    # With no claim, column 7 less the claim is 60000.00: a part of 60000.00 is allowed, and
    # 60000.01 is refused. The claim is not the personal part's to change: no CCA, line 9946 is
    # 10400 - 0 = 10400.00.
    result = return_ci({"rental_cca_classes_rows": (class_1_row("0", "60000.00"),)})

    (record,) = result["ca/t776"][0].get(RENTAL_CLOSING_UCC).value.records
    assert record[CCA_UCC_AT_END] == D("0")
    assert result["ca/t776"][0].get(RENTAL_CCA_CLAIM).value == D("0")
    with pytest.raises(InvalidRecordError) as raised:
        return_ci({"rental_cca_classes_rows": (class_1_row("0", "60000.01"),)})

    assert str(raised.value) == (
        "ca/t776, instance 1: item 1: personal part (60000.01) is above column 7 less the claim "
        "(60000.00)"
    )


def test_a_claim_above_the_maximum_is_still_refused_with_a_personal_part() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        return_ci({"rental_cca_classes_rows": (class_1_row("2400.01"),)})

    assert str(raised.value) == (
        "ca/t776, instance 1: item 1: ca/cca_claimed 2400.01 is above the maximum 2400.00"
    )


COUNT_FLAGS = (
    ("rental_coowner", RENTAL_COOWNER_CHECKED),
    ("rental_partner", RENTAL_PARTNER_CHECKED),
)


@pytest.mark.parametrize(
    ("flag", "value"),
    [("rental_coowner", 2), ("rental_coowner", 13), ("rental_partner", 2)],
)
def test_a_co_owner_or_partner_answer_above_1_is_refused_and_not_read_as_yes(
    flag: str, value: int
) -> None:
    # With the share left at 0 the statement's net income was 0 and no error was raised: a count
    # of 2 or 13 is an input error, not a yes.
    with pytest.raises(
        InputAboveBoundError, match=f"{flag} {value} is above a yes or no answer of 1"
    ):
        return_ci({flag: value})


@pytest.mark.parametrize(("flag", "checked_kind"), COUNT_FLAGS)
def test_a_co_owner_or_partner_answer_of_1_or_0_is_produced_as_it_is(
    flag: str, checked_kind: Any
) -> None:
    yes = return_ci({flag: 1})["ca/t776"][0]
    no = return_ci({flag: 0})["ca/t776"][0]

    assert yes.get(checked_kind).value == 1
    assert no.get(checked_kind).value == 0


@pytest.mark.parametrize(("flag", "checked_kind"), COUNT_FLAGS)
def test_the_trace_checks_the_co_owner_or_partner_answer_as_a_yes_or_no_count(
    flag: str, checked_kind: Any
) -> None:
    rendered = EnglishTraceRenderer().render_all(return_ci({flag: 1})["ca/t776"][0].trace)

    assert f"{checked_kind.label}: {flag} 1, a yes or no answer of 0 or 1" in rendered


# --- a co-owner and a partner, and a figure entered with the answer no (Form T776 lines 2 and 7) --
# The form prints no co-owner or partner question and no rule against a figure of the other holder:
# line 9946 is amount 6 for a sole proprietor or co-owner, and the partnership figure for a partner.


def test_a_partner_answer_0_with_a_5000_line_7_share_gives_line_9946_of_amount_6() -> None:
    # Amount 6 is 8000.00; the 5000 typed on line 7 is not in line 9946's arithmetic.
    result = return_ci({"rental_partner": 0, "rental_partner_share": "5000"})

    assert result["ca/t776"][0].get(RENTAL_NET_INCOME_AFTER_CCA).value == D("8000.00")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("8000.00")


def test_a_partner_answer_0_with_every_partner_figure_typed_keeps_amount_6() -> None:
    changes = {
        "rental_partner": 0,
        "rental_partner_share": "2000",
        "rental_partner_gst_hst_rebate": "250",
        "rental_partner_other_expenses": "150",
    }

    assert return_ci(changes)["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("8000.00")


def test_a_co_owner_answer_0_with_a_4000_line_2_share_keeps_amount_2_of_line_9369() -> None:
    # Amount 2 is line 9369 (10400.00 here), not the 4000 typed as the co-owner's share.
    result = return_ci({"rental_coowner": 0, "rental_coowner_share": "4000"})

    assert result["ca/t776"][0].get(RENTAL_NET_INCOME_SHARE).value == D("10400.00")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("8000.00")


def test_a_co_owner_answer_0_with_the_co_owner_cca_claim_keeps_the_table_claim() -> None:
    result = return_ci({"rental_coowner": 0, "rental_coowner_cca_claim": "300"})
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(NET_RENTAL_INCOME).value == D("8000.00")


def test_line_9945_is_subtracted_as_typed_with_the_co_owner_answer_0() -> None:
    # Line 3 prints "amount 2 minus line 9945" with no condition: 8000.00 - 500 = 7500.00.
    worksheet = return_ci({"rental_coowner": 0, "rental_coowner_other_expenses": "500"})

    assert worksheet["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("7500.00")


def test_co_owner_no_and_partner_yes_gives_the_partners_5000_not_the_co_owner_share() -> None:
    # No T5013 slip: amount 7 is 62.5% of amount 6, 8000.00, so 5000.00.
    changes = {
        "rental_coowner": 0,
        "rental_coowner_share": "4000",
        "rental_partner": 1,
        "rental_partner_percentage": "62.5",
    }

    assert return_ci(changes)["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("5000")


def test_a_co_owner_and_a_partner_both_yes_is_the_partnership_figure_of_500() -> None:
    # Line 33: a co-owner in a partnership reports as one; line 9946 is the partner's figure. No
    # T5013 slip: amount 6 is the co-owner's 1000 and amount 7 is 50% of it, 500.00.
    changes = {
        "rental_coowner": 1,
        "rental_coowner_share": "1000",
        "rental_partner": 1,
        "rental_partner_percentage": "50",
    }

    assert return_ci(changes)["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("500")


def test_a_co_owner_alone_with_its_share_is_accepted_and_its_share_is_the_net_income() -> None:
    worksheet = return_ci({"rental_coowner": 1, "rental_coowner_share": "1000"})["ca-on/return"][0]

    assert worksheet.get(NET_RENTAL_INCOME).value == D("1000")


def test_a_partner_alone_with_its_share_is_accepted_and_its_share_is_the_net_income() -> None:
    # No T5013 slip: amount 7 is 25% of amount 6, 8000.00, so 2000.00.
    worksheet = return_ci(
        {"rental_partner": 1, "rental_partner_t5013_slip": 0, "rental_partner_percentage": "25"}
    )["ca-on/return"][0]

    assert worksheet.get(NET_RENTAL_INCOME).value == D("2000")


def test_both_answers_0_with_no_figures_keeps_the_net_income_of_return_ci() -> None:
    worksheet = return_ci({"rental_coowner": 0, "rental_partner": 0})["ca-on/return"][0]

    assert worksheet.get(NET_RENTAL_INCOME).value == D("8000.00")


# Form T776 Part 4: the form prints no maximum for the personal portion or the short-term portion
# of an expense line, so each is used as typed, even above the line's total: line 9949 and line
# 9365 add them as entered and line 1 "Deductible expenses" (amount A minus line 9949 minus line
# 9366) is signed.

OTHER_EXPENSE_LINES = tuple(line for line in RENTAL_EXPENSE_KINDS if line != "advertising")
BASE_EXPENSES = {
    line: D(amounts[0]) for line, amounts in RETURN_CI_STATEMENT["rental_expenses"].items()
}


def expense_changes(line: str, amounts: tuple[str, str, str]) -> dict[str, Any]:
    """Return CI's statement with one expense line's (total, personal, short-term) amounts."""
    return {"rental_expenses": {**RETURN_CI_STATEMENT["rental_expenses"], line: amounts}}


def total_expenses(line: str, total: str) -> Decimal:
    """Line A of Return CI with the one line's total changed to `total`."""
    return sum(BASE_EXPENSES.values(), D("0")) - BASE_EXPENSES.get(line, D("0")) + D(total)


def above(part: str, bound: str) -> str:
    """The message of `core/at_most`: the part, its value, and the bound it is above."""
    return rf"{re.escape(part)} \S+ is above {re.escape(bound)} \S+"


def test_a_personal_portion_above_its_total_is_worked_as_typed() -> None:
    # Advertising has no total here (0) and a personal portion of 99999: line A is 13600 and line
    # 9949 is 99999, so line 1 is 13600 - 99999 = -86399 and line 9369 is 24000 + 86399 = 110399.
    result = return_ci(expense_changes("advertising", ("0", "99999", "0")))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_PERSONAL_PORTION).value == D("99999")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("-86399")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("110399")


@pytest.mark.parametrize("line", OTHER_EXPENSE_LINES)
def test_a_personal_portion_above_its_total_is_worked_as_typed_on_each_other_expense_line(
    line: str,
) -> None:
    # A total of 100 with a personal portion of 101: line 1 is line A less 101.
    statement = return_ci(expense_changes(line, ("100", "101", "0")))["ca/t776"][0]
    expected = total_expenses(line, "100") - D("101")

    assert statement.get(RENTAL_EXPENSE_KINDS[line][1]).value == D("101")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == expected
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("24000") - expected


def test_a_short_term_portion_above_the_total_is_worked_as_typed() -> None:
    # Advertising's total is 0 and its short-term portion 99999: line 9365 is 99999 and feeds no
    # other line (Chart A has no rows here), so line 1 and line 9369 are Return CI's 13600 and
    # 10400.
    statement = return_ci(expense_changes("advertising", ("0", "0", "99999")))["ca/t776"][0]

    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("99999")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("13600")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("10400")


@pytest.mark.parametrize("line", OTHER_EXPENSE_LINES)
def test_a_short_term_portion_above_the_total_is_worked_as_typed_on_each_other_expense_line(
    line: str,
) -> None:
    statement = return_ci(expense_changes(line, ("100", "0", "101")))["ca/t776"][0]

    assert statement.get(RENTAL_EXPENSE_KINDS[line][2]).value == D("101")
    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("101")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == total_expenses(line, "100")


def test_a_personal_and_short_term_portion_together_above_the_total_are_worked_as_typed() -> None:
    # Advertising 1000 with a personal portion of 800 and a short-term portion of 800: line A is
    # 14600, line 9949 is 800, line 9365 is 800 and line 1 is 14600 - 800 = 13800.
    statement = return_ci(expense_changes("advertising", ("1000", "800", "800")))["ca/t776"][0]

    assert statement.get(RENTAL_PERSONAL_PORTION).value == D("800")
    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("800")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("13800")


@pytest.mark.parametrize("line", OTHER_EXPENSE_LINES)
def test_a_personal_and_short_term_portion_together_above_the_total_are_worked_on_each_line(
    line: str,
) -> None:
    statement = return_ci(expense_changes(line, ("1000", "800", "800")))["ca/t776"][0]

    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == total_expenses(line, "1000") - D(
        "800"
    )


def test_a_personal_portion_equal_to_its_total_is_valid_and_the_return_is_unchanged() -> None:
    # The personal portion of advertising equals its total of 1000: the expenses less the personal
    # portion are the same 13600 as before, so line 9946 and T1 line 12600 stay 8000.00.
    result = return_ci(expense_changes("advertising", ("1000", "1000", "0")))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_ADVERTISING_PERSONAL_PORTION).value == D("1000")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("8000.00")


def test_a_short_term_portion_equal_to_its_total_is_valid() -> None:
    statement = return_ci(expense_changes("advertising", ("1000", "0", "1000")))["ca/t776"][0]

    assert statement.get(RENTAL_ADVERTISING_SHORT_TERM_PORTION).value == D("1000")


def test_the_personal_and_short_term_portions_that_together_equal_the_total_are_valid() -> None:
    statement = return_ci(expense_changes("advertising", ("1000", "600", "400")))["ca/t776"][0]

    assert statement.get(RENTAL_ADVERTISING_PERSONAL_PORTION).value == D("600")
    assert statement.get(RENTAL_ADVERTISING_SHORT_TERM_PORTION).value == D("400")


# Form T776 line 9936: the personal part of CCA and the CCA for business-use-of-home expenses are
# taken off amount ii (the claim of 2400.00 here) in turn. The form prints no maximum for either,
# so each is used as typed and line 9936 is signed: a claim below zero adds to line 9946.


def test_a_personal_part_of_cca_above_the_claim_is_worked_as_typed() -> None:
    # The claim is 2400.00 and the personal part 3000, so line 9936 is -600.00 and line 9946 is
    # 24000 - 13600 - (-600.00) = 11000.00.
    result = return_ci({"rental_cca_personal_part": "3000"})

    assert result["ca/t776"][0].get(RENTAL_CCA_CLAIM).value == D("-600.00")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("11000.00")


def test_a_cca_for_business_use_of_home_above_the_claim_is_worked_as_typed() -> None:
    # No personal part, so line 9936 is 2400.00 - 99999 = -97599.00 and line 9946 is
    # 10400 + 97599.00 = 107999.00.
    result = return_ci({"rental_cca_business_use_of_home": "99999"})

    assert result["ca/t776"][0].get(RENTAL_CCA_CLAIM).value == D("-97599.00")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("107999.00")


def test_a_personal_part_and_business_use_of_home_together_above_the_claim_are_worked() -> None:
    # 1500 and 1000 together are 100 above the claim of 2400.00: line 9936 is -100.00 and line
    # 9946 is 10400 + 100.00 = 10500.00.
    result = return_ci(
        {"rental_cca_personal_part": "1500", "rental_cca_business_use_of_home": "1000"}
    )

    assert result["ca/t776"][0].get(RENTAL_CCA_CLAIM).value == D("-100.00")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("10500.00")


def test_a_personal_part_equal_to_the_claim_is_valid_and_leaves_no_claim() -> None:
    # 2400.00 is the claim, so a personal part of 2400 is valid. Nothing is left for line 9936, so
    # line 9946 and T1 line 12600 are 24000 - 13600 = 10400.00.
    result = return_ci({"rental_cca_personal_part": "2400"})

    assert result["ca/t776"][0].get(RENTAL_CCA_PERSONAL_PART).value == D("2400")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("10400.00")


def test_a_personal_part_and_cca_for_business_use_of_home_that_equal_the_claim_are_valid() -> None:
    # 1400 and 1000 together are the claim of 2400.00: nothing is left, so line 9936 is 0 and line
    # 9946 is 10400.00.
    result = return_ci(
        {"rental_cca_personal_part": "1400", "rental_cca_business_use_of_home": "1000"}
    )
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_PERSONAL_PART).value == D("1400")
    assert statement.get(RENTAL_CCA_BUSINESS_USE_OF_HOME).value == D("1000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("0")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("10400.00")


def test_a_cca_for_business_use_of_home_equal_to_the_claim_is_valid() -> None:
    result = return_ci({"rental_cca_business_use_of_home": "2400"})

    assert result["ca/t776"][0].get(RENTAL_CCA_BUSINESS_USE_OF_HOME).value == D("2400")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("10400.00")


# Form T776 line 2 and the co-owner's figures of lines 9947 and 9948 and amount ii: each share is a
# part of its whole: at most the whole and, for a share of line 9369, of the sign of the whole and
# no larger in absolute value (a share of a loss is a loss no larger than the whole). A share above
# its whole is an input error, refused and not capped; a share equal to its whole is valid.


def co_owner(share: str, **figures: str) -> dict[str, Any]:
    """Return CI with the co-owner's answer 1 and its share of line 9369, and the figures given."""
    return {"rental_coowner": 1, "rental_coowner_share": share, **figures}


# Return CI with insurance of 15000 instead of 1200: the expenses are 27400, so line 9369 is
# 24000 - 27400 = -3400, a loss.
LOSS_CHANGES = expense_changes("insurance", ("15000", "0", "0"))


def test_a_co_owner_share_above_line_9369_is_refused_as_an_input_error() -> None:
    # Line 9369 is 10400.00 (24000 less 13600), so a share of 30000 is above it: `core/at_most`
    # refuses it (HTTP 422).
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/rental_coowner_share", "ca/rental_net_income_upper_bound"),
    ):
        return_ci(co_owner("30000"))


@pytest.mark.parametrize("share", ["-1000", "-30000"])
def test_a_negative_co_owner_share_of_a_positive_line_9369_is_refused(share: str) -> None:
    # A share of a positive whole is not below 0: the lower bound of line 9369 is 0, so -1000 and
    # -30000 are below it.
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/rental_net_income_lower_bound", "ca/rental_coowner_share_checked"),
    ):
        return_ci(co_owner(share))


@pytest.mark.parametrize("share", ["10400", "8000", "1000", "0"])
def test_a_co_owner_share_from_0_to_line_9369_is_valid_and_is_the_net_income(share: str) -> None:
    # 10400.00 is line 9369 itself, which is valid, and so is anything from 0 to it: the share is
    # the net income, line 9946 and T1 line 12600, with no claim, recapture or terminal loss.
    result = return_ci(co_owner(share))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_COOWNER_SHARE_CHECKED).value == D(share)
    assert statement.get(RENTAL_COOWNER_SHARE_LOWER_CHECKED).value == D("0")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D(share)


def test_a_co_owner_share_of_a_loss_between_the_loss_and_0_is_valid() -> None:
    # The whole is -3400: a share of -1000 is between it and 0, so it is the net income, and the
    # share of the whole itself, -3400, is valid too.
    for share in ("-1000", "-3400"):
        result = return_ci({**LOSS_CHANGES, **co_owner(share)})
        statement = result["ca/t776"][0]

        assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-3400")
        assert statement.get(RENTAL_COOWNER_SHARE_CHECKED).value == D(share)
        assert statement.get(RENTAL_COOWNER_SHARE_LOWER_CHECKED).value == D("-3400")
        assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D(share)


def test_a_positive_co_owner_share_of_a_loss_is_refused() -> None:
    # The whole is a loss of 3400, so its upper bound is 0: a share of 1000 is above it.
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/rental_coowner_share", "ca/rental_net_income_upper_bound"),
    ):
        return_ci({**LOSS_CHANGES, **co_owner("1000")})


def test_a_co_owner_share_of_a_loss_larger_than_the_loss_is_refused() -> None:
    # -5000 is below the loss of -3400, so the lower bound is above the share.
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/rental_net_income_lower_bound", "ca/rental_coowner_share_checked"),
    ):
        return_ci({**LOSS_CHANGES, **co_owner("-5000")})


def test_a_co_owner_share_of_recaptured_cca_above_the_classes_recapture_is_refused() -> None:
    # The classes of Return CI recapture 0, so a share of 5000 is above it (line 9947).
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/rental_coowner_recaptured_cca", "ca/rental_cca_table_recapture"),
    ):
        return_ci(co_owner("1000", rental_coowner_recaptured_cca="5000"))


def test_a_co_owner_share_of_the_terminal_loss_above_the_classes_is_refused() -> None:
    # The classes of Return CI have no terminal loss (0): a share of 5000 is above it (line 9948).
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/rental_coowner_terminal_loss", "ca/rental_cca_table_terminal_loss"),
    ):
        return_ci(co_owner("1000", rental_coowner_terminal_loss="5000"))


def test_a_co_owner_share_of_the_cca_claim_above_amount_ii_is_refused() -> None:
    # Amount ii is 2400.00, so a co-owner's share of 3000 is above it (Area A).
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/rental_coowner_cca_claim", "ca/rental_cca_table_claim"),
    ):
        return_ci(co_owner("8000", rental_coowner_cca_claim="3000"))


def test_co_owner_shares_equal_to_their_wholes_are_valid() -> None:
    # The recapture and the terminal loss of the classes are 0, and amount ii is 2400.00: shares
    # equal to each whole are valid. The claim share of 2400.00 is within the limit of 8000.00 (the
    # co-owner's share of line 9369, less the terminal loss), so line 9946 is 8000 - 2400 = 5600.00.
    result = return_ci(
        co_owner(
            "8000",
            rental_coowner_recaptured_cca="0",
            rental_coowner_terminal_loss="0",
            rental_coowner_cca_claim="2400",
        )
    )
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_COOWNER_RECAPTURED_CCA_CHECKED).value == D("0")
    assert statement.get(RENTAL_COOWNER_TERMINAL_LOSS_CHECKED).value == D("0")
    assert statement.get(RENTAL_COOWNER_CCA_CLAIM_CHECKED).value == D("2400")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("5600.00")
