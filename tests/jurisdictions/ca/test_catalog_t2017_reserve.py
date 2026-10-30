"""Registered kinds of Form T2017 (2025), "Summary of Reserves on Dispositions of Capital Property",
Part 1 (page 1 and page 2), in the federal catalog family `t2017_reserve`.

The form is ten row forms, one for each 2025 reserve line that takes a list of dispositions:
`ca/t2017_line_N_reserve` for N in 2, 3, 4, 8, 9, 10, 17, 21, 24 and 27, each run once for each
record of `ca/t2017_line_N_reserve_rows`; and the summary form `ca/t2017`, run once, which adds the
lines of Part 1. The starting inputs are the 2024 figures of lines 1, 7, 16, 20, 23 and 30, and the
2024 figure that line 26 is computed from (lines 66990 and 67058 of the 2024 form); line 26 is that
figure less line 23, signed. Line 14 is entered and read by nothing. The field kinds are declared
once and shared by the ten lists; only lines 2 and 8 take the nine-year answer as a field of their
records.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    T2017_LINE_1,
    T2017_LINE_2,
    T2017_LINE_2_RESERVE_ROWS,
    T2017_LINE_3,
    T2017_LINE_3_RESERVE_ROWS,
    T2017_LINE_4,
    T2017_LINE_4_RESERVE_ROWS,
    T2017_LINE_5,
    T2017_LINE_6,
    T2017_LINE_7,
    T2017_LINE_8,
    T2017_LINE_8_RESERVE_ROWS,
    T2017_LINE_9,
    T2017_LINE_9_RESERVE_ROWS,
    T2017_LINE_10,
    T2017_LINE_10_RESERVE_ROWS,
    T2017_LINE_11,
    T2017_LINE_12,
    T2017_LINE_13,
    T2017_LINE_14,
    T2017_LINE_16,
    T2017_LINE_17,
    T2017_LINE_17_RESERVE_ROWS,
    T2017_LINE_18,
    T2017_LINE_19,
    T2017_LINE_20,
    T2017_LINE_21,
    T2017_LINE_21_RESERVE_ROWS,
    T2017_LINE_22,
    T2017_LINE_23,
    T2017_LINE_24,
    T2017_LINE_24_RESERVE_ROWS,
    T2017_LINE_25,
    T2017_LINE_26,
    T2017_LINE_27,
    T2017_LINE_27_RESERVE_ROWS,
    T2017_LINE_28,
    T2017_LINE_29,
    T2017_LINE_30,
    T2017_LINE_31,
    T2017_LINES_66990_AND_67058_FOR_2024,
    T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
    T2017_RESERVE_APPLICABLE_PERCENTAGE,
    T2017_RESERVE_BY_PAYMENT,
    T2017_RESERVE_BY_PERCENTAGE,
    T2017_RESERVE_CAPITAL_GAIN,
    T2017_RESERVE_CLAIM_LIMIT,
    T2017_RESERVE_CLAIMED,
    T2017_RESERVE_FOUR_YEAR_PERCENTAGE,
    T2017_RESERVE_LATER_YEAR,
    T2017_RESERVE_LATER_YEAR_MAXIMUM,
    T2017_RESERVE_MAXIMUM,
    T2017_RESERVE_NINE_YEAR,
    T2017_RESERVE_NINE_YEAR_CHECKED,
    T2017_RESERVE_NINE_YEAR_PERCENTAGE,
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024_CHECKED,
    T2017_RESERVE_PAYABLE_CHECKED,
    T2017_RESERVE_PERIOD_1_OF_2024,
    T2017_RESERVE_PERIOD_1_OF_2024_CHECKED,
    T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    T2017_RESERVE_PROCEEDS,
    T2017_RESERVE_REPORTED_ON_SLIP,
    T2017_RESERVE_REPORTED_ON_SLIP_CHECKED,
    T2017_RESERVE_YEARS_AFTER_DISPOSITION,
    T2017_ROW_CHANGE,
    T2017_ROW_PREVIOUS_RESERVE,
    T2017_ROW_RESERVE,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The ten lists of the row forms, in the order of their lines.
ROW_LISTS = (
    T2017_LINE_2_RESERVE_ROWS,
    T2017_LINE_3_RESERVE_ROWS,
    T2017_LINE_4_RESERVE_ROWS,
    T2017_LINE_8_RESERVE_ROWS,
    T2017_LINE_9_RESERVE_ROWS,
    T2017_LINE_10_RESERVE_ROWS,
    T2017_LINE_17_RESERVE_ROWS,
    T2017_LINE_21_RESERVE_ROWS,
    T2017_LINE_24_RESERVE_ROWS,
    T2017_LINE_27_RESERVE_ROWS,
)
# The fields of a record: the five the reserve calculation reads, then the reserve claimed for the
# property in the previous year (not read for a disposition in 2025), and the nine-year answer,
# which only the records of lines 2 and 8 hold.
ROW_FIELDS = (
    T2017_RESERVE_CAPITAL_GAIN,
    T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
    T2017_RESERVE_PROCEEDS,
    T2017_RESERVE_YEARS_AFTER_DISPOSITION,
    T2017_RESERVE_CLAIMED,
    T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
)
# The three answers Form T657 and Guide T4037 read, between the previous year's claim and the
# nine-year answer, in the records of the lines that hold QFFP or QSBCS reserves (2, 3, 4, 8, 9
# and 10).
T657_ANSWERS = (
    T2017_RESERVE_PERIOD_1_OF_2024,
    T2017_RESERVE_REPORTED_ON_SLIP,
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
)
T657_LINES = {2, 3, 4, 8, 9, 10}
# The starting inputs: the 2024 figures of Part 1 (the lines that are not computed here). Line 26
# is computed from the 2024 figure that is its starting input.
STARTING = (
    T2017_LINE_1,
    T2017_LINE_7,
    T2017_LINE_16,
    T2017_LINE_20,
    T2017_LINE_23,
    T2017_LINES_66990_AND_67058_FOR_2024,
    T2017_LINE_30,
)
# The input that is not a 2024 figure: line 14 is entered, and no step of the form reads it.
ENTERED = (T2017_LINE_14,)
# The summary's lines that are amounts of the form, none below zero (the totals of the lists and
# the sums of positive lines).
TOTALS = (
    T2017_LINE_2,
    T2017_LINE_3,
    T2017_LINE_4,
    T2017_LINE_8,
    T2017_LINE_9,
    T2017_LINE_10,
    T2017_LINE_17,
    T2017_LINE_21,
    T2017_LINE_24,
    T2017_LINE_27,
    T2017_LINE_5,
    T2017_LINE_11,
)
# The lines printed "(if negative, show in brackets)": the differences and the sums that can be
# negative.
SIGNED_LINES = (
    T2017_LINE_6,
    T2017_LINE_12,
    T2017_LINE_13,
    T2017_LINE_18,
    T2017_LINE_19,
    T2017_LINE_22,
    T2017_LINE_25,
    T2017_LINE_26,
    T2017_LINE_28,
    T2017_LINE_29,
    T2017_LINE_31,
)
# The intermediate kinds of the calculation of reserve, shared by the ten row forms (each form
# runs its own copy of the steps).
INTERMEDIATE = (
    T2017_RESERVE_PAYABLE_CHECKED,
    T2017_RESERVE_BY_PAYMENT,
    T2017_RESERVE_FOUR_YEAR_PERCENTAGE,
    T2017_RESERVE_NINE_YEAR_PERCENTAGE,
    T2017_RESERVE_APPLICABLE_PERCENTAGE,
    T2017_RESERVE_BY_PERCENTAGE,
    T2017_RESERVE_MAXIMUM,
    T2017_RESERVE_LATER_YEAR_MAXIMUM,
    T2017_RESERVE_CLAIM_LIMIT,
    T2017_ROW_RESERVE,
)
ALL_KINDS = (
    *STARTING,
    *ENTERED,
    *TOTALS,
    *SIGNED_LINES,
    *ROW_LISTS,
    *ROW_FIELDS,
    T2017_RESERVE_NINE_YEAR,
    T2017_RESERVE_NINE_YEAR_CHECKED,
    T2017_RESERVE_LATER_YEAR,
    *INTERMEDIATE,
)


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


def test_the_t2017_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t2017_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_summary_lines_are_registered_under_the_form_s_line_numbers() -> None:
    assert [kind.identifier for kind in STARTING] == [
        "ca/t2017_line_1",
        "ca/t2017_line_7",
        "ca/t2017_line_16",
        "ca/t2017_line_20",
        "ca/t2017_line_23",
        "ca/t2017_lines_66990_and_67058_for_2024",
        "ca/t2017_line_30",
    ]
    assert T2017_LINE_13.identifier == "ca/t2017_line_13"
    assert T2017_LINE_26.identifier == "ca/t2017_line_26"
    assert T2017_LINE_31.identifier == "ca/t2017_line_31"


def test_line_26_is_computed_from_its_2024_figure_and_is_not_a_starting_input() -> None:
    assert T2017_LINE_26 not in STARTING
    assert T2017_LINE_26 in SIGNED_LINES
    assert T2017_LINES_66990_AND_67058_FOR_2024 in STARTING
    assert T2017_LINES_66990_AND_67058_FOR_2024.identifier == (
        "ca/t2017_lines_66990_and_67058_for_2024"
    )


def test_line_14_is_a_starting_input_of_its_own_and_is_registered() -> None:
    assert T2017_LINE_14.identifier == "ca/t2017_line_14"
    assert ENTERED == (T2017_LINE_14,)
    assert T2017_LINE_14 not in STARTING


def test_each_row_list_is_a_record_list_kind_named_for_its_line() -> None:
    lines = (2, 3, 4, 8, 9, 10, 17, 21, 24, 27)
    for number, kind in zip(lines, ROW_LISTS, strict=True):
        assert isinstance(kind, RecordListKind), kind.identifier
        assert kind.identifier == f"ca/t2017_line_{number}_reserve_rows"
        assert kind.identifier in RECORD_LISTS, kind.identifier


def test_lines_2_and_8_hold_the_nine_year_answer_and_the_other_lists_do_not() -> None:
    for number, kind in zip((2, 3, 4, 8, 9, 10, 17, 21, 24, 27), ROW_LISTS, strict=True):
        expected = [*ROW_FIELDS, *(T657_ANSWERS if number in T657_LINES else ())]
        if number in {2, 8}:
            expected.append(T2017_RESERVE_NINE_YEAR)
        assert list(kind.fields) == expected, kind.identifier


def test_the_lists_of_qffp_and_qsbcs_reserves_hold_the_three_answers_form_t657_reads() -> None:
    assert [kind.identifier for kind in T657_ANSWERS] == [
        "ca/t2017_reserve_period_1_of_2024",
        "ca/t2017_reserve_reported_on_slip",
        "ca/t2017_reserve_partnership_year_began_before_june_25_2024",
    ]
    for kind in T657_ANSWERS:
        assert kind.value_type is int
        assert kind.non_negative is True


def test_the_row_fields_are_the_reserve_inputs_in_the_printed_order() -> None:
    assert [kind.identifier for kind in ROW_FIELDS] == [
        "ca/t2017_reserve_capital_gain",
        "ca/t2017_reserve_amount_payable_after_year_end",
        "ca/t2017_reserve_proceeds",
        "ca/t2017_reserve_years_after_disposition",
        "ca/t2017_reserve_claimed",
        "ca/t2017_reserve_previous_year_claim",
    ]
    assert T2017_RESERVE_NINE_YEAR.identifier == "ca/t2017_reserve_nine_year"


def test_the_row_fields_are_money_except_the_years_and_the_nine_year_answer() -> None:
    for kind in (
        T2017_RESERVE_CAPITAL_GAIN,
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
        T2017_RESERVE_PROCEEDS,
        T2017_RESERVE_CLAIMED,
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    for count_kind in (T2017_RESERVE_YEARS_AFTER_DISPOSITION, T2017_RESERVE_NINE_YEAR):
        assert count_kind.value_type is int, count_kind.identifier
        assert count_kind.non_negative is True, count_kind.identifier


def test_the_counts_are_registered_as_counts() -> None:
    assert T2017_RESERVE_YEARS_AFTER_DISPOSITION.identifier in COUNTS
    assert T2017_RESERVE_NINE_YEAR.identifier in COUNTS
    assert T2017_RESERVE_NINE_YEAR_CHECKED.identifier in COUNTS
    assert T2017_RESERVE_NINE_YEAR_CHECKED.value_type is int
    assert T2017_RESERVE_NINE_YEAR_CHECKED.non_negative is True


def test_the_later_year_count_is_a_whole_number_registered_as_a_count() -> None:
    assert T2017_RESERVE_LATER_YEAR.identifier == "ca/t2017_reserve_later_year"
    assert T2017_RESERVE_LATER_YEAR.identifier in COUNTS
    assert T2017_RESERVE_LATER_YEAR.value_type is int
    assert T2017_RESERVE_LATER_YEAR.non_negative is True


def test_the_later_year_maximum_and_the_claim_limit_are_money_of_the_row_form() -> None:
    for kind in (T2017_RESERVE_LATER_YEAR_MAXIMUM, T2017_RESERVE_CLAIM_LIMIT):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert T2017_RESERVE_LATER_YEAR_MAXIMUM.identifier == "ca/t2017_reserve_later_year_maximum"
    assert T2017_RESERVE_CLAIM_LIMIT.identifier == "ca/t2017_reserve_claim_limit"


def test_the_starting_inputs_and_the_totals_are_non_negative_money() -> None:
    for kind in (*STARTING, *ENTERED, *TOTALS):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_signed_lines_are_signed_money_and_are_in_the_signed_set() -> None:
    for kind in SIGNED_LINES:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is False, kind.identifier
        assert kind.identifier in SIGNED, kind.identifier


def test_the_row_reserve_is_the_export_the_row_forms_share() -> None:
    assert T2017_ROW_RESERVE.identifier == "ca/t2017_row_reserve"
    assert T2017_ROW_RESERVE.value_type is Decimal
    assert T2017_ROW_RESERVE.non_negative is True


def test_the_intermediate_kinds_of_the_calculation_are_registered_money() -> None:
    for kind in INTERMEDIATE:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_intermediate_kinds_are_in_the_registry_beside_the_row_reserve(
    registry: ArtifactRegistry,
) -> None:
    intermediate: tuple[ArtifactKind[Any], ...] = INTERMEDIATE
    for kind in intermediate:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_each_t2017_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T2017" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_row_list_docstring_quotes_the_form_s_reserve_lines_and_its_nine_year_answer() -> None:
    text = squashed(docstring_of(T2017_LINE_2_RESERVE_ROWS.identifier))

    assert "Amount of 2025 reserve for dispositions of QFFP to your child after 2016," in text
    assert (
        "Family farm or fishing property and small business corporation shares disposed of to "
        "your child, or disposition under a QBT or QCC" in text
    )


def test_the_line_5_docstring_quotes_the_form_s_sum_of_lines_2_to_4() -> None:
    assert "Add lines 2 to 4." in squashed(docstring_of(T2017_LINE_5.identifier))


def test_the_signed_lines_docstrings_quote_the_form_s_bracket_rule() -> None:
    quoted = {
        T2017_LINE_6: "Line 1 minus line 5 (if negative, show in brackets)",
        T2017_LINE_12: "Line 7 minus line 11 (if negative, show in brackets)",
        T2017_LINE_13: "Line 6 plus line 12 (if negative, show in brackets)",
        T2017_LINE_18: "Line 16 minus line 17 (if negative, show in brackets)",
        T2017_LINE_19: "Line 15 plus line 18 (if negative, show in brackets)",
        T2017_LINE_22: "Line 20 minus line 21 (if negative, show in brackets)",
        T2017_LINE_25: "Line 23 minus line 24 (if negative, show in brackets)",
        T2017_LINE_28: "Line 26 minus line 27 (if negative, show in brackets)",
        T2017_LINE_29: "Add lines 19, 22, 25, and 28 (if negative, show in brackets).",
    }
    for kind, phrase in quoted.items():
        assert phrase in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_2024_figure_of_line_26_docstring_quotes_the_form_s_words() -> None:
    text = squashed(docstring_of(T2017_LINES_66990_AND_67058_FOR_2024.identifier))

    assert (
        "Amount of 2024 reserve for dispositions of property after 2020, other than dispositions "
        "listed on lines 66843, 66883, 66910, and 66930 (lines 66990 and 67058 of Form T2017 for "
        "2024)" in text
    )


def test_the_line_26_docstring_quotes_the_form_s_subtraction_of_line_23() -> None:
    text = squashed(docstring_of(T2017_LINE_26.identifier))

    assert (
        "(lines 66990 and 67058 of Form T2017 for 2024 minus amounts reported at line 66937 of "
        "Form T2017 for 2025)" in text
    )


def test_the_line_14_docstring_quotes_the_form_s_words_and_its_condition() -> None:
    text = squashed(docstring_of(T2017_LINE_14.identifier))

    assert "Enter the amount of the most recent reserves claimed on line 66850." in text
    assert (
        "Complete line 66905 only if you are reporting or claiming reserves on line 66883, line "
        "66850, or both for at least two dispositions of QSBCS that originated in more than one "
        "year after 2015." in text
    )


def test_line_31_docstring_names_the_schedule_3_line_it_is_entered_on() -> None:
    text = squashed(docstring_of(T2017_LINE_31.identifier))

    assert "Enter this amount on line 19200 of Schedule 3" in text


def test_the_nine_year_answer_docstring_quotes_the_form_s_nine_year_rule() -> None:
    text = squashed(docstring_of(T2017_RESERVE_NINE_YEAR.identifier))

    assert "a maximum of nine years" in text
    assert (
        "Family farm or fishing property and small business corporation shares disposed of to "
        "your child, or disposition under a QBT or QCC" in text
    )


def test_the_claim_docstring_quotes_the_form_s_reserve_sentence() -> None:
    text = squashed(docstring_of(T2017_RESERVE_CLAIMED.identifier))

    assert "Your reserve for the year cannot be more than the lesser of the following" in text


def test_the_previous_year_claim_docstring_quotes_the_form_s_later_year_sentence() -> None:
    text = squashed(docstring_of(T2017_RESERVE_PREVIOUS_YEAR_CLAIM.identifier))

    assert "the amount you claimed for that property in the previous year (Year A)" in text


def test_the_later_year_count_docstring_quotes_the_form_s_year_b_wording() -> None:
    text = squashed(docstring_of(T2017_RESERVE_LATER_YEAR.identifier))

    assert "a later year (Year B)" in text


def test_the_checked_answers_and_the_row_reserves_form_t657_reads_are_registered() -> None:
    assert T2017_RESERVE_PERIOD_1_OF_2024_CHECKED.identifier == (
        "ca/t2017_reserve_period_1_of_2024_checked"
    )
    assert T2017_RESERVE_REPORTED_ON_SLIP_CHECKED.identifier == (
        "ca/t2017_reserve_reported_on_slip_checked"
    )
    assert T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024_CHECKED.identifier == (
        "ca/t2017_reserve_partnership_year_began_before_june_25_2024_checked"
    )
    for kind in (
        T2017_RESERVE_PERIOD_1_OF_2024_CHECKED,
        T2017_RESERVE_REPORTED_ON_SLIP_CHECKED,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024_CHECKED,
    ):
        assert kind.identifier in COUNTS
        assert kind.value_type is int
    # The reserve of the previous year a row carries into 2025, and the change in the reserve that
    # Form T657 reads: previous year's claim less the 2025 reserve, so signed.
    assert T2017_ROW_PREVIOUS_RESERVE.identifier == "ca/t2017_row_previous_reserve"
    assert T2017_ROW_PREVIOUS_RESERVE.non_negative is True
    assert T2017_ROW_CHANGE.identifier == "ca/t2017_row_change"
    assert T2017_ROW_CHANGE.non_negative is False
    assert T2017_ROW_CHANGE.identifier in SIGNED
    assert T2017_ROW_CHANGE.identifier in REGISTERED
