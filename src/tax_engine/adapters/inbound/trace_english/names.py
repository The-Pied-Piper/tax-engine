"""EnglishNames: how a trace line's text names a figure.

A figure is named the way the form prints it: by its reference ("line 4", "line B") when the form
prints one, otherwise by its title in quotes, and when it has neither (a step of the engine the
form does not print) by its internal label in plain words, never by an invented title.
A trace line's own figure is not named in its sentence: the line already carries its label, and
the form's title and reference for it come from the worksheet beside the text.
A fixed figure from a dataset is named by the wording the form prints for it (the dataset's
`title`, such as "maximum per slip"), else by its family in plain words.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Protocol

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.domain.parameters.amount import Amount
from tax_engine.domain.parameters.datasets import ParameterDataset

__all__ = ["EnglishNames", "FigureNames", "Labelled"]

# A bare line number or letter ("4", "B", "26000", "5a") is a line of the form; anything else
# ("Box 3", "Part 2") is already how the form says it.
_LINE_REFERENCE = re.compile(r"[A-Za-z0-9]+")


def _plain_words(label: str) -> str:
    """An internal label in plain words: "t2204_exemption" -> "t2204 exemption"."""
    return label.replace("_", " ")


class Labelled(Protocol):
    """Anything with a label: an artifact kind, a record list or one of its fields."""

    @property
    def label(self) -> str:
        """The figure's internal label."""
        ...


class FigureNames(Protocol):
    """Where the printed title and reference of a figure come from: a Worksheet."""

    def title(self, label: str) -> str | None:
        """The printed title of the figure `label`, if the form prints one."""
        ...

    def reference(self, label: str) -> str | None:
        """What the form prints beside the figure `label`, if it prints anything."""
        ...


class EnglishNames:
    """Names figures in English: by printed reference, else printed title, else label."""

    def __init__(self, printed: FigureNames | None = None) -> None:
        """Name figures from `printed`, a worksheet; with none, every figure is its label."""
        self._printed = printed

    @property
    def printed(self) -> FigureNames | None:
        """The worksheet figures are named from, if any."""
        return self._printed

    def figure(self, figure: Labelled, value: Decimal | int) -> str:
        """The name of `figure` with its figure in brackets, e.g. "line 2 (70000.00)"."""
        shown = EnglishFigures.money(value) if isinstance(value, Decimal) else str(value)
        return f"{self.of(figure)} ({shown})"

    def of(self, figure: Labelled) -> str:
        """The name of `figure` for a sentence."""
        return self.of_label(figure.label)

    def parameter(self, dataset: ParameterDataset[Amount]) -> str:
        """A fixed figure from a dataset: its name, then the figure in brackets.

        The name is the title the form prints for the figure ("the maximum per slip (81200.00)");
        a dataset without one is named by its family in plain words, never by an invented title.
        """
        name = dataset.title or _plain_words(dataset.family.rsplit("/", 1)[-1])
        return f"the {name} ({EnglishFigures.money(dataset.values.value)})"

    def of_label(self, label: str) -> str:
        """The name of the figure `label` for a sentence."""
        if self._printed is None:
            return _plain_words(label)
        reference = self._printed.reference(label)
        if reference is not None:
            return f"line {reference}" if _LINE_REFERENCE.fullmatch(reference) else reference
        title = self._printed.title(label)
        if title is not None:
            return f'"{title}"'
        return _plain_words(label)
