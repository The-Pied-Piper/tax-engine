"""Trace line for forms: the lines of one run of a form, grouped under the form's name."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.trace.base import TraceLine

__all__ = ["FormInstanceLine"]


@dataclass(frozen=True)
class FormInstanceLine(TraceLine):
    """The `lines` of the run of the form named `form` on its instance at `position` (from 1; a
    form without an instances list has one instance, 1), in the order they were recorded.

    Its own class: the form is a group of capabilities, not a capability, so the lines of a run
    are kept together here rather than among the lines of another form's.
    """

    form: str
    position: int
    lines: tuple[TraceLine, ...]

    @property
    def amount(self) -> Decimal:
        """Zero: the group is not about one figure; its inner lines each are."""
        return Decimal(0)
