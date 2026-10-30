"""Registered kinds of Form T1032, "Joint Election to Split Pension Income", in the federal catalog
family `t1032_pension_income_splitting`.

The form is `ca/t1032` (no instances, run once): Step 2, "Calculate the maximum split-pension
amount" (lines 1 to 21), Step 3 (line 22, the one elected amount, checked against line 21 and
carried on line 21000 or line 11600 of the return), Step 4 (the pension income amounts of lines
31400 for the transferring and the receiving spouse) and Step 5 (the income tax deducted, lines 35
to 42). The starting inputs are lines 1, 2, 4, 18, 32, 35, 37 and 40 and the two yes-or-no
answers; line 22 is an input too, entered once; T1 lines 21000 and 11600 are worked out from it.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    T1032_ELECTION_APPLIES,
    T1032_ELIGIBLE_PENSION_INCOME,
    T1032_FILER_IS_TRANSFERRING_SPOUSE,
    T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED,
    T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL,
    T1032_INCOME_TAX_DEDUCTED_ON_PENSION,
    T1032_LINE_1_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_2_CHECKED,
    T1032_LINE_3,
    T1032_LINE_4_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_5,
    T1032_LINE_7,
    T1032_LINE_8,
    T1032_LINE_8_BEFORE_GATE,
    T1032_LINE_12,
    T1032_LINE_13,
    T1032_LINE_15,
    T1032_LINE_16,
    T1032_LINE_17,
    T1032_LINE_18,
    T1032_LINE_18_MONTHS_IN_TAX_YEAR,
    T1032_LINE_19,
    T1032_LINE_21,
    T1032_LINE_21_IF_CONDITIONS_MET,
    T1032_LINE_21_IF_NOT_SEPARATED,
    T1032_LINE_22,
    T1032_LINE_22_CHECKED,
    T1032_LINE_22_TOTAL,
    T1032_LINE_29,
    T1032_LINE_30,
    T1032_LINE_31,
    T1032_LINE_31_AFTER_NOTE_1,
    T1032_LINE_33,
    T1032_LINE_34,
    T1032_LINE_35_CHECKED,
    T1032_LINE_35_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_35_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_36,
    T1032_LINE_37_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_39,
    T1032_LINE_39_TOTAL,
    T1032_LINE_42,
    T1032_LINE_42_TOTAL,
    T1032_LINE_31400,
    T1032_LINE_31400_RECEIVING,
    T1032_LINE_31400_RECEIVING_TOTAL,
    T1032_LINE_31400_TRANSFERRING,
    T1032_LINE_31400_TRANSFERRING_TOTAL,
    T1032_LINE_43700,
    T1032_MARITAL_STATUS_CHANGED,
    T1032_MARITAL_STATUS_CHANGED_CHECKED,
    T1032_MONTHS_IN_TAX_YEAR,
    T1032_MONTHS_IN_TAX_YEAR_CEILING,
    T1032_MONTHS_IN_TAX_YEAR_CHECKED,
    T1032_MONTHS_MARRIED,
    T1032_MONTHS_MARRIED_CHECKED,
    T1032_NOT_SEPARATED_90_DAYS,
    T1032_NOT_SEPARATED_90_DAYS_CHECKED,
    T1032_NOTE_1_APPLIES,
    T1032_NOTE_1_LINE_8_BOUND,
    T1032_NOTE_1_LINE_8_CHECKED,
    T1032_NOTE_1_LINE_8_TO_CHECK,
    T1032_NOTE_1_LINE_17,
    T1032_NOTE_1_LINE_17_IS_ZERO,
    T1032_NOTE_1_LINE_22,
    T1032_NOTE_1_LINE_29,
    T1032_NOTE_1_LINE_29_APPLIES,
    T1032_NOTE_1_LINE_30,
    T1032_NOTE_1_LINE_31,
    T1032_NOTE_1_LINE_32_LIMIT,
    T1032_NOTE_1_LINE_33,
    T1032_NOTE_1_PAYMENTS_A_TO_D,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_CHECKED,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_IF_APPLIES,
    T1032_NOTE_1_PAYMENTS_TO_REMOVE,
    T1032_NOTE_1_PAYMENTS_TOTAL,
    T1032_NOTE_1_PAYMENTS_TOTAL_IF_APPLIES,
    T1032_NOTE_1_RECALCULATION,
    T1032_NOTE_1_RESULT,
    T1032_NOTE_1_RESULT_LIMIT,
    T1032_OTHER_INCOME_OF_TRANSFERRING_SPOUSE,
    T1032_RCA_PAYMENTS_QUALIFY,
    T1032_RCA_PAYMENTS_QUALIFY_CHECKED,
    T1032_RECEIVING_SPOUSE_PENSION_AMOUNT,
    T1032_RECEIVING_SPOUSE_UNDER_65,
    T1032_RECEIVING_SPOUSE_UNDER_65_CHECKED,
    T1032_RESIDENTS_OF_CANADA,
    T1032_RESIDENTS_OF_CANADA_CHECKED,
    T1032_T4A_BOX_128,
    T1032_T4A_RCA_BOX_17,
    T1032_TRANSFERRING_SPOUSE_65_OR_OLDER,
    T1032_TRANSFERRING_SPOUSE_65_OR_OLDER_CHECKED,
    T1032_TRANSFERRING_SPOUSE_DIED,
    T1032_TRANSFERRING_SPOUSE_DIED_CHECKED,
    T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE,
    T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, REGISTERED

# The money kinds: non-negative dollars and cents, the starting amounts of the form (the lines
# 1, 2, 4, 18 months, 32, 35, 37 and 40) and every calculated line of the form.
MONEY = (
    T1032_ELIGIBLE_PENSION_INCOME,
    T1032_T4A_BOX_128,
    T1032_T4A_RCA_BOX_17,
    T1032_MONTHS_MARRIED,
    T1032_MONTHS_IN_TAX_YEAR,
    T1032_RECEIVING_SPOUSE_PENSION_AMOUNT,
    T1032_INCOME_TAX_DEDUCTED_ON_PENSION,
    T1032_LINE_2_CHECKED,
    T1032_LINE_3,
    T1032_LINE_5,
    T1032_LINE_7,
    T1032_LINE_8_BEFORE_GATE,
    T1032_LINE_8,
    T1032_LINE_12,
    T1032_LINE_13,
    T1032_LINE_15,
    T1032_LINE_16,
    T1032_LINE_17,
    T1032_MONTHS_MARRIED_CHECKED,
    T1032_MONTHS_IN_TAX_YEAR_CEILING,
    T1032_MONTHS_IN_TAX_YEAR_CHECKED,
    T1032_LINE_18,
    T1032_LINE_18_MONTHS_IN_TAX_YEAR,
    T1032_LINE_19,
    T1032_LINE_21,
    T1032_LINE_22,
    T1032_LINE_22_CHECKED,
    T1032_LINE_29,
    T1032_LINE_30,
    T1032_LINE_31,
    T1032_LINE_31400_TRANSFERRING,
    T1032_LINE_34,
    T1032_LINE_31400_RECEIVING,
    T1032_LINE_35_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_37_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_35_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_35_CHECKED,
    T1032_LINE_36,
    T1032_LINE_42,
    T1032_LINE_22_TOTAL,
    T1032_LINE_42_TOTAL,
    T1032_LINE_43700,
    T1032_LINE_31400,
    T1032_LINE_31400_RECEIVING_TOTAL,
    T1032_LINE_31400_TRANSFERRING_TOTAL,
    T1032_LINE_1_OF_TRANSFERRING_SPOUSE,
    T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_4_OF_TRANSFERRING_SPOUSE,
    T1032_OTHER_INCOME_OF_TRANSFERRING_SPOUSE,
    T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_21_IF_NOT_SEPARATED,
    T1032_LINE_21_IF_CONDITIONS_MET,
)
# The counts: the three yes-or-no answers, and their checked forms (a count of 0 or 1).
COUNT_KINDS = (
    T1032_RCA_PAYMENTS_QUALIFY,
    T1032_MARITAL_STATUS_CHANGED,
    T1032_FILER_IS_TRANSFERRING_SPOUSE,
    T1032_RCA_PAYMENTS_QUALIFY_CHECKED,
    T1032_MARITAL_STATUS_CHANGED_CHECKED,
    T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED,
    T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL,
    T1032_ELECTION_APPLIES,
    T1032_TRANSFERRING_SPOUSE_DIED,
    T1032_TRANSFERRING_SPOUSE_DIED_CHECKED,
    T1032_NOT_SEPARATED_90_DAYS,
    T1032_NOT_SEPARATED_90_DAYS_CHECKED,
    T1032_RESIDENTS_OF_CANADA,
    T1032_RESIDENTS_OF_CANADA_CHECKED,
)
# Line 39 and its total can be below 0: a receiving spouse's return computes line 39 from its own
# income tax deducted, and reads line 42 instead.
SIGNED_MONEY = (T1032_LINE_39, T1032_LINE_39_TOTAL)
ALL_KINDS = (*MONEY, *SIGNED_MONEY, *COUNT_KINDS)


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module (its
    name is a constant of the declaration's call, which may take the catalog first)."""
    folder = Path(tax_engine.jurisdictions.ca.catalog.__file__).parent
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


