"""Unit tests for EnglishNames and for naming figures in a rendered trace, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishNames, EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.names import short_form_title
from tax_engine.domain.figure_names import ImportedFigure
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet

GROSS = AmountKind("ex/gross_pay")
LESS = AmountKind("ex/allowance")
NET = AmountKind("ex/net_pay")


def _Printed(titles: dict[str, str], references: dict[str, str]) -> Worksheet:  # noqa: N802
    """A worksheet of no figures that prints `titles` and `references` for some of them."""
    return Worksheet(figure_titles=titles, figure_references=references)


def test_with_no_worksheet_a_figure_is_its_label_in_plain_words() -> None:
    assert EnglishNames().of(GROSS) == "gross pay"
    assert EnglishNames().figure(GROSS, Decimal("70000.00")) == "gross pay (70000.00)"


def test_a_bare_reference_is_a_line_of_the_form() -> None:
    names = EnglishNames(_Printed({}, {"gross_pay": "4", "allowance": "B", "net_pay": "5a"}))

    assert names.of(GROSS) == "line 4"
    assert names.of(LESS) == "line B"
    assert names.of(NET) == "line 5a"


def test_a_reference_that_is_not_a_bare_line_is_used_as_printed() -> None:
    names = EnglishNames(_Printed({}, {"gross_pay": "Box 3"}))

    assert names.of(GROSS) == "Box 3"


def test_a_reference_wins_over_a_title_and_a_title_over_a_label() -> None:
    names = EnglishNames(
        _Printed({"gross_pay": "Gross pay", "allowance": "Allowance"}, {"gross_pay": "4"})
    )

    assert names.of(GROSS) == "line 4"
    assert names.of(LESS) == '"Allowance"'
    assert names.of(NET) == "net pay"


def test_a_figure_is_followed_by_its_value_in_brackets() -> None:
    names = EnglishNames(_Printed({}, {"gross_pay": "2"}))

    assert names.figure(GROSS, Decimal("70000.00")) == "line 2 (70000.00)"
    assert names.figure(GROSS, 3) == "line 2 (3)"


def test_a_rendered_line_names_its_figures_as_the_form_prints_them_and_not_its_own() -> None:
    line = SubtractedNotBelowZeroLine(
        output=NET,
        minuend=GROSS,
        minuend_amount=Decimal("70000.00"),
        subtrahend=LESS,
        subtrahend_amount=Decimal("71300.00"),
        result=Decimal("0.00"),
        rounding=NO_ROUNDING,
    )
    printed = _Printed({}, {"gross_pay": "2", "allowance": "B", "net_pay": "4"})

    assert EnglishTraceRenderer().render(line, printed) == (
        "Line 2 (70000.00) less line B (71300.00), not below 0, gives 0.00 (not rounded)."
    )
    assert EnglishTraceRenderer().render(line) == (
        "Gross pay (70000.00) less allowance (71300.00), not below 0, gives 0.00 (not rounded)."
    )


def _imported(
    reference: str | None, title: str | None = None, *, one_instance: bool = True
) -> ImportedFigure:
    return ImportedFigure("Form ON428: Ontario Tax", title, reference, one_instance)


def test_a_figure_read_from_another_form_is_named_as_that_form_prints_it() -> None:
    sheet = Worksheet(
        imported_figures={"gross_pay": _imported("90"), "allowance": _imported("Box 3")}
    )
    names = EnglishNames(sheet)

    assert names.of(GROSS) == "line 90 of ON428"
    assert names.of(LESS) == "Box 3 of ON428"
    assert names.figure(GROSS, Decimal("3911.45")) == "line 90 of ON428 (3911.45)"


def test_an_imported_figure_with_no_reference_is_named_by_its_title_then_by_its_label() -> None:
    sheet = Worksheet(
        imported_figures={"gross_pay": _imported(None, "Gross pay"), "net_pay": _imported(None)}
    )
    names = EnglishNames(sheet)

    assert names.of(GROSS) == '"Gross pay" of ON428'
    assert names.of(NET) == "net pay"


def test_an_imported_figure_of_a_form_without_a_title_is_named_without_the_form() -> None:
    sheet = Worksheet(imported_figures={"gross_pay": ImportedFigure(None, None, "90", True)})

    assert EnglishNames(sheet).of(GROSS) == "line 90"


def test_a_form_is_named_by_its_title_up_to_the_colon_without_form() -> None:
    assert short_form_title("Form ON428: Ontario Tax") == "ON428"
    assert short_form_title("Schedule 8: Canada Pension Plan Contributions") == "Schedule 8"
    assert short_form_title("T1 General") == "T1 General"


def test_an_item_of_a_one_instance_form_has_no_item_number() -> None:
    sheet = Worksheet(imported_figures={"gross_pay": _imported("90")})
    names = EnglishNames(sheet)

    assert names.of_item(GROSS, 1) == "line 90 of ON428"
    assert names.of_item(LESS, 2) == "allowance of item 2"


def test_an_item_of_a_form_with_instances_is_named_by_its_position() -> None:
    sheet = Worksheet(imported_figures={"gross_pay": _imported("5", one_instance=False)})

    assert EnglishNames(sheet).of_item(GROSS, 2) == "line 5 of ON428, item 2"


def test_two_figures_with_one_reference_are_told_apart_by_their_titles() -> None:
    sheet = Worksheet(
        figure_titles={"allowance": "Allowance"},
        figure_references={"gross_pay": "87", "allowance": "87", "net_pay": "88"},
    )
    names = EnglishNames(sheet)

    assert names.of(LESS) == '"Allowance"'
    assert names.of(GROSS) == "line 87"
    assert names.of(NET) == "line 88"
