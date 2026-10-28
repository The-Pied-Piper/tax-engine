"""CA-ON 2025 end to end: return eb, Guide T4036's short-term rentals example (Kevin)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    GROSS_RENTAL_INCOME,
    NET_INCOME,
    NET_RENTAL_INCOME,
    REFUND_OR_BALANCE_OWING,
    RENTAL_DEDUCTIBLE_EXPENSES,
    RENTAL_EXPENSES_LESS_PERSONAL_PORTION,
    RENTAL_GROSS_RENTS,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    RENTAL_NON_COMPLIANT_EXPENSES,
    RENTAL_PERSONAL_PORTION,
    RENTAL_SHORT_TERM_PORTION,
    RENTAL_TOTAL_EXPENSES,
    SHORT_TERM_RENTAL_GROSS_RENTS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

# Guide T4036 "Example" (pages 18 and 19): the Chart A rows are the guide's, the rents and the
# other expenses are chosen figures.
RETURN_EB_STATEMENT: dict[str, Any] = {
    "rental_properties": ((1, "3000", "3000"), (2, "1500", "7500"), (1, "1400", "1400")),
    "rental_expenses": {
        "insurance": ("4300", "0", "4300"),
        "repairs_and_maintenance": ("1000", "0", "0"),
    },
    "short_term_rental_units_rows": (("2100", 30, 84), ("1500", 35, 35), ("700", 0, 14)),
}


def return_eb(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return EB's inputs, as in `returns/2025_return_eb.yaml`: Kevin's three short-term rentals.

    Chart A's rows are the guide's (2100 for 30 of 84 days, 1500 for 35 of 35, 700 for 0 of 14),
    so the line 9365 total of 4300 (insurance's short-term portion) gives line 9366 of 2250.00.
    The chosen rents are 11900 in all (5900 of it short-term) and the chosen expenses 5300, so
    line 9369 and T1 line 12600 are 11900 - (5300 - 2250.00) = 8850.00.
    """
    return rental_return(RETURN_EB_STATEMENT, changes, **overrides)


def test_return_ebs_short_term_and_gross_rents_are_on_lines_8140_8141_and_12599() -> None:
    # Part 3: line 8140 is the short-term column, 3000 + 1500 + 1400 = 5900; line 8141 is the all
    # units column, 3000 + 7500 + 1400 = 11900; with no other income (line 8230), line 8299, and so
    # T1 line 12599, is 11900.
    result = return_eb()
    statement = result["ca/t776"][0]

    assert statement.get(SHORT_TERM_RENTAL_GROSS_RENTS).value == D("5900")
    assert statement.get(RENTAL_GROSS_RENTS).value == D("11900")
    assert statement.get(GROSS_RENTAL_INCOME).value == D("11900")


def test_return_ebs_part_4_totals_match_the_guide_on_lines_9365_and_9366() -> None:
    # Part 4: line A is 5300 (insurance 4300 and repairs 1000) and line 9949 is 0; line 9365 is the
    # short-term portion of the insurance, 4300, which is the Chart A column 3 total (2100 + 1500
    # + 700); line 9366 is the Chart A total, 2250.00, which the guide prints. Line 1 is
    # 5300 - 0 - 2250.00 = 3050.00.
    result = return_eb()
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_TOTAL_EXPENSES).value == D("5300")
    assert statement.get(RENTAL_PERSONAL_PORTION).value == D("0")
    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("4300")
    assert statement.get(RENTAL_NON_COMPLIANT_EXPENSES).value == D("2250.00")
    assert statement.get(RENTAL_EXPENSES_LESS_PERSONAL_PORTION).value == D("5300")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("3050.00")