def test_the_t1032_kinds_are_registered_under_their_identifiers(
    registry: ArtifactRegistry,
) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t1032_kinds_are_in_the_snapshot_and_the_counts_are_in_counts() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED
    assert {kind.identifier for kind in COUNT_KINDS} <= COUNTS
    for kind in MONEY:
        assert kind.identifier not in COUNTS, kind.identifier


def test_the_t1032_identifiers_are_named_by_the_form_and_its_lines() -> None:
    assert T1032_ELIGIBLE_PENSION_INCOME.identifier == "ca/t1032_eligible_pension_income"
    assert T1032_LINE_21.identifier == "ca/t1032_line_21"
    assert T1032_LINE_22_CHECKED.identifier == "ca/t1032_line_22_checked"
    assert T1032_LINE_31400_TRANSFERRING.identifier == "ca/t1032_line_31400_transferring"
    assert T1032_LINE_31400_RECEIVING.identifier == "ca/t1032_line_31400_receiving"
    assert T1032_LINE_39.identifier == "ca/t1032_line_39"
    assert T1032_LINE_42.identifier == "ca/t1032_line_42"


def test_the_money_kinds_are_non_negative_decimals() -> None:
    for kind in MONEY:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_line_39_and_its_total_are_decimals_that_may_be_below_0() -> None:
    for kind in SIGNED_MONEY:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is False, kind.identifier


