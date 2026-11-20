"""Trace line for the lesser of counts: Schedule P Part D line 59."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.trace.base import TraceLine

__all__ = ["LesserOfCountsLine"]


@dataclass(frozen=True)
class LesserOfCountsLine(TraceLine):
    """The `result` produced as `output`: the least of `parts`, each a kind and its count."""

    output: ArtifactKind[int]
    parts: tuple[tuple[ArtifactKind[int], int], ...]
    result: int

    @property
    def amount(self) -> Decimal:
        """The least of the counts."""
        return Decimal(self.result)

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