def test_return_ebs_net_rental_income_is_8850_on_line_12600_and_the_only_income() -> None:
    # Line 9369 is 11900 - 3050.00 = 8850.00; with no co-owner, partner, recapture, terminal loss
    # or CCA, line 9946 and T1 line 12600 are 8850.00, the whole of total income, net income and
    # taxable income, below every tax threshold, so there is no tax and no refund or balance owing.
    result = return_eb()
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("8850.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("8850")
    assert worksheet.get(TOTAL_INCOME).value == D("8850.00")
    assert worksheet.get(NET_INCOME).value == D("8850.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("8850.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_return_eb_with_rental_1_short_term_days_of_500_is_worked_as_typed() -> None:
    # The form prints no maximum for Chart A column 5, so 500 is used as typed: row 1 is
    # 2100 x 30 / 500 = 126.00, line 9366 is 126.00 + 1500.00 + 0.00 = 1626.00 and line 1 is
    # 5300 - 0 - 1626.00 = 3674.00.
    changes = {
        "short_term_rental_units_rows": (("2100", 30, 500), ("1500", 35, 35), ("700", 0, 14))
    }

    statement = return_eb(changes)["ca/t776"][0]

    assert statement.get(RENTAL_NON_COMPLIANT_EXPENSES).value == D("1626.00")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("3674.00")


def test_return_ebs_trace_works_each_chart_a_row_on_its_own() -> None:
    # Column 6 of each row, as the guide prints it: 2100 x 30 / 84 = 750.00, 1500 x 35 / 35 =
    # 1500.00 and 700 x 0 / 14 = 0.00, each rounded half-up to the cent.
    result = return_eb()
    statement = result["ca/t776"][0]
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "rental_non_compliant_expenses: row 1: expenses 2100 for 30 non-compliant days of 84 "
        "short-term days = 750 (half-up to 0.01)"
    ) in rendered
    assert (
        "rental_non_compliant_expenses: row 2: expenses 1500 for 35 non-compliant days of 35 "
        "short-term days = 1500 (half-up to 0.01)"
    ) in rendered
    assert (
        "rental_non_compliant_expenses: row 3: expenses 700 for 0 non-compliant days of 14 "
        "short-term days = 0 (half-up to 0.01)"
    ) in rendered
    assert "rental_non_compliant_expenses: item 1 750 + item 2 1500 + item 3 0 = 2250" in rendered


# Form T776 Part 4, Return EB's insurance (a total of 1000 in the expense lines, the rest of the
# statement as above): the form prints no maximum for the personal portion or the short-term
# portion of a line, so each is used as typed, even above the line's total, and line 1 "Deductible
# expenses" (amount A minus line 9949 minus line 9366) is signed. The short-term portion of 4300
# keeps line 9365 at Chart A's column 3 total of 4300.


def insurance_changes(amounts: tuple[str, str, str]) -> dict[str, Any]:
    """Return EB's statement with insurance's (total, personal, short-term) amounts changed."""
    return {"rental_expenses": {**RETURN_EB_STATEMENT["rental_expenses"], "insurance": amounts}}


def above(part: str, bound: str) -> str:
    """The message of `core/at_most`: the part, its value, and the bound it is above."""
    return rf"{re.escape(part)} \S+ is above {re.escape(bound)} \S+"


def test_a_personal_portion_above_the_insurance_total_is_worked_as_typed() -> None:
    # Line A is 1000 + 1000 = 2000 and line 9949 is 1100, so amount A less line 9949 is 900;
    # line 9366 is 2250.00, so line 1 is 900 - 2250.00 = -1350.00 and line 9369 is
    # 11900 - (-1350.00) = 13250.00.
    result = return_eb(insurance_changes(("1000", "1100", "4300")))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_PERSONAL_PORTION).value == D("1100")
    assert statement.get(RENTAL_EXPENSES_LESS_PERSONAL_PORTION).value == D("900")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("-1350.00")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("13250.00")


def test_a_short_term_portion_above_the_insurance_total_is_worked_as_typed() -> None:
    # The short-term portion of 8000 is only added into line 9365, which Chart A's column 3
    # total of 4300 stays under; line 1 is 2000 - 0 - 2250.00 = -250.00 and line 9369 is
    # 11900 - (-250.00) = 12150.00.
    result = return_eb(insurance_changes(("1000", "0", "8000")))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("8000")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("-250.00")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("12150.00")


