"""Unit tests for printing a figure's unit in English trace sentences, with made-up kinds and units.

A figure with a unit prints it with its number: before it ("EX$3500.00") or after it ("12 moons",
"1 moon"), with a space between only when the unit's English text is `spaced`. The
`EnglishUnitText` in the `EnglishUnitTextRegistry` given to `EnglishNames` writes it, the unit
itself being only its identifier; a unit with no text is refused, naming it. A figure with none
prints as it always has. The unit is the worksheet's (`FigureNames.unit(label)`), so a sentence
names it for the figures it reads and for the figure it gives; a dataset's constant (a per-unit
amount, threshold, cap or bound) stays bare.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishNames, EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.unit_text import (
    EnglishUnitText,
    EnglishUnitTextRegistry,
)
from tax_engine.adapters.inbound.unit_text import Placement
from tax_engine.domain.blank import BLANK
from tax_engine.domain.errors import UnknownRegistrationError
from tax_engine.domain.kinds import AmountKind, CountKind, RecordListKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.trace import (
    AmountByBandLine,
    BracketColumnFigureLine,
    ChosenByCountLine,
    ChosenByRangeLine,
    ChosenBySignLine,
    ConditionLine,
    DefaultedInputLine,
    FirstRecordCountLine,
    ItemLesserOfLine,
    ItemsTotalLine,
    ItemSumLine,
    RecordPositiveTotalLine,
    RecordTotalLine,
    SubtractedNotBelowZeroLine,
)
from tax_engine.domain.unit import Unit
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.trace import AmountByCountLine

D = Decimal
CROWNS = Unit("ex/crowns")
MOONS = Unit("ex/moons")
WEEKS = Unit("ex/weeks")  # declared, but given no English text
TEXTS = EnglishUnitTextRegistry()
TEXTS.register_text(EnglishUnitText("ex/crowns", "EX$", "EX$", Placement.BEFORE, spaced=False))
TEXTS.register_text(EnglishUnitText("ex/moons", "moon", "moons", Placement.AFTER, spaced=True))

GROSS = AmountKind("ex/gross_pay")
LESS = AmountKind("ex/allowance")
NET = AmountKind("ex/net_pay")
TERM = CountKind("ex/term", non_negative=True)
OUT = AmountKind("ex/contribution")
CENT = RoundTo(increment=D("0.01"), mode=RoundingMode.HALF_UP)


def sheet(units: dict[str, Unit], references: dict[str, str] | None = None) -> Worksheet:
    return Worksheet(figure_units=units, figure_references=references or {})


def test_a_figure_without_a_unit_prints_as_before() -> None:
    names = EnglishNames(sheet({}, {"gross_pay": "2"}), TEXTS)

    assert names.figure(GROSS, D("70000.00")) == "line 2 (70000.00)"
    assert names.figure(TERM, 12) == "term (12)"
    assert EnglishNames().figure(GROSS, D("70000.00")) == "gross pay (70000.00)"


def test_a_unit_before_the_number_is_printed_against_it() -> None:
    names = EnglishNames(sheet({"gross_pay": CROWNS}, {"gross_pay": "2"}), TEXTS)

    assert names.figure(GROSS, D("70000.00")) == "line 2 (EX$70000.00)"


def test_a_unit_after_the_number_is_printed_after_it() -> None:
    names = EnglishNames(sheet({"term": MOONS}), TEXTS)

    assert names.figure(TERM, 12) == "term (12 moons)"


def test_a_unit_after_the_number_is_singular_for_one_and_plural_otherwise() -> None:
    names = EnglishNames(sheet({"term": MOONS}), TEXTS)

    assert names.figure(TERM, 1) == "term (1 moon)"
    assert names.figure(TERM, 0) == "term (0 moons)"
    assert names.figure(TERM, 2) == "term (2 moons)"


def test_only_the_figure_with_the_unit_prints_it() -> None:
    names = EnglishNames(sheet({"term": MOONS}), TEXTS)

    assert names.figure(GROSS, D("1.00")) == "gross pay (1.00)"


def test_a_line_names_the_unit_of_each_figure_it_reads() -> None:
    line = SubtractedNotBelowZeroLine(
        output=NET,
        minuend=GROSS,
        minuend_amount=D("70000.00"),
        subtrahend=LESS,
        subtrahend_amount=D("71300.00"),
        result=D("0.00"),
        rounding=NO_ROUNDING,
    )
    printed = sheet({"gross_pay": CROWNS, "allowance": CROWNS, "net_pay": CROWNS})

    assert EnglishTraceRenderer(unit_texts=TEXTS).render(line, printed) == (
        "Gross pay (EX$70000.00) less allowance (EX$71300.00), not below 0, "
        "gives EX$0.00 (not rounded)."
    )


def test_a_result_with_no_unit_gives_the_plain_figure_though_its_terms_have_one() -> None:
    line = SubtractedNotBelowZeroLine(
        output=NET,
        minuend=GROSS,
        minuend_amount=D("70000.00"),
        subtrahend=LESS,
        subtrahend_amount=D("71300.00"),
        result=D("0.00"),
        rounding=NO_ROUNDING,
    )

    assert EnglishTraceRenderer(unit_texts=TEXTS).render(line, sheet({"gross_pay": CROWNS})) == (
        "Gross pay (EX$70000.00) less allowance (71300.00), not below 0, gives 0.00 (not rounded)."
    )


def test_an_input_taken_as_its_default_prints_its_unit() -> None:
    line = DefaultedInputLine(TERM, 12)

    assert EnglishTraceRenderer(unit_texts=TEXTS).render(line, sheet({"term": MOONS})) == (
        "No value given, so the form's default gives 12 moons."
    )
    assert EnglishTraceRenderer(unit_texts=TEXTS).render(
        DefaultedInputLine(TERM, 1), sheet({"term": MOONS})
    ) == ("No value given, so the form's default gives 1 moon.")


def test_an_input_taken_as_its_default_without_a_unit_prints_as_before() -> None:
    assert EnglishTraceRenderer(unit_texts=TEXTS).render(
        DefaultedInputLine(TERM, 12), sheet({})
    ) == ("No value given, so the form's default gives 12.")
    assert EnglishTraceRenderer(unit_texts=TEXTS).render(DefaultedInputLine(TERM, 12)) == (
        "No value given, so the form's default gives 12."
    )


def test_an_amount_taken_as_its_default_prints_its_unit() -> None:
    line = DefaultedInputLine(GROSS, D("0.00"))

    assert EnglishTraceRenderer(unit_texts=TEXTS).render(line, sheet({"gross_pay": CROWNS})) == (
        "No value given, so the form's default gives EX$0.00."
    )


def test_a_table_amount_prints_the_unit_of_its_count_and_of_its_result() -> None:
    line = AmountByCountLine(OUT, TERM, 12, D("3500"), CENT, D("3500"))
    printed = sheet({"term": MOONS, "contribution": CROWNS}, {"term": "A"})

    assert EnglishTraceRenderer(unit_texts=TEXTS).render(line, printed) == (
        "The table amount for line A (12 moons) is EX$3500.00 (rounded to the nearest cent)."
    )


def test_a_table_amount_without_units_prints_as_before() -> None:
    line = AmountByCountLine(OUT, TERM, 12, D("3500"), NO_ROUNDING, D("3500"))

    assert EnglishTraceRenderer(unit_texts=TEXTS).render(line) == (
        "The table amount for term (12) is 3500.00 (not rounded)."
    )


# --- a unit with no English text ------------------------------------------------------------------


def test_a_figure_whose_unit_has_no_english_text_is_refused_naming_the_unit() -> None:
    names = EnglishNames(sheet({"term": WEEKS}), TEXTS)

    with pytest.raises(UnknownRegistrationError, match="ex/weeks"):
        names.figure(TERM, 12)
    with pytest.raises(UnknownRegistrationError, match="ex/weeks"):
        names.shown("term", 12)


def test_a_sentence_whose_unit_has_no_english_text_is_refused_naming_the_unit() -> None:
    with pytest.raises(UnknownRegistrationError, match="ex/weeks"):
        EnglishTraceRenderer(unit_texts=TEXTS).render(
            DefaultedInputLine(TERM, 12), sheet({"term": WEEKS})
        )


def test_english_names_use_the_unit_texts_they_are_given_not_the_shared_ones() -> None:
    other = EnglishUnitTextRegistry()
    other.register_text(EnglishUnitText("ex/moons", "lune", "lunes", Placement.AFTER, spaced=True))

    assert EnglishNames(sheet({"term": MOONS}), other).figure(TERM, 2) == "term (2 lunes)"
    assert EnglishNames(sheet({"term": MOONS}), TEXTS).figure(TERM, 2) == "term (2 moons)"


def test_the_english_renderer_passes_its_unit_texts_on_to_the_names() -> None:
    other = EnglishUnitTextRegistry()
    other.register_text(EnglishUnitText("ex/moons", "lune", "lunes", Placement.AFTER, spaced=True))

    assert EnglishTraceRenderer(unit_texts=other).render(
        DefaultedInputLine(TERM, 1), sheet({"term": MOONS})
    ) == ("No value given, so the form's default gives 1 lune.")


def test_english_figures_no_longer_write_units() -> None:
    assert not hasattr(EnglishFigures, "with_unit")


def test_a_negative_amount_prints_its_unit_after_the_sign_in_a_sentence() -> None:
    names = EnglishNames(sheet({"gross_pay": CROWNS}), TEXTS)

    assert names.figure(GROSS, D("-1.00")) == "gross pay (-EX$1.00)"
    assert names.shown("gross_pay", D("-1.00")) == "-EX$1.00"
    assert names.shown("gross_pay", D("5")) == "EX$5.00"
    assert names.shown("term", 12) == "12"
    assert names.shown(None, D("5")) == "5.00"


# --- record list sentences ------------------------------------------------------------------------

TOTAL = AmountKind("ex/total")
WAGES = AmountKind("ex/wages")
BONUS = AmountKind("ex/bonus")
JOBS = RecordListKind("ex/jobs", fields=())


def render(line: object, printed: Worksheet | None = None) -> str:
    return EnglishTraceRenderer(unit_texts=TEXTS).render(line, printed)  # type: ignore[arg-type]


def test_a_record_total_prints_the_unit_of_each_item_and_of_the_total() -> None:
    line = RecordTotalLine(TOTAL, WAGES, (D("10"), D("20.5")), D("30.5"))

    assert render(line, sheet({"wages": CROWNS, "total": CROWNS})) == (
        "Wages of item 1 (EX$10.00) plus wages of item 2 (EX$20.50) gives EX$30.50."
    )
    assert render(line, sheet({"wages": CROWNS})) == (
        "Wages of item 1 (EX$10.00) plus wages of item 2 (EX$20.50) gives 30.50."
    )
    assert render(line, sheet({"total": CROWNS})) == (
        "Wages of item 1 (10.00) plus wages of item 2 (20.50) gives EX$30.50."
    )
    assert render(line) == "Wages of item 1 (10.00) plus wages of item 2 (20.50) gives 30.50."


def test_a_record_total_of_no_items_prints_the_unit_of_the_total() -> None:
    line = RecordTotalLine(TOTAL, WAGES, (), D("0"))

    assert render(line, sheet({"total": CROWNS})) == "No items, so EX$0.00."
    assert render(line) == "No items, so 0.00."


def test_a_positive_total_prints_the_unit_of_each_item_and_of_the_total() -> None:
    line = RecordPositiveTotalLine(TOTAL, WAGES, (D("10"), D("-4")), D("10"))
    printed = sheet({"wages": CROWNS, "total": CROWNS})

    assert render(line, printed) == (
        "Wages of item 1 (EX$10.00) plus wages of item 2 (-EX$4.00) counts 0 gives EX$10.00. "
        "Only positive amounts are added; a zero or negative amount counts 0."
    )
    assert render(line) == (
        "Wages of item 1 (10.00) plus wages of item 2 (-4.00) counts 0 gives 10.00. "
        "Only positive amounts are added; a zero or negative amount counts 0."
    )


def test_a_positive_total_of_no_items_prints_the_unit_of_the_total() -> None:
    line = RecordPositiveTotalLine(TOTAL, WAGES, (), D("0"))

    assert render(line, sheet({"total": CROWNS})).startswith("No items, so EX$0.00. ")
    assert render(line).startswith("No items, so 0.00. ")


def test_the_value_of_the_first_item_prints_its_unit() -> None:
    line = FirstRecordCountLine(TERM_OUT, TERM, 12, 3)

    assert render(line, sheet({"term": MOONS})) == "Term of item 1 (12 moons), of 3 items."
    assert render(line) == "Term of item 1 (12), of 3 items."


def test_the_total_of_some_items_prints_its_unit_on_each_item_and_the_total() -> None:
    line = ItemsTotalLine(TOTAL, ((1, D("10")), (3, D("20.5"))), D("30.5"))

    assert render(line, sheet({"total": CROWNS})) == (
        "Item 1 (EX$10.00) plus item 3 (EX$20.50) gives EX$30.50."
    )
    assert render(line) == "Item 1 (10.00) plus item 3 (20.50) gives 30.50."
    assert render(ItemsTotalLine(TOTAL, (), D("0")), sheet({"total": CROWNS})) == (
        "No items, so EX$0.00."
    )


def test_the_sum_of_one_item_prints_the_unit_of_its_parts_and_its_total() -> None:
    line = ItemSumLine(TOTAL, 2, ((WAGES, D("10")), (BONUS, D("5"))), D("15"))

    assert render(line, sheet({"wages": CROWNS, "bonus": CROWNS, "total": CROWNS})) == (
        "Item 2: wages (EX$10.00) plus bonus (EX$5.00) gives EX$15.00."
    )
    assert render(line, sheet({"total": CROWNS})) == (
        "Item 2: wages (10.00) plus bonus (5.00) gives EX$15.00."
    )
    assert render(line) == "Item 2: wages (10.00) plus bonus (5.00) gives 15.00."


def test_the_lesser_of_one_item_prints_the_unit_of_its_parts_and_its_result() -> None:
    line = ItemLesserOfLine(TOTAL, 2, ((WAGES, D("10")), (BONUS, D("5"))), D("5"))

    assert render(line, sheet({"wages": CROWNS, "bonus": CROWNS, "total": CROWNS})) == (
        "Item 2: lesser of wages (EX$10.00) and bonus (EX$5.00) gives EX$5.00."
    )
    assert render(line, sheet({"total": CROWNS})) == (
        "Item 2: lesser of wages (10.00) and bonus (5.00) gives EX$5.00."
    )
    assert render(line) == "Item 2: lesser of wages (10.00) and bonus (5.00) gives 5.00."
    single = ItemLesserOfLine(TOTAL, 2, ((WAGES, D("10")),), D("10"))
    assert render(single, sheet({"total": CROWNS})) == "Item 2: wages (10.00) gives EX$10.00."


# --- choices --------------------------------------------------------------------------------------

CREDIT = AmountKind("ex/credit")
BALANCE = AmountKind("ex/balance")
CHILDREN = CountKind("ex/children")
TERM_OUT = CountKind("ex/term_out")
FLAGGED = CountKind("ex/flagged", non_negative=True)


def test_a_candidate_chosen_by_a_count_prints_the_units_of_its_figures() -> None:
    line = ChosenByCountLine(NET, TERM, 2, CREDIT, D("750.5"))

    assert render(line, sheet({"credit": CROWNS, "term": MOONS})) == (
        "Credit (EX$750.50), chosen because term (2 moons) is not 0."
    )
    assert render(line) == "Credit (750.50), chosen because term (2) is not 0."


def test_a_candidate_chosen_by_a_sign_or_a_range_prints_the_units_of_its_figures() -> None:
    printed = sheet({"credit": CROWNS, "balance": CROWNS})

    assert render(ChosenBySignLine(NET, BALANCE, D("-4"), CREDIT, D("10")), printed) == (
        "Credit (EX$10.00), chosen because balance (-EX$4.00) is negative."
    )
    assert render(ChosenBySignLine(NET, BALANCE, D("-4"), None, D("0")), printed) == (
        "0, no amount when balance (-EX$4.00) is negative."
    )
    assert render(ChosenByRangeLine(NET, BALANCE, D("52000"), CREDIT, D("300")), printed) == (
        "Credit (EX$300.00), chosen because balance (EX$52000.00) fits its range."
    )


def test_a_condition_prints_the_unit_of_each_figure_it_read() -> None:
    line = ConditionLine(
        FLAGGED, 1, "Income over the limit", ((GROSS, D("120")), (TERM, 12), (LESS, BLANK)), True
    )
    printed = sheet({"gross_pay": CROWNS, "term": MOONS})

    assert render(line, printed) == (
        'Condition 1 "Income over the limit" '
        "(read gross pay (EX$120.00), term (12 moons), allowance (left blank)) applies."
    )
    assert render(line) == (
        'Condition 1 "Income over the limit" '
        "(read gross pay (120.00), term (12), allowance (left blank)) applies."
    )


# --- rate tables ----------------------------------------------------------------------------------

FIFTY = D("50000")


def test_the_amount_of_a_band_prints_its_unit_but_not_the_charts_constants() -> None:
    sloped = AmountByBandLine(
        NET, GROSS, D("70000"), FIFTY, None, FIFTY, Rate(D("0.1")), D("100"), NO_ROUNDING, D("2100")
    )
    flat = AmountByBandLine(
        NET, GROSS, D("70000"), FIFTY, D("300"), None, None, None, NO_ROUNDING, D("300")
    )
    printed = sheet({"net_pay": CROWNS})

    assert render(sloped, printed) == (
        "Gross pay (70000.00) is over 50000.00, so (70000.00 minus 50000.00) × 10% plus 100.00 "
        "gives EX$2100.00 (not rounded)."
    )
    assert render(flat, printed) == (
        "Gross pay (70000.00) is over 50000.00, so the amount is EX$300.00 (not rounded)."
    )
    assert render(sloped) == (
        "Gross pay (70000.00) is over 50000.00, so (70000.00 minus 50000.00) × 10% plus 100.00 "
        "gives 2100.00 (not rounded)."
    )
    assert render(flat) == (
        "Gross pay (70000.00) is over 50000.00, so the amount is 300.00 (not rounded)."
    )


def test_a_bracket_columns_printed_amounts_print_their_unit_but_a_rate_stays_a_percentage() -> None:
    lower = BracketColumnFigureLine(NET, GROSS, D("52000"), "lower bound", D("50000"))
    at_start = BracketColumnFigureLine(NET, GROSS, D("52000"), "tax at start", D("5000"))
    rate = BracketColumnFigureLine(NET, GROSS, D("52000"), "rate", D("0.205"))
    printed = sheet({"net_pay": CROWNS})

    assert (
        render(lower, printed)
        == "Gross pay (52000.00) falls in the bracket that starts at EX$50000.00."
    )
    assert render(at_start, printed) == (
        "Gross pay (52000.00) falls in a bracket with EX$5000.00 of tax on the income below it."
    )
    assert render(rate, printed) == "Gross pay (52000.00) falls in a bracket with the rate 20.5%."
    assert render(lower) == "Gross pay (52000.00) falls in the bracket that starts at 50000.00."
    assert render(at_start) == (
        "Gross pay (52000.00) falls in a bracket with 5000.00 of tax on the income below it."
    )
