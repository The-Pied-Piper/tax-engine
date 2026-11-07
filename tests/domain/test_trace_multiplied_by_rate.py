"""Unit tests for `MultipliedByRateLine`, the trace line of the `core/multiply_by_rate` capability,
with made-up values.

The line lives in `tax_engine.domain.trace.arithmetic` and the package re-exports it. It keeps the
output, the base artifact's kind and value, the rate artifact's kind and value (a Decimal, as
given), the rounding rule and the rounded result; its `amount` is the result.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal

import pytest

import tax_engine.domain.trace
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.trace import MultipliedByRateLine, TraceLine
from tax_engine.domain.trace import arithmetic as trace_arithmetic

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

EXCESS_TAX = AmountKind("ex/excess_tax")
EXCESS_INCOME = AmountKind("ex/excess_income")
COLUMN_RATE = AmountKind("ex/column_rate")


def _line() -> MultipliedByRateLine:
    return MultipliedByRateLine(
        output=EXCESS_TAX,
        base_kind=EXCESS_INCOME,
        base_value=D("16449.00"),
        rate_kind=COLUMN_RATE,
        rate_value=D("0.0915"),
        rounding=CENT,
        result=D("1505.08"),
    )


def test_the_line_is_a_trace_line_exported_by_its_module_and_the_package() -> None:
    assert issubclass(MultipliedByRateLine, TraceLine)
    assert "MultipliedByRateLine" in trace_arithmetic.__all__
    assert tax_engine.domain.trace.MultipliedByRateLine is MultipliedByRateLine


def test_a_line_keeps_what_it_was_given_in_field_order() -> None:
    assert [f.name for f in fields(MultipliedByRateLine)] == [
        "output",
        "base_kind",
        "base_value",
        "rate_kind",
        "rate_value",
        "rounding",
        "result",
    ]

    line = _line()

    assert line.output is EXCESS_TAX
    assert line.base_kind is EXCESS_INCOME
    assert line.base_value == D("16449.00")
    assert line.rate_kind is COLUMN_RATE
    assert line.rate_value == D("0.0915")
    assert line.rounding == CENT
    assert line.result == D("1505.08")


def test_its_amount_is_the_result() -> None:
    assert _line().amount == D("1505.08")


def test_a_line_is_frozen() -> None:
    line = _line()

    with pytest.raises(FrozenInstanceError):
        line.result = D("1")  # type: ignore[misc]
