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
        """The label of the figure this line is about, so a reader finds it by label instead of
        wording.

        Several lines about one figure share its label; `None` for a line not about a figure.
        """

    @property
    @abstractmethod
    def amount(self) -> Decimal:
        """The figure this line is about."""
