"""Unit tests for the blank trace lines, with made-up values.

`LeftBlankLine`, `BlankFallbackLine` and `BlankPassedOnLine` live in `tax_engine.domain.trace.blank`
and the package re-exports them. A blank has no figure, so only the fallback line has an `amount`.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal

import pytest

import tax_engine.domain.trace
from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.trace import BlankFallbackLine, BlankPassedOnLine, LeftBlankLine, TraceLine
from tax_engine.domain.trace import blank as trace_blank

CHART_GAIN = ArtifactKind("ex/chart_gain", Decimal)
DEDUCTION = ArtifactKind("ex/deduction", Decimal)


def test_the_lines_are_trace_lines_exported_by_their_module_and_the_package() -> None:
    for line_class in (LeftBlankLine, BlankFallbackLine, BlankPassedOnLine):
        assert issubclass(line_class, TraceLine)
        assert line_class.__name__ in trace_blank.__all__
        assert getattr(tax_engine.domain.trace, line_class.__name__) is line_class


def test_a_line_keeps_what_it_was_given() -> None:
    assert [f.name for f in fields(LeftBlankLine)] == ["kind"]
    assert [f.name for f in fields(BlankFallbackLine)] == ["kind", "fallback"]
    assert [f.name for f in fields(BlankPassedOnLine)] == ["output", "because"]


def test_a_line_is_frozen_and_compares_by_value() -> None:
    line = LeftBlankLine(CHART_GAIN)

    assert line == LeftBlankLine(CHART_GAIN)
    with pytest.raises(FrozenInstanceError):
        line.kind = DEDUCTION  # type: ignore[misc]


def test_only_the_fallback_line_has_a_figure() -> None:
    assert LeftBlankLine(CHART_GAIN).amount == 0
    assert BlankPassedOnLine(DEDUCTION, (CHART_GAIN,)).amount == 0
    assert BlankFallbackLine(DEDUCTION, Decimal("7.5")).amount == Decimal("7.5")
    assert BlankFallbackLine(DEDUCTION, 3).amount == 3
