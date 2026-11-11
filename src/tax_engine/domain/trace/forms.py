"""Trace line for forms: the lines of one run of a form, grouped under the form's name."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.figure_names import FigureNames
from tax_engine.domain.trace.base import TraceLine

__all__ = ["FormInstanceLine"]


@dataclass(frozen=True)
class FormInstanceLine(TraceLine):
    """The `lines` of the run of the form named `form` on its instance at `position` (from 1), in
    the order recorded.

    `printed` is the worksheet of that run, whose titles and references name the figures of `lines`;
    a line built without one names them by label.
    """

    form: str
    position: int
    lines: tuple[TraceLine, ...]
    printed: FigureNames | None = None

    @property
    def amount(self) -> Decimal:
        """Zero: the group is not about one figure; its inner lines each are."""
        return Decimal(0)

    @property
    def label(self) -> str | None:
        """None: the line is not about one figure."""
        return None
