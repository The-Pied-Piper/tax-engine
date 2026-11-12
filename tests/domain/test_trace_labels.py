"""Unit tests for the label of a trace line: the figure it is about, or an explicit `None`.

Every line type states its own label, so a reader finds a figure by label instead of by wording.
"""

from __future__ import annotations

import inspect
from decimal import Decimal

import pytest

import tax_engine.domain.trace as domain_trace
import tax_engine.jurisdictions.ca.trace as ca_trace
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import (
    BlankFallbackLine,
    BlankFieldFallbackLine,
    BlankPassedOnLine,
    FormInstanceLine,
    SubtractedLine,
    TraceLine,
)
from tax_engine.domain.trace.blank import BlankField

D = Decimal


def _line_classes() -> list[type[TraceLine]]:
    found = {
        cls
        for module in (domain_trace, ca_trace)
        for _, cls in inspect.getmembers(module, inspect.isclass)
        if issubclass(cls, TraceLine) and cls is not TraceLine
    }
    return sorted(found, key=lambda cls: cls.__name__)


LINE_CLASSES = _line_classes()


def test_every_line_type_is_found() -> None:
    assert len(LINE_CLASSES) == 63


@pytest.mark.parametrize("cls", LINE_CLASSES, ids=[cls.__name__ for cls in LINE_CLASSES])
def test_every_line_type_states_its_own_label(cls: type[TraceLine]) -> None:
    assert "label" in vars(cls)
    assert not inspect.isabstract(cls)


def test_a_line_about_a_figure_is_labelled_with_its_output() -> None:
    net = AmountKind("ex/net_income")
    line = SubtractedLine(
        net, AmountKind("ex/a"), D(3), AmountKind("ex/b"), D(1), NO_ROUNDING, D(2)
    )

    assert line.label == "net_income"


def test_the_blank_lines_are_labelled_with_the_blank_figure() -> None:
    rent = AmountKind("ex/rent")
    records = AmountKind("ex/units")
    total = AmountKind("ex/total")

    assert BlankFallbackLine(rent, 0).label == "rent"
    assert BlankFieldFallbackLine(BlankField(rent, records, 2), 0).label == "rent"
    assert BlankPassedOnLine(total, (rent,)).label == "total"


def test_lines_about_one_figure_share_its_label() -> None:
    rent = AmountKind("ex/rent")

    records = AmountKind("ex/units")

    assert (
        BlankFieldFallbackLine(BlankField(rent, records, 1), 0).label
        == BlankFallbackLine(rent, 0).label
    )


def test_a_form_instance_is_not_about_a_figure() -> None:
    assert FormInstanceLine("ex/rental", 1, ()).label is None
