"""The trace line base class: one fact in a capability's explanation of its result."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

__all__ = ["TraceLine"]


@dataclass(frozen=True)
class TraceLine(ABC):
    """One fact in a capability's explanation of its result; subclasses are frozen dataclasses.

    A dataclass itself (with no fields) so every line supports `dataclasses.fields`.
    """

    @property
    @abstractmethod
    def label(self) -> str | None:
        """The label of the figure this line is about, so a reader finds its figure by label
        instead of by wording; several lines about one figure share its label.

        Required of every line type: `None`, stated by the line type, for a line that is not
        about a figure.
        """

    @property
    @abstractmethod
    def amount(self) -> Decimal:
        """The figure this line is about."""
