"""Registered kinds of Form T936 "Calculation of Cumulative Net Investment Loss (CNIL) to December
31, 2025", in the federal catalog family `t936` (`tax_calculator/jurisdictions/ca/catalog/t936.py`).

The form `ca/t936` runs once. Its five starting amounts are the printed lines the filer enters:
Part 3 line 15 (investment expenses of previous years), line 20 (investment income of previous
years), the 2024 part of line 17 (the amount from line 17218 of Form T2048 for 2024) and Chart A
lines 15 and 16 (boxes 21 and 30 of the 2025 T3 slips). Every other line is a step of the form
that reads the return's figures, so each printed line that computes is its own kind. The exports
are Chart A line 14 and Part 3 line C, which Form T657 Step 1 line 15 and Step 2 line 16 read.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import tax_calculator.jurisdictions.ca.catalog
from tax_calculator.domain.artifact import ArtifactRegistry
from tax_calculator.jurisdictions.ca.catalog import (
    T657_CUMULATIVE_NET_INVESTMENT_LOSS,
    T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    T936_ADDITIONAL_INVESTMENT_EXPENSES,
    T936_ADDITIONAL_INVESTMENT_INCOME,
    T936_CHART_A_LINE_3,
    T936_CHART_A_LINE_7,
    T936_CHART_A_LINE_8,
    T936_CHART_A_LINE_8_WHEN_NEGATIVE,
    T936_CHART_A_LINE_8_WHEN_POSITIVE,
    T936_CHART_A_LINE_9,
    T936_CHART_A_LINE_9_AT_INCLUSION_RATE,
    T936_CHART_A_LINE_11,
    T936_CHART_A_LINE_13,
    T936_CHART_A_LINE_14,
    T936_CHART_A_LINE_14_BEFORE_GATE,
    T936_CHART_A_LINE_14_WHEN_LINE_1_NEGATIVE,
    T936_CHART_A_LINE_14_WHEN_LINE_1_POSITIVE,
    T936_CHART_A_LINE_17,
    T936_CHART_A_LINE_19,
    T936_CHART_A_LINE_19_BEFORE_GATE,
    T936_CNIL,
    T936_CUMULATIVE_INVESTMENT_EXPENSES,
    T936_CUMULATIVE_INVESTMENT_INCOME,
    T936_EXPLORATION_EXPENSES_AT_HALF,
    T936_EXPLORATION_RECOVERY_INCOME_CHECKED,
    T936_INVESTMENT_EXPENSES_PREVIOUS_YEARS,
    T936_INVESTMENT_INCOME,
    T936_INVESTMENT_INCOME_PREVIOUS_YEARS,
    T936_LINE_16,
    T936_NET_RENTAL_INCOME,
    T936_NET_RENTAL_LOSS,
    T936_OTHER_INVESTMENT_EXPENSES,
    T936_OTHER_PROPERTY_INCOME,
    T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
    T936_PARTNERSHIP_LOSSES,
    T936_PARTNERSHIP_TAXABLE_CAPITAL_GAINS,
    T936_RECOVERY_OF_EXPLORATION_EXPENSES,
    T936_T3_BOX_21_CAPITAL_GAINS,
    T936_T3_BOX_30_CAPITAL_GAINS,
    T936_T2017_LINE_13,
    T936_T2048_LINE_17215,
    T936_T2048_LINE_17216,
    T936_T2048_LINE_17218,
    T936_T2048_LINE_17218_FOR_2024,
    T936_T2048_LINE_17218_FOR_2025,
    T936_TOTAL_INVESTMENT_EXPENSES,
    T936_TOTAL_INVESTMENT_INCOME,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The five starting amounts, each a non-negative amount as the filer enters it.
INPUTS = (
    T936_INVESTMENT_EXPENSES_PREVIOUS_YEARS,
    T936_INVESTMENT_INCOME_PREVIOUS_YEARS,
    T936_T2048_LINE_17218_FOR_2024,
    T936_T3_BOX_21_CAPITAL_GAINS,
    T936_T3_BOX_30_CAPITAL_GAINS,
)
# The computed amounts: one for each printed line that a step of the form computes (the lines that
# are another line's amount, such as Part 3 line 14 = line A, have no kind of their own), and the
# two "before the gate" amounts that the two "do not complete lines ... enter 0" instructions of
# Chart A switch off.
COMPUTED = (
    T936_NET_RENTAL_LOSS,
    T936_PARTNERSHIP_LOSSES,
    T936_EXPLORATION_EXPENSES_AT_HALF,
    T936_OTHER_INVESTMENT_EXPENSES,
    T936_ADDITIONAL_INVESTMENT_EXPENSES,
    T936_TOTAL_INVESTMENT_EXPENSES,
    T936_NET_RENTAL_INCOME,
    T936_INVESTMENT_INCOME,
    T936_PARTNERSHIP_TAXABLE_CAPITAL_GAINS,
    T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
    T936_OTHER_PROPERTY_INCOME,
    T936_EXPLORATION_RECOVERY_INCOME_CHECKED,
    T936_RECOVERY_OF_EXPLORATION_EXPENSES,
    T936_ADDITIONAL_INVESTMENT_INCOME,
    T936_TOTAL_INVESTMENT_INCOME,
    T936_LINE_16,
    T936_T2048_LINE_17218_FOR_2025,
    T936_T2048_LINE_17218,
    T936_CUMULATIVE_INVESTMENT_EXPENSES,
    T936_CUMULATIVE_INVESTMENT_INCOME,
    T936_CNIL,
    T936_T2048_LINE_17215,
    T936_CHART_A_LINE_3,
    T936_CHART_A_LINE_7,
    T936_T2017_LINE_13,
    T936_CHART_A_LINE_8_WHEN_POSITIVE,
    T936_CHART_A_LINE_8_WHEN_NEGATIVE,
    T936_CHART_A_LINE_8,
    T936_CHART_A_LINE_9,
    T936_CHART_A_LINE_9_AT_INCLUSION_RATE,
    T936_CHART_A_LINE_11,
    T936_T2048_LINE_17216,
    T936_CHART_A_LINE_13,
    T936_CHART_A_LINE_14_BEFORE_GATE,
    T936_CHART_A_LINE_14_WHEN_LINE_1_POSITIVE,
    T936_CHART_A_LINE_14_WHEN_LINE_1_NEGATIVE,
    T936_CHART_A_LINE_14,
    T936_CHART_A_LINE_17,
    T936_CHART_A_LINE_19_BEFORE_GATE,
    T936_CHART_A_LINE_19,
)
# The signed amounts: Chart A lines 3, 7, 8, 9, 11's product, 13, 17 and 19 print no floor (or "if
# negative, show in brackets"), and Part 2 line 10 and line B and Part 3 lines 18 and 21 print none
# either.
SIGNED_KINDS = (
    T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
    T936_TOTAL_INVESTMENT_INCOME,
    T936_CUMULATIVE_INVESTMENT_INCOME,
    T936_CUMULATIVE_INVESTMENT_EXPENSES,
    T936_CHART_A_LINE_3,
    T936_CHART_A_LINE_7,
    T936_T2017_LINE_13,
    T936_CHART_A_LINE_8_WHEN_POSITIVE,
    T936_CHART_A_LINE_8_WHEN_NEGATIVE,
    T936_CHART_A_LINE_8,
    T936_CHART_A_LINE_9,
    T936_CHART_A_LINE_9_AT_INCLUSION_RATE,
    T936_CHART_A_LINE_13,
    T936_CHART_A_LINE_17,
    T936_CHART_A_LINE_19_BEFORE_GATE,
    T936_CHART_A_LINE_19,
)
ALL_KINDS = (*INPUTS, *COMPUTED)


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module (its
    name is a constant of the declaration's call, which may take the catalog first)."""
    folder = Path(tax_calculator.jurisdictions.ca.catalog.__file__).parent
    for path in sorted(folder.glob("*.py")):
        body = ast.parse(path.read_text()).body
        for statement, following in zip(body, body[1:], strict=False):
            if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
                continue
            constants = [
                each.value for each in statement.value.args if isinstance(each, ast.Constant)
            ]
            if not (
                identifier.rpartition("/")[2] in constants
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                continue
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def test_the_t936_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t936_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_t936_kinds_have_the_identifiers_of_their_lines() -> None:
    assert {kind.identifier for kind in INPUTS} == {
        "ca/t936_investment_expenses_previous_years",
        "ca/t936_investment_income_previous_years",
        "ca/t936_t2048_line_17218_for_2024",
        "ca/t936_t3_box_21_capital_gains",
        "ca/t936_t3_box_30_capital_gains",
    }
    assert T936_CHART_A_LINE_14.identifier == "ca/t936_chart_a_line_14"
    assert T936_CNIL.identifier == "ca/t936_cnil"
    assert T936_ADDITIONAL_INVESTMENT_INCOME.identifier == "ca/t936_additional_investment_income"
    assert T936_TOTAL_INVESTMENT_EXPENSES.identifier == "ca/t936_total_investment_expenses"
    assert T936_TOTAL_INVESTMENT_INCOME.identifier == "ca/t936_total_investment_income"


def test_every_t936_kind_is_a_decimal_money_amount() -> None:
    for kind in ALL_KINDS:
        assert kind.value_type is Decimal, kind.identifier


def test_the_starting_amounts_are_non_negative_decimals() -> None:
    for kind in INPUTS:
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_signed_lines_of_the_form_are_signed_and_the_rest_are_not() -> None:
    for kind in SIGNED_KINDS:
        assert kind.non_negative is False, kind.identifier
        assert kind.identifier in SIGNED, kind.identifier
    for kind in ALL_KINDS:
        if kind in SIGNED_KINDS:
            continue
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_two_exports_and_chart_a_line_20_are_never_negative() -> None:
    # Chart A line 14 "(if negative, enter "0")", line 20 "(if negative, enter "0")" and line C
    # "(if negative, enter "0")".
    assert T936_CHART_A_LINE_14.non_negative is True
    assert T936_CNIL.non_negative is True
    assert T936_ADDITIONAL_INVESTMENT_INCOME.non_negative is True


def test_the_t936_kinds_are_not_counts_or_record_lists() -> None:
    for kind in ALL_KINDS:
        assert kind.identifier not in COUNTS | RECORD_LISTS, kind.identifier


def test_each_t936_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T936" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_starting_amounts_quote_their_printed_lines() -> None:
    quotes = {
        T936_INVESTMENT_EXPENSES_PREVIOUS_YEARS.identifier: (
            "Total investment expenses claimed in previous years after 1987",
            "Amount from line 16 in Part 3 of Form T936 for 2024",
        ),
        T936_INVESTMENT_INCOME_PREVIOUS_YEARS.identifier: (
            "Total investment income reported in previous years after 1987",
            "Amount from line 19 of Part 3 of Form T936 for 2024",
        ),
        T936_T2048_LINE_17218_FOR_2024.identifier: (
            "Amount from line 17218 of Form T2048 for 2024 to 2025",
        ),
        T936_T3_BOX_21_CAPITAL_GAINS.identifier: (
            "Enter the amount from box 21 of all 2025 T3 slips.",
        ),
        T936_T3_BOX_30_CAPITAL_GAINS.identifier: (
            "Enter the amount from box 30 of all 2025 T3 slips.",
        ),
    }
    for identifier, quoted in quotes.items():
        for quote in quoted:
            assert quote in squashed(docstring_of(identifier)), (identifier, quote)


def test_part_1_kinds_quote_their_printed_lines() -> None:
    quotes = {
        T936_NET_RENTAL_LOSS.identifier: "Net rental losses (line 12600)",
        T936_PARTNERSHIP_LOSSES.identifier: (
            "Limited or non-active partnership losses (line 12200) other than allowable capital "
            "losses"
        ),
        T936_EXPLORATION_EXPENSES_AT_HALF.identifier: (
            "50% of exploration and development expenses (line 22400)"
        ),
        T936_OTHER_INVESTMENT_EXPENSES.identifier: (
            "Any other investment expenses claimed in 2025 to earn property income"
        ),
        T936_ADDITIONAL_INVESTMENT_EXPENSES.identifier: (
            "enter whichever is less: line 20 in Chart A or line 25300 of your return"
        ),
        T936_TOTAL_INVESTMENT_EXPENSES.identifier: (
            "Add lines 1 to 7. Total investment expenses claimed in 2025"
        ),
    }
    for identifier, quote in quotes.items():
        assert quote in squashed(docstring_of(identifier)), identifier


def test_part_2_kinds_quote_their_printed_lines() -> None:
    quotes = {
        T936_INVESTMENT_INCOME.identifier: "Investment income (lines 12000 and 12100)",
        T936_NET_RENTAL_INCOME.identifier: (
            "Net rental income, including recaptured capital cost allowance (line 12600)"
        ),
        T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS.identifier: (
            "Net income from limited or non-active partnership (line 12200) other than taxable "
            "capital gains"
        ),
        T936_OTHER_PROPERTY_INCOME.identifier: "Any other property income reported in 2025",
        T936_RECOVERY_OF_EXPLORATION_EXPENSES.identifier: (
            "50% of income from the recovery of exploration and development expenses (line 13000)"
        ),
        T936_ADDITIONAL_INVESTMENT_INCOME.identifier: (
            'Line 14 minus line 19 (if negative, enter "0") Additional investment income'
        ),
        T936_TOTAL_INVESTMENT_INCOME.identifier: (
            "Add lines 8 to 13. Total investment income reported in 2025"
        ),
    }
    for identifier, quote in quotes.items():
        assert quote in squashed(docstring_of(identifier)), identifier


def test_part_3_kinds_quote_their_printed_lines() -> None:
    quotes = {
        T936_LINE_16.identifier: "Line 14 plus line 15",
        T936_T2048_LINE_17218.identifier: "Amount from line 17218 of Form T2048 for 2024 to 2025",
        T936_T2048_LINE_17218_FOR_2025.identifier: "line 17218 of Form T2048",
        T936_CUMULATIVE_INVESTMENT_EXPENSES.identifier: (
            "Cumulative investment expenses (line 16 minus line 17)"
        ),
        T936_CUMULATIVE_INVESTMENT_INCOME.identifier: (
            "Cumulative investment income (total of lines 19 and 20)"
        ),
        T936_CNIL.identifier: (
            'Line 18 minus line 21 (if negative, enter "0") CNIL to December 31, 2025'
        ),
    }
    for identifier, quote in quotes.items():
        assert quote in squashed(docstring_of(identifier)), identifier


def test_chart_a_kinds_quote_their_printed_lines() -> None:
    quotes = {
        T936_T2048_LINE_17215.identifier: "Amount from line 17215 of Form T2048",
        T936_CHART_A_LINE_3.identifier: "Line 1 minus line 2",
        T936_CHART_A_LINE_7.identifier: "Add lines 4 to 6 (if negative, show in brackets).",
        T936_T2017_LINE_13.identifier: "line 13 of Form T2017",
        T936_CHART_A_LINE_8.identifier: (
            "If you reported an amount on line 19200 of Schedule 3, enter the amount from line 13 "
            "of Form T2017"
        ),
        T936_CHART_A_LINE_9.identifier: "Line 7 plus line 8 (if negative, show in brackets)",
        T936_CHART_A_LINE_9_AT_INCLUSION_RATE.identifier: (
            "Line 9 multiplied by the percentage on line 10"
        ),
        T936_CHART_A_LINE_11.identifier: '(if negative, enter "0")',
        T936_T2048_LINE_17216.identifier: "Amount from line 17216 of Form T2048",
        T936_CHART_A_LINE_13.identifier: "Line 11 minus line 12",
        T936_CHART_A_LINE_14_BEFORE_GATE.identifier: (
            'Line 3 minus line 13 (if negative, enter "0")'
        ),
        T936_CHART_A_LINE_14.identifier: (
            'If the amount is "0", do not complete lines 2 to 17, and enter "0" on line 20'
        ),
        T936_CHART_A_LINE_17.identifier: "Line 15 minus line 16",
        T936_CHART_A_LINE_19_BEFORE_GATE.identifier: (
            "Line 17 multiplied by the percentage on line 18"
        ),
        T936_CHART_A_LINE_19.identifier: (
            'If the total from line 14 is "0", do not complete lines 15 to 19, and enter "0" on '
            "line 20"
        ),
    }
    for identifier, quote in quotes.items():
        assert quote in squashed(docstring_of(identifier)), identifier


def test_the_two_t657_lines_are_no_longer_starting_amounts() -> None:
    # Form T657 Step 1 line 15 and Step 2 line 16 are the totals of Form T936's exports now, so
    # their docstrings name the form and the export, and no longer call the figure "a starting
    # amount".
    for kind, export in (
        (T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS, "ca/t936.t936_chart_a_line_14"),
        (T657_CUMULATIVE_NET_INVESTMENT_LOSS, "ca/t936.t936_cnil"),
    ):
        text = squashed(docstring_of(kind.identifier))
        assert "starting amount" not in text, kind.identifier
        assert "T936" in text, kind.identifier
        assert export in text, kind.identifier