def test_the_two_yes_or_no_answers_and_their_checked_forms_are_non_negative_int_counts() -> None:
    for kind in COUNT_KINDS:
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_starting_inputs_are_the_registered_money_and_counts_of_the_form() -> None:
    starting: tuple[ArtifactKind[Any], ...] = (
        T1032_ELIGIBLE_PENSION_INCOME,
        T1032_T4A_BOX_128,
        T1032_T4A_RCA_BOX_17,
        T1032_MONTHS_MARRIED,
        T1032_MONTHS_IN_TAX_YEAR,
        T1032_RECEIVING_SPOUSE_PENSION_AMOUNT,
        T1032_INCOME_TAX_DEDUCTED_ON_PENSION,
        T1032_RCA_PAYMENTS_QUALIFY,
        T1032_MARITAL_STATUS_CHANGED,
        T1032_FILER_IS_TRANSFERRING_SPOUSE,
        T1032_TRANSFERRING_SPOUSE_DIED,
        T1032_NOT_SEPARATED_90_DAYS,
        T1032_RESIDENTS_OF_CANADA,
    )
    assert len(starting) == 13
    assert [kind.identifier for kind in starting if kind.value_type is int] == [
        "ca/t1032_rca_payments_qualify",
        "ca/t1032_marital_status_changed",
        "ca/t1032_filer_is_transferring_spouse",
        "ca/t1032_transferring_spouse_died",
        "ca/t1032_not_separated_90_days",
        "ca/t1032_residents_of_canada",
    ]


def test_the_checked_answers_of_the_two_counts_are_the_yes_or_no_outputs() -> None:
    assert T1032_RCA_PAYMENTS_QUALIFY_CHECKED.identifier == "ca/t1032_rca_payments_qualify_checked"
    assert T1032_MARITAL_STATUS_CHANGED_CHECKED.identifier == (
        "ca/t1032_marital_status_changed_checked"
    )


def test_each_t1032_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T1032" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_line_1_docstring_quotes_the_form_line_and_its_statement() -> None:
    text = squashed(docstring_of(T1032_ELIGIBLE_PENSION_INCOME.identifier))

    assert "Line 1 and line 68020" in text
    assert "Federal Worksheet for line 31400" in text


