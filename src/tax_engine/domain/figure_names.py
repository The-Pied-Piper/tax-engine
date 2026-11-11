"""How a form's figures are named as the form prints them, for whoever reads a trace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

__all__ = ["FigureNames", "ImportedFigure"]


@dataclass(frozen=True)
class ImportedFigure:
    """A figure a form reads from another form's export, as the exporting form prints it.

    `one_instance` is whether the exporting form has no instances list, so the figure has no
    item number to name.
    """

    form_title: str | None
    title: str | None
    reference: str | None
    one_instance: bool


class FigureNames(Protocol):
    """Where the printed names of a form's figures come from: a Worksheet."""

    @property
    def form_title(self) -> str | None:
        """The printed title of the form, if its manifest gives one."""
        ...

    def title(self, label: str) -> str | None:
        """The printed title of the figure `label`, if the form prints one."""
        ...

    def reference(self, label: str) -> str | None:
        """What the form prints beside the figure `label`, if it prints anything."""
        ...

    def imported(self, label: str) -> ImportedFigure | None:
        """The figure `label` as another form prints it, if this form reads it from there."""
        ...

    def shares_reference(self, label: str) -> bool:
        """Whether another figure of the form prints the same reference as the figure `label`."""
        ...
