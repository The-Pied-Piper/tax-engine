"""EnglishNames: how a trace line's text names a figure.

By the form's reference ("line 4"), else its title in quotes, else its label in plain words, never
an invented title; a dataset's figure by its `title`, unquoted.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Protocol

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.unit_text import EnglishUnitTextRegistry
from tax_engine.domain.figure_names import FigureNames, ImportedFigure
from tax_engine.domain.parameters.amount import Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.unit import Unit

__all__ = ["EnglishNames", "FigureNames", "Labelled", "short_form_title"]

# A bare line number or letter ("4", "B", "26000", "5a"), or a box of a line ("87 box A"), is a line
# of the form; anything else ("Box 3", "Part 2") is already how the form says it.
_LINE_REFERENCE = re.compile(r"[A-Za-z0-9]+( box [A-Z])?")


def _line_of(reference: str) -> str:
    """A printed reference in a sentence: "line 4" for a bare line number or letter,
    "line 87 box A" for a box of a line."""
    return f"line {reference}" if _LINE_REFERENCE.fullmatch(reference) else reference


def _plain_words(label: str) -> str:
    """An internal label in plain words: "t2204_exemption" -> "t2204 exemption"."""
    return label.replace("_", " ")


def short_form_title(title: str) -> str:
    """How a sentence names a form: its printed title up to the colon, without a leading "Form ",
    e.g. "Form ON428: Ontario Tax" -> "ON428".
    """
    head = title.partition(":")[0].strip()
    return head.removeprefix("Form ")


class Labelled(Protocol):
    """Anything with a label: an artifact kind, a record list or one of its fields."""

    @property
    def label(self) -> str:
        """The figure's internal label."""
        ...


class EnglishNames:
    """Names figures in English: by printed reference, else printed title, else label."""

    def __init__(
        self,
        printed: FigureNames | None = None,
        unit_texts: EnglishUnitTextRegistry | None = None,
    ) -> None:
        """Name figures from `printed`, a worksheet; with none, every figure is its label.

        A figure's unit is written with its text in `unit_texts`, by default the shared registry.
        """
        self._printed = printed
        self._unit_texts = EnglishUnitTextRegistry.shared() if unit_texts is None else unit_texts

    @property
    def printed(self) -> FigureNames | None:
        """The worksheet figures are named from, if any."""
        return self._printed

    @property
    def unit_texts(self) -> EnglishUnitTextRegistry:
        """The registry unit text is looked up in."""
        return self._unit_texts

    def figure(self, figure: Labelled, value: Decimal | int) -> str:
        """The name of `figure` with its figure in brackets, e.g. "line 2 (70000.00)"."""
        return f"{self.of(figure)} ({self.shown(figure.label, value)})"

    def shown(self, label: str | None, value: Decimal | int) -> str:
        """`value` as the figure `label` is written: an amount in cents or finer, a count whole,
        with the figure's unit if it has one ("EX$3500.00", "12 moons"). `None` has no unit.
        """
        text = EnglishFigures.money(value) if isinstance(value, Decimal) else str(value)
        unit = None if label is None else self.unit_of(label)
        if unit is None:
            return text
        return self._unit_texts.for_unit(unit).write(text, value)

    def unit_of(self, label: str) -> Unit | None:
        """The unit of the figure `label`, as the form that makes it declares; `None` for none."""
        if self._printed is None:
            return None
        imported = self._printed.imported(label)
        return self._printed.unit(label) if imported is None else imported.unit

    def of(self, figure: Labelled) -> str:
        """The name of `figure` for a sentence."""
        return self.of_label(figure.label)

    def of_item(self, figure: Labelled, position: int) -> str:
        """The name of `figure` as read from item `position` of a list.

        A figure another form exports, from a form with one instance, has no item to name.
        """
        imported = None if self._printed is None else self._printed.imported(figure.label)
        if imported is not None and imported.one_instance:
            return self.of(figure)
        if imported is not None:
            return f"{self.of(figure)}, item {position}"
        return f"{self.of(figure)} of item {position}"

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
        imported = self._printed.imported(label)
        if imported is not None:
            return self._imported(label, imported)
        reference = self._printed.reference(label)
        title = self._printed.title(label)
        # Two figures on one line (an input and the step that reads it) print one reference, which
        # would name both: the title tells them apart where the form gives one.
        if reference is not None and (title is None or not self._printed.shares_reference(label)):
            return _line_of(reference)
        if title is not None:
            return f'"{title}"'
        return _plain_words(label)

    @staticmethod
    def _imported(label: str, imported: ImportedFigure) -> str:
        """The name of a figure another form exports: as that form prints it, then which form."""
        if imported.reference is not None:
            name = _line_of(imported.reference)
        elif imported.title is not None:
            name = f'"{imported.title}"'
        else:
            return _plain_words(label)
        if imported.form_title is None:
            return name
        return f"{name} of {short_form_title(imported.form_title)}"