def test_the_line_18_docstring_quotes_the_months_and_the_note_on_a_deceased_spouse() -> None:
    text = squashed(docstring_of(T1032_MONTHS_MARRIED.identifier))

    assert "Line 18" in text
    assert "Line 68030" in text


def test_the_line_18_denominator_docstring_quotes_the_twelve_and_note_1() -> None:
    text = squashed(docstring_of(T1032_LINE_18_MONTHS_IN_TAX_YEAR.identifier))

    assert "Number of months in the tax year (12) (Note 1)" in text


def test_the_line_22_docstring_quotes_the_limit_of_the_elected_amount() -> None:
    text = squashed(docstring_of(T1032_LINE_22_CHECKED.identifier))

    assert "The split-pension amount cannot be more than the amount from line 21" in text


def test_the_line_31400_docstrings_quote_the_two_thousand_dollar_rule() -> None:
    for kind in (T1032_LINE_31400_TRANSFERRING, T1032_LINE_31400_RECEIVING):
        text = squashed(docstring_of(kind.identifier))

        assert "whichever is less: $2,000 or the amount from line" in text, kind.identifier


def test_the_line_39_docstring_quotes_the_result_for_line_43700() -> None:
    text = squashed(docstring_of(T1032_LINE_39.identifier))

    assert "Enter the result on line 43700 of the transferring spouse's or common-law" in text


def test_the_intermediate_kinds_of_each_step_are_registered_beside_the_exports(
    registry: ArtifactRegistry,
) -> None:
    intermediate: tuple[ArtifactKind[Any], ...] = (
        T1032_LINE_2_CHECKED,
        T1032_LINE_3,
        T1032_LINE_5,
        T1032_LINE_7,
        T1032_LINE_8_BEFORE_GATE,
        T1032_LINE_8,
        T1032_LINE_12,
        T1032_LINE_13,
        T1032_LINE_15,
        T1032_LINE_16,
        T1032_LINE_17,
        T1032_MONTHS_MARRIED_CHECKED,
        T1032_MONTHS_IN_TAX_YEAR_CEILING,
        T1032_LINE_18_MONTHS_IN_TAX_YEAR,
        T1032_MONTHS_IN_TAX_YEAR_CHECKED,
        T1032_LINE_18,
        T1032_LINE_19,
        T1032_LINE_21,
        T1032_LINE_22,
        T1032_LINE_29,
        T1032_LINE_30,
        T1032_LINE_31,
        T1032_LINE_34,
        T1032_LINE_35_CHECKED,
        T1032_LINE_36,
    )
    for kind in intermediate:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier


def test_the_filer_is_transferring_spouse_docstring_quotes_the_form_s_two_returns() -> None:
    text = squashed(docstring_of(T1032_FILER_IS_TRANSFERRING_SPOUSE.identifier))

    assert "line 21000 of the transferring spouse's" in text
    assert "line 11600 of the receiving spouse's" in text


def test_the_line_22_docstring_quotes_the_amount_the_filer_enters_on_the_return() -> None:
    text = squashed(docstring_of(T1032_LINE_22.identifier))

    assert "Line 22" in text
    assert "21000" in text
    assert "11600" in text


def test_the_line_1_check_docstrings_quote_line_8_of_the_federal_worksheet() -> None:
    for kind in (
        T1032_LINE_1_OF_TRANSFERRING_SPOUSE,
        T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE,
    ):
        text = squashed(docstring_of(kind.identifier))

        assert "line 8 of the transferring spouse's" in text, kind.identifier
        assert "Federal Worksheet for line 31400" in text, kind.identifier


def test_the_line_4_check_docstrings_quote_line_4_and_t1_line_13000() -> None:
    for kind in (
        T1032_LINE_4_OF_TRANSFERRING_SPOUSE,
        T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED,
    ):
        text = squashed(docstring_of(kind.identifier))

        assert "box 17 of the transferring spouse's" in text, kind.identifier
        assert "T4A-RCA" in text, kind.identifier
    other = squashed(docstring_of(T1032_OTHER_INCOME_OF_TRANSFERRING_SPOUSE.identifier))
    assert "line 13000" in other
    assert "already included in box 16" in other
    assert "refused" in squashed(
        docstring_of(T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED.identifier)
    )


