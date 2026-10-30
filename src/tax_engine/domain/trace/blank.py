"""Trace lines for blanks: a line left blank, a blank taken as a fallback, a blank passed on."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.trace.base import TraceLine

__all__ = ["BlankFallbackLine", "BlankPassedOnLine", "LeftBlankLine"]


@dataclass(frozen=True)
class LeftBlankLine(TraceLine):
    """The `kind` the computation started with, left blank."""

    kind: ArtifactKind[Any]

    @property
    def amount(self) -> Decimal:
        """Zero: a blank has no figure, so the line is not about one."""
        return Decimal(0)


@dataclass(frozen=True)
class BlankFallbackLine(TraceLine):
    """The blank `kind` that a capability took as `fallback`, the value it supplies for a blank."""

    kind: ArtifactKind[Any]
    fallback: Decimal | int

    @property
    def amount(self) -> Decimal:
        """The fallback taken."""
        return Decimal(self.fallback)


@dataclass(frozen=True)
class BlankPassedOnLine(TraceLine):
    """The `output` left blank because the kinds in `because`, sorted, were blank."""

    output: ArtifactKind[Any]
    because: tuple[ArtifactKind[Any], ...]

    @property
    def amount(self) -> Decimal:
        """Zero: a blank has no figure, so the line is not about one."""
        return Decimal(0)
