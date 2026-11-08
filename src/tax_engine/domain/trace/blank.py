"""Trace lines for blanks: a line left blank, a blank taken as a fallback, a blank passed on."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "BlankFieldFallbackLine",
    "BlankFallbackLine",
    "BlankPassedOnLine",
    "LeftBlankLine",
]


@dataclass(frozen=True)
class LeftBlankLine(TraceLine):
    """The `kind` the computation started with, left blank."""

    kind: ArtifactKind[Any]

    @property
    def amount(self) -> Decimal:
        """Zero: a blank has no figure, so the line is not about one."""
        return Decimal(0)

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.kind.label


@dataclass(frozen=True)
class BlankFallbackLine(TraceLine):
    """The blank `kind` that a capability took as `fallback`, the value it supplies for a blank."""

    kind: ArtifactKind[Any]
    fallback: Decimal | int

    @property
    def amount(self) -> Decimal:
        """The fallback taken."""
        return Decimal(self.fallback)

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.kind.label


@dataclass(frozen=True)
class BlankField:
    """The field `kind` of the record at `position` (from 1) in the record list `records`, left
    blank.
    """

    kind: ArtifactKind[Any]
    records: ArtifactKind[Any]
    position: int


@dataclass(frozen=True)
class BlankFieldFallbackLine(TraceLine):
    """The blank record field `field` that a capability took as `fallback`, the value it supplies
    for a blank."""

    field: BlankField
    fallback: Decimal | int

    @property
    def amount(self) -> Decimal:
        """The fallback taken."""
        return Decimal(self.fallback)

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.field.kind.label


@dataclass(frozen=True)
class BlankPassedOnLine(TraceLine):
    """The `output` left blank because the kinds in `because`, sorted, and the record fields in
    `because_fields`, in the order of their lists and records, were blank.
    """

    output: ArtifactKind[Any]
    because: tuple[ArtifactKind[Any], ...]
    because_fields: tuple[BlankField, ...] = ()

    @property
    def amount(self) -> Decimal:
        """Zero: a blank has no figure, so the line is not about one."""
        return Decimal(0)

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