# --- line 33 and Note 1 ---------------------------------------------------------------------

NOTE_1_COUNT_KINDS: tuple[ArtifactKind[int], ...] = (
    T1032_RECEIVING_SPOUSE_UNDER_65,
    T1032_TRANSFERRING_SPOUSE_65_OR_OLDER,
    T1032_RECEIVING_SPOUSE_UNDER_65_CHECKED,
    T1032_TRANSFERRING_SPOUSE_65_OR_OLDER_CHECKED,
    T1032_NOTE_1_APPLIES,
    T1032_NOTE_1_LINE_17_IS_ZERO,
    T1032_NOTE_1_LINE_29_APPLIES,
    T1032_NOTE_1_RECALCULATION,
)
NOTE_1_MONEY: tuple[ArtifactKind[Decimal], ...] = (
    T1032_NOTE_1_PAYMENTS_A_TO_D,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_CHECKED,
    T1032_NOTE_1_PAYMENTS_TOTAL,
    T1032_NOTE_1_PAYMENTS_TO_REMOVE,
    T1032_NOTE_1_LINE_32_LIMIT,
    T1032_NOTE_1_PAYMENTS_TOTAL_IF_APPLIES,
    T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_IF_APPLIES,
    T1032_NOTE_1_LINE_8_TO_CHECK,
    T1032_NOTE_1_LINE_8_BOUND,
    T1032_NOTE_1_LINE_8_CHECKED,
    T1032_NOTE_1_RESULT_LIMIT,
    T1032_NOTE_1_LINE_22,
)
NOTE_1_KINDS: tuple[ArtifactKind[Any], ...] = (*NOTE_1_MONEY, *NOTE_1_COUNT_KINDS)


def test_the_note_1_kinds_are_registered_under_their_identifiers(
    registry: ArtifactRegistry,
) -> None:
    for kind in NOTE_1_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_note_1_kinds_are_in_the_snapshot_and_the_counts_are_in_counts() -> None:
    assert {kind.identifier for kind in NOTE_1_KINDS} <= REGISTERED
    assert {kind.identifier for kind in NOTE_1_COUNT_KINDS} <= COUNTS
    for kind in NOTE_1_MONEY:
        assert kind.identifier not in COUNTS, kind.identifier


def test_the_note_1_counts_are_non_negative_ints() -> None:
    for kind in NOTE_1_COUNT_KINDS:
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier


NOTE_1_SIGNED: tuple[ArtifactKind[Decimal], ...] = (
    T1032_NOTE_1_RESULT,
    T1032_NOTE_1_LINE_17,
    T1032_NOTE_1_LINE_29,
    T1032_NOTE_1_LINE_30,
    T1032_NOTE_1_LINE_31,
    T1032_NOTE_1_LINE_33,
    T1032_LINE_31_AFTER_NOTE_1,
    T1032_LINE_33,
)


def test_the_note_1_figures_the_form_prints_no_floor_for_are_signed_decimals() -> None:
    for kind in NOTE_1_SIGNED:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is False, kind.identifier


def test_the_note_1_money_kinds_are_non_negative_decimals() -> None:
    for kind in NOTE_1_MONEY:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_each_note_1_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in NOTE_1_KINDS:
        assert "T1032" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_payments_docstring_quotes_the_five_kinds_of_amounts_of_the_form() -> None:
    text = squashed(docstring_of(T1032_NOTE_1_PAYMENTS_A_TO_D.identifier))

    for quoted in (
        "registered retirement income fund (RRIF)",
        "money purchase provision of a registered pension plan (RPP)",
        "pooled registered pension plan (PRPP)",
        "advanced life deferred annuity",
        "eligible veterans benefits",
    ):
        assert quoted in text, quoted


def test_the_death_docstring_quotes_the_exception_of_note_1() -> None:
    text = squashed(docstring_of(T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH.identifier))

    assert "does not need to remove those payments from line 1" in text
    assert "as a consequence of the death of a spouse or common-law partner" in text


def test_the_line_33_docstring_quotes_the_form() -> None:
    text = squashed(docstring_of(T1032_LINE_33.identifier))

    assert "Line 33: Otherwise, enter the amount from line 30" in text