def test_a_personal_and_short_term_portion_together_above_the_insurance_total_are_worked() -> None:
    # Line 9949 is 800, line A 2000 and line 9366 2250.00, so line 1 is 2000 - 800 - 2250.00 =
    # -1050.00 and line 9369 is 11900 - (-1050.00) = 12950.00.
    result = return_eb(insurance_changes(("1000", "800", "4300")))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("-1050.00")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("12950.00")


# Form T776 Chart A column 3 "Related portion of the total from line 9365 of Part 4": the rows
# together are at most line 9365 (4300 here, insurance's short-term portion), so a sum above it is
# refused, not capped and not worked. Equal is valid.


def chart_a_changes(first: str) -> dict[str, Any]:
    """Return EB's Chart A rows with the first row's column 3 changed to `first`."""
    return {"short_term_rental_units_rows": ((first, 30, 84), ("1500", 35, 35), ("700", 0, 14))}


@pytest.mark.parametrize("first", ["4000", "99999"])
def test_chart_a_column_3_rows_above_line_9365_in_total_are_refused_not_worked(first: str) -> None:
    # 4000 + 1500 + 700 is 6200 against line 9365 of 4300; 99999 was an HTTP 500 before the check.
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/short_term_rental_related_expenses_total", "ca/rental_short_term_portion"),
    ):
        return_eb(chart_a_changes(first))


def test_chart_a_column_3_one_dollar_above_line_9365_in_total_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=above("ca/short_term_rental_related_expenses_total", "ca/rental_short_term_portion"),
    ):
        return_eb(chart_a_changes("2101"))


def test_chart_a_column_3_rows_equal_to_line_9365_in_total_are_valid() -> None:
    # 2600 + 1000 + 700 is 4300, equal to line 9365. Line B is 2600 x 30 / 84 = 928.57 (half-up),
    # plus 1000 x 35 / 35 = 1000 and 700 x 0 / 14 = 0, so 1928.57.
    changes = {"short_term_rental_units_rows": (("2600", 30, 84), ("1000", 35, 35), ("700", 0, 14))}
    statement = return_eb(changes)["ca/t776"][0]

    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("4300")
    assert statement.get(RENTAL_NON_COMPLIANT_EXPENSES).value == D("1928.57")


# Form T776 Part 3: a row's "Gross rents for short-term rentals" is part of its "Gross rents for all
# units", so a row whose short-term rents are above its gross rents is refused. Equal is valid.


def test_a_property_row_with_short_term_rents_above_its_gross_rents_is_refused() -> None:
    # Row 1 has 3001 of short-term rents against 3000 of gross rents: refused, not capped.
    with pytest.raises(
        InputAboveBoundError,
        match=(
            r"item 1: ca/rental_property_short_term_rents 3001 is above "
            r"ca/rental_property_gross_rents 3000"
        ),
    ):
        return_eb(
            {"rental_properties": ((1, "3001", "3000"), (2, "1500", "7500"), (1, "1400", "1400"))}
        )


def test_a_later_property_row_with_short_term_rents_above_its_gross_rents_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"item 3: ca/rental_property_short_term_rents 1401 is above",
    ):
        return_eb(
            {"rental_properties": ((1, "3000", "3000"), (2, "1500", "7500"), (1, "1401", "1400"))}
        )


def test_a_property_row_with_short_term_rents_equal_to_its_gross_rents_is_valid() -> None:
    # Row 2 is all short-term rents: 7500 of each, so line 8140 is 3000 + 7500 + 1400 = 11900 and
    # line 8141 is the same 11900.
    statement = return_eb(
        {"rental_properties": ((1, "3000", "3000"), (2, "7500", "7500"), (1, "1400", "1400"))}
    )["ca/t776"][0]

    assert statement.get(SHORT_TERM_RENTAL_GROSS_RENTS).value == D("11900")
    assert statement.get(RENTAL_GROSS_RENTS).value == D("11900")
