"""Unit tests for the trace line of a form instance, with made-up values.

A form runs once per instance, each on its own worksheet. Its trace lines come back grouped in
one `FormInstanceLine` per instance: the form's name, the instance's position from 1 (as items of
a record list are named) and the lines of that instance's run, in order. It lives in
`tax_engine.domain.trace.forms`, and the package re-exports it.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal

import pytest

import tax_engine.domain.trace
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import FormInstanceLine, RecordTotalLine, SubtractedLine, TraceLine
from tax_engine.domain.trace import forms as trace_forms

D = Decimal

NET_INCOME = AmountKind("ex/net_income")
GROSS_RENT = AmountKind("ex/gross_rent")
EXPENSES = AmountKind("ex/expenses")
UNIT_AMOUNT = AmountKind("ex/unit_amount")
UNIT_TOTAL = AmountKind("ex/unit_total")

SUBTRACTED = SubtractedLine(
    NET_INCOME, GROSS_RENT, D("12000"), EXPENSES, D("2000"), NO_ROUNDING, D("10000")
)
TOTAL = RecordTotalLine(UNIT_TOTAL, UNIT_AMOUNT, (D("100"), D("250.50")), D("350.50"))


def line() -> FormInstanceLine:
    return FormInstanceLine("ex/rental", 2, (SUBTRACTED, TOTAL))


def test_is_a_trace_line_of_the_forms_module_re_exported_by_the_package() -> None:
    assert issubclass(FormInstanceLine, TraceLine)
    assert FormInstanceLine.__module__ == "tax_engine.domain.trace.forms"
    assert list(trace_forms.__all__) == ["FormInstanceLine"]
    assert "FormInstanceLine" in tax_engine.domain.trace.__all__


def test_fields_in_order() -> None:
    found = line()

    assert [f.name for f in fields(found)] == ["form", "position", "lines", "printed"]
    assert found == FormInstanceLine(form="ex/rental", position=2, lines=(SUBTRACTED, TOTAL))
    assert found.form == "ex/rental"
    assert found.position == 2
    assert found.lines == (SUBTRACTED, TOTAL)
    assert isinstance(found.lines, tuple)


def test_amount_is_a_decimal() -> None:
    assert isinstance(line().amount, Decimal)


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(line(), "form", "ex/other")  # noqa: B010


def test_lines_are_equal_by_value() -> None:
    assert line() == line()
    assert line() is not line()
    assert hash(line()) == hash(line())


def test_lines_differ_by_form_position_or_inner_lines() -> None:
    assert line() != FormInstanceLine("ex/other", 2, (SUBTRACTED, TOTAL))
    assert line() != FormInstanceLine("ex/rental", 3, (SUBTRACTED, TOTAL))
    assert line() != FormInstanceLine("ex/rental", 2, (TOTAL, SUBTRACTED))
    assert line() != FormInstanceLine("ex/rental", 2, (SUBTRACTED,))


def test_an_instance_may_have_no_inner_lines() -> None:
    assert FormInstanceLine("ex/rental", 1, ()).lines == ()
