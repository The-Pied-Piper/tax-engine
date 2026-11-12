"""Unit tests for printing a figure's unit in English trace sentences, with made-up kinds and units.

A figure with a unit prints it with its number: before the number against it ("EX$3500.00") or
after it with a space ("12 moons", "1 moon"). A figure with none prints as it always has. The
unit is the worksheet's (`FigureNames.unit(label)`), so a sentence names it for the figures it
reads and for the figure it gives.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.unit import Placement, Unit

import tax_engine.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishNames, EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.trace import DefaultedInputLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.trace import AmountByCountLine

D = Decimal
CROWNS = Unit("crowns", "EX$", "EX$", Placement.BEFORE)
MOONS = Unit("moons", "moon", "moons", Placement.AFTER)

GROSS = AmountKind("ex/gross_pay")
LESS = AmountKind("ex/allowance")
NET = AmountKind("ex/net_pay")
TERM = CountKind("ex/term", non_negative=True)
OUT = AmountKind("ex/contribution")
CENT = RoundTo(increment=D("0.01"), mode=RoundingMode.HALF_UP)


def sheet(units: dict[str, Unit], references: dict[str, str] | None = None) -> Worksheet:
    return Worksheet(figure_units=units, figure_references=references or {})


def test_a_figure_without_a_unit_prints_as_before() -> None:
    names = EnglishNames(sheet({}, {"gross_pay": "2"}))

    assert names.figure(GROSS, D("70000.00")) == "line 2 (70000.00)"
    assert names.figure(TERM, 12) == "term (12)"
    assert EnglishNames().figure(GROSS, D("70000.00")) == "gross pay (70000.00)"


def test_a_unit_before_the_number_is_printed_against_it() -> None:
    names = EnglishNames(sheet({"gross_pay": CROWNS}, {"gross_pay": "2"}))

    assert names.figure(GROSS, D("70000.00")) == "line 2 (EX$70000.00)"


def test_a_unit_after_the_number_is_printed_after_it() -> None:
    names = EnglishNames(sheet({"term": MOONS}))

    assert names.figure(TERM, 12) == "term (12 moons)"


def test_a_unit_after_the_number_is_singular_for_one_and_plural_otherwise() -> None:
    names = EnglishNames(sheet({"term": MOONS}))

    assert names.figure(TERM, 1) == "term (1 moon)"
    assert names.figure(TERM, 0) == "term (0 moons)"
    assert names.figure(TERM, 2) == "term (2 moons)"


def test_only_the_figure_with_the_unit_prints_it() -> None:
    names = EnglishNames(sheet({"term": MOONS}))

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

    assert EnglishTraceRenderer().render(line, printed) == (
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

    assert EnglishTraceRenderer().render(line, sheet({"gross_pay": CROWNS})) == (
        "Gross pay (EX$70000.00) less allowance (71300.00), not below 0, gives 0.00 (not rounded)."
    )


def test_an_input_taken_as_its_default_prints_its_unit() -> None:
    line = DefaultedInputLine(TERM, 12)

    assert EnglishTraceRenderer().render(line, sheet({"term": MOONS})) == (
        "No value given, so the form's default gives 12 moons."
    )
    assert EnglishTraceRenderer().render(DefaultedInputLine(TERM, 1), sheet({"term": MOONS})) == (
        "No value given, so the form's default gives 1 moon."
    )


def test_an_input_taken_as_its_default_without_a_unit_prints_as_before() -> None:
    assert EnglishTraceRenderer().render(DefaultedInputLine(TERM, 12), sheet({})) == (
        "No value given, so the form's default gives 12."
    )
    assert EnglishTraceRenderer().render(DefaultedInputLine(TERM, 12)) == (
        "No value given, so the form's default gives 12."
    )


def test_an_amount_taken_as_its_default_prints_its_unit() -> None:
    line = DefaultedInputLine(GROSS, D("0.00"))

    assert EnglishTraceRenderer().render(line, sheet({"gross_pay": CROWNS})) == (
        "No value given, so the form's default gives EX$0.00."
    )


def test_a_table_amount_prints_the_unit_of_its_count_and_of_its_result() -> None:
    line = AmountByCountLine(OUT, TERM, 12, D("3500"), CENT, D("3500"))
    printed = sheet({"term": MOONS, "contribution": CROWNS}, {"term": "A"})

    assert EnglishTraceRenderer().render(line, printed) == (
        "The table amount for line A (12 moons) is EX$3500.00 (rounded to the nearest cent)."
    )


def test_a_table_amount_without_units_prints_as_before() -> None:
    line = AmountByCountLine(OUT, TERM, 12, D("3500"), NO_ROUNDING, D("3500"))

    assert EnglishTraceRenderer().render(line) == (
        "The table amount for term (12) is 3500.00 (not rounded)."
    )
