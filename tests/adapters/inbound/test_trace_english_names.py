"""Unit tests for EnglishNames and for naming figures in a rendered trace, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishNames, EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import SubtractedNotBelowZeroLine

GROSS = AmountKind("ex/gross_pay")
LESS = AmountKind("ex/allowance")
NET = AmountKind("ex/net_pay")


class _Printed:
    """A stand-in for a worksheet: what the form prints for some figures."""

    def __init__(self, titles: dict[str, str], references: dict[str, str]) -> None:
        self._titles = titles
        self._references = references

    def title(self, label: str) -> str | None:
        return self._titles.get(label)

    def reference(self, label: str) -> str | None:
        return self._references.get(label)


def test_with_no_worksheet_a_figure_is_its_label() -> None:
    assert EnglishNames().of(GROSS) == "gross_pay"
    assert EnglishNames().figure(GROSS, Decimal("70000.00")) == "gross_pay (70000.00)"


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
    assert names.of(NET) == "net_pay"


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
        "gross_pay (70000.00) less allowance (71300.00), not below 0, gives 0.00 (not rounded)."
    )
